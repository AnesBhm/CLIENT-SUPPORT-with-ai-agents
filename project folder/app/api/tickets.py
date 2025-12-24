from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas import ticket as ticket_schemas
from app.schemas.common import PaginatedResponse
from app.schemas.response import ResponseCreate, Response as ResponseSchema
from app.services import ticket_service
from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

# 1. Specific string paths first
@router.get("/me", response_model=PaginatedResponse[ticket_schemas.Ticket])
async def read_my_tickets(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get tickets for the authenticated user.
    """
    items, total = await ticket_service.get_tickets_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return {
        "items": items,
        "total": total,
        "page": (skip // limit) + 1,
        "pages": (total + limit - 1) // limit
    }



@router.get("/escalated", response_model=PaginatedResponse[ticket_schemas.Ticket]) # TODO: Paginate this too if critical, but user requirement generic list pagination
async def read_escalated_tickets(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    """
    Get escalated tickets for agents.
    """
    from app.models.ticket import TicketStatus
    return await ticket_service.get_tickets_by_status(db, status=TicketStatus.ESCALATED, skip=skip, limit=limit)

# 2. General collections
@router.get("/", response_model=PaginatedResponse[ticket_schemas.Ticket])
async def read_tickets(
    category: ticket_schemas.TicketCategory | None = None,
    search: str | None = None,
    # TODO: status filter if needed by frontend
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    items, total = await ticket_service.get_tickets(db, category=category, search=search, skip=skip, limit=limit)
    return {
        "items": items,
        "total": total,
        "page": (skip // limit) + 1,
        "pages": (total + limit - 1) // limit
    }

@router.post("/", response_model=ticket_schemas.Ticket)
async def create_ticket(
    ticket: ticket_schemas.TicketCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("DEBUG: Creating ticket...", flush=True)
    try:
        created_ticket = await ticket_service.create_ticket(db=db, ticket=ticket, customer_id=current_user.id)
        # Trigger AI processing in background
        from app.services import ai_service
        background_tasks.add_task(ai_service.process_ticket_with_ai, ticket_id=created_ticket.id)
        return created_ticket
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Debugging 500: {str(e)}")

# 3. Path parameters (ID)
@router.get("/{ticket_id}", response_model=ticket_schemas.Ticket)
async def read_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    db_ticket = await ticket_service.get_ticket(db, ticket_id=ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db_ticket

@router.get("/{ticket_id}/status")
async def get_ticket_status(ticket_id: int, db: AsyncSession = Depends(get_db)):
    """
    Long polling helper. Returns simplified status for frontend UI.
    """
    from app.models.ticket import TicketStatus
    
    ticket = await ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    # Map internal status to frontend status
    frontend_status = "Processing"
    ai_typing = True
    ai_response_body = None
    
    if ticket.status == TicketStatus.RESOLVED_BY_AI:
        frontend_status = "AI_Resolved"
        ai_typing = False
        ai_response_body = ticket.ai_response
    elif ticket.status == TicketStatus.ESCALATED:
        frontend_status = "Escalated"
        ai_typing = False
        ai_response_body = ticket.ai_response # Optional: show escalation message
    elif ticket.status == TicketStatus.RESOLVED_BY_AGENT:
         frontend_status = "AI_Resolved" # Or handle differently, but user asked for these 3 states
         ai_typing = False
         ai_response_body = "Resolved by Agent." 
    
    return {
        "status": frontend_status,
        "ai_typing": ai_typing,
        "ai_response_body": ai_response_body
    }

@router.post("/{ticket_id}/responses", response_model=ResponseSchema)
async def create_ticket_response(
    ticket_id: int,
    response_in: ResponseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Agent reply to a ticket.
    """
    # Verify ticket exists
    ticket = await ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    return await ticket_service.create_response(
        db, 
        ticket_id=ticket_id, 
        content=response_in.content, 
        agent_id=current_user.id
    )

@router.put("/{ticket_id}", response_model=ticket_schemas.Ticket)
async def update_ticket(
    ticket_id: int, 
    ticket_update: ticket_schemas.TicketUpdate, 
    db: AsyncSession = Depends(get_db)
):
    updated_ticket = await ticket_service.update_ticket(db, ticket_id=ticket_id, ticket_update=ticket_update)
    if not updated_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return updated_ticket

@router.post("/{ticket_id}/feedback", response_model=ticket_schemas.Ticket)
async def submit_feedback(
    ticket_id: int, 
    feedback: ticket_schemas.TicketFeedback,
    db: AsyncSession = Depends(get_db)
):
    updated_ticket = await ticket_service.update_ticket_feedback(
        db, 
        ticket_id, 
        feedback.is_satisfied,
        feedback.feedback_reason
    )
    if not updated_ticket:
         raise HTTPException(status_code=404, detail="Ticket not found")
    return updated_ticket
