"""
exposed_tables.py - IGNIS Database Whitelist (29 Tables)
Only the tables approved for NLP-to-SQL queries.
"""

# ============================================================
# TABLE WHITELIST (29 Tables)
# ============================================================

EXPOSED_TABLES = {
    # ==================== KPI TABLES (20) ====================
    "kpi_overall_equipment_efficiency_data",
    "kpi_defect_rate_data",
    "kpi_energy_efficiency_data",
    "kpi_energy_used_data",
    "kpi_downtime_data",
    "kpi_mean_time_between_failures_data",
    "kpi_mean_time_to_repair_data",
    "kpi_mean_time_between_stoppages_data",
    "kpi_yield_data",
    "kpi_first_pass_yield_data",
    "kpi_rework_rate_data",
    "kpi_resource_capacity_utilization_data",
    "kpi_quantity_produced_data",
    "kpi_output_rate_data",
    "kpi_production_efficiency_data",
    "kpi_on_time_delivery_data",
    "kpi_cycle_time_data",
    "kpi_maintenance_compliance_data",
    "kpi_planned_maintenance_data",
    "kpi_safety_incidents_reported_data",
    
    # ==================== CORE PROCESS TABLES (3) ====================
    "core_process_tap_production",
    "core_process_tap_process",
    "core_process_tap_grading",
    
    # ==================== LOG BOOK TABLES (1) ====================
    "log_book_furnace_down_time_event",
    
    # ==================== FURNACE TABLES (2) ====================
    "furnace_config_parameters",
    "furnace_furnaceconfig",  # This is the 'furnace' table
    
    # ==================== MASTER TABLES (3) ====================
    "plant_plant",  # Plant master
    "log_book_reasons",  # down_time_reason
    "log_book_downtime_type_master",  # down_time_type
}

# ============================================================
# TABLE DESCRIPTIONS FOR LLM CONTEXT
# ============================================================

TABLE_DESCRIPTIONS = {
    # KPI Tables
    "kpi_overall_equipment_efficiency_data": "OEE percentage (furnace health) by furnace and date. Columns: record_id, date, shift_id, oee_percentage, furnace_no, machine_id, plant_id, workshop_id",
    "kpi_defect_rate_data": "Defect rate percentage. Columns: record_id, date, shift_id, defect_rate, furnace_no, machine_id, plant_id",
    "kpi_energy_efficiency_data": "Energy efficiency (kWh/ton). Columns: record_id, date, shift_id, energy_efficiency, furnace_no, machine_id, plant_id",
    "kpi_energy_used_data": "Total energy consumed (kWh). Columns: record_id, date, shift_id, energy_used, furnace_no, machine_id, plant_id",
    "kpi_downtime_data": "Downtime hours. Columns: record_id, date, shift_id, downtime_hours, furnace_no, machine_id, plant_id",
    "kpi_mean_time_between_failures_data": "MTBF hours. Columns: record_id, date, shift_id, mtbf_hours, furnace_no, machine_id, plant_id",
    "kpi_mean_time_to_repair_data": "MTTR hours. Columns: record_id, date, shift_id, mttr_hours, furnace_no, machine_id, plant_id",
    "kpi_mean_time_between_stoppages_data": "MTBS hours. Columns: record_id, date, shift_id, mtbs_hours, furnace_no, machine_id, plant_id",
    "kpi_yield_data": "Yield percentage. Columns: record_id, date, shift_id, yield_percentage, furnace_no, machine_id, plant_id",
    "kpi_first_pass_yield_data": "First pass yield. Columns: record_id, date, shift_id, first_pass_yield, furnace_no, machine_id, plant_id",
    "kpi_rework_rate_data": "Rework rate percentage. Columns: record_id, date, shift_id, rework_rate_percentage, furnace_no, machine_id, plant_id",
    "kpi_resource_capacity_utilization_data": "Capacity utilization. Columns: record_id, date, shift_id, utilization_percentage, furnace_no, machine_id, plant_id",
    "kpi_quantity_produced_data": "Quantity produced. Columns: record_id, date, shift_id, quantity_produced, furnace_no, machine_id, plant_id",
    "kpi_output_rate_data": "Output rate. Columns: record_id, date, shift_id, output_rate_percentage, furnace_no, machine_id, plant_id",
    "kpi_production_efficiency_data": "Production efficiency. Columns: record_id, date, shift_id, production_efficiency_percentage, furnace_no, machine_id, plant_id",
    "kpi_on_time_delivery_data": "On-time delivery. Columns: record_id, date, shift_id, on_time_delivery_percentage, furnace_no, machine_id, plant_id",
    "kpi_cycle_time_data": "Cycle time. Columns: record_id, date, shift_id, cycle_time, furnace_no, machine_id, plant_id",
    "kpi_maintenance_compliance_data": "Maintenance compliance. Columns: record_id, date, shift_id, compliance_percentage, furnace_no, machine_id, plant_id",
    "kpi_planned_maintenance_data": "Planned maintenance. Columns: record_id, date, shift_id, planned_maintenance_percentage, furnace_no, machine_id, plant_id",
    "kpi_safety_incidents_reported_data": "Safety incidents. Columns: record_id, date, shift_id, incidents_percentage, furnace_no, machine_id, plant_id",
    
    # Core Process Tables
    "core_process_tap_production": "Tap production with cast weights. Columns: id, tap_id, furnace_no (via tap_process), tap_production_datetime, cast_weight, liquid_weight, energy, energy_efficiency, ladle_number_code, plant_id",
    "core_process_tap_process": "Tap process status. Columns: id, tap_id, furnace_no, tap_datetime, tap_progress, tap_status, tap_hole_id, target_material, plant_id",
    "core_process_tap_grading": "Tap grading with allocated grades. Columns: id, tap_id, allocated_grade, allocated_grade_quality, allocated_grade_priority, allocated_grade_bulk_pile, plant_id",
    
    # Log Book Tables
    "log_book_furnace_down_time_event": "Furnace downtime events. Columns: id, furnace_no, obs_start_dt, obs_end_dt, downtime_hours, equipment_id, reason_id, downtime_type_id, plant_id",
    
    # Furnace Tables
    "furnace_config_parameters": "Furnace configuration. Columns: id, furnace_config_id, effective_date, crucible_diameter, crucible_depth, energy_losses, target_energy_efficiency, target_availability, target_furnace_load, plant_id",
    "furnace_furnaceconfig": "Furnace master. Columns: id, furnace_no, furnace_description, is_active, workshop_id, plant_id, cost_center_id",
    
    # Master Tables
    "plant_plant": "Plant master. Columns: id, plant_code, plant_name",
    "log_book_reasons": "Downtime reasons. Columns: id, reason_name, reason_code",
    "log_book_downtime_type_master": "Downtime types. Columns: id, name, down_time_type_code",
}

# ============================================================
# KPI COLUMN MAPPINGS (keyword -> table, column)
# ============================================================

KPI_COLUMN_MAPPINGS = {
    # Performance KPIs
    "oee": ("kpi_overall_equipment_efficiency_data", "oee_percentage"),
    "health": ("kpi_overall_equipment_efficiency_data", "oee_percentage"),
    "efficiency": ("kpi_overall_equipment_efficiency_data", "oee_percentage"),
    "yield": ("kpi_yield_data", "yield_percentage"),
    "defect": ("kpi_defect_rate_data", "defect_rate"),
    "production_efficiency": ("kpi_production_efficiency_data", "production_efficiency_percentage"),
    "output": ("kpi_output_rate_data", "output_rate_percentage"),
    "quantity": ("kpi_quantity_produced_data", "quantity_produced"),
    "cycle_time": ("kpi_cycle_time_data", "cycle_time"),
    "first_pass": ("kpi_first_pass_yield_data", "first_pass_yield"),
    "rework": ("kpi_rework_rate_data", "rework_rate_percentage"),
    
    # Maintenance KPIs
    "downtime": ("kpi_downtime_data", "downtime_hours"),
    "mtbf": ("kpi_mean_time_between_failures_data", "mtbf_hours"),
    "mttr": ("kpi_mean_time_to_repair_data", "mttr_hours"),
    "mtbs": ("kpi_mean_time_between_stoppages_data", "mtbs_hours"),
    "maintenance_compliance": ("kpi_maintenance_compliance_data", "compliance_percentage"),
    "planned_maintenance": ("kpi_planned_maintenance_data", "planned_maintenance_percentage"),
    
    # Energy KPIs
    "energy_efficiency": ("kpi_energy_efficiency_data", "energy_efficiency"),
    "energy_used": ("kpi_energy_used_data", "energy_used"),
    "energy": ("kpi_energy_used_data", "energy_used"),
    
    # Safety & Compliance KPIs
    "safety": ("kpi_safety_incidents_reported_data", "incidents_percentage"),
    "incidents": ("kpi_safety_incidents_reported_data", "incidents_percentage"),
    
    # Capacity & Delivery KPIs
    "capacity": ("kpi_resource_capacity_utilization_data", "utilization_percentage"),
    "utilization": ("kpi_resource_capacity_utilization_data", "utilization_percentage"),
    "delivery": ("kpi_on_time_delivery_data", "on_time_delivery_percentage"),
    
    # Production Tables
    "tap": ("core_process_tap_production", "cast_weight"),
    "production": ("core_process_tap_production", "cast_weight"),
    "cast_weight": ("core_process_tap_production", "cast_weight"),
    "liquid_weight": ("core_process_tap_production", "liquid_weight"),
    
    # Furnace Config
    "crucible": ("furnace_config_parameters", "crucible_diameter"),
    "config": ("furnace_config_parameters", "effective_date"),
    "furnace": ("furnace_furnaceconfig", "furnace_no"),
}

# ============================================================
# AGGREGATION RULES
# ============================================================

AGGREGATION_RULES = {
    # Use AVG for percentages
    "oee_percentage": "AVG",
    "yield_percentage": "AVG",
    "defect_rate": "AVG",
    "energy_efficiency": "AVG",
    "compliance_percentage": "AVG",
    "incidents_percentage": "AVG",
    "utilization_percentage": "AVG",
    "on_time_delivery_percentage": "AVG",
    "production_efficiency_percentage": "AVG",
    "output_rate_percentage": "AVG",
    "first_pass_yield": "AVG",
    "rework_rate_percentage": "AVG",
    "planned_maintenance_percentage": "AVG",
    
    # Use SUM for quantities
    "downtime_hours": "SUM",
    "energy_used": "SUM",
    "quantity_produced": "SUM",
    "cast_weight": "SUM",
    "liquid_weight": "SUM",
    "energy": "SUM",
    
    # Use AVG for hours/time metrics
    "mtbf_hours": "AVG",
    "mttr_hours": "AVG",
    "mtbs_hours": "AVG",
    "cycle_time": "AVG",
}

# ============================================================
# DATE COLUMNS PER TABLE TYPE
# ============================================================

DATE_COLUMNS = {
    "kpi_": "date",
    "core_process_tap_production": "tap_production_datetime",
    "core_process_tap_process": "tap_datetime",
    "furnace_config_parameters": "effective_date",
    "log_book_furnace_down_time_event": "obs_start_dt",
    "default": "created_at",
}


def get_date_column(table_name: str) -> str:
    """Get the appropriate date column for a table."""
    for prefix, column in DATE_COLUMNS.items():
        if table_name.startswith(prefix) or table_name == prefix:
            return column
    return DATE_COLUMNS["default"]


def get_aggregation(column_name: str) -> str:
    """Get recommended aggregation function for a column."""
    return AGGREGATION_RULES.get(column_name, "AVG")


def is_exposed_table(table_name: str) -> bool:
    """Check if a table is in the exposed whitelist."""
    return table_name.lower() in EXPOSED_TABLES
