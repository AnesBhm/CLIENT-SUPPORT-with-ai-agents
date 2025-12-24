from agno.agent import Agent
from agno.team import Team
from pydantic import BaseModel, Field
from agno.models.mistral import MistralChat
from dotenv import load_dotenv, find_dotenv
from typing import Literal

load_dotenv(find_dotenv())

def run_rag_pipeline(user_query: str, max_retries: int = 3) -> dict:
    """
    Lazy-load and run RAG pipeline with feedback loop for non-safe cases.
    Retries up to max_retries times if evaluation is not safe.
    Returns dict with evaluation status and response.
    """
    try:
        import google.generativeai as genai
        from chromadb import PersistentClient
        from FlagEmbedding import BGEM3FlagModel
        
        # Initialize RAG components
        genai.configure(api_key='add key here')
        gemini_model = genai.GenerativeModel("gemini-2.5-flash")
        
        bge_model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
        chroma_client = PersistentClient(path='chroma_archive')
        chroma_collection = chroma_client.get_collection(name="test_collection")
        
        # Feedback loop state
        refined_query = user_query
        feedback_history = []
        
        for attempt in range(1, max_retries + 1):
            print(f"   🔄 Attempt {attempt}/{max_retries}...")
            
            # Get embedding
            embedding = bge_model.encode([refined_query], batch_size=1, max_length=8192)["dense_vecs"][0]
            
            # Retrieve relevant docs (increase n_results on retry)
            n_results = 6 + (attempt - 1) * 2  # 6, 8, 10 for attempts 1, 2, 3
            results = chroma_collection.query(query_embeddings=[embedding], n_results=min(n_results, 15))
            docs = results['documents'][0]
            
            # Format docs for evaluation
            docs_text = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(docs)])
            evaluation_input = f"USER QUERY:\n{refined_query}\n\n{'='*60}\n\nRETRIEVED DOCUMENTS:\n{docs_text}"
            
            # Evaluate chunk quality
            print(f"   🔍 Evaluating retrieved documents quality...")
            evaluation_response = evaluation_team.run(evaluation_input)
            evaluation = evaluation_response.content.strip().lower()
            
            print(f"   ✅ Evaluation result: {evaluation}")
            
            # If safe or multiple_answers, proceed with generation
            if evaluation in ["safe", "multiple_answers"]:
                if evaluation == "multiple_answers":
                    print("   ℹ️ Multiple answers detected - will present all options")
                
                # Generate response
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

QUESTION DE L'UTILISATEUR : {user_query}

VOTRE RÉPONSE :"""
                
                response = gemini_model.generate_content(
                    prompt,
                    generation_config={"max_output_tokens": 100000, "temperature": 0}
                )
                
                if not response.candidates:
                    return {"status": "error", "response": "Error: No response generated."}
                
                candidate = response.candidates[0]
                
                if candidate.finish_reason == 3:
                    return {"status": "error", "response": "Error: Response blocked by safety filters."}
                elif candidate.finish_reason == 2:
                    return {"status": "error", "response": "Error: Response exceeded maximum token limit."}
                elif candidate.finish_reason not in [0, 1]:
                    return {"status": "error", "response": f"Error: Response finished with reason code {candidate.finish_reason}."}
                
                if not candidate.content.parts:
                    return {"status": "error", "response": "Error: No content in response."}
                
                success_msg = f"\n✅ Successfully resolved after {attempt} attempt(s)" if attempt > 1 else ""
                return {
                    "status": evaluation,
                    "response": response.text,
                    "attempts": attempt,
                    "success_message": success_msg
                }
            
            # Not safe - prepare for retry or escalate
            if attempt < max_retries:
                # Refine query based on evaluation issue
                print(f"   ⚠️ Issue detected: {evaluation}. Refining query...")
                
                if evaluation == "contradictory":
                    feedback_history.append(f"Attempt {attempt}: Found contradictory information in documents.")
                    refined_query = f"{user_query} (Previous attempt found contradictions - need consistent information about this specific aspect)"
                
                elif evaluation == "missing_knowledge":
                    feedback_history.append(f"Attempt {attempt}: Documents lacked necessary information.")
                    refined_query = f"{user_query} (Previous search was too narrow - need more comprehensive documentation about this topic)"
                
                print(f"   🔄 Refined query: {refined_query}")
            else:
                # Max retries reached - escalate
                print(f"   ❌ Failed after {max_retries} attempts. Escalating to human agent...")
                
                escalation_msg = f"""⚠️ Je n'ai pas pu trouver une réponse fiable après {max_retries} tentatives.

Problème rencontré : {evaluation}

📞 Votre demande sera escaladée à un agent humain.
Veuillez contacter : support@doxa.dz

Un agent vous répondra dans les plus brefs délais avec des informations précises.

Référence : ESCALATION-{evaluation.upper()}-{attempt}"""
                
                return {
                    "status": f"escalated_{evaluation}",
                    "response": escalation_msg,
                    "attempts": attempt,
                    "feedback_history": feedback_history
                }
        
        # Should not reach here, but safety fallback
        return {
            "status": "escalated_unknown",
            "response": "⚠️ Votre demande nécessite l'assistance d'un agent humain. Contactez support@doxa.dz"
        }
        
    except Exception as e:
        return {"status": "error", "response": f"RAG Pipeline Error: {str(e)}"}

class QueryCategory(BaseModel):
    """Structured output for query classification - returns ONLY the category label."""
    category: Literal["spam", "aggressive", "sensitive", "out_of_scope", "ambiguous", "doxa_related"] = Field(
        ..., 
        description="The classification category. Must be exactly one of: spam, aggressive, sensitive, out_of_scope, ambiguous, doxa_related"
    )

mistral_model = MistralChat(id="mistral-small-latest", temperature=0.1)

# ============================================================================
# EVALUATION AGENTS - Check retrieved chunks quality before RAG generation
# ============================================================================

contradictory_agent = Agent(
    name="Contradiction Detector Agent",
    model=mistral_model,
    description="Detects if retrieved documents contain contradictory information.",
    markdown=True,
    instructions=[
        "Analyze the retrieved documents for contradictions.",
        "",
        "CONTRADICTORY if:",
        "- Different documents give opposite answers to the same question",
        "- Numbers/prices conflict (e.g., one says 500 DZD, another says 1000 DZD for same item)",
        "- Instructions contradict (e.g., one says 'click here', another says 'don't click here')",
        "- Dates or versions conflict",
        "",
        "NOT CONTRADICTORY if:",
        "- Documents discuss different topics",
        "- Documents provide complementary information",
        "- Slight wording differences but same meaning",
        "",
        "If contradictions exist: respond ONLY with 'contradictory'",
        "Otherwise: respond ONLY with 'consistent'"
    ]
)

missing_knowledge_agent = Agent(
    name="Missing Knowledge Agent",
    model=mistral_model,
    description="Detects if retrieved documents lack information to answer the query.",
    markdown=True,
    instructions=[
        "Check if retrieved documents contain enough information to answer the user's query.",
        "",
        "MISSING KNOWLEDGE if:",
        "- Query asks for specific details not in any document",
        "- Documents are vaguely related but don't answer the question",
        "- Key information needed to answer is absent",
        "- Documents discuss the topic but lack the requested specifics",
        "",
        "SUFFICIENT KNOWLEDGE if:",
        "- At least one document directly answers the query",
        "- Documents contain the requested information",
        "- Answer can be constructed from document content",
        "",
        "If information is missing: respond ONLY with 'missing'",
        "Otherwise: respond ONLY with 'sufficient'"
    ]
)

multiple_answers_agent = Agent(
    name="Multiple Answers Agent",
    model=mistral_model,
    description="Detects if documents provide multiple valid but different answers.",
    markdown=True,
    instructions=[
        "Check if documents provide multiple different answers (not contradictory, just different options).",
        "",
        "MULTIPLE ANSWERS if:",
        "- Documents list different valid options/methods (e.g., 3 pricing plans)",
        "- Multiple solutions are provided for same problem",
        "- Different approaches are mentioned",
        "",
        "SINGLE ANSWER if:",
        "- All documents point to one clear answer",
        "- Documents discuss different aspects but consistent conclusion",
        "",
        "If multiple distinct answers: respond ONLY with 'multiple'",
        "Otherwise: respond ONLY with 'single'"
    ]
)

# Team that evaluates retrieved chunks quality
evaluation_team = Team(
    model=mistral_model,
    name="Chunk Evaluation Team",
    markdown=True,
    members=[
        contradictory_agent,
        missing_knowledge_agent,
        multiple_answers_agent
    ],
    instructions=[
        "Evaluate retrieved documents for quality issues before RAG generation.",
        "",
        "EVALUATION PRIORITY (check in order, return first match):",
        "1. 'contradictory' - documents contain conflicting information",
        "2. 'missing_knowledge' - documents don't contain needed information",
        "3. 'multiple_answers' - documents provide multiple valid options (this is OK, just informative)",
        "4. 'safe' - documents are good quality, can proceed with RAG",
        "",
        "ABSOLUTE OUTPUT RULE:",
        "Your ENTIRE response must be ONLY ONE WORD from:",
        "contradictory OR missing_knowledge OR multiple_answers OR safe",
        "",
        "DO NOT write explanations. ONLY the category word.",
        "",
        "Examples:",
        "- If docs conflict on pricing: contradictory",
        "- If docs don't answer the query: missing_knowledge",
        "- If docs list 3 pricing plans: multiple_answers",
        "- If docs clearly answer query: safe"
    ]
)

# ============================================================================
# CLASSIFICATION AGENTS - Check query validity
# ============================================================================

# Agent that validates if query is about Doxa platform
rag_agent = Agent(
    name="RAG Pipeline Agent",
    model=mistral_model,
    description="Validates if user query is specifically about Doxa project management platform.",
    markdown=True,
    instructions=[
        "You are a gatekeeper for the Doxa RAG system.",
        "",
        "CONTEXT: Doxa is a SaaS collaborative project management platform.",
        "",
        "ACCEPT queries about (respond 'doxa_related'):",
        "✓ Explicitly mentions 'Doxa' by name",
        "✓ Project management features: create project, tasks, kanban, sprints, workflows",
        "✓ Pricing, payment plans, subscription, billing, costs, fees",
        "✓ Account features: login, password, user management, onboarding, signup",
        "✓ Integrations: Slack, Teams, GitHub, API, webhooks",
        "✓ Mobile app, desktop app, platform features",
        "✓ Support, troubleshooting, help with features",
        "✓ Team collaboration, invites, permissions, roles",
        "",
        "REJECT queries about (respond 'not_doxa'):",
        "✗ Geography: 'where is paris', 'capital of france'",
        "✗ Weather: 'what's the weather'",
        "✗ General knowledge: 'what is AI', 'who is X person'",
        "✗ Cooking, entertainment, sports, news",
        "✗ Health, fitness, personal advice",
        "✗ Other software (unless asking for Doxa comparison)",
        "",
        "KEY RULE: If query is about project management, pricing, accounts, or platform features, ACCEPT it.",
        "",
        "Response:",
        "- If about project management/Doxa features: 'doxa_related'",
        "- Otherwise: 'not_doxa'"
    ]
)

# Agents for each classification category
spam_agent = Agent(
    name="Spam Detector Agent",
    model=mistral_model,
    description="Detects spam, nonsense, or gibberish queries.",
    markdown=True,
    instructions=[
        "Detect spam/nonsense queries:",
        "- Random characters: 'asdfasdf', '!!!!!!'",
        "- Repeated words: 'hello hello hello hello'",
        "- Gibberish: 'ajskdjfhaksdf'",
        "- Empty or meaningless: '???', '...'",
        "",
        "If spam/nonsense: respond ONLY with 'spam'",
        "Otherwise: respond ONLY with 'valid'"
    ]
)

ambiguous_agent = Agent(
    name="Ambiguity Detector Agent",
    model=mistral_model,
    description="Detects vague or unclear queries needing clarification.",
    markdown=True,
    instructions=[
        "Detect ambiguous queries that lack sufficient context:",
        "- Generic help requests: 'help', 'i need help', 'help me', 'need assistance'",
        "- Vague references: 'help me with this', 'how do I do that', 'fix this'",
        "- Too vague: 'that thing', 'it', 'the issue'",
        "- Missing context: 'how to fix?' (fix what?)",
        "- Unclear pronouns without context: 'can it do this?' (what is 'it'?)",
        "- Single word questions: 'help?', 'how?', 'what?'",
        "",
        "CLEAR queries have specific intent:",
        "- 'How do I create a project in Doxa?' (specific action)",
        "- 'What are the pricing plans?' (specific question)",
        "- 'I need help resetting my password' (specific problem)",
        "",
        "If lacks context or too vague: respond ONLY with 'ambiguous'",
        "Otherwise: respond ONLY with 'clear'"
    ]
)

aggressive_agent = Agent(
    name="Aggression Detector Agent",
    model=mistral_model,
    description="Detects hostile, aggressive, or abusive language.",
    markdown=True,
    instructions=[
        "Detect aggressive/hostile language:",
        "- Insults, profanity, threats",
        "- Hostile tone: 'you idiots', 'this is garbage'",
        "- Demanding rudely: 'fix this NOW'",
        "",
        "Note: Frustration is OK if polite: 'I'm frustrated but...'",
        "",
        "If aggressive/abusive: respond ONLY with 'aggressive'",
        "Otherwise: respond ONLY with 'polite'"
    ]
)

sensitive_agent = Agent(
    name="Sensitive Data Detector Agent",
    model=mistral_model,
    description="Detects queries containing sensitive personal information.",
    markdown=True,
    instructions=[
        "Detect sensitive personal data:",
        "- Credit card numbers, SSN, passwords",
        "- Personal addresses, phone numbers",
        "- Medical records, financial details",
        "",
        "Note: Account issues like 'reset password' are OK (no actual data shared)",
        "",
        "If contains sensitive data: respond ONLY with 'sensitive'",
        "Otherwise: respond ONLY with 'safe'"
    ]
)

# Agent for non-Doxa queries
out_of_scope_agent = Agent(
    name="Out of Scope Agent",
    model=mistral_model,
    description="Detects queries completely unrelated to Doxa platform.",
    markdown=True,
    instructions=[
        "Detect queries that have ZERO relation to Doxa project management platform.",
        "",
        "OUT OF SCOPE examples (respond 'out_of_scope'):",
        "✗ 'where is paris located' - geography",
        "✗ 'what's the weather' - weather",
        "✗ 'how to cook pasta' - cooking",
        "✗ 'what is AI' - general knowledge",
        "✗ 'who won the game' - sports",
        "✗ 'latest news' - current events",
        "✗ 'tell me a joke' - entertainment",
        "✗ 'who is X person' - celebrity/people",
        "",
        "IN SCOPE - DO NOT classify as out_of_scope (respond 'relevant'):",
        "✓ 'payment plans' - pricing question",
        "✓ 'how to create project' - feature question",
        "✓ 'pricing' - about Doxa costs",
        "✓ 'integrate with Slack' - feature question",
        "✓ 'reset password' - account question",
        "✓ Any question about project management features",
        "",
        "CRITICAL: Questions about pricing, projects, tasks, accounts, features are IN SCOPE.",
        "",
        "Response:",
        "- If unrelated to software/project management: 'out_of_scope'",
        "- If related to platform features: 'relevant'"
    ]
)

# Team that coordinates classification agents
classification_team = Team(
    model=mistral_model,
    name="Query Classification Team",
    markdown=True,
    members=[
        spam_agent,
        aggressive_agent,
        sensitive_agent,
        out_of_scope_agent,
        ambiguous_agent,
        rag_agent
    ],
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
        "Your ENTIRE response must be ONLY ONE WORD from this list:",
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

def main():
    """
    Main function to run classification and RAG pipeline in terminal.
    """
    print("=" * 60)
    print("DOXA RAG SYSTEM - Terminal Interface")
    print("=" * 60)
    
    # Get user query
    user_query = input("\nEnter your question: ").strip()
    
    if not user_query:
        print("Error: No query provided.")
        return
    
    print(f"\n📝 Processing query: '{user_query}'")
    print("-" * 60)
    
    # Run classification
    print("\n🔍 Step 1: Classifying query...")
    classification_response = classification_team.run(user_query)
    classification = classification_response.content.strip().lower()
    
    print(f"✅ Classification: {classification}")
    print("-" * 60)
    
    # Handle based on classification
    if classification == "doxa_related":
        print("\n🤖 Step 2: Running RAG pipeline...")
        rag_result = run_rag_pipeline(user_query)
        
        print(f"\n   📊 RAG Status: {rag_result['status']}")
        
        # Show feedback history if escalated
        if rag_result['status'].startswith('escalated_') and 'feedback_history' in rag_result:
            print(f"\n   📝 Retry History:")
            for feedback in rag_result['feedback_history']:
                print(f"      • {feedback}")
        
        # Show success message if resolved after retries
        if 'success_message' in rag_result and rag_result['success_message']:
            print(rag_result['success_message'])
        
        print("\n📋 RAG Response:")
        print("=" * 60)
        print(rag_result['response'])
        print("=" * 60)
        
        # Additional info based on evaluation
        if rag_result['status'] == "multiple_answers":
            print("\nℹ️ Note: Multiple valid options were found in the documentation.")
        elif rag_result['status'].startswith('escalated_'):
            print(f"\n🚨 ESCALATION: Query forwarded to human support after {rag_result.get('attempts', 3)} attempts.")
    
    elif classification == "spam":
        print("\n⚠️ Response: This appears to be spam or nonsense. Please provide a valid query.")
    
    elif classification == "aggressive":
        print("\n⚠️ Response: Your message contains aggressive language. Please rephrase politely.")
    
    elif classification == "sensitive":
        print("\n⚠️ Response: Your query contains sensitive personal information. Please avoid sharing private data.")
    
    elif classification == "out_of_scope":
        print("\n⚠️ Response: This question is outside the scope of Doxa platform support.")
        print("I can only help with questions about Doxa project management platform.")
    
    elif classification == "ambiguous":
        print("\n⚠️ Response: Your question is too vague. Please provide more specific details.")
        print("Example: Instead of 'I need help', try 'How do I create a project in Doxa?'")
    
    else:
        print(f"\n⚠️ Unknown classification: {classification}")

if __name__ == "__main__":
    main()
