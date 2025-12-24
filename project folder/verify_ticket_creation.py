import asyncio
import os
from dotenv import load_dotenv

# Load env vars before imports
load_dotenv()

from app.core.database import SessionLocal
from app.services import ticket_service, user_service
from app.schemas.ticket import TicketCreate, TicketCategory

async def create_ticket_test():
    async with SessionLocal() as db:
        admin_email = "admin@doxa.com"
        user = await user_service.get_user_by_email(db, admin_email)
        
        if not user:
            print("Admin user not found. Run create_admin.py first.")
            return

        print(f"Creating ticket for user {user.email} (ID: {user.id})...")
        
        ticket_in = TicketCreate(
            subject="Test Ticket for Internal Error Check",
            description="Checking if ticket creation throws 500 error.",
            category=TicketCategory.BUGS,
            ai_confidence_score=0.0
        )
        
        try:
            ticket = await ticket_service.create_ticket(db, ticket_in, customer_id=user.id)
            print(f"Successfully created ticket {ticket.id}: {ticket.subject}")
        except Exception as e:
            print(f"Failed to create ticket: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_ticket_test())
