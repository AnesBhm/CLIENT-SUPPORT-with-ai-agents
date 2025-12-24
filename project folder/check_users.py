import asyncio
from app.core.database import SessionLocal
from app.services import user_service

async def check_users():
    async with SessionLocal() as db:
        admin_email = "admin@doxa.com"
        print(f"Checking for user {admin_email}...")
        try:
            user = await user_service.get_user_by_email(db, admin_email)
            if user:
                print(f"User found: {user.email}, ID: {user.id}, Role: {user.role}, Is Active: {user.is_active}")
            else:
                print("User NOT found.")
        except Exception as e:
            print(f"Error checking user: {e}")

if __name__ == "__main__":
    asyncio.run(check_users())
