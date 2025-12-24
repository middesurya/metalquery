"""
Guardrails AI Integration Layer

Uses the official guardrails-ai package for input validation:
- Regex-based validators for PII, profanity, sensitive data
- Guard class for structured validation

Reference: https://docs.guardrailsai.com/
"""

import re
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Import Guardrails AI
try:
    from guardrails import Guard
    from guardrails.validators import register_validator, Validator, PassResult, FailResult
    from guardrails.classes.validation.validation_result import ValidationResult
    GUARDRAILS_AVAILABLE = True
    logger.info("✅ Guardrails AI package loaded successfully")
except ImportError as e:
    GUARDRAILS_AVAILABLE = False
    logger.warning(f"⚠️ Guardrails AI not installed: {e}")


@dataclass
class GuardrailsResult:
    """Result from Guardrails check"""
    is_safe: bool
    reason: str
    violation_type: Optional[str] = None
    detected_items: Optional[List[str]] = None


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM VALIDATORS using Guardrails AI framework
# ═══════════════════════════════════════════════════════════════════════════════

if GUARDRAILS_AVAILABLE:
    
    @register_validator(name="pii-detector", data_type="string")
    class PIIDetector(Validator):
        """Detects Personally Identifiable Information"""
        
        def __init__(self, on_fail: str = "exception"):
            super().__init__(on_fail=on_fail)
            self.patterns = {
                "ssn": r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
                "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
                "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
                "aadhaar": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
                "pan": r"\b[A-Z]{5}\d{4}[A-Z]\b",
            }
        
        def validate(self, value: str, metadata: Dict) -> ValidationResult:
            for pii_type, pattern in self.patterns.items():
                if re.search(pattern, value):
                    return FailResult(
                        error_message=f"PII detected: {pii_type}",
                        fix_value=None
                    )
            return PassResult()
    
    
    @register_validator(name="profanity-filter", data_type="string")
    class ProfanityFilter(Validator):
        """Filters profanity and toxic language"""
        
        def __init__(self, on_fail: str = "exception"):
            super().__init__(on_fail=on_fail)
            self.patterns = [
                r"(?i)\b(fuck|shit|ass|damn|bitch|bastard|crap)\b",
                r"(?i)\b(idiot|stupid|dumb|moron|retard)\b",
            ]
        
        def validate(self, value: str, metadata: Dict) -> ValidationResult:
            for pattern in self.patterns:
                if re.search(pattern, value):
                    return FailResult(
                        error_message="Profanity detected",
                        fix_value=None
                    )
            return PassResult()
    
    
    @register_validator(name="sensitive-data-filter", data_type="string")
    class SensitiveDataFilter(Validator):
        """Detects passwords, API keys, credentials"""
        
        def __init__(self, on_fail: str = "exception"):
            super().__init__(on_fail=on_fail)
            self.patterns = {
                "password": r"(?i)\b(password|passwd|pwd)\s*[:=]\s*\S+",
                "api_key": r"(?i)\b(api[_-]?key|secret[_-]?key|token)\s*[:=]\s*\S+",
            }
        
        def validate(self, value: str, metadata: Dict) -> ValidationResult:
            for data_type, pattern in self.patterns.items():
                if re.search(pattern, value):
                    return FailResult(
                        error_message=f"Sensitive data detected: {data_type}",
                        fix_value=None
                    )
            return PassResult()


class GuardrailsLayer:
    """
    Guardrails AI integration for input validation.
    Uses Guard class with custom validators.
    """
    
    def __init__(self):
        self.guardrails_enabled = GUARDRAILS_AVAILABLE
        
        if self.guardrails_enabled:
            # Create Guard with custom validators
            self.guard = Guard().use_many(
                PIIDetector(on_fail="noop"),
                ProfanityFilter(on_fail="noop"),
                SensitiveDataFilter(on_fail="noop"),
            )
            logger.info("✅ GuardrailsLayer initialized with Guardrails AI validators")
        else:
            self.guard = None
            self._init_regex_fallback()
            logger.info("GuardrailsLayer using regex fallback")
    
    def _init_regex_fallback(self):
        """Initialize regex patterns as fallback"""
        self.pii_patterns = {
            "ssn": r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
            "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        }
        self.profanity_patterns = [
            r"(?i)\b(fuck|shit|ass|damn|bitch|bastard)\b",
        ]
        self.sensitive_patterns = {
            "password": r"(?i)\b(password|passwd|pwd)\s*[:=]\s*\S+",
            "api_key": r"(?i)\b(api[_-]?key|secret[_-]?key)\s*[:=]\s*\S+",
        }
    
    def validate(self, text: str) -> GuardrailsResult:
        """Run validation using Guardrails AI or regex fallback"""
        
        if self.guardrails_enabled and self.guard:
            return self._validate_with_guardrails(text)
        else:
            return self._validate_with_regex(text)
    
    def _validate_with_guardrails(self, text: str) -> GuardrailsResult:
        """Use Guardrails AI Guard for validation"""
        try:
            result = self.guard.validate(text)
            
            if result.validation_passed:
                return GuardrailsResult(is_safe=True, reason="Passed Guardrails AI validation")
            else:
                # Extract failure reason
                errors = [str(e) for e in result.validation_summaries] if hasattr(result, 'validation_summaries') else ["Validation failed"]
                return GuardrailsResult(
                    is_safe=False,
                    reason="; ".join(errors) if errors else "Guardrails validation failed",
                    violation_type="guardrails"
                )
        except Exception as e:
            logger.warning(f"Guardrails validation error: {e}")
            # Fallback to regex
            return self._validate_with_regex(text)
    
    def _validate_with_regex(self, text: str) -> GuardrailsResult:
        """Fallback regex validation"""
        # PII check
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, text):
                return GuardrailsResult(
                    is_safe=False,
                    reason=f"PII detected: {pii_type}",
                    violation_type="pii"
                )
        
        # Profanity check
        for pattern in self.profanity_patterns:
            if re.search(pattern, text):
                return GuardrailsResult(
                    is_safe=False,
                    reason="Inappropriate language detected",
                    violation_type="profanity"
                )
        
        # Sensitive data check
        for data_type, pattern in self.sensitive_patterns.items():
            if re.search(pattern, text):
                return GuardrailsResult(
                    is_safe=False,
                    reason=f"Sensitive data detected: {data_type}",
                    violation_type="sensitive_data"
                )
        
        return GuardrailsResult(is_safe=True, reason="Passed validation")
    
    def get_blocked_message(self, result: GuardrailsResult) -> str:
        """Generate user-friendly message for blocked content"""
        
        if result.violation_type == "pii":
            return (
                "🔒 **Privacy Alert**: Your message contains personal information.\n\n"
                "Please remove sensitive data and try again."
            )
        
        if result.violation_type == "profanity":
            return (
                "🚫 **Language Alert**: Please use appropriate language.\n\n"
                "I'm here to help with manufacturing data queries."
            )
        
        if result.violation_type == "sensitive_data":
            return (
                "🔐 **Security Alert**: Your message contains credentials.\n\n"
                "Please don't share passwords or API keys in queries."
            )
        
        return f"Your query was blocked: {result.reason}"


# Export for backward compatibility
class CombinedGuard:
    """Combines GuardrailsLayer with custom QueryGuard"""
    
    def __init__(self):
        from query_guard import EnhancedQueryGuard
        self.custom_guard = EnhancedQueryGuard()
        self.guardrails = GuardrailsLayer()
        logger.info("✅ CombinedGuard initialized")
    
    def check(self, query: str, user_id: str = "anonymous") -> Dict:
        # Guardrails AI first
        gr_result = self.guardrails.validate(query)
        if not gr_result.is_safe:
            return {
                'is_safe': False,
                'message': self.guardrails.get_blocked_message(gr_result),
                'reason': gr_result.reason
            }
        
        # Then custom guard
        custom_result = self.custom_guard.check_query_relevance(query, user_id)
        if not custom_result.is_relevant:
            return {
                'is_safe': False,
                'message': custom_result.suggested_message,
                'reason': custom_result.reason
            }
        
        return {'is_safe': True, 'message': None, 'reason': "Passed all checks"}


# Quick test
if __name__ == "__main__":
    print(f"\nGuardrails AI Available: {GUARDRAILS_AVAILABLE}\n")
    
    layer = GuardrailsLayer()
    tests = [
        "Show OEE for furnace 1",
        "My SSN is 123-45-6789",
        "What the fuck is OEE?",
        "password=secret123 show data",
    ]
    
    for query in tests:
        result = layer.validate(query)
        status = "✅" if result.is_safe else "❌"
        print(f"{status} {query[:40]:40} -> {result.reason}")
