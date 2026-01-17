#!/usr/bin/env python3
"""Quick spot-check test - 10 key queries"""
import requests
import json

# Test 10 representative queries
TESTS = [
    ("OEE", "What is the average oee for all furnaces", "KPI Card"),
    ("OEE", "Show Average OEE by furnace", "Bar Chart"),
    ("Energy", "What is the total energy used?", "KPI Card"),
    ("Energy", "Show energy consumption by furnace", "Bar Chart"),
    ("Yield", "Show yield by shift", "Bar Chart"),
    ("Downtime", "What is the average downtime per furnace", "Line Chart"),
    ("Cycle Time", "What is the average cycle time overall?", "KPI Card"),
    ("Safety", "What is the average safety incidents percentage?", "KPI Card"),
    ("MTBF", "What is the average MTBF?", "KPI Card"),
    ("Tap", "Show tap status summary", "Bar Chart"),
]

def test(cat, q, exp):
    """Test one query."""
    try:
        r = requests.post("http://localhost:8003/api/v1/chat", json={"question": q}, timeout=20)
        d = r.json()

        sql_ok = d.get('success') and len(d.get('sql', '')) > 0
        chart_config = d.get('chart_config') or {}
        graph = chart_config.get('chart_type', '').lower() if chart_config else ''

        # Normalize
        if 'kpi' in graph or 'progress' in graph or 'metric' in graph:
            graph_norm = "KPI Card"
        elif 'bar' in graph:
            graph_norm = "Bar Chart"
        elif 'line' in graph or 'area' in graph:
            graph_norm = "Line Chart"
        elif 'table' in graph:
            graph_norm = "Table"
        else:
            graph_norm = graph if graph else "Unknown"

        match = graph_norm == exp
        status = "[PASS]" if (sql_ok and match) else "[WARN]" if sql_ok else "[FAIL]"

        print(f"{status} {cat}: {q[:50]}")
        if not match and sql_ok:
            print(f"       Graph: Expected '{exp}', Got '{graph_norm}'")
        if not sql_ok:
            print(f"       SQL: Failed to generate")

        return sql_ok, match
    except Exception as e:
        print(f"[ERROR] {cat}: {q[:50]} - {str(e)}")
        return False, False

print("=" * 70)
print("QUICK VALIDATION TEST (10 queries)")
print("=" * 70 + "\n")

passed = 0
total = len(TESTS)

for cat, q, exp in TESTS:
    sql_ok, match = test(cat, q, exp)
    if sql_ok and match:
        passed += 1

print("\n" + "=" * 70)
print(f"RESULT: {passed}/{total} passed ({passed/total*100:.0f}%)")
print("=" * 70)
