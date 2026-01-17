#!/usr/bin/env python3
"""
Comprehensive Test Script for Full Query Validation
Handles large query lists with smart rate limiting and detailed reporting
"""
import requests
import json
import time
import csv
from datetime import datetime
from collections import defaultdict

# API Configuration
NLP_API_URL = "http://localhost:8003/api/v1/chat"
REQUEST_TIMEOUT = 30
DELAY_BETWEEN_REQUESTS = 2.5  # 2.5 seconds = ~24 requests/minute (under 27 limit)

# Manually validated queries to skip
MANUALLY_VALIDATED = [
    "Show downtime by furnace",
    "What is the downtime by furnace?",
    "Show total downtime by furnace",
    "Display downtime by shift",
    "Show safety incidents by furnace",
    "Show cycle time by furnace",
    "Show taps by furnace",
    "Display taps by furnace"
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

def load_queries_from_tsv(filepath: str):
    """Load queries from TSV/Markdown table file."""
    queries = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Check if it's markdown table format (has pipes)
        if lines and '|' in lines[0]:
            # Parse markdown table
            headers = [h.strip() for h in lines[0].split('|')[1:-1]]  # Skip first and last empty elements

            for line in lines[2:]:  # Skip header and separator line
                if not line.strip() or '---' in line:
                    continue

                columns = [c.strip() for c in line.split('|')[1:-1]]
                if len(columns) != len(headers):
                    continue

                row = dict(zip(headers, columns))

                # Skip manually validated queries
                question = row.get('Question', '').strip()
                if question in MANUALLY_VALIDATED:
                    continue

                if question:  # Skip empty questions
                    queries.append({
                        'category': row.get('Category', 'General').strip(),
                        'question': question,
                        'expected_sql': row.get('SQL', '').strip(),
                        'expected_graph': row.get('Predicted Graph Type', '').strip(),
                        'status': row.get('Status', 'New').strip()
                    })
        else:
            # Parse tab-separated format
            reader = csv.DictReader(lines, delimiter='\t')
            for row in reader:
                # Skip manually validated queries
                question = row.get('Question', '').strip()
                if question in MANUALLY_VALIDATED:
                    continue

                if question:  # Skip empty questions
                    queries.append({
                        'category': row.get('Category', 'General').strip(),
                        'question': question,
                        'expected_sql': row.get('SQL', '').strip(),
                        'expected_graph': row.get('Predicted Graph Type', '').strip(),
                        'status': row.get('Status', 'New').strip()
                    })
    except Exception as e:
        print(f"[ERROR] Failed to load file: {e}")
        import traceback
        traceback.print_exc()
        return []

    return queries

def validate_sql(actual_sql: str, expected_sql: str, question: str) -> tuple:
    """
    Validate if generated SQL is correct.
    Returns (is_valid, reason)
    """
    if not actual_sql:
        return False, "No SQL generated"

    actual_lower = actual_sql.lower().strip()

    # Basic validation: Must have SELECT
    if 'select' not in actual_lower:
        return False, "Invalid SQL: Missing SELECT"

    # Check if it's routed to BRD instead of SQL
    if 'brd' in actual_lower or 'documentation' in actual_lower:
        return False, "Routed to BRD instead of SQL"

    # If we have expected SQL, compare key components
    if expected_sql:
        expected_lower = expected_sql.lower().strip()

        # Extract table names from both
        actual_tables = [t.strip() for t in actual_lower.split('from')[1].split('where')[0].split('join') if t.strip()]
        expected_tables = [t.strip() for t in expected_lower.split('from')[1].split('where')[0].split('join') if t.strip()]

        # Check if main table matches
        if actual_tables and expected_tables:
            actual_main = actual_tables[0].split()[0]
            expected_main = expected_tables[0].split()[0]
            if actual_main != expected_main:
                return False, f"Table mismatch: Expected {expected_main}, got {actual_main}"

    return True, "Valid"

def test_query(category: str, question: str, expected_sql: str, expected_graph: str, test_num: int, total: int):
    """Test a single query and return results."""
    print(f"\n[{test_num}/{total}] {category}: {question[:70]}...")

    try:
        # Send request
        response = requests.post(
            NLP_API_URL,
            json={"question": question},
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        # Extract response data
        success = data.get('success', False)
        actual_sql = data.get('sql', '')
        chart_config = data.get('chart_config') or {}
        actual_graph_raw = chart_config.get('chart_type', '')
        actual_graph = normalize_graph_type(actual_graph_raw)

        # Validate SQL
        sql_valid, sql_reason = validate_sql(actual_sql, expected_sql, question)

        # Validate graph type
        graph_match = actual_graph == expected_graph if expected_graph else True

        # Determine status
        if not success:
            status = "FAIL"
            reason = "API returned success=false"
        elif not sql_valid:
            status = "FAIL"
            reason = sql_reason
        elif not graph_match:
            status = "WARN"
            reason = f"Graph mismatch: Expected '{expected_graph}', got '{actual_graph}'"
        else:
            status = "PASS"
            reason = "All checks passed"

        # Print result
        symbol = "[PASS]" if status == "PASS" else "[WARN]" if status == "WARN" else "[FAIL]"
        print(f"  {symbol} {status}")
        print(f"     SQL: {'Valid' if sql_valid else sql_reason}")
        print(f"     Graph: {actual_graph} {'(MATCH)' if graph_match else f'(Expected: {expected_graph})'}")

        return {
            'category': category,
            'question': question,
            'expected_sql': expected_sql[:200],
            'actual_sql': actual_sql[:200],
            'expected_graph': expected_graph,
            'actual_graph': actual_graph,
            'sql_valid': sql_valid,
            'sql_reason': sql_reason,
            'graph_match': graph_match,
            'status': status,
            'reason': reason,
            'success': success
        }

    except requests.exceptions.Timeout:
        print(f"  [ERROR] Request timeout after {REQUEST_TIMEOUT}s")
        return {
            'category': category,
            'question': question,
            'status': 'ERROR',
            'reason': 'Request timeout',
            'sql_valid': False,
            'graph_match': False
        }
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Request failed: {str(e)}")
        return {
            'category': category,
            'question': question,
            'status': 'ERROR',
            'reason': f'Request error: {str(e)}',
            'sql_valid': False,
            'graph_match': False
        }
    except Exception as e:
        print(f"  [ERROR] Unexpected error: {str(e)}")
        return {
            'category': category,
            'question': question,
            'status': 'ERROR',
            'reason': f'Unexpected error: {str(e)}',
            'sql_valid': False,
            'graph_match': False
        }

def print_summary(results: list):
    """Print detailed summary of test results."""
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    warnings = sum(1 for r in results if r['status'] == 'WARN')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')

    sql_valid = sum(1 for r in results if r.get('sql_valid', False))
    graph_match = sum(1 for r in results if r.get('graph_match', False))

    print(f"\nTotal Queries Tested: {total}")
    print(f"  PASSED:   {passed:4d} ({passed/total*100:5.1f}%)")
    print(f"  WARNINGS: {warnings:4d} ({warnings/total*100:5.1f}%)")
    print(f"  FAILED:   {failed:4d} ({failed/total*100:5.1f}%)")
    print(f"  ERRORS:   {errors:4d} ({errors/total*100:5.1f}%)")

    print(f"\nSQL Generation: {sql_valid}/{total} ({sql_valid/total*100:.1f}%)")
    print(f"Graph Type Match: {graph_match}/{total} ({graph_match/total*100:.1f}%)")

    # Category breakdown
    print("\n" + "-" * 80)
    print("CATEGORY BREAKDOWN:")
    print("-" * 80)

    categories = defaultdict(lambda: {'total': 0, 'passed': 0, 'warnings': 0, 'failed': 0, 'errors': 0})
    for r in results:
        cat = r.get('category', 'Unknown')
        categories[cat]['total'] += 1
        if r['status'] == 'PASS':
            categories[cat]['passed'] += 1
        elif r['status'] == 'WARN':
            categories[cat]['warnings'] += 1
        elif r['status'] == 'FAIL':
            categories[cat]['failed'] += 1
        else:
            categories[cat]['errors'] += 1

    for cat in sorted(categories.keys()):
        stats = categories[cat]
        pass_rate = stats['passed'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"\n  {cat}:")
        print(f"    Total: {stats['total']}, Passed: {stats['passed']} ({pass_rate:.1f}%), "
              f"Warnings: {stats['warnings']}, Failed: {stats['failed']}, Errors: {stats['errors']}")

    # Issues found
    print("\n" + "-" * 80)
    print("ISSUES FOUND:")
    print("-" * 80)

    sql_failures = [r for r in results if not r.get('sql_valid', False)]
    if sql_failures:
        print(f"\nSQL Validation Failures ({len(sql_failures)}):")
        for r in sql_failures[:10]:  # Show first 10
            print(f"  - {r['question'][:70]}")
            print(f"    Reason: {r.get('sql_reason', 'Unknown')}")

    graph_mismatches = [r for r in results if not r.get('graph_match', False) and r.get('sql_valid', False)]
    if graph_mismatches:
        print(f"\nGraph Type Mismatches ({len(graph_mismatches)}):")
        for r in graph_mismatches[:10]:  # Show first 10
            print(f"  - {r['question'][:70]}")
            print(f"    Expected: {r['expected_graph']}, Got: {r['actual_graph']}")

    print("\n" + "=" * 80)

def save_results(results: list, timestamp: str):
    """Save results to JSON and CSV files."""
    # JSON report
    json_filename = f"validation_results_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed JSON report saved to: {json_filename}")

    # CSV report
    csv_filename = f"validation_results_{timestamp}.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    print(f"CSV report saved to: {csv_filename}")

def main():
    """Main test execution."""
    print("=" * 80)
    print("COMPREHENSIVE QUERY VALIDATION TEST")
    print("=" * 80)
    print(f"\nStarting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API: {NLP_API_URL}")
    print(f"Rate limiting: {DELAY_BETWEEN_REQUESTS}s between requests (~{60/DELAY_BETWEEN_REQUESTS:.0f} req/min)")

    # Load queries
    print("\nLoading queries from test_queries.tsv...")
    queries = load_queries_from_tsv('test_queries.tsv')

    if not queries:
        print("[ERROR] No queries loaded. Please check test_queries.tsv file.")
        return

    print(f"Loaded {len(queries)} queries (excluding {len(MANUALLY_VALIDATED)} manually validated)")
    print(f"Estimated time: {len(queries) * DELAY_BETWEEN_REQUESTS / 60:.1f} minutes")
    print("\nStarting tests...\n")

    # Run tests
    results = []
    start_time = time.time()

    for i, query in enumerate(queries, 1):
        result = test_query(
            query['category'],
            query['question'],
            query['expected_sql'],
            query['expected_graph'],
            i,
            len(queries)
        )
        results.append(result)

        # Rate limiting delay
        if i < len(queries):
            time.sleep(DELAY_BETWEEN_REQUESTS)

    elapsed_time = time.time() - start_time

    # Print summary
    print_summary(results)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_results(results, timestamp)

    print(f"\nTotal time: {elapsed_time/60:.1f} minutes")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
