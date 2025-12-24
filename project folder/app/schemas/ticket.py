from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class TicketStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED_BY_AI = "Resolved By AI"
    RESOLVED_BY_AGENT = "Resolved By Agent"
    ESCALATED = "Escalated"

class TicketCategory(str, Enum):
    ACCOUNT = "Account"
    TEAM_MANAGEMENT = "Team Management"
    WORKFLOW = "Workflow"
    NOTIFICATIONS = "Notifications"
    BUGS = "Bugs"
    BILLING = "Billing"
    PRIVACY = "Privacy"
    GUIDANCE = "Guidance"
    OTHER = "Other"

from pydantic import BaseModel, Field
from app.schemas.response import Response

# ... (Enums unchanged)

class TicketBase(BaseModel):
    subject: str = Field(..., min_length=5)
    description: str = Field(..., min_length=10)
    category: TicketCategory = TicketCategory.OTHER

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    agent_id: Optional[int] = None
    ai_confidence_score: Optional[float] = None
    category: Optional[TicketCategory] = None
    closed_at: Optional[datetime] = None
    

class TicketFeedback(BaseModel):
    is_satisfied: bool
    feedback_reason: Optional[str] = None

class Ticket(TicketBase):
    id: int
    status: TicketStatus
    category: TicketCategory
    ai_confidence_score: float
    is_satisfied: Optional[bool] = None

    feedback_reason: Optional[str] = None
    ai_response: Optional[str] = None
    created_at: datetime
    closed_at: Optional[datetime] = None
    customer_id: int
    agent_id: Optional[int] = None
    
    responses: list[Response] = []

    class Config:
        from_attributes = True
