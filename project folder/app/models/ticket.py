from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, DateTime, Float, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base
import enum

class TicketStatus(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED_BY_AI = "Resolved By AI"
    RESOLVED_BY_AGENT = "Resolved By Agent"
    ESCALATED = "Escalated"
    REJECTED = "Rejected"

class TicketCategory(str, enum.Enum):
    ACCOUNT = "Account"
    TEAM_MANAGEMENT = "Team Management"
    WORKFLOW = "Workflow"
    NOTIFICATIONS = "Notifications"
    BUGS = "Bugs"
    BILLING = "Billing"
    PRIVACY = "Privacy"
    GUIDANCE = "Guidance"
    OTHER = "Other"

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.OPEN)
    category: Mapped[TicketCategory] = mapped_column(Enum(TicketCategory), default=TicketCategory.OTHER)
    ai_confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_satisfied: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    feedback_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_response: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Relationships
    responses = relationship("Response", backref="ticket", cascade="all, delete-orphan", lazy="selectin")


