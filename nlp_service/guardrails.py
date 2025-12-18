"""
SQL Security Guardrails
Validates generated SQL to ensure it meets security requirements.
"""
import re
import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML
from typing import Tuple, List, Set


class SQLGuardrails:
    """
    Security guardrails for validating SQL queries.
    Ensures only safe SELECT queries are executed.
    """
    
    # Dangerous SQL keywords that should NEVER appear
    BLOCKED_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER',
        'CREATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', 'CALL',
        'MERGE', 'UPSERT', 'REPLACE', 'LOCK', 'UNLOCK'
    }
    
    # Dangerous patterns (SQL injection attempts)
    DANGEROUS_PATTERNS = [
        r';\s*--',           # Statement terminator followed by comment
        r'--\s*$',           # Trailing comment
        r'/\*.*\*/',         # Block comments
        r';\s*\w+',          # Multiple statements
        r'UNION\s+ALL\s+SELECT.*FROM\s+pg_',  # System table access via UNION
        r'pg_catalog',       # Direct system catalog access
        r'information_schema',  # Information schema access
        r'pg_\w+',           # PostgreSQL system tables
    ]
    
    def __init__(self, allowed_tables: Set[str] = None, allowed_columns: Set[str] = None):
        """
        Initialize guardrails with optional table/column allowlists.
        
        Args:
            allowed_tables: Set of table names that can be queried
            allowed_columns: Set of column names that can be accessed
        """
        self.allowed_tables = allowed_tables or set()
        self.allowed_columns = allowed_columns or set()
    
    def validate(self, sql: str) -> Tuple[bool, str]:
        """
        Validate SQL query against security rules.
        """
        if not sql or not sql.strip():
            return False, "Empty SQL query"
        
        # Normalize: strip and get first word
        sql = sql.strip()
        sql_upper = sql.upper()
        
        # Check 1: Must be a SELECT
        if not sql_upper.startswith('SELECT') and not sql_upper.startswith('WITH'):
            # Allow common CTEs if they are selects
            # But for simplicity, let's just stick to SELECT for now
            if not re.match(r'^\s*(SELECT|WITH)', sql_upper):
                return False, "Only SELECT queries are allowed"
        
        # Check 2: No blocked keywords (using word boundaries)
        for keyword in self.BLOCKED_KEYWORDS:
            pattern = rf'\b{keyword}\b'
            if re.search(pattern, sql_upper):
                return False, f"Blocked keyword detected: {keyword}"
        
        # Check 3: No dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, sql_upper, re.IGNORECASE | re.DOTALL):
                return False, f"Dangerous pattern detected"
        
        # Check 4: Use sqlparse for structural validation
        try:
            parsed = sqlparse.parse(sql)
            if not parsed:
                return False, "Could not parse SQL"
            
            # Check for multiple statements
            if len(parsed) > 1:
                # If there are multiple, check if they are just whitespace/comments
                real_statements = [s for s in parsed if s.get_type() != 'UNKNOWN' or str(s).strip()]
                if len(real_statements) > 1:
                    return False, "Multiple SQL statements not allowed"
            
            statement = parsed[0]
            # Ensure it's a SELECT type
            if statement.get_type() != 'SELECT':
                return False, "Only SELECT statements are allowed"
                
        except Exception as e:
            return False, f"SQL parsing error: {str(e)}"
        
        # Check 5: Table allowlist (if configured)
        if self.allowed_tables:
            tables_in_query = self._extract_tables(sql)
            if tables_in_query:
                unauthorized = tables_in_query - self.allowed_tables
                if unauthorized:
                    return False, f"Unauthorized tables: {', '.join(unauthorized)}"
        
        return True, "Query validated successfully"
    
    def _extract_tables(self, sql: str) -> Set[str]:
        """
        Extract table names from SQL query.
        
        Args:
            sql: The SQL query
            
        Returns:
            Set of table names found in the query
        """
        tables = set()
        
        # Simple regex-based extraction (works for most cases)
        # Pattern: FROM table_name or JOIN table_name
        patterns = [
            r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            tables.update(match.lower() for match in matches)
        
        return tables
    
    def sanitize_for_display(self, sql: str) -> str:
        """
        Sanitize SQL for safe display (remove sensitive info).
        
        Args:
            sql: The SQL query
            
        Returns:
            Sanitized SQL string
        """
        # Remove any embedded credentials or sensitive patterns
        sanitized = re.sub(r"password\s*=\s*'[^']*'", "password='***'", sql, flags=re.IGNORECASE)
        return sanitized


# Singleton instance with default configuration
guardrails = SQLGuardrails()


def validate_sql(sql: str, allowed_tables: Set[str] = None) -> Tuple[bool, str]:
    """
    Convenience function to validate SQL.
    
    Args:
        sql: The SQL query to validate
        allowed_tables: Optional set of allowed table names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    validator = SQLGuardrails(allowed_tables=allowed_tables)
    return validator.validate(sql)
