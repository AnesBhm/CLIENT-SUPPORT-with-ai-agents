
import google.generativeai as genai

import os
import pandas as pd
from chromadb import PersistentClient
from FlagEmbedding import BGEM3FlagModel

import google.generativeai as genai

genai.configure(api_key='AIzaSyC_LOAdwi2z2aEZlCCUYe0JK--azhfc2zA')
model_ai = genai.GenerativeModel("gemini-2.5-flash")

model = BGEM3FlagModel(
    "BAAI/bge-m3",
    use_fp16=True
)

def get_embedding(text: str, max_length: int = 8192):
    """
    Generate a dense embedding for a text chunk using BGE-M3.

    Args:
        text (str): Input text chunk
        max_length (int): Maximum token length

    Returns:
        numpy.ndarray: Dense embedding vector
    """
    embedding = model.encode(
        [text],
        batch_size=1,
        max_length=max_length
    )["dense_vecs"][0]

    return embedding

clientTestLocal = PersistentClient(path='chroma_archive')
collectionTestLocal = clientTestLocal.get_collection(name="test_collection")

def get_relevant_docs(user_query):
    query_embeddings = get_embedding(user_query)  # single vector
    results = collectionTestLocal.query(
        query_embeddings=[query_embeddings],  # wrap in list
        n_results=6
    )
    return results


def make_rag_prompt(query, docs):
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

def ask_rag(prompt, model):
    response = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": 100000, "temperature": 0}
    )
    return response.text

def query_doxa_rag(user_query):
    """
    Process a user query through the RAG pipeline.
    
    Args:
        user_query (str): The user's question
        
    Returns:
        str: The AI-generated answer based on relevant documents
    """
    # Get relevant documents
    relevant_docs = get_relevant_docs(user_query)
    
    # Create RAG prompt
    prompt = make_rag_prompt(user_query, relevant_docs['documents'][0])
    
    # Generate answer
    answer = ask_rag(prompt, model_ai)
    
    return answer

# Example usage:
if __name__ == "__main__":
    user_message = 'quelle sont les CAS DE FACTURATION SPÉCIFIQUES?'
    answer = query_doxa_rag(user_message)
    print(answer)




