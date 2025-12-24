from pydantic import BaseModel
from datetime import datetime

class ResponseBase(BaseModel):
    content: str
    
class ResponseCreate(ResponseBase):
    pass

class Response(ResponseBase):
    id: int
    ticket_id: int
    agent_id: int | None = None
    created_at: datetime
    
    class Config:
        from_attributes = True
