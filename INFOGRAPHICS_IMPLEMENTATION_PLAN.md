# Infographics Implementation Plan for MetalQuery AI Chatbot

> **Version**: 1.0.0
> **Date**: January 2026
> **Status**: Proposed
> **Author**: AI Architecture Analysis

## Executive Summary

This document outlines a comprehensive plan for implementing AI-powered infographics and data visualization capabilities in the MetalQuery AI chatbot. The approach is inspired by Microsoft's LIDA framework and incorporates 2025-2026 best practices for LLM-driven visualization generation.

---

## Table of Contents

1. [Current Architecture Analysis](#current-architecture-analysis)
2. [Proposed Architecture](#proposed-architecture)
3. [Technology Stack](#technology-stack)
4. [Implementation Phases](#implementation-phases)
5. [Component Specifications](#component-specifications)
6. [Security Considerations](#security-considerations)
7. [File Structure](#file-structure)
8. [References](#references)

---

## Current Architecture Analysis

### Existing System Overview

```
┌─────────────────────┐
│  React Frontend     │ ← No charting library
│  - ResultsTable     │ ← Raw tabular data only
│  - ImageGallery     │ ← BRD images only
└─────────────────────┘
         │
┌─────────────────────┐
│  Django Backend     │ ← Returns raw results[]
│  - chat()           │
└─────────────────────┘
         │
┌─────────────────────┐
│  NLP Service        │ ← No visualization logic
│  - generate_sql()   │
│  - format_response()│
└─────────────────────┘
```

### Current Response Structure

```json
{
  "success": true,
  "query_type": "sql",
  "response": "The OEE for furnace 1 is 92.5%",
  "sql": "SELECT AVG(oee_percentage) FROM ...",
  "results": [{"furnace_no": 1, "oee_percentage": 92.5}],
  "confidence_score": 95,
  "relevance_score": 92
}
```

### Identified Integration Points

| Component | File | Integration Point |
|-----------|------|-------------------|
| Frontend Chat | `frontend/src/App.jsx` | `ChatMessage` component |
| Django API | `backend/chatbot/views.py` | `chat()` view response |
| NLP Service | `nlp_service/main.py` | `hybrid_chat()` endpoint |

---

## Proposed Architecture

### LIDA-Inspired Visualization Pipeline

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           REACT FRONTEND (Port 5173)                        │
├────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────────┐   ┌─────────────────────────────┐  │
│  │ChatMessage  │   │ ChartRenderer   │   │  InfographicCard            │  │
│  │  - text     │   │  - Recharts     │   │  - KPI Gauge                │  │
│  │  - results  │   │  - Line/Bar/Pie │   │  - Metric Cards             │  │
│  │  - chart*   │   │  - Interactive  │   │  - Trend Indicators         │  │
│  └─────────────┘   └─────────────────┘   └─────────────────────────────┘  │
│         │                   ↑                          ↑                   │
│         └───────────────────┴──────────────────────────┘                   │
│                             │                                              │
│                    chart_config JSON (validated)                           │
└────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ POST /api/chatbot/chat/
                              ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        DJANGO BACKEND (Port 8000)                           │
├────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  chat() view - Enhanced Response                                      │  │
│  │                                                                       │  │
│  │  {                                                                    │  │
│  │    "success": true,                                                   │  │
│  │    "query_type": "sql",                                               │  │
│  │    "response": "The OEE for Furnace 1 is 92.5%",                      │  │
│  │    "sql": "SELECT ...",                                               │  │
│  │    "results": [...],                                                  │  │
│  │    "chart_config": {                    // ← NEW                      │  │
│  │      "type": "gauge",                                                 │  │
│  │      "data": [...],                                                   │  │
│  │      "options": {...}                                                 │  │
│  │    },                                                                 │  │
│  │    "infographic": {                     // ← NEW                      │  │
│  │      "template": "kpi_card",                                          │  │
│  │      "metrics": [...]                                                 │  │
│  │    }                                                                  │  │
│  │  }                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ POST /api/v1/chat
                              ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                       NLP SERVICE (Port 8004)                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    VISUALIZATION PIPELINE                            │   │
│  │                    (LIDA-Inspired, Groq-Powered)                      │   │
│  │                                                                       │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │   │
│  │  │ 1. DATA      │ -> │ 2. GOAL      │ -> │ 3. CONFIG            │   │   │
│  │  │ SUMMARIZER   │    │ FINDER       │    │ GENERATOR            │   │   │
│  │  │              │    │              │    │                      │   │   │
│  │  │ Input:       │    │ Determines:  │    │ Outputs:             │   │   │
│  │  │ - SQL results│    │ - Chart type │    │ - Recharts config    │   │   │
│  │  │ - Question   │    │ - Viz goal   │    │ - Validated JSON     │   │   │
│  │  │ - Schema     │    │ - Metrics    │    │ - Infographic spec   │   │   │
│  │  └──────────────┘    └──────────────┘    └──────────────────────┘   │   │
│  │          │                   │                      │                │   │
│  │          └───────────────────┴──────────────────────┘                │   │
│  │                              │                                        │   │
│  │                    ┌─────────▼─────────┐                             │   │
│  │                    │ 4. VIZ VALIDATOR  │                             │   │
│  │                    │ - Schema check    │                             │   │
│  │                    │ - Security scan   │                             │   │
│  │                    │ - Size limits     │                             │   │
│  │                    └───────────────────┘                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend Charting Library: Recharts

**Selection Rationale:**

| Criteria | Recharts | Chart.js | Plotly | D3.js |
|----------|----------|----------|--------|-------|
| React Integration | Native | Wrapper | Wrapper | Manual |
| Learning Curve | Low | Low | Medium | High |
| Customization | High | Medium | High | Very High |
| Bundle Size | Medium | Small | Large | Large |
| Declarative API | Yes | No | Partial | No |

**Decision: Recharts** - Best balance of React integration, ease of use, and customization for manufacturing dashboards.

### Installation

```bash
cd frontend
npm install recharts
```

---

## Implementation Phases

### Phase 1: Frontend Charting Infrastructure

**Scope:** Install Recharts and create base chart components.

**New Components:**

```
frontend/src/components/
├── charts/
│   ├── ChartRenderer.jsx       # Main chart dispatcher
│   ├── LineChartView.jsx       # Time series (OEE trends)
│   ├── BarChartView.jsx        # Comparisons (furnace vs furnace)
│   ├── PieChartView.jsx        # Distributions (defect breakdown)
│   ├── GaugeChart.jsx          # Single KPI values (current OEE)
│   ├── AreaChartView.jsx       # Cumulative metrics
│   └── ScatterPlotView.jsx     # Correlations
│
└── infographics/
    ├── KPICard.jsx             # Single metric card with trend
    ├── MetricGrid.jsx          # Multi-metric dashboard
    ├── TrendIndicator.jsx      # Up/down/stable arrows
    └── ComparisonCard.jsx      # Before/after comparisons
```

**ChartRenderer Component:**

```jsx
// frontend/src/components/charts/ChartRenderer.jsx
import React from 'react';
import { ResponsiveContainer } from 'recharts';
import LineChartView from './LineChartView';
import BarChartView from './BarChartView';
import PieChartView from './PieChartView';
import GaugeChart from './GaugeChart';
import AreaChartView from './AreaChartView';
import KPICard from '../infographics/KPICard';
import MetricGrid from '../infographics/MetricGrid';

const ChartRenderer = ({ config, data }) => {
  if (!config || !data || data.length === 0) return null;

  const chartTypes = {
    'line': LineChartView,
    'bar': BarChartView,
    'pie': PieChartView,
    'gauge': GaugeChart,
    'area': AreaChartView,
    'kpi_card': KPICard,
    'metric_grid': MetricGrid
  };

  const ChartComponent = chartTypes[config.type];
  if (!ChartComponent) return null;

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        <ChartComponent config={config} data={data} />
      </ResponsiveContainer>
    </div>
  );
};

export default ChartRenderer;
```

---

### Phase 2: NLP Visualization Service

**Scope:** Create LIDA-inspired visualization pipeline in NLP service.

**New Module Structure:**

```
nlp_service/visualization/
├── __init__.py
├── viz_summarizer.py       # Summarize data characteristics
├── viz_goal_finder.py      # LLM-powered chart type selection
├── viz_config_generator.py # Generate Recharts JSON config
├── viz_templates.py        # KPI-specific templates
├── viz_validator.py        # Validate & sanitize configs
└── viz_constants.py        # Chart type definitions
```

**Data Summarizer:**

```python
# nlp_service/visualization/viz_summarizer.py
from typing import List, Dict, Any
import re

class DataSummarizer:
    """
    Summarizes SQL results into a compact representation
    for LLM chart type selection.
    """

    TEMPORAL_PATTERNS = ['date', 'time', 'timestamp', 'created', 'updated', 'day', 'month', 'year']

    def summarize(self, results: List[Dict], question: str) -> Dict:
        if not results:
            return {"shape": "empty", "row_count": 0, "summary": "No data"}

        columns = list(results[0].keys()) if results else []

        # Analyze column types
        numeric_cols = []
        categorical_cols = []
        temporal_cols = []

        for col in columns:
            sample_values = [r.get(col) for r in results[:10] if r.get(col) is not None]

            if any(pattern in col.lower() for pattern in self.TEMPORAL_PATTERNS):
                temporal_cols.append(col)
            elif sample_values and all(isinstance(v, (int, float)) for v in sample_values):
                numeric_cols.append(col)
            else:
                categorical_cols.append(col)

        return {
            "row_count": len(results),
            "column_count": len(columns),
            "columns": columns,
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "temporal_columns": temporal_cols,
            "has_time_series": len(temporal_cols) > 0,
            "is_single_value": len(results) == 1 and len(numeric_cols) == 1,
            "is_comparison": len(categorical_cols) > 0 and len(numeric_cols) > 0,
            "aggregation_detected": self._detect_aggregation(question),
            "comparison_detected": self._detect_comparison(question),
            "sample_values": results[:3]
        }

    def _detect_aggregation(self, question: str) -> str:
        q = question.lower()
        if any(w in q for w in ['average', 'avg', 'mean']):
            return 'AVG'
        if any(w in q for w in ['total', 'sum']):
            return 'SUM'
        if any(w in q for w in ['count', 'how many']):
            return 'COUNT'
        if any(w in q for w in ['maximum', 'max', 'highest']):
            return 'MAX'
        if any(w in q for w in ['minimum', 'min', 'lowest']):
            return 'MIN'
        return None

    def _detect_comparison(self, question: str) -> bool:
        q = question.lower()
        return any(w in q for w in ['compare', 'versus', 'vs', 'between', 'difference'])
```

**LLM-Powered Goal Finder:**

```python
# nlp_service/visualization/viz_goal_finder.py
import json
import logging
from typing import Dict, Tuple
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

class VizGoalFinder:
    """
    Uses Groq LLM to determine the best visualization type
    based on data summary and user question.
    """

    CHART_SELECTION_PROMPT = """You are a data visualization expert for manufacturing analytics.

Given the following data summary and user question, determine the best chart type.

DATA SUMMARY:
{data_summary}

USER QUESTION: "{question}"

AVAILABLE CHART TYPES:
- "gauge": Single KPI value with target indicator (e.g., "What is current OEE?")
- "line": Time series trends with points (e.g., "Show OEE trend over time")
- "bar": Comparisons across categories (e.g., "Compare OEE by furnace")
- "pie": Composition/distribution as percentages (e.g., "Breakdown of defect types")
- "area": Cumulative or filled time series (e.g., "Cumulative production")
- "kpi_card": Single metric with trend indicator and context
- "metric_grid": Multiple related metrics displayed together
- "table": Raw data display (use for complex multi-column queries)

SELECTION RULES:
1. Single numeric value → "gauge" or "kpi_card"
2. Time series data → "line" or "area"
3. Category comparison → "bar"
4. Percentage breakdown → "pie"
5. Multiple KPIs → "metric_grid"
6. Complex data → "table"

Respond with JSON only (no markdown):
{{
  "chart_type": "<type>",
  "x_axis": "<column_name or null>",
  "y_axis": "<column_name or null>",
  "group_by": "<column_name or null>",
  "title": "<descriptive chart title>",
  "reasoning": "<one sentence explanation>"
}}"""

    async def find_goal(self, data_summary: Dict, question: str, llm) -> Dict:
        prompt = self.CHART_SELECTION_PROMPT.format(
            data_summary=json.dumps(data_summary, indent=2),
            question=question
        )

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            return self._parse_response(response.content)
        except Exception as e:
            logger.error(f"VizGoalFinder error: {e}")
            return self._fallback_goal(data_summary)

    def _parse_response(self, content: str) -> Dict:
        """Parse LLM JSON response."""
        try:
            # Remove markdown code blocks if present
            content = content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]

            return json.loads(content)
        except json.JSONDecodeError:
            return self._fallback_goal({})

    def _fallback_goal(self, data_summary: Dict) -> Dict:
        """Fallback when LLM fails."""
        if data_summary.get('is_single_value'):
            return {"chart_type": "kpi_card", "title": "Result"}
        if data_summary.get('has_time_series'):
            return {"chart_type": "line", "title": "Trend"}
        if data_summary.get('is_comparison'):
            return {"chart_type": "bar", "title": "Comparison"}
        return {"chart_type": "table", "title": "Results"}
```

**Config Generator:**

```python
# nlp_service/visualization/viz_config_generator.py
from typing import Dict, List, Any

class VizConfigGenerator:
    """
    Generates Recharts-compatible JSON configuration.
    """

    # DaVinci Design System Colors
    COLORS = {
        'primary': '#3b82f6',
        'secondary': '#f97316',
        'success': '#22c55e',
        'warning': '#f59e0b',
        'danger': '#ef4444',
        'purple': '#a855f7',
        'palette': ['#3b82f6', '#f97316', '#22c55e', '#a855f7', '#f59e0b', '#ef4444']
    }

    def generate(self, goal: Dict, results: List[Dict]) -> Dict:
        chart_type = goal.get("chart_type", "table")

        generators = {
            "gauge": self._generate_gauge_config,
            "line": self._generate_line_config,
            "bar": self._generate_bar_config,
            "pie": self._generate_pie_config,
            "area": self._generate_area_config,
            "kpi_card": self._generate_kpi_card_config,
            "metric_grid": self._generate_metric_grid_config,
            "table": self._generate_table_config
        }

        generator = generators.get(chart_type, self._generate_table_config)
        config = generator(goal, results)
        config['generated'] = True
        return config

    def _generate_line_config(self, goal: Dict, results: List[Dict]) -> Dict:
        x_key = goal.get("x_axis") or self._find_x_axis(results)
        y_key = goal.get("y_axis") or self._find_y_axis(results)

        return {
            "type": "line",
            "data": results,
            "options": {
                "xAxis": {"dataKey": x_key, "label": x_key},
                "yAxis": {"domain": ["auto", "auto"]},
                "lines": [
                    {
                        "dataKey": y_key,
                        "stroke": self.COLORS['primary'],
                        "strokeWidth": 2,
                        "dot": {"r": 4},
                        "activeDot": {"r": 6}
                    }
                ],
                "tooltip": True,
                "legend": False,
                "title": goal.get("title", "Trend"),
                "animation": True,
                "grid": True
            }
        }

    def _generate_bar_config(self, goal: Dict, results: List[Dict]) -> Dict:
        x_key = goal.get("x_axis") or self._find_categorical(results)
        y_key = goal.get("y_axis") or self._find_y_axis(results)

        return {
            "type": "bar",
            "data": results,
            "options": {
                "xAxis": {"dataKey": x_key},
                "yAxis": {"domain": [0, "auto"]},
                "bars": [
                    {
                        "dataKey": y_key,
                        "fill": self.COLORS['primary'],
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
        name_key = self._find_categorical(results)
        value_key = self._find_y_axis(results)

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

    def _generate_gauge_config(self, goal: Dict, results: List[Dict]) -> Dict:
        y_key = goal.get("y_axis") or self._find_y_axis(results)
        value = results[0].get(y_key, 0) if results else 0

        # Determine unit and max based on column name
        unit, max_val = self._detect_unit_and_max(y_key)

        return {
            "type": "gauge",
            "data": {"value": value, "max": max_val},
            "options": {
                "title": goal.get("title", y_key),
                "unit": unit,
                "thresholds": {
                    "low": {"value": max_val * 0.5, "color": self.COLORS['danger']},
                    "medium": {"value": max_val * 0.8, "color": self.COLORS['warning']},
                    "high": {"value": max_val, "color": self.COLORS['success']}
                },
                "animation": True
            }
        }

    def _generate_kpi_card_config(self, goal: Dict, results: List[Dict]) -> Dict:
        y_key = goal.get("y_axis") or self._find_y_axis(results)
        value = results[0].get(y_key, 0) if results else 0
        unit, _ = self._detect_unit_and_max(y_key)

        return {
            "type": "kpi_card",
            "data": {"value": value, "previous": None},
            "options": {
                "title": goal.get("title", y_key),
                "unit": unit,
                "trend": None,
                "color": self.COLORS['primary']
            }
        }

    def _generate_area_config(self, goal: Dict, results: List[Dict]) -> Dict:
        config = self._generate_line_config(goal, results)
        config["type"] = "area"
        config["options"]["fill"] = self.COLORS['primary']
        config["options"]["fillOpacity"] = 0.3
        return config

    def _generate_metric_grid_config(self, goal: Dict, results: List[Dict]) -> Dict:
        metrics = []
        if results:
            for key, value in results[0].items():
                if isinstance(value, (int, float)):
                    unit, _ = self._detect_unit_and_max(key)
                    metrics.append({
                        "label": key.replace('_', ' ').title(),
                        "value": value,
                        "unit": unit
                    })

        return {
            "type": "metric_grid",
            "data": metrics,
            "options": {
                "title": goal.get("title", "Metrics"),
                "columns": min(len(metrics), 4)
            }
        }

    def _generate_table_config(self, goal: Dict, results: List[Dict]) -> Dict:
        return {
            "type": "table",
            "data": results,
            "options": {
                "title": goal.get("title", "Results")
            }
        }

    def _find_x_axis(self, results: List[Dict]) -> str:
        if not results:
            return None
        temporal = ['date', 'time', 'timestamp', 'day', 'month', 'year', 'created']
        for key in results[0].keys():
            if any(t in key.lower() for t in temporal):
                return key
        return list(results[0].keys())[0]

    def _find_y_axis(self, results: List[Dict]) -> str:
        if not results:
            return None
        for key, value in results[0].items():
            if isinstance(value, (int, float)):
                return key
        return list(results[0].keys())[-1]

    def _find_categorical(self, results: List[Dict]) -> str:
        if not results:
            return None
        for key, value in results[0].items():
            if isinstance(value, str):
                return key
        return list(results[0].keys())[0]

    def _detect_unit_and_max(self, column_name: str) -> tuple:
        col = column_name.lower()
        if 'percentage' in col or 'oee' in col or 'yield' in col or 'rate' in col:
            return '%', 100
        if 'hour' in col or 'time' in col:
            return 'hrs', 24
        if 'kwh' in col or 'energy' in col:
            return 'kWh', 10000
        if 'kg' in col or 'weight' in col:
            return 'kg', 1000
        if 'temperature' in col or 'temp' in col:
            return '°C', 2000
        return '', 100
```

**KPI Templates:**

```python
# nlp_service/visualization/viz_templates.py

KPI_TEMPLATES = {
    "oee": {
        "chart_type": "gauge",
        "title": "Overall Equipment Effectiveness",
        "unit": "%",
        "max": 100,
        "thresholds": {"low": 65, "medium": 85, "high": 100},
        "colors": {"low": "#ef4444", "medium": "#f59e0b", "high": "#22c55e"}
    },
    "downtime": {
        "chart_type": "bar",
        "title": "Downtime Analysis",
        "unit": "hours",
        "colors": ["#ef4444", "#f97316", "#eab308", "#22c55e"]
    },
    "yield": {
        "chart_type": "area",
        "title": "Production Yield",
        "unit": "%",
        "fill": "#3b82f6",
        "gradient": True
    },
    "mtbf": {
        "chart_type": "kpi_card",
        "title": "Mean Time Between Failures",
        "unit": "hours"
    },
    "mttr": {
        "chart_type": "kpi_card",
        "title": "Mean Time To Repair",
        "unit": "hours"
    },
    "energy": {
        "chart_type": "line",
        "title": "Energy Consumption",
        "unit": "kWh"
    },
    "defect_rate": {
        "chart_type": "pie",
        "title": "Defect Distribution",
        "unit": "%"
    },
    "production": {
        "chart_type": "bar",
        "title": "Production Output",
        "unit": "units"
    },
    "cycle_time": {
        "chart_type": "line",
        "title": "Cycle Time Trend",
        "unit": "minutes"
    }
}

def get_template_for_query(question: str, columns: list) -> dict:
    """Match query to best KPI template."""
    q = question.lower()

    # Direct matches
    for kpi, template in KPI_TEMPLATES.items():
        if kpi.replace('_', ' ') in q or kpi in q:
            return template

    # Column-based matching
    for col in columns:
        col_lower = col.lower()
        for kpi, template in KPI_TEMPLATES.items():
            if kpi in col_lower:
                return template

    return None
```

**Config Validator:**

```python
# nlp_service/visualization/viz_validator.py
from typing import Dict, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class VizConfigValidator:
    """
    Validates chart configurations for security and correctness.
    """

    ALLOWED_CHART_TYPES = {
        "line", "bar", "pie", "gauge", "area",
        "scatter", "kpi_card", "metric_grid", "table"
    }

    MAX_DATA_POINTS = 1000
    MAX_SERIES = 10
    MAX_STRING_LENGTH = 500

    DANGEROUS_PATTERNS = [
        "javascript:", "onclick", "onerror", "onload", "onmouseover",
        "<script", "</script>", "eval(", "Function(",
        "__proto__", "constructor", "prototype",
        "document.", "window.", "alert(", "confirm(",
        "innerHTML", "outerHTML"
    ]

    def validate(self, config: Dict) -> Tuple[bool, str]:
        """Validate chart configuration."""
        if not config:
            return False, "Empty config"

        # Check chart type
        chart_type = config.get("type")
        if chart_type not in self.ALLOWED_CHART_TYPES:
            return False, f"Invalid chart type: {chart_type}"

        # Check data size
        data = config.get("data", [])
        if isinstance(data, list) and len(data) > self.MAX_DATA_POINTS:
            return False, f"Too many data points: {len(data)} (max: {self.MAX_DATA_POINTS})"

        # Check for code injection
        if self._contains_dangerous_patterns(config):
            logger.warning(f"Dangerous pattern detected in chart config")
            return False, "Invalid content detected in config"

        # Check string lengths
        if not self._check_string_lengths(config):
            return False, "String value too long"

        return True, "Valid"

    def _contains_dangerous_patterns(self, obj: Any, depth: int = 0) -> bool:
        """Recursively check for dangerous patterns."""
        if depth > 10:  # Prevent infinite recursion
            return False

        if isinstance(obj, str):
            obj_lower = obj.lower()
            return any(p.lower() in obj_lower for p in self.DANGEROUS_PATTERNS)
        elif isinstance(obj, dict):
            return any(
                self._contains_dangerous_patterns(k, depth + 1) or
                self._contains_dangerous_patterns(v, depth + 1)
                for k, v in obj.items()
            )
        elif isinstance(obj, list):
            return any(self._contains_dangerous_patterns(v, depth + 1) for v in obj)
        return False

    def _check_string_lengths(self, obj: Any, depth: int = 0) -> bool:
        """Check all strings are within length limits."""
        if depth > 10:
            return True

        if isinstance(obj, str):
            return len(obj) <= self.MAX_STRING_LENGTH
        elif isinstance(obj, dict):
            return all(
                self._check_string_lengths(v, depth + 1)
                for v in obj.values()
            )
        elif isinstance(obj, list):
            return all(self._check_string_lengths(v, depth + 1) for v in obj)
        return True

    def sanitize(self, config: Dict) -> Dict:
        """Sanitize config by removing dangerous content."""
        if not config:
            return config

        return self._sanitize_recursive(config)

    def _sanitize_recursive(self, obj: Any, depth: int = 0) -> Any:
        if depth > 10:
            return obj

        if isinstance(obj, str):
            # Remove dangerous patterns
            sanitized = obj
            for pattern in self.DANGEROUS_PATTERNS:
                sanitized = sanitized.replace(pattern, '')
            # Truncate if too long
            return sanitized[:self.MAX_STRING_LENGTH]
        elif isinstance(obj, dict):
            return {k: self._sanitize_recursive(v, depth + 1) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_recursive(v, depth + 1) for v in obj[:self.MAX_DATA_POINTS]]
        return obj
```

---

### Phase 3: Integration with Chat Flow

**NLP Service Modification:**

```python
# nlp_service/main.py - Add to imports
from visualization import VizPipeline

# Initialize pipeline
viz_pipeline = None

@app.on_event("startup")
async def startup_event():
    global viz_pipeline
    # ... existing startup code ...

    # Initialize visualization pipeline
    viz_pipeline = VizPipeline()
    logger.info("✓ Visualization pipeline initialized")

# Modify hybrid_chat endpoint
@app.post("/api/v1/chat")
async def hybrid_chat(request: HybridChatRequest):
    # ... existing code ...

    if query_type == "sql":
        sql_response = await generate_sql(sql_request)

        # NEW: Generate visualization config
        chart_config = None
        if sql_response.success and sql_response.sql:
            try:
                llm = get_llm(max_tokens=256)
                chart_config = await viz_pipeline.generate_config(
                    question=request.question,
                    sql=sql_response.sql,
                    llm=llm
                )
            except Exception as e:
                logger.warning(f"Viz config generation failed: {e}")

        return HybridChatResponse(
            success=sql_response.success,
            query_type="sql",
            sql=sql_response.sql,
            chart_config=chart_config,  # NEW FIELD
            # ... rest ...
        )
```

**Django Backend Modification:**

```python
# backend/chatbot/views.py - Modify response

def chat(request):
    # ... existing code ...

    # Get chart config from NLP response
    chart_config = nlp_data.get('chart_config')

    # Finalize config with actual results
    if chart_config and results:
        chart_config['data'] = results[:100]  # Limit data points

    return JsonResponse({
        'success': True,
        'query_type': 'sql',
        'response': natural_response,
        'sql': sql,
        'results': results[:50],
        'chart_config': chart_config,  # NEW
        'confidence_score': nlp_data.get('confidence_score'),
        'relevance_score': nlp_data.get('relevance_score')
    })
```

**Frontend Integration:**

```jsx
// frontend/src/App.jsx - Modify sendMessage and ChatMessage

const sendMessage = async (messageText) => {
  // ... existing code ...

  const botMessage = {
    text: data.response,
    isUser: false,
    sql: data.sql,
    results: data.results,
    chart_config: data.chart_config,  // NEW
    confidence_score: data.confidence_score,
    relevance_score: data.relevance_score
  };

  setMessages(prev => [...prev, botMessage]);
};

// In ChatMessage component
{message.chart_config && (
  <ChartRenderer
    config={message.chart_config}
    data={message.results}
  />
)}
```

---

### Phase 4: Styling (DaVinci Design System)

**Chart Styles:**

```css
/* frontend/src/App.css - Add chart styles */

/* Chart Container */
.chart-container {
    background: rgba(26, 39, 68, 0.5);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
}

.chart-container:hover {
    border-color: rgba(59, 130, 246, 0.3);
}

.chart-title {
    font-size: 14px;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Recharts Overrides */
.recharts-cartesian-grid-horizontal line,
.recharts-cartesian-grid-vertical line {
    stroke: rgba(255, 255, 255, 0.1);
}

.recharts-text {
    fill: #94a3b8;
    font-size: 12px;
}

.recharts-tooltip-wrapper {
    outline: none;
}

.recharts-default-tooltip {
    background: rgba(26, 39, 68, 0.95) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    padding: 12px !important;
}

.recharts-tooltip-label {
    color: #fff !important;
    font-weight: 600;
    margin-bottom: 8px;
}

.recharts-tooltip-item {
    color: #94a3b8 !important;
}

/* KPI Card */
.kpi-card {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.05));
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    border: 1px solid rgba(59, 130, 246, 0.2);
}

.kpi-value {
    font-size: 48px;
    font-weight: bold;
    color: #fff;
    line-height: 1;
}

.kpi-unit {
    font-size: 24px;
    color: #94a3b8;
    margin-left: 4px;
}

.kpi-label {
    font-size: 14px;
    color: #94a3b8;
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.kpi-trend {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-top: 12px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
}

.kpi-trend.up {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
}

.kpi-trend.down {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

.kpi-trend.stable {
    background: rgba(148, 163, 184, 0.2);
    color: #94a3b8;
}

/* Gauge Chart */
.gauge-chart {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
}

.gauge-value {
    font-size: 56px;
    font-weight: bold;
    color: #fff;
}

.gauge-label {
    font-size: 14px;
    color: #94a3b8;
    margin-top: 8px;
}

/* Metric Grid */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
}

.metric-item {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}

.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #fff;
}

.metric-label {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 4px;
}
```

---

### Phase 5: Advanced Features (Future)

**5.1 Chart Export:**

```jsx
import html2canvas from 'html2canvas';

const exportChart = async (elementId, filename) => {
    const element = document.getElementById(elementId);
    const canvas = await html2canvas(element);
    const link = document.createElement('a');
    link.download = `${filename}.png`;
    link.href = canvas.toDataURL();
    link.click();
};
```

**5.2 Interactive Drilldown:**

```jsx
const handleChartClick = (data, index) => {
    if (data && data.activePayload) {
        const clickedItem = data.activePayload[0].payload;
        // Trigger follow-up query
        sendMessage(`Show details for ${clickedItem.name}`);
    }
};
```

**5.3 Real-time Updates:**

```jsx
useEffect(() => {
    if (autoRefresh && lastQuery) {
        const interval = setInterval(() => {
            refreshData(lastQuery);
        }, refreshInterval);
        return () => clearInterval(interval);
    }
}, [autoRefresh, lastQuery]);
```

---

## Security Considerations

### 1. No Code Execution
- All chart configurations are JSON data structures
- No executable JavaScript in configs
- Recharts renders from data only

### 2. Input Validation
- Validate all chart configs before rendering
- Check for XSS patterns in titles/labels
- Limit data array sizes

### 3. Data Limits
- Max 1000 data points per chart
- Max 10 series per chart
- Max 500 characters per string

### 4. Sanitization
- Strip dangerous patterns from all strings
- Escape HTML entities
- Validate color values

---

## File Structure

```
metalquery/
├── frontend/
│   ├── package.json                    # + recharts
│   └── src/
│       ├── App.jsx                     # Modified
│       ├── App.css                     # + chart styles
│       └── components/
│           ├── charts/
│           │   ├── ChartRenderer.jsx   # NEW
│           │   ├── LineChartView.jsx   # NEW
│           │   ├── BarChartView.jsx    # NEW
│           │   ├── PieChartView.jsx    # NEW
│           │   ├── GaugeChart.jsx      # NEW
│           │   └── AreaChartView.jsx   # NEW
│           └── infographics/
│               ├── KPICard.jsx         # NEW
│               ├── MetricGrid.jsx      # NEW
│               └── TrendIndicator.jsx  # NEW
│
├── backend/
│   └── chatbot/
│       └── views.py                    # Modified
│
└── nlp_service/
    ├── main.py                         # Modified
    └── visualization/                  # NEW MODULE
        ├── __init__.py
        ├── viz_summarizer.py
        ├── viz_goal_finder.py
        ├── viz_config_generator.py
        ├── viz_templates.py
        └── viz_validator.py
```

---

## References

- [Microsoft LIDA](https://microsoft.github.io/lida/) - Automatic Visualization Generation
- [Recharts Documentation](https://recharts.org/) - React Charting Library
- [Charts-of-Thought](https://arxiv.org/html/2508.04842v1) - LLM Visualization Enhancement
- [LogRocket React Charts 2025](https://blog.logrocket.com/best-react-chart-libraries-2025/)
- [AI Visualization Best Practices 2025](https://ai2.work/technology/ai-tech-llm-visualization-2025/)

---

## Appendix: Chart Type Decision Matrix

| Query Pattern | Data Shape | Chart Type |
|---------------|------------|------------|
| "What is current OEE?" | Single value | Gauge |
| "Show OEE trend" | Time series | Line |
| "Compare by furnace" | Categories + values | Bar |
| "Breakdown of defects" | Categories + percentages | Pie |
| "Cumulative production" | Time series | Area |
| "Show MTBF and MTTR" | Multiple KPIs | Metric Grid |
| Complex multi-column | Any | Table |

---

*Document generated as part of MetalQuery AI Chatbot enhancement project.*
