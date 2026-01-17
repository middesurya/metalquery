#!/usr/bin/env python3
"""
Subset Test - 30 diverse queries across all categories
Estimated time: ~30 minutes with rate limiting
"""

import requests
import json
import time
import re
import csv
from datetime import datetime
from typing import Dict, List, Tuple
from difflib import SequenceMatcher

NLP_SERVICE_URL = "http://localhost:8003"

# Diverse subset of 30 test cases across all categories
TEST_CASES = [
    # OEE (5 queries)
    ("OEE", "What is the average oee for all furnaces", "SELECT AVG(oee_percentage) as average_oee FROM kpi_overall_equipment_efficiency_data", "KPI Card"),
    ("OEE", "Show OEE by furnace", "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC", "Bar Chart"),
    ("OEE", "Which furnace has highest OEE?", "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC LIMIT 1", "Bar Chart"),
    ("OEE", "Show OEE trend last week", "SELECT date, furnace_no, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' ORDER BY date DESC", "Table"),
    ("OEE", "Show oee by shift", "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC", "Bar Chart"),

    # Downtime (4 queries)
    ("Downtime", "What is the total downtime?", "SELECT SUM(downtime_hours) as total_downtime FROM kpi_downtime_data", "KPI Card"),
    ("Downtime", "Show downtime by furnace", "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC", "Line Chart"),
    ("Downtime", "Which machine has most downtime?", "SELECT machine_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY machine_id ORDER BY total_downtime DESC LIMIT 1", "Line Chart"),
    ("Downtime", "Show daily downtime trend", "SELECT date, SUM(downtime_hours) as daily_downtime FROM kpi_downtime_data GROUP BY date ORDER BY date DESC LIMIT 30", "Line Chart"),

    # Energy (4 queries)
    ("Energy", "What is the total energy used?", "SELECT SUM(energy_used) as total_energy_used FROM kpi_energy_used_data", "KPI Card"),
    ("Energy", "Show energy consumption by furnace", "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total_energy DESC", "Bar Chart"),
    ("Energy", "Show monthly energy consumption", "SELECT DATE_TRUNC('month', date)::DATE as month, SUM(energy_used) as monthly_energy FROM kpi_energy_used_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC", "Line Chart"),
    ("Energy", "Which machine uses most energy?", "SELECT machine_id, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY machine_id ORDER BY total_energy DESC LIMIT 1", "Bar Chart"),

    # Yield (3 queries)
    ("Yield", "What is the average yield?", "SELECT AVG(yield_percentage) as avg_yield FROM kpi_yield_data", "KPI Card"),
    ("Yield", "Show yield by furnace", "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC", "Bar Chart"),
    ("Yield", "Which shift has highest yield?", "SELECT shift_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY shift_id ORDER BY avg_yield DESC LIMIT 1", "Bar Chart"),

    # Defect Rate (2 queries)
    ("Defect Rate", "What is the average defect rate?", "SELECT AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data", "KPI Card"),
    ("Defect Rate", "Show defect rate by shift", "SELECT shift_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY shift_id ORDER BY avg_defect_rate DESC", "Bar Chart"),

    # Cycle Time (3 queries)
    ("Cycle Time", "What is the average cycle time overall?", "SELECT AVG(cycle_time) as average_cycle_time FROM kpi_cycle_time_data", "KPI Card"),
    ("Cycle Time", "Show Average cycle time by furnace", "SELECT furnace_no, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY furnace_no ORDER BY avg_cycle_time DESC", "Line Chart"),
    ("Cycle Time", "Show daily cycle time trend", "SELECT date, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY date DESC", "Line Chart"),

    # General Production (4 queries)
    ("General", "What is the total quantity produced?", "SELECT SUM(quantity_produced) as total_quantity FROM kpi_quantity_produced_data", "KPI Card"),
    ("General", "Show production by furnace", "SELECT furnace_no, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_qty DESC", "Bar Chart"),
    ("General", "Show production by shift", "SELECT shift_id, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY shift_id ORDER BY total_qty DESC", "Bar Chart"),
    ("General", "What is the average production efficiency?", "SELECT AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data", "KPI Card"),

    # Tap Process (2 queries)
    ("Tap Process", "How many taps today?", "SELECT COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process WHERE DATE(tap_datetime) = CURRENT_DATE", "KPI Card"),
    ("Tap Process", "Show taps by furnace", "SELECT furnace_no, COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process GROUP BY furnace_no ORDER BY tap_count DESC", "Bar Chart"),

    # Maintenance & Safety (3 queries)
    ("Maintenance", "What is the average maintenance compliance?", "SELECT AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data", "KPI Card"),
    ("Safety", "What is the average safety incidents percentage?", "SELECT AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data", "KPI Card"),
    ("General", "List all furnaces", "SELECT furnace_no, furnace_description, is_active FROM furnace_furnaceconfig ORDER BY furnace_no", "Table"),
]

# Allowed tables
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


def normalize_sql(sql: str) -> str:
    """Normalize SQL for comparison."""
    if not sql:
        return ""
    sql = sql.upper()
    sql = re.sub(r'\s+', ' ', sql)
    sql = sql.strip()
    return sql


def compare_sql(expected: str, actual: str) -> Tuple[bool, float, str]:
    """Compare expected and actual SQL."""
    if not actual:
        return False, 0.0, "No SQL generated"

    norm_expected = normalize_sql(expected)
    norm_actual = normalize_sql(actual)

    if norm_expected == norm_actual:
        return True, 1.0, "Exact match"

    similarity = SequenceMatcher(None, norm_expected, norm_actual).ratio()

    # Check key elements
    exp_upper = expected.upper()
    act_upper = actual.upper() if actual else ""

    checks = {
        "same_aggregate": any(agg in exp_upper and agg in act_upper for agg in ["AVG(", "SUM(", "COUNT(", "MIN(", "MAX("]),
        "same_group_by": ("GROUP BY" in exp_upper) == ("GROUP BY" in act_upper),
        "same_table": False
    }

    # Check same table
    exp_table = re.search(r'FROM\s+(\w+)', exp_upper)
    act_table = re.search(r'FROM\s+(\w+)', act_upper)
    if exp_table and act_table:
        checks["same_table"] = exp_table.group(1) == act_table.group(1)

    match_count = sum(checks.values())

    if similarity >= 0.8 or (similarity >= 0.6 and match_count >= 2):
        return True, similarity, f"High similarity ({similarity:.0%})"
    elif similarity >= 0.5 and match_count >= 2:
        return True, similarity, f"Structural match ({similarity:.0%})"

    return False, similarity, f"Low match ({similarity:.0%})"


def normalize_graph(graph_type: str) -> str:
    """Normalize graph type."""
    if not graph_type:
        return ""
    return graph_type.lower().replace(" ", "_").replace("chart", "").strip("_")


def compare_graph(expected: str, actual: str) -> Tuple[bool, str]:
    """Compare graph types."""
    exp_norm = normalize_graph(expected)
    act_norm = normalize_graph(actual)

    if exp_norm == act_norm:
        return True, "Match"

    # Flexible matching
    kpi_variants = {"kpi", "kpi_card"}
    bar_variants = {"bar", "bar_"}
    line_variants = {"line", "line_", "area"}

    if exp_norm in kpi_variants and act_norm in kpi_variants:
        return True, "KPI match"
    if exp_norm in bar_variants and act_norm in bar_variants:
        return True, "Bar match"
    if exp_norm in line_variants and act_norm in line_variants:
        return True, "Line/Area match"

    return False, f"Mismatch: expected '{expected}', got '{actual}'"


def test_query(category: str, question: str, expected_sql: str, expected_graph: str,
               max_retries: int = 3) -> Dict:
    """Test a single query."""
    result = {
        "category": category,
        "question": question,
        "expected_sql": expected_sql,
        "expected_graph": expected_graph,
        "actual_sql": None,
        "actual_graph": None,
        "sql_match": False,
        "sql_similarity": 0.0,
        "graph_match": False,
        "error": None,
        "status": "FAIL"
    }

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
                    result["actual_sql"] = data.get("sql", "")

                    # Infer graph type from SQL structure
                    sql_upper = (result["actual_sql"] or "").upper()
                    has_group_by = "GROUP BY" in sql_upper
                    has_aggregate = any(agg in sql_upper for agg in ["AVG(", "SUM(", "COUNT(", "MIN(", "MAX("])
                    has_date = any(d in sql_upper for d in ["DATE", "MONTH", "WEEK", "DAY"])

                    if has_aggregate and not has_group_by:
                        result["actual_graph"] = "KPI Card"
                    elif has_group_by:
                        if has_date:
                            result["actual_graph"] = "Line Chart"
                        else:
                            result["actual_graph"] = "Bar Chart"
                    else:
                        result["actual_graph"] = "Table"

                    # Compare
                    result["sql_match"], result["sql_similarity"], _ = compare_sql(expected_sql, result["actual_sql"])
                    result["graph_match"], _ = compare_graph(expected_graph, result["actual_graph"])

                    if result["sql_match"] and result["graph_match"]:
                        result["status"] = "PASS"
                    elif result["sql_match"]:
                        result["status"] = "SQL_ONLY"
                    elif result["graph_match"]:
                        result["status"] = "GRAPH_ONLY"

                    return result
                else:
                    error_msg = data.get("error", "Unknown")
                    if "Token limit" in error_msg:
                        wait_match = re.search(r'wait (\d+) seconds', error_msg)
                        wait_time = int(wait_match.group(1)) + 2 if wait_match else 60
                        if attempt < max_retries - 1:
                            print(f" [rate limit, waiting {wait_time}s]", end="", flush=True)
                            time.sleep(wait_time)
                            continue
                    result["error"] = error_msg
            else:
                result["error"] = f"HTTP {response.status_code}"

        except Exception as e:
            result["error"] = str(e)
        break

    return result


def main():
    print("\n" + "=" * 70)
    print("CHATBOT SUBSET TEST - 30 Diverse Queries")
    print("=" * 70)
    print(f"Test cases: {len(TEST_CASES)}")

    # Check health
    try:
        health = requests.get(f"{NLP_SERVICE_URL}/health", timeout=5)
        print(f"NLP Service: {'HEALTHY' if health.status_code == 200 else 'UNHEALTHY'}")
    except Exception as e:
        print(f"NLP Service: UNREACHABLE - {e}")
        return

    results = []
    for i, (category, question, expected_sql, expected_graph) in enumerate(TEST_CASES):
        print(f"\n[{i+1}/{len(TEST_CASES)}] {category}: {question[:45]}...", end="", flush=True)

        result = test_query(category, question, expected_sql, expected_graph)
        results.append(result)

        status_icon = {
            "PASS": "PASS",
            "SQL_ONLY": "SQL",
            "GRAPH_ONLY": "GRAPH",
            "FAIL": "FAIL"
        }.get(result["status"], "FAIL")

        print(f" [{status_icon}]", end="")
        if result["error"]:
            print(f" Error: {result['error'][:25]}", end="")

        # Delay between tests
        if i < len(TEST_CASES) - 1:
            time.sleep(3)

    # Summary
    print("\n\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    total = len(results)
    full_pass = sum(1 for r in results if r["status"] == "PASS")
    sql_match = sum(1 for r in results if r["sql_match"])
    graph_match = sum(1 for r in results if r["graph_match"])
    errors = sum(1 for r in results if r["error"])

    print(f"Total Tests:    {total}")
    print(f"Full Pass:      {full_pass}/{total} ({full_pass*100/total:.1f}%)")
    print(f"SQL Match:      {sql_match}/{total} ({sql_match*100/total:.1f}%)")
    print(f"Graph Match:    {graph_match}/{total} ({graph_match*100/total:.1f}%)")
    print(f"Errors:         {errors}")

    # Category breakdown
    print("\nBy Category:")
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "sql": 0, "graph": 0, "pass": 0}
        categories[cat]["total"] += 1
        if r["sql_match"]:
            categories[cat]["sql"] += 1
        if r["graph_match"]:
            categories[cat]["graph"] += 1
        if r["status"] == "PASS":
            categories[cat]["pass"] += 1

    for cat, stats in sorted(categories.items()):
        sql_pct = stats['sql']*100/stats['total']
        graph_pct = stats['graph']*100/stats['total']
        print(f"  {cat:15} SQL: {sql_pct:5.1f}% | Graph: {graph_pct:5.1f}%")

    # Save results to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"subset_test_results_{timestamp}.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "Question", "Status", "SQL_Match", "SQL_Similarity",
                        "Graph_Match", "Expected_Graph", "Actual_Graph", "Error"])
        for r in results:
            writer.writerow([
                r["category"], r["question"], r["status"],
                "YES" if r["sql_match"] else "NO", f"{r['sql_similarity']:.0%}",
                "YES" if r["graph_match"] else "NO",
                r["expected_graph"], r["actual_graph"] or "None",
                r["error"] or ""
            ])
    print(f"\nResults saved to: {csv_file}")

    # Print failures
    failures = [r for r in results if r["status"] == "FAIL"]
    if failures:
        print(f"\n{'='*70}")
        print(f"FAILURES ({len(failures)})")
        print("=" * 70)
        for r in failures:
            print(f"\n[{r['category']}] {r['question']}")
            print(f"  Expected Graph: {r['expected_graph']} | Actual: {r['actual_graph']}")
            if r['error']:
                print(f"  Error: {r['error']}")
            if r['actual_sql']:
                print(f"  SQL Generated: {r['actual_sql'][:80]}...")


if __name__ == "__main__":
    main()
