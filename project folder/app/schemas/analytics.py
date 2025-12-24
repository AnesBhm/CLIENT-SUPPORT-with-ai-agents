from pydantic import BaseModel
from typing import Dict

class CategorySatisfactionStats(BaseModel):
    satisfied_count: int
    unsatisfied_count: int
    total_ai_resolved: int
    satisfaction_rate: float

class AnalyticsBase(BaseModel):
    metric_name: str
    value: int

class AnalyticsCreate(AnalyticsBase):
    pass

class Analytics(AnalyticsBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_tickets: int
    ai_resolved_tickets: int
    waiting_tickets_count: int
    average_response_time_hours: float
    escalation_percentage: float
    ai_satisfaction_by_category: Dict[str, CategorySatisfactionStats] = {}
    low_satisfaction_alert: bool = False
    total_satisfaction_rate: float = 0.0
