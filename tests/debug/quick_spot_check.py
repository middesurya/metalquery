#!/usr/bin/env python3
"""Quick spot check of key query patterns."""
import requests
import time

NLP_SERVICE_URL = "http://localhost:8003"

ALLOWED_TABLES = [
    "kpi_downtime_data", "kpi_safety_incidents_reported_data",
    "kpi_overall_equipment_efficiency_data", "kpi_yield_data",
    "kpi_energy_used_data", "kpi_cycle_time_data"
]

# Key patterns to spot-check
SPOT_CHECKS = [
    ("Safety (was 0%)", "What is the average safety incidents percentage?"),
    ("Safety by furnace", "Show safety incidents by furnace"),
    ("Downtime (was 50%)", "Show downtime by furnace"),
    ("Downtime variant", "What is the downtime by furnace?"),
    ("OEE control", "Show OEE by furnace"),
    ("Cycle Time", "Show Average cycle time by furnace"),
]

def test_query(label, question):
    """Test a single query."""
    try:
        response = requests.post(
            f"{NLP_SERVICE_URL}/api/v1/chat",
            json={"question": question, "allowed_tables": ALLOWED_TABLES},
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                sql = data.get("sql", "")
                graph = data.get("graph_type", "")
                conf = data.get("confidence", 0)

                # Check routing by looking at the table in SQL
                routed_to_sql = bool(sql and any(table in sql.lower() for table in ALLOWED_TABLES))

                print(f"\nPASS: {label}")
                print(f"  Q: {question}")
                print(f"  Routed to: {'SQL' if routed_to_sql else 'Unknown'}")
                print(f"  SQL: {sql[:120]}...")
                print(f"  Graph: {graph}")
                print(f"  Confidence: {conf:.0%}")
                return True
            else:
                error = data.get("error", "Unknown")
                print(f"\nFAIL: {label}")
                print(f"  Q: {question}")
                print(f"  Error: {error[:100]}")
                return False
        else:
            print(f"\n✗ {label}")
            print(f"  Q: {question}")
            print(f"  HTTP Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"\n✗ {label}")
        print(f"  Q: {question}")
        print(f"  Exception: {str(e)[:100]}")
        return False

print("=" * 80)
print("QUICK SPOT CHECK - Key Query Patterns")
print("=" * 80)

success_count = 0
for label, question in SPOT_CHECKS:
    if test_query(label, question):
        success_count += 1
    time.sleep(3)  # Brief delay between queries

print("\n" + "=" * 80)
print(f"RESULTS: {success_count}/{len(SPOT_CHECKS)} queries successful")
print("=" * 80)
