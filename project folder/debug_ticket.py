import asyncio
from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate
from app.services import ticket_service

async def main():
    print("Initializing DB...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as db:
        print("Creating User...")
        user = User(email="debug@test.com", hashed_password="pw", role=UserRole.CLIENT)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"User created: {user.id}")

        print("Creating Ticket...")
        ticket_data = TicketCreate(
            subject="Debug Subject",
            description="Debug Desc",
            customer_id=user.id,
            ai_confidence_score=0.5
        )
        try:
            ticket = await ticket_service.create_ticket(db, ticket_data)
            print(f"Ticket created: {ticket.id}")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
