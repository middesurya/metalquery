"""
KPI-Specific Visualization Templates for Manufacturing Metrics.
"""

from typing import Dict, List, Optional

# DaVinci Colors
COLORS = {
    'primary': '#3b82f6',
    'secondary': '#f97316',
    'success': '#22c55e',
    'warning': '#f59e0b',
    'danger': '#ef4444'
}

KPI_TEMPLATES = {
    "oee": {
        "chart_type": "gauge",
        "title": "Overall Equipment Effectiveness",
        "unit": "%",
        "max": 100,
        "thresholds": {
            "low": {"value": 50, "color": COLORS['danger']},
            "medium": {"value": 80, "color": COLORS['warning']},
            "high": {"value": 100, "color": COLORS['success']}
        }
    },
    "downtime": {
        "chart_type": "bar",
        "title": "Downtime Analysis",
        "unit": "hours",
        "colors": [COLORS['danger'], COLORS['warning'], COLORS['primary']]
    },
    "yield": {
        "chart_type": "gauge",
        "title": "Production Yield",
        "unit": "%",
        "max": 100,
        "thresholds": {
            "low": {"value": 70, "color": COLORS['danger']},
            "medium": {"value": 90, "color": COLORS['warning']},
            "high": {"value": 100, "color": COLORS['success']}
        }
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
    "defect": {
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
    },
    "efficiency": {
        "chart_type": "gauge",
        "title": "Efficiency",
        "unit": "%",
        "max": 100,
        "thresholds": {
            "low": {"value": 60, "color": COLORS['danger']},
            "medium": {"value": 85, "color": COLORS['warning']},
            "high": {"value": 100, "color": COLORS['success']}
        }
    },
    "availability": {
        "chart_type": "gauge",
        "title": "Availability",
        "unit": "%",
        "max": 100
    },
    "performance": {
        "chart_type": "gauge",
        "title": "Performance",
        "unit": "%",
        "max": 100
    },
    "quality": {
        "chart_type": "gauge",
        "title": "Quality Rate",
        "unit": "%",
        "max": 100
    },
    "temperature": {
        "chart_type": "line",
        "title": "Temperature",
        "unit": "C"
    },
    "output_rate": {
        "chart_type": "bar",
        "title": "Output Rate",
        "unit": "units/hr"
    }
}


def get_template_for_query(question: str, columns: List[str]) -> Optional[Dict]:
    """
    Match query to best KPI template based on question and column names.

    Args:
        question: User's question
        columns: Column names from result set

    Returns:
        Matching template or None
    """
    q = question.lower()
    cols_lower = [c.lower() for c in columns]

    # Direct question matches
    for kpi, template in KPI_TEMPLATES.items():
        kpi_words = kpi.replace('_', ' ')
        if kpi_words in q or kpi in q:
            return template.copy()

    # Column-based matching
    for col in cols_lower:
        for kpi, template in KPI_TEMPLATES.items():
            if kpi in col:
                return template.copy()

    # Keyword matching
    keyword_map = {
        'oee': ['oee', 'overall equipment', 'effectiveness'],
        'downtime': ['downtime', 'down time', 'stopped'],
        'yield': ['yield', 'output yield'],
        'mtbf': ['mtbf', 'mean time between', 'failures'],
        'mttr': ['mttr', 'mean time to repair', 'repair time'],
        'energy': ['energy', 'power', 'electricity', 'kwh'],
        'defect': ['defect', 'defects', 'reject', 'rejected'],
        'production': ['production', 'output', 'produced', 'manufactured'],
        'cycle_time': ['cycle time', 'cycle_time', 'takt'],
        'efficiency': ['efficiency', 'efficient'],
        'temperature': ['temperature', 'temp', 'heat']
    }

    for kpi, keywords in keyword_map.items():
        if any(kw in q for kw in keywords):
            return KPI_TEMPLATES.get(kpi, {}).copy()

    return None


def apply_template_to_config(config: Dict, template: Dict) -> Dict:
    """
    Apply template settings to an existing config.

    Args:
        config: Generated chart config
        template: KPI template

    Returns:
        Enhanced config with template settings
    """
    if not template:
        return config

    # Apply chart type if not already set
    if template.get('chart_type') and config.get('type') == 'table':
        config['type'] = template['chart_type']

    # Apply unit
    if template.get('unit') and config.get('options'):
        config['options']['unit'] = template['unit']

    # Apply thresholds for gauge
    if template.get('thresholds') and config.get('type') == 'gauge':
        config['options']['thresholds'] = template['thresholds']

    # Apply title if better
    if template.get('title'):
        if not config.get('options'):
            config['options'] = {}
        # Only override if current title is generic
        current_title = config.get('options', {}).get('title', '')
        if not current_title or current_title in ['Results', 'Value', 'Data']:
            config['options']['title'] = template['title']

    return config
