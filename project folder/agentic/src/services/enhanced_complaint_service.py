"""
Enhanced ticket processing service with advanced agent pipeline
Includes Query Analyzer with summary (<100 words) and keywords (5-10)
Full latency instrumentation with trace_id for debugging
"""
import json
import re
from typing import Dict, Optional

from ..services.classification_service import classification_service
from ..services.enhanced_rag_service import enhanced_rag_service
from ..agents.advanced_agents import advanced_agent_factory
from ..utils.pipeline_tracer import create_tracer, PipelineTracer
from ..utils.query_logger import query_logger


class EnhancedComplaintService:
    """Enhanced service for processing user complaints through full agentic pipeline"""
    
    def __init__(self):
        """Initialize advanced agents including Query Analyzer and Response Composer"""
        self.query_analyzer = advanced_agent_factory.create_query_analyzer_agent()
        self.intent_agent = advanced_agent_factory.create_query_intent_agent()
        self.context_agent = advanced_agent_factory.create_context_enrichment_agent()
        # Language detection and response composition
        self.language_detector = advanced_agent_factory.create_language_detector_agent()
        self.response_composer = advanced_agent_factory.create_response_composer_agent()
    
    def _parse_query_analysis(self, response_text: str) -> Dict:
        """
        Parse the JSON output from Query Analyzer agent.
        
        Returns:
            Dict with summary, keywords, word_count, intent
        """
        try:
            # Try to extract JSON from the response
            # Handle cases where LLM might wrap in markdown code blocks
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback: return empty structure
        return {
            "summary": response_text[:200] if response_text else "Unable to analyze query",
            "keywords": [],
            "word_count": 0,
            "intent": "unknown"
        }
    
    def process_complaint(self, complaint_text: str, ticket_id: Optional[int] = None) -> Dict[str, any]:
        """
        Process a user complaint through the FULL enhanced agentic pipeline.
        
        Pipeline Steps:
        1. Classification (spam, aggressive, sensitive, etc.) with regex detection
        2. Query Analyzer: Summary (<100 words) + Keywords (5-10)
        3. Context Enrichment
        4. RAG Pipeline (if doxa_related) - retrieves from knowledge base
        5. Language Detection + Response Composition
        6. Confidence Scoring
        
        Includes full latency instrumentation with trace_id.
        Target: <10s end-to-end (<5s is ideal)
        
        Args:
            complaint_text: The user's ticket text
            ticket_id: Optional ticket ID for tracing
            
        Returns:
            Dict with classification, response, confidence, query_analysis, pipeline_metrics
        """
        # Initialize pipeline tracer for latency instrumentation
        tracer = create_tracer(ticket_id=ticket_id)
        tracer.start_pipeline()
        
        result = {
            "original_query": complaint_text,
            "rag_used": False,
            "intent": None,
            "enriched_query": None,
            "validation": None,
            "confidence_score": 0.0,
            "query_analysis": {
                "summary": None,
                "keywords": [],
                "word_count": 0,
                "intent": None
            },
            # Pipeline metrics
            "trace_id": tracer.trace_id,
            "pipeline_metrics": None
        }
        
        try:
            # STEP 1: Classification (with regex-based sensitive data detection)
            with tracer.stage("classification"):
                print(f"[Pipeline] Step 1: Classification")
                classification = classification_service.classify_query(complaint_text)
                result["classification"] = classification
                tracer.record_llm_call()
                print(f"[Pipeline] Classification: {classification}")
            
            # Get classification response
            classification_result = classification_service.get_response_for_classification(classification)
            
            # If not doxa_related, return early
            if not classification_result["should_process"]:
                result["response"] = classification_result["message"]
                if classification_result.get("escalate"):
                    result["should_escalate"] = True
                    result["escalation_priority"] = classification_result.get("escalation_priority", "HIGH")
                tracer.end_pipeline()
                result["pipeline_metrics"] = tracer.get_summary()
                return result
            
            # STEP 2: Query Analyzer - Summary + Keywords
            with tracer.stage("query_analysis"):
                print(f"[Pipeline] Step 2: Query Analyzer (Summary + Keywords)")
                try:
                    analyzer_response = self.query_analyzer.run(complaint_text)
                    tracer.record_llm_call()
                    query_analysis = self._parse_query_analysis(analyzer_response.content)
                    result["query_analysis"] = query_analysis
                    result["intent"] = query_analysis.get("intent", "unknown")
                    
                    print(f"[Pipeline] Query Analysis:")
                    print(f"   📝 Summary ({query_analysis.get('word_count', 0)} words): {query_analysis.get('summary', 'N/A')[:100]}...")
                    print(f"   🔑 Keywords ({len(query_analysis.get('keywords', []))}): {query_analysis.get('keywords', [])}")
                    print(f"   🎯 Intent: {query_analysis.get('intent', 'unknown')}")
                except Exception as e:
                    print(f"[Pipeline] Query Analyzer Error: {e}")
                    result["query_analysis"] = {
                        "summary": complaint_text[:100],
                        "keywords": complaint_text.split()[:5],
                        "word_count": len(complaint_text.split()),
                        "intent": "unknown"
                    }
            
            # STEP 3: Context Enrichment
            with tracer.stage("context_enrichment"):
                print(f"[Pipeline] Step 3: Context Enrichment")
                enrichment_response = self.context_agent.run(complaint_text)
                tracer.record_llm_call()
                enriched_query = enrichment_response.content.strip()
                result["enriched_query"] = enriched_query
                print(f"[Pipeline] Enriched Query: {enriched_query[:100]}...")
            
            # STEP 4: RAG Pipeline with enriched query
            with tracer.stage("rag_pipeline"):
                print(f"[Pipeline] Step 4: RAG Pipeline with Feedback Loop")
                print(f"[Pipeline]   → Sending enriched query to RAG service...")
                tracer.record_rag_attempt()
                rag_result = enhanced_rag_service.query_with_feedback_loop(enriched_query, max_retries=3)
                tracer.record_documents(rag_result.get("relevant_docs_count", 0))
                
                # Track retries
                for _ in range(rag_result.get("attempts", 1) - 1):
                    tracer.record_retry()
                    tracer.record_rag_attempt()
                
                print(f"\n[RAG RESULT] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"[RAG RESULT] Classification: {rag_result.get('classification_result', 'N/A')}")
                print(f"[RAG RESULT] Evaluation: {rag_result.get('evaluation_result', 'N/A')}")
                print(f"[RAG RESULT] Confidence: {rag_result.get('confidence_score', 0)}%")
                print(f"[RAG RESULT] Is Safe: {rag_result.get('is_safe', False)}")
                print(f"[RAG RESULT] Attempts: {rag_result.get('attempts', 1)}")
                print(f"[RAG RESULT] Relevant Docs: {rag_result.get('relevant_docs_count', 0)}")
                
                raw_ai_response = rag_result["answer"] if "answer" in rag_result else rag_result["response"]
                print(f"[RAG RESULT] Response Preview: {raw_ai_response[:200]}...")
                print(f"[RAG RESULT] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            
            # STEP 5: Language Detection
            with tracer.stage("language_detection"):
                print(f"[Pipeline] Step 5: Language Detection")
                try:
                    lang_response = self.language_detector.run(complaint_text)
                    tracer.record_llm_call()
                    detected_language = lang_response.content.strip().lower()[:2]
                    if detected_language not in ["fr", "en", "ar", "es"]:
                        detected_language = "fr"
                    result["detected_language"] = detected_language
                    print(f"[Pipeline] Detected Language: {detected_language}")
                except Exception as e:
                    print(f"[Pipeline] Language Detection Error: {e}, defaulting to French")
                    detected_language = "fr"
                    result["detected_language"] = detected_language
            
            # STEP 6: Response Composition
            with tracer.stage("response_composition"):
                print(f"[Pipeline] Step 6: Response Composer")
                try:
                    compose_input = f"""
language: {detected_language}
user_query: {complaint_text}
raw_answer: {raw_ai_response}
"""
                    composed_response = self.response_composer.run(compose_input)
                    tracer.record_llm_call()
                    final_response = composed_response.content.strip()
                    result["response"] = final_response
                    result["raw_rag_response"] = raw_ai_response
                    print(f"[Pipeline] Response composed successfully ({len(final_response)} chars)")
                except Exception as e:
                    print(f"[Pipeline] Response Composer Error: {e}, using raw response")
                    result["response"] = raw_ai_response
            
            # Set remaining result fields
            result["relevant_docs_count"] = rag_result.get("relevant_docs_count", 0)
            result["rag_used"] = True
            result["rag_status"] = rag_result.get("evaluation_result", "unknown")
            result["rag_attempts"] = rag_result.get("attempts", 1)
            result["confidence_score"] = rag_result.get("confidence_score", 0.0)
            
            # Check if escalated
            if not rag_result.get("is_safe", True):
                result["escalated"] = True
                result["escalation_reason"] = rag_result.get("reason", "low_confidence")
                result["feedback_history"] = rag_result.get("feedback_history", [])
                print(f"[Pipeline] ⚠️  ESCALATED: {result['escalation_reason']}")
            else:
                print(f"[Pipeline] ✅ Response generated successfully")
            
            print(f"[Pipeline] RAG Complete: Evaluation={rag_result.get('evaluation_result', 'N/A')}, Attempts={rag_result.get('attempts', 1)}, Safe={rag_result.get('is_safe', True)}")
            
        except Exception as e:
            print(f"[Pipeline] Critical Error: {e}")
            result["response"] = "I apologize, but I encountered an error processing your request. Please contact support@doxa.dz"
            result["confidence_score"] = 0.0
        finally:
            # End pipeline and record metrics
            tracer.end_pipeline()
            result["pipeline_metrics"] = tracer.get_summary()
        
        # Add recommendation based on confidence
        print(f"[Pipeline] Final Confidence Score from RAG: {result['confidence_score']}")
        result["recommendation"] = self._get_recommendation(result["confidence_score"])
        
        # Log query result to JSON
        try:
            query_logger.log_query_result(
                query=complaint_text,
                result=result,
                ticket_id=ticket_id
            )
        except Exception as e:
            print(f"[Pipeline] ⚠️ Failed to log query result: {e}")
        
        return result
    
    def _get_recommendation(self, confidence: float) -> str:
        """Get recommendation based on confidence score"""
        if confidence >= 0.80:
            return "auto_resolve"
        elif confidence >= 0.60:
            return "suggest_human_review"
        elif confidence >= 0.40:
            return "escalate_to_human"
        else:
            return "reject_and_escalate"
    
    def process_ticket(self, ticket_text: str, ticket_id: Optional[int] = None) -> Dict[str, any]:
        """Alias for process_complaint for API compatibility"""
        return self.process_complaint(ticket_text, ticket_id)


# Global instance
enhanced_ticket_service = EnhancedComplaintService()
