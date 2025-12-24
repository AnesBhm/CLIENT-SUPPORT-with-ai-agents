"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional, List


class QueryCategory(BaseModel):
    """Structured output for query classification"""
    category: Literal[
        "spam", 
        "aggressive", 
        "sensitive", 
        "out_of_scope", 
        "ambiguous", 
        "doxa_related"
    ] = Field(
        ..., 
        description="The classification category"
    )


class QueryAnalysis(BaseModel):
    """Query Analyzer output - summary + keywords"""
    summary: Optional[str] = Field(None, description="Summary of the query (<100 words)")
    keywords: List[str] = Field(default_factory=list, description="5-10 extracted keywords")
    word_count: int = Field(0, description="Number of words in summary")
    intent: Optional[str] = Field(None, description="Detected intent category")


class SensitiveDataInfo(BaseModel):
    """Sensitive data detection details"""
    detected: bool = Field(False, description="Whether sensitive data was detected")
    types: List[str] = Field(default_factory=list, description="Types of sensitive data found")
    risk_summary: Optional[dict] = Field(None, description="Risk level counts")
    redacted_text: Optional[str] = Field(None, description="Text with sensitive data redacted")


class PipelineMetrics(BaseModel):
    """Pipeline latency and performance metrics"""
    trace_id: str = Field(..., description="Unique trace ID for debugging")
    total_latency_ms: int = Field(0, description="Total pipeline latency in milliseconds")
    latency_target_met: bool = Field(True, description="Whether <10s target was met")
    latency_ideal_met: bool = Field(False, description="Whether <5s ideal target was met")
    llm_calls: int = Field(0, description="Number of LLM API calls")
    rag_attempts: int = Field(1, description="Number of RAG retrieval attempts")
    had_errors: bool = Field(False, description="Whether any errors occurred")
    stages: List[str] = Field(default_factory=list, description="Pipeline stages executed")


class TicketRequest(BaseModel):
    """Schema for ticket submission"""
    subject: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    ticket_id: Optional[int] = None  # For tracing


class TicketResponse(BaseModel):
    """Schema for ticket response with full metrics"""
    classification_result: str  # Changed from 'classification' to match backend
    response: str
    rag_used: bool = False
    confidence_score: int = 0  # 0-100 scale
    evaluation_result: Optional[str] = None  # safe, contradictory, missing_knowledge, etc.
    is_safe: bool = True
    intent: Optional[str] = None
    validation: Optional[str] = None
    attempts: int = 1
    reason: Optional[str] = None
    dev_notes: Optional[dict] = None
    # Query Analyzer metrics
    query_analysis: Optional[QueryAnalysis] = None
    # Sensitive data detection
    sensitive_data: Optional[SensitiveDataInfo] = None
    # Pipeline metrics (latency, trace_id)
    pipeline_metrics: Optional[PipelineMetrics] = None
    detected_language: Optional[str] = Field(None, description="Detected language code (fr, en, ar, es)")


class RAGRequest(BaseModel):
    """Schema for RAG query request"""
    query: str = Field(..., min_length=1, description="User query for RAG system")


class RAGResponse(BaseModel):
    """Schema for RAG query response"""
    query: str
    answer: str
    relevant_docs_count: int = 0
