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
            
            # Get confidence score
            confidence_response = evaluation_confidence_agent.run(evaluation_input)
            confidence_score = int(confidence_response.content.strip())
            
            print(f"   ✅ Evaluation result: {evaluation} (confidence: {confidence_score}%)")
            
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
                    "classification_result": "doxa_related",
                    "evaluation_result": evaluation,
                    "confidence_score": confidence_score,
                    "is_safe": True,
                    "response": response.text,
                    "attempts": attempt,
                    "success_message": success_msg,
                    "reason": f"Documents evaluated as {evaluation} with {confidence_score}% confidence",
                    "dev_notes": "No escalation needed - query answered successfully"
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
                
                # Dev guidance for escalation
                if evaluation == "contradictory":
                    dev_notes = {
                        "escalation_type": "CONTRADICTORY_DOCUMENTS",
                        "action_required": "Human agent should review source documents and resolve conflicts",
                        "send_to_agent": ["user_query", "conflicting_documents", "feedback_history"],
                        "priority": "MEDIUM"
                    }
                elif evaluation == "missing_knowledge":
                    dev_notes = {
                        "escalation_type": "KNOWLEDGE_GAP",
                        "action_required": "Agent should answer from external knowledge or update docs",
                        "send_to_agent": ["user_query", "attempted_searches", "feedback_history"],
                        "priority": "HIGH"
                    }
                else:
                    dev_notes = {
                        "escalation_type": "UNKNOWN_ISSUE",
                        "action_required": "Manual review required",
                        "send_to_agent": ["user_query", "all_context"],
                        "priority": "HIGH"
                    }
                
                return {
                    "classification_result": "doxa_related",
                    "evaluation_result": evaluation,
                    "confidence_score": confidence_score,
                    "is_safe": False,
                    "response": escalation_msg,
                    "attempts": attempt,
                    "feedback_history": feedback_history,
                    "reason": f"Failed after {attempt} attempts due to {evaluation}",
                    "dev_notes": dev_notes
                }
        
        # Should not reach here, but safety fallback
        return {
            "classification_result": "doxa_related",
            "evaluation_result": "unknown",
            "confidence_score": 0,
            "is_safe": False,
            "response": "⚠️ Votre demande nécessite l'assistance d'un agent humain. Contactez support@doxa.dz",
            "reason": "Unknown error in feedback loop",
            "dev_notes": {
                "escalation_type": "SYSTEM_ERROR",
                "action_required": "Debug feedback loop logic",
                "send_to_agent": ["user_query", "full_error_context"],
                "priority": "CRITICAL"
            }
        }
        
    except Exception as e:
        return {
            "classification_result": "doxa_related",
            "evaluation_result": "error",
            "confidence_score": 0,
            "is_safe": False,
            "response": f"RAG Pipeline Error: {str(e)}",
            "reason": f"Technical error: {str(e)}",
            "dev_notes": {
                "escalation_type": "TECHNICAL_ERROR",
                "action_required": "Debug RAG pipeline",
                "send_to_agent": ["error_message", "stack_trace"],
                "priority": "CRITICAL"
            }
        }

class QueryCategory(BaseModel):
    """Structured output for query classification - returns ONLY the category label."""
    category: Literal["spam", "aggressive", "sensitive", "out_of_scope", "ambiguous", "doxa_related"] = Field(
        ..., 
        description="The classification category. Must be exactly one of: spam, aggressive, sensitive, out_of_scope, ambiguous, doxa_related"
    )

mistral_model = MistralChat(id="mistral-small-latest", temperature=0.1)

# ============================================================================
# CONFIDENCE SCORING AGENTS
# ============================================================================

classification_confidence_agent = Agent(
    name="Classification Confidence Agent",
    model=mistral_model,
    description="Evaluates confidence level of classification decision.",
    markdown=True,
    instructions=[
        "Evaluate confidence in classification decision on scale 0-100%.",
        "",
        "HIGH CONFIDENCE (80-100%):",
        "- Clear, unambiguous query",
        "- Strong indicators of category",
        "- No edge cases",
        "",
        "MEDIUM CONFIDENCE (50-79%):",
        "- Some ambiguity but leans toward category",
        "- Could fit multiple categories but one is dominant",
        "",
        "LOW CONFIDENCE (0-49%):",
        "- Borderline case",
        "- Ambiguous indicators",
        "- Could easily be reclassified",
        "",
        "Response format: ONLY a number 0-100",
        "Examples:",
        "- Clear spam 'asdfasdf': 95",
        "- Borderline question: 55",
        "- Very unclear: 30"
    ]
)

evaluation_confidence_agent = Agent(
    name="Evaluation Confidence Agent",
    model=mistral_model,
    description="Evaluates confidence in document evaluation decision.",
    markdown=True,
    instructions=[
        "Evaluate confidence that retrieved documents can properly answer query on scale 0-100%.",
        "",
        "HIGH CONFIDENCE (80-100%):",
        "- Documents directly address query",
        "- Clear, unambiguous information",
        "- Multiple sources confirm same answer",
        "",
        "MEDIUM CONFIDENCE (50-79%):",
        "- Documents partially answer query",
        "- Some relevant info but gaps exist",
        "- Answer requires inference",
        "",
        "LOW CONFIDENCE (0-49%):",
        "- Documents barely relevant",
        "- Contradictory or missing information",
        "- Cannot confidently answer",
        "",
        "Response format: ONLY a number 0-100",
        "Examples:",
        "- Perfect match docs: 95",
        "- Partial coverage: 65",
        "- Poor match: 25"
    ]
)

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
    description="Detects vague or unclear queries needing clarification, including greetings.",
    markdown=True,
    instructions=[
        "Detect ambiguous queries that lack sufficient context, including greetings without questions.",
        "",
        "AMBIGUOUS if:",
        "- Generic help requests: 'help', 'i need help', 'help me', 'need assistance'",
        "- Vague references: 'help me with this', 'how do I do that', 'fix this'",
        "- Too vague: 'that thing', 'it', 'the issue'",
        "- Missing context: 'how to fix?' (fix what?)",
        "- Unclear pronouns without context: 'can it do this?' (what is 'it'?)",
        "- Single word questions: 'help?', 'how?', 'what?'",
        "- Greetings alone: 'hello', 'hi', 'hey', 'bonjour', 'salut', 'good morning', 'hi there'",
        "- Greetings + vague: 'hello, i need help', 'hi there, can you help?'",
        "",
        "CLEAR queries have specific intent:",
        "- 'How do I create a project in Doxa?' (specific action)",
        "- 'What are the pricing plans?' (specific question)",
        "- 'I need help resetting my password' (specific problem)",
        "- 'Hello, how do I create a project?' (greeting + specific question = CLEAR)",
        "",
        "If lacks context, too vague, or just greeting: respond ONLY with 'ambiguous'",
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
        "5. 'ambiguous' - too vague, lacks context, greetings alone (e.g. 'help', 'i need help', 'hello', 'hi', 'bonjour')",
        "6. 'doxa_related' - valid specific query about Doxa platform",
        "",
        "CRITICAL RULES:",
        "- Greetings alone ('hi', 'hello', 'bonjour') = 'ambiguous'",
        "- Greetings + vague ('hi, help me') = 'ambiguous'",
        "- Greetings + specific question ('hi, pricing plans?') = 'doxa_related'",
        "- General knowledge questions MUST be 'out_of_scope', NOT 'doxa_related'",
        "",
        "🚨 ABSOLUTE OUTPUT RULE - THIS IS CRITICAL:",
        "Your response must be EXACTLY ONE WORD. Nothing else. No punctuation. No explanation.",
        "VALID outputs: spam | aggressive | sensitive | out_of_scope | ambiguous | doxa_related",
        "",
        "WRONG outputs that will cause errors:",
        "❌ 'Hello! How can I assist you today?'",
        "❌ 'The query is ambiguous'",
        "❌ '{\"category\": \"ambiguous\"}'",
        "❌ 'ambiguous.'",
        "❌ 'Category: ambiguous'",
        "",
        "CORRECT outputs:",
        "✅ ambiguous",
        "✅ doxa_related",
        "✅ out_of_scope",
        "✅ spam",
        "",
        "Examples with EXACT expected output:",
        "Input: 'hi' → Output: ambiguous",
        "Input: 'hello' → Output: ambiguous",
        "Input: 'bonjour' → Output: ambiguous",
        "Input: 'pricing plans' → Output: doxa_related",
        "Input: 'where is paris' → Output: out_of_scope",
        "Input: 'asdfgh' → Output: spam",
        "",
        "REMEMBER: Just the category word. Nothing else. NO greetings, NO sentences, NO explanations."
    ]
)

def process_query(user_query: str) -> dict:
    """
    Process user query through classification and RAG pipeline.
    
    Args:
        user_query: The user's question/query string
        
    Returns:
        dict: Complete result with classification, confidence, safety status, response, and metadata
    """
    if not user_query or not user_query.strip():
        return {
            "classification_result": "invalid_input",
            "confidence_score": 0,
            "is_safe": False,
            "reason": "Empty or invalid query provided",
            "response": "Error: No query provided.",
            "dev_notes": {
                "escalation_type": "INVALID_INPUT",
                "action_required": "None - validation error",
                "send_to_agent": [],
                "priority": "LOW"
            }
        }
    
    # Run classification with structured output
    classification_response = classification_team.run(user_query)
    
    # Extract classification from structured response
    if hasattr(classification_response, 'content'):
        classification_text = classification_response.content.strip().lower()
    else:
        classification_text = str(classification_response).strip().lower()
    
    # Parse structured output if using response_model
    if 'category' in classification_text or '{' in classification_text:
        try:
            import json
            if isinstance(classification_response.content, str):
                data = json.loads(classification_response.content)
                classification = data.get('category', 'unknown').lower()
            else:
                classification = classification_text
        except:
            classification = classification_text
    else:
        classification = classification_text
    
    # Clean up classification - extract just the category word
    valid_categories = ['spam', 'aggressive', 'sensitive', 'out_of_scope', 'ambiguous', 'doxa_related']
    classification = classification.replace('_', ' ').strip()
    
    # Find matching category
    matched_category = None
    for category in valid_categories:
        if category.replace('_', ' ') in classification or category in classification:
            matched_category = category
            break
    
    if not matched_category:
        # If still no match, default based on content
        if any(word in classification for word in ['hello', 'hi', 'bonjour', 'greeting']):
            matched_category = 'ambiguous'
        else:
            matched_category = 'unknown'
    
    classification = matched_category
    
    # Get confidence score for classification
    confidence_response = classification_confidence_agent.run(f"Query: {user_query}\nClassification: {classification}")
    classification_confidence = int(confidence_response.content.strip())
    
    # Base result structure
    result = {
        "classification_result": classification,
        "confidence_score": classification_confidence,
        "query": user_query
    }
    
    # Base result structure
    result = {
        "classification_result": classification,
        "confidence_score": classification_confidence,
        "query": user_query
    }
    
    # Handle based on classification
    if classification == "doxa_related":
        rag_result = run_rag_pipeline(user_query)
        
        # Merge RAG result with base result
        result.update({
            "evaluation_result": rag_result.get('evaluation_result', 'unknown'),
            "confidence_score": rag_result['confidence_score'],  # Override with RAG confidence
            "is_safe": rag_result['is_safe'],
            "response": rag_result['response'],
            "reason": rag_result['reason'],
            "attempts": rag_result.get('attempts', 1),
            "dev_notes": rag_result.get('dev_notes', "No escalation needed")
        })
        
        if 'feedback_history' in rag_result:
            result['feedback_history'] = rag_result['feedback_history']
        if 'success_message' in rag_result:
            result['success_message'] = rag_result['success_message']
    
    elif classification == "spam":
        result.update({
            "is_safe": False,
            "reason": "Query appears to be spam/gibberish",
            "response": "This appears to be spam or nonsense. Please provide a valid query.",
            "dev_notes": {
                "escalation_type": "SPAM_DETECTED",
                "action_required": "None - auto-rejected",
                "send_to_agent": [],
                "priority": "LOW",
                "note": "Do NOT send spam queries to human agents"
            }
        })
    
    elif classification == "aggressive":
        result.update({
            "is_safe": False,
            "reason": "Aggressive or abusive language detected",
            "response": "Your message contains aggressive language. Please rephrase politely.",
            "dev_notes": {
                "escalation_type": "AGGRESSIVE_LANGUAGE",
                "action_required": "Log incident, may require moderation",
                "send_to_agent": ["user_id", "message_text", "timestamp"],
                "priority": "MEDIUM",
                "note": "Send to agent for abuse tracking"
            }
        })
    
    elif classification == "sensitive":
        result.update({
            "is_safe": False,
            "reason": "Sensitive personal data detected in query",
            "response": "Your query contains sensitive personal information. Please avoid sharing private data.",
            "dev_notes": {
                "escalation_type": "SENSITIVE_DATA",
                "action_required": "Redact/delete sensitive data from logs",
                "send_to_agent": ["redacted_query", "data_type_detected"],
                "priority": "HIGH",
                "note": "DO NOT send raw sensitive data to agents"
            }
        })
    
    elif classification == "out_of_scope":
        result.update({
            "is_safe": False,
            "reason": "Query not related to Doxa platform",
            "response": "This question is outside the scope of Doxa platform support. I can only help with questions about Doxa project management platform.",
            "dev_notes": {
                "escalation_type": "OUT_OF_SCOPE",
                "action_required": "None - auto-rejected",
                "send_to_agent": [],
                "priority": "LOW",
                "note": "Do NOT send out-of-scope queries unless pattern emerges"
            }
        })
    
    elif classification == "ambiguous":
        result.update({
            "is_safe": False,
            "reason": "Query too vague, lacks context, or is just a greeting",
            "response": "Hello! I'm here to help with questions about Doxa. Please ask a specific question. Example: 'What are the pricing plans?' or 'How do I create a project in Doxa?'",
            "dev_notes": {
                "escalation_type": "AMBIGUOUS_QUERY",
                "action_required": "Prompt user for clarification",
                "send_to_agent": ["user_id", "original_query"],
                "priority": "LOW",
                "note": "Send to agent only if user persists with vague queries"
            }
        })
    
    else:
        result.update({
            "is_safe": False,
            "reason": "Unknown classification result",
            "response": f"Unknown classification: {classification}",
            "dev_notes": {
                "escalation_type": "CLASSIFICATION_ERROR",
                "action_required": "Debug classification system",
                "send_to_agent": ["user_query", "classification_result", "full_context"],
                "priority": "CRITICAL"
            }
        })
    
    return result


def main():
    """
    Terminal interface for the DOXA RAG system.
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
    
    # Process query
    print("\n🔍 Step 1: Classifying query...")
    result = process_query(user_query)
    
    print(f"✅ Classification: {result['classification_result']} (confidence: {result['confidence_score']}%)")
    print("-" * 60)
    
    # Display results
    if result['classification_result'] == "doxa_related":
        print("\n🤖 Step 2: RAG Pipeline Results")
        print(f"\n   📊 Evaluation: {result.get('evaluation_result', 'unknown')}")
        print(f"   📊 Confidence Score: {result['confidence_score']}%")
        print(f"   📊 Is Safe: {result['is_safe']} (threshold: 60%)")
        print(f"   📊 Reason: {result['reason']}")
        
        # Show feedback history if escalated
        if not result['is_safe'] and 'feedback_history' in result:
            print(f"\n   📝 Retry History:")
            for feedback in result['feedback_history']:
                print(f"      • {feedback}")
        
        # Show success message if resolved after retries
        if 'success_message' in result and result['success_message']:
            print(result['success_message'])
        
        print("\n📋 Response:")
        print("=" * 60)
        print(result['response'])
        print("=" * 60)
        
        # Show developer notes for escalations
        if not result['is_safe'] and isinstance(result.get('dev_notes'), dict):
            print("\n🔧 Developer Notes:")
            dev_notes = result['dev_notes']
            print(f"   Escalation Type: {dev_notes.get('escalation_type', 'N/A')}")
            print(f"   Action Required: {dev_notes.get('action_required', 'N/A')}")
            print(f"   Priority: {dev_notes.get('priority', 'N/A')}")
            print(f"   Send to Agent: {', '.join(dev_notes.get('send_to_agent', []))}")
            print(f"\n🚨 ESCALATION: Query forwarded to human support.")
    
    else:
        # Non-doxa classifications
        print(f"\n   📊 Confidence Score: {result['confidence_score']}%")
        print(f"   📊 Is Safe: {result['is_safe']}")
        print(f"   📊 Reason: {result['reason']}")
        print(f"\n⚠️ Response: {result['response']}")
        
        if isinstance(result.get('dev_notes'), dict):
            print("\n🔧 Developer Notes:")
            dev_notes = result['dev_notes']
            print(f"   Escalation Type: {dev_notes.get('escalation_type', 'N/A')}")
            print(f"   Action Required: {dev_notes.get('action_required', 'N/A')}")
            print(f"   Priority: {dev_notes.get('priority', 'N/A')}")
            send_to_agent = dev_notes.get('send_to_agent', [])
            if send_to_agent:
                print(f"   Send to Agent: {', '.join(send_to_agent)}")
            if 'note' in dev_notes:
                print(f"   Note: {dev_notes['note']}")

if __name__ == "__main__":
    main()
