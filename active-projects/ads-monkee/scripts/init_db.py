"""
Initialize Database
===================

Create all tables and run initial setup.
Use Alembic migrations in production.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import init_db, async_engine
from backend.config import settings


async def main():
    """Initialize database tables."""
    print(f"Initializing database: {settings.DATABASE_URL.split('@')[-1]}")
    print("Environment:", settings.ENVIRONMENT)
    
    if settings.is_production:
        print("\n⚠️  WARNING: Running in PRODUCTION mode!")
        print("Use Alembic migrations instead: alembic upgrade head")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
    
    try:
        await init_db()
        print("✅ Database tables created successfully!")
        
        # Verify by listing tables
        async with async_engine.connect() as conn:
            result = await conn.execute(
                """
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename
                """
            )
            tables = [row[0] for row in result]
            
            print(f"\n📋 Created {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

