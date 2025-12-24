import asyncio
import os
from dotenv import load_dotenv

# Load env vars before imports
load_dotenv()

from app.core.database import SessionLocal
from app.services import user_service
from app.schemas.user import UserCreate, UserRole

async def create_admin():
    async with SessionLocal() as db:
        admin_email = "admin@doxa.com"
        existing_admin = await user_service.get_user_by_email(db, admin_email)
        
        if existing_admin:
            print(f"Admin user {admin_email} already exists.")
            return

        print(f"Creating admin user {admin_email}...")
        admin_user = UserCreate(
            email=admin_email,
            password="Admin123!",
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_over_18=True,
            receives_updates=False
        )
        
        try:
            user = await user_service.create_user(db, admin_user)
            print(f"Successfully created admin user: {user.email} with role {user.role}")
        except Exception as e:
            print(f"Failed to create admin user: {e}")

if __name__ == "__main__":
    asyncio.run(create_admin())
