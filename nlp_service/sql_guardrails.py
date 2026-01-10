"""
SQL Security Guardrails
Validates generated SQL to ensure it meets strict read-only security requirements.
"""

import re
import sqlparse
from typing import Tuple, Set


class SQLGuardrails:
    """
    Security guardrails for validating SQL queries.
    Allows ONLY read-only SELECT queries (including WITH/CTEs).
    """

    # ❌ SQL operations that must NEVER be allowed
    # Note: REPLACE removed because REPLACE() is a safe string function.
    # The check for SELECT-only queries already prevents REPLACE INTO statements.
    BLOCKED_KEYWORDS = {
        "INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER",
        "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE", "CALL",
        "MERGE", "UPSERT", "LOCK", "UNLOCK",
        "INTO", "COPY", "LOAD", "SET", "DECLARE",  # Additional security
    }

    # ❌ Patterns commonly used in SQL injection or privilege escalation
    DANGEROUS_PATTERNS = [
        r";\s*--",                 # Statement chaining
        r"--\s*$",                 # Trailing comment
        r"/\*.*?\*/",              # Block comments
        r";\s*\w+",                # Multiple statements
        r"pg_catalog",             # PostgreSQL system catalog
        r"information_schema",     # Information schema
        r"\bpg_\w+",               # PostgreSQL internal tables
    ]

    def __init__(self, allowed_tables: Set[str] = None):
        self.allowed_tables = {t.lower() for t in allowed_tables} if allowed_tables else set()

    def validate(self, sql: str) -> Tuple[bool, str]:
        """
        Validate SQL against security rules.

        Returns:
            (True, "Query validated successfully") OR (False, "Error message")
        """

        if not sql or not sql.strip():
            return False, "Empty SQL query"

        # Remove SQL comments (single-line -- and multi-line /* */)
        # This allows LLM to add helpful comments without triggering security checks
        sql_no_comments = re.sub(r'--[^\n]*', '', sql)  # Remove -- comments
        sql_no_comments = re.sub(r'/\*.*?\*/', '', sql_no_comments, flags=re.DOTALL)  # Remove /* */ comments

        # Normalize SQL (collapse whitespace)
        sql_clean = re.sub(r"\s+", " ", sql_no_comments).strip()
        sql_upper = sql_clean.upper()

        # ✅ Allow SELECT and WITH only
        if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
            return False, "Only read-only SELECT queries are allowed"

        # ❌ Block dangerous SQL keywords
        for keyword in self.BLOCKED_KEYWORDS:
            if re.search(rf"\b{keyword}\b", sql_upper):
                return False, f"Blocked SQL operation detected: {keyword}"

        # ❌ Block dangerous SQL patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, sql_upper, re.IGNORECASE | re.DOTALL):
                return False, "Dangerous SQL pattern detected"

        # ❌ Block multiple SQL statements
        parsed = sqlparse.parse(sql_clean)
        if len(parsed) != 1:
            return False, "Multiple SQL statements are not allowed"

        # ✅ Validate statement type
        statement = parsed[0]
        stmt_type = statement.get_type()

        # sqlparse returns UNKNOWN for WITH (CTE) queries
        if stmt_type not in ("SELECT", "UNKNOWN"):
            return False, "Only read-only SELECT queries are allowed"

        # ✅ Enforce table allowlist (if provided)
        if self.allowed_tables:
            tables_in_query = self._extract_tables(sql_clean)
            unauthorized = tables_in_query - self.allowed_tables
            if unauthorized:
                return False, f"Unauthorized tables accessed: {', '.join(unauthorized)}"

        return True, "Query validated successfully"

    def _extract_tables(self, sql: str) -> Set[str]:
        """
        Extract table names from FROM and JOIN clauses.
        Excludes EXTRACT(... FROM ...) function syntax.
        """
        tables = set()
        
        # First, remove EXTRACT(... FROM ...) to avoid false positives
        # EXTRACT(MONTH FROM date) should NOT extract 'date' as a table
        sql_cleaned = re.sub(
            r"\bEXTRACT\s*\([^)]*\bFROM\b[^)]*\)",
            "",
            sql,
            flags=re.IGNORECASE
        )
        
        # Also remove DATE_TRUNC and similar functions that use FROM
        sql_cleaned = re.sub(
            r"\bDATE_TRUNC\s*\([^)]*\)",
            "",
            sql_cleaned,
            flags=re.IGNORECASE
        )

        patterns = [
            r"\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            r"\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, sql_cleaned, re.IGNORECASE)
            tables.update(m.lower() for m in matches)

        return tables

    def sanitize_for_display(self, sql: str) -> str:
        """
        Sanitize SQL for safe logging or display.
        """
        return re.sub(
            r"password\s*=\s*'[^']*'",
            "password='***'",
            sql,
            flags=re.IGNORECASE
        )


# ✅ Singleton instance
guardrails = SQLGuardrails()


def validate_sql(sql: str, allowed_tables: Set[str] = None) -> Tuple[bool, str]:
    """
    Convenience validation function.
    """
    validator = SQLGuardrails(allowed_tables=allowed_tables)
    return validator.validate(sql)
