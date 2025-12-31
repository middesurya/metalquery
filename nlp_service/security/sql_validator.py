"""
SQL Injection Validator - Multi-layer SQL injection prevention
"""

import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SQLInjectionValidator:
    """
    Multi-layer SQL injection prevention for NLP2SQL systems.
    """
    
    def __init__(self):
        self.dangerous_keywords = {
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE',
            'EXEC', 'EXECUTE', 'SCRIPT', 'DECLARE', 'CAST',
            'XP_', 'SP_', 'SHUTDOWN', 'GRANT', 'REVOKE'
        }
        
        self.allowed_tables = {
            # KPI Tables
            'kpi_overall_equipment_efficiency_data',
            'kpi_defect_rate_data',
            'kpi_energy_efficiency_data',
            'kpi_energy_used_data',
            'kpi_downtime_data',
            'kpi_yield_data',
            'kpi_quantity_produced_data',
            'kpi_first_pass_yield_data',
            'kpi_rework_rate_data',
            'kpi_resource_capacity_utilization_data',
            'kpi_output_rate_data',
            'kpi_production_efficiency_data',
            'kpi_on_time_delivery_data',
            'kpi_cycle_time_data',
            'kpi_mean_time_between_failures_data',
            'kpi_mean_time_to_repair_data',
            'kpi_mean_time_between_stoppages_data',
            'kpi_maintenance_compliance_data',
            'kpi_planned_maintenance_data',
            'kpi_safety_incidents_reported_data',
            # Core Process Tables
            'core_process_tap_production',
            'core_process_tap_process',
            'core_process_tap_grading',
            # Log Book Tables
            'log_book_furnace_down_time_event',
            'log_book_reasons',
            'log_book_downtime_type_master',
            # Furnace Tables
            'furnace_furnaceconfig',
            'furnace_config_parameters',
            # Master Tables
            'plant_plant',
        }
        
        self.allowed_operations = {'SELECT'}
    
    def validate_sql(self, sql_query: str) -> Dict[str, any]:
        """
        Comprehensive SQL validation.
        Returns: {is_safe: bool, issues: [list], score: float}
        """
        issues = []
        score = 0.0
        
        # Check 1: Basic syntax validation
        if not sql_query or not sql_query.strip():
            return {'is_safe': False, 'issues': ['Empty SQL query'], 'score': 1.0}
        
        sql_upper = sql_query.upper().strip()
        
        # Check 2: Verify operation type
        operation = self._get_operation(sql_upper)
        if operation not in self.allowed_operations:
            issues.append(f"Only SELECT allowed, got {operation}")
            score += 0.4
        
        # Check 3: Check for dangerous keywords
        dangerous = self._check_dangerous_keywords(sql_upper)
        if dangerous:
            issues.append(f"Dangerous keywords detected: {dangerous}")
            score += 0.5
        
        # Check 4: Verify table access
        tables = self._extract_tables(sql_query)
        unknown_tables = [t for t in tables if t.lower() not in self.allowed_tables]
        if unknown_tables:
            issues.append(f"Unauthorized table access: {unknown_tables}")
            score += 0.3
        
        # Check 5: Detect injection patterns
        injection_patterns = self._check_injection_patterns(sql_query)
        if injection_patterns:
            issues.append(f"Potential SQL injection: {injection_patterns}")
            score += 0.6
        
        # Check 6: Check for stacked queries
        if self._has_stacked_queries(sql_query):
            issues.append("Stacked queries detected")
            score += 0.5
        
        result = {
            'is_safe': score < 0.3 and len(issues) == 0,
            'issues': issues,
            'score': min(score, 1.0),
            'tables': tables,
            'operation': operation
        }
        
        if not result['is_safe']:
            logger.warning(f"🚨 SQL VALIDATION FAILED: {issues}")
        
        return result
    
    def _get_operation(self, sql_upper: str) -> str:
        """Extract main SQL operation."""
        operations = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE']
        for op in operations:
            if sql_upper.startswith(op):
                return op
        return "UNKNOWN"
    
    def _check_dangerous_keywords(self, query: str) -> List[str]:
        """Find dangerous SQL keywords."""
        found = []
        for keyword in self.dangerous_keywords:
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, query, re.IGNORECASE):
                found.append(keyword)
        return found
    
    def _extract_tables(self, sql_query: str) -> List[str]:
        """Extract table names from query."""
        tables = []
        
        # Pattern for FROM clause
        from_match = re.findall(r'\bFROM\s+(\w+)', sql_query, re.IGNORECASE)
        tables.extend(from_match)
        
        # Pattern for JOIN clauses
        join_match = re.findall(r'\bJOIN\s+(\w+)', sql_query, re.IGNORECASE)
        tables.extend(join_match)
        
        return list(set(tables))
    
    def _check_injection_patterns(self, query: str) -> List[str]:
        """Detect common SQL injection patterns."""
        patterns = [
            (r"'\s*OR\s*'1'\s*=\s*'1", "OR-based injection"),
            (r"'\s*OR\s*1\s*=\s*1", "OR-based injection"),
            (r";\s*DROP\s+TABLE", "DROP TABLE injection"),
            (r"UNION\s+ALL\s+SELECT", "UNION-based injection"),
            (r"UNION\s+SELECT", "UNION-based injection"),
            (r"--\s*$", "Comment-based injection"),
            (r"/\*.*\*/", "Multiline comment injection"),
            (r"<script", "Script tag injection"),
            (r"\\x[0-9a-f]+", "Hex encoding injection"),
            (r"CHAR\s*\(", "CHAR function injection"),
            (r"CONCAT\s*\(.*SELECT", "CONCAT injection"),
        ]
        
        found = []
        for pattern, name in patterns:
            if re.search(pattern, query, re.IGNORECASE | re.MULTILINE):
                found.append(name)
        return found
    
    def _has_stacked_queries(self, query: str) -> bool:
        """Check for stacked queries (multiple statements)."""
        # Count semicolons not inside quotes
        semicolons = re.findall(r';(?=(?:[^\']*\'[^\']*\')*[^\']*$)', query)
        return len(semicolons) > 1


class SQLQuerySanitizer:
    """
    Sanitizes SQL queries to remove potentially dangerous content.
    """
    
    @staticmethod
    def sanitize(sql: str) -> str:
        """
        Remove potentially dangerous content from SQL.
        """
        # Remove comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # Remove multiple semicolons
        sql = re.sub(r';\s*;', ';', sql)
        
        # Remove trailing semicolon
        sql = sql.strip().rstrip(';')
        
        return sql
    
    @staticmethod
    def add_row_limit(sql: str, max_rows: int = 100) -> str:
        """
        Add or enforce row limit on SELECT queries.
        """
        if 'LIMIT' not in sql.upper():
            sql = sql.rstrip(';') + f" LIMIT {max_rows}"
        else:
            # Extract existing limit and enforce max
            limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
            if limit_match:
                existing_limit = int(limit_match.group(1))
                if existing_limit > max_rows:
                    sql = re.sub(r'LIMIT\s+\d+', f'LIMIT {max_rows}', sql, flags=re.IGNORECASE)
        
        return sql
