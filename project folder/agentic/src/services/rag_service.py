"""
RAG service using BGE embeddings and ChromaDB
"""
import google.generativeai as genai
from chromadb import PersistentClient
from FlagEmbedding import BGEM3FlagModel
from typing import List, Dict

from ..config.settings import settings


class RAGService:
    """Service for RAG (Retrieval-Augmented Generation) operations"""
    
    def __init__(self):
        """Initialize RAG components"""
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
        
        # Initialize BGE model
        self.bge_model = BGEM3FlagModel(
            settings.BGE_MODEL_NAME,
            use_fp16=settings.BGE_USE_FP16
        )
        
        # Initialize ChromaDB
        self.chroma_client = PersistentClient(path=settings.CHROMA_PERSIST_PATH)
        self.collection = self.chroma_client.get_collection(
            name=settings.CHROMA_COLLECTION_NAME
        )
    
    def get_embedding(self, text: str, max_length: int = None) -> List[float]:
        """
        Generate a dense embedding for a text chunk using BGE-M3.
        
        Args:
            text: Input text chunk
            max_length: Maximum token length (uses settings default if None)
            
        Returns:
            Dense embedding vector as list
        """
        if max_length is None:
            max_length = settings.BGE_MAX_LENGTH
            
        embedding = self.bge_model.encode(
            [text],
            batch_size=1,
            max_length=max_length
        )["dense_vecs"][0]
        
        return embedding.tolist()
    
    def get_relevant_docs(self, user_query: str) -> Dict:
        """
        Retrieve relevant documents from ChromaDB.
        
        Args:
            user_query: The user's query
            
        Returns:
            ChromaDB query results
        """
        query_embeddings = self.get_embedding(user_query)
        results = self.collection.query(
            query_embeddings=[query_embeddings],
            n_results=settings.CHROMA_N_RESULTS
        )
        return results
    
    def make_rag_prompt(self, query: str, docs: List[str]) -> str:
        """
        Create a RAG prompt with context from retrieved documents.
        
        Args:
            query: User's query
            docs: List of relevant document chunks
            
        Returns:
            Formatted prompt string
        """
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
    
    def ask_rag(self, prompt: str) -> str:
        """
        Generate answer using Gemini model.
        
        Args:
            prompt: The formatted RAG prompt
            
        Returns:
            Generated answer text
        """
        response = self.gemini_model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": settings.GEMINI_MAX_OUTPUT_TOKENS,
                "temperature": settings.GEMINI_TEMPERATURE
            }
        )
        return response.text
    
    def query_doxa_rag(self, user_query: str) -> Dict[str, any]:
        """
        Process a user query through the RAG pipeline.
        
        Args:
            user_query: The user's question
            
        Returns:
            Dict with answer and metadata
        """
        # Get relevant documents
        relevant_docs = self.get_relevant_docs(user_query)
        
        # Create RAG prompt
        prompt = self.make_rag_prompt(user_query, relevant_docs['documents'][0])
        
        # Generate answer
        answer = self.ask_rag(prompt)
        
        return {
            "answer": answer,
            "relevant_docs_count": len(relevant_docs['documents'][0]),
            "query": user_query
        }


# Global instance
rag_service = RAGService()
