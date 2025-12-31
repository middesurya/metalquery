"""
Flipping Detector - Defense Against Prompt Flipping Attacks
Based on FlipAttack research (ICLR 2025) - 78.97% attack success rate defense
"""

import re
from typing import Dict, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FlippingMode(Enum):
    WORD_ORDER = "word_order"           # "bomb a build to how"
    CHAR_IN_WORD = "char_in_word"       # "woH ot dliub a bmob"
    CHAR_IN_SENTENCE = "char_in_sentence"  # "bmob a dliub ot woH"
    FOOL_MODEL = "fool_model"           # Asks flip word order with reversed chars


class FlippingDetector:
    """
    Detects prompt flipping attacks by analyzing token patterns.
    Based on FlipAttack research (ICLR 2025).
    """
    
    def __init__(self):
        self.flipping_patterns = [
            (r'\b[a-z]{3,}(?:[a-z]){0,3}\b', 'char_reversal'),
            (r'\b[\W_]+[\w]*\b', 'high_special_char'),
            (r'[\s]{2,}', 'irregular_spacing'),
        ]
        
        self.harmful_keywords = {
            'bomb', 'exploit', 'hack', 'malware', 'bypass', 'jailbreak',
            'extract', 'leak', 'steal', 'fraudulent', 'unauthorized',
            'delete', 'drop', 'truncate', 'destroy', 'kill', 'attack',
            'inject', 'override', 'admin', 'root', 'password', 'credential'
        }
    
    def detect_flipping(self, prompt: str) -> Dict[str, any]:
        """
        Analyze prompt for flipping attack indicators.
        Returns confidence score (0-1) and detected modes.
        """
        scores = {}
        
        # Check Mode 1: Word order flipping
        words = prompt.split()
        reversed_check = self._check_word_order_reversal(words)
        scores['word_order'] = reversed_check
        
        # Check Mode 2: Character reversal within words
        char_reversal = self._check_char_reversal(prompt)
        scores['char_in_word'] = char_reversal
        
        # Check Mode 3: Full sentence reversal
        full_reversal = self._check_full_reversal(prompt)
        scores['char_in_sentence'] = full_reversal
        
        # Check Mode 4: Fool model
        fool_score = self._check_fool_model(prompt)
        scores['fool_model'] = fool_score
        
        # Overall flipping confidence
        flipping_confidence = max(scores.values())
        detected_modes = [k for k, v in scores.items() if v > 0.6]
        
        result = {
            'is_flipped': flipping_confidence > 0.65,
            'confidence': flipping_confidence,
            'detected_modes': detected_modes,
            'individual_scores': scores
        }
        
        if result['is_flipped']:
            logger.warning(f"🚨 FLIPPING ATTACK DETECTED: {detected_modes} (confidence: {flipping_confidence:.2f})")
        
        return result
    
    def _check_word_order_reversal(self, words: list) -> float:
        """
        Detect if words appear in reverse order.
        Example: "bomb a build to how" (reversed: "how to build a bomb")
        """
        reversed_text = ' '.join(reversed(words))
        harmful_match = sum(1 for kw in self.harmful_keywords 
                           if kw in reversed_text.lower())
        return min(harmful_match * 0.25, 1.0)
    
    def _check_char_reversal(self, text: str) -> float:
        """
        Detect characters reversed within words.
        Example: "woH" (reversed: "How")
        """
        words = text.split()
        reversal_count = 0
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) > 2:
                reversed_word = clean_word[::-1]
                if reversed_word.lower() in self.harmful_keywords:
                    reversal_count += 1
        
        return min(reversal_count * 0.4, 1.0)
    
    def _check_full_reversal(self, text: str) -> float:
        """
        Detect full sentence reversal.
        """
        perplexity_increase = self._estimate_perplexity_anomaly(text)
        return min(perplexity_increase / 100, 1.0)
    
    def _check_fool_model(self, prompt: str) -> float:
        """
        Detect conflicting task instructions.
        """
        if 'flip' in prompt.lower():
            if 'word' in prompt and 'character' not in prompt:
                return 0.5
        return 0.0
    
    def _estimate_perplexity_anomaly(self, text: str) -> float:
        """
        Rough perplexity estimate based on character patterns.
        """
        unusual_patterns = len(re.findall(r'[a-z]{5,}', text))
        total_patterns = len(re.findall(r'\b\w+\b', text))
        
        if total_patterns == 0:
            return 0.0
        return (unusual_patterns / total_patterns) * 100


class PromptSignatureValidator:
    """
    Validates prompt authenticity against known attack signatures.
    Detects prompt injection payloads and jailbreak attempts.
    """
    
    def __init__(self):
        self.attack_signatures = [
            # Prompt injection indicators
            {'pattern': r'(ignore.*previous|disregard|forget)', 'type': 'direct_injection', 'severity': 0.8},
            {'pattern': r'(system prompt|system message|admin mode)', 'type': 'role_assumption', 'severity': 0.7},
            {'pattern': r'(execute.*command|run.*code|unsafe)', 'type': 'code_execution', 'severity': 0.9},
            
            # Indirect injection
            {'pattern': r'(curl|http|request|fetch).*https?', 'type': 'external_data', 'severity': 0.6},
            {'pattern': r'(eval|exec|compile)', 'type': 'code_eval', 'severity': 0.9},
            
            # SQL-specific injection
            {'pattern': r"(union\s+select|drop\s+table|delete\s+from|update\s+.*set|insert\s+into)", 'type': 'direct_sql', 'severity': 0.95},
            {'pattern': r"(--\s*$|;\s*--|/\*|\*/)", 'type': 'sql_comment', 'severity': 0.7},
            {'pattern': r"('\s*or\s+'1'\s*=\s*'1|'\s*or\s+1\s*=\s*1)", 'type': 'sql_tautology', 'severity': 0.95},
            
            # Red teaming signatures
            {'pattern': r'(metric|game|fake|cheat|fake result)', 'type': 'reward_hack', 'severity': 0.5},
            {'pattern': r'(hidden.*goal|secret|deceptive)', 'type': 'deceptive_align', 'severity': 0.6},
            {'pattern': r'(leak|extract|exfiltrate|dump)', 'type': 'data_exfil', 'severity': 0.8},
            
            # Jailbreak patterns
            {'pattern': r'(pretend|roleplay|act as|you are now)', 'type': 'jailbreak', 'severity': 0.5},
            {'pattern': r'(dan|developer mode|no restrictions)', 'type': 'jailbreak', 'severity': 0.7},
        ]
    
    def validate(self, prompt: str) -> Dict[str, any]:
        """
        Check prompt against attack signatures.
        Returns: {is_safe: bool, threats: [list], score: float}
        """
        threats = []
        threat_score = 0.0
        
        for sig in self.attack_signatures:
            if re.search(sig['pattern'], prompt, re.IGNORECASE):
                threats.append({
                    'type': sig['type'],
                    'severity': sig['severity']
                })
                threat_score += sig['severity'] * 0.15
        
        threat_score = min(threat_score, 1.0)
        threat_types = list(set([t['type'] for t in threats]))
        
        result = {
            'is_safe': threat_score < 0.4,
            'threat_types': threat_types,
            'threat_score': threat_score,
            'detected_signatures': len(threats),
            'threats': threats
        }
        
        if not result['is_safe']:
            logger.warning(f"🚨 INJECTION ATTACK DETECTED: {threat_types} (score: {threat_score:.2f})")
        
        return result
