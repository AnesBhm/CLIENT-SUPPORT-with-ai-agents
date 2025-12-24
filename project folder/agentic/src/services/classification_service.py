"""
Classification service for query categorization
Enhanced with regex-based sensitive data detection for 100% escalation
"""
from agno.agent import Agent
from agno.models.mistral import MistralChat
from typing import Dict, Tuple, Optional

from ..agents.classification_agents import agent_factory
from ..config.settings import settings
from ..utils.sensitive_data_detector import sensitive_data_detector


class ClassificationService:
    """Service for classifying user queries with enhanced sensitive data detection"""
    
    def __init__(self):
        """Initialize classification team and sensitive data detector"""
        self.model = MistralChat(
            id=settings.MISTRAL_MODEL_ID,
            temperature=settings.MISTRAL_TEMPERATURE
        )
        
        # Sensitive data detector (regex-based) for 100% escalation
        self.sensitive_detector = sensitive_data_detector
        
        # Create classification agent (using Agent directly as Team does not accept these args)
        self.classification_team = Agent(
            model=self.model,
            name="Query Classifier",
            description="Classifies user queries for Doxa platform support.",
            markdown=True,
            instructions=[
                "Classify user query for Doxa platform support system.",
                "",
                "CLASSIFICATION PRIORITY (check in order, return first match):",
                "1. 'spam' - gibberish, random characters, nonsense, repeated words",
                "2. 'aggressive' - hostile, abusive, threatening language",
                "3. 'sensitive' - contains personal sensitive data (SSN, credit cards, etc.)",
                "4. 'out_of_scope' - unrelated topics (geography, weather, cooking, general knowledge, etc.)",
                "5. 'ambiguous' - too vague, lacks context (e.g. 'help', 'i need help')",
                "6. 'doxa_related' - valid specific query about Doxa platform",
                "",
                "CRITICAL: General knowledge questions MUST be 'out_of_scope', NOT 'doxa_related'.",
                "Examples: 'where is paris' = out_of_scope, 'what is AI' = out_of_scope",
                "",
                "ABSOLUTE OUTPUT RULE - READ THIS CAREFULLY:",
                "1. DO NOT ANSWER THE QUESTION. You are a CLASSIFIER, not an assistant.",
                "2. Your ENTIRE response must be ONLY ONE WORD from this list:",
                "spam OR aggressive OR sensitive OR out_of_scope OR ambiguous OR doxa_related",
                "",
                "DO NOT write ANYTHING else. No JSON. No explanations. No sentences. No punctuation.",
                "ONLY the single category word.",
                "",
                "CORRECT outputs:",
                "out_of_scope",
                "doxa_related",
                "ambiguous",
                "spam",
                "",
                "WRONG outputs (DO NOT DO THIS):",
                "'The query is out of scope'",
                "{\"category\": \"out_of_scope\"}",
                "out_of_scope.",
                "Category: out_of_scope",
                "",
                "Query examples - YOUR RESPONSE SHOULD BE EXACTLY AS SHOWN:",
                "Query: 'How do I create a project in Doxa?' YOUR RESPONSE: doxa_related",
                "Query: 'what are the payment plans' YOUR RESPONSE: doxa_related",
                "Query: 'pricing options' YOUR RESPONSE: doxa_related",
                "Query: 'where is paris located' YOUR RESPONSE: out_of_scope",
                "Query: 'i need help' YOUR RESPONSE: ambiguous",
                "Query: 'asdfgh' YOUR RESPONSE: spam"
            ]
        )
    
    def classify_query(self, query: str) -> str:
        """
        Classify a user query into one of the predefined categories.
        PRIORITY: Regex-based sensitive data detection runs FIRST for 100% escalation.
        
        Args:
            query: The user's query text
            
        Returns:
            Classification category as string
        """
        # STEP 1: Check for sensitive data with regex patterns FIRST (100% escalation)
        sensitive_result = self.sensitive_detector.detect(query)
        if sensitive_result["contains_sensitive_data"]:
            print(f"   🔴 SENSITIVE DATA DETECTED (Regex): {sensitive_result['detected_types']}")
            print(f"   🔴 Risk Summary: {sensitive_result['risk_summary']}")
            print(f"   🔴 MANDATORY ESCALATION: 100%")
            return "sensitive"
        
        # STEP 2: Run LLM-based classification for other categories
        response = self.classification_team.run(query)
        classification = response.content.strip().lower()
        return classification
    
    def classify_query_detailed(self, query: str) -> Dict:
        """
        Detailed classification with full sensitive data analysis.
        
        Args:
            query: The user's query text
            
        Returns:
            Dict with classification and sensitive data details
        """
        # Run sensitive data detection
        sensitive_result = self.sensitive_detector.detect(query)
        
        result = {
            "query": query,
            "sensitive_data_detected": sensitive_result["contains_sensitive_data"],
            "sensitive_details": None,
            "classification": None,
            "should_escalate": False,
            "escalation_reason": None
        }
        
        if sensitive_result["contains_sensitive_data"]:
            result["classification"] = "sensitive"
            result["should_escalate"] = True  # 100% ESCALATION
            result["escalation_reason"] = sensitive_result["escalation_reason"]
            result["sensitive_details"] = {
                "detected_types": sensitive_result["detected_types"],
                "risk_summary": sensitive_result["risk_summary"],
                "redacted_text": sensitive_result["redacted_text"]
            }
        else:
            # Run LLM classification
            response = self.classification_team.run(query)
            result["classification"] = response.content.strip().lower()
        
        return result
    
    def get_response_for_classification(self, classification: str) -> Dict[str, any]:
        """
        Get appropriate response based on classification.
        
        Args:
            classification: The classification category
            
        Returns:
            Dict with response details
        """
        responses = {
            "spam": {
                "message": "This appears to be spam or nonsense. Please provide a valid query.",
                "should_process": False
            },
            "aggressive": {
                "message": "Your message contains aggressive language. Please rephrase politely.",
                "should_process": False
            },
            "sensitive": {
                "message": "⚠️ ALERTE SÉCURITÉ: Votre message contient des données personnelles sensibles (numéros de carte, téléphone, email, etc.). Pour votre protection, ces informations ont été détectées et votre demande sera traitée par un agent humain. Ne partagez JAMAIS vos données sensibles dans un chat.",
                "should_process": False,
                "escalate": True,  # 100% MANDATORY ESCALATION
                "escalation_priority": "CRITICAL"
            },
            "out_of_scope": {
                "message": "This question is outside the scope of Doxa platform support. I can only help with questions about Doxa project management platform.",
                "should_process": False
            },
            "ambiguous": {
                "message": "Your question is too vague. Please provide more specific details. Example: Instead of 'I need help', try 'How do I create a project in Doxa?'",
                "should_process": False
            },
            "doxa_related": {
                "message": "Query accepted for processing.",
                "should_process": True
            }
        }
        
        return responses.get(classification, {
            "message": f"Unknown classification: {classification}",
            "should_process": False
        })


# Global instance
classification_service = ClassificationService()
