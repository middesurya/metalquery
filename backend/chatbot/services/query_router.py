"""
Query Router
Routes queries to NLP-SQL or RAG based on content analysis.
"""
import re
import logging
from typing import Tuple, Literal

logger = logging.getLogger(__name__)

QueryType = Literal["nlp-sql", "rag", "hybrid"]


class QueryRouter:
    """
    Routes queries to the appropriate handler (SQL generation vs BRD RAG).
    Uses keyword analysis to determine query intent.
    """
    
    # Keywords that suggest SQL/data queries
    SQL_KEYWORDS = {
        # Data retrieval with numbers/metrics
        'show', 'get', 'list', 'display', 'how many',
        'total', 'average', 'sum', 'count', 'minimum', 'maximum',
        # KPIs and metrics (numeric values)
        'oee', 'efficiency', 'yield', 'downtime', 'mtbf', 'mttr',
        'output', 'defect', 'incidents', 'production',
        # Time-based (asking for data in a period)
        'last week', 'last month', 'yesterday', 'today', 'between',
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december',
        # Furnace specific data
        'furnace 1', 'furnace 2', 'furnace 3', 'furnace no',
        # Aggregations
        'by furnace', 'per furnace', 'by date', 'trend', 'compare',
    }
    
    # Keywords that suggest BRD/documentation queries
    RAG_KEYWORDS = {
        # Process questions
        'how to', 'how do', 'what is the process', 'what are the steps',
        'procedure', 'workflow', 'guidelines', 'policy', 'rule',
        # Definitions & explanations
        'define', 'definition', 'meaning', 'explain', 'describe',
        'what does', 'what is a', 'what is the', 'tell me about',
        # Specific BRD concepts
        'what is ehs', 'what is brd', 'what is sop',
        'ehs', 'environment health safety', 'incident reporting',
        # Requirements
        'requirement', 'specification', 'brd', 'document',
        'configure', 'configuration', 'setup', 'setting',
        # Roles and access
        'role', 'permission', 'access', 'user access', 'who can',
        # Master data concepts
        'master data', 'material maintenance', 'grading plan',
    }
    
    @classmethod
    def detect_query_type(cls, question: str) -> QueryType:
        """
        Detect whether query should go to NLP-SQL or RAG.
        
        Args:
            question: User's question
            
        Returns:
            'nlp-sql', 'rag', or 'hybrid'
        """
        question_lower = question.lower().strip()
        
        sql_score = 0
        rag_score = 0
        
        # Check for SQL keywords
        for keyword in cls.SQL_KEYWORDS:
            if keyword in question_lower:
                sql_score += len(keyword.split())
        
        # Check for RAG keywords
        for keyword in cls.RAG_KEYWORDS:
            if keyword in question_lower:
                rag_score += len(keyword.split()) * 2  # RAG weighted higher
        
        # Special patterns
        if re.search(r'\b\d+\b', question_lower):  # Contains numbers
            sql_score += 2
        if re.search(r'(percentage|%|hours|tons|kwh)', question_lower):
            sql_score += 3
        if re.search(r'how (to|do|does|can|should)', question_lower):
            rag_score += 5
        
        logger.debug(f"Query routing scores - SQL: {sql_score}, RAG: {rag_score}")
        
        if sql_score > rag_score:
            return 'nlp-sql'
        elif rag_score > sql_score:
            return 'rag'
        else:
            return 'hybrid'
    
    @classmethod
    def get_confidence(cls, question: str) -> Tuple[QueryType, float]:
        """
        Get query type with confidence score.
        
        Returns:
            Tuple of (query_type, confidence)
        """
        question_lower = question.lower().strip()
        
        sql_score = sum(1 for kw in cls.SQL_KEYWORDS if kw in question_lower)
        rag_score = sum(1 for kw in cls.RAG_KEYWORDS if kw in question_lower)
        
        total = sql_score + rag_score
        if total == 0:
            return 'hybrid', 0.5
        
        query_type = cls.detect_query_type(question)
        
        if query_type == 'nlp-sql':
            confidence = min(sql_score / total, 0.95)
        elif query_type == 'rag':
            confidence = min(rag_score / total, 0.95)
        else:
            confidence = 0.5
        
        return query_type, confidence


# Convenience function
def route_query(question: str) -> QueryType:
    """Route a query to NLP-SQL or RAG handler."""
    return QueryRouter.detect_query_type(question)
