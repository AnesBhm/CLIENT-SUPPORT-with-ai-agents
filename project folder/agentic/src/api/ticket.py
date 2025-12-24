"""
FastAPI endpoints for ticket processing
"""
from fastapi import APIRouter, HTTPException
from typing import Dict

from ..schemas.ticket import (
    TicketRequest, TicketResponse, RAGRequest, RAGResponse,
    QueryAnalysis, SensitiveDataInfo, PipelineMetrics
)
from ..services.ticket_service import ticket_service
from ..services.enhanced_complaint_service import enhanced_ticket_service
from ..services.rag_service import rag_service

router = APIRouter()

@router.post("/process-enhanced", response_model=TicketResponse)
async def process_ticket_enhanced(request: TicketRequest) -> Dict:
    """
    Process ticket through ENHANCED agentic pipeline with all agents.
    
    Pipeline includes:
    - Classification with regex-based sensitive data detection (100% escalation)
    - Query Analyzer: Summary (<100 words) + Keywords (5-10)
    - Context Enrichment  
    - RAG Pipeline with feedback loop
    - Language Detection
    - Response Composition (Template: Thanks + Problem + Solution + Action)
    - Confidence Scoring
    
    Full latency instrumentation with trace_id.
    Target: <10s end-to-end (<5s is ideal)
    """
    try:
        result = enhanced_ticket_service.process_ticket(
            request.description, 
            ticket_id=request.ticket_id
        )
        
        # Convert confidence_score to 0-100 scale if it's 0-1
        confidence = result.get("confidence_score", 0.0)
        if confidence <= 1.0:
            confidence = int(confidence * 100)
        else:
            confidence = int(confidence)
        
        # Determine is_safe based on confidence, escalation, and sensitive data
        is_safe = (
            confidence >= 60 and 
            not result.get("escalated", False) and
            not result.get("should_escalate", False)
        )
        
        # Build dev_notes if escalated
        dev_notes = None
        if result.get("escalated", False) or result.get("should_escalate", False):
            dev_notes = {
                "escalation_type": result.get("escalation_reason", result.get("escalation_priority", "UNKNOWN")).upper(),
                "action_required": "Human agent review needed",
                "feedback_history": result.get("feedback_history", []),
                "priority": result.get("escalation_priority", "HIGH" if confidence < 40 else "MEDIUM")
            }
        
        # Build query_analysis from result
        query_analysis_data = result.get("query_analysis", {})
        query_analysis = QueryAnalysis(
            summary=query_analysis_data.get("summary"),
            keywords=query_analysis_data.get("keywords", []),
            word_count=query_analysis_data.get("word_count", 0),
            intent=query_analysis_data.get("intent")
        ) if query_analysis_data else None
        
        # Build pipeline metrics
        metrics_data = result.get("pipeline_metrics", {})
        pipeline_metrics = PipelineMetrics(
            trace_id=metrics_data.get("trace_id", "N/A"),
            total_latency_ms=metrics_data.get("total_latency_ms", 0),
            latency_target_met=metrics_data.get("latency_target_met", True),
            latency_ideal_met=metrics_data.get("latency_ideal_met", False),
            llm_calls=metrics_data.get("llm_calls", 0),
            rag_attempts=metrics_data.get("rag_attempts", 1),
            had_errors=metrics_data.get("had_errors", False),
            stages=metrics_data.get("stages", [])
        ) if metrics_data else None
        
        return TicketResponse(
            classification_result=result["classification"],
            response=result["response"],
            rag_used=result["rag_used"],
            confidence_score=confidence,
            evaluation_result=result.get("rag_status", result.get("validation", "unknown")),
            is_safe=is_safe,
            intent=result.get("intent"),
            validation=result.get("validation"),
            attempts=result.get("rag_attempts", result.get("attempts", 1)),
            reason=f"Confidence: {confidence}%, Validation: {result.get('validation', 'N/A')}",
            dev_notes=dev_notes,
            query_analysis=query_analysis,
            pipeline_metrics=pipeline_metrics,
            detected_language=result.get("detected_language")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing ticket: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "agentic-ai"}
