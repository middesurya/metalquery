"""
Data Summarizer - Analyzes SQL results for visualization decisions.
Inspired by Microsoft LIDA's summarization module.
"""

from typing import List, Dict, Any
import re


class DataSummarizer:
    """
    Summarizes SQL results into a compact representation
    for LLM chart type selection.
    """

    TEMPORAL_PATTERNS = [
        'date', 'time', 'timestamp', 'created', 'updated',
        'day', 'month', 'year', 'week', 'hour', 'minute',
        'start_time', 'end_time', 'record_date', 'shift_date'
    ]

    CATEGORICAL_PATTERNS = [
        'name', 'type', 'category', 'status', 'shift',
        'furnace', 'machine', 'operator', 'grade', 'product',
        'reason', 'cause', 'location', 'plant'
    ]

    def summarize(self, results: List[Dict], question: str) -> Dict:
        """
        Summarize data characteristics for visualization decision.

        Args:
            results: SQL query results
            question: User's original question

        Returns:
            Dictionary with data summary
        """
        if not results:
            return {
                "shape": "empty",
                "row_count": 0,
                "column_count": 0,
                "summary": "No data available"
            }

        columns = list(results[0].keys()) if results else []

        # Analyze column types
        numeric_cols = []
        categorical_cols = []
        temporal_cols = []

        for col in columns:
            col_lower = col.lower()
            sample_values = [r.get(col) for r in results[:10] if r.get(col) is not None]

            # Check temporal first
            if any(pattern in col_lower for pattern in self.TEMPORAL_PATTERNS):
                temporal_cols.append(col)
            # Check if numeric
            elif sample_values and all(isinstance(v, (int, float)) for v in sample_values):
                numeric_cols.append(col)
            # Check categorical patterns
            elif any(pattern in col_lower for pattern in self.CATEGORICAL_PATTERNS):
                categorical_cols.append(col)
            # Default: if string, treat as categorical
            elif sample_values and all(isinstance(v, str) for v in sample_values):
                categorical_cols.append(col)

        # Determine data shape
        row_count = len(results)
        col_count = len(columns)

        # Detect query patterns
        aggregation = self._detect_aggregation(question)
        comparison = self._detect_comparison(question)
        trend = self._detect_trend(question)

        return {
            "row_count": row_count,
            "column_count": col_count,
            "columns": columns,
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "temporal_columns": temporal_cols,
            "has_time_series": len(temporal_cols) > 0 and len(numeric_cols) > 0,
            "is_single_value": row_count == 1 and len(numeric_cols) <= 2,
            "is_comparison": len(categorical_cols) > 0 and len(numeric_cols) > 0,
            "is_distribution": len(categorical_cols) > 0 and len(numeric_cols) == 1,
            "is_multi_metric": row_count == 1 and len(numeric_cols) >= 2,
            "aggregation_detected": aggregation,
            "comparison_detected": comparison,
            "trend_detected": trend,
            "sample_values": results[:3] if len(results) <= 3 else results[:2]
        }

    def _detect_aggregation(self, question: str) -> str:
        """Detect aggregation type from question."""
        q = question.lower()

        if any(w in q for w in ['average', 'avg', 'mean']):
            return 'AVG'
        if any(w in q for w in ['total', 'sum', 'cumulative']):
            return 'SUM'
        if any(w in q for w in ['count', 'how many', 'number of']):
            return 'COUNT'
        if any(w in q for w in ['maximum', 'max', 'highest', 'best', 'top']):
            return 'MAX'
        if any(w in q for w in ['minimum', 'min', 'lowest', 'worst', 'bottom']):
            return 'MIN'
        return None

    def _detect_comparison(self, question: str) -> bool:
        """Detect if question asks for comparison."""
        q = question.lower()
        comparison_words = [
            'compare', 'versus', 'vs', 'between', 'difference',
            'by furnace', 'by shift', 'by machine', 'by plant',
            'each furnace', 'each shift', 'per furnace', 'per shift',
            'breakdown', 'distribution'
        ]
        return any(w in q for w in comparison_words)

    def _detect_trend(self, question: str) -> bool:
        """Detect if question asks for trend/time series."""
        q = question.lower()
        trend_words = [
            'trend', 'over time', 'history', 'historical',
            'last week', 'last month', 'last year', 'past',
            'daily', 'weekly', 'monthly', 'yearly',
            'change', 'progression', 'evolution'
        ]
        return any(w in q for w in trend_words)
