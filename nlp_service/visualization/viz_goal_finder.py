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
1. "progress_bar" - Single KPI with horizontal progress bar (best for: current OEE, percentages)
2. "kpi_card" - Single metric card with optional trend (best for: non-percentage values)
3. "line" - Time series line chart (best for: trends over time, historical data)
4. "area" - Filled area chart (best for: cumulative values, volume over time)
5. "bar" - Vertical bar chart (best for: comparing categories, rankings)
6. "pie" - Pie/donut chart (best for: percentage breakdowns, distributions)
7. "metric_grid" - Multiple metrics in grid (best for: dashboard with several KPIs)
8. "table" - Raw data table (best for: detailed multi-column data, complex queries)

CRITICAL DECISION RULES (apply in order):
1. Single numeric value (1 row, 1-2 numeric columns) → "progress_bar" or "kpi_card"
2. Question contains "by [category]" (by furnace, by shift, by machine) → "bar" chart
3. Question asks for "breakdown", "distribution", "proportion" → "pie" chart
4. Multiple categories with numeric values (3-20 rows) → "bar" chart for comparison
5. Time series with dates AND trend keywords → "line" or "area"
6. More than 20 rows or complex multi-column data → "table"

EXAMPLES:
- "Show OEE by furnace" → bar chart (comparing furnaces)
- "Production by shift" → bar chart (comparing shifts)
- "Breakdown of defects by type" → pie chart (distribution)
- "OEE trend over last month" → line chart (time series)
- "Current OEE for furnace 1" → progress_bar (single percentage)
- "Total production count" → kpi_card (single value)

IMPORTANT: Prefer bar/pie charts over tables when data has clear categorical groupings!

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
            valid_types = {'progress_bar', 'kpi_card', 'line', 'area', 'bar', 'pie', 'metric_grid', 'table'}
            if result.get('chart_type') not in valid_types:
                logger.warning(f"Invalid chart_type: {result.get('chart_type')}")
                return self.find_goal_heuristic(data_summary, "")

            return result

        except (json.JSONDecodeError, IndexError, TypeError) as e:
            logger.warning(f"JSON parse error: {e}")
            return self.find_goal_heuristic(data_summary, "")

    # Patterns indicating "by category" aggregation queries
    BY_CATEGORY_PATTERNS = [
        'by furnace', 'by shift', 'by machine', 'by plant', 'by workshop',
        'by product', 'by material', 'by supplier', 'by equipment', 'by operator',
        'by type', 'by category', 'by status', 'by grade', 'by reason',
        'per furnace', 'per shift', 'per machine', 'each furnace', 'each shift',
        'for each', 'across furnaces', 'across shifts', 'all furnaces', 'all shifts'
    ]

    # Patterns indicating percentage-based metrics
    PERCENTAGE_PATTERNS = ['percent', 'oee', 'yield', 'rate', 'efficiency']

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
        q_lower = question.lower()

        x_col = categorical_cols[0] if categorical_cols else None
        y_col = numeric_cols[0] if numeric_cols else None

        # Rule 1: "by X" aggregation queries -> bar chart
        if any(p in q_lower for p in self.BY_CATEGORY_PATTERNS):
            if x_col and y_col and row_count >= 1:
                return self._make_goal("bar", x_col, y_col, question)

        # Rule 2: Single value -> progress_bar or kpi_card
        if data_summary.get('is_single_value'):
            title = self._generate_title(question, y_col)
            if y_col and any(p in y_col.lower() for p in self.PERCENTAGE_PATTERNS):
                return {"chart_type": "progress_bar", "y_axis": y_col, "title": title}
            return {"chart_type": "kpi_card", "y_axis": y_col, "title": title}

        # Rule 3: Multiple KPIs in single row -> metric_grid
        if data_summary.get('is_multi_metric') and len(numeric_cols) >= 2:
            return {"chart_type": "metric_grid", "title": self._generate_title(question, None)}

        # Rule 4: Distribution requested with few categories -> pie chart
        if data_summary.get('distribution_detected') and data_summary.get('is_distribution'):
            if x_col and y_col and row_count <= 8:
                return self._make_goal("pie", x_col, y_col, question)

        # Rule 5: Comparison detected -> bar chart
        if data_summary.get('comparison_detected') or data_summary.get('is_comparison'):
            if x_col and y_col and row_count >= 2:
                return self._make_goal("bar", x_col, y_col, question)

        # Rule 6: Time series with trend keywords -> line chart
        if data_summary.get('has_time_series') and data_summary.get('trend_detected'):
            if temporal_cols and numeric_cols:
                return self._make_goal("line", temporal_cols[0], numeric_cols[0], question)

        # Rule 7: Categorical with values (3-50 rows) -> bar chart
        if categorical_cols and numeric_cols and 3 <= row_count <= 50:
            return self._make_goal("bar", categorical_cols[0], numeric_cols[0], question)

        # Rule 8: Distribution fallback -> pie chart
        if data_summary.get('is_distribution') and row_count <= 8:
            if x_col and y_col:
                return self._make_goal("pie", x_col, y_col, question)

        # Rule 9: Small temporal dataset without categories -> line chart
        if row_count <= 30 and numeric_cols and not categorical_cols and temporal_cols:
            return self._make_goal("line", temporal_cols[0], numeric_cols[0], question)

        return {"chart_type": "table", "title": "Query Results"}

    def _make_goal(self, chart_type: str, x_col: str, y_col: str, question: str) -> Dict:
        """Create a standardized goal dictionary."""
        return {
            "chart_type": chart_type,
            "x_axis": x_col,
            "y_axis": y_col,
            "title": self._generate_title(question, y_col)
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
