"""
Visualization Config Generator - Generates Recharts-compatible JSON configs.
"""

from typing import Dict, List, Any, Optional


class VizConfigGenerator:
    """
    Generates Recharts-compatible JSON configuration from visualization goals.
    """

    # DaVinci Design System Colors
    COLORS = {
        'primary': '#3b82f6',      # Blue
        'secondary': '#f97316',    # Orange
        'success': '#22c55e',      # Green
        'warning': '#f59e0b',      # Amber
        'danger': '#ef4444',       # Red
        'purple': '#a855f7',       # Purple
        'cyan': '#06b6d4',         # Cyan
        'pink': '#ec4899',         # Pink
        'palette': [
            '#3b82f6', '#f97316', '#22c55e', '#a855f7',
            '#f59e0b', '#ef4444', '#06b6d4', '#ec4899'
        ]
    }

    def generate(self, goal: Dict, results: List[Dict]) -> Dict:
        """
        Generate chart configuration from goal and data.

        Args:
            goal: Visualization goal with chart_type, axes, title
            results: SQL query results

        Returns:
            Recharts-compatible config dict
        """
        chart_type = goal.get("chart_type", "table")

        generators = {
            "progress_bar": self._generate_progress_bar_config,
            "kpi_card": self._generate_kpi_card_config,
            "line": self._generate_line_config,
            "area": self._generate_area_config,
            "bar": self._generate_bar_config,
            "pie": self._generate_pie_config,
            "metric_grid": self._generate_metric_grid_config,
            "table": self._generate_table_config
        }

        generator = generators.get(chart_type, self._generate_table_config)
        config = generator(goal, results)
        config['generated'] = True

        return config

    def _generate_line_config(self, goal: Dict, results: List[Dict]) -> Dict:
        """Generate line chart config."""
        x_key = goal.get("x_axis") or self._find_x_axis(results)
        y_key = goal.get("y_axis") or self._find_y_axis(results)

        # Fallback to table if we can't find required keys
        if not x_key or not y_key:
            return self._generate_table_config(goal, results)

        return {
            "type": "line",
            "data": results,
            "options": {
                "xAxis": {"dataKey": x_key, "label": self._format_label(x_key)},
                "yAxis": {"domain": ["auto", "auto"]},
                "lines": [
                    {
                        "dataKey": y_key,
                        "stroke": self.COLORS['primary'],
                        "strokeWidth": 2,
                        "name": self._format_label(y_key)
                    }
                ],
                "tooltip": True,
                "legend": False,
                "title": goal.get("title", "Trend"),
                "animation": True,
                "grid": True
            }
        }

    def _generate_area_config(self, goal: Dict, results: List[Dict]) -> Dict:
        """Generate area chart config."""
        config = self._generate_line_config(goal, results)
        config["type"] = "area"
        config["options"]["fill"] = self.COLORS['primary']
        config["options"]["fillOpacity"] = 0.3
        return config

    def _generate_bar_config(self, goal: Dict, results: List[Dict]) -> Dict:
        """Generate bar chart config."""
        x_key = goal.get("x_axis") or self._find_categorical(results)
        y_key = goal.get("y_axis") or self._find_y_axis(results)

        # Fallback to table if we can't find required keys
        if not x_key or not y_key:
            return self._generate_table_config(goal, results)

        return {
            "type": "bar",
            "data": results,
            "options": {
                "xAxis": {"dataKey": x_key, "label": self._format_label(x_key)},
                "yAxis": {"domain": [0, "auto"]},
                "bars": [
                    {
                        "dataKey": y_key,
                        "fill": self.COLORS['primary'],
                        "name": self._format_label(y_key),
                        "radius": [4, 4, 0, 0]
                    }
                ],
                "tooltip": True,
                "legend": False,
                "title": goal.get("title", "Comparison"),
                "animation": True
            }
        }

    def _generate_pie_config(self, goal: Dict, results: List[Dict]) -> Dict:
        """Generate pie chart config."""
        name_key = goal.get("x_axis") or self._find_categorical(results)
        value_key = goal.get("y_axis") or self._find_y_axis(results)

        # Fallback to table if we can't find required keys
        if not name_key or not value_key:
            return self._generate_table_config(goal, results)

        return {
            "type": "pie",
            "data": results,
            "options": {
                "dataKey": value_key,
                "nameKey": name_key,
                "colors": self.COLORS['palette'],
                "innerRadius": 60,
                "outerRadius": 100,
                "tooltip": True,
                "legend": True,
                "title": goal.get("title", "Distribution"),
                "label": True
            }
        }

    def _generate_progress_bar_config(self, goal: Dict, results: List[Dict]) -> Dict:
        """Generate progress bar card config."""
        y_key = goal.get("y_axis") or self._find_y_axis(results)
        value = self._get_first_value(results, y_key)

        # Determine unit and max based on column name
        unit, max_val = self._detect_unit_and_max(y_key)

        return {
            "type": "progress_bar",
            "data": {"value": value, "max": max_val},
            "options": {
                "title": goal.get("title", self._format_label(y_key)),
                "unit": unit,
                "thresholds": {
                    "low": 50,    # < 50% = red
                    "medium": 80  # < 80% = amber, >= 80% = green
                }
            }
        }

    def _generate_kpi_card_config(self, goal: Dict, results: List[Dict]) -> Dict:
        """Generate KPI card config."""
        y_key = goal.get("y_axis") or self._find_y_axis(results)
        value = self._get_first_value(results, y_key)
        unit, _ = self._detect_unit_and_max(y_key)

        return {
            "type": "kpi_card",
            "data": {"value": value, "previous": None},
            "options": {
                "title": goal.get("title", self._format_label(y_key)),
                "unit": unit,
                "trend": None,
                "color": self.COLORS['primary']
            }
        }

    def _generate_metric_grid_config(self, goal: Dict, results: List[Dict]) -> Dict:
        """Generate metric grid config. Aggregates multiple rows if present."""
        metrics = []

        if results and len(results) > 0:
            # If single row, use values directly
            if len(results) == 1:
                row = results[0]
                for key, value in row.items():
                    if isinstance(value, (int, float)):
                        unit, _ = self._detect_unit_and_max(key)
                        metrics.append({
                            "label": self._format_label(key),
                            "value": round(value, 2) if isinstance(value, float) else value,
                            "unit": unit
                        })
            else:
                # Multiple rows: calculate averages for numeric columns
                first_row = results[0]
                for key in first_row.keys():
                    values = [r.get(key) for r in results if isinstance(r.get(key), (int, float))]
                    if values:
                        avg_value = sum(values) / len(values)
                        unit, _ = self._detect_unit_and_max(key)
                        metrics.append({
                            "label": f"Avg {self._format_label(key)}",
                            "value": round(avg_value, 2),
                            "unit": unit,
                            "count": len(values)  # Include count for context
                        })

        return {
            "type": "metric_grid",
            "data": metrics,
            "options": {
                "title": goal.get("title", "Metrics Overview"),
                "columns": min(len(metrics), 4)
            }
        }

    def _generate_table_config(self, goal: Dict, results: List[Dict]) -> Dict:
        """Generate table config (fallback)."""
        return {
            "type": "table",
            "data": results,
            "options": {
                "title": goal.get("title", "Results")
            }
        }

    # Helper methods

    def _find_x_axis(self, results: List[Dict]) -> Optional[str]:
        """Find best column for X axis (temporal or first column)."""
        if not results:
            return None

        columns = list(results[0].keys())
        temporal_patterns = ['date', 'time', 'timestamp', 'day', 'month', 'year', 'week', 'created']

        # Look for temporal columns first
        for col in columns:
            if any(p in col.lower() for p in temporal_patterns):
                return col

        # Return first column
        return columns[0] if columns else None

    def _find_y_axis(self, results: List[Dict]) -> Optional[str]:
        """Find best column for Y axis (numeric)."""
        if not results:
            return None

        for key, value in results[0].items():
            if isinstance(value, (int, float)):
                return key

        # Return last column as fallback
        columns = list(results[0].keys())
        return columns[-1] if columns else None

    def _find_categorical(self, results: List[Dict]) -> Optional[str]:
        """Find best categorical column."""
        if not results:
            return None

        for key, value in results[0].items():
            if isinstance(value, str):
                return key

        return list(results[0].keys())[0] if results[0] else None

    def _get_first_value(self, results: List[Dict], key: Optional[str]) -> Any:
        """Get first value for a key."""
        if not results or not key:
            return 0

        value = results[0].get(key, 0)
        if isinstance(value, float):
            return round(value, 2)
        return value

    def _format_label(self, column_name: Optional[str]) -> str:
        """Format column name into human-readable label."""
        if not column_name:
            return "Value"

        # Replace underscores with spaces and title case
        label = column_name.replace('_', ' ').title()

        # Handle common abbreviations
        replacements = {
            'Oee': 'OEE',
            'Mtbf': 'MTBF',
            'Mttr': 'MTTR',
            'Kwh': 'kWh',
            'Id': 'ID',
            'No': 'No.',
            'Avg': 'Average'
        }

        for old, new in replacements.items():
            label = label.replace(old, new)

        return label

    def _detect_unit_and_max(self, column_name: Optional[str]) -> tuple:
        """Detect unit and max value based on column name."""
        if not column_name:
            return '', 100

        col = column_name.lower()

        # Percentage metrics
        if any(p in col for p in ['percentage', 'percent', 'oee', 'yield', 'rate', 'efficiency']):
            return '%', 100

        # Time metrics
        if any(p in col for p in ['hour', 'hrs', 'time', 'mtbf', 'mttr', 'duration']):
            return 'hrs', 24

        # Energy metrics
        if any(p in col for p in ['kwh', 'energy', 'power', 'watt']):
            return 'kWh', 10000

        # Weight metrics
        if any(p in col for p in ['kg', 'weight', 'mass', 'ton']):
            return 'kg', 1000

        # Temperature metrics
        if any(p in col for p in ['temperature', 'temp', 'celsius', 'fahrenheit']):
            return 'C', 2000

        # Count metrics
        if any(p in col for p in ['count', 'number', 'qty', 'quantity']):
            return '', 1000

        # Default
        return '', 100
