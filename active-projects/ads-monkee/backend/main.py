"""
Ads Monkee FastAPI Application
===============================

Main entry point for the backend API server.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================================
# Lifespan Events
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events.
    
    Startup:
    - Initialize database connections
    - Start background tasks
    - Load configuration
    
    Shutdown:
    - Close database connections
    - Clean up resources
    """
    # Startup
    logger.info(f"Starting Ads Monkee API (Environment: {settings.ENVIRONMENT})")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    
    # Initialize Sentry if configured
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                integrations=[FastApiIntegration()],
            )
            logger.info("Sentry monitoring initialized")
        except ImportError:
            logger.warning("Sentry SDK not installed, monitoring disabled")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ads Monkee API")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Ads Monkee API",
    description="Unified Digital Advertising Management Platform",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# ============================================================================
# Middleware
# ============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Exception Handlers
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    
    Logs error and returns generic 500 response in production,
    detailed error in development.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if settings.is_development:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "type": type(exc).__name__,
            },
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please contact support.",
            },
        )


# ============================================================================
# Health Check Routes
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint - API status."""
    return {
        "service": "Ads Monkee API",
        "version": "0.1.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Used by Render and load balancers to verify service is healthy.
    Per SBEP v2.0: Should verify critical dependencies are accessible.
    """
    health_status = {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    # Database connectivity check
    try:
        from sqlalchemy import text
        from backend.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            await session.commit()
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
    
    # Redis connectivity check (if Redis URL is configured)
    try:
        import redis
        if settings.REDIS_URL and not settings.REDIS_URL.startswith("redis://localhost"):
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            health_status["checks"]["redis"] = "healthy"
        else:
            health_status["checks"]["redis"] = "not_configured"
    except Exception as e:
        if settings.REDIS_URL and not settings.REDIS_URL.startswith("redis://localhost"):
            health_status["status"] = "degraded"
            health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        else:
            health_status["checks"]["redis"] = "not_configured"
    
    return health_status


# ============================================================================
# API Routes
# ============================================================================

# Import routers
from backend.routers import analysis, health
from backend.api.routes import reports, clients

# Register routers
app.include_router(health.router)  # No prefix for /health
app.include_router(analysis.router, prefix="/api")
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])

# TODO: Add remaining routers
# from backend.routers import auth, modifications
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(modifications.router, prefix="/api/modifications", tags=["Modifications"])

# ============================================================================
# Development Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )

