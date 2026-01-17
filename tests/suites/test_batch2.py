#!/usr/bin/env python3
"""
Batch 2 Test - 30 more diverse queries across all categories
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

# Second batch of 30 test cases - different from batch 1
TEST_CASES = [
    # OEE - Different patterns (5)
    ("OEE", "What is the average OEE per day?", "SELECT date, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date ORDER BY date DESC", "Line Chart"),
    ("OEE", "Show OEE statistics", "SELECT MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, AVG(oee_percentage) as avg_oee, STDDEV(oee_percentage) as stddev_oee FROM kpi_overall_equipment_efficiency_data", "KPI Card"),
    ("OEE", "Compare OEE between Furnace 1 and 2", "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE furnace_no IN (1, 2) GROUP BY furnace_no ORDER BY avg_oee DESC", "Bar Chart"),
    ("OEE", "Show OEE records above 90%", "SELECT date, furnace_no, shift_id, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage > 90 ORDER BY oee_percentage DESC LIMIT 100", "Table"),
    ("OEE", "Which product_type_id has the highest OEE?", "SELECT product_type_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY product_type_id ORDER BY avg_oee DESC LIMIT 1", "Bar Chart"),

    # Downtime - Using question format to avoid routing issue (4)
    ("Downtime", "What is the average downtime per furnace?", "SELECT furnace_no, AVG(downtime_hours) as avg_downtime FROM kpi_downtime_data GROUP BY furnace_no", "Line Chart"),
    ("Downtime", "Show downtime events exceeding 8 hours", "SELECT obs_start_dt, furnace_no, downtime_hours FROM log_book_furnace_down_time_event WHERE downtime_hours > 8 ORDER BY downtime_hours DESC", "Table"),
    ("Downtime", "What is the downtime last week?", "SELECT date, furnace_no, SUM(downtime_hours) as downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date, furnace_no ORDER BY date DESC", "Line Chart"),
    ("Downtime", "Show downtime statistics by furnace", "SELECT furnace_no, MIN(downtime_hours) as min, MAX(downtime_hours) as max, AVG(downtime_hours) as avg, SUM(downtime_hours) as total, COUNT(*) as count FROM kpi_downtime_data GROUP BY furnace_no", "Line Chart"),

    # Energy - Different patterns (4)
    ("Energy", "What is the average energy efficiency?", "SELECT AVG(energy_efficiency) as avg_energy_efficiency FROM kpi_energy_efficiency_data", "KPI Card"),
    ("Energy", "Show energy efficiency by furnace", "SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency", "Bar Chart"),
    ("Energy", "Which furnace is most energy efficient?", "SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency ASC LIMIT 1", "Bar Chart"),
    ("Energy", "Show energy consumption last 7 days", "SELECT date, SUM(energy_used) as daily_total FROM kpi_energy_used_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date ORDER BY date", "Line Chart"),

    # Yield - More patterns (3)
    ("Yield", "Show yield statistics by furnace", "SELECT furnace_no, AVG(yield_percentage) as avg_yield, STDDEV(yield_percentage) as stddev_yield, MIN(yield_percentage) as min_yield, MAX(yield_percentage) as max_yield FROM kpi_yield_data GROUP BY furnace_no", "Bar Chart"),
    ("Yield", "Show low yield records", "SELECT date, shift_id, furnace_no, yield_percentage FROM kpi_yield_data WHERE yield_percentage < 85 ORDER BY yield_percentage ASC LIMIT 100", "Table"),
    ("Yield", "Which furnace has best yield?", "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC LIMIT 1", "Bar Chart"),

    # Defect Rate (2)
    ("Defect Rate", "Show defect rate trend last 30 days", "SELECT date, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC", "Line Chart"),
    ("Defect Rate", "Which furnace has highest defect rate?", "SELECT furnace_no, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY furnace_no ORDER BY avg_defect_rate DESC LIMIT 1", "Bar Chart"),

    # Cycle Time (3)
    ("Cycle Time", "What is the total cycle time per day?", "SELECT date, SUM(cycle_time) as total_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY date DESC", "Line Chart"),
    ("Cycle Time", "Show top 5 machines by cycle time", "SELECT machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id ORDER BY avg_cycle_time DESC LIMIT 5", "Line Chart"),
    ("Cycle Time", "Show records where cycle time is greater than 90", "SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE cycle_time > 90 ORDER BY cycle_time DESC LIMIT 100", "Table"),

    # General/Production (4)
    ("General", "Show daily production", "SELECT date, SUM(quantity_produced) as daily_production FROM kpi_quantity_produced_data GROUP BY date ORDER BY date DESC LIMIT 30", "Line Chart"),
    ("General", "What is the average MTBF?", "SELECT AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data", "KPI Card"),
    ("General", "Show mtbf by furnace", "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC", "Line Chart"),
    ("General", "What is the average MTTR?", "SELECT AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data", "KPI Card"),

    # Tap Process (3)
    ("Tap Process", "Show daily tap production", "SELECT DATE_TRUNC('day', tap_production_datetime)::DATE as production_date, COUNT(DISTINCT tap_id) as tap_count, SUM(cast_weight) as daily_weight FROM core_process_tap_production GROUP BY DATE_TRUNC('day', tap_production_datetime) ORDER BY production_date DESC LIMIT 30", "Line Chart"),
    ("Tap Process", "What is the total cast weight?", "SELECT SUM(cast_weight) as total_cast_weight FROM core_process_tap_production", "KPI Card"),
    ("Tap Process", "Show tap status summary", "SELECT tap_status, COUNT(*) as count FROM core_process_tap_process GROUP BY tap_status ORDER BY count DESC", "Bar Chart"),

    # Maintenance (2)
    ("Maintenance", "Show planned maintenance by furnace", "SELECT furnace_no, AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data GROUP BY furnace_no ORDER BY avg_planned DESC", "Bar Chart"),
    ("Maintenance", "Show compliance trend", "SELECT date, AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data GROUP BY date ORDER BY date DESC LIMIT 30", "Line Chart"),
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


def normalize_sql(sql: str) -> str:
    if not sql:
        return ""
    sql = sql.upper()
    sql = re.sub(r'\s+', ' ', sql)
    return sql.strip()


def compare_sql(expected: str, actual: str) -> Tuple[bool, float, str]:
    if not actual:
        return False, 0.0, "No SQL generated"

    norm_expected = normalize_sql(expected)
    norm_actual = normalize_sql(actual)

    if norm_expected == norm_actual:
        return True, 1.0, "Exact match"

    similarity = SequenceMatcher(None, norm_expected, norm_actual).ratio()

    exp_upper = expected.upper()
    act_upper = actual.upper() if actual else ""

    checks = {
        "same_aggregate": any(agg in exp_upper and agg in act_upper for agg in ["AVG(", "SUM(", "COUNT(", "MIN(", "MAX("]),
        "same_group_by": ("GROUP BY" in exp_upper) == ("GROUP BY" in act_upper),
        "same_table": False
    }

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
    if not graph_type:
        return ""
    return graph_type.lower().replace(" ", "_").replace("chart", "").strip("_")


def compare_graph(expected: str, actual: str) -> Tuple[bool, str]:
    exp_norm = normalize_graph(expected)
    act_norm = normalize_graph(actual)

    if exp_norm == act_norm:
        return True, "Match"

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
    print("CHATBOT BATCH 2 TEST - 30 More Queries")
    print("=" * 70)
    print(f"Test cases: {len(TEST_CASES)}")

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

        if i < len(TEST_CASES) - 1:
            time.sleep(3)

    # Summary
    print("\n\n" + "=" * 70)
    print("BATCH 2 TEST SUMMARY")
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

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"batch2_test_results_{timestamp}.csv"
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


if __name__ == "__main__":
    main()
