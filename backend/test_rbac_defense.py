"""
Test Script: RBAC Defense-in-Depth - Unauthorized Table Blocking

This tests the scenario where even if the LLM generates SQL with unauthorized tables,
Django's validation layer blocks it.

Run: python manage.py shell < test_rbac_defense.py
Or:  python test_rbac_defense.py (if Django settings configured)
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from chatbot.views import extract_tables_from_sql, validate_sql_tables

print("=" * 60)
print("RBAC DEFENSE-IN-DEPTH TEST")
print("Scenario: LLM generates unauthorized table -> Django blocks")
print("=" * 60)


# Test 1: extract_tables_from_sql function
print("\n[TEST 1] extract_tables_from_sql()")
print("-" * 40)

test_cases_extract = [
    ("SELECT * FROM kpi_oee_data", {"kpi_oee_data"}),
    ("SELECT * FROM users_user", {"users_user"}),
    ("SELECT a.* FROM kpi_oee_data a JOIN plant_plant b ON a.plant_id = b.id",
     {"kpi_oee_data", "plant_plant"}),
    ("SELECT EXTRACT(MONTH FROM date) FROM kpi_yield_data", {"kpi_yield_data"}),
    ("SELECT * FROM kpi_oee_data WHERE date > '2024-01-01'", {"kpi_oee_data"}),
]

for sql, expected in test_cases_extract:
    result = extract_tables_from_sql(sql)
    status = "PASS" if result == expected else "FAIL"
    print(f"  {status}: {sql[:50]}...")
    if result != expected:
        print(f"       Expected: {expected}, Got: {result}")


# Test 2: validate_sql_tables - User with limited permissions
print("\n[TEST 2] validate_sql_tables() - Defense in Depth")
print("-" * 40)

# Simulate a user who only has access to OEE and yield tables
limited_allowed_tables = {
    "kpi_overall_equipment_efficiency_data",
    "kpi_yield_data",
    "plant_plant",
}

test_cases_validate = [
    # (SQL, should_pass, description)
    (
        "SELECT * FROM kpi_overall_equipment_efficiency_data",
        True,
        "Authorized single table"
    ),
    (
        "SELECT * FROM kpi_overall_equipment_efficiency_data a JOIN plant_plant b ON a.plant_id = b.id",
        True,
        "Authorized multiple tables"
    ),
    (
        "SELECT * FROM kpi_downtime_data",  # User doesn't have DOWNTIME KPI
        False,
        "UNAUTHORIZED: kpi_downtime_data (no DOWNTIME permission)"
    ),
    (
        "SELECT * FROM users_user",  # System table - never exposed
        False,
        "UNAUTHORIZED: users_user (system table)"
    ),
    (
        "SELECT * FROM kpi_overall_equipment_efficiency_data a JOIN kpi_downtime_data b ON a.date = b.date",
        False,
        "UNAUTHORIZED: Mixed authorized + unauthorized tables"
    ),
    (
        "SELECT * FROM core_process_tap_production",  # User doesn't have TAP_PROC
        False,
        "UNAUTHORIZED: core_process_tap_production (no TAP_PROC permission)"
    ),
]

all_passed = True
for sql, should_pass, description in test_cases_validate:
    is_valid, error = validate_sql_tables(sql, limited_allowed_tables)

    if should_pass:
        status = "PASS" if is_valid else "FAIL"
        if not is_valid:
            all_passed = False
            print(f"  {status}: {description}")
            print(f"       Unexpected error: {error}")
        else:
            print(f"  {status}: {description}")
    else:
        # Expected to be blocked
        status = "PASS" if not is_valid else "FAIL"
        if is_valid:
            all_passed = False
            print(f"  {status}: {description}")
            print(f"       Should have been BLOCKED but was allowed!")
        else:
            print(f"  {status}: {description}")
            print(f"       Correctly blocked: {error}")


# Test 3: Simulate full attack scenario
print("\n[TEST 3] Full Attack Scenario Simulation")
print("-" * 40)

print("  Scenario: User with only OEE permission asks about downtime")
print("  If LLM somehow generates: SELECT * FROM kpi_downtime_data")
print()

attack_sql = "SELECT AVG(downtime_hours) FROM kpi_downtime_data WHERE date >= '2024-01-01'"
is_valid, error = validate_sql_tables(attack_sql, limited_allowed_tables)

if not is_valid:
    print(f"  PASS: Django blocked unauthorized access!")
    print(f"       Error returned: {error}")
else:
    print(f"  FAIL: Unauthorized access was NOT blocked!")
    all_passed = False


# Test 4: Edge cases
print("\n[TEST 4] Edge Cases")
print("-" * 40)

edge_cases = [
    # SQL with table name in different case
    ("SELECT * FROM KPI_DOWNTIME_DATA", False, "Case insensitive check"),
    # Subquery with unauthorized table
    ("SELECT * FROM kpi_yield_data WHERE plant_id IN (SELECT id FROM users_user)", False, "Subquery attack"),
    # Complex JOIN chain
    ("SELECT * FROM kpi_yield_data a JOIN plant_plant b ON 1=1 LEFT JOIN kpi_energy_used_data c ON 1=1", False, "JOIN chain with unauthorized"),
]

for sql, should_pass, description in edge_cases:
    is_valid, error = validate_sql_tables(sql, limited_allowed_tables)
    expected_blocked = not should_pass
    actual_blocked = not is_valid

    if expected_blocked == actual_blocked:
        status = "PASS"
    else:
        status = "FAIL"
        all_passed = False

    print(f"  {status}: {description}")
    if not is_valid:
        print(f"       Blocked: {error}")


# Summary
print("\n" + "=" * 60)
if all_passed:
    print("ALL TESTS PASSED - Defense-in-depth is working!")
    print("Django successfully blocks unauthorized table access.")
else:
    print("SOME TESTS FAILED - Review the failures above.")
print("=" * 60)
