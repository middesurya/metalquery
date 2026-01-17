"""
prompts_v2.py - Enhanced Schema-Aware Prompts for 29 IGNIS Tables
Version 3.0 with multi-table JOINs, foreign key mapping, and error recovery
"""

from typing import Dict, List, Any, Optional
import re


# ============================================================
# SCHEMA ANALYZER CLASS
# ============================================================

class SchemaAnalyzer:
    """Analyzes database schema to provide context for prompts."""
    
    def __init__(self, schema_dict: Dict[str, Any]):
        self.schema = schema_dict or {}
        self.tables = list(self.schema.keys()) if isinstance(self.schema, dict) else []
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Get columns for a specific table."""
        if isinstance(self.schema, dict) and table_name in self.schema:
            table_info = self.schema[table_name]
            if isinstance(table_info, dict) and 'columns' in table_info:
                return list(table_info['columns'].keys())
            elif isinstance(table_info, list):
                return table_info
        return []
    
    def find_matching_table(self, question: str) -> Optional[str]:
        """Find best matching table based on question keywords."""
        question_lower = question.lower()
        
        # Use TABLE_SCHEMA for matching
        for table_name, info in TABLE_SCHEMA.items():
            for keyword in info.get("keywords", []):
                if keyword in question_lower:
                    return table_name
        return None
    
    def get_date_column(self, table_name: str) -> str:
        """Get the appropriate date column for a table."""
        if table_name in TABLE_SCHEMA:
            return TABLE_SCHEMA[table_name].get("date_column", "date")
        return "date"
    
    def get_value_column(self, table_name: str) -> Optional[str]:
        """Get the main value column for aggregation."""
        if table_name in TABLE_SCHEMA:
            return TABLE_SCHEMA[table_name].get("value_column")
        return None
    
    def get_aggregation_type(self, table_name: str) -> str:
        """Get recommended aggregation type for a table."""
        if table_name in TABLE_SCHEMA:
            return TABLE_SCHEMA[table_name].get("aggregation", "AVG")
        return "AVG"


# ============================================================
# COMPLETE TABLE SCHEMA (29 Tables)
# ============================================================

TABLE_SCHEMA = {
    # ========== KPI TABLES (20) ==========
    "kpi_overall_equipment_efficiency_data": {
        "description": "OEE percentage (furnace health)",
        "columns": ["record_id", "date", "shift_id", "oee_percentage", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id", "material_id_id", "supplier_id"],
        "value_column": "oee_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["oee", "furnace health", "health", "efficiency", "overall equipment", "performance"]
    },
    "kpi_defect_rate_data": {
        "description": "Defect rate percentage",
        "columns": ["record_id", "date", "shift_id", "defect_rate", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "defect_rate",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["defect", "defects", "quality"]
    },
    "kpi_energy_efficiency_data": {
        "description": "Energy efficiency (kWh/ton)",
        "columns": ["record_id", "date", "shift_id", "energy_efficiency", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "energy_efficiency",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["energy efficiency", "kwh per ton"]
    },
    "kpi_energy_used_data": {
        "description": "Total energy consumed (kWh)",
        "columns": ["record_id", "date", "shift_id", "energy_used", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "energy_used",
        "aggregation": "SUM",
        "date_column": "date",
        "keywords": ["energy used", "energy consumed", "consumption", "kwh"]
    },
    "kpi_downtime_data": {
        "description": "Downtime hours",
        "columns": ["record_id", "date", "shift_id", "downtime_hours", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "downtime_hours",
        "aggregation": "SUM",
        "date_column": "date",
        "keywords": ["downtime", "down time", "stopped"]
    },
    "kpi_mean_time_between_failures_data": {
        "description": "MTBF hours",
        "columns": ["record_id", "date", "shift_id", "mtbf_hours", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "mtbf_hours",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["mtbf", "mean time between failures", "reliability"]
    },
    "kpi_mean_time_to_repair_data": {
        "description": "MTTR hours",
        "columns": ["record_id", "date", "shift_id", "mttr_hours", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "mttr_hours",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["mttr", "mean time to repair", "repair time"]
    },
    "kpi_mean_time_between_stoppages_data": {
        "description": "MTBS hours",
        "columns": ["record_id", "date", "shift_id", "mtbs_hours", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "mtbs_hours",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["mtbs", "mean time between stoppages"]
    },
    "kpi_yield_data": {
        "description": "Yield percentage",
        "columns": ["record_id", "date", "shift_id", "yield_percentage", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "yield_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["yield", "output quality"]
    },
    "kpi_first_pass_yield_data": {
        "description": "First pass yield percentage",
        "columns": ["record_id", "date", "shift_id", "first_pass_yield", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "first_pass_yield",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["first pass", "fpy"]
    },
    "kpi_rework_rate_data": {
        "description": "Rework rate percentage",
        "columns": ["record_id", "date", "shift_id", "rework_rate_percentage", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "rework_rate_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["rework", "redo"]
    },
    "kpi_resource_capacity_utilization_data": {
        "description": "Capacity utilization percentage",
        "columns": ["record_id", "date", "shift_id", "utilization_percentage", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "utilization_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["capacity", "utilization", "usage"]
    },
    "kpi_quantity_produced_data": {
        "description": "Quantity produced",
        "columns": ["record_id", "date", "shift_id", "quantity_produced", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "quantity_produced",
        "aggregation": "SUM",
        "date_column": "date",
        "keywords": ["quantity", "produced", "output", "batch count"]
    },
    "kpi_output_rate_data": {
        "description": "Output rate percentage",
        "columns": ["record_id", "date", "shift_id", "output_rate_percentage", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "output_rate_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["output rate", "production rate"]
    },
    "kpi_production_efficiency_data": {
        "description": "Production efficiency percentage",
        "columns": ["record_id", "date", "shift_id", "production_efficiency_percentage", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "production_efficiency_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["production efficiency"]
    },
    "kpi_on_time_delivery_data": {
        "description": "On-time delivery percentage",
        "columns": ["record_id", "date", "shift_id", "on_time_delivery_percentage", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "on_time_delivery_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["delivery", "on time", "otd"]
    },
    "kpi_cycle_time_data": {
        "description": "Cycle time",
        "columns": ["record_id", "date", "shift_id", "cycle_time", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "cycle_time",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["cycle time", "time per unit"]
    },
    "kpi_maintenance_compliance_data": {
        "description": "Maintenance compliance percentage",
        "columns": ["record_id", "date", "shift_id", "compliance_percentage", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "compliance_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["maintenance compliance", "compliance"]
    },
    "kpi_planned_maintenance_data": {
        "description": "Planned maintenance percentage",
        "columns": ["record_id", "date", "shift_id", "planned_maintenance_percentage", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "planned_maintenance_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["planned maintenance", "scheduled maintenance"]
    },
    "kpi_safety_incidents_reported_data": {
        "description": "Safety incidents percentage",
        "columns": ["record_id", "date", "shift_id", "incidents_percentage", "furnace_no", "machine_id", "plant_id", "product_type_id", "workshop_id"],
        "value_column": "incidents_percentage",
        "aggregation": "AVG",
        "date_column": "date",
        "keywords": ["safety", "incidents", "accidents"]
    },
    
    # ========== CORE PROCESS TABLES (3) ==========
    "core_process_tap_production": {
        "description": "Tap production with cast weights and energy",
        "columns": ["id", "tap_id", "tap_production_datetime", "cast_weight", "liquid_weight", "energy", "energy_efficiency", 
                   "graded_cast_weight", "downgrade_quantity", "ladle_number_code", "ladle_weight_before_tapping", 
                   "ladle_weight_after_tapping", "ladle_weight_after_casting", "ladle_weight_after_slag_removal", 
                   "casting_slag_weight", "recycling_metal_weight", "ferrous_pans", "source", "plant_id"],
        "value_column": "cast_weight",
        "aggregation": "SUM",
        "date_column": "tap_production_datetime",
        "keywords": ["tap", "cast", "weight", "tapping", "tap production"]
    },
    "core_process_tap_process": {
        "description": "Tap process status and progress",
        "columns": ["id", "tap_id", "furnace_no", "tap_datetime", "tap_progress", "tap_status", "tap_hole_id", "target_material", "plant_id"],
        "value_column": "tap_id",
        "aggregation": "COUNT",
        "date_column": "tap_datetime",
        "keywords": ["tap process", "tap status", "progress"]
    },
    "core_process_tap_grading": {
        "description": "Tap grading with allocated grades",
        "columns": ["id", "tap_id", "allocated_grade", "allocated_grade_quality", "allocated_grade_priority", "allocated_grade_bulk_pile", "cast_process_code", "plant_id"],
        "value_column": "allocated_grade",
        "aggregation": "COUNT",
        "date_column": "created_at",
        "keywords": ["grading", "grade", "quality", "allocation"]
    },
    
    # ========== LOG BOOK TABLES (1) ==========
    "log_book_furnace_down_time_event": {
        "description": "Furnace downtime events with reasons",
        "columns": ["id", "furnace_no", "obs_start_dt", "obs_end_dt", "downtime_hours", "equipment_id", "reason_id", "downtime_type_id", "plant_id"],
        "value_column": "downtime_hours",
        "aggregation": "SUM",
        "date_column": "obs_start_dt",
        "keywords": ["downtime event", "event", "log", "stoppage"]
    },
    
    # ========== FURNACE TABLES (2) ==========
    "furnace_config_parameters": {
        "description": "Furnace configuration parameters",
        "columns": ["id", "furnace_config_id", "effective_date", "crucible_diameter", "crucible_depth", 
                   "energy_losses", "joule_losses_coefficient", "default_epi_index", "corrected_reactance_coefficient",
                   "design_mv", "fixed_cost", "target_energy_efficiency", "target_cost_budget", 
                   "target_availability", "target_furnace_load", "pcd_theoretical", "pcd_actual", "plant_id"],
        "value_column": "crucible_diameter",
        "aggregation": "AVG",
        "date_column": "effective_date",
        "keywords": ["config", "configuration", "parameters", "crucible", "settings"]
    },
    "furnace_furnaceconfig": {
        "description": "Furnace master data",
        "columns": ["id", "furnace_no", "furnace_description", "is_active", "workshop_id", "cost_center_id", "power_delivery_id", "plant_id"],
        "value_column": "furnace_no",
        "aggregation": "COUNT",
        "date_column": "created_at",
        "keywords": ["furnace", "furnaces", "list"]
    },
    
    # ========== MASTER TABLES (3) ==========
    "plant_plant": {
        "description": "Plant master data",
        "columns": ["id", "plant_code", "plant_name"],
        "value_column": "plant_code",
        "aggregation": "COUNT",
        "date_column": "created_at",
        "keywords": ["plant", "plants", "location"]
    },
    "log_book_reasons": {
        "description": "Downtime reason codes",
        "columns": ["id", "reason_name", "reason_code"],
        "value_column": "reason_code",
        "aggregation": "COUNT",
        "date_column": "created_at",
        "keywords": ["reason", "reasons", "why"]
    },
    "log_book_downtime_type_master": {
        "description": "Downtime type definitions",
        "columns": ["id", "name", "down_time_type_code"],
        "value_column": "down_time_type_code",
        "aggregation": "COUNT",
        "date_column": "created_at",
        "keywords": ["downtime type", "type", "category"]
    },
}


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """You are an expert PostgreSQL SQL generator for a furnace manufacturing analytics system 
with advanced schema understanding, relationship mapping, and intelligent query building.

════════════════════════════════════════════════════════════════════════════════════

CORE CAPABILITIES:

1. SINGLE-TABLE QUERIES
   ✓ Simple aggregations on KPI tables
   ✓ Date filtering and furnace-based filtering
   ✓ Automatic aggregation type detection (AVG/SUM/COUNT/MIN/MAX)
   ✓ Raw data queries with LIMIT

2. MULTI-TABLE JOIN QUERIES
   ✓ Automatic JOIN path resolution between any tables
   ✓ Foreign key-aware relationship traversal
   ✓ Optimal JOIN ordering and SQL generation
   ✓ Support for 2-4 table complex queries

3. INTELLIGENT AGGREGATION
   ✓ Detects user intent from question keywords
   ✓ Overrides table defaults when appropriate
   ✓ Supports: AVG, SUM, COUNT, MIN, MAX
   ✓ Handles "total", "average", "trend", "show" semantics

4. ERROR RECOVERY
   ✓ Debug prompts for SQL generation failures
   ✓ Automatic correction logic
   ✓ Self-healing capabilities

════════════════════════════════════════════════════════════════════════════════════

STRICT RULES:

1. Output ONLY valid PostgreSQL - no explanations, markdown, or backticks
2. Use ONLY tables and columns from the PROVIDED SCHEMA
3. Filter by 'furnace_no' (INTEGER) when furnace-specific queries requested
4. CRITICAL: Per-table HINT blocks OVERRIDE global rules
5. Add LIMIT 100 for raw data queries
6. Order by date DESC for time-series data
7. Use parameterized values (actual dates/numbers, not variables)

════════════════════════════════════════════════════════════════════════════════════

⚠️ CRITICAL: VARCHAR COLUMN TYPES IN ALL KPI TABLES ⚠️

The following columns are VARCHAR (text) NOT INTEGER across ALL 20 KPI tables.
You MUST use STRING QUOTES when filtering these columns:

  COLUMN NAME      │ CORRECT ✅                    │ WRONG ❌
  ─────────────────┼──────────────────────────────┼─────────────────────
  shift_id         │ WHERE shift_id = '4'         │ WHERE shift_id = 4
                   │ WHERE shift_id IN ('4','12') │ WHERE shift_id IN (4,12)
  ─────────────────┼──────────────────────────────┼─────────────────────
  machine_id       │ WHERE machine_id = 'FURNACE' │ WHERE machine_id = FURNACE
                   │ WHERE machine_id IN ('A','B')│ WHERE machine_id IN (A,B)
  ─────────────────┼──────────────────────────────┼─────────────────────
  product_type_id  │ WHERE product_type_id='M004' │ WHERE product_type_id=M004
                   │ WHERE product_type_id IN (...│ ...

INTEGER columns (use numbers WITHOUT quotes):
  - furnace_no: WHERE furnace_no = 1, furnace_no IN (1, 888)
  - plant_id: WHERE plant_id = 1
  - record_id: WHERE record_id = 123

════════════════════════════════════════════════════════════════════════════════════

AGGREGATION RULES:

WHEN TO USE AGGREGATION:
├─ User asks for: "total", "average", "sum", "count", "compare"
├─ Percentages (oee_percentage, yield_percentage, etc.) → AVG()
├─ Quantities (cast_weight, quantity_produced, downtime_hours) → SUM()
├─ Counts ("how many", "number of") → COUNT()
└─ Always check HINT block for user-requested override!

WHEN NOT TO USE AGGREGATION:
├─ User asks for: "trend", "show data", "list", "recent", "details"
├─ User wants to see raw records
├─ Just SELECT the columns directly with LIMIT and ORDER BY
└─ Example: "Show OEE trend" → No aggregation, raw data with dates

CRITICAL SQL RULES FOR AGGREGATION:
├─ If using aggregate functions (SUM, AVG, COUNT) WITHOUT GROUP BY:
│   └─ DO NOT use ORDER BY (single aggregate result, nothing to sort)
├─ If using aggregate functions WITH GROUP BY:
│   └─ ORDER BY must use GROUP BY columns or aggregate expressions only
│   └─ Example: ORDER BY furnace_no or ORDER BY SUM(downtime_hours) DESC
├─ If NOT using aggregate functions:
│   └─ ORDER BY can use any column (e.g., ORDER BY date DESC)

════════════════════════════════════════════════════════════════════════════════════

COLUMN SELECTION RULES:
1. SELECT ONLY columns necessary to answer the question.
2. DO NOT include `record_id`, `id`, `created_at`, `modified_at` unless explicitly requested.
3. DO NOT use `SELECT *` or select all available columns "just in case".
4. Example: "Show defect rate" → `SELECT date, defect_rate FROM ...` (NOT `SELECT record_id, shift_id, ...`)

VISUALIZATION-READY QUERIES (CRITICAL FOR CHARTING):
1. ALWAYS include the date/time column for time-series KPI data - charts need an X-axis
2. For "list", "show", "display" queries: SELECT date, {value_column} FROM ... ORDER BY date
3. For filtered queries (e.g., "OEE for machine X"): Include date to show trend over time
4. Single numeric columns WITHOUT date/category CANNOT be visualized as charts
5. Example: "List OEE for machine CAST_BAY" → SELECT date, oee_percentage FROM ... WHERE machine_id = 'CAST_BAY' ORDER BY date

AMBIGUITY RESOLUTION:
1. "Production" / "Output" → Use `kpi_quantity_produced_data`
2. "Tap Production" / "Cast Weight" / "Ladle" → Use `core_process_tap_production`

════════════════════════════════════════════════════════════════════════════════════

DATE FILTERING PATTERNS:

Specific Date Range:
  WHERE {date_column} BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'

Relative Date Filters:
  ├─ Last 7 days: WHERE {date_column} >= CURRENT_DATE - INTERVAL '7 days'
  ├─ Last 30 days: WHERE {date_column} >= CURRENT_DATE - INTERVAL '30 days'
  ├─ Last 90 days: WHERE {date_column} >= CURRENT_DATE - INTERVAL '90 days'
  ├─ This month: WHERE EXTRACT(MONTH FROM {date_column}) = EXTRACT(MONTH FROM CURRENT_DATE)
  └─ Last month: WHERE EXTRACT(MONTH FROM {date_column}) = EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')

════════════════════════════════════════════════════════════════════════════════════

MULTI-TABLE JOIN STRATEGY:

1. IDENTIFY TARGET TABLE
   └─ Find best matching table based on user question keywords

2. FIND RELATED TABLES
   └─ Traverse foreign key relationships to find connected tables

3. BUILD JOIN PATH
   ├─ Use foreign keys to connect tables
   ├─ Prefer INNER JOIN over LEFT JOIN when possible
   ├─ Optimal join order: dimension tables last
   └─ Example: fact_table → dimension1 → dimension2 → master_data

4. CONSTRUCT QUERY
   ├─ Start with main fact/process table
   ├─ Add JOINs in dependency order
   ├─ Apply filters in WHERE clause
   ├─ Add GROUP BY for aggregations
   └─ Add ORDER BY for sorting

5. JOIN EXAMPLE
   SELECT p.plant_name, f.furnace_no, 
          AVG(k.oee_percentage) as avg_oee
   FROM kpi_overall_equipment_efficiency_data k
   JOIN furnace_furnaceconfig f ON k.furnace_no = f.furnace_no
   JOIN plant_plant p ON k.plant_id = p.plant_id
   WHERE k.date >= CURRENT_DATE - INTERVAL '30 days'
   GROUP BY p.plant_name, f.furnace_no
   ORDER BY avg_oee DESC

════════════════════════════════════════════════════════════════════════════════════

FOREIGN KEY RELATIONSHIPS (for JOINs):

KPI Tables → furnace_furnaceconfig
  └─ ON kpi_table.furnace_no = furnace_furnaceconfig.furnace_no

furnace_furnaceconfig → furnace_config_parameters
  └─ ON furnace_furnaceconfig.id = furnace_config_parameters.furnace_config_id

KPI/Process Tables → plant_plant
  └─ ON table.plant_id = plant_plant.id

core_process_tap_production → core_process_tap_process
  └─ ON tap_production.tap_id = tap_process.tap_id

core_process_tap_process → core_process_tap_grading
  └─ ON tap_process.tap_id = tap_grading.tap_id

log_book_furnace_down_time_event → log_book_reasons
  └─ ON downtime_event.reason_id = reasons.id

log_book_furnace_down_time_event → log_book_downtime_type_master
  └─ ON downtime_event.downtime_type_id = downtime_type_master.id

════════════════════════════════════════════════════════════════════════════════════

ERROR HANDLING:

1. AMBIGUOUS QUERIES
   → ERROR: Ambiguous query. Please specify metric (e.g., OEE, downtime, production).

2. MULTI-METRIC QUERIES (not supported)
   → ERROR: Multi-metric queries not yet supported. Please ask one metric at a time.

3. UNKNOWN TABLE MAPPING
   → ERROR: Cannot map question to a specific table. Please specify what data you need.

4. COLUMN NOT FOUND
   → Verify column exists in the specified table schema
   → Use correct column names (snake_case, exact match)

════════════════════════════════════════════════════════════════════════════════════

SUPPORTED TABLES SUMMARY:

KPI TABLES (20):
├─ kpi_overall_equipment_efficiency_data (OEE %)
├─ kpi_defect_rate_data (quality metrics)
├─ kpi_downtime_data (equipment downtime hours)
├─ kpi_yield_data (production yield %)
├─ kpi_energy_used_data (kWh consumed)
├─ kpi_energy_efficiency_data (kWh/ton)
├─ kpi_quantity_produced_data (units produced)
├─ kpi_cycle_time_data (time per unit)
├─ kpi_mean_time_between_failures_data (MTBF hours)
├─ kpi_mean_time_to_repair_data (MTTR hours)
├─ kpi_mean_time_between_stoppages_data (MTBS hours)
├─ kpi_first_pass_yield_data (FPY %)
├─ kpi_rework_rate_data (rework %)
├─ kpi_resource_capacity_utilization_data (capacity %)
├─ kpi_output_rate_data (output %)
├─ kpi_production_efficiency_data (efficiency %)
├─ kpi_on_time_delivery_data (OTD %)
├─ kpi_maintenance_compliance_data (compliance %)
├─ kpi_planned_maintenance_data (scheduled maintenance %)
└─ kpi_safety_incidents_reported_data (safety incidents %)

CORE PROCESS TABLES (3):
├─ core_process_tap_production (cast production with weights/energy)
├─ core_process_tap_process (tap tracking status)
└─ core_process_tap_grading (quality grading allocation)

MASTER/CONFIG TABLES (3):
├─ plant_plant (plant definitions)
├─ furnace_furnaceconfig (furnace master data)
└─ furnace_config_parameters (furnace configuration)

LOG/REFERENCE TABLES (3):
├─ log_book_furnace_down_time_event (downtime events)
├─ log_book_reasons (reason codes)
└─ log_book_downtime_type_master (downtime type definitions)

TOTAL: 29 tables with 50+ foreign key relationships
"""


# ============================================================
# FEW-SHOT EXAMPLES (80+ Examples in 10 Categories)
# ============================================================

FEW_SHOT_EXAMPLES = [
    # ═══════════════════════════════════════════════════════════════════
    # TYPE 1: SIMPLE AGGREGATION (12)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average oee for all furnaces", "sql": "SELECT AVG(oee_percentage) as average_oee FROM kpi_overall_equipment_efficiency_data"},
    {"q": "What is the average oee for furnace 1", "sql": "SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1"},
    {"q": "What is the average oee for furnace 1 last 30 days", "sql": "SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1 AND date >= CURRENT_DATE - INTERVAL '30 days'"},
    {"q": "Show Average OEE by furnace", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC"},
    {"q": "Show OEE by furnace", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC"},
    {"q": "Show oee by furnace", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC"},
    {"q": "Show Total downtime by furnace", "sql": "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC"},
    {"q": "Show Total energy consumption by furnace", "sql": "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total_energy DESC"},
    {"q": "Which furnace has highest OEE?", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC LIMIT 1"},
    {"q": "Show Total quantity produced by furnace", "sql": "SELECT furnace_no, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_qty DESC"},
    {"q": "What is the average yield for furnace 2", "sql": "SELECT AVG(yield_percentage) FROM kpi_yield_data WHERE furnace_no = 2"},
    {"q": "Show what is the total downtime last year", "sql": "SELECT SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '1 year'"},
    {"q": "What is the average downtime per furnace", "sql": "SELECT furnace_no, AVG(downtime_hours) as avg_downtime FROM kpi_downtime_data GROUP BY furnace_no"},
    {"q": "What is the total production for furnace 1 last month", "sql": "SELECT SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data WHERE furnace_no = 1 AND date >= CURRENT_DATE - INTERVAL '30 days'"},
    {"q": "Show production by furnace", "sql": "SELECT furnace_no, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_qty DESC"},
    {"q": "Show production by furnace", "sql": "SELECT furnace_no, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_qty DESC"},
    {"q": "Show downtime by furnace", "sql": "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC"},
    {"q": "Show downtime by furnace", "sql": "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC"},
    {"q": "Show energy consumption by furnace", "sql": "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total_energy DESC"},
    {"q": "Show energy by furnace", "sql": "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total_energy DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 2: TREND ANALYSIS - NO AGGREGATION (12)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show OEE trend for Furnace 2", "sql": "SELECT date, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 2 ORDER BY date DESC LIMIT 100"},
    {"q": "Display downtime trend last 30 days", "sql": "SELECT date, furnace_no, downtime_hours FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC"},
    {"q": "Show recent defect rate data", "sql": "SELECT date, shift_id, furnace_no, defect_rate FROM kpi_defect_rate_data ORDER BY date DESC LIMIT 50"},
    {"q": "Show OEE trend last week", "sql": "SELECT date, furnace_no, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' ORDER BY date DESC"},
    {"q": "List all furnaces", "sql": "SELECT furnace_no, furnace_description, is_active FROM furnace_furnaceconfig ORDER BY furnace_no"},
    {"q": "Show downtime events for Furnace 1", "sql": "SELECT obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE furnace_no = 1 ORDER BY obs_start_dt DESC LIMIT 50"},
    {"q": "Show recent tap production data", "sql": "SELECT tap_id, cast_weight, energy, tap_production_datetime FROM core_process_tap_production ORDER BY tap_production_datetime DESC LIMIT 20"},
    {"q": "Show yield data for last month", "sql": "SELECT date, furnace_no, yield_percentage FROM kpi_yield_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC"},
    {"q": "Display energy efficiency trend", "sql": "SELECT date, furnace_no, energy_efficiency FROM kpi_energy_efficiency_data ORDER BY date DESC LIMIT 100"},
    {"q": "Show MTTR data for Furnace 2", "sql": "SELECT date, mttr_hours FROM kpi_mean_time_to_repair_data WHERE furnace_no = 2 ORDER BY date DESC LIMIT 100"},
    {"q": "List recent quality issues", "sql": "SELECT date, furnace_no, defect_rate FROM kpi_defect_rate_data ORDER BY date DESC LIMIT 100"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 3: COMPARATIVE ANALYSIS (10)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Compare OEE between Furnace 1 and 2", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE furnace_no IN (1, 2) GROUP BY furnace_no ORDER BY avg_oee DESC"},
    {"q": "Which shift has highest yield?", "sql": "SELECT shift_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY shift_id ORDER BY avg_yield DESC LIMIT 1"},
    {"q": "Show yield by shift", "sql": "SELECT shift_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY shift_id ORDER BY avg_yield DESC"},
    {"q": "Show yield by shift", "sql": "SELECT shift_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY shift_id ORDER BY avg_yield DESC"},
    {"q": "Show production by shift", "sql": "SELECT shift_id, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY shift_id ORDER BY total_qty DESC"},
    {"q": "Show production by shift", "sql": "SELECT shift_id, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY shift_id ORDER BY total_qty DESC"},
    {"q": "Show oee by shift", "sql": "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC"},
    {"q": "Show OEE by shift", "sql": "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC"},
    {"q": "Compare all furnaces by OEE", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee, MAX(oee_percentage) as max_oee, MIN(oee_percentage) as min_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC"},
    {"q": "Show rank furnaces by defect rate", "sql": "SELECT furnace_no, AVG(defect_rate) as avg_defect FROM kpi_defect_rate_data GROUP BY furnace_no ORDER BY avg_defect DESC"},
    {"q": "Compare downtime between machines", "sql": "SELECT machine_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY machine_id ORDER BY total_downtime DESC"},
    {"q": "Which product type has highest yield?", "sql": "SELECT product_type_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY product_type_id ORDER BY avg_yield DESC LIMIT 1"},
    {"q": "Compare energy efficiency by furnace", "sql": "SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency"},
    {"q": "Show production efficiency by shift", "sql": "SELECT shift_id, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency DESC"},
    {"q": "Compare MTBF by furnace", "sql": "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC"},
    {"q": "Show best and worst shift by oee", "sql": "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 4: MULTI-METRIC JOINS (8)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show Average OEE by furnace with names", "sql": "SELECT f.furnace_no, f.furnace_description, AVG(k.oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data k JOIN furnace_furnaceconfig f ON k.furnace_no = f.furnace_no GROUP BY f.furnace_no, f.furnace_description ORDER BY avg_oee DESC"},
    {"q": "Show tap production by tap status", "sql": "SELECT t.tap_status, COUNT(t.tap_id) as tap_count, SUM(tp.cast_weight) as total_weight FROM core_process_tap_process t JOIN core_process_tap_production tp ON t.tap_id = tp.tap_id GROUP BY t.tap_status ORDER BY tap_count DESC"},
    {"q": "Show downtime events with reasons for furnace 1", "sql": "SELECT d.obs_start_dt, d.obs_end_dt, d.downtime_hours, r.reason_name FROM log_book_furnace_down_time_event d LEFT JOIN log_book_reasons r ON d.reason_id = r.id WHERE d.furnace_no = 1 ORDER BY d.obs_start_dt DESC LIMIT 50"},
    {"q": "Show oee and yield by furnace last month", "sql": "SELECT f.furnace_no, f.furnace_description, AVG(k1.oee_percentage) as avg_oee, AVG(k2.yield_percentage) as avg_yield FROM kpi_overall_equipment_efficiency_data k1 JOIN kpi_yield_data k2 ON k1.furnace_no = k2.furnace_no AND k1.date = k2.date JOIN furnace_furnaceconfig f ON k1.furnace_no = f.furnace_no WHERE k1.date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY f.furnace_no, f.furnace_description ORDER BY avg_oee DESC"},
    {"q": "Show production with furnace details", "sql": "SELECT f.furnace_no, f.furnace_description, SUM(tp.cast_weight) as total_weight, AVG(tp.energy_efficiency) as avg_efficiency FROM core_process_tap_production tp JOIN core_process_tap_process t ON tp.tap_id = t.tap_id JOIN furnace_furnaceconfig f ON t.furnace_no = f.furnace_no GROUP BY f.furnace_no, f.furnace_description ORDER BY total_weight DESC"},
    {"q": "Show oee by plant", "sql": "SELECT p.plant_name, AVG(k.oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data k JOIN plant_plant p ON k.plant_id = p.id GROUP BY p.id, p.plant_name ORDER BY avg_oee DESC"},
    {"q": "Show energy usage by furnace with config", "sql": "SELECT f.furnace_no, f.furnace_description, SUM(k.energy_used) as total_energy FROM kpi_energy_used_data k JOIN furnace_furnaceconfig f ON k.furnace_no = f.furnace_no GROUP BY f.furnace_no, f.furnace_description ORDER BY total_energy DESC"},
    {"q": "Show tap grading with tap status", "sql": "SELECT t.tap_status, COUNT(DISTINCT g.tap_id) as graded_taps FROM core_process_tap_grading g JOIN core_process_tap_process t ON g.tap_id = t.tap_id GROUP BY t.tap_status"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 5: TEMPORAL COMPARISON (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Compare OEE January vs February 2025", "sql": "SELECT EXTRACT(MONTH FROM date) as month, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE EXTRACT(YEAR FROM date) = 2025 AND EXTRACT(MONTH FROM date) IN (1, 2) GROUP BY EXTRACT(MONTH FROM date) ORDER BY month"},
    {"q": "Show week over week downtime comparison", "sql": "SELECT CASE WHEN date >= CURRENT_DATE - INTERVAL '7 days' THEN 'Current Week' ELSE 'Previous Week' END as period, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '14 days' GROUP BY period"},
    {"q": "Compare last 2 months of OEE", "sql": "SELECT DATE_TRUNC('month', date)::DATE as month, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE date >= CURRENT_DATE - INTERVAL '60 days' GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC"},
    {"q": "Show monthly energy trend", "sql": "SELECT DATE_TRUNC('month', date)::DATE as month, SUM(energy_used) as monthly_total FROM kpi_energy_used_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC"},
    {"q": "Show this month vs last month downtime", "sql": "SELECT CASE WHEN date >= CURRENT_DATE - INTERVAL '30 days' THEN 'This Month' ELSE 'Last Month' END as period, SUM(downtime_hours) as total FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '60 days' GROUP BY period"},
    {"q": "Show year to date production", "sql": "SELECT DATE_TRUNC('month', tap_production_datetime)::DATE as month, SUM(cast_weight) as monthly_production FROM core_process_tap_production WHERE EXTRACT(YEAR FROM tap_production_datetime) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY DATE_TRUNC('month', tap_production_datetime) ORDER BY month DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 6: THRESHOLD-BASED (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show OEE records above 90%", "sql": "SELECT date, furnace_no, shift_id, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage > 90 ORDER BY oee_percentage DESC LIMIT 100"},
    {"q": "Show downtime events exceeding 8 hours", "sql": "SELECT obs_start_dt, furnace_no, downtime_hours FROM log_book_furnace_down_time_event WHERE downtime_hours > 8 ORDER BY downtime_hours DESC"},
    {"q": "Show furnaces with low efficiency below 80%", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no HAVING AVG(oee_percentage) < 80"},
    {"q": "Show defect rate above 5 percent", "sql": "SELECT date, shift_id, furnace_no, defect_rate FROM kpi_defect_rate_data WHERE defect_rate > 5 ORDER BY defect_rate DESC LIMIT 100"},
    {"q": "Show energy usage above average", "sql": "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no HAVING SUM(energy_used) > (SELECT AVG(energy_used) FROM kpi_energy_used_data)"},
    {"q": "Show low yield furnaces below 85%", "sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no HAVING AVG(yield_percentage) < 85 ORDER BY avg_yield"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 7: RANKING / TOP-N (7)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show top 5 furnaces by production", "sql": "SELECT furnace_no, SUM(cast_weight) as total_production FROM core_process_tap_production GROUP BY furnace_no ORDER BY total_production DESC LIMIT 5"},
    {"q": "Show bottom 3 furnaces by yield", "sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield ASC LIMIT 3"},
    {"q": "Show top 10 shifts by output", "sql": "SELECT shift_id, SUM(quantity_produced) as total_output FROM kpi_quantity_produced_data GROUP BY shift_id ORDER BY total_output DESC LIMIT 10"},
    {"q": "What is the worst furnace by OEE", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee ASC LIMIT 1"},
    {"q": "Show top 3 machines by energy", "sql": "SELECT machine_id, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY machine_id ORDER BY total_energy DESC LIMIT 3"},
    {"q": "What is the best shift by efficiency", "sql": "SELECT shift_id, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency DESC LIMIT 1"},
    {"q": "What is the most reliable furnace", "sql": "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC LIMIT 1"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 8: STATISTICAL (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show oee statistics", "sql": "SELECT MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, AVG(oee_percentage) as avg_oee, STDDEV(oee_percentage) as stddev_oee FROM kpi_overall_equipment_efficiency_data"},
    {"q": "Show downtime statistics by furnace", "sql": "SELECT furnace_no, MIN(downtime_hours) as min, MAX(downtime_hours) as max, AVG(downtime_hours) as avg, SUM(downtime_hours) as total, COUNT(*) as count FROM kpi_downtime_data GROUP BY furnace_no"},
    {"q": "Show energy efficiency range", "sql": "SELECT MIN(energy_efficiency) as min_eff, MAX(energy_efficiency) as max_eff, AVG(energy_efficiency) as avg_eff FROM kpi_energy_efficiency_data"},
    {"q": "Show yield statistics by furnace", "sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield, STDDEV(yield_percentage) as stddev_yield, MIN(yield_percentage) as min_yield, MAX(yield_percentage) as max_yield FROM kpi_yield_data GROUP BY furnace_no"},
    {"q": "Show production quantity statistics", "sql": "SELECT AVG(quantity_produced) as avg_qty, MAX(quantity_produced) as max_qty, MIN(quantity_produced) as min_qty, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 9: TIME-SERIES BUCKETING (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average oee per day", "sql": "SELECT DATE_TRUNC('day', date)::DATE as day, AVG(oee_percentage) as daily_avg FROM kpi_overall_equipment_efficiency_data GROUP BY DATE_TRUNC('day', date) ORDER BY day DESC"},
    {"q": "What is the total production per week", "sql": "SELECT DATE_TRUNC('week', tap_production_datetime)::DATE as week, SUM(cast_weight) as weekly_total FROM core_process_tap_production GROUP BY DATE_TRUNC('week', tap_production_datetime) ORDER BY week DESC"},
    {"q": "Show monthly energy by furnace", "sql": "SELECT DATE_TRUNC('month', date)::DATE as month, furnace_no, SUM(energy_used) as monthly_total FROM kpi_energy_used_data GROUP BY DATE_TRUNC('month', date), furnace_no ORDER BY month DESC, furnace_no"},
    {"q": "Show daily downtime summary", "sql": "SELECT DATE_TRUNC('day', date)::DATE as day, SUM(downtime_hours) as daily_downtime, COUNT(*) as event_count FROM kpi_downtime_data GROUP BY DATE_TRUNC('day', date) ORDER BY day DESC"},
    {"q": "Show weekly yield trend", "sql": "SELECT DATE_TRUNC('week', date)::DATE as week, AVG(yield_percentage) as weekly_avg_yield FROM kpi_yield_data GROUP BY DATE_TRUNC('week', date) ORDER BY week DESC"},
    {"q": "Show daily tap production", "sql": "SELECT DATE_TRUNC('day', tap_production_datetime)::DATE as production_date, COUNT(DISTINCT tap_id) as tap_count, SUM(cast_weight) as daily_weight FROM core_process_tap_production GROUP BY DATE_TRUNC('day', tap_production_datetime) ORDER BY production_date DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 10: ANOMALY DETECTION (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show unusually high downtime", "sql": "SELECT obs_start_dt, furnace_no, downtime_hours FROM log_book_furnace_down_time_event WHERE downtime_hours > (SELECT AVG(downtime_hours) + 2 * STDDEV(downtime_hours) FROM log_book_furnace_down_time_event) ORDER BY downtime_hours DESC"},
    {"q": "Show oee outliers below normal", "sql": "SELECT date, furnace_no, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < (SELECT AVG(oee_percentage) - 2 * STDDEV(oee_percentage) FROM kpi_overall_equipment_efficiency_data) ORDER BY oee_percentage"},
    {"q": "Show unusually low yield", "sql": "SELECT date, furnace_no, yield_percentage FROM kpi_yield_data WHERE yield_percentage < (SELECT AVG(yield_percentage) - 1.5 * STDDEV(yield_percentage) FROM kpi_yield_data) ORDER BY yield_percentage"},
    {"q": "Show energy spikes above normal", "sql": "SELECT date, furnace_no, energy_used FROM kpi_energy_used_data WHERE energy_used > (SELECT AVG(energy_used) + 2 * STDDEV(energy_used) FROM kpi_energy_used_data) ORDER BY energy_used DESC"},
    {"q": "Show high defect rate anomalies", "sql": "SELECT date, furnace_no, defect_rate FROM kpi_defect_rate_data WHERE defect_rate > (SELECT AVG(defect_rate) + 1.5 * STDDEV(defect_rate) FROM kpi_defect_rate_data) ORDER BY defect_rate DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # VARCHAR FILTERING - CRITICAL (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show oee for shift 4", "sql": "SELECT date, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE shift_id = '4' ORDER BY date DESC LIMIT 100"},
    {"q": "Compare shifts 4, 12, and 20 downtime", "sql": "SELECT shift_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE shift_id IN ('4', '12', '20') GROUP BY shift_id ORDER BY total_downtime DESC"},
    {"q": "Show oee for machine furnace", "sql": "SELECT date, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE machine_id = 'FURNACE' ORDER BY date DESC LIMIT 100"},
    {"q": "Show production for product m004", "sql": "SELECT date, quantity_produced FROM kpi_quantity_produced_data WHERE product_type_id = 'M004' ORDER BY date DESC LIMIT 100"},
    {"q": "Compare products MET30 and MET32 yield", "sql": "SELECT product_type_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data WHERE product_type_id IN ('MET30', 'MET32') GROUP BY product_type_id ORDER BY avg_yield DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 11: CYCLE TIME - QUICK LOOKUPS (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the cycle time for FURNACE on 2024-01-07?", "sql": "SELECT date, shift_id, cycle_time, furnace_no FROM kpi_cycle_time_data WHERE machine_id = 'FURNACE' AND date = '2024-01-07' ORDER BY shift_id"},
    {"q": "Show all cycle time records for 2024-01-08", "sql": "SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE date = '2024-01-08' ORDER BY shift_id"},
    {"q": "What was the cycle time for shift 12 on 2024-01-09?", "sql": "SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE shift_id = '12' AND date = '2024-01-09'"},
    {"q": "List cycle times for machine CAST_BAY", "sql": "SELECT date, shift_id, cycle_time, furnace_no FROM kpi_cycle_time_data WHERE machine_id = 'CAST_BAY' ORDER BY date DESC LIMIT 100"},
    {"q": "Show cycle time for furnace 888 on 2024-01-07", "sql": "SELECT date, shift_id, cycle_time, machine_id FROM kpi_cycle_time_data WHERE furnace_no = 888 AND date = '2024-01-07' ORDER BY shift_id"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 12: CYCLE TIME - AGGREGATIONS (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average cycle time overall?", "sql": "SELECT AVG(cycle_time) as average_cycle_time FROM kpi_cycle_time_data"},
    {"q": "What is the total cycle time per day?", "sql": "SELECT date, SUM(cycle_time) as total_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY date DESC"},
    {"q": "What is the average cycle time per shift?", "sql": "SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY shift_id ORDER BY avg_cycle_time DESC"},
    {"q": "Which day had the highest average cycle time?", "sql": "SELECT date, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY avg_cycle_time DESC LIMIT 1"},
    {"q": "Give me the min, max, and average cycle time for 2024-01-07", "sql": "SELECT MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE date = '2024-01-07'"},
    {"q": "Show Average cycle time by furnace", "sql": "SELECT furnace_no, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY furnace_no ORDER BY avg_cycle_time DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 13: CYCLE TIME - SHIFT ANALYSIS (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Which shift has the highest average cycle time?", "sql": "SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY shift_id ORDER BY avg_cycle_time DESC LIMIT 1"},
    {"q": "Compare cycle time between shifts 4, 12, and 20", "sql": "SELECT shift_id, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE shift_id IN ('4', '12', '20') GROUP BY shift_id ORDER BY avg_cycle_time DESC"},
    {"q": "Show cycle time trend by shift over time", "sql": "SELECT date, shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY date, shift_id ORDER BY date DESC, shift_id"},
    {"q": "Show on 2024-01-08, which shift was slowest?", "sql": "SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE date = '2024-01-08' GROUP BY shift_id ORDER BY avg_cycle_time DESC LIMIT 1"},
    {"q": "Show What's the average cycle time for shift 20 across all days?", "sql": "SELECT AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE shift_id = '20'"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 14: CYCLE TIME - MACHINE PERFORMANCE (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Which machine has the highest average cycle time?", "sql": "SELECT machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id ORDER BY avg_cycle_time DESC LIMIT 1"},
    {"q": "Show top 5 machines by cycle time", "sql": "SELECT machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id ORDER BY avg_cycle_time DESC LIMIT 5"},
    {"q": "Which machine had cycle time above 90?", "sql": "SELECT DISTINCT machine_id, date, shift_id, cycle_time FROM kpi_cycle_time_data WHERE cycle_time > 90 ORDER BY cycle_time DESC"},
    {"q": "Compare cycle time for FURNACE vs ELECTROD", "sql": "SELECT machine_id, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE machine_id IN ('FURNACE', 'ELECTROD') GROUP BY machine_id ORDER BY avg_cycle_time DESC"},
    {"q": "Show for unkwn_eq, what's the average cycle time by shift?", "sql": "SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE machine_id = 'UNKWN_EQ' GROUP BY shift_id ORDER BY avg_cycle_time DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 15: CYCLE TIME - FURNACE COMPARISONS (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Compare average cycle time between furnace 1 and furnace 888", "sql": "SELECT furnace_no, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE furnace_no IN (1, 888) GROUP BY furnace_no ORDER BY avg_cycle_time DESC"},
    {"q": "Which furnace has more cycle time spikes?", "sql": "SELECT furnace_no, COUNT(*) as spike_count FROM kpi_cycle_time_data WHERE cycle_time > (SELECT AVG(cycle_time) + STDDEV(cycle_time) FROM kpi_cycle_time_data) GROUP BY furnace_no ORDER BY spike_count DESC"},
    {"q": "Show cycle time distribution for furnace 888", "sql": "SELECT MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time, AVG(cycle_time) as avg_cycle_time, STDDEV(cycle_time) as stddev_cycle_time, COUNT(*) as total_records FROM kpi_cycle_time_data WHERE furnace_no = 888"},
    {"q": "What is the max cycle time for furnace 1?", "sql": "SELECT MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE furnace_no = 1"},
    {"q": "Show cycle time statistics by furnace", "sql": "SELECT furnace_no, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time, STDDEV(cycle_time) as stddev_cycle_time FROM kpi_cycle_time_data GROUP BY furnace_no ORDER BY avg_cycle_time DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 16: CYCLE TIME - PRODUCT-BASED (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average cycle time for product M004?", "sql": "SELECT AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE product_type_id = 'M004'"},
    {"q": "Which product_type_id has the highest cycle time?", "sql": "SELECT product_type_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY product_type_id ORDER BY avg_cycle_time DESC LIMIT 1"},
    {"q": "Compare cycle time for MET30 vs MET32", "sql": "SELECT product_type_id, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE product_type_id IN ('MET30', 'MET32') GROUP BY product_type_id ORDER BY avg_cycle_time DESC"},
    {"q": "Show cycle time by product_type_id for each day", "sql": "SELECT date, product_type_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY date, product_type_id ORDER BY date DESC, product_type_id"},
    {"q": "Which products have cycle time above 80 on 2024-01-07?", "sql": "SELECT DISTINCT product_type_id, cycle_time FROM kpi_cycle_time_data WHERE cycle_time > 80 AND date = '2024-01-07' ORDER BY cycle_time DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 17: CYCLE TIME - TREND ANALYSIS (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show is cycle time increasing from jan 7 to jan 9?", "sql": "SELECT date, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE date BETWEEN '2024-01-07' AND '2024-01-09' GROUP BY date ORDER BY date"},
    {"q": "Show the cycle time trend per machine across days", "sql": "SELECT date, machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY date, machine_id ORDER BY date DESC, machine_id"},
    {"q": "Which machine improved the most between Jan 7 and Jan 9?", "sql": "SELECT machine_id, AVG(CASE WHEN date = '2024-01-07' THEN cycle_time END) as jan7_avg, AVG(CASE WHEN date = '2024-01-09' THEN cycle_time END) as jan9_avg, AVG(CASE WHEN date = '2024-01-07' THEN cycle_time END) - AVG(CASE WHEN date = '2024-01-09' THEN cycle_time END) as improvement FROM kpi_cycle_time_data WHERE date IN ('2024-01-07', '2024-01-09') GROUP BY machine_id ORDER BY improvement DESC LIMIT 1"},
    {"q": "Which shift shows the biggest cycle time variation?", "sql": "SELECT shift_id, STDDEV(cycle_time) as cycle_time_variation, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY shift_id ORDER BY cycle_time_variation DESC LIMIT 1"},
    {"q": "Show daily cycle time trend", "sql": "SELECT date, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY date DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 18: CYCLE TIME - EXCEPTIONS & ALERTS (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show records where cycle time is greater than 90", "sql": "SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE cycle_time > 90 ORDER BY cycle_time DESC LIMIT 100"},
    {"q": "Which machines crossed the cycle time threshold on Jan 8?", "sql": "SELECT DISTINCT machine_id, cycle_time, shift_id FROM kpi_cycle_time_data WHERE date = '2024-01-08' AND cycle_time > 90 ORDER BY cycle_time DESC"},
    {"q": "List the top 10 highest cycle time incidents", "sql": "SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data ORDER BY cycle_time DESC LIMIT 10"},
    {"q": "Which machine had the lowest cycle time and when?", "sql": "SELECT machine_id, date, shift_id, cycle_time FROM kpi_cycle_time_data ORDER BY cycle_time ASC LIMIT 1"},
    {"q": "Show cycle time anomalies above normal", "sql": "SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE cycle_time > (SELECT AVG(cycle_time) + 2 * STDDEV(cycle_time) FROM kpi_cycle_time_data) ORDER BY cycle_time DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 19: CYCLE TIME - CHATBOT STYLE QUESTIONS (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What are the slowest machines today?", "sql": "SELECT machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE date = CURRENT_DATE GROUP BY machine_id ORDER BY avg_cycle_time DESC LIMIT 5"},
    {"q": "Show where are we spending the most time in the process?", "sql": "SELECT machine_id, SUM(cycle_time) as total_cycle_time, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id ORDER BY total_cycle_time DESC LIMIT 5"},
    {"q": "Which area should I investigate first for long cycle times?", "sql": "SELECT machine_id, furnace_no, AVG(cycle_time) as avg_cycle_time, COUNT(*) as record_count FROM kpi_cycle_time_data WHERE cycle_time > (SELECT AVG(cycle_time) FROM kpi_cycle_time_data) GROUP BY machine_id, furnace_no ORDER BY avg_cycle_time DESC LIMIT 5"},
    {"q": "What changed on Jan 8 that caused higher cycle time?", "sql": "SELECT machine_id, shift_id, AVG(cycle_time) as avg_cycle_time, COUNT(*) as record_count FROM kpi_cycle_time_data WHERE date = '2024-01-08' GROUP BY machine_id, shift_id ORDER BY avg_cycle_time DESC"},
    {"q": "Show me cycle time bottlenecks", "sql": "SELECT machine_id, furnace_no, AVG(cycle_time) as avg_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id, furnace_no HAVING AVG(cycle_time) > (SELECT AVG(cycle_time) FROM kpi_cycle_time_data) ORDER BY avg_cycle_time DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 20: OEE - QUICK LOOKUPS (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the OEE for FURNACE on 2024-01-07?", "sql": "SELECT date, shift_id, oee_percentage, furnace_no FROM kpi_overall_equipment_efficiency_data WHERE machine_id = 'FURNACE' AND date = '2024-01-07' ORDER BY shift_id"},
    {"q": "Show all OEE records for 2024-01-08", "sql": "SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data WHERE date = '2024-01-08' ORDER BY shift_id"},
    {"q": "What was the OEE for shift 12 on 2024-01-09?", "sql": "SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data WHERE shift_id = '12' AND date = '2024-01-09'"},
    {"q": "List OEE for machine CAST_BAY", "sql": "SELECT date, shift_id, oee_percentage, furnace_no FROM kpi_overall_equipment_efficiency_data WHERE machine_id = 'CAST_BAY' ORDER BY date DESC LIMIT 100"},
    {"q": "Show OEE for furnace 888 on 2024-01-07", "sql": "SELECT date, shift_id, oee_percentage, machine_id FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 888 AND date = '2024-01-07' ORDER BY shift_id"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 21: OEE - AGGREGATIONS (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average OEE overall?", "sql": "SELECT AVG(oee_percentage) as average_oee FROM kpi_overall_equipment_efficiency_data"},
    {"q": "What is the average OEE per day?", "sql": "SELECT date, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date ORDER BY date DESC"},
    {"q": "What is the average OEE per shift?", "sql": "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC"},
    {"q": "Which day had the highest average OEE?", "sql": "SELECT date, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date ORDER BY avg_oee DESC LIMIT 1"},
    {"q": "Give me the min, max, and average OEE for 2024-01-07", "sql": "SELECT MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE date = '2024-01-07'"},
    {"q": "Show Average OEE by furnace", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 22: OEE - SHIFT ANALYSIS (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Which shift has the highest average OEE?", "sql": "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC LIMIT 1"},
    {"q": "Compare OEE between shifts 4, 12, and 20", "sql": "SELECT shift_id, AVG(oee_percentage) as avg_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data WHERE shift_id IN ('4', '12', '20') GROUP BY shift_id ORDER BY avg_oee DESC"},
    {"q": "Show OEE trend by shift over time", "sql": "SELECT date, shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date, shift_id ORDER BY date DESC, shift_id"},
    {"q": "Show on 2024-01-08, which shift performed best?", "sql": "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE date = '2024-01-08' GROUP BY shift_id ORDER BY avg_oee DESC LIMIT 1"},
    {"q": "Show What's the average OEE for shift 20 across all days?", "sql": "SELECT AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE shift_id = '20'"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 23: OEE - MACHINE PERFORMANCE (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Which machine has the highest average OEE?", "sql": "SELECT machine_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY machine_id ORDER BY avg_oee DESC LIMIT 1"},
    {"q": "Show top 5 machines by OEE", "sql": "SELECT machine_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY machine_id ORDER BY avg_oee DESC LIMIT 5"},
    {"q": "Which machines have OEE below 80?", "sql": "SELECT DISTINCT machine_id, date, shift_id, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < 80 ORDER BY oee_percentage ASC"},
    {"q": "Compare OEE for FURNACE vs ELECTROD", "sql": "SELECT machine_id, AVG(oee_percentage) as avg_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data WHERE machine_id IN ('FURNACE', 'ELECTROD') GROUP BY machine_id ORDER BY avg_oee DESC"},
    {"q": "Show for unkwn_eq, what's the average oee by shift?", "sql": "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE machine_id = 'UNKWN_EQ' GROUP BY shift_id ORDER BY avg_oee DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 24: OEE - FURNACE COMPARISONS (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Compare average OEE between furnace 1 and furnace 888", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE furnace_no IN (1, 888) GROUP BY furnace_no ORDER BY avg_oee DESC"},
    {"q": "Which furnace has the most OEE drops below 70?", "sql": "SELECT furnace_no, COUNT(*) as drop_count FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < 70 GROUP BY furnace_no ORDER BY drop_count DESC"},
    {"q": "Show OEE distribution for furnace 888", "sql": "SELECT MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, AVG(oee_percentage) as avg_oee, STDDEV(oee_percentage) as stddev_oee, COUNT(*) as total_records FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 888"},
    {"q": "What is the max OEE for furnace 1?", "sql": "SELECT MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1"},
    {"q": "Show oee statistics by furnace", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, STDDEV(oee_percentage) as stddev_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 25: OEE - PRODUCT & MATERIAL ANALYSIS (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average OEE for product M004?", "sql": "SELECT AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE product_type_id = 'M004'"},
    {"q": "Which product_type_id has the highest OEE?", "sql": "SELECT product_type_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY product_type_id ORDER BY avg_oee DESC LIMIT 1"},
    {"q": "Compare OEE for MET30 vs MET32", "sql": "SELECT product_type_id, AVG(oee_percentage) as avg_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data WHERE product_type_id IN ('MET30', 'MET32') GROUP BY product_type_id ORDER BY avg_oee DESC"},
    {"q": "Show OEE by product_type_id for each day", "sql": "SELECT date, product_type_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date, product_type_id ORDER BY date DESC, product_type_id"},
    {"q": "Which products have OEE below 75 on 2024-01-07?", "sql": "SELECT DISTINCT product_type_id, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < 75 AND date = '2024-01-07' ORDER BY oee_percentage ASC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 26: OEE - SUPPLIER & WORKSHOP ANALYSIS (4)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show Average OEE by supplier", "sql": "SELECT supplier_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY supplier_id ORDER BY avg_oee DESC"},
    {"q": "Which supplier has the lowest OEE?", "sql": "SELECT supplier_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY supplier_id ORDER BY avg_oee ASC LIMIT 1"},
    {"q": "Show oee by workshop", "sql": "SELECT workshop_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY workshop_id ORDER BY avg_oee DESC"},
    {"q": "Compare OEE across plants", "sql": "SELECT plant_id, AVG(oee_percentage) as avg_oee, COUNT(*) as record_count FROM kpi_overall_equipment_efficiency_data GROUP BY plant_id ORDER BY avg_oee DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 27: OEE - TREND ANALYSIS (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show is oee increasing from jan 7 to jan 9?", "sql": "SELECT date, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE date BETWEEN '2024-01-07' AND '2024-01-09' GROUP BY date ORDER BY date"},
    {"q": "Show the OEE trend per machine across days", "sql": "SELECT date, machine_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date, machine_id ORDER BY date DESC, machine_id"},
    {"q": "Which machine improved the most between Jan 7 and Jan 9?", "sql": "SELECT machine_id, AVG(CASE WHEN date = '2024-01-07' THEN oee_percentage END) as jan7_avg, AVG(CASE WHEN date = '2024-01-09' THEN oee_percentage END) as jan9_avg, AVG(CASE WHEN date = '2024-01-09' THEN oee_percentage END) - AVG(CASE WHEN date = '2024-01-07' THEN oee_percentage END) as improvement FROM kpi_overall_equipment_efficiency_data WHERE date IN ('2024-01-07', '2024-01-09') GROUP BY machine_id ORDER BY improvement DESC LIMIT 1"},
    {"q": "Which shift shows the biggest OEE variation?", "sql": "SELECT shift_id, STDDEV(oee_percentage) as oee_variation, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY oee_variation DESC LIMIT 1"},
    {"q": "Show daily oee trend", "sql": "SELECT date, AVG(oee_percentage) as avg_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date ORDER BY date DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 28: OEE - EXCEPTIONS & ALERTS (5)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show records where OEE is below 70", "sql": "SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < 70 ORDER BY oee_percentage ASC LIMIT 100"},
    {"q": "Which machines had OEE below threshold on Jan 8?", "sql": "SELECT DISTINCT machine_id, oee_percentage, shift_id FROM kpi_overall_equipment_efficiency_data WHERE date = '2024-01-08' AND oee_percentage < 75 ORDER BY oee_percentage ASC"},
    {"q": "List the top 10 lowest OEE incidents", "sql": "SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data ORDER BY oee_percentage ASC LIMIT 10"},
    {"q": "Which machine had the highest OEE and when?", "sql": "SELECT machine_id, date, shift_id, oee_percentage FROM kpi_overall_equipment_efficiency_data ORDER BY oee_percentage DESC LIMIT 1"},
    {"q": "Show oee anomalies below normal", "sql": "SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < (SELECT AVG(oee_percentage) - 2 * STDDEV(oee_percentage) FROM kpi_overall_equipment_efficiency_data) ORDER BY oee_percentage ASC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 29: OEE - CHATBOT STYLE QUESTIONS (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the furnace health today?", "sql": "SELECT furnace_no, AVG(oee_percentage) as health_score FROM kpi_overall_equipment_efficiency_data WHERE date = CURRENT_DATE GROUP BY furnace_no ORDER BY health_score DESC"},
    {"q": "Which furnaces need attention?", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < (SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data) GROUP BY furnace_no ORDER BY avg_oee ASC LIMIT 5"},
    {"q": "How is equipment performing overall?", "sql": "SELECT AVG(oee_percentage) as overall_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, COUNT(*) as total_records FROM kpi_overall_equipment_efficiency_data WHERE date >= CURRENT_DATE - INTERVAL '7 days'"},
    {"q": "Which areas have efficiency problems?", "sql": "SELECT machine_id, furnace_no, AVG(oee_percentage) as avg_oee, COUNT(*) as record_count FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < 80 GROUP BY machine_id, furnace_no ORDER BY avg_oee ASC LIMIT 5"},
    {"q": "Show me the best performing furnaces", "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC LIMIT 5"},
    {"q": "What caused low OEE on Jan 8?", "sql": "SELECT machine_id, shift_id, furnace_no, AVG(oee_percentage) as avg_oee, COUNT(*) as record_count FROM kpi_overall_equipment_efficiency_data WHERE date = '2024-01-08' GROUP BY machine_id, shift_id, furnace_no ORDER BY avg_oee ASC LIMIT 10"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 30: DEFECT RATE (10)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average defect rate?", "sql": "SELECT AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data"},
    {"q": "Show defect rate for furnace 1", "sql": "SELECT date, shift_id, defect_rate FROM kpi_defect_rate_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100"},
    {"q": "Which furnace has highest defect rate?", "sql": "SELECT furnace_no, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY furnace_no ORDER BY avg_defect_rate DESC LIMIT 1"},
    {"q": "Show defect rate by shift", "sql": "SELECT shift_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY shift_id ORDER BY avg_defect_rate DESC"},
    {"q": "Show defect rate trend last 30 days", "sql": "SELECT date, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC"},
    {"q": "Which products have high defect rates?", "sql": "SELECT product_type_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY product_type_id ORDER BY avg_defect_rate DESC LIMIT 5"},
    {"q": "Show defect rate above 5 percent", "sql": "SELECT date, shift_id, furnace_no, defect_rate FROM kpi_defect_rate_data WHERE defect_rate > 5 ORDER BY defect_rate DESC LIMIT 100"},
    {"q": "Compare defect rate between shifts 4 and 12", "sql": "SELECT shift_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data WHERE shift_id IN ('4', '12') GROUP BY shift_id"},
    {"q": "Show quality issues by machine", "sql": "SELECT machine_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY machine_id ORDER BY avg_defect_rate DESC"},
    {"q": "Show defect rate statistics", "sql": "SELECT MIN(defect_rate) as min_defect, MAX(defect_rate) as max_defect, AVG(defect_rate) as avg_defect, STDDEV(defect_rate) as stddev_defect FROM kpi_defect_rate_data"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 31: ENERGY EFFICIENCY (10)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average energy efficiency?", "sql": "SELECT AVG(energy_efficiency) as avg_energy_efficiency FROM kpi_energy_efficiency_data"},
    {"q": "Show energy efficiency for furnace 1", "sql": "SELECT date, shift_id, energy_efficiency FROM kpi_energy_efficiency_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100"},
    {"q": "Which furnace is most energy efficient?", "sql": "SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency ASC LIMIT 1"},
    {"q": "Show energy efficiency by shift", "sql": "SELECT shift_id, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency"},
    {"q": "Show energy efficiency trend", "sql": "SELECT date, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Compare energy efficiency between furnaces", "sql": "SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency, MIN(energy_efficiency) as min_eff, MAX(energy_efficiency) as max_eff FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency"},
    {"q": "Which machines have poor energy efficiency?", "sql": "SELECT machine_id, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY machine_id ORDER BY avg_efficiency DESC LIMIT 5"},
    {"q": "Show energy efficiency by product type", "sql": "SELECT product_type_id, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY product_type_id ORDER BY avg_efficiency"},
    {"q": "Show energy efficiency above threshold", "sql": "SELECT date, furnace_no, energy_efficiency FROM kpi_energy_efficiency_data WHERE energy_efficiency > 500 ORDER BY energy_efficiency DESC LIMIT 100"},
    {"q": "Show kwh per ton statistics", "sql": "SELECT MIN(energy_efficiency) as min_kwh, MAX(energy_efficiency) as max_kwh, AVG(energy_efficiency) as avg_kwh FROM kpi_energy_efficiency_data"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 32: ENERGY USED (10)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the total energy used?", "sql": "SELECT SUM(energy_used) as total_energy_used FROM kpi_energy_used_data"},
    {"q": "Show Total energy consumption by furnace", "sql": "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total_energy DESC"},
    {"q": "Show energy used today", "sql": "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data WHERE date = CURRENT_DATE GROUP BY furnace_no"},
    {"q": "Show daily energy consumption", "sql": "SELECT date, SUM(energy_used) as daily_energy FROM kpi_energy_used_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show energy used by shift", "sql": "SELECT shift_id, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY shift_id ORDER BY total_energy DESC"},
    {"q": "Show monthly energy consumption", "sql": "SELECT DATE_TRUNC('month', date)::DATE as month, SUM(energy_used) as monthly_energy FROM kpi_energy_used_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC"},
    {"q": "Which machine uses most energy?", "sql": "SELECT machine_id, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY machine_id ORDER BY total_energy DESC LIMIT 1"},
    {"q": "Show energy consumption last 7 days", "sql": "SELECT date, SUM(energy_used) as daily_total FROM kpi_energy_used_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date ORDER BY date"},
    {"q": "Compare energy used between furnaces", "sql": "SELECT furnace_no, SUM(energy_used) as total, AVG(energy_used) as avg_per_record FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total DESC"},
    {"q": "Show high energy consumption events", "sql": "SELECT date, shift_id, furnace_no, energy_used FROM kpi_energy_used_data WHERE energy_used > (SELECT AVG(energy_used) + STDDEV(energy_used) FROM kpi_energy_used_data) ORDER BY energy_used DESC LIMIT 50"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 33: DOWNTIME (10)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the total downtime?", "sql": "SELECT SUM(downtime_hours) as total_downtime FROM kpi_downtime_data"},
    {"q": "Show Total downtime by furnace", "sql": "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC"},
    {"q": "Show downtime today", "sql": "SELECT furnace_no, SUM(downtime_hours) as downtime FROM kpi_downtime_data WHERE date = CURRENT_DATE GROUP BY furnace_no"},
    {"q": "Show daily downtime trend", "sql": "SELECT date, SUM(downtime_hours) as daily_downtime FROM kpi_downtime_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show downtime by shift", "sql": "SELECT shift_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY shift_id ORDER BY total_downtime DESC"},
    {"q": "Which machine has most downtime?", "sql": "SELECT machine_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY machine_id ORDER BY total_downtime DESC LIMIT 1"},
    {"q": "Show downtime last week", "sql": "SELECT date, furnace_no, SUM(downtime_hours) as downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date, furnace_no ORDER BY date DESC"},
    {"q": "What is the average downtime per day", "sql": "SELECT date, AVG(downtime_hours) as avg_downtime FROM kpi_downtime_data GROUP BY date ORDER BY date DESC"},
    {"q": "Show furnaces with high downtime", "sql": "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no HAVING SUM(downtime_hours) > 10 ORDER BY total_downtime DESC"},
    {"q": "Compare downtime across workshops", "sql": "SELECT workshop_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY workshop_id ORDER BY total_downtime DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 34: MTBF - MEAN TIME BETWEEN FAILURES (8)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average MTBF?", "sql": "SELECT AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data"},
    {"q": "Show mtbf by furnace", "sql": "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC"},
    {"q": "Which furnace is most reliable?", "sql": "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC LIMIT 1"},
    {"q": "Show mtbf trend last 30 days", "sql": "SELECT date, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC"},
    {"q": "Show mtbf by machine", "sql": "SELECT machine_id, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY machine_id ORDER BY avg_mtbf DESC"},
    {"q": "Show low reliability furnaces", "sql": "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no HAVING AVG(mtbf_hours) < 50 ORDER BY avg_mtbf"},
    {"q": "Show mtbf by shift", "sql": "SELECT shift_id, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY shift_id ORDER BY avg_mtbf DESC"},
    {"q": "Show reliability statistics", "sql": "SELECT MIN(mtbf_hours) as min_mtbf, MAX(mtbf_hours) as max_mtbf, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 35: MTTR - MEAN TIME TO REPAIR (8)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average MTTR?", "sql": "SELECT AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data"},
    {"q": "Show mttr by furnace", "sql": "SELECT furnace_no, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY furnace_no ORDER BY avg_mttr DESC"},
    {"q": "Which furnace takes longest to repair?", "sql": "SELECT furnace_no, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY furnace_no ORDER BY avg_mttr DESC LIMIT 1"},
    {"q": "Show mttr trend", "sql": "SELECT date, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show repair time by machine", "sql": "SELECT machine_id, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY machine_id ORDER BY avg_mttr DESC"},
    {"q": "Show high repair time incidents", "sql": "SELECT date, furnace_no, mttr_hours FROM kpi_mean_time_to_repair_data WHERE mttr_hours > 4 ORDER BY mttr_hours DESC LIMIT 50"},
    {"q": "Show mttr by shift", "sql": "SELECT shift_id, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY shift_id ORDER BY avg_mttr"},
    {"q": "Show repair time statistics", "sql": "SELECT MIN(mttr_hours) as min_mttr, MAX(mttr_hours) as max_mttr, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 36: MTBS - MEAN TIME BETWEEN STOPPAGES (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average MTBS?", "sql": "SELECT AVG(mtbs_hours) as avg_mtbs FROM kpi_mean_time_between_stoppages_data"},
    {"q": "Show mtbs by furnace", "sql": "SELECT furnace_no, AVG(mtbs_hours) as avg_mtbs FROM kpi_mean_time_between_stoppages_data GROUP BY furnace_no ORDER BY avg_mtbs DESC"},
    {"q": "Which furnace has least stoppages?", "sql": "SELECT furnace_no, AVG(mtbs_hours) as avg_mtbs FROM kpi_mean_time_between_stoppages_data GROUP BY furnace_no ORDER BY avg_mtbs DESC LIMIT 1"},
    {"q": "Show mtbs trend", "sql": "SELECT date, AVG(mtbs_hours) as avg_mtbs FROM kpi_mean_time_between_stoppages_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show mtbs by machine", "sql": "SELECT machine_id, AVG(mtbs_hours) as avg_mtbs FROM kpi_mean_time_between_stoppages_data GROUP BY machine_id ORDER BY avg_mtbs DESC"},
    {"q": "Show stoppage frequency statistics", "sql": "SELECT MIN(mtbs_hours) as min_mtbs, MAX(mtbs_hours) as max_mtbs, AVG(mtbs_hours) as avg_mtbs FROM kpi_mean_time_between_stoppages_data"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 37: YIELD (10)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average yield?", "sql": "SELECT AVG(yield_percentage) as avg_yield FROM kpi_yield_data"},
    {"q": "Show yield by furnace", "sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC"},
    {"q": "Which furnace has best yield?", "sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC LIMIT 1"},
    {"q": "Show yield trend last 30 days", "sql": "SELECT date, AVG(yield_percentage) as avg_yield FROM kpi_yield_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC"},
    {"q": "Show yield by shift", "sql": "SELECT shift_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY shift_id ORDER BY avg_yield DESC"},
    {"q": "Show low yield records", "sql": "SELECT date, shift_id, furnace_no, yield_percentage FROM kpi_yield_data WHERE yield_percentage < 85 ORDER BY yield_percentage ASC LIMIT 100"},
    {"q": "Show yield by product type", "sql": "SELECT product_type_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY product_type_id ORDER BY avg_yield DESC"},
    {"q": "Compare yield between furnaces", "sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield, MIN(yield_percentage) as min_yield, MAX(yield_percentage) as max_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC"},
    {"q": "Show daily yield summary", "sql": "SELECT date, AVG(yield_percentage) as avg_yield, COUNT(*) as records FROM kpi_yield_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show yield statistics by furnace", "sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield, STDDEV(yield_percentage) as stddev_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 38: FIRST PASS YIELD (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average first pass yield?", "sql": "SELECT AVG(first_pass_yield) as avg_fpy FROM kpi_first_pass_yield_data"},
    {"q": "Show first pass yield by furnace", "sql": "SELECT furnace_no, AVG(first_pass_yield) as avg_fpy FROM kpi_first_pass_yield_data GROUP BY furnace_no ORDER BY avg_fpy DESC"},
    {"q": "Show fpy trend", "sql": "SELECT date, AVG(first_pass_yield) as avg_fpy FROM kpi_first_pass_yield_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show low fpy records", "sql": "SELECT date, furnace_no, first_pass_yield FROM kpi_first_pass_yield_data WHERE first_pass_yield < 90 ORDER BY first_pass_yield ASC LIMIT 50"},
    {"q": "Show first pass yield by shift", "sql": "SELECT shift_id, AVG(first_pass_yield) as avg_fpy FROM kpi_first_pass_yield_data GROUP BY shift_id ORDER BY avg_fpy DESC"},
    {"q": "Show fpy by product", "sql": "SELECT product_type_id, AVG(first_pass_yield) as avg_fpy FROM kpi_first_pass_yield_data GROUP BY product_type_id ORDER BY avg_fpy DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 39: REWORK RATE (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average rework rate?", "sql": "SELECT AVG(rework_rate_percentage) as avg_rework FROM kpi_rework_rate_data"},
    {"q": "Show rework rate by furnace", "sql": "SELECT furnace_no, AVG(rework_rate_percentage) as avg_rework FROM kpi_rework_rate_data GROUP BY furnace_no ORDER BY avg_rework DESC"},
    {"q": "Show high rework rate records", "sql": "SELECT date, furnace_no, rework_rate_percentage FROM kpi_rework_rate_data WHERE rework_rate_percentage > 5 ORDER BY rework_rate_percentage DESC LIMIT 50"},
    {"q": "Show rework rate trend", "sql": "SELECT date, AVG(rework_rate_percentage) as avg_rework FROM kpi_rework_rate_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show rework by shift", "sql": "SELECT shift_id, AVG(rework_rate_percentage) as avg_rework FROM kpi_rework_rate_data GROUP BY shift_id ORDER BY avg_rework DESC"},
    {"q": "Which product has highest rework?", "sql": "SELECT product_type_id, AVG(rework_rate_percentage) as avg_rework FROM kpi_rework_rate_data GROUP BY product_type_id ORDER BY avg_rework DESC LIMIT 1"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 40: CAPACITY UTILIZATION (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average capacity utilization?", "sql": "SELECT AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data"},
    {"q": "Show capacity utilization by furnace", "sql": "SELECT furnace_no, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY furnace_no ORDER BY avg_utilization DESC"},
    {"q": "Show low utilization furnaces", "sql": "SELECT furnace_no, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY furnace_no HAVING AVG(utilization_percentage) < 70 ORDER BY avg_utilization"},
    {"q": "Show utilization trend", "sql": "SELECT date, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show utilization by shift", "sql": "SELECT shift_id, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY shift_id ORDER BY avg_utilization DESC"},
    {"q": "Show machine utilization", "sql": "SELECT machine_id, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY machine_id ORDER BY avg_utilization DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 41: QUANTITY PRODUCED (8)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the total quantity produced?", "sql": "SELECT SUM(quantity_produced) as total_quantity FROM kpi_quantity_produced_data"},
    {"q": "Show production by furnace", "sql": "SELECT furnace_no, SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_production DESC"},
    {"q": "Show daily production", "sql": "SELECT date, SUM(quantity_produced) as daily_production FROM kpi_quantity_produced_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show production by shift", "sql": "SELECT shift_id, SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data GROUP BY shift_id ORDER BY total_production DESC"},
    {"q": "Show production by product type", "sql": "SELECT product_type_id, SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data GROUP BY product_type_id ORDER BY total_production DESC"},
    {"q": "Show top producing furnaces", "sql": "SELECT furnace_no, SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_production DESC LIMIT 5"},
    {"q": "Show monthly production", "sql": "SELECT DATE_TRUNC('month', date)::DATE as month, SUM(quantity_produced) as monthly_production FROM kpi_quantity_produced_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC"},
    {"q": "Show production trend last week", "sql": "SELECT date, SUM(quantity_produced) as daily_production FROM kpi_quantity_produced_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date ORDER BY date"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 42: OUTPUT RATE (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average output rate?", "sql": "SELECT AVG(output_rate_percentage) as avg_output_rate FROM kpi_output_rate_data"},
    {"q": "Show output rate by furnace", "sql": "SELECT furnace_no, AVG(output_rate_percentage) as avg_output_rate FROM kpi_output_rate_data GROUP BY furnace_no ORDER BY avg_output_rate DESC"},
    {"q": "Show output rate trend", "sql": "SELECT date, AVG(output_rate_percentage) as avg_output_rate FROM kpi_output_rate_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show low output rate records", "sql": "SELECT date, furnace_no, output_rate_percentage FROM kpi_output_rate_data WHERE output_rate_percentage < 80 ORDER BY output_rate_percentage ASC LIMIT 50"},
    {"q": "Show output rate by shift", "sql": "SELECT shift_id, AVG(output_rate_percentage) as avg_output_rate FROM kpi_output_rate_data GROUP BY shift_id ORDER BY avg_output_rate DESC"},
    {"q": "Show best output rate by machine", "sql": "SELECT machine_id, AVG(output_rate_percentage) as avg_output_rate FROM kpi_output_rate_data GROUP BY machine_id ORDER BY avg_output_rate DESC LIMIT 5"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 43: PRODUCTION EFFICIENCY (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average production efficiency?", "sql": "SELECT AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data"},
    {"q": "Show production efficiency by furnace", "sql": "SELECT furnace_no, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency DESC"},
    {"q": "Show efficiency trend", "sql": "SELECT date, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show low efficiency records", "sql": "SELECT date, furnace_no, production_efficiency_percentage FROM kpi_production_efficiency_data WHERE production_efficiency_percentage < 75 ORDER BY production_efficiency_percentage ASC LIMIT 50"},
    {"q": "Show efficiency by shift", "sql": "SELECT shift_id, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency DESC"},
    {"q": "Which furnace is most efficient?", "sql": "SELECT furnace_no, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency DESC LIMIT 1"},
    {"q": "What is the production efficiency percentage in July?", "sql": "SELECT AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data WHERE EXTRACT(MONTH FROM date) = 7"},
    {"q": "Show production efficiency in the month of july", "sql": "SELECT AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data WHERE EXTRACT(MONTH FROM date) = 7"},
    {"q": "Show production efficiency for January", "sql": "SELECT AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data WHERE EXTRACT(MONTH FROM date) = 1"},
    {"q": "Show production efficiency percentage by month", "sql": "SELECT EXTRACT(MONTH FROM date) as month, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY EXTRACT(MONTH FROM date) ORDER BY month"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 44: ON-TIME DELIVERY (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average on-time delivery?", "sql": "SELECT AVG(on_time_delivery_percentage) as avg_otd FROM kpi_on_time_delivery_data"},
    {"q": "Show on-time delivery by furnace", "sql": "SELECT furnace_no, AVG(on_time_delivery_percentage) as avg_otd FROM kpi_on_time_delivery_data GROUP BY furnace_no ORDER BY avg_otd DESC"},
    {"q": "Show otd trend", "sql": "SELECT date, AVG(on_time_delivery_percentage) as avg_otd FROM kpi_on_time_delivery_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show low otd records", "sql": "SELECT date, furnace_no, on_time_delivery_percentage FROM kpi_on_time_delivery_data WHERE on_time_delivery_percentage < 90 ORDER BY on_time_delivery_percentage ASC LIMIT 50"},
    {"q": "Show delivery performance by shift", "sql": "SELECT shift_id, AVG(on_time_delivery_percentage) as avg_otd FROM kpi_on_time_delivery_data GROUP BY shift_id ORDER BY avg_otd DESC"},
    {"q": "What is the best delivery performance", "sql": "SELECT furnace_no, AVG(on_time_delivery_percentage) as avg_otd FROM kpi_on_time_delivery_data GROUP BY furnace_no ORDER BY avg_otd DESC LIMIT 1"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 45: MAINTENANCE COMPLIANCE (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average maintenance compliance?", "sql": "SELECT AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data"},
    {"q": "Show maintenance compliance by furnace", "sql": "SELECT furnace_no, AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data GROUP BY furnace_no ORDER BY avg_compliance DESC"},
    {"q": "Show compliance trend", "sql": "SELECT date, AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show low compliance records", "sql": "SELECT date, furnace_no, compliance_percentage FROM kpi_maintenance_compliance_data WHERE compliance_percentage < 90 ORDER BY compliance_percentage ASC LIMIT 50"},
    {"q": "Show compliance by shift", "sql": "SELECT shift_id, AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data GROUP BY shift_id ORDER BY avg_compliance DESC"},
    {"q": "Which furnace has best compliance?", "sql": "SELECT furnace_no, AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data GROUP BY furnace_no ORDER BY avg_compliance DESC LIMIT 1"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 46: PLANNED MAINTENANCE (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average planned maintenance?", "sql": "SELECT AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data"},
    {"q": "Show planned maintenance by furnace", "sql": "SELECT furnace_no, AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data GROUP BY furnace_no ORDER BY avg_planned DESC"},
    {"q": "Show planned maintenance trend", "sql": "SELECT date, AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show low planned maintenance", "sql": "SELECT date, furnace_no, planned_maintenance_percentage FROM kpi_planned_maintenance_data WHERE planned_maintenance_percentage < 80 ORDER BY planned_maintenance_percentage ASC LIMIT 50"},
    {"q": "Show scheduled maintenance by shift", "sql": "SELECT shift_id, AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data GROUP BY shift_id ORDER BY avg_planned DESC"},
    {"q": "Show maintenance schedule statistics", "sql": "SELECT MIN(planned_maintenance_percentage) as min_planned, MAX(planned_maintenance_percentage) as max_planned, AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 47: SAFETY INCIDENTS (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the average safety incidents percentage?", "sql": "SELECT AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data"},
    {"q": "Show safety incidents by furnace", "sql": "SELECT furnace_no, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY furnace_no ORDER BY avg_incidents DESC"},
    {"q": "Show safety incidents trend", "sql": "SELECT date, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY date ORDER BY date DESC LIMIT 30"},
    {"q": "Show high incident records", "sql": "SELECT date, furnace_no, incidents_percentage FROM kpi_safety_incidents_reported_data WHERE incidents_percentage > 5 ORDER BY incidents_percentage DESC LIMIT 50"},
    {"q": "Show safety by shift", "sql": "SELECT shift_id, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY shift_id ORDER BY avg_incidents DESC"},
    {"q": "Which area has most incidents?", "sql": "SELECT machine_id, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY machine_id ORDER BY avg_incidents DESC LIMIT 5"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 48: TAP PRODUCTION (10)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the total cast weight?", "sql": "SELECT SUM(cast_weight) as total_cast_weight FROM core_process_tap_production"},
    {"q": "Show cast weight by plant", "sql": "SELECT plant_id, SUM(cast_weight) as total_cast_weight FROM core_process_tap_production GROUP BY plant_id ORDER BY total_cast_weight DESC"},
    {"q": "Show daily tap production", "sql": "SELECT DATE_TRUNC('day', tap_production_datetime)::DATE as production_date, COUNT(DISTINCT tap_id) as tap_count, SUM(cast_weight) as total_weight FROM core_process_tap_production GROUP BY DATE_TRUNC('day', tap_production_datetime) ORDER BY production_date DESC LIMIT 30"},
    {"q": "Show recent tap production", "sql": "SELECT tap_id, cast_weight, liquid_weight, energy, tap_production_datetime FROM core_process_tap_production ORDER BY tap_production_datetime DESC LIMIT 20"},
    {"q": "What is the average energy per tap", "sql": "SELECT AVG(energy) as avg_energy FROM core_process_tap_production"},
    {"q": "Show tap production energy efficiency", "sql": "SELECT AVG(energy_efficiency) as avg_energy_efficiency FROM core_process_tap_production"},
    {"q": "What is the total liquid weight produced", "sql": "SELECT SUM(liquid_weight) as total_liquid_weight FROM core_process_tap_production"},
    {"q": "Show slag weight by plant", "sql": "SELECT plant_id, SUM(casting_slag_weight) as total_slag FROM core_process_tap_production GROUP BY plant_id ORDER BY total_slag DESC"},
    {"q": "Show recycling metal statistics", "sql": "SELECT SUM(recycling_metal_weight) as total_recycled FROM core_process_tap_production"},
    {"q": "Show ladle weight analysis", "sql": "SELECT AVG(ladle_weight_before_tapping) as avg_before, AVG(ladle_weight_after_tapping) as avg_after FROM core_process_tap_production"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 49: TAP PROCESS (8)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "How many taps today?", "sql": "SELECT COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process WHERE DATE(tap_datetime) = CURRENT_DATE"},
    {"q": "Show taps by furnace", "sql": "SELECT furnace_no, COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process GROUP BY furnace_no ORDER BY tap_count DESC"},
    {"q": "Show tap status summary", "sql": "SELECT tap_status, COUNT(*) as count FROM core_process_tap_process GROUP BY tap_status ORDER BY count DESC"},
    {"q": "Show recent tap processes", "sql": "SELECT tap_id, furnace_no, tap_datetime, tap_status, tap_progress FROM core_process_tap_process ORDER BY tap_datetime DESC LIMIT 20"},
    {"q": "Show tap progress distribution", "sql": "SELECT tap_progress, COUNT(*) as count FROM core_process_tap_process GROUP BY tap_progress ORDER BY count DESC"},
    {"q": "Show taps by tap hole", "sql": "SELECT tap_hole_id, COUNT(*) as tap_count FROM core_process_tap_process GROUP BY tap_hole_id ORDER BY tap_count DESC"},
    {"q": "Show target materials used", "sql": "SELECT target_material, COUNT(*) as count FROM core_process_tap_process GROUP BY target_material ORDER BY count DESC"},
    {"q": "Show daily tap count trend", "sql": "SELECT DATE_TRUNC('day', tap_datetime)::DATE as tap_date, COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process GROUP BY DATE_TRUNC('day', tap_datetime) ORDER BY tap_date DESC LIMIT 30"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 50: TAP GRADING (6)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "Show all allocated grades", "sql": "SELECT allocated_grade, COUNT(*) as count FROM core_process_tap_grading GROUP BY allocated_grade ORDER BY count DESC"},
    {"q": "Show grade quality distribution", "sql": "SELECT allocated_grade_quality, COUNT(*) as count FROM core_process_tap_grading GROUP BY allocated_grade_quality ORDER BY count DESC"},
    {"q": "Show grade priority breakdown", "sql": "SELECT allocated_grade_priority, COUNT(*) as count FROM core_process_tap_grading GROUP BY allocated_grade_priority ORDER BY count DESC"},
    {"q": "Show grading by cast process", "sql": "SELECT cast_process_code, COUNT(*) as count FROM core_process_tap_grading GROUP BY cast_process_code ORDER BY count DESC"},
    {"q": "Show bulk pile allocations", "sql": "SELECT allocated_grade_bulk_pile, COUNT(*) as count FROM core_process_tap_grading GROUP BY allocated_grade_bulk_pile ORDER BY count DESC"},
    {"q": "Show recent grading records", "sql": "SELECT tap_id, allocated_grade, allocated_grade_quality, allocated_grade_priority FROM core_process_tap_grading ORDER BY id DESC LIMIT 50"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 51: DOWNTIME EVENTS LOG (10)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "What is the total downtime from events", "sql": "SELECT SUM(downtime_hours) as total_downtime FROM log_book_furnace_down_time_event"},
    {"q": "Show downtime events by furnace", "sql": "SELECT furnace_no, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY furnace_no ORDER BY total_downtime DESC"},
    {"q": "Show recent downtime events", "sql": "SELECT furnace_no, obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event ORDER BY obs_start_dt DESC LIMIT 20"},
    {"q": "Show downtime by reason", "sql": "SELECT reason_id, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY reason_id ORDER BY total_downtime DESC"},
    {"q": "Show downtime by type", "sql": "SELECT downtime_type_id, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY downtime_type_id ORDER BY total_downtime DESC"},
    {"q": "Show long downtime events", "sql": "SELECT furnace_no, obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE downtime_hours > 4 ORDER BY downtime_hours DESC LIMIT 50"},
    {"q": "Show downtime events last 7 days", "sql": "SELECT furnace_no, obs_start_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE obs_start_dt >= CURRENT_DATE - INTERVAL '7 days' ORDER BY obs_start_dt DESC"},
    {"q": "Show daily downtime event summary", "sql": "SELECT DATE_TRUNC('day', obs_start_dt)::DATE as event_date, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY DATE_TRUNC('day', obs_start_dt) ORDER BY event_date DESC LIMIT 30"},
    {"q": "Show downtime by equipment", "sql": "SELECT equipment_id, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY equipment_id ORDER BY total_downtime DESC"},
    {"q": "Show downtime events by plant", "sql": "SELECT plant_id, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY plant_id ORDER BY total_downtime DESC"},

    # ═══════════════════════════════════════════════════════════════════
    # TYPE 52: FURNACE CONFIG & MASTER DATA (8)
    # ═══════════════════════════════════════════════════════════════════
    {"q": "List all furnaces", "sql": "SELECT furnace_no, furnace_description, is_active FROM furnace_furnaceconfig ORDER BY furnace_no"},
    {"q": "Show active furnaces", "sql": "SELECT furnace_no, furnace_description FROM furnace_furnaceconfig WHERE is_active = true ORDER BY furnace_no"},
    {"q": "Show furnaces by workshop", "sql": "SELECT workshop_id, COUNT(*) as furnace_count FROM furnace_furnaceconfig GROUP BY workshop_id ORDER BY furnace_count DESC"},
    {"q": "Show furnace configuration parameters", "sql": "SELECT furnace_config_id, crucible_diameter, crucible_depth, target_energy_efficiency FROM furnace_config_parameters ORDER BY furnace_config_id"},
    {"q": "Show all plants", "sql": "SELECT id, plant_code, plant_name FROM plant_plant ORDER BY id"},
    {"q": "Show downtime reasons list", "sql": "SELECT id, reason_name, reason_code FROM log_book_reasons ORDER BY id"},
    {"q": "Show downtime types list", "sql": "SELECT id, name, down_time_type_code FROM log_book_downtime_type_master ORDER BY id"},
    {"q": "Show furnace energy targets", "sql": "SELECT furnace_config_id, target_energy_efficiency, target_availability, target_furnace_load FROM furnace_config_parameters ORDER BY furnace_config_id"},
]

# ============================================================
# ORIGINAL EXAMPLES (PRESERVED AS COMMENTS)
# ============================================================
# The following examples were the original set before enhancement.
# Kept for reference and rollback purposes.
# ============================================================

# ORIGINAL_FEW_SHOT_EXAMPLES = [
#     # ========== SIMPLE AGGREGATIONS ==========
#     {"q": "What is the average oee for furnace 1 last month",
#      "sql": "SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1 AND date >= CURRENT_DATE - INTERVAL '30 days'"},
#     
#     {"q": "Show Total downtime by furnace",
#      "sql": "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC"},
#     
#     {"q": "Which furnace has highest OEE?",
#      "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC LIMIT 1"},
#     
#     {"q": "What is furnace health", 
#      "sql": "SELECT furnace_no, AVG(oee_percentage) as health_score FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY health_score DESC"},
#     
#     {"q": "Compare OEE by furnace", 
#      "sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC"},
#     
#     {"q": "What is the average yield for Furnace 2?", 
#      "sql": "SELECT AVG(yield_percentage) FROM kpi_yield_data WHERE furnace_no = 2"},
#     
#     {"q": "What is the total downtime for furnace 1 last 30 days", 
#      "sql": "SELECT SUM(downtime_hours) FROM kpi_downtime_data WHERE furnace_no = 1 AND date >= CURRENT_DATE - INTERVAL '30 days'"},
#     
#     {"q": "What is the total downtime last year", 
#      "sql": "SELECT SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '1 year'"},
#     
#     {"q": "What is the total energy used last week", 
#      "sql": "SELECT furnace_no, SUM(energy_used) as total FROM kpi_energy_used_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY furnace_no"},
#     
#     {"q": "Show Average MTBF by furnace", 
#      "sql": "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no"},
#     
#     {"q": "What is the total production for furnace 1 in january 2025", 
#      "sql": "SELECT SUM(cast_weight) as total_production FROM core_process_tap_production WHERE tap_production_datetime BETWEEN '2025-01-01' AND '2025-01-31'"},
#     
#     # ========== TREND QUERIES (NO AGGREGATION) ==========
#     {"q": "Show OEE trend for Furnace 2",
#      "sql": "SELECT date, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 2 ORDER BY date DESC LIMIT 100"},
#     
#     {"q": "Show recent tap production",
#      "sql": "SELECT tap_id, cast_weight, energy, tap_production_datetime FROM core_process_tap_production ORDER BY tap_production_datetime DESC LIMIT 20"},
#     
#     {"q": "Show OEE trend last week", 
#      "sql": "SELECT date, furnace_no, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' ORDER BY date DESC"},
#     
#     {"q": "Show defect rate trend for furnace 2", 
#      "sql": "SELECT date, defect_rate FROM kpi_defect_rate_data WHERE furnace_no = 2 ORDER BY date DESC LIMIT 100"},
#     
#     {"q": "Show yield data for last month", 
#      "sql": "SELECT date, furnace_no, yield_percentage FROM kpi_yield_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC"},
#     
#     {"q": "List all furnaces", 
#      "sql": "SELECT furnace_no, furnace_description, is_active FROM furnace_furnaceconfig ORDER BY furnace_no"},
#     
#     {"q": "Show downtime events for Furnace 1", 
#      "sql": "SELECT obs_start_dt, obs_end_dt, downtime_hours, reason_id FROM log_book_furnace_down_time_event WHERE furnace_no = 1 ORDER BY obs_start_dt DESC LIMIT 50"},
#     
#     {"q": "Show crucible diameter and depth for furnace 1", 
#      "sql": "SELECT crucible_diameter, crucible_depth FROM furnace_config_parameters WHERE furnace_config_id = 1"},
#     
#     {"q": "Show MTTR data for Furnace 2", 
#      "sql": "SELECT date, mttr_hours FROM kpi_mean_time_to_repair_data WHERE furnace_no = 2 ORDER BY date DESC LIMIT 100"},
#     
#     {"q": "Show all downtime reasons", 
#      "sql": "SELECT reason_name, reason_code FROM log_book_reasons"},
#     
#     {"q": "Show downtime types", 
#      "sql": "SELECT name, down_time_type_code FROM log_book_downtime_type_master"},
#     
#     # ========== MULTI-TABLE JOINs ==========
#     {"q": "Show Average OEE by furnace with furnace names",
#      "sql": "SELECT f.furnace_no, f.furnace_description, AVG(k.oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data k JOIN furnace_furnaceconfig f ON k.furnace_no = f.furnace_no GROUP BY f.furnace_no, f.furnace_description ORDER BY avg_oee DESC"},
#     
#     {"q": "Show tap production by plant and furnace",
#      "sql": "SELECT p.plant_name, f.furnace_no, f.furnace_description, COUNT(t.tap_id) as total_taps, SUM(tp.cast_weight) as total_weight FROM core_process_tap_production tp JOIN core_process_tap_process t ON tp.tap_id = t.tap_id JOIN furnace_furnaceconfig f ON t.furnace_no = f.furnace_no JOIN plant_plant p ON tp.plant_id = p.id GROUP BY p.id, p.plant_name, f.furnace_no, f.furnace_description ORDER BY total_weight DESC"},
#     
#     {"q": "Show downtime events with reasons for furnace 1",
#      "sql": "SELECT d.obs_start_dt, d.obs_end_dt, d.downtime_hours, r.reason_name, dt.name as downtime_type FROM log_book_furnace_down_time_event d LEFT JOIN log_book_reasons r ON d.reason_id = r.id LEFT JOIN log_book_downtime_type_master dt ON d.downtime_type_id = dt.id WHERE d.furnace_no = 1 ORDER BY d.obs_start_dt DESC LIMIT 50"},
#     
#     {"q": "Compare OEE and yield by furnace last month",
#      "sql": "SELECT f.furnace_no, f.furnace_description, AVG(k1.oee_percentage) as avg_oee, AVG(k2.yield_percentage) as avg_yield FROM kpi_overall_equipment_efficiency_data k1 JOIN kpi_yield_data k2 ON k1.furnace_no = k2.furnace_no AND k1.date = k2.date JOIN furnace_furnaceconfig f ON k1.furnace_no = f.furnace_no WHERE k1.date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY f.furnace_no, f.furnace_description ORDER BY avg_oee DESC"},
#     
#     {"q": "Show oee by plant",
#      "sql": "SELECT p.plant_name, AVG(k.oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data k JOIN plant_plant p ON k.plant_id = p.id GROUP BY p.id, p.plant_name ORDER BY avg_oee DESC"},
#     
#     {"q": "Show production with furnace details",
#      "sql": "SELECT f.furnace_no, f.furnace_description, SUM(tp.cast_weight) as total_weight, AVG(tp.energy_efficiency) as avg_efficiency FROM core_process_tap_production tp JOIN core_process_tap_process t ON tp.tap_id = t.tap_id JOIN furnace_furnaceconfig f ON t.furnace_no = f.furnace_no GROUP BY f.furnace_no, f.furnace_description ORDER BY total_weight DESC"},
#     
#     # ========== AGGREGATION OVERRIDE EXAMPLES ==========
#     {"q": "What is the total oee for furnace 1 last month", 
#      "sql": "SELECT SUM(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1 AND date >= CURRENT_DATE - INTERVAL '30 days'"},
#     
#     {"q": "What is the average downtime per furnace", 
#      "sql": "SELECT furnace_no, AVG(downtime_hours) FROM kpi_downtime_data GROUP BY furnace_no"},
#     
#     {"q": "Show Average and total energy used by furnace", 
#      "sql": "SELECT furnace_no, AVG(energy_used) as avg_energy, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no"},
#     
#     {"q": "How many downtime events for Furnace 1", 
#      "sql": "SELECT COUNT(*) FROM kpi_downtime_data WHERE furnace_no = 1"},
#     
#     {"q": "What is the total and average yield for furnace 2 in january", 
#      "sql": "SELECT SUM(yield_percentage) as total_yield, AVG(yield_percentage) as avg_yield FROM kpi_yield_data WHERE furnace_no = 2 AND date BETWEEN '2025-01-01' AND '2025-01-31'"},
#     
#     # ========== VARCHAR COLUMN EXAMPLES ==========
#     {"q": "Show oee for shift 4",
#      "sql": "SELECT date, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE shift_id = '4' ORDER BY date DESC LIMIT 100"},
#     
#     {"q": "Compare downtime between shifts 4, 12, and 20",
#      "sql": "SELECT shift_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE shift_id IN ('4', '12', '20') GROUP BY shift_id ORDER BY total_downtime DESC"},
#     
#     {"q": "Which shift has highest yield",
#      "sql": "SELECT shift_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY shift_id ORDER BY avg_yield DESC LIMIT 1"},
#     
#     {"q": "Show oee for machine furnace",
#      "sql": "SELECT date, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE machine_id = 'FURNACE' ORDER BY date DESC LIMIT 100"},
#     
#     {"q": "Compare downtime between FURNACE and ELECTROD machines",
#      "sql": "SELECT machine_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE machine_id IN ('FURNACE', 'ELECTROD') GROUP BY machine_id ORDER BY total_downtime DESC"},
#     
#     {"q": "Show oee for product m004",
#      "sql": "SELECT date, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE product_type_id = 'M004' ORDER BY date DESC LIMIT 100"},
#     
#     {"q": "Compare yield between MET30 and MET32",
#      "sql": "SELECT product_type_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data WHERE product_type_id IN ('MET30', 'MET32') GROUP BY product_type_id ORDER BY avg_yield DESC"},
#     
#     # ========== GENERIC KPI QUERY PATTERNS ==========
#     {"q": "What is the average oee per day",
#      "sql": "SELECT date, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date ORDER BY date DESC"},
#     
#     {"q": "Show OEE records above 90",
#      "sql": "SELECT date, shift_id, furnace_no, machine_id, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage > 90 ORDER BY oee_percentage DESC LIMIT 100"},
#     
#     {"q": "Show highest oee recorded",
#      "sql": "SELECT date, shift_id, furnace_no, machine_id, oee_percentage FROM kpi_overall_equipment_efficiency_data ORDER BY oee_percentage DESC LIMIT 1"},
#     
#     {"q": "Show min, max, and average oee",
#      "sql": "SELECT MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data"},
#     
#     {"q": "Show oee on 2024-01-07",
#      "sql": "SELECT shift_id, furnace_no, machine_id, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE date = '2024-01-07' ORDER BY oee_percentage DESC"},
#     
#     # ========== ERROR EXAMPLES ==========
#     {"q": "Show production",
#      "sql": "ERROR: Ambiguous query. Please specify metric (e.g., quantity produced, production efficiency, tap production)."},
#     
#     {"q": "Show oee and downtime comparison",
#      "sql": "ERROR: Multi-metric queries not yet supported. Please ask one metric at a time."},
#     
#     {"q": "What happened yesterday", 
#      "sql": "ERROR: Cannot map question to a specific table. Please specify what data you need (e.g., OEE, downtime, production)."},
# ]


def find_best_table(question: str) -> Optional[str]:
    """Find best matching table based on question keywords."""
    question_lower = question.lower()

    best_match = None
    best_score = 0

    for table_name, info in TABLE_SCHEMA.items():
        score = 0
        for keyword in info.get("keywords", []):
            if keyword in question_lower:
                score += len(keyword)  # Longer matches score higher

        if score > best_score:
            best_score = score
            best_match = table_name

    return best_match


def find_best_table_filtered(question: str, schema: Dict) -> Optional[str]:
    """Find best matching table from filtered schema based on question keywords."""
    question_lower = question.lower()

    best_match = None
    best_score = 0

    for table_name, info in schema.items():
        score = 0
        for keyword in info.get("keywords", []):
            if keyword in question_lower:
                score += len(keyword)  # Longer matches score higher

        if score > best_score:
            best_score = score
            best_match = table_name

    return best_match


def resolve_aggregation(question: str, table_name: str) -> str:
    """
    Resolve user-requested aggregation, override table default if needed.
    
    Priority:
    1. USER EXPLICIT: "average/total/count" in question → Use that
    2. Table default: AVG/SUM/COUNT → Fallback
    """
    question_lower = question.lower()
    
    # Check for NO aggregation keywords (trend/list/show/recent)
    no_agg_keywords = ["trend", "list", "show", "recent", "details", "all"]
    for kw in no_agg_keywords:
        if kw in question_lower and "total" not in question_lower and "average" not in question_lower:
            return "NONE"  # Signal: no aggregation needed
    
    # User explicit keywords (HIGHEST priority)
    if "average" in question_lower or "avg" in question_lower or "mean" in question_lower:
        return "AVG"
    elif "total" in question_lower or "sum" in question_lower:
        return "SUM"
    elif "count" in question_lower or "how many" in question_lower:
        return "COUNT"
    
    # Table default (fallback)
    return TABLE_SCHEMA.get(table_name, {}).get("aggregation", "AVG")


def build_prompt_with_schema(
    schema_dict: Dict,
    question: str,
    allowed_tables: List[str] = None
) -> str:
    """
    Build enhanced prompt with schema analysis and JOIN support (v3.0).

    Args:
        schema_dict: Complete TABLE_SCHEMA mapping
        question: User's natural language question
        allowed_tables: Optional RBAC whitelist - if provided, filter TABLE_SCHEMA

    Returns:
        Production-ready prompt for LLM
    """

    # ════════════════════════════════════════════════════════
    # RBAC: Filter TABLE_SCHEMA to allowed tables only
    # ════════════════════════════════════════════════════════
    working_schema = TABLE_SCHEMA
    if allowed_tables:
        allowed_set = set(allowed_tables)
        working_schema = {
            table: info
            for table, info in TABLE_SCHEMA.items()
            if table in allowed_set
        }
        logger.info(f"🔐 RBAC: Schema filtered to {len(working_schema)}/{len(TABLE_SCHEMA)} tables")

    # Find best matching table from FILTERED schema
    best_table = find_best_table_filtered(question, working_schema)
    table_hint = ""

    if best_table and best_table in working_schema:
        info = working_schema[best_table]
        user_aggregation = resolve_aggregation(question, best_table)
        table_default = info['aggregation']

        # Build aggregation hint
        if user_aggregation == "NONE":
            agg_hint = "NO AGGREGATION - return raw rows with LIMIT and ORDER BY date"
        elif user_aggregation != table_default:
            agg_hint = f"USER REQUESTED: {user_aggregation}() ← PRIORITY! (overrides default {table_default})"
        else:
            agg_hint = f"Use {user_aggregation}() for aggregation"

        # Get live columns from schema_dict if available
        display_columns = info['columns']
        if schema_dict and best_table in schema_dict:
            live_table = schema_dict[best_table]
            if hasattr(live_table, 'columns'):
                display_columns = [c.name for c in live_table.columns]

        table_hint = f"""
HINT FOR THIS QUERY:
─ Best matching table: {best_table}
─ Description: {info.get('description', 'N/A')}
─ Value column: {info.get('value_column', 'N/A')}
─ Aggregation: {agg_hint}
─ Date column: {info.get('date_column', 'date')}
─ Columns available: {', '.join(display_columns[:15])}...
─ Filter by 'furnace_no' (INTEGER) - DO NOT use '_id' suffix unless explicitly in columns
─ IMPORTANT: User-requested aggregation OVERRIDES table default!
"""

    # Build TRIMMED schema text - only top 5 candidate tables from FILTERED schema
    # This reduces noise and helps model focus on the hint
    schema_text = "\nRELEVANT TABLES (candidates):\n"

    # Get top 5 tables by keyword match score from filtered schema
    question_lower = question.lower()
    table_scores = []
    for table_name, info in working_schema.items():
        score = sum(len(kw) for kw in info.get("keywords", []) if kw in question_lower)
        table_scores.append((table_name, info, score))
    
    # Sort by score descending, take top 5
    table_scores.sort(key=lambda x: x[2], reverse=True)
    top_tables = table_scores[:5]
    
    for table_name, info, score in top_tables:
        # Get live columns from schema_dict if available
        cols_list = info["columns"]
        if schema_dict and table_name in schema_dict:
            live_table = schema_dict[table_name]
            if hasattr(live_table, 'columns'):
                cols_list = [c.name for c in live_table.columns]
                
        cols = ", ".join(cols_list[:12])
        schema_text += f"  • {table_name}: {cols}...\n"
    
    # Build few-shot examples (use more examples for better learning)
    examples = "\n\n".join([f"Q: {ex['q']}\nSQL: {ex['sql']}" for ex in FEW_SHOT_EXAMPLES[:15]])
    
    return f"""{SYSTEM_PROMPT}
{table_hint}

{schema_text}

EXAMPLES (Learn from these patterns):
{examples}

User Question: {question}

SQL Query (ONLY valid PostgreSQL, no explanations):"""


# Alias for v3.0 API compatibility
build_prompt_with_schema_and_joins = build_prompt_with_schema


def build_prompt_debug(schema_dict: Dict, question: str, failed_sql: str) -> str:
    """Build a debug prompt when previous SQL failed validation."""
    best_table = find_best_table(question)
    info = TABLE_SCHEMA.get(best_table, {})
    
    return f"""{SYSTEM_PROMPT}

PREVIOUS SQL HAD ERRORS:
{failed_sql}

ISSUES TO FIX:
- Verify table exists in schema
- Verify column names are correct
- Use 'furnace_no' not 'furnace_id' for filtering
- Use correct date column for the table

CORRECT TABLE: {best_table or 'unknown'}
CORRECT COLUMNS: {', '.join(info.get('columns', [])[:10])}
DATE COLUMN: {info.get('date_column', 'date')}
VALUE COLUMN: {info.get('value_column', 'unknown')}

Question: {question}

CORRECTED SQL:"""


# Legacy compatibility
def get_sql_generation_prompt(schema_context: str) -> str:
    """Legacy function."""
    return SYSTEM_PROMPT + f"\n\nSCHEMA:\n{schema_context}"


def get_few_shot_prompt() -> str:
    """Legacy function."""
    return "\n\n".join([f"Q: {ex['q']}\nSQL: {ex['sql']}" for ex in FEW_SHOT_EXAMPLES])


RESPONSE_FORMAT_PROMPT = """Summarize the query results briefly and factually.

Question: {question}
SQL: {sql}
Results: {results}

RULES:
1. Use ONLY the numeric values and column names present in Results.
2. Include appropriate units (%, hours, kg, etc.).
3. Be concise - 1-2 sentences maximum.
4. DO NOT guess reasons, causes, or explanations not present in the data.
5. DO NOT make recommendations unless explicitly asked.
6. If Results is empty, say "No data found for this query."
"""
