"""
Advanced agents for query processing and response enhancement
"""
import json
import re
from agno.agent import Agent
from agno.models.mistral import MistralChat

from ..config.settings import settings


class AdvancedAgentFactory:
    """Factory for creating advanced processing agents"""
    
    def __init__(self):
        """Initialize Mistral model"""
        self.model = MistralChat(
            id=settings.MISTRAL_MODEL_ID,
            temperature=settings.MISTRAL_TEMPERATURE
        )
    
    def create_query_analyzer_agent(self) -> Agent:
        """
        Agent Query Analyzer - Creates summary (<100 words) and extracts 5-10 keywords.
        Returns structured metrics: summary, keywords.
        """
        return Agent(
            name="Query Analyzer Agent",
            model=self.model,
            description="Analyzes user query to create summary and extract keywords for RAG retrieval.",
            markdown=False,
            instructions=[
                "Analyze the user's query and return a structured analysis.",
                "",
                "YOUR TASK:",
                "1. Create a SUMMARY of the query (MAXIMUM 100 words, ideally 30-50 words)",
                "   - Capture the main intent and context",
                "   - Be concise but complete",
                "",
                "2. Extract 5-10 KEYWORDS from the query",
                "   - Include main topics, actions, and entities",
                "   - Include domain-specific terms (Doxa, project, task, etc.)",
                "   - Include synonyms if relevant",
                "",
                "OUTPUT FORMAT (STRICT JSON):",
                "{",
                '  "summary": "Brief summary of user intent in under 100 words",',
                '  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],',
                '  "word_count": <number of words in summary>,',
                '  "intent": "primary intent category"',
                "}",
                "",
                "INTENT CATEGORIES: how_to, information, troubleshooting, comparison, pricing, feature_request, account, complaint",
                "",
                "EXAMPLE INPUT: 'Comment créer un nouveau projet dans Doxa et inviter mon équipe?'",
                "EXAMPLE OUTPUT:",
                "{",
                '  "summary": "L\'utilisateur souhaite savoir comment créer un projet sur la plateforme Doxa et comment inviter des membres de son équipe à collaborer sur ce projet.",',
                '  "keywords": ["créer", "projet", "Doxa", "inviter", "équipe", "collaboration", "nouveau", "membres"],',
                '  "word_count": 28,',
                '  "intent": "how_to"',
                "}",
                "",
                "IMPORTANT: Return ONLY valid JSON. No markdown, no explanation, no additional text."
            ]
        )
    
    def create_query_intent_agent(self) -> Agent:
        """
        Agent that determines the specific intent behind the user's query.
        Helps route to the right processing pipeline.
        """
        return Agent(
            name="Query Intent Agent",
            model=self.model,
            description="Analyzes user query to determine specific intent and required action.",
            markdown=True,
            instructions=[
                "Analyze the user's query to determine their specific intent.",
                "",
                "INTENT CATEGORIES:",
                "",
                "1. 'how_to' - User wants step-by-step instructions",
                "   Examples: 'How do I...', 'Steps to...', 'Guide for...'",
                "",
                "2. 'information' - User wants factual information",
                "   Examples: 'What is...', 'Tell me about...', 'Explain...'",
                "",
                "3. 'troubleshooting' - User has a problem to solve",
                "   Examples: 'I can't...', 'Not working...', 'Error when...'",
                "",
                "4. 'comparison' - User wants to compare options",
                "   Examples: 'Difference between...', 'Which is better...', 'Compare...'",
                "",
                "5. 'pricing' - User asks about costs/plans",
                "   Examples: 'How much...', 'Pricing...', 'Cost of...'",
                "",
                "6. 'feature_request' - User wants to know if feature exists",
                "   Examples: 'Can I...', 'Does Doxa support...', 'Is it possible...'",
                "",
                "7. 'account' - User has account-related query",
                "   Examples: 'Reset password...', 'Change email...', 'Delete account...'",
                "",
                "OUTPUT FORMAT:",
                "Respond with ONLY the intent category, nothing else.",
                "Valid outputs: how_to, information, troubleshooting, comparison, pricing, feature_request, account",
                "",
                "Examples:",
                "Query: 'How do I create a project?' → how_to",
                "Query: 'What are the pricing plans?' → pricing",
                "Query: 'I can't login' → troubleshooting",
                "Query: 'Does Doxa support Slack integration?' → feature_request"
            ]
        )
    
    def create_context_enrichment_agent(self) -> Agent:
        """
        Agent that enriches the query with additional context for better RAG retrieval.
        Expands abbreviations, adds synonyms, identifies key terms.
        """
        return Agent(
            name="Context Enrichment Agent",
            model=self.model,
            description="Enriches user query with additional context for better document retrieval.",
            markdown=True,
            instructions=[
                "Enrich the user's query to improve document retrieval.",
                "",
                "ENRICHMENT TASKS:",
                "",
                "1. EXPAND ABBREVIATIONS",
                "   - 'PM' → 'project management'",
                "   - 'API' → 'application programming interface'",
                "   - 'UI' → 'user interface'",
                "",
                "2. ADD DOMAIN CONTEXT",
                "   - 'project' → 'Doxa project, project management, project creation'",
                "   - 'task' → 'task management, assign tasks, task tracking'",
                "",
                "3. IDENTIFY KEY TERMS",
                "   - Extract important keywords: 'create', 'project', 'team'",
                "   - Add synonyms: 'create' → 'make, add, new'",
                "",
                "4. ADD RELATED CONCEPTS",
                "   - If query mentions 'pricing' → add 'subscription, plans, cost, billing'",
                "   - If query mentions 'login' → add 'authentication, access, credentials'",
                "",
                "OUTPUT FORMAT:",
                "Return enriched query with additional context terms.",
                "",
                "Example:",
                "Input: 'How to create PM in Doxa?'",
                "Output: 'How to create project management project in Doxa platform project creation new project add project'",
                "",
                "Input: 'Pricing plans'",
                "Output: 'Pricing plans subscription costs billing fees payment tiers packages'",
                "",
                "Keep it concise but comprehensive. Focus on terms that will match documentation."
            ]
        )
    
    def create_response_validation_agent(self) -> Agent:
        """
        Agent that validates if the RAG response actually answers the user's question.
        Checks for hallucinations and relevance.
        """
        return Agent(
            name="Response Validation Agent",
            model=self.model,
            description="Validates that the generated response actually answers the user's question.",
            markdown=True,
            instructions=[
                "Validate if the AI response properly answers the user's question.",
                "",
                "VALIDATION CHECKS:",
                "",
                "1. RELEVANCE CHECK",
                "   - Does the response address the user's specific question?",
                "   - Are the key points from the question covered?",
                "",
                "2. COMPLETENESS CHECK",
                "   - Is the answer complete or partial?",
                "   - Are there missing critical details?",
                "",
                "3. ACCURACY CHECK",
                "   - Does the response stay within the provided context?",
                "   - Are there any invented details not in the docs?",
                "",
                "4. CLARITY CHECK",
                "   - Is the answer clear and understandable?",
                "   - Is it structured well (steps, bullets, etc.)?",
                "",
                "INPUT:",
                "You will receive:",
                "- Original user question",
                "- AI-generated response",
                "- Source documents used",
                "",
                "OUTPUT FORMAT:",
                "Respond with ONLY one of these:",
                "- 'valid' - Response is good, answers the question properly",
                "- 'partial' - Response is partially correct but missing details",
                "- 'irrelevant' - Response doesn't answer the question",
                "- 'hallucination' - Response contains information not in docs",
                "",
                "Examples:",
                "Question: 'How to create a project?'",
                "Response: 'Click Projects > New Project > Fill details'",
                "Validation: valid",
                "",
                "Question: 'What are pricing plans?'",
                "Response: 'Doxa offers great features for teams.'",
                "Validation: irrelevant"
            ]
        )
    
    def create_language_detector_agent(self) -> Agent:
        """
        Agent that detects the language of the user's query.
        Supports: French (fr), English (en), Arabic (ar), Spanish (es).
        """
        return Agent(
            name="Language Detector Agent",
            model=self.model,
            description="Detects the language of user input for appropriate response formatting.",
            markdown=False,
            instructions=[
                "Detect the language of the user's message.",
                "",
                "SUPPORTED LANGUAGES:",
                "- 'fr' - French (Français)",
                "- 'en' - English",
                "- 'ar' - Arabic (العربية)",
                "- 'es' - Spanish (Español)",
                "",
                "OUTPUT FORMAT:",
                "Return ONLY the 2-letter language code: fr, en, ar, or es",
                "",
                "EXAMPLES:",
                "Input: 'Comment créer un projet?' → fr",
                "Input: 'How do I create a project?' → en",
                "Input: 'كيف أنشئ مشروع؟' → ar",
                "Input: '¿Cómo creo un proyecto?' → es",
                "",
                "RULES:",
                "- If mixed languages, choose the dominant one",
                "- If uncertain, default to 'fr' (French)",
                "- Return ONLY the code, no explanation"
            ]
        )
    
    def create_response_composer_agent(self) -> Agent:
        """
        Agent Response Composer - Formats AI responses with structured template.
        Template: Thanks + Problem Recap + Solution + Next Action
        Adapts to detected language.
        """
        return Agent(
            name="Response Composer Agent",
            model=self.model,
            description="Composes professional, structured responses with proper template.",
            markdown=True,
            instructions=[
                "Format the AI response into a professional, structured customer support response.",
                "",
                "TEMPLATE STRUCTURE (4 PARTS):",
                "",
                "1. REMERCIEMENTS (Thanks)",
                "   - Brief thank you for contacting support",
                "   - FR: 'Merci de nous avoir contactés.'",
                "   - EN: 'Thank you for reaching out to us.'",
                "",
                "2. REFORMULATION DU PROBLÈME (Problem Recap)",
                "   - Show understanding of the issue",
                "   - FR: 'Nous comprenons que vous souhaitez [problème].'",
                "   - EN: 'We understand that you would like to [problem].'",
                "",
                "3. SOLUTION DÉTAILLÉE (Detailed Solution)",
                "   - Provide the actual answer/solution",
                "   - Use bullet points or numbered steps if applicable",
                "   - Be clear and actionable",
                "",
                "4. PROCHAINE ACTION (Next Action / CTA)",
                "   - Tell user what to do next",
                "   - FR: 'N'hésitez pas à nous recontacter si vous avez d'autres questions.'",
                "   - EN: 'Please don't hesitate to reach out if you have further questions.'",
                "   - Include contact: support@doxa.dz",
                "",
                "INPUT FORMAT:",
                "You will receive:",
                "- language: 'fr', 'en', 'ar', or 'es'",
                "- user_query: The original question",
                "- raw_answer: The AI-generated answer from RAG",
                "",
                "OUTPUT FORMAT:",
                "Return the formatted response following the 4-part template.",
                "Use appropriate language based on the 'language' parameter.",
                "",
                "EXAMPLE OUTPUT (French):",
                "---",
                "Merci de nous avoir contactés concernant Doxa.",
                "",
                "Nous comprenons que vous souhaitez savoir comment créer un nouveau projet.",
                "",
                "Voici les étapes à suivre :",
                "1. Connectez-vous à votre compte Doxa",
                "2. Cliquez sur le bouton '+ Nouveau Projet'",
                "3. Remplissez les informations requises",
                "4. Cliquez sur 'Créer'",
                "",
                "N'hésitez pas à nous recontacter si vous avez d'autres questions.",
                "Contact : support@doxa.dz",
                "---",
                "",
                "TONE: Professional, helpful, concise. No hallucinations."
            ]
        )
    
    def create_confidence_scoring_agent(self) -> Agent:
        """
        Agent that calculates a confidence score for the response quality.
        Helps determine if human escalation is needed.
        """
        return Agent(
            name="Confidence Scoring Agent",
            model=self.model,
            description="Calculates confidence score for the AI response quality.",
            markdown=True,
            instructions=[
                "Calculate a confidence score (0.0 to 1.0) for the AI response.",
                "",
                "SCORING FACTORS:",
                "",
                "1. DOCUMENT RELEVANCE (40%)",
                "   - How relevant are the retrieved documents?",
                "   - High: 0.4, Medium: 0.25, Low: 0.1",
                "",
                "2. RESPONSE COMPLETENESS (30%)",
                "   - Does response fully answer the question?",
                "   - Complete: 0.3, Partial: 0.15, Incomplete: 0.0",
                "",
                "3. QUERY CLARITY (20%)",
                "   - How clear was the user's question?",
                "   - Clear: 0.2, Somewhat clear: 0.1, Vague: 0.0",
                "",
                "4. SOURCE QUALITY (10%)",
                "   - Are sources official documentation?",
                "   - Official: 0.1, Community: 0.05, Unknown: 0.0",
                "",
                "CONFIDENCE LEVELS:",
                "- 0.80 - 1.00: High confidence - Auto-resolve",
                "- 0.60 - 0.79: Medium confidence - Suggest human review",
                "- 0.40 - 0.59: Low confidence - Escalate to human",
                "- 0.00 - 0.39: Very low confidence - Reject/Escalate",
                "",
                "INPUT:",
                "You will receive:",
                "- User query",
                "- AI response",
                "- Number of relevant documents found",
                "- Response validation result",
                "",
                "OUTPUT FORMAT:",
                "Return ONLY a number between 0.0 and 1.0 (e.g., 0.85)",
                "",
                "Examples:",
                "Clear query + Complete response + 5 docs + valid → 0.87",
                "Vague query + Partial response + 2 docs + partial → 0.45",
                "Clear query + Good response + 0 docs + hallucination → 0.15"
            ]
        )


# Global factory instance
advanced_agent_factory = AdvancedAgentFactory()
