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
        "chart_type": "progress_bar",
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
        "chart_type": "progress_bar",
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
        "chart_type": "progress_bar",
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
        "chart_type": "progress_bar",
        "title": "Availability",
        "unit": "%",
        "max": 100
    },
    "performance": {
        "chart_type": "progress_bar",
        "title": "Performance",
        "unit": "%",
        "max": 100
    },
    "quality": {
        "chart_type": "progress_bar",
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
    Uses word boundary matching to avoid false positives.

    Args:
        question: User's question
        columns: Column names from result set

    Returns:
        Matching template or None
    """
    import re

    q = question.lower()
    cols_lower = [c.lower() for c in columns]

    # Direct question matches with word boundaries
    for kpi, template in KPI_TEMPLATES.items():
        kpi_words = kpi.replace('_', ' ')
        # Use word boundaries to avoid "yield" matching "output_yield"
        if re.search(rf'\b{re.escape(kpi_words)}\b', q) or re.search(rf'\b{re.escape(kpi)}\b', q):
            return template.copy()

    # Column-based matching with word boundaries
    for col in cols_lower:
        for kpi, template in KPI_TEMPLATES.items():
            # Match kpi at start, end, or surrounded by underscores/spaces
            if re.search(rf'(^|_){re.escape(kpi)}(_|$)', col):
                return template.copy()

    # Keyword matching with word boundaries
    keyword_map = {
        'oee': ['oee', 'overall equipment', 'effectiveness'],
        'downtime': ['downtime', 'down time', 'stopped'],
        'yield': ['yield'],  # More specific to avoid false matches
        'mtbf': ['mtbf', 'mean time between failures'],
        'mttr': ['mttr', 'mean time to repair'],
        'energy': ['energy', 'power consumption', 'electricity', 'kwh'],
        'defect': ['defect', 'defects', 'reject rate', 'rejected'],
        'production': ['production', 'output', 'produced', 'manufactured'],
        'cycle_time': ['cycle time', 'cycle_time', 'takt time'],
        'efficiency': ['efficiency'],  # More specific
        'temperature': ['temperature', 'temp']
    }

    for kpi, keywords in keyword_map.items():
        for kw in keywords:
            # Word boundary matching
            if re.search(rf'\b{re.escape(kw)}\b', q):
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

    # Apply thresholds for progress_bar
    if template.get('thresholds') and config.get('type') == 'progress_bar':
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
