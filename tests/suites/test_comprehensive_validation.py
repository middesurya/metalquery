#!/usr/bin/env python3
"""
Comprehensive Validation Test for NLP-to-SQL System
Tests all queries from the master list (excluding 8 already manually validated)
"""
import requests
import json
import time
import csv
from datetime import datetime
from typing import Dict, List, Tuple

# API Configuration
NLP_API_URL = "http://localhost:8003/api/v1/chat"
ALLOWED_TABLES = [
    "kpi_overall_equipment_efficiency_data",
    "kpi_downtime_data",
    "kpi_energy_used_data",
    "kpi_yield_data",
    "kpi_cycle_time_data",
    "kpi_defect_rate_data",
    "kpi_energy_efficiency_data",
    "kpi_quantity_produced_data",
    "kpi_output_rate_data",
    "kpi_production_efficiency_data",
    "kpi_on_time_delivery_data",
    "kpi_maintenance_compliance_data",
    "kpi_planned_maintenance_data",
    "kpi_safety_incidents_reported_data",
    "kpi_mean_time_between_failures_data",
    "kpi_mean_time_to_repair_data",
    "kpi_mean_time_between_stoppages_data",
    "kpi_first_pass_yield_data",
    "kpi_rework_rate_data",
    "kpi_resource_capacity_utilization_data",
    "core_process_tap_production",
    "core_process_tap_process",
    "core_process_tap_grading",
    "log_book_furnace_down_time_event",
    "furnace_furnaceconfig",
    "furnace_config_parameters",
    "plant_plant",
    "log_book_reasons",
    "log_book_downtime_type_master"
]

# Graph type mapping for validation
GRAPH_TYPE_MAPPING = {
    "KPI Card": ["kpi_card", "progress_bar", "metric_grid"],
    "Bar Chart": ["bar"],
    "Line Chart": ["line", "area"],
    "Table": ["table"],
    "Pie Chart": ["pie"]
}

# Queries already manually validated (skip these)
MANUALLY_VALIDATED = {
    "Show downtime by furnace",
    "What is the downtime by furnace?",
    "Show total downtime by furnace",
    "Display downtime by shift",
    "Show safety incidents by furnace",
    "Show cycle time by furnace",
    "Show taps by furnace",
    "Display taps by furnace"
}

def load_test_queries(filepath: str) -> List[Dict]:
    """Load test queries from CSV file."""
    queries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Skip manually validated queries
            if row['Question'].strip() in MANUALLY_VALIDATED:
                continue
            queries.append({
                'category': row['Category'],
                'question': row['Question'],
                'expected_sql': row['SQL'],
                'expected_graph': row['Predicted Graph Type'],
                'status': row['Status']
            })
    return queries

def call_nlp_api(question: str) -> Dict:
    """Call NLP service API and return response."""
    try:
        response = requests.post(
            NLP_API_URL,
            json={
                "question": question,
                "allowed_tables": ALLOWED_TABLES
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "success": False}

def normalize_graph_type(graph_type: str) -> str:
    """Normalize graph type for comparison."""
    if not graph_type:
        return "unknown"

    gt_lower = graph_type.lower().strip()

    # Map actual response to expected categories
    for expected, actuals in GRAPH_TYPE_MAPPING.items():
        if any(actual in gt_lower for actual in actuals):
            return expected

    return graph_type

def validate_sql_basic(sql: str, expected_sql: str) -> Tuple[bool, str]:
    """Basic SQL validation - check if key elements match."""
    if not sql:
        return False, "No SQL generated"

    sql_lower = sql.lower()
    expected_lower = expected_sql.lower()

    # Check for SELECT statement
    if 'select' not in sql_lower:
        return False, "Not a SELECT statement"

    # Extract key elements from expected SQL
    expected_tables = set()
    expected_columns = set()
    expected_aggregations = set()

    # Simple extraction (keywords)
    for word in expected_lower.split():
        if word in ['sum', 'avg', 'count', 'min', 'max']:
            expected_aggregations.add(word)
        if 'kpi_' in word or 'core_' in word or 'log_' in word or 'furnace_' in word:
            expected_tables.add(word.strip(',()'))

    # Check if generated SQL has similar elements
    sql_has_aggregation = any(agg in sql_lower for agg in expected_aggregations)
    sql_has_tables = any(table in sql_lower for table in expected_tables)

    if expected_aggregations and not sql_has_aggregation:
        return False, f"Missing aggregations: {expected_aggregations}"

    if expected_tables and not sql_has_tables:
        return False, f"Missing tables: {expected_tables}"

    return True, "SQL structure valid"

def test_query(query_data: Dict, test_num: int, total: int) -> Dict:
    """Test a single query and return results."""
    question = query_data['question']
    expected_sql = query_data['expected_sql']
    expected_graph = query_data['expected_graph']
    category = query_data['category']

    print(f"\n[{test_num}/{total}] Testing: {question[:80]}...")

    # Call API
    response = call_nlp_api(question)

    # Parse response
    success = response.get('success', False)
    actual_sql = response.get('sql', '')
    actual_graph = response.get('graph_type', '')
    error = response.get('error', '')

    # Validate SQL
    sql_valid, sql_reason = validate_sql_basic(actual_sql, expected_sql)

    # Validate graph type
    actual_graph_normalized = normalize_graph_type(actual_graph)
    expected_graph_normalized = expected_graph.strip()
    graph_match = actual_graph_normalized == expected_graph_normalized

    # Determine overall status
    if not success:
        overall_status = "FAIL - API Error"
    elif not sql_valid:
        overall_status = "FAIL - SQL Invalid"
    elif not graph_match:
        overall_status = "WARN - Graph Mismatch"
    else:
        overall_status = "PASS"

    result = {
        'category': category,
        'question': question,
        'expected_sql': expected_sql[:100] + "..." if len(expected_sql) > 100 else expected_sql,
        'actual_sql': actual_sql[:100] + "..." if len(actual_sql) > 100 else actual_sql,
        'expected_graph': expected_graph_normalized,
        'actual_graph': actual_graph_normalized,
        'sql_valid': sql_valid,
        'sql_reason': sql_reason,
        'graph_match': graph_match,
        'success': success,
        'error': error,
        'overall_status': overall_status
    }

    # Print result
    status_symbol = "✓" if overall_status == "PASS" else "⚠" if "WARN" in overall_status else "✗"
    print(f"  {status_symbol} {overall_status}")
    if not success:
        print(f"     Error: {error}")
    if not graph_match:
        print(f"     Graph: Expected '{expected_graph_normalized}', Got '{actual_graph_normalized}'")

    return result

def generate_report(results: List[Dict], output_file: str):
    """Generate comprehensive test report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Calculate statistics
    total = len(results)
    passed = sum(1 for r in results if r['overall_status'] == "PASS")
    warnings = sum(1 for r in results if "WARN" in r['overall_status'])
    failed = sum(1 for r in results if "FAIL" in r['overall_status'])

    sql_valid = sum(1 for r in results if r['sql_valid'])
    graph_match = sum(1 for r in results if r['graph_match'])

    # Category breakdown
    categories = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'passed': 0, 'warnings': 0, 'failed': 0}
        categories[cat]['total'] += 1
        if r['overall_status'] == "PASS":
            categories[cat]['passed'] += 1
        elif "WARN" in r['overall_status']:
            categories[cat]['warnings'] += 1
        else:
            categories[cat]['failed'] += 1

    # Write CSV report
    csv_file = output_file.replace('.txt', '.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['category', 'question', 'expected_graph', 'actual_graph', 'graph_match',
                     'sql_valid', 'success', 'overall_status', 'error']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                'category': r['category'],
                'question': r['question'],
                'expected_graph': r['expected_graph'],
                'actual_graph': r['actual_graph'],
                'graph_match': r['graph_match'],
                'sql_valid': r['sql_valid'],
                'success': r['success'],
                'overall_status': r['overall_status'],
                'error': r.get('error', '')
            })

    # Write text report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("COMPREHENSIVE VALIDATION TEST REPORT\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("=" * 80 + "\n\n")

        f.write("SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Queries Tested: {total}\n")
        f.write(f"  PASSED:   {passed:4d} ({passed/total*100:5.1f}%)\n")
        f.write(f"  WARNINGS: {warnings:4d} ({warnings/total*100:5.1f}%)\n")
        f.write(f"  FAILED:   {failed:4d} ({failed/total*100:5.1f}%)\n\n")

        f.write(f"SQL Generation: {sql_valid}/{total} ({sql_valid/total*100:.1f}%)\n")
        f.write(f"Graph Type Match: {graph_match}/{total} ({graph_match/total*100:.1f}%)\n\n")

        f.write("CATEGORY BREAKDOWN\n")
        f.write("-" * 80 + "\n")
        for cat, stats in sorted(categories.items()):
            f.write(f"\n{cat}:\n")
            f.write(f"  Total: {stats['total']}\n")
            f.write(f"  Passed: {stats['passed']} ({stats['passed']/stats['total']*100:.1f}%)\n")
            f.write(f"  Warnings: {stats['warnings']} ({stats['warnings']/stats['total']*100:.1f}%)\n")
            f.write(f"  Failed: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("DETAILED RESULTS\n")
        f.write("=" * 80 + "\n\n")

        for i, r in enumerate(results, 1):
            f.write(f"[{i}/{total}] {r['question']}\n")
            f.write(f"  Category: {r['category']}\n")
            f.write(f"  Status: {r['overall_status']}\n")
            f.write(f"  SQL Valid: {r['sql_valid']} - {r['sql_reason']}\n")
            f.write(f"  Graph Match: {r['graph_match']} - Expected: {r['expected_graph']}, Got: {r['actual_graph']}\n")
            if r.get('error'):
                f.write(f"  Error: {r['error']}\n")
            f.write("\n")

    print(f"\nReport saved to: {output_file}")
    print(f"CSV saved to: {csv_file}")

def main():
    """Main test execution."""
    print("=" * 80)
    print("COMPREHENSIVE VALIDATION TEST")
    print("=" * 80)
    print(f"\nSkipping {len(MANUALLY_VALIDATED)} manually validated queries")
    print("Testing all remaining queries from master list...\n")

    # Create test data file from user's list
    # Note: User should paste their data into test_queries.tsv
    test_file = "test_queries.tsv"

    try:
        queries = load_test_queries(test_file)
    except FileNotFoundError:
        print(f"Error: {test_file} not found!")
        print("Please create test_queries.tsv with your query list (tab-separated)")
        return

    print(f"Loaded {len(queries)} queries to test\n")

    # Run tests
    results = []
    for i, query_data in enumerate(queries, 1):
        result = test_query(query_data, i, len(queries))
        results.append(result)

        # Rate limiting - wait 1 second between requests
        if i < len(queries):
            time.sleep(1)

    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"validation_report_{timestamp}.txt"
    generate_report(results, report_file)

    # Print summary
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    passed = sum(1 for r in results if r['overall_status'] == "PASS")
    warnings = sum(1 for r in results if "WARN" in r['overall_status'])
    failed = sum(1 for r in results if "FAIL" in r['overall_status'])

    print(f"\nPASSED:   {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
    print(f"WARNINGS: {warnings}/{len(results)} ({warnings/len(results)*100:.1f}%)")
    print(f"FAILED:   {failed}/{len(results)} ({failed/len(results)*100:.1f}%)")
    print(f"\nFull report: {report_file}")

if __name__ == "__main__":
    main()
