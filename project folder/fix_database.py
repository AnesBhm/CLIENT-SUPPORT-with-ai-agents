import asyncio
import os
import shutil
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models.base import Base
# Import all models to ensure they are registered
from app.models import user, ticket, analytics, response

load_dotenv()

DB_FILE = "doxa_support_v1.db"

async def reset_db():
    print("Stopping to be safe... (ensure no write locks if possible)")
    
    # File deletion is blocked by running server. Using drop_all instead.
    print("Recreating database schema (dropping old tables)...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    print("Tables created.")
    
    # Run Create Admin
    from create_admin import create_admin
    print("Seeding admin user...")
    await create_admin()
    print("Done! Database fixed.")

if __name__ == "__main__":
    asyncio.run(reset_db())
