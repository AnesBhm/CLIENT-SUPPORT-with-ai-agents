"""
Ticket processing service that orchestrates classification and RAG
"""
from typing import Dict

from ..services.classification_service import classification_service
from ..services.rag_service import rag_service


class TicketService:
    """Service for processing user tickets through the agentic pipeline"""
    
    def process_ticket(self, ticket_text: str) -> Dict[str, any]:
        """
        Process a user ticket through classification and RAG pipeline.
        
        Args:
            ticket_text: The user's ticket text
            
        Returns:
            Dict with classification, response, and metadata
        """
        # Step 1: Classify the query
        classification = classification_service.classify_query(ticket_text)
        
        # Step 2: Get response based on classification
        classification_result = classification_service.get_response_for_classification(classification)
        
        result = {
            "classification": classification,
            "rag_used": False,
            "response": classification_result["message"]
        }
        
        # Step 3: If doxa_related, run RAG pipeline
        if classification_result["should_process"]:
            rag_result = rag_service.query_doxa_rag(ticket_text)
            result["response"] = rag_result["answer"]
            result["rag_used"] = True
            result["relevant_docs_count"] = rag_result["relevant_docs_count"]
        
        return result


# Global instance
ticket_service = TicketService()
