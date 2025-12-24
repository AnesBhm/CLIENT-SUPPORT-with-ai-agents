"""
Query Result JSON Logger
Logs each processed query with structured data for analysis and auditing.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class QueryLogger:
    """Logger for saving query processing results to JSON files"""
    
    def __init__(self, log_dir: str = "logs/query_results"):
        """
        Initialize query logger.
        
        Args:
            log_dir: Directory to save JSON log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_log_file_path(self) -> Path:
        """Get log file path with date-based rotation"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"queries_{date_str}.json"
    
    def _extract_rag_docs(self, result: Dict) -> List[Dict]:
        """
        Extract RAG documents from result.
        
        Args:
            result: Query processing result dictionary
            
        Returns:
            List of document dictionaries with content and metadata
        """
        rag_docs = []
        
        # Check if RAG was used
        if not result.get("rag_used", False):
            return rag_docs
        
        # Try to extract from various possible locations
        relevant_docs_count = result.get("relevant_docs_count", 0)
        
        # Create placeholder docs based on count
        for i in range(relevant_docs_count):
            rag_docs.append({
                "doc_id": i + 1,
                "content": f"Document {i + 1} (content not available in result)",
                "relevance_score": None
            })
        
        return rag_docs
    
    def log_query_result(
        self,
        query: str,
        result: Dict[str, Any],
        ticket_id: Optional[int] = None
    ) -> None:
        """
        Log a query processing result to JSON file.
        
        Args:
            query: Original user query
            result: Processing result from enhanced_complaint_service
            ticket_id: Optional ticket ID
        """
        timestamp = datetime.now().isoformat()
        trace_id = result.get("trace_id", result.get("pipeline_metrics", {}).get("trace_id", "N/A"))
        
        # Extract query analysis
        query_analysis = result.get("query_analysis", {})
        
        # Build structured log entry
        log_entry = {
            # Metadata with optimized indexes
            "metadata": {
                "timestamp": timestamp,
                "trace_id": trace_id,
                "ticket_id": ticket_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S")
            },
            
            # Table 1: Summary
            "summary": {
                "original_query": query,
                "query_summary": query_analysis.get("summary"),
                "word_count": query_analysis.get("word_count", len(query.split())),
                "intent": query_analysis.get("intent", result.get("intent")),
                "classification": result.get("classification"),
                "detected_language": result.get("detected_language")
            },
            
            # Table 2: Keywords
            "keywords": {
                "extracted_keywords": query_analysis.get("keywords", []),
                "keyword_count": len(query_analysis.get("keywords", [])),
                "enriched_query": result.get("enriched_query")
            },
            
            # Table 3: RAG Documents
            "rag_docs": {
                "rag_used": result.get("rag_used", False),
                "documents": self._extract_rag_docs(result),
                "relevant_docs_count": result.get("relevant_docs_count", 0),
                "rag_attempts": result.get("rag_attempts", result.get("attempts", 1)),
                "rag_status": result.get("rag_status", result.get("evaluation_result"))
            },
            
            # Table 4: Response
            "response": {
                "final_response": result.get("response"),
                "raw_rag_response": result.get("raw_rag_response"),
                "response_length": len(result.get("response", "")),
                "validation": result.get("validation")
            },
            
            # Table 5: Confidence
            "confidence": {
                "confidence_score": result.get("confidence_score", 0.0),
                "is_safe": result.get("confidence_score", 0.0) >= 60 and not result.get("escalated", False),
                "recommendation": result.get("recommendation"),
                "evaluation_result": result.get("rag_status", result.get("validation"))
            },
            
            # Table 6: Escalation Reason
            "escalade_reason": {
                "escalated": result.get("escalated", result.get("should_escalate", False)),
                "escalation_reason": result.get("escalation_reason", result.get("escalation_priority")),
                "escalation_priority": result.get("escalation_priority"),
                "feedback_history": result.get("feedback_history", []),
                "dev_notes": result.get("dev_notes")
            },
            
            # Table 7: Pipeline Metrics (bonus for optimization)
            "pipeline_metrics": result.get("pipeline_metrics", {})
        }
        
        # Append to daily log file
        log_file = self._get_log_file_path()
        
        # Read existing logs if file exists
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                # File is corrupted or empty, start fresh
                logs = []
        
        # Append new log entry
        logs.append(log_entry)
        
        # Write back to file with pretty formatting
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        
        print(f"[QueryLogger] ✅ Logged query result to {log_file}")
        print(f"[QueryLogger]    Trace ID: {trace_id}")
        print(f"[QueryLogger]    Confidence: {result.get('confidence_score', 0.0)}")
        print(f"[QueryLogger]    Escalated: {log_entry['escalade_reason']['escalated']}")
    
    def get_logs_by_date(self, date: str) -> List[Dict]:
        """
        Retrieve logs for a specific date.
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            List of log entries for that date
        """
        log_file = self.log_dir / f"queries_{date}.json"
        
        if not log_file.exists():
            return []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_logs_by_trace_id(self, trace_id: str, date: Optional[str] = None) -> Optional[Dict]:
        """
        Retrieve log entry by trace ID.
        
        Args:
            trace_id: Trace ID to search for
            date: Optional date to narrow search (YYYY-MM-DD)
            
        Returns:
            Log entry if found, None otherwise
        """
        if date:
            logs = self.get_logs_by_date(date)
        else:
            # Search today's logs
            date = datetime.now().strftime("%Y-%m-%d")
            logs = self.get_logs_by_date(date)
        
        for log in logs:
            if log.get("metadata", {}).get("trace_id") == trace_id:
                return log
        
        return None


# Global instance
query_logger = QueryLogger()
