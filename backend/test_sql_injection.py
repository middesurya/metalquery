"""
Test Script: SQL Injection Defense
Tests that SQLValidator blocks all common SQL injection patterns.

Run: python test_sql_injection.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from chatbot.views import SQLValidator

print("=" * 70)
print("SQL INJECTION DEFENSE TEST")
print("Testing SQLValidator against common injection patterns")
print("=" * 70)

# Test categories
test_cases = []

# ============================================================
# Category 1: Basic SQL Injection - DROP/DELETE/UPDATE
# ============================================================
test_cases.append(("DROP TABLE Attack", [
    ("SELECT * FROM users; DROP TABLE users;--", False, "Classic DROP TABLE"),
    ("SELECT * FROM kpi_oee_data; DROP TABLE kpi_oee_data", False, "DROP with semicolon"),
    ("DROP TABLE users", False, "Direct DROP"),
], "Destructive Commands"))

# ============================================================
# Category 2: Data Modification Attacks
# ============================================================
test_cases.append(("Data Modification", [
    ("INSERT INTO users VALUES (1, 'hacker')", False, "Direct INSERT"),
    ("UPDATE users SET password='hacked'", False, "Direct UPDATE"),
    ("DELETE FROM users WHERE 1=1", False, "Direct DELETE"),
    ("SELECT * FROM users; INSERT INTO users VALUES(1,'x')", False, "SELECT + INSERT"),
    ("SELECT * FROM users; UPDATE users SET admin=1", False, "SELECT + UPDATE"),
    ("SELECT * FROM users; DELETE FROM users", False, "SELECT + DELETE"),
], "Data Modification"))

# ============================================================
# Category 3: System Table Access
# ============================================================
test_cases.append(("System Table Access", [
    ("SELECT * FROM pg_tables", False, "PostgreSQL pg_tables"),
    ("SELECT * FROM pg_user", False, "PostgreSQL pg_user"),
    ("SELECT * FROM pg_shadow", False, "PostgreSQL pg_shadow (passwords)"),
    ("SELECT * FROM information_schema.tables", False, "information_schema.tables"),
    ("SELECT * FROM information_schema.columns", False, "information_schema.columns"),
    ("SELECT table_name FROM information_schema.tables", False, "Schema enumeration"),
], "System Tables"))

# ============================================================
# Category 4: Comment-Based Injection
# ============================================================
test_cases.append(("Comment Injection", [
    ("SELECT * FROM users--", False, "Single-line comment"),
    ("SELECT * FROM users -- WHERE admin=0", False, "Comment to bypass WHERE"),
    ("SELECT * FROM users/**/WHERE/**/1=1", False, "Block comment"),
    ("SELECT * FROM users /* admin bypass */", False, "Inline block comment"),
], "SQL Comments"))

# ============================================================
# Category 5: Multiple Statement Injection
# ============================================================
test_cases.append(("Multiple Statements", [
    ("SELECT 1; SELECT 2", False, "Two SELECT statements"),
    ("SELECT * FROM a; SELECT * FROM b;", False, "Multiple SELECTs with trailing"),
    ("SELECT * FROM users;--", False, "Statement with comment"),
], "Statement Stacking"))

# ============================================================
# Category 6: Stored Procedure / Function Calls
# ============================================================
test_cases.append(("Stored Procedures", [
    ("EXEC xp_cmdshell 'whoami'", False, "SQL Server xp_cmdshell"),
    ("EXECUTE sp_configure", False, "SQL Server sp_configure"),
    ("CALL my_procedure()", False, "CALL procedure"),
    ("SELECT * FROM users; EXEC master..xp_cmdshell 'dir'", False, "SELECT + EXEC"),
], "Procedure Execution"))

# ============================================================
# Category 7: Privilege Escalation
# ============================================================
test_cases.append(("Privilege Escalation", [
    ("GRANT ALL ON users TO hacker", False, "GRANT privileges"),
    ("REVOKE SELECT ON users FROM public", False, "REVOKE privileges"),
    ("CREATE USER hacker WITH PASSWORD 'pass'", False, "CREATE USER"),
    ("ALTER USER admin WITH SUPERUSER", False, "ALTER USER"),
], "Privilege Commands"))

# ============================================================
# Category 8: Data Exfiltration via COPY/LOAD
# ============================================================
test_cases.append(("Data Exfiltration", [
    ("COPY users TO '/tmp/users.csv'", False, "COPY to file"),
    ("COPY (SELECT * FROM users) TO '/tmp/data'", False, "COPY SELECT"),
    ("LOAD DATA INFILE '/etc/passwd' INTO TABLE t", False, "LOAD DATA"),
    ("SELECT * INTO OUTFILE '/tmp/data' FROM users", False, "SELECT INTO OUTFILE"),
], "File Operations"))

# ============================================================
# Category 9: SET/DECLARE Attacks
# ============================================================
test_cases.append(("SET/DECLARE", [
    ("SET @a = 1; SELECT @a", False, "SET variable"),
    ("DECLARE @cmd VARCHAR(100)", False, "DECLARE variable"),
    ("SET ROLE admin", False, "SET ROLE"),
], "Variable Manipulation"))

# ============================================================
# Category 10: Valid SELECT Queries (Should PASS)
# ============================================================
test_cases.append(("Valid Queries", [
    ("SELECT * FROM kpi_oee_data", True, "Simple SELECT"),
    ("SELECT AVG(oee_percentage) FROM kpi_oee_data", True, "SELECT with aggregate"),
    ("SELECT * FROM kpi_oee_data WHERE date > '2024-01-01'", True, "SELECT with WHERE"),
    ("SELECT a.*, b.plant_name FROM kpi_oee_data a JOIN plant_plant b ON a.plant_id = b.id", True, "SELECT with JOIN"),
    ("SELECT EXTRACT(MONTH FROM date) AS month FROM kpi_oee_data", True, "SELECT with EXTRACT"),
    ("SELECT * FROM kpi_oee_data ORDER BY date DESC LIMIT 10", True, "SELECT with ORDER/LIMIT"),
], "Valid Queries (Should Pass)"))

# ============================================================
# Run Tests
# ============================================================
total_tests = 0
passed_tests = 0
failed_tests = []

for category_name, cases, description in test_cases:
    print(f"\n[{category_name}] {description}")
    print("-" * 50)

    for sql, should_pass, test_name in cases:
        total_tests += 1
        is_valid, error = SQLValidator.validate(sql)

        if should_pass:
            if is_valid:
                print(f"  PASS: {test_name}")
                passed_tests += 1
            else:
                print(f"  FAIL: {test_name}")
                print(f"       Expected: VALID, Got: {error}")
                failed_tests.append((test_name, sql, "Should be valid", error))
        else:
            if not is_valid:
                print(f"  PASS: {test_name} -> Blocked: {error}")
                passed_tests += 1
            else:
                print(f"  FAIL: {test_name}")
                print(f"       Expected: BLOCKED, but was allowed!")
                print(f"       SQL: {sql}")
                failed_tests.append((test_name, sql, "Should be blocked", "Allowed"))

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 70)
print(f"RESULTS: {passed_tests}/{total_tests} tests passed")
print("=" * 70)

if failed_tests:
    print("\nFailed Tests:")
    for name, sql, expected, actual in failed_tests:
        print(f"  - {name}: {expected}, got {actual}")
        print(f"    SQL: {sql[:60]}...")
else:
    print("\nALL TESTS PASSED!")
    print("SQLValidator successfully blocks all SQL injection patterns.")

print("=" * 70)
