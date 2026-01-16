"""
Query Router
Automatically detects whether a question should be answered via SQL or BRD documents.
"""
import re
import logging
from typing import Tuple, Literal

logger = logging.getLogger(__name__)

QueryType = Literal["sql", "brd", "unknown"]


class QueryRouter:
    """
    Routes queries to the appropriate handler (SQL generation vs BRD RAG).
    Enhanced with table-specific keywords for accurate routing.
    """
    
    # Keywords that suggest SQL/data queries
    SQL_KEYWORDS = {
        # Data retrieval with numbers/metrics
        "show", "get", "list", "display", "how many", "what is", "what are",
        "total", "average", "sum", "count", "minimum", "maximum", "min", "max",
        "give me", "find", "which", "where", "when",
        
        # KPIs and metrics (numeric values) - ALL 20 KPI tables
        "oee", "efficiency", "yield", "downtime", "mtbf", "mttr", "mtbs",
        "output", "defect", "incidents", "energy", "production",
        "cycle time", "rework", "compliance", "utilization", "delivery",
        "first pass", "fpy", "otd", "safety",
        
        # Cycle Time specific keywords
        "slowest", "fastest", "time per unit", "processing time",
        "above 90", "above 80", "greater than", "less than", "threshold",
        "crossed", "exceeded", "below",
        
        # Machine/Equipment keywords (from kpi tables)
        "machine", "equipment", "furnace", "cast_bay", "electrod", "unkwn_eq",
        
        # Shift-based queries
        "shift", "shift 4", "shift 12", "shift 20", "per shift", "by shift",
        
        # Product-based queries
        "product", "product_type", "m004", "met30", "met32", "material",
        
        # Time-based (asking for data in a period)
        "last week", "last month", "last year", "yesterday", "today", "between",
        "last 7 days", "last 30 days", "last 90 days", "last 365 days",
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",
        "2024", "2025", "jan 7", "jan 8", "jan 9",
        "2024-01-07", "2024-01-08", "2024-01-09",
        
        # Furnace specific data (with numbers)
        "furnace 1", "furnace 2", "furnace 3", "furnace 4", "furnace 888",
        "furnace no", "for furnace",
        
        # Aggregations and comparisons
        "by furnace", "per furnace", "by date", "per day", "by day",
        "trend", "compare", "comparison", "vs", "versus",
        "top 5", "top 10", "highest", "lowest", "best", "worst",
        "improved", "decreased", "increased", "variation", "spike", "spikes",
        "distribution",
        
        # Alert/Exception queries
        "records where", "incidents", "exceptions", "alert", "warning",
        
        # Core Process tables
        "tap", "cast weight", "tapping", "grading", "grade",
        
        # Chatbot-feel queries that map to SQL
        "investigate", "spending", "area", "changed", "caused",
    }
    
    # KPI metrics - when combined with "what is", route to SQL not BRD
    KPI_METRICS = {
        # All 20 KPI metrics
        "oee", "efficiency", "yield", "downtime", "mtbf", "mttr", "mtbs",
        "production", "energy", "defect", "output", "cycle time",
        "maintenance compliance", "first pass yield", "rework rate",
        "capacity utilization", "on time delivery", "safety incidents",
        "energy efficiency", "energy used", "output rate", "production efficiency",
        "quantity produced", "planned maintenance",
        # Derived/common terms
        "furnace health", "performance", "throughput",
    }
    
    # ════════════════════════════════════════════════════════════════════════
    # BRD KEYWORDS - From 33 BRD Documents
    # These suggest documentation/process queries rather than data queries
    # ════════════════════════════════════════════════════════════════════════
    BRD_KEYWORDS = {
        # Question patterns that indicate BRD queries
        "how to", "how do", "how does", "how can", "how should",
        "what is the process", "what are the steps",
        "procedure", "workflow", "guidelines", "policy", "rule",
        "define", "definition", "meaning", "explain", "describe",
        "what does", "tell me about", "explain about",
        
        # BRD S03 - System Configuration
        "system config", "plant config", "furnace config",
        "plant configuration", "furnace configuration", "system configuration",
        "user access control", "user access", "access control",
        "roles", "users", "configure", "configuration", "setup", "setting",
        
        # BRD S04 - Master Data & Material Maintenance
        "master data", "material maintenance",
        "furnace raw materials", "furnace raw material", "raw materials", "raw material",
        "additives", "additive",
        "byproducts", "by-products", "by products", "byproduct",
        "wip", "work in progress",
        "grading plan", "grading", "products", "product",
        
        # BRD S05 - Core Process
        "core process", "core process production", "production process", "process flow",
        "tapping", "cast", "electrode",
        
        # BRD S06 - Reports (structure, not data)
        "report format", "report structure", "report fields", "reports",
        "raw material consumption report", "raw material consumption",
        "raw material analysis report", "raw material analysis",
        "raw material size analysis", "size analysis report", "size analysis",
        "spout analysis report", "spout analysis",
        "tap analysis report", "tap analysis",
        "production report", "production report structure",
        "downtime analysis report", "downtime analysis", "downtime report",
        "quality summary report", "quality summary", "quality report",
        
        # BRD S08 - Lab Analysis
        "lab analysis", "laboratory analysis", "laboratory",
        "lab raw material", "lab raw material analysis",
        "lab spout analysis", "lab spout",
        "lab tap analysis", "lab tap",
        
        # BRD S09 - Log Book
        "log book", "logbook", "log",
        "tap hole log", "tap hole",
        "furnace downtime log", "furnace downtime", "downtime log",
        "furnace bed log", "furnace bed", "bed log",
        
        # BRD S013 - EHS
        "ehs", "incident", "incident reporting", "incident report",
        "safety reporting", "safety report", "safety",
        "environment health safety", "environment health", "health safety",
        
        # General BRD terms
        "brd", "sop", "document", "requirement", "specification",
        "who can", "permission", "role",
    }
    
    # ════════════════════════════════════════════════════════════════════════
    # BRD CONCEPTS - ALWAYS route to BRD (highest priority)
    # When "what is <concept>", route to BRD not SQL
    # ════════════════════════════════════════════════════════════════════════
    BRD_CONCEPTS = {
        # General BRD/Documentation terms
        "ehs", "sop", "brd", "policy", "procedure", "guideline", "guidelines",
        "workflow", "configuration", "requirement", "process",
        
        # BRD S03 - System Configuration
        "plant config", "plant configuration",
        "furnace config", "furnace configuration", 
        "system config", "system configuration",
        "user access", "access control", "roles", "users",
        
        # BRD S04 - Master Data & Material Maintenance
        "raw material", "raw materials", "furnace raw material", "furnace raw materials",
        "additives", "additive",
        "byproducts", "by-products", "byproduct",
        "wip", "work in progress",
        "grading plan", "material maintenance", "master data",
        
        # BRD S05 - Core Process
        "core process", "production process", "process flow",
        
        # BRD S06 - Reports (structure concepts)
        "consumption report", "production report", "quality summary", "quality report",
        "downtime analysis", "downtime report", "size analysis",
        "raw material consumption", "raw material analysis",
        
        # BRD S08 - Lab Analysis
        "lab analysis", "laboratory", "laboratory analysis",
        "spout analysis", "tap analysis",
        
        # BRD S09 - Log Book
        "log book", "logbook",
        "tap hole log", "tap hole",
        "furnace bed", "bed log", "furnace bed log",
        # Removed "furnace downtime" - conflicts with KPI data queries
        "downtime log", "furnace downtime log",

        # BRD S013 - EHS
        "incident reporting", "incident report",
        # Removed "safety" - conflicts with KPI data queries (safety incidents)
        "safety reporting",
        "environment health", "environment health safety",
    }
    
    @classmethod
    def route(cls, question: str) -> Tuple[QueryType, float]:
        """
        Determine the query type.
        
        Args:
            question: User's question
            
        Returns:
            Tuple of (query_type, confidence)
        """
        question_lower = question.lower().strip()
        
        # ═════════════════════════════════════════════════════════════════════
        # PRIORITY CHECK 0: "explain/describe/tell me about" → ALWAYS BRD
        # These are documentation questions, never SQL data queries
        # ═════════════════════════════════════════════════════════════════════
        if re.search(r'^(explain|describe|tell me about|what does|how does)', question_lower):
            logger.info(f"Routing to BRD: explanation/documentation query detected")
            return "brd", 0.95
        
        if "explain about" in question_lower or "explain the" in question_lower:
            logger.info(f"Routing to BRD: 'explain about/the' pattern detected")
            return "brd", 0.95
        
        # ✅ PRIORITY CHECK 1: "what is <BRD concept>" patterns → BRD (check FIRST!)
        # BRD concepts are more specific, so check them before generic SQL metrics
        if re.search(r'what (is|are|does|was|were)', question_lower):
            for concept in cls.BRD_CONCEPTS:
                if concept in question_lower:
                    logger.info(f"Routing to BRD: 'what is' + concept '{concept}' detected")
                    return "brd", 0.90
        
        # ✅ PRIORITY CHECK 2: "what is <kpi metric>" patterns → SQL
        # Examples: "what is the oee for furnace 1", "what is downtime last week"
        if re.search(r'what (is|are|was|were)', question_lower):
            for metric in cls.KPI_METRICS:
                if metric in question_lower:
                    logger.info(f"Routing to SQL: 'what is' + KPI metric '{metric}' detected")
                    return "sql", 0.90

        # ✅ PRIORITY CHECK 3: "show/display X by furnace/shift/date" → SQL
        # These are data aggregation queries, not documentation
        if re.search(r'(show|display|list|get) .+ (by|per) (furnace|shift|date|day|month|week)', question_lower):
            logger.info(f"Routing to SQL: 'show X by furnace/shift/date' pattern detected")
            return "sql", 0.92

        # ✅ PRIORITY CHECK 4: KPI data queries with aggregation words → SQL
        # Examples: "show downtime by furnace", "display taps by furnace"
        kpi_data_patterns = [
            r'(show|display|get|list) (total|average|sum|count)?\s*(downtime|oee|yield|energy|production|taps?|incidents)',
            r'(downtime|safety incidents|energy|yield|oee|production|taps?) (by|per) (furnace|shift)',
        ]
        for pattern in kpi_data_patterns:
            if re.search(pattern, question_lower):
                logger.info(f"Routing to SQL: KPI data query pattern detected")
                return "sql", 0.91

        sql_score = 0
        brd_score = 0
        
        # Check for SQL keywords
        for keyword in cls.SQL_KEYWORDS:
            if keyword in question_lower:
                sql_score += len(keyword.split())  # Multi-word keywords score higher
        
        # Check for BRD keywords
        for keyword in cls.BRD_KEYWORDS:
            if keyword in question_lower:
                brd_score += len(keyword.split()) * 2  # BRD keywords weighted higher
        
        # ✅ Concept override: if BRD concept present, boost BRD score
        for concept in cls.BRD_CONCEPTS:
            if concept in question_lower:
                brd_score += 5
        
        # Special patterns
        # Questions asking for numeric data are likely SQL
        if re.search(r'\b\d+\b', question_lower):  # Contains numbers
            sql_score += 2
        if re.search(r'(percentage|%|hours|tons|kwh)', question_lower):
            sql_score += 3
        
        # Questions with "how to" or "what is the process" are BRD
        if re.search(r'how (to|do|does|can|should)', question_lower):
            brd_score += 5
        if "process" in question_lower and "production" not in question_lower:
            brd_score += 3
        
        # Calculate confidence
        total_score = sql_score + brd_score
        if total_score == 0:
            return "unknown", 0.0
        
        if sql_score > brd_score:
            confidence = sql_score / total_score
            return "sql", min(confidence, 0.95)
        elif brd_score > sql_score:
            confidence = brd_score / total_score
            return "brd", min(confidence, 0.95)
        else:
            return "unknown", 0.5
    
    @classmethod
    def explain_routing(cls, question: str) -> str:
        """Explain why a query was routed a certain way."""
        query_type, confidence = cls.route(question)
        question_lower = question.lower()
        
        matched_sql = [k for k in cls.SQL_KEYWORDS if k in question_lower]
        matched_brd = [k for k in cls.BRD_KEYWORDS if k in question_lower]
        
        explanation = f"Query type: {query_type} (confidence: {confidence:.2f})\n"
        explanation += f"SQL keywords matched: {matched_sql}\n"
        explanation += f"BRD keywords matched: {matched_brd}"
        
        return explanation


# Convenience function
def route_query(question: str) -> Tuple[QueryType, float]:
    """Route a query to SQL or BRD handler."""
    return QueryRouter.route(question)
