"""
Enhanced RAG service with document evaluation and feedback loop
"""
import google.generativeai as genai
from chromadb import PersistentClient
from FlagEmbedding import BGEM3FlagModel
from typing import List, Dict

from ..config.settings import settings
from ..agents.evaluation_agents import evaluation_agent_factory


class EnhancedRAGService:
    """Enhanced RAG service with document quality evaluation and retry mechanism"""
    
    def __init__(self):
        """Initialize RAG components with evaluation team"""
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        
        # Initialize BGE model
        self.bge_model = BGEM3FlagModel(
            settings.BGE_MODEL_NAME,
            use_fp16=settings.BGE_USE_FP16
        )
        
        # Initialize ChromaDB (use data/chroma_archive as fallback)
        try:
            self.chroma_client = PersistentClient(path=settings.CHROMA_PERSIST_PATH)
        except:
            # Fallback to chroma_archive if data/chroma_db doesn't exist yet
            self.chroma_client = PersistentClient(path="data/chroma_archive")
        
        self.collection = self.chroma_client.get_collection(
            name=settings.CHROMA_COLLECTION_NAME
        )
        
        # Initialize evaluation team
        self.evaluation_team = evaluation_agent_factory.create_evaluation_team()
        
        # Import advanced agents for confidence scoring
        from ..agents.advanced_agents import advanced_agent_factory
        self.confidence_agent = advanced_agent_factory.create_confidence_scoring_agent()
    
    def get_embedding(self, text: str, max_length: int = None) -> List[float]:
        """Generate embedding for text"""
        if max_length is None:
            max_length = settings.BGE_MAX_LENGTH
            
        embedding = self.bge_model.encode(
            [text],
            batch_size=1,
            max_length=max_length
        )["dense_vecs"][0]
        
        return embedding.tolist()
    
    def get_relevant_docs(self, query: str, n_results: int = None) -> Dict:
        """Retrieve relevant documents from ChromaDB"""
        if n_results is None:
            n_results = settings.CHROMA_N_RESULTS
            
        query_embeddings = self.get_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_embeddings],
            n_results=n_results
        )
        return results
    
    def evaluate_documents(self, query: str, documents: List[str]) -> str:
        """
        Evaluate document quality using evaluation team.
        
        Returns:
            One of: 'proceed' (documents are good) or 'escalate' (quality issues detected)
        """
        # Format docs for evaluation
        docs_text = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(documents)])
        evaluation_input = f"USER QUERY:\n{query}\n\n{'='*60}\n\nRETRIEVED DOCUMENTS:\n{docs_text}"
        
        # Run evaluation team
        evaluation_response = self.evaluation_team.run(evaluation_input)
        evaluation = evaluation_response.content.strip().lower()
        
        return evaluation
    
    def make_rag_prompt(self, query: str, docs: List[str]) -> str:
        """Create RAG prompt with context"""
        context = "\n".join(f"- {doc}" for doc in docs)
        prompt = f"""Vous êtes un assistant de support technique pour Doxa. Votre rôle est de répondre aux questions des utilisateurs en vous basant UNIQUEMENT sur la documentation fournie.

RÈGLES STRICTES :
1. Répondez UNIQUEMENT avec les informations présentes dans le contexte ci-dessous
2. Si l'information n'est pas explicitement mentionnée dans le contexte, répondez : "Cette information n'est pas disponible dans la documentation fournie. Je vous recommande de contacter support@doxa.dz pour plus de détails."
3. Ne faites AUCUNE supposition, déduction ou utilisation de connaissances externes
4. Citez les informations pertinentes du contexte dans votre réponse
5. Si plusieurs sources du contexte sont pertinentes, combinez-les de manière cohérente
6. Soyez précis et concis - évitez les informations non pertinentes
7. Si la question nécessite des détails qui ne sont que partiellement dans le contexte, indiquez clairement ce qui est disponible et ce qui ne l'est pas

CONTEXTE DOCUMENTAIRE :
{context}

---

QUESTION DE L'UTILISATEUR : {query}

VOTRE RÉPONSE :"""
        return prompt
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini"""
        response = self.gemini_model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": settings.GEMINI_MAX_OUTPUT_TOKENS,
                "temperature": settings.GEMINI_TEMPERATURE
            }
        )
        
        # Handle response errors
        if not response.candidates:
            return "Error: No response generated."
        
        candidate = response.candidates[0]
        
        if candidate.finish_reason == 3:
            return "Error: Response blocked by safety filters."
        elif candidate.finish_reason == 2:
            return "Error: Response exceeded maximum token limit."
        elif candidate.finish_reason not in [0, 1]:
            return f"Error: Response finished with reason code {candidate.finish_reason}."
        
        if not candidate.content.parts:
            return "Error: No content in response."
        
        return response.text
    
    def calculate_confidence_score(self, query: str, response: str, relevant_docs_count: int, evaluation_result: str) -> float:
        """
        Calculate confidence score AFTER RAG generates response from knowledge base.
        This measures how confident we are in the RAG-generated answer.
        
        Args:
            query: Original user query
            response: Generated response from RAG
            relevant_docs_count: Number of relevant documents retrieved
            evaluation_result: Document evaluation result ('proceed' or 'escalate')
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence_prompt = f"""
        User Query: {query}
        Query Clarity: {'clear' if len(query.split()) > 3 else 'vague'}
        AI Response from Knowledge Base: {response}
        Number of Relevant Documents Retrieved: {relevant_docs_count}
        Document Quality Evaluation: {evaluation_result}
        
        Based on the above information, calculate a confidence score (0-100) for how confident we are in this RAG-generated response.
        Consider:
        - Number and quality of retrieved documents
        - How well the response answers the query
        - Document evaluation result
        
        Return ONLY a number between 0 and 100.
        """
        
        try:
            confidence_response = self.confidence_agent.run(confidence_prompt)
            confidence_text = confidence_response.content.strip()
            # Extract number from response
            confidence = float(''.join(c for c in confidence_text if c.isdigit() or c == '.'))
            if confidence > 1.0:
                confidence = confidence / 100  # Convert percentage to decimal
            return round(confidence, 2)
        except Exception as e:
            print(f"   ⚠️ Confidence calculation failed: {e}. Using fallback.")
            # Fallback confidence calculation based on docs and evaluation
            base_confidence = 0.5
            
            # Document evaluation score
            if evaluation_result == "proceed":
                base_confidence += 0.3
            
            # Document count score
            if relevant_docs_count >= 5:
                base_confidence += 0.15
            elif relevant_docs_count >= 3:
                base_confidence += 0.10
            elif relevant_docs_count >= 1:
                base_confidence += 0.05
            
            return min(base_confidence, 0.95)
    
    def query_with_feedback_loop(
        self, 
        user_query: str, 
        max_retries: int = 3
    ) -> Dict[str, any]:
        """
        Query RAG with feedback loop - retries if documents are low quality.
        
        Pipeline:
        1. Retrieve documents
        2. Evaluate document quality
        3. If safe/multiple_answers → Generate response
        4. If contradictory/missing_knowledge → Refine query and retry
        5. After max_retries → Escalate to human
        
        Args:
            user_query: User's question
            max_retries: Maximum retry attempts (default: 3)
            
        Returns:
            Dict with status, response, attempts, and metadata
        """
        refined_query = user_query
        feedback_history = []
        
        for attempt in range(1, max_retries + 1):
            print(f"   🔄 Attempt {attempt}/{max_retries}...")
            
            # STEP 1: Retrieve documents (increase n_results on retry)
            n_results = settings.CHROMA_N_RESULTS + (attempt - 1) * 2  # 6, 8, 10
            results = self.get_relevant_docs(refined_query, n_results=min(n_results, 15))
            docs = results['documents'][0]
            
            print(f"   📚 Retrieved {len(docs)} documents")
            
            # STEP 2: Evaluate document quality
            print(f"   🔍 Evaluating document quality...")
            evaluation = self.evaluate_documents(refined_query, docs)
            
            print(f"   ✅ Evaluation: {evaluation}")
            
            # STEP 3: If safe or multiple_answers, generate response (less strict!)
            if evaluation in ["safe", "multiple_answers"]:
                prompt = self.make_rag_prompt(user_query, docs)
                response_text = self.generate_response(prompt)
                
                # STEP 4: Calculate confidence score AFTER getting response from knowledge base
                print(f"   📊 Calculating confidence score for RAG response...")
                confidence_score = self.calculate_confidence_score(
                    query=user_query,
                    response=response_text,
                    relevant_docs_count=len(docs),
                    evaluation_result=evaluation
                )
                print(f"   ✅ Confidence Score: {confidence_score}")
                
                success_msg = f"Successfully resolved after {attempt} attempt(s)" if attempt > 1 else ""
                
                return {
                    "classification_result": "doxa_related",
                    "evaluation_result": evaluation,
                    "should_escalate": False,
                    "response": response_text,
                    "attempts": attempt,
                    "relevant_docs_count": len(docs),
                    "confidence_score": confidence_score,
                    "success_message": success_msg,
                    "reason": f"Documents evaluated as safe to proceed",
                    "dev_notes": "No escalation needed - query answered successfully",
                    "query": user_query
                }
            
            # STEP 4: Escalate needed - retry or escalate
            if attempt < max_retries:
                print(f"   ⚠️ Quality issues detected. Refining query...")
                
                # Refine query for retry
                feedback_history.append(f"Attempt {attempt}: Document quality issues detected")
                refined_query = f"{user_query} (Previous search had quality issues - need better documentation)"
                
                print(f"   🔄 Refined query: {refined_query}")
            else:
                # Max retries reached - escalate to human
                print(f"   ❌ Failed after {max_retries} attempts. Escalating...")
                
                escalation_msg = f"""⚠️ Je n'ai pas pu trouver une réponse fiable après {max_retries} tentatives.

Problème rencontré : Document quality issues

📞 Votre demande sera escaladée à un agent humain.
Veuillez contacter : support@doxa.dz

Un agent vous répondra dans les plus brefs délais avec des informations précises.

Référence : ESCALATION-QUALITY-{attempt}"""
                
                # Dev guidance for escalation
                dev_notes = {
                    "escalation_type": "DOCUMENT_QUALITY_ISSUES",
                    "action_required": "Human agent should review query and provide accurate answer",
                    "send_to_agent": ["user_query", "feedback_history", "retrieved_documents"],
                    "priority": "HIGH"
                }
                
                return {
                    "classification_result": "doxa_related",
                    "evaluation_result": evaluation,
                    "should_escalate": True,
                    "response": escalation_msg,
                    "attempts": attempt,
                    "feedback_history": feedback_history,
                    "reason": f"Failed after {attempt} attempts due to document quality issues",
                    "dev_notes": dev_notes
                }
        
        # Safety fallback (should not reach here)
        return {
            "classification_result": "doxa_related",
            "evaluation_result": "unknown",
            "should_escalate": True,
            "response": "⚠️ Votre demande nécessite l'assistance d'un agent humain. Contactez support@doxa.dz",
            "reason": "Unknown error in feedback loop",
            "dev_notes": {
                "escalation_type": "SYSTEM_ERROR",
                "action_required": "Debug feedback loop logic",
                "send_to_agent": ["user_query", "full_error_context"],
                "priority": "CRITICAL"
            },
            "query": user_query
        }
    
    def query_doxa_rag(self, user_query: str) -> Dict[str, any]:
        """
        Standard RAG query (backward compatible with existing code).
        Uses feedback loop internally.
        """
        return self.query_with_feedback_loop(user_query, max_retries=3)


# Global instance
enhanced_rag_service = EnhancedRAGService()
