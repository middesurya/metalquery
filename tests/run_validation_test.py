#!/usr/bin/env python3
"""
Comprehensive Validation Test - Simplified Runner
Tests queries and validates SQL + Graph Type predictions
"""
import requests
import json
import time
from datetime import datetime

# API Configuration
NLP_API_URL = "http://localhost:8003/api/v1/chat"

# Test queries (sample - add more from your list)
TEST_QUERIES = [
    # OEE Queries
    {"cat": "OEE", "q": "What is the average oee for all furnaces", "exp_graph": "KPI Card"},
    {"cat": "OEE", "q": "Show Average OEE by furnace", "exp_graph": "Bar Chart"},
    {"cat": "OEE", "q": "Which furnace has highest OEE?", "exp_graph": "Bar Chart"},

    # Energy Queries
    {"cat": "Energy", "q": "Show Total energy consumption by furnace", "exp_graph": "Bar Chart"},
    {"cat": "Energy", "q": "Show energy consumption by furnace", "exp_graph": "Bar Chart"},
    {"cat": "Energy", "q": "What is the total energy used?", "exp_graph": "KPI Card"},

    # Yield Queries
    {"cat": "Yield", "q": "What is the average yield for furnace 2", "exp_graph": "KPI Card"},
    {"cat": "Yield", "q": "Show yield by shift", "exp_graph": "Bar Chart"},
    {"cat": "Yield", "q": "Which furnace has best yield?", "exp_graph": "Bar Chart"},

    # Downtime Queries (excluding manually validated ones)
    {"cat": "Downtime", "q": "Show what is the total downtime last year", "exp_graph": "KPI Card"},
    {"cat": "Downtime", "q": "What is the average downtime per furnace", "exp_graph": "Line Chart"},

    # Production Queries
    {"cat": "General", "q": "Show Total quantity produced by furnace", "exp_graph": "Bar Chart"},
    {"cat": "General", "q": "Show production by furnace", "exp_graph": "Bar Chart"},
    {"cat": "General", "q": "What is the total production for furnace 1 last month", "exp_graph": "KPI Card"},

    # Cycle Time Queries (excluding manually validated)
    {"cat": "Cycle Time", "q": "What is the average cycle time overall?", "exp_graph": "KPI Card"},
    {"cat": "Cycle Time", "q": "Show Average cycle time by furnace", "exp_graph": "Line Chart"},
    {"cat": "Cycle Time", "q": "Which shift has the highest average cycle time?", "exp_graph": "Line Chart"},

    # Defect Rate Queries
    {"cat": "Defect Rate", "q": "What is the average defect rate?", "exp_graph": "KPI Card"},
    {"cat": "Defect Rate", "q": "Show defect rate by shift", "exp_graph": "Bar Chart"},
    {"cat": "Defect Rate", "q": "Which furnace has highest defect rate?", "exp_graph": "Bar Chart"},

    # Safety Queries (excluding manually validated)
    {"cat": "Safety", "q": "What is the average safety incidents percentage?", "exp_graph": "KPI Card"},
    {"cat": "Safety", "q": "Show safety incidents trend", "exp_graph": "Line Chart"},
    {"cat": "Safety", "q": "Show safety by shift", "exp_graph": "Bar Chart"},

    # MTBF/MTTR Queries
    {"cat": "General", "q": "What is the average MTBF?", "exp_graph": "KPI Card"},
    {"cat": "General", "q": "Show mtbf by furnace", "exp_graph": "Line Chart"},
    {"cat": "General", "q": "What is the average MTTR?", "exp_graph": "KPI Card"},
    {"cat": "General", "q": "Show mttr by furnace", "exp_graph": "Line Chart"},

    # Tap Process Queries (excluding manually validated)
    {"cat": "Tap Process", "q": "Show tap status summary", "exp_graph": "Bar Chart"},
    {"cat": "Tap Process", "q": "Show tap progress distribution", "exp_graph": "Bar Chart"},
    {"cat": "Tap Process", "q": "How many taps today?", "exp_graph": "KPI Card"},
]

def normalize_graph_type(graph_type: str) -> str:
    """Normalize graph type for comparison."""
    if not graph_type:
        return "Unknown"

    gt_lower = graph_type.lower().strip()

    # Mapping
    if any(x in gt_lower for x in ["kpi", "kpi_card", "progress_bar", "metric_grid"]):
        return "KPI Card"
    elif "bar" in gt_lower:
        return "Bar Chart"
    elif any(x in gt_lower for x in ["line", "area"]):
        return "Line Chart"
    elif "pie" in gt_lower:
        return "Pie Chart"
    elif "table" in gt_lower:
        return "Table"

    return graph_type

def test_query(category, question, expected_graph, test_num, total):
    """Test a single query."""
    print(f"\n[{test_num}/{total}] {category}: {question[:60]}...")

    try:
        response = requests.post(
            NLP_API_URL,
            json={"question": question},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        success = data.get('success', False)
        sql = data.get('sql', '')
        actual_graph = normalize_graph_type(data.get('graph_type', ''))

        # Validate
        sql_ok = success and len(sql) > 0
        graph_match = actual_graph == expected_graph

        # Status
        if not success:
            status = "FAIL - No SQL"
            symbol = "[FAIL]"
        elif not sql_ok:
            status = "FAIL - SQL Empty"
            symbol = "[FAIL]"
        elif not graph_match:
            status = "WARN - Graph Mismatch"
            symbol = "[WARN]"
        else:
            status = "PASS"
            symbol = "[PASS]"

        print(f"  {symbol} {status}")
        print(f"     SQL: {'YES' if sql_ok else 'NO'}")
        print(f"     Graph: Expected '{expected_graph}', Got '{actual_graph}' - {'MATCH' if graph_match else 'MISMATCH'}")

        if sql and len(sql) < 200:
            print(f"     SQL: {sql[:100]}...")

        return {
            'category': category,
            'question': question,
            'expected_graph': expected_graph,
            'actual_graph': actual_graph,
            'sql_ok': sql_ok,
            'graph_match': graph_match,
            'status': status,
            'sql': sql[:200] if sql else ''
        }

    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return {
            'category': category,
            'question': question,
            'expected_graph': expected_graph,
            'actual_graph': 'Error',
            'sql_ok': False,
            'graph_match': False,
            'status': 'ERROR',
            'sql': ''
        }

def main():
    """Run validation test."""
    print("=" * 80)
    print("COMPREHENSIVE VALIDATION TEST")
    print("=" * 80)
    print(f"\nTesting {len(TEST_QUERIES)} queries...")
    print("(Excluding 8 manually validated queries)\n")

    results = []
    for i, test in enumerate(TEST_QUERIES, 1):
        result = test_query(
            test['cat'],
            test['q'],
            test['exp_graph'],
            i,
            len(TEST_QUERIES)
        )
        results.append(result)

        # Rate limiting
        if i < len(TEST_QUERIES):
            time.sleep(0.5)

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for r in results if r['status'] == 'PASS')
    warnings = sum(1 for r in results if 'WARN' in r['status'])
    failed = sum(1 for r in results if 'FAIL' in r['status'] or 'ERROR' in r['status'])

    sql_ok = sum(1 for r in results if r['sql_ok'])
    graph_match = sum(1 for r in results if r['graph_match'])

    print(f"\nTotal Queries: {len(results)}")
    print(f"  PASSED:   {passed:3d} ({passed/len(results)*100:5.1f}%)")
    print(f"  WARNINGS: {warnings:3d} ({warnings/len(results)*100:5.1f}%)")
    print(f"  FAILED:   {failed:3d} ({failed/len(results)*100:5.1f}%)")
    print(f"\nSQL Generation: {sql_ok}/{len(results)} ({sql_ok/len(results)*100:.1f}%)")
    print(f"Graph Type Match: {graph_match}/{len(results)} ({graph_match/len(results)*100:.1f}%)")

    # Category breakdown
    print("\nCATEGORY BREAKDOWN:")
    categories = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'passed': 0, 'warnings': 0, 'failed': 0}
        categories[cat]['total'] += 1
        if r['status'] == 'PASS':
            categories[cat]['passed'] += 1
        elif 'WARN' in r['status']:
            categories[cat]['warnings'] += 1
        else:
            categories[cat]['failed'] += 1

    for cat in sorted(categories.keys()):
        stats = categories[cat]
        print(f"\n  {cat}:")
        print(f"    Total: {stats['total']}, Passed: {stats['passed']}, Warnings: {stats['warnings']}, Failed: {stats['failed']}")

    # Issues
    print("\nISSUES FOUND:")
    graph_mismatches = [r for r in results if not r['graph_match'] and r['sql_ok']]
    if graph_mismatches:
        print(f"\nGraph Type Mismatches ({len(graph_mismatches)}):")
        for r in graph_mismatches[:10]:  # Show first 10
            print(f"  - {r['question'][:60]}")
            print(f"    Expected: {r['expected_graph']}, Got: {r['actual_graph']}")

    sql_failures = [r for r in results if not r['sql_ok']]
    if sql_failures:
        print(f"\nSQL Generation Failures ({len(sql_failures)}):")
        for r in sql_failures[:5]:  # Show first 5
            print(f"  - {r['question'][:60]}")

    print("\n" + "=" * 80)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"validation_results_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {filename}")

if __name__ == "__main__":
    main()
