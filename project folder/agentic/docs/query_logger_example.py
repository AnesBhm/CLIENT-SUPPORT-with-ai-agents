"""
Example: Query Logger Usage and JSON Structure

This file demonstrates the JSON structure created by the query logger.
"""

# Example JSON structure that will be saved for each query:

EXAMPLE_LOG_ENTRY = {
    # Metadata with optimized indexes
    "metadata": {
        "timestamp": "2025-12-23T02:11:00.123456",
        "trace_id": "trace_abc123xyz",
        "ticket_id": 12345,
        "date": "2025-12-23",
        "time": "02:11:00"
    },
    
    # Table 1: Summary
    "summary": {
        "original_query": "Comment puis-je réinitialiser mon mot de passe Doxa?",
        "query_summary": "L'utilisateur demande comment réinitialiser son mot de passe pour accéder à Doxa.",
        "word_count": 8,
        "intent": "password_reset",
        "classification": "doxa_related",
        "detected_language": "fr"
    },
    
    # Table 2: Keywords
    "keywords": {
        "extracted_keywords": ["réinitialiser", "mot de passe", "Doxa", "compte", "accès"],
        "keyword_count": 5,
        "enriched_query": "Comment réinitialiser mot de passe compte Doxa procédure récupération accès"
    },
    
    # Table 3: RAG Documents
    "rag_docs": {
        "rag_used": True,
        "documents": [
            {
                "doc_id": 1,
                "content": "Pour réinitialiser votre mot de passe...",
                "relevance_score": None
            }
        ],
        "relevant_docs_count": 3,
        "rag_attempts": 1,
        "rag_status": "safe"
    },
    
    # Table 4: Response
    "response": {
        "final_response": "Bonjour! Pour réinitialiser votre mot de passe Doxa...",
        "raw_rag_response": "Pour réinitialiser votre mot de passe...",
        "response_length": 245,
        "validation": "safe"
    },
    
    # Table 5: Confidence
    "confidence": {
        "confidence_score": 0.85,
        "is_safe": True,
        "recommendation": "auto_resolve",
        "evaluation_result": "safe"
    },
    
    # Table 6: Escalation Reason
    "escalade_reason": {
        "escalated": False,
        "escalation_reason": None,
        "escalation_priority": None,
        "feedback_history": [],
        "dev_notes": None
    },
    
    # Table 7: Pipeline Metrics
    "pipeline_metrics": {
        "trace_id": "trace_abc123xyz",
        "total_latency_ms": 4523,
        "latency_target_met": True,
        "latency_ideal_met": True,
        "llm_calls": 5,
        "rag_attempts": 1,
        "had_errors": False,
        "stages": [
            {"name": "classification", "duration_ms": 234},
            {"name": "query_analysis", "duration_ms": 456},
            {"name": "context_enrichment", "duration_ms": 123},
            {"name": "rag_pipeline", "duration_ms": 3200},
            {"name": "language_detection", "duration_ms": 210},
            {"name": "response_composition", "duration_ms": 300}
        ]
    }
}

# The logger saves all entries for a day in: logs/query_results/queries_YYYY-MM-DD.json
# Each file contains an array of log entries like the one above.

# Optimized indexes for querying:
# - metadata.timestamp: ISO format for chronological sorting
# - metadata.trace_id: Unique identifier for correlation
# - metadata.date: Quick date-based filtering
# - confidence.confidence_score: Filter by confidence level
# - escalade_reason.escalated: Filter escalated queries
