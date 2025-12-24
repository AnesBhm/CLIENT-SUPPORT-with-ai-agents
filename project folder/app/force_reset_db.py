import asyncio
from app.core.database import engine
from app.models.base import Base
# Import all models to ensure metadata is populated
from app.models.user import User
from app.models.ticket import Ticket
from app.models.analytics import Analytics

async def reset_db():
    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
    print("Database reset complete.")

if __name__ == "__main__":
    asyncio.run(reset_db())
