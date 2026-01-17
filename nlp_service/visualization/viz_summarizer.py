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

    # Temporal patterns: be careful not to match metric columns like 'cycle_time', 'downtime'
    # Use patterns that specifically indicate date/time columns, not time-based metrics
    TEMPORAL_PATTERNS = [
        'date', 'timestamp', 'created_at', 'updated_at', 'created', 'updated',
        'start_time', 'end_time', 'record_date', 'shift_date',
        '_date', '_timestamp'  # Suffix patterns
    ]

    # Metric patterns that look temporal but are actually numeric values
    # Based on FEW_SHOT_EXAMPLES KPI tables
    METRIC_TIME_PATTERNS = [
        'cycle_time', 'downtime', 'runtime', 'uptime', 'lead_time',
        'processing_time', 'wait_time', 'idle_time', 'duration',
        'mtbf', 'mttr', 'mtbs',  # Mean time metrics
        'downtime_hours', 'mtbf_hours', 'mttr_hours', 'mtbs_hours',
        '_time', '_hours'  # Suffix patterns for time-based metrics
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

            # Check if it's a time-based METRIC first (cycle_time, downtime, etc.)
            # These are numeric values, not temporal columns
            is_metric_time = any(pattern in col_lower for pattern in self.METRIC_TIME_PATTERNS)

            # Check if values are numeric - actual metric values take priority
            if sample_values and all(isinstance(v, (int, float)) for v in sample_values):
                # Treat ID-like columns as categorical even if numeric
                if col_lower.endswith(('_no', '_id', '_code')):
                    categorical_cols.append(col)
                else:
                    numeric_cols.append(col)
            # Check temporal patterns (but NOT if it's a time metric)
            elif not is_metric_time and any(pattern in col_lower for pattern in self.TEMPORAL_PATTERNS):
                temporal_cols.append(col)
            # Check categorical patterns by column NAME (for string columns)
            elif any(pattern in col_lower for pattern in self.CATEGORICAL_PATTERNS):
                categorical_cols.append(col)
            # Also treat columns ending with _type, _name as categorical
            elif col_lower.endswith(('_type', '_name')):
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
        distribution = self._detect_distribution(question)
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
            "distribution_detected": distribution,
            "trend_detected": trend,
            "sample_values": results[:3] if len(results) <= 3 else results[:2]
        }

    # Pattern definitions for query analysis
    AGGREGATION_PATTERNS = {
        'AVG': ['average', 'avg', 'mean'],
        'SUM': ['total', 'sum', 'cumulative'],
        'COUNT': ['count', 'how many', 'number of'],
        'MAX': ['maximum', 'max', 'highest', 'best', 'top'],
        'MIN': ['minimum', 'min', 'lowest', 'worst', 'bottom'],
    }

    COMPARISON_PATTERNS = [
        'compare', 'versus', 'vs', 'between', 'difference',
        'by furnace', 'by shift', 'by machine', 'by plant', 'by workshop',
        'by product', 'by material', 'by supplier', 'by equipment', 'by operator',
        'by type', 'by category', 'by status', 'by grade', 'by reason',
        'each furnace', 'each shift', 'each machine', 'each product',
        'per furnace', 'per shift', 'per machine', 'per product',
        'for each furnace', 'for each shift', 'for each machine',
        'rank', 'ranking', 'top 5', 'top 10', 'top', 'bottom', 'best', 'worst',
        'highest', 'lowest', 'most', 'least',
        'which furnace', 'which shift', 'which machine', 'which product',
        'across', 'all furnaces', 'all shifts', 'all machines', 'all products',
        'statistics', 'summary by', 'grouped by', 'group by',
        'show by', 'list by', 'display by', 'get by'
    ]

    DISTRIBUTION_PATTERNS = [
        'breakdown', 'distribution', 'proportion', 'percentage of',
        'share', 'composition', 'split', 'allocation',
        'by type', 'by category', 'by reason', 'by cause',
        'by status', 'by grade', 'by priority', 'by classification',
        'grade distribution', 'status summary', 'quality distribution',
        'defect breakdown', 'failure distribution',
        'what percent', 'how much of', 'portion of'
    ]

    TREND_PATTERNS = [
        'trend', 'over time', 'history', 'historical',
        'last week', 'last month', 'last year', 'last 7 days', 'last 30 days',
        'past', 'recent', 'daily', 'weekly', 'monthly', 'yearly',
        'change', 'progression', 'evolution', 'increasing', 'decreasing',
        'display trend', 'show trend', 'trend for'
    ]

    def _matches_any(self, text: str, patterns: list) -> bool:
        """Check if text matches any pattern in the list."""
        return any(p in text for p in patterns)

    def _detect_aggregation(self, question: str) -> str:
        """Detect aggregation type from question."""
        q = question.lower()
        for agg_type, patterns in self.AGGREGATION_PATTERNS.items():
            if self._matches_any(q, patterns):
                return agg_type
        return None

    def _detect_comparison(self, question: str) -> bool:
        """Detect if question asks for comparison (bar chart)."""
        return self._matches_any(question.lower(), self.COMPARISON_PATTERNS)

    def _detect_distribution(self, question: str) -> bool:
        """Detect if question asks for distribution/breakdown (pie chart)."""
        return self._matches_any(question.lower(), self.DISTRIBUTION_PATTERNS)

    def _detect_trend(self, question: str) -> bool:
        """Detect if question asks for trend/time series (line chart)."""
        return self._matches_any(question.lower(), self.TREND_PATTERNS)
