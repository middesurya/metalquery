#!/usr/bin/env python3
"""Debug the 3 failed queries to understand the issues."""

import requests
import json
import time

NLP_SERVICE_URL = "http://localhost:8003"

FAILED_QUERIES = [
    {
        "question": "Show downtime by furnace",
        "expected_sql": "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC",
        "expected_graph": "Line Chart"
    },
    {
        "question": "Show taps by furnace",
        "expected_sql": "SELECT furnace_no, COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process GROUP BY furnace_no ORDER BY tap_count DESC",
        "expected_graph": "Bar Chart"
    },
    {
        "question": "What is the average safety incidents percentage?",
        "expected_sql": "SELECT AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data",
        "expected_graph": "KPI Card"
    }
]

ALLOWED_TABLES = [
    "kpi_overall_equipment_efficiency_data", "kpi_downtime_data", "kpi_energy_used_data",
    "kpi_energy_efficiency_data", "kpi_yield_data", "kpi_defect_rate_data", "kpi_cycle_time_data",
    "kpi_quantity_produced_data", "kpi_production_efficiency_data", "kpi_output_rate_data",
    "kpi_mean_time_between_failures_data", "kpi_mean_time_to_repair_data",
    "kpi_mean_time_between_stoppages_data", "kpi_resource_capacity_utilization_data",
    "kpi_on_time_delivery_data", "kpi_maintenance_compliance_data", "kpi_planned_maintenance_data",
    "kpi_safety_incidents_reported_data", "kpi_first_pass_yield_data", "kpi_rework_rate_data",
    "core_process_tap_production", "core_process_tap_process", "core_process_tap_grading",
    "log_book_furnace_down_time_event", "furnace_furnaceconfig", "plant_plant"
]

def test_query(question, max_retries=3):
    """Test a single query and return full response."""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{NLP_SERVICE_URL}/api/v1/chat",
                json={"question": question, "allowed_tables": ALLOWED_TABLES},
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {
                        "success": True,
                        "sql": data.get("sql"),
                        "sources": data.get("sources"),
                        "confidence": data.get("confidence_score")
                    }
                else:
                    error = data.get("error", "Unknown")
                    if "Token limit" in error:
                        import re
                        wait_match = re.search(r'wait (\d+) seconds', error)
                        wait_time = int(wait_match.group(1)) + 2 if wait_match else 60
                        print(f"  Rate limited, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    return {"success": False, "error": error}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    return {"success": False, "error": "Max retries exceeded"}

def main():
    print("=" * 70)
    print("DEBUGGING FAILED QUERIES")
    print("=" * 70)

    for i, query in enumerate(FAILED_QUERIES):
        print(f"\n{'='*70}")
        print(f"QUERY {i+1}: {query['question']}")
        print("=" * 70)

        print(f"\nExpected SQL:")
        print(f"  {query['expected_sql']}")
        print(f"\nExpected Graph: {query['expected_graph']}")

        print(f"\nTesting...")
        result = test_query(query['question'])

        if result.get("success"):
            print(f"\nActual SQL Generated:")
            print(f"  {result['sql']}")
            print(f"\nTables Used: {result.get('sources')}")
            print(f"Confidence: {result.get('confidence')}")

            # Compare
            expected_upper = query['expected_sql'].upper()
            actual_upper = (result['sql'] or "").upper()

            # Check key differences
            print(f"\nAnalysis:")

            # Same table?
            import re
            exp_table = re.search(r'FROM\s+(\w+)', expected_upper)
            act_table = re.search(r'FROM\s+(\w+)', actual_upper)
            if exp_table and act_table:
                print(f"  Expected table: {exp_table.group(1)}")
                print(f"  Actual table: {act_table.group(1)}")
                print(f"  Tables match: {exp_table.group(1) == act_table.group(1)}")

            # Same aggregation?
            exp_has_sum = "SUM(" in expected_upper
            act_has_sum = "SUM(" in actual_upper
            exp_has_count = "COUNT(" in expected_upper
            act_has_count = "COUNT(" in actual_upper
            exp_has_avg = "AVG(" in expected_upper
            act_has_avg = "AVG(" in actual_upper

            print(f"  Expected SUM: {exp_has_sum}, Actual SUM: {act_has_sum}")
            print(f"  Expected COUNT: {exp_has_count}, Actual COUNT: {act_has_count}")
            print(f"  Expected AVG: {exp_has_avg}, Actual AVG: {act_has_avg}")

            # Group by?
            exp_group = "GROUP BY" in expected_upper
            act_group = "GROUP BY" in actual_upper
            print(f"  Expected GROUP BY: {exp_group}, Actual GROUP BY: {act_group}")

        else:
            print(f"\nERROR: {result.get('error')}")

        # Wait before next query
        if i < len(FAILED_QUERIES) - 1:
            print("\nWaiting 5s before next query...")
            time.sleep(5)

    print("\n" + "=" * 70)
    print("DEBUG COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
