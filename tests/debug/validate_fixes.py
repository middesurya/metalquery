#!/usr/bin/env python3
"""Quick validation of routing fixes."""

import requests
import time

NLP_SERVICE_URL = "http://localhost:8003"

# Test queries that were problematic
VALIDATION_QUERIES = [
    # Safety queries (were 0% before fix)
    ("What is the average safety incidents percentage?", "safety"),
    ("Show safety incidents by furnace", "safety"),

    # Downtime patterns (were 50% before fix)
    ("Show downtime by furnace", "downtime"),
    ("What is the downtime by furnace?", "downtime"),
    ("Show total downtime by furnace", "downtime"),

    # Control queries (should still work)
    ("What is the total downtime?", "downtime"),
    ("Show OEE by furnace", "oee"),
    ("What is the average yield?", "yield"),
]

ALLOWED_TABLES = [
    "kpi_downtime_data", "kpi_safety_incidents_reported_data",
    "kpi_overall_equipment_efficiency_data", "kpi_yield_data"
]

def test_query(question):
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
                return {"success": True, "sql": sql[:100] if sql else "None"}
            else:
                return {"success": False, "error": data.get("error", "Unknown")}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)[:50]}

print("=" * 70)
print("VALIDATION TEST - Routing Fixes")
print("=" * 70)

success_count = 0
total = len(VALIDATION_QUERIES)

for question, category in VALIDATION_QUERIES:
    result = test_query(question)

    status = "PASS" if result.get("success") else "FAIL"
    print(f"\n[{status}] {category.upper()}: {question}")

    if result.get("success"):
        print(f"    SQL: {result['sql']}...")
        success_count += 1
    else:
        print(f"    Error: {result.get('error', 'Unknown')}")

    time.sleep(2)

print(f"\n{'=' * 70}")
print(f"VALIDATION RESULTS: {success_count}/{total} ({success_count*100/total:.0f}%)")
print("=" * 70)

if success_count == total:
    print("SUCCESS: All queries passed! Routing fixes successful.")
elif success_count >= total * 0.8:
    print("SUCCESS: Most queries passed! Significant improvement.")
else:
    print("WARNING: Some queries still failing. May need additional tuning.")
