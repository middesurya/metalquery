"""
accuracy_scorer.py - Quality & Confidence Scoring for SQL Generation

This module calculates two key metrics for every generated SQL query:
1. Confidence (Systematic): Based on static analysis (syntax, schema validity).
2. Relevance (Semantic): Based on LLM evaluation of Question <-> SQL alignment.
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config import settings

logger = logging.getLogger(__name__)

class AccuracyScorer:
    """
    Scoring engine to rate SQL generation quality.
    Separates 'Quality' (this class) from 'Security' (Guardrails).
    """

    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.model_name,
            temperature=0,
            max_tokens=128  # Short response for scoring
        )

    def calculate_confidence(self, diagnostic_result: Dict[str, Any]) -> int:
        """
        Calculates a heuristic confidence score (0-100) based on diagnostic results.
        
        Logic:
        - Base Score: 100
        - Penalties:
            - Critical Error (Invalid SQL, Table not found): -100
            - Major Error (Column not found): -20 per error
            - Warning (Type mismatch, risky pattern): -5 per warning
        """
        score = 100
        
        errors = diagnostic_result.get('errors', [])
        warnings = diagnostic_result.get('warnings', [])

        # 1. Critical Errors: Immediate failure
        if not diagnostic_result.get('valid', False):
            return 0  # Invalid SQL is 0 confidence
        
        if any("table" in e.lower() and "not found" in e.lower() for e in errors):
            return 0
            
        # 2. Major Errors (if any remained in 'errors' list but considered valid for some reason)
        score -= (len(errors) * 20)
        
        # 3. Warnings (Minor issues)
        score -= (len(warnings) * 5)
        
        # Clamp score
        return max(0, min(100, score))

    async def calculate_relevance(self, question: str, sql: str) -> int:
        """
        Uses LLM to judge semantic relevance: "Does this SQL answer the question?"
        Returns 0-100.
        """
        try:
            prompt = f"""You are a SQL Quality Judge. Rate the relevance of the SQL to the User Question on a scale of 0-100.

User Question: "{question}"
Generated SQL: "{sql}"

Scoring Criteria:
- 100: Perfect match (Correct structure, efficient, captures intent).
- 80-99: Good match (Minor issues, maybe extra columns or slightly inefficient).
- 50-79: Acceptable (Technically correct but might miss nuance, e.g. "show 5" but missing LIMIT).
- < 50: Poor/Wrong (Completely wrong table, missing filters, or answering a different question).

Return ONLY a JSON object:
{{
    "score": <integer_0_to_100>,
    "reason": "<short_explanation>"
}}
"""
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()
            
            # Clean potential markdown
            if "```" in content:
                content = content.split("```")[1].replace("json", "").strip()
            
            data = json.loads(content)
            score = int(data.get("score", 0))
            reason = data.get("reason", "No reason provided")
            
            logger.info(f"⚖️ Relevance Scored: {score}/100 - {reason}")
            return score, reason
            
        except Exception as e:
            logger.warning(f"Relevance scoring failed: {e}")
            return 50, str(e)  # Default to neutral if scoring fails
