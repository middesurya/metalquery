#!/usr/bin/env python3
"""Test visualization goal finder fixes for graph type inference."""

import sys
sys.path.append('nlp_service')
sys.path.append('nlp_service/visualization')

from viz_goal_finder import VizGoalFinder

# Test cases from manual testing
TEST_CASES = [
    {
        "query": "Show downtime by furnace",
        "data_summary": {
            "row_count": 1,
            "columns": ["furnace_no", "total_downtime_hours"],
            "numeric_columns": ["total_downtime_hours"],
            "categorical_columns": ["furnace_no"],
            "temporal_columns": [],
            "is_single_value": True,
            "has_time_series": False,
        },
        "expected_chart": "bar",
        "issue": "Query 1 - Was getting KPI card, should get bar chart"
    },
    {
        "query": "What is the downtime by furnace?",
        "data_summary": {
            "row_count": 2,
            "columns": ["furnace_no", "total_downtime_hours"],
            "numeric_columns": ["total_downtime_hours"],
            "categorical_columns": ["furnace_no"],
            "temporal_columns": [],
            "is_single_value": False,
            "has_time_series": False,
        },
        "expected_chart": "bar",
        "issue": "Query 2 - Already working correctly"
    },
    {
        "query": "Show total downtime by furnace",
        "data_summary": {
            "row_count": 2,
            "columns": ["furnace_no", "total_downtime_hours"],
            "numeric_columns": ["total_downtime_hours"],
            "categorical_columns": ["furnace_no"],
            "temporal_columns": [],
            "is_single_value": False,
            "has_time_series": False,
        },
        "expected_chart": "bar",
        "issue": "Query 3 - Already working correctly"
    },
    {
        "query": "Display downtime by shift",
        "data_summary": {
            "row_count": 3,
            "columns": ["shift_no", "total_downtime_hours"],
            "numeric_columns": ["total_downtime_hours"],
            "categorical_columns": ["shift_no"],
            "temporal_columns": [],
            "is_single_value": False,
            "has_time_series": False,
        },
        "expected_chart": "bar",
        "issue": "Query 4 - Already working correctly"
    },
    {
        "query": "Show safety incidents by furnace",
        "data_summary": {
            "row_count": 2,
            "columns": ["furnace_no", "incident_count"],
            "numeric_columns": ["incident_count"],
            "categorical_columns": ["furnace_no"],
            "temporal_columns": [],
            "is_single_value": False,
            "has_time_series": False,
        },
        "expected_chart": "bar",
        "issue": "Query 5 - Already working correctly"
    },
    {
        "query": "Show cycle time by furnace",
        "data_summary": {
            "row_count": 50,
            "columns": ["furnace_no", "cycle_time"],
            "numeric_columns": ["cycle_time"],
            "categorical_columns": ["furnace_no"],
            "temporal_columns": [],
            "is_single_value": False,
            "has_time_series": False,
        },
        "expected_chart": "bar",
        "issue": "Query 6 - Already working correctly (50 rows)"
    },
    {
        "query": "Show taps by furnace",
        "data_summary": {
            "row_count": 25,
            "columns": ["furnace_no", "tap_count"],
            "numeric_columns": ["tap_count"],
            "categorical_columns": ["furnace_no"],
            "temporal_columns": [],
            "is_single_value": False,
            "has_time_series": False,
        },
        "expected_chart": "bar",
        "issue": "Query 7 - Was getting table, should get bar chart (25 rows)"
    },
    {
        "query": "Display taps by furnace",
        "data_summary": {
            "row_count": 25,
            "columns": ["furnace_no", "tap_count"],
            "numeric_columns": ["tap_count"],
            "categorical_columns": ["furnace_no"],
            "temporal_columns": [],
            "is_single_value": False,
            "has_time_series": False,
        },
        "expected_chart": "bar",
        "issue": "Query 8 - Was getting table, should get bar chart (25 rows)"
    },
]

print("=" * 80)
print("VISUALIZATION GOAL FINDER - FIX VALIDATION TEST")
print("=" * 80)
print("\nTesting fixes:")
print("  1. Rule 1 (PRIORITY): 'by X' patterns now checked BEFORE single-value detection")
print("  2. Rule 7: Extended row count threshold from 20 to 50")
print("=" * 80)

finder = VizGoalFinder()
passed = 0
failed = 0

for i, test_case in enumerate(TEST_CASES, 1):
    print(f"\n[Test {i}/8] {test_case['query']}")
    print(f"  Rows: {test_case['data_summary']['row_count']}")
    print(f"  Issue: {test_case['issue']}")

    result = finder.find_goal_heuristic(test_case['data_summary'], test_case['query'])

    actual_chart = result.get('chart_type')
    expected_chart = test_case['expected_chart']

    if actual_chart == expected_chart:
        print(f"  [PASS] Got '{actual_chart}' chart (expected '{expected_chart}')")
        passed += 1
    else:
        print(f"  [FAIL] Got '{actual_chart}' chart (expected '{expected_chart}')")
        print(f"     Full result: {result}")
        failed += 1

print("\n" + "=" * 80)
print(f"RESULTS: {passed}/{len(TEST_CASES)} passed, {failed}/{len(TEST_CASES)} failed")
print("=" * 80)

if failed == 0:
    print("\n[SUCCESS] ALL TESTS PASSED! Graph type inference fixes are working correctly.")
    print("\nFixed issues:")
    print("  - Query 1: 'by furnace' with 1 row now returns bar chart (not KPI card)")
    print("  - Queries 7-8: 'by furnace' with 25 rows now return bar chart (not table)")
else:
    print(f"\n[WARNING] {failed} test(s) failed. Additional fixes may be needed.")
    sys.exit(1)
