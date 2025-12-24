import asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ticket import Ticket, TicketStatus
from app.services import ticket_service
from app.core.database import SessionLocal

AGENTIC_SERVICE_URL = "http://localhost:8002/api/v1/tickets/process-enhanced"
# Increased timeout to handle slow AI responses (2 minutes)
AI_REQUEST_TIMEOUT = 120.0

async def process_ticket_with_ai(ticket_id: int):
    """
    Background task to process ticket with AI agent pipeline.
    Calls the Agentic Service API.
    """
    try:
        with open("ai_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[START] Processing ticket {ticket_id}\n")
            
        async with SessionLocal() as db:
            print(f"AI Agent: Processing ticket {ticket_id}...", flush=True)
            ticket = await ticket_service.get_ticket(db, ticket_id)
            if not ticket:
                print("AI Agent: Ticket not found.", flush=True)
                with open("ai_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"[ERROR] Ticket {ticket_id} not found\n")
                return

            # Prepare request payload
            payload = {
                "subject": ticket.subject or "",
                "description": ticket.description or "",
                "category": None
            }
            
            print(f"AI Agent: Calling Agentic Service at {AGENTIC_SERVICE_URL} (timeout: {AI_REQUEST_TIMEOUT}s)...", flush=True)
            with open("ai_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[REQUEST] Sending to Agentic Service: {payload}\n")
            
            # Call Agentic Service with extended timeout
            async with httpx.AsyncClient(timeout=AI_REQUEST_TIMEOUT) as client:
                try:
                    response = await client.post(AGENTIC_SERVICE_URL, json=payload)
                    response.raise_for_status()
                    result = response.json()
                    
                    # Extract Data
                    # Agentic service returns confidence_score as int 0-100
                    raw_confidence = result.get("confidence_score", 0)
                    confidence_score = float(raw_confidence) / 100.0
                    
                    is_safe = result.get("is_safe", True)
                    ai_response = result.get("response", "")
                    classification = result.get("classification_result", "unknown")
                    
                    print(f"AI Agent: Received response. Classification: {classification}. Confidence: {confidence_score:.2f}", flush=True)

                    # Update Ticket
                    ticket.ai_confidence_score = confidence_score
                    ticket.ai_response = ai_response

                    # Log response to file since we don't have a column yet
                    with open("ai_log.txt", "a", encoding="utf-8") as f:
                        f.write(f"Ticket {ticket_id} Result:\n")
                        f.write(f"  Classification: {classification}\n")
                        f.write(f"  Confidence: {confidence_score}\n")
                        f.write(f"  Is Safe: {is_safe}\n")
                        f.write(f"  Response: {ai_response}\n\n")

                    if not is_safe:
                        print("AI Agent: Low confidence or validation failure. Escalating ticket.", flush=True)
                        ticket.status = TicketStatus.ESCALATED
                    else:
                        # NEW LOGIC: Check for rejection categories
                        rejection_categories = ["spam", "aggressive", "out_of_scope", "ambiguous", "sensitive"]
                        
                        if classification.lower() in rejection_categories:
                            print(f"AI Agent: Ticket classified as '{classification}'. Rejecting ticket.", flush=True)
                            ticket.status = TicketStatus.REJECTED
                        elif confidence_score >= 0.6:
                             print("AI Agent: High confidence. Auto-resolution candidate.", flush=True)
                             ticket.status = TicketStatus.RESOLVED_BY_AI
                        else:
                             print("AI Agent: Low confidence despite safety. Escalating.", flush=True)
                             ticket.status = TicketStatus.ESCALATED

                    db.add(ticket)
                    await db.commit()
                    await db.refresh(ticket)
                    
                    print(f"AI Agent: Finished ticket {ticket_id}. Status: {ticket.status.value}", flush=True)
                    with open("ai_log.txt", "a", encoding="utf-8") as f:
                        f.write(f"[COMPLETE] Ticket {ticket_id} processed. Status: {ticket.status.value}, Response: {ai_response[:100]}...\n")

                except httpx.TimeoutException as exc:
                    # Timeout - escalate the ticket so it doesn't get stuck
                    print(f"AI Agent: TIMEOUT waiting for Agentic Service (>{AI_REQUEST_TIMEOUT}s): {exc}", flush=True)
                    with open("ai_log.txt", "a", encoding="utf-8") as f:
                        f.write(f"[TIMEOUT] Ticket {ticket_id} - AI processing timed out after {AI_REQUEST_TIMEOUT}s\n")
                    # Escalate the ticket to agent since AI couldn't process in time
                    ticket.status = TicketStatus.ESCALATED
                    ticket.ai_response = "AI processing timed out. This ticket has been escalated to a human agent."
                    db.add(ticket)
                    await db.commit()
                    print(f"AI Agent: Ticket {ticket_id} escalated due to timeout.", flush=True)
                    
                except httpx.RequestError as exc:
                    print(f"AI Agent: Connection error to Agentic Service: {exc}", flush=True)
                    with open("ai_log.txt", "a", encoding="utf-8") as f:
                        f.write(f"[ERROR] Ticket {ticket_id} - Connection error: {exc}\n")
                    # Escalate the ticket so it doesn't get stuck
                    ticket.status = TicketStatus.ESCALATED
                    ticket.ai_response = "AI service is unavailable. This ticket has been escalated to a human agent."
                    db.add(ticket)
                    await db.commit()
                    print(f"AI Agent: Ticket {ticket_id} escalated due to connection error.", flush=True)
                    
                except httpx.HTTPStatusError as exc:
                    print(f"AI Agent: HTTP error from Agentic Service: {exc.response.status_code} - {exc.response.text}", flush=True)
                    with open("ai_log.txt", "a", encoding="utf-8") as f:
                        f.write(f"[HTTP_ERROR] Ticket {ticket_id} - {exc.response.status_code}: {exc.response.text}\n")
                    # Escalate the ticket so it doesn't get stuck
                    ticket.status = TicketStatus.ESCALATED
                    ticket.ai_response = f"AI processing error (HTTP {exc.response.status_code}). This ticket has been escalated to a human agent."
                    db.add(ticket)
                    await db.commit()
                    print(f"AI Agent: Ticket {ticket_id} escalated due to HTTP error.", flush=True)

    except Exception as e:
        with open("ai_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[FATAL_ERROR] Ticket {ticket_id if 'ticket_id' in dir() else 'unknown'}: {e}\n")
        print(f"AI Agent FATAL ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        # Try to escalate the ticket even in fatal errors
        try:
            async with SessionLocal() as db:
                ticket = await ticket_service.get_ticket(db, ticket_id)
                if ticket and ticket.status not in [TicketStatus.RESOLVED_BY_AI, TicketStatus.ESCALATED, TicketStatus.RESOLVED_BY_AGENT]:
                    ticket.status = TicketStatus.ESCALATED
                    ticket.ai_response = "An unexpected error occurred. This ticket has been escalated to a human agent."
                    db.add(ticket)
                    await db.commit()
        except:
            pass  # Best effort - if this fails, the ticket may be stuck