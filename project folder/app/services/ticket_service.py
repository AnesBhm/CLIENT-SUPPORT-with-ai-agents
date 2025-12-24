from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from app.models.ticket import Ticket, TicketStatus
from app.models.response import Response
from app.schemas.ticket import TicketCreate, TicketUpdate
from datetime import datetime

async def create_ticket(db: AsyncSession, ticket: TicketCreate, customer_id: int):
    ticket_data = ticket.model_dump()
    ticket_data["customer_id"] = customer_id
    db_ticket = Ticket(**ticket_data)
    db.add(db_ticket)
    await db.commit()
    await db.refresh(db_ticket)
    return db_ticket

async def create_response(db: AsyncSession, ticket_id: int, content: str, agent_id: int):
    # Determine if this resolves the ticket? Maybe not automatically. 
    # But usually agent response -> RESOLVED_BY_AGENT or IN_PROGRESS.
    # User requirement doesn't specify status change on response, but logical.
    # For now just create response.
    db_response = Response(
        ticket_id=ticket_id,
        content=content,
        agent_id=agent_id
    )
    db.add(db_response)
    
    # Also update ticket status to Resolved By Agent? Or In Progress?
    # Req 12: "Marquer le ticket comme résolu/fermé"
    ticket = await get_ticket(db, ticket_id)
    if ticket:
        ticket.status = TicketStatus.RESOLVED_BY_AGENT
        ticket.closed_at = datetime.utcnow()
        ticket.agent_id = agent_id
        db.add(ticket)
        
    await db.commit()
    await db.refresh(db_response)
    return db_response

async def get_tickets(
    db: AsyncSession, 
    category: str | None = None, 
    search: str | None = None,
    status: str | None = None,
    skip: int = 0, 
    limit: int = 100
):
    query = select(Ticket)
    
    if category:
        query = query.where(Ticket.category == category)
        
    if status:
        query = query.where(Ticket.status == status)
        
    if search:
        # Search by ID or Subject
        search_filter = or_(
            Ticket.subject.ilike(f"%{search}%"),
            # Cast ID to string for search if needed, or check if search is digit
        )
        if search.isdigit():
             search_filter = or_(search_filter, Ticket.id == int(search))
             
        query = query.where(search_filter)

    # Count total for pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get items
    result = await db.execute(query.offset(skip).limit(limit))
    items = result.scalars().all()
    
    return items, total

async def get_tickets_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    query = select(Ticket).where(Ticket.customer_id == user_id)
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    result = await db.execute(query.offset(skip).limit(limit))
    items = result.scalars().all()
    return items, total

async def get_ticket(db: AsyncSession, ticket_id: int):
    # Eager load responses
    query = select(Ticket).options(selectinload(Ticket.responses)).where(Ticket.id == ticket_id)
    result = await db.execute(query)
    return result.scalars().first()

async def update_ticket_feedback(db: AsyncSession, ticket_id: int, is_satisfied: bool, feedback_reason: str | None):
    ticket = await get_ticket(db, ticket_id)
    if ticket:
        ticket.is_satisfied = is_satisfied
        ticket.feedback_reason = feedback_reason
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
    return ticket

async def update_ticket(db: AsyncSession, ticket_id: int, ticket_update: TicketUpdate):
    ticket = await get_ticket(db, ticket_id)
    if not ticket:
        return None
    
    update_data = ticket_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ticket, key, value)
        
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket

async def get_analytics_stats(db: AsyncSession):
    # Total Tickets
    total_result = await db.execute(select(func.count(Ticket.id)))
    total_tickets = total_result.scalar() or 0

    if total_tickets == 0:
        return {
            "total_tickets": 0,
            "ai_resolved_tickets": 0,
            "waiting_tickets_count": 0,
            "average_response_time_hours": 0.0,
            "escalation_percentage": 0.0
        }

    # AI Resolved 
    ai_resolved_result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.RESOLVED_BY_AI)
    )
    ai_resolved_tickets = ai_resolved_result.scalar() or 0

    # Waiting Tickets (Not Resolved)
    # Status NOT IN (RESOLVED_BY_AI, RESOLVED_BY_AGENT)
    waiting_query = select(func.count(Ticket.id)).where(
        Ticket.status.notin_([TicketStatus.RESOLVED_BY_AI, TicketStatus.RESOLVED_BY_AGENT])
    )
    waiting_result = await db.execute(waiting_query)
    waiting_tickets_count = waiting_result.scalar() or 0

    # Escalation Percentage
    escalated_result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.ESCALATED)
    )
    escalated_count = escalated_result.scalar() or 0
    escalation_percentage = (escalated_count / total_tickets) * 100

    # Avg Response Time (Mocking logic: ClosedAt - CreatedAt)
    avg_time_result = await db.execute(
        select(func.avg(Ticket.closed_at - Ticket.created_at)).where(Ticket.closed_at.isnot(None))
    )
    average_response_time_hours = 0.0 

    # AI Satisfaction by Category
    stats_query = select(Ticket.category, Ticket.is_satisfied, func.count(Ticket.id)).where(
        Ticket.status == TicketStatus.RESOLVED_BY_AI
    ).group_by(Ticket.category, Ticket.is_satisfied)
    
    stats_result = await db.execute(stats_query)
    rows = stats_result.all()
    
    # Process rows into nested dict
    category_stats = {}
    
    for category, is_satisfied, count in rows:
        cat_str = category.value if hasattr(category, 'value') else str(category)
        if cat_str not in category_stats:
            category_stats[cat_str] = {"satisfied": 0, "unsatisfied": 0}
            
        if is_satisfied:
            category_stats[cat_str]["satisfied"] += count
        else:
            category_stats[cat_str]["unsatisfied"] += count

    # Calculate percentages
    final_cat_stats = {}
    for cat, data in category_stats.items():
        total = data["satisfied"] + data["unsatisfied"]
        rate = 0.0
        if total > 0:
            rate = (data["satisfied"] / total) * 100
        final_cat_stats[cat] = {
            "satisfied_count": data["satisfied"],
            "unsatisfied_count": data["unsatisfied"],
            "total_ai_resolved": total,
            "satisfaction_rate": round(rate, 2)
        }

    # Global Satisfaction Alert Logic
    global_sat_query = select(Ticket.is_satisfied, func.count(Ticket.id)).where(
        Ticket.status.in_([TicketStatus.RESOLVED_BY_AI, TicketStatus.RESOLVED_BY_AGENT]),
        Ticket.is_satisfied.isnot(None) 
    ).group_by(Ticket.is_satisfied)

    global_sat_result = await db.execute(global_sat_query)
    global_rows = global_sat_result.all()

    global_satisfied = 0
    global_unsatisfied = 0

    for is_satisfied, count in global_rows:
        if is_satisfied:
            global_satisfied += count
        else:
            global_unsatisfied += count
            
    total_feedback = global_satisfied + global_unsatisfied
    total_satisfaction_rate = 0.0
    low_satisfaction_alert = False

    if total_feedback > 0:
        total_satisfaction_rate = (global_satisfied / total_feedback) * 100
        if total_satisfaction_rate < 75.0:
            low_satisfaction_alert = True
            print(f"ALERT: High Unsatisfaction detected! Rate: {total_satisfaction_rate:.2f}%")

    return {
        "total_tickets": total_tickets,
        "ai_resolved_tickets": ai_resolved_tickets,
        "waiting_tickets_count": waiting_tickets_count,
        "average_response_time_hours": average_response_time_hours,
        "escalation_percentage": round(escalation_percentage, 2),
        "ai_satisfaction_by_category": final_cat_stats,
        "low_satisfaction_alert": low_satisfaction_alert,
        "total_satisfaction_rate": round(total_satisfaction_rate, 2)
    }
