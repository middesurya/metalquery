import os
import django
import sys
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chatbot.views import get_local_schema

def verify_schema():
    try:
        schema = get_local_schema()
        print(f"Generated schema for {len(schema)} tables.")
        
        expected_tables = {
            'kpi_overall_equipment_efficiency_data',
            'kpi_defect_rate_data',
            'kpi_energy_efficiency_data',
            'kpi_downtime_data',
            'kpi_mean_time_between_failures_data',
            'kpi_yield_data',
            'kpi_resource_capacity_utilization_data',
            'kpi_safety_incidents_reported_data',
            'kpi_cycle_time_data',
            'kpi_output_rate_data',
            'kpi_quantity_produced_data',
            'kpi_production_efficiency_data',
            'kpi_on_time_delivery_data',
            'kpi_first_pass_yield_data',
            'kpi_rework_rate_data',
            'kpi_energy_used_data',
            'kpi_maintenance_compliance_data',
            'kpi_mean_time_to_repair_data',
            'kpi_mean_time_between_stoppages_data',
            'kpi_planned_maintenance_data',
            'core_process_tap_process',
            'core_process_tap_production',
            'core_process_tap_grading',
            'furnace_config_parameters',
            'log_book_furnace_down_time_event',
        }
        
        found_tables = set(schema.keys())
        
        missing = expected_tables - found_tables
        unexpected = found_tables - expected_tables
        
        if missing:
            print(f"[FAILED] Missing tables: {missing}")
        elif unexpected:
            print(f"[WARNING] Unexpected tables: {unexpected}")
        else:
            print("[SUCCESS] All 25 expected tables are present in the schema.")
            
        # Print sample field for one table
        sample_table = 'kpi_overall_equipment_efficiency_data'
        if sample_table in schema:
            print(f"\nSample fields for {sample_table}:")
            for col in schema[sample_table]['columns'][:3]:
                print(f" - {col['name']} ({col['type']})")

    except Exception as e:
        print(f"[FAILED] Error generating schema: {e}")

if __name__ == "__main__":
    verify_schema()
