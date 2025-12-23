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
    """
    
    # Keywords that suggest SQL/data queries
    SQL_KEYWORDS = {
        # Data retrieval with numbers/metrics
        "show", "get", "list", "display", "how many", "what is",
        "total", "average", "sum", "count", "minimum", "maximum",
        # KPIs and metrics (numeric values)
        "oee", "efficiency", "yield", "downtime", "mtbf", "mttr",
        "output", "defect", "incidents", "energy", "production",
        # Time-based (asking for data in a period)
        "last week", "last month", "last year", "yesterday", "today", "between",
        "last 7 days", "last 30 days", "last 90 days", "last 365 days",
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",
        # Furnace specific data
        "furnace 1", "furnace 2", "furnace 3", "furnace no",
        # Aggregations
        "by furnace", "per furnace", "by date", "trend", "compare",
    }
    
    # KPI metrics - when combined with "what is", route to SQL not BRD
    KPI_METRICS = {
        "oee", "efficiency", "yield", "downtime", "mtbf", "mttr", "mtbs",
        "production", "energy", "defect", "output", "cycle time",
        "maintenance compliance", "first pass yield", "rework rate",
        "capacity utilization", "on time delivery", "safety incidents",
    }
    
    # Keywords that suggest BRD/documentation queries
    BRD_KEYWORDS = {
        # Process questions
        "how to", "how do", "what is the process", "what are the steps",
        "procedure", "workflow", "guidelines", "policy", "rule",
        # Definitions & explanations (removed "what is the" - handled separately)
        "define", "definition", "meaning", "explain", "describe",
        "what does", "what is a", "tell me about",
        # Specific BRD concepts (high priority)
        "what is ehs", "what is brd", "what is sop",
        "ehs", "environment health safety", "incident reporting", "safety reporting",
        # Requirements
        "requirement", "specification", "brd", "document",
        "configure", "configuration", "setup", "setting",
        # Roles and access
        "role", "permission", "access", "user access", "who can",
        # Reports structure (not data)
        "report format", "report structure", "report fields",
        # Master data concepts
        "master data", "material maintenance", "grading plan",
        # Lab analysis processes
        "lab analysis", "spout analysis", "tap analysis", "raw material analysis",
        # Log book processes
        "log book", "tap hole log", "furnace bed", "downtime log",
    }
    
    # Concepts that are ALWAYS BRD (override SQL)
    BRD_CONCEPTS = {
        "ehs", "sop", "brd", "policy", "procedure", "guideline",
        "workflow", "configuration", "requirement",
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
        
        # ✅ PRIORITY CHECK 1: "what is <kpi metric>" patterns → SQL
        # Examples: "what is the oee for furnace 1", "what is downtime last week"
        if re.search(r'what (is|are|was|were)', question_lower):
            for metric in cls.KPI_METRICS:
                if metric in question_lower:
                    logger.info(f"Routing to SQL: 'what is' + KPI metric '{metric}' detected")
                    return "sql", 0.90
        
        # ✅ PRIORITY CHECK 2: "what is <concept>" patterns → BRD (only for non-metrics)
        if re.match(r'^what (is|are|does) \w+\??$', question_lower):
            # Short "what is X" questions are typically asking for definitions
            for concept in cls.BRD_CONCEPTS:
                if concept in question_lower:
                    return "brd", 0.90
        
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
