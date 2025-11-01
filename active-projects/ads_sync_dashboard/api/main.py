"""
FastAPI main application.

Main entry point for the ads_sync dashboard backend API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.routes import runbooks, reports, jobs, data
from api.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ads_sync Dashboard API",
    version="0.1.0",
    description="""
    Backend API for the ads_sync command center.
    
    This API provides endpoints for:
    - Executing ads_sync CLI commands via background jobs (RQ)
    - Generating reports
    - Checking job status
    - Querying data freshness
    
    All heavy operations (CLI commands) run asynchronously in background workers.
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
# Handle cors_origins as either "*" or comma-separated list
origins = ["*"] if settings.cors_origins == "*" else settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(runbooks.router)
app.include_router(reports.router)
app.include_router(jobs.router)
app.include_router(data.router)


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "ads_sync Dashboard API",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Dict with health status
    
    Example:
        GET /health
        
        Response:
        {
            "status": "healthy",
            "redis_host": "localhost",
            "redis_port": 6379,
            "ads_sync_path": "../ads_sync"
        }
    """
    return {
        "status": "healthy",
        "redis_host": settings.redis_host,
        "redis_port": settings.redis_port,
        "ads_sync_path": str(settings.ads_sync_project_path)
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting ads_sync Dashboard API")
    logger.info(f"Redis: {settings.redis_host}:{settings.redis_port}")
    logger.info(f"ads_sync path: {settings.ads_sync_project_path}")
    logger.info(f"CORS origins: {settings.cors_origins}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down ads_sync Dashboard API")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )

