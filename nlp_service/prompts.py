# prompts.py - Version 2.0
# Advanced NLP-to-SQL Prompt System with Dynamic Schema Introspection
# Addresses: schema validation, column matching, date handling, furnace filtering, feedback loop

from typing import Dict, List, Any, Optional
import re

# ============================================================
# SYSTEM PROMPT - Enhanced with dynamic schema guidance
# ============================================================

SYSTEM_PROMPT = """
You are an expert PostgreSQL SQL generator for a furnace manufacturing analytics system.

STRICT RULES:
1. Use ONLY tables and columns from the PROVIDED SCHEMA below.
2. NEVER invent table names, column names, or relationships.
3. Output ONLY the SQL query - no explanations, no markdown, no backticks.
4. Use PostgreSQL syntax.
5. If you cannot answer from the schema, respond with: INSUFFICIENT_SCHEMA

DATE HANDLING RULES:
- KPI tables use 'date' column (DATE type)
- Config tables use 'effective_date' column
- Log tables use 'obs_start_dt' or timestamp columns
- For date ranges: WHERE date BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'
- For relative dates: WHERE date >= CURRENT_DATE - INTERVAL 'N days'

FURNACE FILTERING RULES:
- Filter furnaces by 'furnace_no' column (INTEGER) in KPI tables
- Use exact match: WHERE furnace_no = 1
- furnace_id is a foreign key - do NOT use for filtering

AGGREGATION RULES:
- Percentages (oee_percentage, yield_percentage, etc.) → use AVG()
- Quantities (quantity_produced, cast_weight, etc.) → use SUM()
- Durations (downtime_hours, mtbf_hours, etc.) → use SUM() or AVG()
- Counts (incidents, events) → use COUNT()
- Always GROUP BY furnace_no when comparing furnaces

OUTPUT FORMAT:
- Single valid SELECT statement
- Add LIMIT 100 for raw data queries
- Use ORDER BY date DESC for time-series data
"""

# ============================================================
# TABLE METADATA - For dynamic schema introspection
# ============================================================

TABLE_METADATA = {
    # Production Performance
    "kpi_overall_equipment_efficiency_data": {
        "description": "OEE/Health percentage by furnace and date",
        "value_column": "oee_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["oee", "health", "efficiency", "performance", "overall equipment"]
    },
    "kpi_cycle_time_data": {
        "description": "Production cycle time metrics",
        "value_column": "cycle_time",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["cycle", "time", "production time"]
    },
    "kpi_yield_data": {
        "description": "Yield percentage metrics",
        "value_column": "yield_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["yield", "output quality"]
    },
    "kpi_output_rate_data": {
        "description": "Output rate percentage",
        "value_column": "output_rate_percentage",
        "aggregation": "SUM",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["output", "rate", "production rate"]
    },
    "kpi_quantity_produced_data": {
        "description": "Total quantity produced",
        "value_column": "quantity_produced",
        "aggregation": "SUM",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["quantity", "batch", "produced", "count"]
    },
    
    # Quality
    "kpi_defect_rate_data": {
        "description": "Defect rate percentage",
        "value_column": "defect_rate",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["defect", "quality", "defective"]
    },
    "kpi_first_pass_yield_data": {
        "description": "First pass yield percentage",
        "value_column": "first_pass_yield",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["first pass", "fpy"]
    },
    "kpi_rework_rate_data": {
        "description": "Rework rate percentage",
        "value_column": "rework_rate_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["rework"]
    },
    
    # Energy
    "kpi_energy_used_data": {
        "description": "Total energy consumption",
        "value_column": "energy_used",
        "aggregation": "SUM",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["energy used", "consumption", "power"]
    },
    "kpi_energy_efficiency_data": {
        "description": "Energy efficiency metrics",
        "value_column": "energy_efficiency",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["energy efficiency"]
    },
    
    # Maintenance & Reliability
    "kpi_downtime_data": {
        "description": "Downtime hours by furnace",
        "value_column": "downtime_hours",
        "aggregation": "SUM",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["downtime", "down time", "stoppage"]
    },
    "kpi_maintenance_compliance_data": {
        "description": "Maintenance compliance percentage",
        "value_column": "compliance_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["maintenance", "compliance"]
    },
    "kpi_mean_time_between_failures_data": {
        "description": "MTBF in hours",
        "value_column": "mtbf_hours",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["mtbf", "mean time between failure", "reliability"]
    },
    "kpi_mean_time_to_repair_data": {
        "description": "MTTR in hours",
        "value_column": "mttr_hours",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["mttr", "mean time to repair", "repair time"]
    },
    "kpi_mean_time_between_stoppages_data": {
        "description": "MTBS in hours",
        "value_column": "mtbs_hours",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["mtbs", "stoppages"]
    },
    "kpi_planned_maintenance_data": {
        "description": "Planned maintenance percentage",
        "value_column": "planned_maintenance_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["planned maintenance"]
    },
    
    # Safety
    "kpi_safety_incidents_reported_data": {
        "description": "Safety incidents count",
        "value_column": "incidents_percentage",
        "aggregation": "COUNT",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["safety", "incident", "accident"]
    },
    
    # Financial
    "kpi_total_revenue_data": {
        "description": "Total revenue",
        "value_column": "total_revenue",
        "aggregation": "SUM",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["revenue", "income"]
    },
    "kpi_operating_costs_data": {
        "description": "Operating costs",
        "value_column": "operating_costs",
        "aggregation": "SUM",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["cost", "operating", "expense"]
    },
    
    # Capacity
    "kpi_resource_capacity_utilization_data": {
        "description": "Capacity utilization percentage",
        "value_column": "utilization_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["capacity", "utilization"]
    },
    "kpi_on_time_delivery_data": {
        "description": "On-time delivery percentage",
        "value_column": "on_time_delivery_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "has_furnace": True,
        "keywords": ["delivery", "on time"]
    },
    
    # Core Process
    "core_process_tap_production": {
        "description": "Tap production records with cast weight",
        "value_column": "cast_weight",
        "aggregation": "SUM",
        "date_column": "tap_production_datetime",
        "has_furnace": True,
        "keywords": ["tap", "production", "cast", "weight"]
    },
    "core_process_tap_grading": {
        "description": "Tap grading and quality allocation",
        "value_column": "allocated_grade",
        "aggregation": None,
        "date_column": "grading_datetime",
        "has_furnace": True,
        "keywords": ["grade", "grading", "quality grade"]
    },
    
    # Configuration
    "furnace_config_parameters": {
        "description": "Furnace configuration and settings",
        "value_column": None,
        "aggregation": None,
        "date_column": "effective_date",
        "has_furnace": True,
        "keywords": ["config", "configuration", "parameter", "setting", "crucible"]
    },
    
    # Downtime Events
    "log_book_furnace_down_time_event": {
        "description": "Detailed downtime events with reasons",
        "value_column": "downtime_hours",
        "aggregation": "SUM",
        "date_column": "obs_start_dt",
        "has_furnace": True,
        "keywords": ["downtime event", "reason", "log"]
    },
    
    # Added: 4 missing tables for complete schema coverage
    "furnace_furnaceconfig": {
        "description": "Furnace master data (furnace_no, description, workshop)",
        "value_column": None,
        "aggregation": None,
        "date_column": None,
        "has_furnace": True,
        "keywords": ["furnace", "furnace list", "furnace config", "all furnaces"]
    },
    "plant_plant": {
        "description": "Plant/site master data",
        "value_column": None,
        "aggregation": None,
        "date_column": None,
        "has_furnace": False,
        "keywords": ["plant", "site", "location", "factory"]
    },
    "log_book_reason_master": {
        "description": "Downtime reason codes and descriptions",
        "value_column": None,
        "aggregation": None,
        "date_column": None,
        "has_furnace": False,
        "keywords": ["reason", "downtime reason", "cause", "reason code"]
    },
    "log_book_downtime_type_master": {
        "description": "Downtime type classifications (planned, unplanned)",
        "value_column": None,
        "aggregation": None,
        "date_column": None,
        "has_furnace": False,
        "keywords": ["downtime type", "type", "planned", "unplanned", "classification"]
    },
}

# ============================================================
# FEW-SHOT EXAMPLES - Comprehensive coverage
# ============================================================

FEW_SHOT_EXAMPLES = [
    # OEE/Health
    {"user": "What is the average OEE for Furnace 1 between Jan 1 and Jan 31, 2025?",
     "sql": "SELECT AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1 AND date BETWEEN '2025-01-01' AND '2025-01-31'"},
    {"user": "Show furnace health by furnace",
     "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC"},
    
    # Yield
    {"user": "Show the average yield by furnace",
     "sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC"},
    {"user": "Yield trend for Furnace 2",
     "sql": "SELECT date, yield_percentage FROM kpi_yield_data WHERE furnace_no = 2 ORDER BY date DESC LIMIT 100"},
    
    # Downtime
    {"user": "What is the total downtime for Furnace 1 in January 2025?",
     "sql": "SELECT SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE furnace_no = 1 AND date BETWEEN '2025-01-01' AND '2025-01-31'"},
    {"user": "Downtime by furnace last 30 days",
     "sql": "SELECT furnace_no, SUM(downtime_hours) as total FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY furnace_no ORDER BY total DESC"},
    
    # Energy
    {"user": "What is the average energy efficiency for Furnace 1 in January 2025?",
     "sql": "SELECT AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data WHERE furnace_no = 1 AND date BETWEEN '2025-01-01' AND '2025-01-31'"},
    {"user": "Total energy used last week",
     "sql": "SELECT furnace_no, SUM(energy_used) as total FROM kpi_energy_used_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY furnace_no"},
    
    # MTBF/Reliability
    {"user": "What is the MTBF for Furnace 1 in January 2025?",
     "sql": "SELECT AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data WHERE furnace_no = 1 AND date BETWEEN '2025-01-01' AND '2025-01-31'"},
    {"user": "MTTR by furnace",
     "sql": "SELECT furnace_no, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY furnace_no ORDER BY avg_mttr ASC"},
    
    # Tap Production
    {"user": "What was the total tap production for Furnace 1 in January 2025?",
     "sql": "SELECT SUM(cast_weight) as total_production FROM core_process_tap_production WHERE furnace_no = 1 AND tap_production_datetime BETWEEN '2025-01-01' AND '2025-01-31'"},
    {"user": "Recent tap production",
     "sql": "SELECT tap_id, furnace_no, cast_weight, tap_production_datetime FROM core_process_tap_production ORDER BY tap_production_datetime DESC LIMIT 20"},
    
    # Quality
    {"user": "Defect rate by furnace",
     "sql": "SELECT furnace_no, AVG(defect_rate) as avg_defect FROM kpi_defect_rate_data GROUP BY furnace_no ORDER BY avg_defect ASC"},
    
    # Maintenance
    {"user": "Show maintenance compliance percentage",
     "sql": "SELECT furnace_no, AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data GROUP BY furnace_no"},
    
    # Safety
    {"user": "How many safety incidents were reported for Furnace 1 in January 2025?",
     "sql": "SELECT COUNT(*) as incident_count FROM kpi_safety_incidents_reported_data WHERE furnace_no = 1 AND date BETWEEN '2025-01-01' AND '2025-01-31'"},
    
    # Config
    {"user": "What are the crucible diameter and depth for Furnace 1?",
     "sql": "SELECT crucible_diameter, crucible_depth FROM furnace_config_parameters WHERE furnace_no = 1"},
]

# ============================================================
# DYNAMIC SCHEMA INTROSPECTION
# ============================================================

def find_best_table(question: str) -> Optional[Dict]:
    """
    Find the best matching table based on question keywords.
    Returns table metadata or None if no match.
    """
    question_lower = question.lower()
    best_match = None
    best_score = 0
    
    for table_name, metadata in TABLE_METADATA.items():
        score = 0
        for keyword in metadata["keywords"]:
            if keyword in question_lower:
                score += len(keyword)  # Longer matches score higher
        
        if score > best_score:
            best_score = score
            best_match = {"table": table_name, **metadata}
    
    return best_match


def validate_columns(sql: str, schema_context: str) -> tuple:
    """
    Validate that columns in SQL exist in schema.
    Returns (is_valid, error_message or None).
    """
    # Extract column names from SQL (simplified)
    # In production, use sqlparse for accurate parsing
    
    # Get table name from SQL
    from_match = re.search(r"FROM\s+(\w+)", sql, re.IGNORECASE)
    if not from_match:
        return True, None  # Can't validate without table name
    
    table_name = from_match.group(1).lower()
    
    # Check if table exists in schema
    if table_name not in schema_context.lower():
        return False, f"Table '{table_name}' not found in schema"
    
    return True, None


def generate_sql_hint(question: str) -> str:
    """
    Generate a hint for the LLM based on question analysis.
    """
    table_info = find_best_table(question)
    if not table_info:
        return ""
    
    hint = f"\nHINT: Best matching table is '{table_info['table']}'"
    hint += f"\n- Value column: {table_info['value_column']}"
    hint += f"\n- Use {table_info['aggregation']}() for aggregation"
    hint += f"\n- Date column: {table_info['date_column']}"
    if table_info['has_furnace']:
        hint += "\n- Filter by 'furnace_no' for specific furnace"
    
    return hint


# ============================================================
# BUILD PROMPT FUNCTION
# ============================================================

def build_prompt(schema_text: str, user_question: str) -> str:
    """
    Constructs the final prompt with dynamic hints and examples.
    """
    # Generate dynamic hint based on question
    hint = generate_sql_hint(user_question)
    
    # Build few-shot examples
    examples = ""
    for ex in FEW_SHOT_EXAMPLES:
        examples += f"\nUser: {ex['user']}\nSQL: {ex['sql']}\n"

    return f"""
{SYSTEM_PROMPT}
{hint}

SCHEMA:
{schema_text}

FEW-SHOT EXAMPLES:
{examples}

User: {user_question}
SQL:
"""


# ============================================================
# LEGACY COMPATIBILITY
# ============================================================

def get_sql_generation_prompt(schema_context: str) -> str:
    """Legacy function for backward compatibility."""
    return SYSTEM_PROMPT + f"\n\nSCHEMA:\n{schema_context}"


def get_few_shot_prompt() -> str:
    """Generate few-shot examples as a formatted string."""
    return "\n\n".join([f"Q: {ex['user']}\nSQL: {ex['sql']}" for ex in FEW_SHOT_EXAMPLES])


RESPONSE_FORMAT_PROMPT = """Explain query results concisely.
Question: {question}
SQL: {sql}
Results: {results}
Format values with units (%, hours, tons, kWh). Be brief.
Your response:"""
