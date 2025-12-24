"""
Classification agents for query categorization
"""
from agno.agent import Agent
from agno.models.mistral import MistralChat

from ..config.settings import settings


class AgentFactory:
    """Factory for creating classification agents"""
    
    def __init__(self):
        """Initialize Mistral model"""
        self.model = MistralChat(
            id=settings.MISTRAL_MODEL_ID,
            temperature=settings.MISTRAL_TEMPERATURE
        )
    
    def create_rag_agent(self) -> Agent:
        """Create RAG validation agent"""
        return Agent(
            name="RAG Pipeline Agent",
            model=self.model,
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
    
    def create_spam_agent(self) -> Agent:
        """Create spam detection agent"""
        return Agent(
            name="Spam Detector Agent",
            model=self.model,
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
    
    def create_ambiguous_agent(self) -> Agent:
        """Create ambiguity detection agent"""
        return Agent(
            name="Ambiguity Detector Agent",
            model=self.model,
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
    
    def create_aggressive_agent(self) -> Agent:
        """Create aggression detection agent"""
        return Agent(
            name="Aggression Detector Agent",
            model=self.model,
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
    
    def create_sensitive_agent(self) -> Agent:
        """Create sensitive data detection agent"""
        return Agent(
            name="Sensitive Data Detector Agent",
            model=self.model,
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
    
    def create_out_of_scope_agent(self) -> Agent:
        """Create out-of-scope detection agent"""
        return Agent(
            name="Out of Scope Agent",
            model=self.model,
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
    
    def create_classification_confidence_agent(self) -> Agent:
        """Create classification confidence scoring agent"""
        return Agent(
            name="Classification Confidence Agent",
            model=self.model,
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


# Global factory instance
agent_factory = AgentFactory()

# Create confidence agent instance
classification_confidence_agent = agent_factory.create_classification_confidence_agent()
