from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, DateTime
from datetime import datetime
from app.models.base import Base

class Response(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    
    # Optional: Link to the agent who responded. 
    # If None, it might be an automated response or system message (though requirement said Ticket-Response 1:N, Agent-Response 1:N)
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
