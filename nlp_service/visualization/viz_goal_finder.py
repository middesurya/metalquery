"""
Visualization Goal Finder - Uses LLM to determine optimal chart type.
Inspired by Microsoft LIDA's goal exploration module.
"""

import json
import logging
from typing import Dict, Optional
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


class VizGoalFinder:
    """
    Uses Groq LLM to determine the best visualization type
    based on data summary and user question.
    """

    CHART_SELECTION_PROMPT = """You are a data visualization expert for manufacturing analytics dashboards.

Given the data summary and user question below, determine the best chart type to visualize the results.

DATA SUMMARY:
{data_summary}

USER QUESTION: "{question}"

CHART TYPE OPTIONS:
1. "gauge" - Single KPI value with progress indicator (best for: current OEE, single metric)
2. "kpi_card" - Single metric card with optional trend (best for: one value answers)
3. "line" - Time series line chart (best for: trends over time, historical data)
4. "area" - Filled area chart (best for: cumulative values, volume over time)
5. "bar" - Vertical bar chart (best for: comparing categories, rankings)
6. "pie" - Pie/donut chart (best for: percentage breakdowns, distributions)
7. "metric_grid" - Multiple metrics in grid (best for: dashboard with several KPIs)
8. "table" - Raw data table (best for: detailed multi-column data, complex queries)

DECISION RULES:
- Single numeric value (1 row, 1-2 numeric columns) → "gauge" or "kpi_card"
- Time series with dates → "line" or "area"
- Comparing across categories (furnaces, shifts) → "bar"
- Percentage breakdown or distribution → "pie"
- Multiple KPIs in one row → "metric_grid"
- More than 20 rows or complex data → "table"

Return ONLY valid JSON (no markdown, no explanation):
{{"chart_type": "<type>", "x_axis": "<column or null>", "y_axis": "<column or null>", "title": "<chart title>", "reasoning": "<brief reason>"}}"""

    async def find_goal(self, data_summary: Dict, question: str, llm) -> Dict:
        """
        Use LLM to determine visualization goal.

        Args:
            data_summary: Data characteristics from DataSummarizer
            question: User's original question
            llm: LangChain LLM instance

        Returns:
            Visualization goal dict with chart_type, axes, title
        """
        try:
            # Prepare summary for prompt (limit size)
            summary_for_prompt = {
                "row_count": data_summary.get("row_count"),
                "columns": data_summary.get("columns"),
                "numeric_columns": data_summary.get("numeric_columns"),
                "categorical_columns": data_summary.get("categorical_columns"),
                "temporal_columns": data_summary.get("temporal_columns"),
                "is_single_value": data_summary.get("is_single_value"),
                "has_time_series": data_summary.get("has_time_series"),
                "sample": data_summary.get("sample_values", [])[:2]
            }

            prompt = self.CHART_SELECTION_PROMPT.format(
                data_summary=json.dumps(summary_for_prompt, indent=2, default=str),
                question=question
            )

            response = llm.invoke([HumanMessage(content=prompt)])
            return self._parse_response(response.content, data_summary)

        except Exception as e:
            logger.warning(f"LLM goal finding failed: {e}, using heuristics")
            return self.find_goal_heuristic(data_summary, question)

    def _parse_response(self, content: str, data_summary: Dict) -> Dict:
        """Parse LLM JSON response safely."""
        try:
            # Clean up response
            content = content.strip()

            # Remove markdown code blocks if present (handle various formats)
            if content.startswith('```'):
                lines = content.split('\n')
                # Find the closing ``` more safely
                start_idx = 1
                end_idx = len(lines)
                for i in range(len(lines) - 1, 0, -1):
                    if lines[i].strip() == '```':
                        end_idx = i
                        break
                content = '\n'.join(lines[start_idx:end_idx])
                content = content.strip()

            # Remove 'json' prefix if present
            if content.startswith('json'):
                content = content[4:].strip()

            # Try to extract JSON object if there's extra text
            if not content.startswith('{'):
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group()

            result = json.loads(content)

            # Validate result is a dict
            if not isinstance(result, dict):
                logger.warning(f"LLM returned non-dict: {type(result)}")
                return self.find_goal_heuristic(data_summary, "")

            # Validate chart_type
            valid_types = {'gauge', 'kpi_card', 'line', 'area', 'bar', 'pie', 'metric_grid', 'table'}
            if result.get('chart_type') not in valid_types:
                logger.warning(f"Invalid chart_type: {result.get('chart_type')}")
                return self.find_goal_heuristic(data_summary, "")

            return result

        except (json.JSONDecodeError, IndexError, TypeError) as e:
            logger.warning(f"JSON parse error: {e}")
            return self.find_goal_heuristic(data_summary, "")

    def find_goal_heuristic(self, data_summary: Dict, question: str) -> Dict:
        """
        Fallback heuristic-based goal finding when LLM is unavailable.

        Args:
            data_summary: Data characteristics
            question: User's question

        Returns:
            Visualization goal dict
        """
        row_count = data_summary.get('row_count', 0)
        numeric_cols = data_summary.get('numeric_columns', [])
        categorical_cols = data_summary.get('categorical_columns', [])
        temporal_cols = data_summary.get('temporal_columns', [])

        # Rule 1: Single value → gauge or kpi_card
        if data_summary.get('is_single_value'):
            y_col = numeric_cols[0] if numeric_cols else None
            title = self._generate_title(question, y_col)

            # Use gauge for percentage metrics
            if y_col and any(p in y_col.lower() for p in ['percent', 'oee', 'yield', 'rate', 'efficiency']):
                return {
                    "chart_type": "gauge",
                    "y_axis": y_col,
                    "title": title
                }
            return {
                "chart_type": "kpi_card",
                "y_axis": y_col,
                "title": title
            }

        # Rule 2: Multiple KPIs in single row → metric_grid
        if data_summary.get('is_multi_metric') and len(numeric_cols) >= 2:
            return {
                "chart_type": "metric_grid",
                "title": self._generate_title(question, None)
            }

        # Rule 3: Time series → line chart
        if data_summary.get('has_time_series') and temporal_cols and numeric_cols:
            return {
                "chart_type": "line",
                "x_axis": temporal_cols[0],
                "y_axis": numeric_cols[0],
                "title": self._generate_title(question, numeric_cols[0])
            }

        # Rule 4: Trend detected → line chart
        if data_summary.get('trend_detected') and numeric_cols:
            x_col = temporal_cols[0] if temporal_cols else (categorical_cols[0] if categorical_cols else None)
            return {
                "chart_type": "line" if x_col else "bar",
                "x_axis": x_col,
                "y_axis": numeric_cols[0],
                "title": self._generate_title(question, numeric_cols[0])
            }

        # Rule 5: Distribution explicitly requested → pie chart (check BEFORE bar comparison)
        # Keywords like "breakdown", "distribution", "proportion" trigger pie charts
        if data_summary.get('distribution_detected') and data_summary.get('is_distribution') and row_count <= 8:
            x_col = categorical_cols[0] if categorical_cols else None
            y_col = numeric_cols[0] if numeric_cols else None
            if x_col and y_col:
                return {
                    "chart_type": "pie",
                    "x_axis": x_col,
                    "y_axis": y_col,
                    "title": self._generate_title(question, y_col)
                }

        # Rule 6: Comparison → bar chart
        if data_summary.get('comparison_detected') or data_summary.get('is_comparison'):
            x_col = categorical_cols[0] if categorical_cols else None
            y_col = numeric_cols[0] if numeric_cols else None
            if x_col and y_col:
                return {
                    "chart_type": "bar",
                    "x_axis": x_col,
                    "y_axis": y_col,
                    "title": self._generate_title(question, y_col)
                }

        # Rule 7: Distribution with few categories → pie chart (fallback)
        if data_summary.get('is_distribution') and row_count <= 8:
            x_col = categorical_cols[0] if categorical_cols else None
            y_col = numeric_cols[0] if numeric_cols else None
            if x_col and y_col:
                return {
                    "chart_type": "pie",
                    "x_axis": x_col,
                    "y_axis": y_col,
                    "title": self._generate_title(question, y_col)
                }

        # Rule 7: Categorical with values → bar chart
        if categorical_cols and numeric_cols and row_count <= 20:
            return {
                "chart_type": "bar",
                "x_axis": categorical_cols[0],
                "y_axis": numeric_cols[0],
                "title": self._generate_title(question, numeric_cols[0])
            }

        # Rule 8: Small dataset with time aspect → line
        if row_count <= 30 and numeric_cols:
            x_col = temporal_cols[0] if temporal_cols else (categorical_cols[0] if categorical_cols else None)
            if x_col:
                return {
                    "chart_type": "line",
                    "x_axis": x_col,
                    "y_axis": numeric_cols[0],
                    "title": self._generate_title(question, numeric_cols[0])
                }

        # Default: table for complex data
        return {
            "chart_type": "table",
            "title": "Query Results"
        }

    def _generate_title(self, question: str, metric_col: Optional[str]) -> str:
        """Generate a chart title from question and metric."""
        # Clean up question for title
        q = question.strip()
        if q.endswith('?'):
            q = q[:-1]

        # Shorten long questions
        if len(q) > 50:
            # Try to extract key part
            keywords = ['show', 'what is', 'get', 'display', 'list', 'find']
            for kw in keywords:
                if kw in q.lower():
                    idx = q.lower().find(kw)
                    q = q[idx + len(kw):].strip()
                    break
            if len(q) > 50:
                q = q[:47] + "..."

        # Capitalize first letter
        return q[0].upper() + q[1:] if q else (metric_col or "Results")
