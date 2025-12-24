"""
Sensitive Data Detection Utility with Regex Patterns
Detects credit cards, emails, phone numbers, SSN, passwords, and other PII
ESCALATION: 100% automatic escalation when sensitive data is detected
"""
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class SensitiveDataMatch:
    """Represents a detected sensitive data match"""
    data_type: str
    pattern_name: str
    matched_text: str
    start_pos: int
    end_pos: int
    risk_level: str  # "critical", "high", "medium"


class SensitiveDataDetector:
    """
    Detects sensitive personal information using regex patterns.
    Implements MANDATORY 100% escalation when sensitive data is found.
    """
    
    # =============================================================================
    # REGEX PATTERNS FOR SENSITIVE DATA DETECTION
    # =============================================================================
    
    PATTERNS = {
        # Credit Card Patterns (Critical Risk)
        "credit_card_visa": {
            "pattern": r"\b4[0-9]{3}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}\b",
            "description": "Visa card (starts with 4)",
            "risk_level": "critical",
            "example": "4111-1111-1111-1111"
        },
        "credit_card_mastercard": {
            "pattern": r"\b5[1-5][0-9]{2}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}\b",
            "description": "Mastercard (starts with 51-55)",
            "risk_level": "critical",
            "example": "5500-0000-0000-0004"
        },
        "credit_card_amex": {
            "pattern": r"\b3[47][0-9]{2}[\s\-]?[0-9]{6}[\s\-]?[0-9]{5}\b",
            "description": "American Express (starts with 34 or 37)",
            "risk_level": "critical",
            "example": "3782-822463-10005"
        },
        "credit_card_generic": {
            "pattern": r"\b(?:\d{4}[\s\-]?){3}\d{4}\b",
            "description": "Generic 16-digit card number",
            "risk_level": "critical",
            "example": "1234-5678-9012-3456"
        },
        
        # Email Patterns (High Risk)
        "email_standard": {
            "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
            "description": "Standard email address",
            "risk_level": "high",
            "example": "user@example.com"
        },
        
        # Phone Number Patterns (High Risk)
        "phone_international": {
            "pattern": r"\b\+?[1-9]\d{1,14}\b",
            "description": "International phone (E.164 format)",
            "risk_level": "high",
            "example": "+33612345678"
        },
        "phone_french": {
            "pattern": r"\b(?:0|\+33[\s\.]?)[1-9](?:[\s\.\-]?\d{2}){4}\b",
            "description": "French phone number",
            "risk_level": "high",
            "example": "06 12 34 56 78"
        },
        "phone_us": {
            "pattern": r"\b(?:\+1[\s\-]?)?(?:\([0-9]{3}\)|[0-9]{3})[\s\-]?[0-9]{3}[\s\-]?[0-9]{4}\b",
            "description": "US phone number",
            "risk_level": "high",
            "example": "(555) 123-4567"
        },
        "phone_algerian": {
            "pattern": r"\b(?:0|\+213[\s\.]?)[567]\d{2}[\s\.\-]?\d{2}[\s\.\-]?\d{2}[\s\.\-]?\d{2}\b",
            "description": "Algerian phone number",
            "risk_level": "high",
            "example": "+213 555 12 34 56"
        },
        
        # SSN / National ID Patterns (Critical Risk)
        "ssn_us": {
            "pattern": r"\b\d{3}[\s\-]?\d{2}[\s\-]?\d{4}\b",
            "description": "US Social Security Number",
            "risk_level": "critical",
            "example": "123-45-6789"
        },
        "nin_french": {
            "pattern": r"\b[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b",
            "description": "French National ID (INSEE)",
            "risk_level": "critical",
            "example": "1 85 12 75 115 005 42"
        },
        
        # Password Patterns (Critical Risk)
        "password_explicit": {
            "pattern": r"(?i)\b(?:password|pwd|pass|mot\s*de\s*passe|mdp)[\s:=]+\S+",
            "description": "Explicitly shared password",
            "risk_level": "critical",
            "example": "password: mySecret123"
        },
        "password_secret": {
            "pattern": r"(?i)\b(?:secret|token|api[_\s]?key|private[_\s]?key)[\s:=]+\S+",
            "description": "Secret/API key shared",
            "risk_level": "critical",
            "example": "api_key: sk-xxxx"
        },
        
        # Financial Data (Critical Risk)
        "iban": {
            "pattern": r"\b[A-Z]{2}\d{2}[\s]?(?:\d{4}[\s]?){4,7}\d{1,4}\b",
            "description": "IBAN bank account",
            "risk_level": "critical",
            "example": "FR76 3000 6000 0112 3456 7890 189"
        },
        "cvv": {
            "pattern": r"(?i)\b(?:cvv|cvc|cvv2|cvc2|security\s*code)[\s:=]+\d{3,4}\b",
            "description": "Card CVV/CVC code",
            "risk_level": "critical",
            "example": "CVV: 123"
        },
        
        # Address Patterns (Medium Risk)
        "address_full": {
            "pattern": r"\b\d{1,5}\s+(?:[A-Za-zÀ-ÿ]+\s+){1,5}(?:street|st|avenue|ave|road|rd|boulevard|blvd|rue|avenue|place)\b",
            "description": "Full street address",
            "risk_level": "medium",
            "example": "123 Main Street"
        },
        "postal_code_fr": {
            "pattern": r"\b(?:F-|FR)?(?:0[1-9]|[1-9][0-9])\d{3}\b",
            "description": "French postal code",
            "risk_level": "medium",
            "example": "75001"
        },
        
        # Date of Birth (Medium Risk) - only when explicitly labeled
        "dob_explicit": {
            "pattern": r"(?i)\b(?:date\s*(?:of\s*)?birth|dob|né\s*le|naissance)[\s:=]+\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b",
            "description": "Date of birth",
            "risk_level": "medium",
            "example": "DOB: 15/03/1990"
        },
    }
    
    # Exclusion patterns - these are NOT sensitive (e.g., "reset password" without actual password)
    EXCLUSION_PATTERNS = [
        r"(?i)reset\s+(?:my\s+)?password",
        r"(?i)forgot\s+(?:my\s+)?password",
        r"(?i)change\s+(?:my\s+)?password",
        r"(?i)password\s+reset",
        r"(?i)update\s+(?:my\s+)?email",
        r"(?i)verify\s+(?:my\s+)?email",
    ]
    
    def __init__(self):
        """Initialize detector with compiled patterns"""
        self.compiled_patterns = {}
        for name, config in self.PATTERNS.items():
            self.compiled_patterns[name] = {
                "regex": re.compile(config["pattern"], re.IGNORECASE),
                "description": config["description"],
                "risk_level": config["risk_level"]
            }
        
        self.exclusion_regexes = [re.compile(p) for p in self.EXCLUSION_PATTERNS]
    
    def _is_excluded(self, text: str) -> bool:
        """Check if text matches any exclusion pattern"""
        for regex in self.exclusion_regexes:
            if regex.search(text):
                return True
        return False
    
    def detect(self, text: str) -> Dict:
        """
        Detect sensitive data in text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dict with detection results:
            {
                "contains_sensitive_data": bool,
                "should_escalate": bool (always True if sensitive data found),
                "matches": List[SensitiveDataMatch],
                "risk_summary": {"critical": int, "high": int, "medium": int},
                "detected_types": List[str],
                "redacted_text": str
            }
        """
        # Check exclusions first
        if self._is_excluded(text):
            return {
                "contains_sensitive_data": False,
                "should_escalate": False,
                "matches": [],
                "risk_summary": {"critical": 0, "high": 0, "medium": 0},
                "detected_types": [],
                "redacted_text": text,
                "exclusion_matched": True
            }
        
        matches: List[SensitiveDataMatch] = []
        risk_summary = {"critical": 0, "high": 0, "medium": 0}
        detected_types = set()
        
        for name, config in self.compiled_patterns.items():
            for match in config["regex"].finditer(text):
                sensitive_match = SensitiveDataMatch(
                    data_type=name.split("_")[0],  # e.g., "credit" from "credit_card_visa"
                    pattern_name=name,
                    matched_text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    risk_level=config["risk_level"]
                )
                matches.append(sensitive_match)
                risk_summary[config["risk_level"]] += 1
                detected_types.add(name)
        
        contains_sensitive = len(matches) > 0
        
        # Generate redacted text
        redacted_text = text
        for match in sorted(matches, key=lambda m: m.start_pos, reverse=True):
            mask = "[REDACTED-" + match.data_type.upper() + "]"
            redacted_text = redacted_text[:match.start_pos] + mask + redacted_text[match.end_pos:]
        
        return {
            "contains_sensitive_data": contains_sensitive,
            "should_escalate": contains_sensitive,  # 100% ESCALATION
            "matches": matches,
            "risk_summary": risk_summary,
            "detected_types": list(detected_types),
            "redacted_text": redacted_text,
            "escalation_reason": self._get_escalation_reason(matches) if contains_sensitive else None
        }
    
    def _get_escalation_reason(self, matches: List[SensitiveDataMatch]) -> str:
        """Generate escalation reason message"""
        critical_count = sum(1 for m in matches if m.risk_level == "critical")
        high_count = sum(1 for m in matches if m.risk_level == "high")
        
        types_found = list(set(m.data_type for m in matches))
        
        if critical_count > 0:
            return f"CRITICAL: Detected {critical_count} critical-risk data items ({', '.join(types_found)}). MANDATORY escalation to human agent."
        elif high_count > 0:
            return f"HIGH RISK: Detected {high_count} high-risk data items ({', '.join(types_found)}). Escalation required."
        else:
            return f"MEDIUM RISK: Detected personal data ({', '.join(types_found)}). Review recommended."
    
    def quick_check(self, text: str) -> Tuple[bool, str]:
        """
        Quick check for sensitive data - returns (is_sensitive, classification)
        
        Returns:
            Tuple of (is_sensitive: bool, classification: str)
            classification is either "sensitive" or "safe"
        """
        result = self.detect(text)
        if result["contains_sensitive_data"]:
            return True, "sensitive"
        return False, "safe"


# Global singleton instance
sensitive_data_detector = SensitiveDataDetector()
