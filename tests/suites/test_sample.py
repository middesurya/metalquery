#!/usr/bin/env python3
"""Quick sample test to verify script works before full run."""

import requests
import json
import time

NLP_SERVICE_URL = "http://localhost:8003"

SAMPLE_TESTS = [
    ("OEE", "What is the average oee for all furnaces", "KPI Card"),
    ("Downtime", "What is the total downtime?", "KPI Card"),
    ("Energy", "What is the total energy used?", "KPI Card"),
    ("Yield", "What is the average yield?", "KPI Card"),
    ("General", "What is the total quantity produced?", "KPI Card"),
]

ALLOWED_TABLES = [
    "kpi_overall_equipment_efficiency_data", "kpi_downtime_data", "kpi_energy_used_data",
    "kpi_yield_data", "kpi_quantity_produced_data"
]

def test_query(question, expected_graph):
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

                # Get graph type from chart_config (directly in response root)
                chart_config = data.get("chart_config") or {}
                chart_type = chart_config.get("type", "") if chart_config else ""

                # Map internal chart types to expected graph types
                chart_type_mapping = {
                    "progress_bar": "KPI Card",
                    "kpi_card": "KPI Card",
                    "bar": "Bar Chart",
                    "line": "Line Chart",
                    "area": "Line Chart",
                    "pie": "Bar Chart",
                    "table": "Table",
                    "metric_grid": "KPI Card"
                }

                # If chart_config is None, infer from SQL structure
                if not chart_type and sql:
                    sql_upper = sql.upper()
                    has_group_by = "GROUP BY" in sql_upper
                    has_aggregate = any(agg in sql_upper for agg in ["AVG(", "SUM(", "COUNT(", "MIN(", "MAX("])

                    if has_aggregate and not has_group_by:
                        actual_graph = "KPI Card"
                    elif has_group_by:
                        if "DATE" in sql_upper or "MONTH" in sql_upper:
                            actual_graph = "Line Chart"
                        else:
                            actual_graph = "Bar Chart"
                    else:
                        actual_graph = "Table"
                else:
                    actual_graph = chart_type_mapping.get(chart_type, chart_type.title() if chart_type else "Table")

                # Normalize for comparison
                def normalize(g):
                    return g.lower().replace(" ", "_").replace("chart", "").strip("_") if g else ""

                return {
                    "success": True,
                    "sql": sql,
                    "expected_graph": expected_graph,
                    "actual_graph": actual_graph,
                    "chart_type_raw": chart_type,
                    "graph_match": normalize(expected_graph) == normalize(actual_graph) or
                                   (normalize(expected_graph) in ["kpi", "kpi_card"] and normalize(actual_graph) in ["kpi", "kpi_card"]) or
                                   (normalize(expected_graph) in ["bar", "bar_chart"] and normalize(actual_graph) in ["bar", "bar_chart"]) or
                                   (normalize(expected_graph) in ["line", "line_chart"] and normalize(actual_graph) in ["line", "line_chart"])
                }
            else:
                return {"success": False, "error": data.get("error", "Unknown")}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("\n" + "="*60)
    print("SAMPLE TEST - Verifying Script Works")
    print("="*60)

    # Check health
    try:
        health = requests.get(f"{NLP_SERVICE_URL}/health", timeout=5)
        print(f"NLP Service: {'HEALTHY' if health.status_code == 200 else 'UNHEALTHY'}")
    except Exception as e:
        print(f"NLP Service: UNREACHABLE - {e}")
        return

    results = []
    for i, (category, question, expected_graph) in enumerate(SAMPLE_TESTS):
        print(f"\n[{i+1}/{len(SAMPLE_TESTS)}] {category}: {question}")

        result = test_query(question, expected_graph)
        results.append(result)

        if result.get("success"):
            print(f"  SQL: {result['sql'][:80]}...")
            print(f"  Expected Graph: {expected_graph}")
            print(f"  Actual Graph: {result['actual_graph']}")
            print(f"  Graph Match: {'YES' if result['graph_match'] else 'NO'}")
        else:
            print(f"  ERROR: {result.get('error', 'Unknown')}")

            # If rate limited, wait and retry
            if "Token limit" in str(result.get("error", "")):
                print("  Waiting 60s for rate limit...")
                time.sleep(60)
                result = test_query(question, expected_graph)
                results[-1] = result
                if result.get("success"):
                    print(f"  RETRY SUCCESS!")
                    print(f"  SQL: {result['sql'][:80]}...")
                    print(f"  Graph Match: {'YES' if result['graph_match'] else 'NO'}")

        # Delay between tests
        if i < len(SAMPLE_TESTS) - 1:
            print("  [waiting 5s...]")
            time.sleep(5)

    # Summary
    successful = sum(1 for r in results if r.get("success"))
    graph_matches = sum(1 for r in results if r.get("graph_match"))

    print("\n" + "="*60)
    print("SAMPLE TEST SUMMARY")
    print("="*60)
    print(f"Successful: {successful}/{len(results)}")
    print(f"Graph Match: {graph_matches}/{len(results)}")

    if successful > 0:
        print("\nScript is working! Ready to run full test suite.")
    else:
        print("\nAll tests failed - check rate limits or service issues.")

if __name__ == "__main__":
    main()
