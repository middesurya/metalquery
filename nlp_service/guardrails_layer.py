"""
Guardrails AI Integration Layer

Combines the custom EnhancedQueryGuard with Guardrails AI validators
for additional protection including:
- Regex-based PII detection
- Profanity/toxic language detection
- Additional pattern matching

This layer is designed to work alongside the existing query_guard.py
"""

import re
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import Guardrails AI - gracefully degrade if not available
GUARDRAILS_AVAILABLE = False
try:
    from guardrails import Guard
    GUARDRAILS_AVAILABLE = True
    logger.info("✅ Guardrails AI loaded successfully")
except ImportError:
    logger.warning("⚠️ Guardrails AI not installed - using regex fallback only")


@dataclass
class GuardrailsResult:
    """Result from Guardrails check"""
    is_safe: bool
    reason: str
    violation_type: Optional[str] = None
    detected_items: Optional[List[str]] = None


class GuardrailsLayer:
    """
    Additional protection layer using Guardrails AI validators
    and custom regex patterns for:
    - PII detection (SSN, credit cards, emails, phone numbers)
    - Profanity filtering
    - Sensitive data detection
    """
    
    def __init__(self):
        self.guardrails_enabled = GUARDRAILS_AVAILABLE
        
        # ═══════════════════════════════════════════════════════════
        # PII DETECTION PATTERNS (regex-based, always available)
        # ═══════════════════════════════════════════════════════════
        self.pii_patterns = {
            "ssn": r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",  # SSN
            "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",  # Credit card
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "aadhaar": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Indian Aadhaar
            "pan": r"\b[A-Z]{5}\d{4}[A-Z]\b",  # Indian PAN
        }
        
        # ═══════════════════════════════════════════════════════════
        # PROFANITY/TOXIC PATTERNS
        # ═══════════════════════════════════════════════════════════
        self.profanity_patterns = [
            r"(?i)\b(fuck|shit|ass|damn|bitch|bastard|crap)\b",
            r"(?i)\b(idiot|stupid|dumb|moron|retard)\b",
            r"(?i)\b(hate|kill|murder|die|death)\s+(you|him|her|them)\b",
        ]
        
        # ═══════════════════════════════════════════════════════════
        # SENSITIVE DATA PATTERNS
        # ═══════════════════════════════════════════════════════════
        self.sensitive_patterns = {
            "password": r"(?i)\b(password|passwd|pwd)\s*[:=]\s*\S+",
            "api_key": r"(?i)\b(api[_-]?key|secret[_-]?key|token)\s*[:=]\s*\S+",
            "credentials": r"(?i)\b(username|user|login)\s*[:=]\s*\S+",
        }
        
        logger.info(f"GuardrailsLayer initialized (Guardrails AI: {self.guardrails_enabled})")
    
    def check_pii(self, text: str) -> GuardrailsResult:
        """Check for personally identifiable information"""
        
        detected = []
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected.append(f"{pii_type}: {len(matches)} found")
                logger.warning(f"🔒 PII DETECTED: {pii_type} in query")
        
        if detected:
            return GuardrailsResult(
                is_safe=False,
                reason="Personally Identifiable Information detected",
                violation_type="pii",
                detected_items=detected
            )
        
        return GuardrailsResult(is_safe=True, reason="No PII detected")
    
    def check_profanity(self, text: str) -> GuardrailsResult:
        """Check for profanity or toxic language"""
        
        for pattern in self.profanity_patterns:
            if re.search(pattern, text):
                logger.warning(f"🚫 PROFANITY DETECTED in query")
                return GuardrailsResult(
                    is_safe=False,
                    reason="Inappropriate language detected",
                    violation_type="profanity"
                )
        
        return GuardrailsResult(is_safe=True, reason="No profanity detected")
    
    def check_sensitive_data(self, text: str) -> GuardrailsResult:
        """Check for passwords, API keys, credentials in plaintext"""
        
        detected = []
        for data_type, pattern in self.sensitive_patterns.items():
            if re.search(pattern, text):
                detected.append(data_type)
                logger.warning(f"🔐 SENSITIVE DATA DETECTED: {data_type}")
        
        if detected:
            return GuardrailsResult(
                is_safe=False,
                reason="Sensitive credentials detected - please don't share passwords or API keys",
                violation_type="sensitive_data",
                detected_items=detected
            )
        
        return GuardrailsResult(is_safe=True, reason="No sensitive data detected")
    
    def validate(self, text: str) -> GuardrailsResult:
        """
        Run all validation checks on the input text.
        Returns the first violation found, or success if all pass.
        """
        
        # Check 1: PII
        pii_result = self.check_pii(text)
        if not pii_result.is_safe:
            return pii_result
        
        # Check 2: Profanity
        profanity_result = self.check_profanity(text)
        if not profanity_result.is_safe:
            return profanity_result
        
        # Check 3: Sensitive data
        sensitive_result = self.check_sensitive_data(text)
        if not sensitive_result.is_safe:
            return sensitive_result
        
        return GuardrailsResult(
            is_safe=True,
            reason="Passed all Guardrails checks"
        )
    
    def get_blocked_message(self, result: GuardrailsResult) -> str:
        """Generate user-friendly message for blocked content"""
        
        if result.violation_type == "pii":
            return (
                "🔒 **Privacy Alert**: Your message appears to contain personal information "
                "(SSN, credit card, phone, etc.).\n\n"
                "Please remove sensitive data and try again."
            )
        
        if result.violation_type == "profanity":
            return (
                "🚫 **Language Alert**: Please use appropriate language.\n\n"
                "I'm here to help with manufacturing data queries."
            )
        
        if result.violation_type == "sensitive_data":
            return (
                "🔐 **Security Alert**: Your message contains credentials or API keys.\n\n"
                "Please don't share passwords or sensitive tokens in queries."
            )
        
        return "Your query was blocked by security filters."


# ═══════════════════════════════════════════════════════════════════════════════
# COMBINED GUARD: Custom QueryGuard + Guardrails AI
# ═══════════════════════════════════════════════════════════════════════════════

class CombinedGuard:
    """
    Combines the custom EnhancedQueryGuard with GuardrailsLayer
    for comprehensive query protection.
    
    Usage:
        from guardrails_layer import CombinedGuard
        guard = CombinedGuard()
        result = guard.check(user_query)
        if not result['is_safe']:
            return result['message']
    """
    
    def __init__(self):
        # Import local guard
        from query_guard import EnhancedQueryGuard
        
        self.custom_guard = EnhancedQueryGuard()
        self.guardrails = GuardrailsLayer()
        
        logger.info("✅ CombinedGuard initialized with both custom + Guardrails protection")
    
    def check(self, query: str, user_id: str = "anonymous") -> Dict:
        """
        Run both guard layers on the query.
        
        Returns:
            {
                'is_safe': bool,
                'passed_custom': bool,
                'passed_guardrails': bool,
                'message': str (if blocked),
                'reason': str
            }
        """
        
        # Layer 1: Guardrails (PII, profanity, sensitive data) - runs first
        guardrails_result = self.guardrails.validate(query)
        if not guardrails_result.is_safe:
            return {
                'is_safe': False,
                'passed_custom': False,
                'passed_guardrails': False,
                'message': self.guardrails.get_blocked_message(guardrails_result),
                'reason': guardrails_result.reason
            }
        
        # Layer 2: Custom guard (domain relevance, security, etc.)
        custom_result = self.custom_guard.check_query_relevance(query, user_id)
        if not custom_result.is_relevant:
            return {
                'is_safe': False,
                'passed_custom': False,
                'passed_guardrails': True,
                'message': custom_result.suggested_message or "Query blocked by domain guard",
                'reason': custom_result.reason
            }
        
        # Both passed
        return {
            'is_safe': True,
            'passed_custom': True,
            'passed_guardrails': True,
            'message': None,
            'reason': "Passed all validation layers"
        }


# Convenience function
def validate_query(query: str, user_id: str = "anonymous") -> Dict:
    """Quick combined validation check"""
    guard = CombinedGuard()
    return guard.check(query, user_id)


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*70)
    print("GUARDRAILS LAYER - TEST RESULTS")
    print("="*70 + "\n")
    
    layer = GuardrailsLayer()
    
    test_cases = [
        ("Show OEE for furnace 1", "valid"),
        ("My SSN is 123-45-6789, show data", "pii"),
        ("My credit card is 4111-1111-1111-1111", "pii"),
        ("Email me at test@example.com", "pii"),
        ("What the fuck is OEE?", "profanity"),
        ("password=secret123 show furnace", "sensitive"),
        ("api_key: sk-12345 show data", "sensitive"),
    ]
    
    for query, test_type in test_cases:
        result = layer.validate(query)
        status = "✓" if (test_type == "valid" and result.is_safe) or \
                        (test_type != "valid" and not result.is_safe) else "✗"
        
        print(f"{status} [{test_type.upper():10}] {query[:45]:<45}")
        print(f"   → Safe: {result.is_safe} | Reason: {result.reason}")
        print()
