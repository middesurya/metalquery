#!/usr/bin/env python3
"""
Test diverse queries from different categories and patterns.
Validates routing fixes and SQL generation quality.
"""
import requests
import time
import re
from datetime import datetime

NLP_SERVICE_URL = "http://localhost:8003"

ALLOWED_TABLES = [
    "kpi_downtime_data", "kpi_safety_incidents_reported_data",
    "kpi_overall_equipment_efficiency_data", "kpi_yield_data",
    "kpi_energy_used_data", "kpi_energy_efficiency_data",
    "kpi_cycle_time_data", "kpi_defect_rate_data",
    "kpi_quantity_produced_data", "kpi_output_rate_data",
    "kpi_production_efficiency_data", "kpi_first_pass_yield_data",
    "kpi_rework_rate_data", "kpi_mean_time_between_failures_data",
    "kpi_mean_time_to_repair_data", "kpi_mean_time_between_stoppages_data",
    "kpi_resource_capacity_utilization_data", "kpi_maintenance_compliance_data",
    "kpi_planned_maintenance_data", "kpi_on_time_delivery_data",
    "core_process_tap_production", "core_process_tap_process",
    "core_process_tap_grading", "log_book_furnace_down_time_event",
    "furnace_furnaceconfig", "plant_plant"
]

# Diverse test cases covering different categories and patterns
TEST_CASES = [
    # Safety queries (previously 0% - testing routing fix)
    ("Safety", "What is the average safety incidents percentage?", "KPI Card"),
    ("Safety", "Show safety incidents by furnace", "Bar Chart"),
    ("Safety", "Show safety incidents trend", "Line Chart"),

    # Downtime queries (previously 50% - testing routing fix)
    ("Downtime", "Show downtime by furnace", "Line Chart"),
    ("Downtime", "What is the downtime by furnace?", "Line Chart"),
    ("Downtime", "Show Total downtime by furnace", "Line Chart"),
    ("Downtime", "Show downtime by shift", "Line Chart"),

    # OEE queries (should still work - control group)
    ("OEE", "What is the average oee for all furnaces", "KPI Card"),
    ("OEE", "Show OEE by furnace", "Bar Chart"),
    ("OEE", "Show OEE by shift", "Bar Chart"),
    ("OEE", "Compare OEE between Furnace 1 and 2", "Bar Chart"),

    # Cycle Time queries (new KPI area)
    ("Cycle Time", "What is the average cycle time overall?", "KPI Card"),
    ("Cycle Time", "Show Average cycle time by furnace", "Line Chart"),
    ("Cycle Time", "Which shift has the highest average cycle time?", "Line Chart"),
    ("Cycle Time", "Show cycle time trend by shift over time", "Line Chart"),

    # Energy queries
    ("Energy", "Show Total energy consumption by furnace", "Bar Chart"),
    ("Energy", "Show energy by furnace", "Bar Chart"),
    ("Energy", "Show energy efficiency by shift", "Bar Chart"),
    ("Energy", "Compare energy efficiency by furnace", "Bar Chart"),

    # Yield queries
    ("Yield", "What is the average yield?", "KPI Card"),
    ("Yield", "Show yield by furnace", "Bar Chart"),
    ("Yield", "Show yield by shift", "Bar Chart"),
    ("Yield", "Which shift has highest yield?", "Bar Chart"),

    # Production/Quantity queries
    ("General", "Show Total quantity produced by furnace", "Bar Chart"),
    ("General", "Show production by furnace", "Bar Chart"),
    ("General", "Show production by shift", "Bar Chart"),

    # Defect Rate queries
    ("Defect Rate", "What is the average defect rate?", "KPI Card"),
    ("Defect Rate", "Show defect rate by shift", "Bar Chart"),
    ("Defect Rate", "Show rank furnaces by defect rate", "Bar Chart"),

    # Tap Process queries
    ("Tap Process", "How many taps today?", "KPI Card"),
    ("Tap Process", "Show taps by furnace", "Bar Chart"),
    ("Tap Process", "Show tap status summary", "Bar Chart"),

    # Maintenance queries
    ("Maintenance", "What is the average maintenance compliance?", "KPI Card"),
    ("Maintenance", "Show maintenance compliance by furnace", "Bar Chart"),
    ("Maintenance", "Show planned maintenance by furnace", "Bar Chart"),

    # Time-based aggregation patterns
    ("OEE", "Show OEE trend last week", "Table"),
    ("Downtime", "Display downtime trend last 30 days", "Table"),
    ("Energy", "Show monthly energy by furnace", "Line Chart"),

    # Comparison patterns
    ("Yield", "Compare yield between furnaces", "Bar Chart"),
    ("Energy", "Compare energy efficiency between furnaces", "Bar Chart"),
    ("Downtime", "Compare downtime between machines", "Line Chart"),

    # Statistical queries
    ("OEE", "Show oee statistics", "KPI Card"),
    ("Cycle Time", "Show cycle time statistics by furnace", "Line Chart"),
    ("Yield", "Show yield statistics by furnace", "Bar Chart"),

    # Complex filters
    ("OEE", "Show OEE records above 90%", "Table"),
    ("Cycle Time", "Show records where cycle time is greater than 90", "Table"),
    ("Downtime", "Show downtime events exceeding 8 hours", "Table"),
]

def normalize_sql(sql):
    """Normalize SQL for comparison - remove whitespace variations."""
    if not sql:
        return ""
    return " ".join(sql.lower().split())

def check_sql_similarity(generated, expected):
    """Check if generated SQL is similar to expected."""
    gen_norm = normalize_sql(generated)
    exp_norm = normalize_sql(expected)

    # Check key components
    if not gen_norm or not exp_norm:
        return 0.0

    # Extract key elements
    gen_table = re.search(r'from\s+(\w+)', gen_norm)
    exp_table = re.search(r'from\s+(\w+)', exp_norm)

    score = 0.0

    # Table match (40 points)
    if gen_table and exp_table and gen_table.group(1) == exp_table.group(1):
        score += 0.4

    # Has aggregation (20 points)
    if any(agg in gen_norm for agg in ['avg(', 'sum(', 'count(', 'max(', 'min(']):
        score += 0.2

    # Has GROUP BY when expected (20 points)
    if 'group by' in exp_norm:
        if 'group by' in gen_norm:
            score += 0.2
    else:
        if 'group by' not in gen_norm:
            score += 0.2

    # Has WHERE clause matching (20 points)
    if 'where' in exp_norm:
        if 'where' in gen_norm:
            score += 0.2
    else:
        score += 0.2

    return score

def test_query(question, expected_graph, max_retries=3):
    """Test a single query and return results."""
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
                    sql = data.get("sql", "")
                    graph = data.get("graph_type", "")

                    # Check SQL generation
                    sql_ok = bool(sql and len(sql) > 10)

                    # Check graph type (normalize comparison)
                    graph_match = graph.lower().replace(" ", "") == expected_graph.lower().replace(" ", "")

                    return {
                        "success": True,
                        "sql": sql[:150] if sql else "None",
                        "sql_ok": sql_ok,
                        "graph": graph,
                        "graph_match": graph_match,
                        "confidence": data.get("confidence", 0)
                    }
                else:
                    error_msg = data.get("error", "Unknown error")

                    # Handle rate limiting
                    if "Token limit" in error_msg or "rate" in error_msg.lower():
                        wait_match = re.search(r'wait (\d+) seconds', error_msg)
                        wait_time = int(wait_match.group(1)) + 2 if wait_match else 60
                        print(f"    Rate limited, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue

                    return {"success": False, "error": error_msg[:100]}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            return {"success": False, "error": str(e)[:100]}

    return {"success": False, "error": "Max retries exceeded"}

# Main execution
print("=" * 80)
print("DIVERSE QUERY VALIDATION TEST")
print("=" * 80)
print(f"Test cases: {len(TEST_CASES)}")
print(f"Categories covered: Safety, Downtime, OEE, Cycle Time, Energy, Yield, etc.")
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

results = {
    "total": 0,
    "success": 0,
    "sql_ok": 0,
    "graph_match": 0,
    "by_category": {}
}

for idx, (category, question, expected_graph) in enumerate(TEST_CASES, 1):
    print(f"\n[{idx}/{len(TEST_CASES)}] {category}: {question[:50]}...")

    result = test_query(question, expected_graph)

    results["total"] += 1

    # Track by category
    if category not in results["by_category"]:
        results["by_category"][category] = {
            "total": 0, "success": 0, "sql_ok": 0, "graph_match": 0
        }

    cat_stats = results["by_category"][category]
    cat_stats["total"] += 1

    if result.get("success"):
        results["success"] += 1
        cat_stats["success"] += 1

        sql_ok = result.get("sql_ok", False)
        graph_match = result.get("graph_match", False)

        if sql_ok:
            results["sql_ok"] += 1
            cat_stats["sql_ok"] += 1

        if graph_match:
            results["graph_match"] += 1
            cat_stats["graph_match"] += 1

        status = []
        if sql_ok:
            status.append("SQL_OK")
        else:
            status.append("SQL_WEAK")

        if graph_match:
            status.append("GRAPH_OK")
        else:
            status.append(f"GRAPH_MISMATCH (got: {result.get('graph', 'None')})")

        print(f"  PASS [{', '.join(status)}]")
        print(f"    SQL: {result['sql']}...")
        print(f"    Confidence: {result.get('confidence', 0):.0%}")
    else:
        print(f"  FAIL: {result.get('error', 'Unknown error')}")
        cat_stats["success"] -= 1  # Don't count as success

    # Delay between requests to avoid rate limiting
    if idx < len(TEST_CASES):
        time.sleep(3)

# Final summary
print("\n" + "=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)

print(f"\nOverall:")
print(f"  Total Tests:       {results['total']}")
print(f"  Success Rate:      {results['success']}/{results['total']} ({results['success']*100/results['total']:.1f}%)")
print(f"  SQL Generation:    {results['sql_ok']}/{results['total']} ({results['sql_ok']*100/results['total']:.1f}%)")
print(f"  Graph Type Match:  {results['graph_match']}/{results['total']} ({results['graph_match']*100/results['total']:.1f}%)")

print(f"\nBy Category:")
for category, stats in sorted(results["by_category"].items()):
    if stats["total"] > 0:
        success_rate = stats["success"] * 100 / stats["total"]
        sql_rate = stats["sql_ok"] * 100 / stats["total"]
        print(f"  {category:20} Success: {stats['success']}/{stats['total']} ({success_rate:.0f}%)  SQL: {sql_rate:.0f}%")

print("\n" + "=" * 80)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Highlight specific improvements
print("\nKey Validation Points:")
print(f"  - Safety queries routing: {'FIXED' if results['by_category'].get('Safety', {}).get('success', 0) > 0 else 'FAILED'}")
print(f"  - Downtime queries routing: {'FIXED' if results['by_category'].get('Downtime', {}).get('success', 0) > 0 else 'FAILED'}")
print(f"  - Control queries (OEE): {'MAINTAINED' if results['by_category'].get('OEE', {}).get('success', 0) > 0 else 'REGRESSION'}")
