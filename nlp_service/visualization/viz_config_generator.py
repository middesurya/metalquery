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

    # Identifier columns that should not have units
    IDENTIFIER_PATTERNS = ['furnace_no', 'machine_id', 'plant_id', 'shift_id', 'workshop', 'equipment']

    def _generate_kpi_card_config(self, goal: Dict, results: List[Dict]) -> Dict:
        """Generate KPI card config."""
        if not results or not results[0]:
            return self._generate_table_config(goal, results)

        # For "which X" questions with identifier + metric columns,
        # show the identifier as main value and metric as subtitle
        columns = list(results[0].keys())
        identifier_col = None
        metric_col = None

        # Find identifier and metric columns
        for col in columns:
            if any(p in col.lower() for p in self.IDENTIFIER_PATTERNS):
                identifier_col = col
            elif isinstance(results[0].get(col), (int, float)):
                if not identifier_col or col != identifier_col:
                    metric_col = col

        # If we have both identifier and metric, format appropriately
        if identifier_col and metric_col:
            identifier_value = results[0].get(identifier_col)
            metric_value = results[0].get(metric_col)
            metric_unit, _ = self._detect_unit_and_max(metric_col)

            # Format identifier label (e.g., "Furnace 1" instead of just "1")
            id_label = self._format_identifier(identifier_col, identifier_value)

            return {
                "type": "kpi_card",
                "data": {
                    "value": id_label,
                    "subtitle": f"{round(metric_value, 2) if isinstance(metric_value, float) else metric_value} {metric_unit}".strip(),
                    "previous": None
                },
                "options": {
                    "title": goal.get("title", self._format_label(metric_col)),
                    "unit": "",  # No unit for identifier
                    "trend": None,
                    "color": self.COLORS['primary']
                }
            }

        # Default: use metric column
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

    def _format_identifier(self, col_name: str, value: Any) -> str:
        """Format identifier value with label (e.g., 'Furnace 1')."""
        if 'furnace' in col_name.lower():
            return f"Furnace {value}"
        if 'machine' in col_name.lower():
            return f"Machine {value}"
        if 'plant' in col_name.lower():
            return f"Plant {value}"
        if 'shift' in col_name.lower():
            return f"Shift {value}"
        if 'workshop' in col_name.lower():
            return f"Workshop {value}"
        return str(value)

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

    # Column type patterns
    TEMPORAL_PATTERNS = ['date', 'time', 'timestamp', 'day', 'month', 'year', 'week', 'created']

    # Label abbreviation corrections
    LABEL_REPLACEMENTS = {
        'Oee': 'OEE', 'Mtbf': 'MTBF', 'Mttr': 'MTTR',
        'Kwh': 'kWh', 'Id': 'ID', 'No': 'No.', 'Avg': 'Average'
    }

    # Unit detection: (patterns, unit, max_value)
    UNIT_RULES = [
        (['percentage', 'percent', 'oee', 'yield', 'rate', 'efficiency'], '%', 100),
        (['hour', 'hrs', 'time', 'mtbf', 'mttr', 'duration'], 'hrs', 24),
        (['kwh', 'energy', 'power', 'watt'], 'kWh', 10000),
        (['kg', 'weight', 'mass', 'ton'], 'kg', 1000),
        (['temperature', 'temp', 'celsius', 'fahrenheit'], 'C', 2000),
        (['count', 'number', 'qty', 'quantity'], '', 1000),
    ]

    def _find_column(self, results: List[Dict], predicate) -> Optional[str]:
        """Find first column matching a predicate function."""
        if not results or not results[0]:
            return None
        for key, value in results[0].items():
            if predicate(key, value):
                return key
        return None

    def _find_x_axis(self, results: List[Dict]) -> Optional[str]:
        """Find best column for X axis (temporal or first column)."""
        if not results:
            return None
        temporal = self._find_column(
            results,
            lambda k, v: any(p in k.lower() for p in self.TEMPORAL_PATTERNS)
        )
        if temporal:
            return temporal
        return list(results[0].keys())[0] if results[0] else None

    def _find_y_axis(self, results: List[Dict]) -> Optional[str]:
        """Find best column for Y axis (numeric)."""
        numeric = self._find_column(results, lambda k, v: isinstance(v, (int, float)))
        if numeric:
            return numeric
        columns = list(results[0].keys()) if results and results[0] else []
        return columns[-1] if columns else None

    def _find_categorical(self, results: List[Dict]) -> Optional[str]:
        """Find best categorical column."""
        categorical = self._find_column(results, lambda k, v: isinstance(v, str))
        if categorical:
            return categorical
        return list(results[0].keys())[0] if results and results[0] else None

    def _get_first_value(self, results: List[Dict], key: Optional[str]) -> Any:
        """Get first value for a key."""
        if not results or not key:
            return 0
        value = results[0].get(key, 0)
        return round(value, 2) if isinstance(value, float) else value

    def _format_label(self, column_name: Optional[str]) -> str:
        """Format column name into human-readable label."""
        if not column_name:
            return "Value"
        label = column_name.replace('_', ' ').title()
        for old, new in self.LABEL_REPLACEMENTS.items():
            label = label.replace(old, new)
        return label

    def _detect_unit_and_max(self, column_name: Optional[str]) -> tuple:
        """Detect unit and max value based on column name."""
        if not column_name:
            return '', 100
        col = column_name.lower()
        for patterns, unit, max_val in self.UNIT_RULES:
            if any(p in col for p in patterns):
                return unit, max_val
        return '', 100
