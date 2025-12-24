"""
Evaluation agents for RAG document quality checking
These agents validate retrieved documents before response generation
"""
from agno.agent import Agent
from agno.team import Team
from agno.models.mistral import MistralChat

from ..config.settings import settings


class EvaluationAgentFactory:
    """Factory for creating document evaluation agents"""
    
    def __init__(self):
        """Initialize Mistral model"""
        self.model = MistralChat(
            id=settings.MISTRAL_MODEL_ID,
            temperature=settings.MISTRAL_TEMPERATURE
        )
    
    def create_contradiction_agent(self) -> Agent:
        """
        Agent that detects contradictory information in retrieved documents.
        Critical for preventing conflicting answers.
        """
        return Agent(
            name="Contradiction Detector Agent",
            model=self.model,
            description="Detects if retrieved documents contain contradictory information.",
            markdown=True,
            instructions=[
                "Analyze the retrieved documents for contradictions.",
                "",
                "BE LENIENT - Only flag MAJOR contradictions that would cause serious confusion.",
                "",
                "CONTRADICTORY if:",
                "- Documents give completely opposite answers (e.g., 'yes' vs 'no' to same question)",
                "- Critical numbers conflict significantly (e.g., price differs by >50%)",
                "- Instructions are directly opposite and dangerous",
                "",
                "NOT CONTRADICTORY if:",
                "- Minor differences in details or wording",
                "- Different aspects of the same topic",
                "- Different versions or options are presented",
                "- Complementary information from different angles",
                "- Slight variations in numbers or dates (could be updates)",
                "",
                "IMPORTANT: If in doubt, consider documents as CONSISTENT.",
                "",
                "If major contradictions exist: respond ONLY with 'contradictory'",
                "Otherwise: respond ONLY with 'consistent'"
            ]
        )
    
    def create_missing_knowledge_agent(self) -> Agent:
        """
        Agent that detects if retrieved documents lack necessary information.
        Prevents generating incomplete or uninformed responses.
        """
        return Agent(
            name="Missing Knowledge Agent",
            model=self.model,
            description="Detects if retrieved documents lack information to answer the query.",
            markdown=True,
            instructions=[
                "Check if retrieved documents contain enough information to answer the user's query.",
                "",
                "BE VERY LENIENT - If there's even a SMALL piece of relevant info, consider it sufficient.",
                "",
                "MISSING KNOWLEDGE ONLY if:",
                "- Documents are 100% completely unrelated to the query topic",
                "- Documents are empty or contain zero useful information",
                "- Not a single word in documents relates to what user asked",
                "",
                "SUFFICIENT KNOWLEDGE if:",
                "- Documents mention the topic AT ALL, even briefly",
                "- Documents contain ANY related information, even partial",
                "- Even ONE document has something relevant",
                "- Documents discuss similar, adjacent, or related topics",
                "- Partial answer is possible from ANY document content",
                "- Some documents are off-topic but at least one is relevant",
                "",
                "IMPORTANT: Default to SUFFICIENT. Only say 'missing' if absolutely nothing relates.",
                "",
                "If information is 100% completely missing: respond ONLY with 'missing'",
                "Otherwise: respond ONLY with 'sufficient'"
            ]
        )
    
    def create_multiple_answers_agent(self) -> Agent:
        """
        Agent that detects if documents provide multiple valid answers.
        This is informational - not an error, but user should be aware of options.
        """
        return Agent(
            name="Multiple Answers Agent",
            model=self.model,
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
    
    def create_evaluation_team(self) -> Team:
        """
        Creates a team that evaluates retrieved document quality.
        Returns one of: 'contradictory', 'missing_knowledge', 'multiple_answers', or 'safe'
        """
        return Team(
            model=self.model,
            name="Chunk Evaluation Team",
            markdown=True,
            members=[
                self.create_contradiction_agent(),
                self.create_missing_knowledge_agent(),
                self.create_multiple_answers_agent()
            ],
            instructions=[
                "Evaluate retrieved documents for quality issues before RAG generation.",
                "",
                "BE VERY LENIENT - Always try to proceed if there's ANY relevant info.",
                "",
                "EVALUATION PRIORITY (check in order):",
                "1. 'safe' - DEFAULT CHOICE. Use if ANY document has relevant info.",
                "2. 'multiple_answers' - documents provide multiple valid options (this is fine!)",
                "3. 'contradictory' - ONLY for MAJOR direct conflicts (very rare!)",
                "4. 'missing_knowledge' - ONLY if 100% of docs are completely unrelated (very rare!)",
                "",
                "KEY PRINCIPLE: If even ONE document contains something useful, return 'safe'.",
                "Off-topic documents mixed with relevant ones = 'safe' (ignore the bad ones).",
                "",
                "ABSOLUTE OUTPUT RULE:",
                "Your ENTIRE response must be ONLY ONE WORD from:",
                "safe OR multiple_answers OR contradictory OR missing_knowledge",
                "",
                "DO NOT write explanations. ONLY the category word.",
                "",
                "Examples:",
                "- 3 unrelated docs + 1 relevant doc: safe",
                "- Docs partially answer query: safe",
                "- Minor inconsistencies: safe",
                "- Docs mention topic briefly: safe",
                "- Docs list 3 options: multiple_answers",
                "- ALL docs 100% unrelated: missing_knowledge",
                "- Docs give exact opposite answers: contradictory"
            ]
        )
    
    def create_evaluation_confidence_agent(self) -> Agent:
        """
        Agent that scores confidence in evaluation decision.
        Helps determine if escalation is needed.
        """
        return Agent(
            name="Evaluation Confidence Agent",
            model=self.model,
            description="Scores confidence level of document evaluation on 0-100% scale.",
            markdown=True,
            instructions=[
                "Score confidence in the evaluation decision (0-100%).",
                "",
                "HIGH CONFIDENCE (80-100%):",
                "- Clear, obvious quality issues or lack thereof",
                "- Strong evidence for the evaluation",
                "- No ambiguity in documents",
                "",
                "MEDIUM CONFIDENCE (50-79%):",
                "- Some indicators but not definitive",
                "- Minor ambiguity in documents",
                "- Borderline quality issues",
                "",
                "LOW CONFIDENCE (0-49%):",
                "- Very unclear document quality",
                "- Highly ambiguous content",
                "- Could be evaluated differently",
                "",
                "Response format: ONLY a number 0-100",
                "Examples:",
                "- Clear contradiction in docs: 95",
                "- Borderline missing info: 60",
                "- Very unclear: 35"
            ]
        )


# Global factory instance
evaluation_agent_factory = EvaluationAgentFactory()

# Create confidence agent instance
evaluation_confidence_agent = evaluation_agent_factory.create_evaluation_confidence_agent()