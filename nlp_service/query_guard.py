"""
Enhanced QueryGuard - Production-grade query filtering with multi-layer detection.

Sits BEFORE the query router to:
- Block irrelevant/off-topic questions early
- Catch harmful/security-related queries
- Detect obfuscation and abuse patterns
- Save LLM processing costs
- Provide detailed rejection reasons for logging

Flow: User Question → [ENHANCED GUARD] → [ROUTER] → [PROCESSOR]
"""

import re
import logging
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum
from collections import Counter
import difflib


logger = logging.getLogger(__name__)


class QueryRelevance(Enum):
    RELEVANT = "relevant"
    IRRELEVANT = "irrelevant"
    HARMFUL = "harmful"
    GREETING = "greeting"
    OBFUSCATED = "obfuscated"
    SPAM = "spam"


@dataclass
class GuardResult:
    """Result from query guard check."""
    is_relevant: bool
    relevance_type: QueryRelevance
    reason: str
    confidence: float  # 0.0 to 1.0
    suggested_message: Optional[str] = None
    violation_details: Optional[Dict] = None  # For debugging/logging


class EnhancedQueryGuard:
    """
    Production-grade query filter with multi-layer detection:
    
    Layer 1: Syntax/Security (injection, malware, URLs)
    Layer 2: Semantic (repetition, gibberish, tokenization)
    Layer 3: Intent (fuzzy matching, structure validation)
    Layer 4: Context (rate limiting, conversation history)
    """
    
    def __init__(self, confidence_threshold: float = 0.65):
        self.confidence_threshold = confidence_threshold
        self.query_history: Dict[str, List[str]] = {}
        self.rate_limits = {"queries_per_minute": 30, "identical_queries": 3}
        
        # ═══════════════════════════════════════════════════════════
        # SECURITY PATTERNS 
        # ═══════════════════════════════════════════════════════════
        self.security_patterns = {
            "sql_injection": [
                r"(?i)(\bUNION\b|\bSELECT\b.*\bFROM\b|\bDROP\b|\bDELETE\b|\bINSERT\b)",
                r"(?i)('|\")\s*(?:or|and)\s*('|\")?1('|\")?",
                r"(?i)(--|#|\/\*|\*\/)",
                r"(?i)(\bEXEC\b|\bEXECUTE\b|\bSHELL\b)",
                r"`.*`",
                r"';.*?;--",
            ],
            "prompt_injection": [
                r"(?i)(ignore|disregard|forget).*?(previous|prior|instruction|prompt)",
                r"(?i)(jailbreak|bypass|override|disable).*?filter",
                r"(?i)simulate a.*?(unrestricted|uncensored|without safety)",
                r"(?i)(act as|role play|pretend to be).*?without",
                r"(?i)you are no longer",
                r"(?i)(system prompt|hidden instruction|true purpose)",
            ],
            "nosql_injection": [
                r"(?i)(\$where|\$regex|\$ne|\$gt|\$lt|\$exists)",
                r"(?i)({.*?:.*?\})",
                r"(?i)(db\..*?\.find)",
            ],
            "xss": [
                r"<script[^>]*>",
                r"javascript:",
                r"on(load|error|click|mouse)",
                r"<iframe",
            ],
            "malware": [
                r"(?i)(virus|trojan|backdoor|ransomware|botnet|exploit|0day)",
                r"(?i)(hack|crack|bruteforce|password.*dump)",
                r"(?i)(phishing|spoofing|man-in-the-middle)",
            ],
            "urls_and_external": [
                r"https?://[^\s]+",
                r"www\.[^\s]+",
                r"\.exe|\.bat|\.cmd|\.ps1",
            ]
        }
        
        # ═══════════════════════════════════════════════════════════
        # GIBBERISH PATTERNS
        # ═══════════════════════════════════════════════════════════
        self.gibberish_patterns = [
            r"^[a-z]{1,2}$",  # Too short
            r"^[aeiou]{4,}$",  # Only vowels
            r"^[bcdfghjklmnpqrstvwxyz]{6,}$",  # Only consonants
            r"^[\W\d_]{3,}$",  # Only symbols/numbers
            r"^(.)\1{5,}$",  # Repeated chars
            r"^\d+$",  # Only numbers
        ]
        
        # ═══════════════════════════════════════════════════════════
        # GREETING PATTERNS
        # ═══════════════════════════════════════════════════════════
        self.greeting_patterns = [
            r"^(hello|hi|hey|howdy|hola|greetings)(\s+\w+)*\s*[!?.]*$",
            r"^(good\s+(morning|afternoon|evening|night))(\s+\w+)*\s*[!?.]*$",
            r"^(goodbye|bye|see you|later|thanks|thank you)(\s+\w+)*\s*[!?.]*$",
            r"^how are you",
            r"^what'?s up",
            r"^(nice|pleased)\s+to\s+meet\s+you",
        ]
        
        # ═══════════════════════════════════════════════════════════
        # META PATTERNS (questions about the AI)
        # ═══════════════════════════════════════════════════════════
        self.meta_patterns = [
            r"^(who|what).*?(are|is)\s+you\??$",
            r"^(what\s+can|are)\s+your\s+(capabilities|features)",
            r"^(tell|introduce).*?yourself",
        ]
        
        # ═══════════════════════════════════════════════════════════
        # GENERAL KNOWLEDGE PATTERNS (off-topic)
        # ═══════════════════════════════════════════════════════════
        self.general_knowledge_patterns = [
            r"(?i)\b(weather|forecast|temperature)\b",
            r"(?i)\b(news|headline|politics|government)\b",
            r"(?i)\b(sport|football|cricket|basketball)\b",
            r"(?i)\b(movie|film|netflix|series)\b",
            r"(?i)\b(recipe|cooking|food)\b",
            r"(?i)\b(joke|funny|humor|tell me a)\b",
            r"(?i)\b(song|music|artist|album)\b",
            r"(?i)\b(capital of|president of|who invented)\b",
            # Language/translation patterns
            r"(?i)\b(in spanish|in french|in german|in hindi|in chinese|in japanese)\b",
            r"(?i)\b(translate|translation|called in|say in|meaning in)\b",
            r"(?i)\b(language|dictionary|definition of)\b",
            # Nonsense/absurd patterns  
            r"(?i)\b(god|devil|heaven|hell|soul|spirit|afterlife)\b",
            r"(?i)\b(mates? with|breed|reproduce|give birth|marry|love)\b",
            r"(?i)\b(aliens?|ufo|ghost|magic|supernatural)\b",
            r"(?i)\b(kill|murder|die|death|dead)\b",
            r"(?i)\b(dream|nightmare|sleep|fairy|unicorn)\b",
            # Non-manufacturing products (not made in furnaces)
            r"(?i)\b(milk|cheese|butter|bread|food|fruit|vegetable|meat|fish|chicken|egg)\b",
            r"(?i)\b(car|truck|bicycle|motorcycle|plane|boat|vehicle)\b",
            r"(?i)\b(clothes|shirt|pants|shoes|dress|jacket|hat)\b",
            r"(?i)\b(phone|laptop|computer|tablet|tv|television)\b",
            r"(?i)\b(book|paper|pen|pencil|paint|art)\b",
            r"(?i)\b(medicine|drug|pill|vaccine|hospital|doctor)\b",
            r"(?i)\b(house|building|apartment|room|office|school)\b",
        ]
        
        # ═══════════════════════════════════════════════════════════
        # PROGRAMMING PATTERNS (off-topic)
        # ═══════════════════════════════════════════════════════════
        self.programming_patterns = [
            r"(?i)\b(javascript|js|python|java|c\+\+|typescript|react|angular|vue)\b",
            r"(?i)\b(int|let|var|const|function|class|def|import|export)\b",
            r"(?i)\b(code|coding|programming|developer|software|api|frontend|backend)\b",
            r"(?i)\b(html|css|sql syntax|database schema|table structure)\b",
            r"(?i)\b(error|exception|bug|debug|compile|runtime)\b",
            r"(?i)\b(npm|pip|package|library|framework|module)\b",
        ]
        
        # ═══════════════════════════════════════════════════════════
        # MATH/ARITHMETIC PATTERNS (disguised with domain keywords)
        # ═══════════════════════════════════════════════════════════
        self.math_patterns = [
            r"\d+\s*[\+\-\*\/\^]\s*\d+",  # 2+2, 10-5, 3*4, etc.
            r"(?i)\bsum of \d+ number",  # "sum of 10 numbers"
            r"(?i)\b(add|subtract|multiply|divide|plus|minus|times)\b.*\d",
            r"(?i)\bwhat is \d+\s*[\+\-\*\/]",  # "what is 2 +"
            r"(?i)\bcalculate \d+\s*[\+\-\*\/]",  # "calculate 5 *"
            r"(?i)\b\d+\s*(plus|minus|times|divided by)\s*\d+",
            r"(?i)\b(factorial|square root|sqrt|power of)\b",
            r"(?i)\bsolve\s+\d",  # "solve 2+2"
        ]
        
        # ═══════════════════════════════════════════════════════════
        # ACTION WORDS (required for valid queries)
        # ═══════════════════════════════════════════════════════════
        self.action_words = [
            # Question words
            "what", "which", "how", "when", "where", "why", "who",
            # Data retrieval
            "show", "get", "list", "display", "find", "fetch",
            "calculate", "compute", "average", "sum", "count",
            "compare", "analyze", "check", "provide",
            "top", "bottom", "highest", "lowest", "best", "worst",
            "give", "retrieve", "filter", "between", "from", "for", "by",
            # BRD/Documentation action words
            "explain", "describe", "tell", "about", "define", "meaning",
        ]
        
        # ═══════════════════════════════════════════════════════════
        # DOMAIN KEYWORDS (manufacturing-specific)
        # ═══════════════════════════════════════════════════════════
        self.primary_keywords = [
            "furnace", "oee", "efficiency", "production", "defect",
            "yield", "downtime", "quality", "output", "shift",
            "ignis", "mes", "equipment", "machine",
        ]
        
        self.secondary_keywords = [
            # KPI & Performance
            "mtbf", "mttr", "mtbs", "fpy", "compliance", "utilization",
            "today", "yesterday", "last week", "last month",
            
            # Core Process (from BRD S05.02)
            "tap", "cast", "tapping", "grading", "electrode", "core process",
            
            # System Config (from BRD S03)
            "plant config", "furnace config", "system config", "configuration",
            "user access", "roles", "users", "access control",
            
            # Master Data (from BRD S04)
            "master data", "material maintenance", "raw materials", "additives",
            "byproducts", "by-products", "wip", "work in progress", 
            "grading plan", "products", "material",
            
            # Reports (from BRD S06)
            "report", "reports", "raw material consumption", "consumption",
            "raw material analysis", "size analysis", "spout analysis",
            "tap analysis", "production report", "downtime analysis",
            "quality summary", "quality report",
            
            # Lab Analysis (from BRD S08)
            "lab", "lab analysis", "laboratory", "analysis",
            "spout", "spout analysis",
            
            # Log Book (from BRD S09)
            "log", "log book", "logbook", "tap hole", "tap hole log",
            "furnace downtime", "downtime log", "furnace bed", "bed log",
            
            # EHS (from BRD S013)
            "ehs", "incident", "incident reporting", "safety", "environment",
            "health safety", "environment health",
            
            # General BRD terms
            "brd", "sop", "procedure", "workflow", "guideline", "process",
            "metric", "kpi", "dashboard", "setup", "setting",
        ]
        
        # Typo variants for fuzzy matching
        self.keyword_variants = {
            "furnace": ["furnce", "furnasse", "burner"],
            "efficiency": ["efficency", "efficient"],
            "oee": ["o.e.e", "o.e.e.", "oe.e"],
            "production": ["prodcution", "producton", "produciton"],
            "defect": ["defects", "deffect"],
            "quality": ["qualitu", "qualit"],
            "ignis": ["igni", "igs"],
        }
    
    # ═══════════════════════════════════════════════════════════════════════
    # LAYER 1: SECURITY THREATS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _check_security_threats(self, query: str) -> Tuple[bool, Optional[GuardResult]]:
        """Check for SQL injection, prompt injection, malware, etc."""
        
        for threat_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    logger.warning(f"🚨 SECURITY THREAT DETECTED: {threat_type}")
                    return True, GuardResult(
                        is_relevant=False,
                        relevance_type=QueryRelevance.HARMFUL,
                        reason=f"Security threat detected: {threat_type}",
                        confidence=1.0,
                        suggested_message="🔒 I cannot process that request. Suspicious syntax detected.",
                        violation_details={"threat_type": threat_type, "pattern": pattern}
                    )
        
        return False, None
    
    # ═══════════════════════════════════════════════════════════════════════
    # LAYER 2: GIBBERISH & SPAM DETECTION
    # ═══════════════════════════════════════════════════════════════════════
    
    def _check_gibberish(self, query: str) -> Tuple[bool, Optional[GuardResult]]:
        """Detect nonsense, spam, repetitive patterns."""
        
        query_clean = query.lower().strip()
        
        # Check gibberish patterns
        for pattern in self.gibberish_patterns:
            if re.match(pattern, query_clean):
                logger.info(f"📢 GIBBERISH DETECTED: {query_clean}")
                return True, GuardResult(
                    is_relevant=False,
                    relevance_type=QueryRelevance.SPAM,
                    reason="Query appears to be gibberish or spam",
                    confidence=0.95,
                    suggested_message="🤔 I didn't understand that. Please ask a clear question about manufacturing data."
                )
        
        # Check word repetition
        words = query_clean.split()
        if len(words) > 3:
            word_freq = Counter(words)
            max_freq = max(word_freq.values())
            repetition_ratio = max_freq / len(words)
            
            if repetition_ratio > 0.4:
                logger.info(f"📢 EXCESSIVE REPETITION: {query_clean}")
                return True, GuardResult(
                    is_relevant=False,
                    relevance_type=QueryRelevance.SPAM,
                    reason=f"Excessive word repetition detected ({repetition_ratio:.1%})",
                    confidence=0.85,
                    suggested_message="🤔 Your query has too many repetitions. Please ask clearly."
                )
        
        # Check character diversity (detect obfuscation)
        unique_chars = len(set(query_clean.replace(" ", "")))
        query_len = len(query_clean.replace(" ", ""))
        if query_len > 10 and (unique_chars / query_len) < 0.15:
            logger.info(f"📢 LOW CHAR DIVERSITY (possible obfuscation): {query_clean}")
            return True, GuardResult(
                is_relevant=False,
                relevance_type=QueryRelevance.OBFUSCATED,
                reason="Query has suspiciously low character diversity",
                confidence=0.75,
                suggested_message="🤔 I couldn't understand that query format. Please ask clearly."
            )
        
        return False, None
    
    # ═══════════════════════════════════════════════════════════════════════
    # LAYER 3: SEMANTIC VALIDITY
    # ═══════════════════════════════════════════════════════════════════════
    
    def _check_semantic_validity(self, query: str) -> Tuple[bool, Optional[GuardResult]]:
        """Check if query has valid semantic structure."""
        
        query_lower = query.lower()
        tokens = re.findall(r'\b\w+\b', query_lower)
        
        # Check minimum length
        if len(tokens) < 2:
            logger.info(f"📢 TOO SHORT: {query}")
            return True, GuardResult(
                is_relevant=False,
                relevance_type=QueryRelevance.IRRELEVANT,
                reason="Query too short to be meaningful",
                confidence=0.7,
                suggested_message="🤔 Please provide more context in your question."
            )
        
        # Check for action word
        has_action = any(token in self.action_words for token in tokens)
        
        # Skip action word check if BRD domain keywords are present
        # (BRD queries like "explain about plant config" are valid without action words)
        brd_keywords = [
            "raw material", "additives", "plant config", "furnace config", 
            "system config", "configuration", "process", "procedure", "workflow",
            "grading plan", "lab analysis", "log book", "logbook", "tap hole",
            "ehs", "incident", "sop", "brd", "setup", "setting",
            "master data", "access control", "roles", "users",
        ]
        has_brd_keyword = any(kw in query_lower for kw in brd_keywords)
        
        if not has_action and not has_brd_keyword:
            logger.info(f"📢 NO ACTION WORD: {query}")
            return True, GuardResult(
                is_relevant=False,
                relevance_type=QueryRelevance.IRRELEVANT,
                reason="No action word detected (show, get, what, how, explain, etc.)",
                confidence=0.65,
                suggested_message="🤔 Please start with an action word: **Show**, **What**, **Get**, **How**, **Explain**."
            )
        
        # Suspicious tech/programming words that don't belong in manufacturing queries
        suspicious_words = {
            "neural", "schema", "architecture", "model", "training", "ai", "ml",
            "blockchain", "crypto", "nft", "token", "deploy", "container", "docker",
            "kubernetes", "server", "client", "localhost", "port", "http", "https",
            "algorithm", "recursive", "iterate", "array", "object", "string",
            "ur", "u", "pls", "plz", "gonna", "wanna", "dunno",  # Slang
        }
        
        suspicious_found = [t for t in tokens if t in suspicious_words]
        if suspicious_found:
            logger.info(f"📢 SUSPICIOUS WORDS: {suspicious_found} in query: {query}")
            return True, GuardResult(
                is_relevant=False,
                relevance_type=QueryRelevance.IRRELEVANT,
                reason=f"Suspicious non-manufacturing terms detected: {suspicious_found}",
                confidence=0.75,
                suggested_message="🤔 That doesn't look like a manufacturing data question.\n\n"
                                 "Try: \"Show OEE for furnace 1 last week\""
            )
        
        return False, None
    
    # ═══════════════════════════════════════════════════════════════════════
    # LAYER 4: GREETING & META DETECTION
    # ═══════════════════════════════════════════════════════════════════════
    
    def _check_greeting_meta(self, query: str) -> Tuple[bool, Optional[GuardResult]]:
        """Detect greetings, meta questions, off-topic requests."""
        
        query_lower = query.lower().strip()
        
        # Check greetings
        for pattern in self.greeting_patterns:
            if re.match(pattern, query_lower):
                logger.info(f"📢 GREETING: {query}")
                return True, GuardResult(
                    is_relevant=False,
                    relevance_type=QueryRelevance.GREETING,
                    reason="Greeting detected",
                    confidence=0.95,
                    suggested_message="👋 Hello! I'm **IGNIS Assistant**.\n\n"
                                     "I can help with:\n"
                                     "• 📊 \"Show OEE for furnace 1 last week\"\n"
                                     "• 📈 \"What is the average efficiency by shift?\"\n"
                                     "• 📖 \"What is the EHS incident reporting process?\"\n\n"
                                     "How can I help you today?"
                )
        
        # Check meta questions
        for pattern in self.meta_patterns:
            if re.search(pattern, query_lower):
                logger.info(f"📢 META QUESTION: {query}")
                return True, GuardResult(
                    is_relevant=False,
                    relevance_type=QueryRelevance.IRRELEVANT,
                    reason="Meta question about AI",
                    confidence=0.9,
                    suggested_message="🤖 I'm **IGNIS Assistant** - specialized in manufacturing data queries from the IGNIS system."
                )
        
        return False, None
    
    # ═══════════════════════════════════════════════════════════════════════
    # LAYER 5: OFF-TOPIC DETECTION
    # ═══════════════════════════════════════════════════════════════════════
    
    def _check_off_topic(self, query: str) -> Tuple[bool, Optional[GuardResult]]:
        """Detect general knowledge, chitchat, unrelated topics."""
        
        query_lower = query.lower()
        
        # Check general knowledge patterns
        for pattern in self.general_knowledge_patterns:
            if re.search(pattern, query_lower):
                logger.info(f"📢 OFF-TOPIC: {query}")
                return True, GuardResult(
                    is_relevant=False,
                    relevance_type=QueryRelevance.IRRELEVANT,
                    reason="General knowledge query (off-topic)",
                    confidence=0.9,
                    suggested_message="🎯 I specialize in **IGNIS manufacturing data**.\n\n"
                                     "Ask about: furnace, OEE, efficiency, production, defects, etc."
                )
        
        # Check programming patterns
        for pattern in self.programming_patterns:
            if re.search(pattern, query_lower):
                logger.info(f"📢 PROGRAMMING QUESTION: {query}")
                return True, GuardResult(
                    is_relevant=False,
                    relevance_type=QueryRelevance.IRRELEVANT,
                    reason="Programming/coding question detected",
                    confidence=0.9,
                    suggested_message="💻 I'm not a programming assistant!\n\n"
                                     "I specialize in **manufacturing data queries**, not coding help."
                )
        
        # Check math/arithmetic patterns (blocks "2+2 in furnace" type queries)
        for pattern in self.math_patterns:
            if re.search(pattern, query):
                logger.info(f"📢 MATH QUESTION BLOCKED: {query}")
                return True, GuardResult(
                    is_relevant=False,
                    relevance_type=QueryRelevance.IRRELEVANT,
                    reason="Math/arithmetic question detected (not a data query)",
                    confidence=0.9,
                    suggested_message="🧮 I'm not a calculator!\n\n"
                                     "I can only query **manufacturing data** from the IGNIS database.\n\n"
                                     "Try: \"Show OEE for furnace 1\" or \"What is the average efficiency?\""
                )
        
        return False, None
    
    # ═══════════════════════════════════════════════════════════════════════
    # LAYER 6: FUZZY KEYWORD MATCHING
    # ═══════════════════════════════════════════════════════════════════════
    
    def _fuzzy_keyword_match(self, query: str, tolerance: float = 0.75) -> List[str]:
        """Find domain keywords with typo tolerance using difflib."""
        
        query_tokens = re.findall(r'\b\w+\b', query.lower())
        matched_keywords = []
        
        for token in query_tokens:
            # Exact match
            if token in self.primary_keywords or token in self.secondary_keywords:
                matched_keywords.append(token)
            else:
                # Fuzzy match
                all_keywords = self.primary_keywords + self.secondary_keywords
                matches = difflib.get_close_matches(token, all_keywords, n=1, cutoff=tolerance)
                if matches:
                    matched_keywords.append(matches[0])
            
            # Check variant spellings
            for keyword, variants in self.keyword_variants.items():
                if token in variants:
                    matched_keywords.append(keyword)
        
        return list(set(matched_keywords))
    
    def _check_domain_relevance(self, query: str) -> Tuple[bool, Optional[GuardResult]]:
        """Check if query contains sufficient domain keywords."""
        
        query_lower = query.lower()
        
        # ══════════════════════════════════════════════════════════════════════
        # COMPREHENSIVE BRD MULTI-WORD PHRASES
        # Extracted from actual 33 BRD PDF documents in /brd folder
        # ══════════════════════════════════════════════════════════════════════
        brd_multiword_phrases = [
            # ═══════════════════════════════════════════════════════════════════
            # BRD S03 - System Configuration
            # ═══════════════════════════════════════════════════════════════════
            "plant config", "plant configuration",
            "furnace config", "furnace configuration",
            "system config", "system configuration",
            "user access", "user access control",
            "access control", "roles", "users",
            
            # ═══════════════════════════════════════════════════════════════════
            # BRD S04 - Master Data & Material Maintenance
            # ═══════════════════════════════════════════════════════════════════
            "master data", "material maintenance",
            "raw material", "raw materials", "furnace raw material", "furnace raw materials",
            "additives", "additive",
            "byproduct", "byproducts", "by-product", "by-products", "by product", "by products",
            "wip", "work in progress",
            "grading plan", "grading",
            "products", "product",
            
            # ═══════════════════════════════════════════════════════════════════
            # BRD S05 - Core Process
            # ═══════════════════════════════════════════════════════════════════
            "core process", "core process production",
            "production process", "process flow",
            "tapping", "tap", "cast", "electrode",
            
            # ═══════════════════════════════════════════════════════════════════
            # BRD S06 - Reports
            # ═══════════════════════════════════════════════════════════════════
            "raw material consumption", "raw material consumption report",
            "raw material analysis", "raw material analysis report",
            "raw material size analysis", "size analysis",
            "spout analysis", "spout analysis report",
            "tap analysis", "tap analysis report",
            "production report", "production",
            "downtime analysis", "downtime analysis report", "downtime report",
            "quality summary", "quality summary report", "quality report",
            "report format", "report structure", "report fields", "reports",
            
            # ═══════════════════════════════════════════════════════════════════
            # BRD S08 - Lab Analysis
            # ═══════════════════════════════════════════════════════════════════
            "lab analysis", "laboratory analysis", "laboratory",
            "lab raw material", "lab raw material analysis",
            "lab spout analysis", "lab spout",
            "lab tap analysis", "lab tap",
            
            # ═══════════════════════════════════════════════════════════════════
            # BRD S09 - Log Book
            # ═══════════════════════════════════════════════════════════════════
            "log book", "logbook", "log",
            "tap hole", "tap hole log",
            "furnace bed", "furnace bed log", "bed log",
            "furnace downtime", "furnace downtime log", "downtime log",
            
            # ═══════════════════════════════════════════════════════════════════
            # BRD S013 - EHS (Environment Health Safety)
            # ═══════════════════════════════════════════════════════════════════
            "ehs", "incident", "incident reporting", "incident report",
            "safety", "safety reporting", "safety report",
            "environment", "environment health", "environment health safety",
            "health safety",
            
            # ═══════════════════════════════════════════════════════════════════
            # General BRD/SOP/Documentation Terms
            # ═══════════════════════════════════════════════════════════════════
            "brd", "sop", "procedure", "workflow", "guideline", "guidelines",
            "policy", "process", "requirement", "specification",
            "configure", "configuration", "setup", "setting", "settings",
            
            # ═══════════════════════════════════════════════════════════════════
            # Question Patterns that indicate BRD queries
            # ═══════════════════════════════════════════════════════════════════
            "how to", "how do", "how does", "how can", "how should",
            "tell me about", "explain about", "explain the",
            "describe", "describe the", "definition", "define",
            "what is the process", "what are the steps",
            "what does", "meaning of",
        ]
        
        # Check if any multi-word phrase is in the query
        for phrase in brd_multiword_phrases:
            if phrase in query_lower:
                logger.info(f"✓ Multi-word BRD phrase matched: '{phrase}'")
                return False, None
        
        # Fall back to token-based fuzzy matching
        matched = self._fuzzy_keyword_match(query)
        
        if len(matched) == 0:
            logger.info(f"📢 NO DOMAIN KEYWORDS: {query}")
            return True, GuardResult(
                is_relevant=False,
                relevance_type=QueryRelevance.IRRELEVANT,
                reason="No manufacturing domain keywords found",
                confidence=0.8,
                suggested_message="🤔 That doesn't seem to be about manufacturing data.\n\n"
                                 "Try: \"Show OEE for furnace 1 last week\""
            )
        
        return False, None
    
    # ═══════════════════════════════════════════════════════════════════════
    # LAYER 7: RATE LIMITING
    # ═══════════════════════════════════════════════════════════════════════
    
    def _check_rate_limits(self, user_id: str, query: str) -> Tuple[bool, Optional[GuardResult]]:
        """Detect spam, identical queries, rate limit abuse."""
        
        if user_id not in self.query_history:
            self.query_history[user_id] = []
        
        history = self.query_history[user_id]
        
        # Check identical query count
        identical_count = sum(1 for q in history if q.lower().strip() == query.lower().strip())
        if identical_count >= self.rate_limits["identical_queries"]:
            logger.warning(f"⚠️ RATE LIMIT: Too many identical queries from {user_id}")
            return True, GuardResult(
                is_relevant=False,
                relevance_type=QueryRelevance.SPAM,
                reason="Too many identical queries detected",
                confidence=0.95,
                suggested_message="🔄 Please don't repeat the same question. Ask something different!"
            )
        
        # Add to history (keep last 50)
        history.append(query)
        history = history[-50:]
        self.query_history[user_id] = history
        
        return False, None
    
    # ═══════════════════════════════════════════════════════════════════════
    # MAIN CHECK METHOD
    # ═══════════════════════════════════════════════════════════════════════
    
    def check_query_relevance(
        self,
        query: str,
        user_id: str = "anonymous",
        enable_rate_limiting: bool = True,
    ) -> GuardResult:
        """
        Multi-layer query guard check.
        
        Args:
            query: User's question
            user_id: For rate limiting and history tracking
            enable_rate_limiting: Check rate limits and history
            
        Returns:
            GuardResult with relevance status and confidence
        """
        
        # Empty query check
        if not query or not isinstance(query, str):
            return GuardResult(
                is_relevant=False,
                relevance_type=QueryRelevance.IRRELEVANT,
                reason="Empty or invalid query",
                confidence=1.0,
                suggested_message="Please provide a question."
            )
        
        query = query.strip()
        
        # LAYER 1: Security threats
        is_blocked, result = self._check_security_threats(query)
        if is_blocked:
            return result
        
        # LAYER 2: Gibberish & repetition
        is_blocked, result = self._check_gibberish(query)
        if is_blocked:
            return result
        
        # LAYER 3: Semantic validity
        is_blocked, result = self._check_semantic_validity(query)
        if is_blocked:
            return result
        
        # LAYER 4: Greeting & meta questions
        is_blocked, result = self._check_greeting_meta(query)
        if is_blocked:
            return result
        
        # LAYER 5: Off-topic detection
        is_blocked, result = self._check_off_topic(query)
        if is_blocked:
            return result
        
        # LAYER 6: Domain relevance
        is_blocked, result = self._check_domain_relevance(query)
        if is_blocked:
            return result
        
        # LAYER 7: Rate limiting (optional)
        if enable_rate_limiting:
            is_blocked, result = self._check_rate_limits(user_id, query)
            if is_blocked:
                return result
        
        # ✅ PASSED ALL CHECKS
        logger.info(f"✓ Query PASSED all checks: {query[:60]}...")
        return GuardResult(
            is_relevant=True,
            relevance_type=QueryRelevance.RELEVANT,
            reason="Query passed all validation layers",
            confidence=0.95,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Global guard instance for reuse
_guard_instance = None

def get_guard() -> EnhancedQueryGuard:
    """Get singleton guard instance."""
    global _guard_instance
    if _guard_instance is None:
        _guard_instance = EnhancedQueryGuard()
    return _guard_instance


def check_query(query: str, user_id: str = "anonymous") -> GuardResult:
    """Quick guard check with all layers enabled."""
    return get_guard().check_query_relevance(query, user_id=user_id)


def check_query_fast(query: str) -> GuardResult:
    """Fast guard check - security + semantic only (skip rate limiting)."""
    return get_guard().check_query_relevance(query, enable_rate_limiting=False)


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY
# ═══════════════════════════════════════════════════════════════════════════════

# Alias for backward compatibility with main.py
QueryGuard = EnhancedQueryGuard

# Export keywords for backward compatibility
IGNIS_KEYWORDS = [
    "furnace", "oee", "efficiency", "production", "defect",
    "yield", "downtime", "quality", "output", "shift",
    "ignis", "mes", "equipment", "machine",
    "mtbf", "mttr", "mtbs", "fpy", "compliance", "utilization",
    "tap", "cast", "tapping", "grading", "electrode",
    "ehs", "brd", "sop", "process", "metric", "kpi",
    "today", "yesterday", "last week", "last month",
]


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    guard = EnhancedQueryGuard()
    
    test_cases = [
        ("Show OEE for furnace 1 last week", "valid"),
        ("What is the average efficiency by shift?", "valid"),
        ("Show * FROM furnace WHERE '1'='1", "security"),
        ("aaaaaaaaa bbbbbbbb", "gibberish"),
        ("Hello there!", "greeting"),
        ("What's the weather today?", "offtopic"),
        ("furnace", "action"),
        ("what to use int or let in js for ignis", "programming"),
        ("can u tell that vinay is going to marry", "no_keyword"),
    ]
    
    print("\n" + "="*70)
    print("ENHANCED QUERY GUARD - TEST RESULTS")
    print("="*70 + "\n")
    
    for query, test_type in test_cases:
        result = guard.check_query_relevance(query)
        status = "✓" if (test_type == "valid" and result.is_relevant) or \
                        (test_type != "valid" and not result.is_relevant) else "✗"
        
        print(f"{status} [{test_type.upper():12}] {query[:50]:<50}")
        print(f"   → {result.relevance_type.value:12} | Confidence: {result.confidence:.2f}")
        print(f"   → Reason: {result.reason}")
        print()
