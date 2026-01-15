"""
diagnostic.py - SQL Diagnostic and Validation
Validates generated SQL against schema
"""

from typing import Dict, List, Any, Optional, Tuple
import re


class SQLDiagnostic:
    """
    Diagnose and validate generated SQL against database schema.
    """
    
    def __init__(self, schema_dict: Dict[str, Any]):
        self.schema = schema_dict or {}
        self.tables = set(self.schema.keys()) if isinstance(self.schema, dict) else set()
    
    def extract_table_name(self, sql: str) -> Optional[str]:
        """Extract table name from SQL query."""
        match = re.search(r'FROM\s+(\w+)', sql, re.IGNORECASE)
        return match.group(1).lower() if match else None
    
    def extract_columns(self, sql: str) -> List[str]:
        """Extract column names from SELECT clause."""
        # Get SELECT clause
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return []
        
        select_clause = select_match.group(1)
        
        # Handle SELECT *
        if '*' in select_clause:
            return ['*']
        
        # Extract column names (simplified)
        columns = []
        # Remove aggregations to get column names
        for part in select_clause.split(','):
            part = part.strip()
            # Extract from AVG(col), SUM(col), etc.
            agg_match = re.search(r'(?:AVG|SUM|COUNT|MAX|MIN)\s*\(\s*(\w+)\s*\)', part, re.IGNORECASE)
            if agg_match:
                columns.append(agg_match.group(1).lower())
            else:
                # Plain column
                col_match = re.search(r'^(\w+)', part)
                if col_match:
                    columns.append(col_match.group(1).lower())
        
        return columns
    
    def extract_where_columns(self, sql: str) -> List[str]:
        """Extract columns used in WHERE clause."""
        where_match = re.search(r'WHERE\s+(.+?)(?:GROUP BY|ORDER BY|LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if not where_match:
            return []
        
        where_clause = where_match.group(1)
        columns = re.findall(r'(\w+)\s*(?:=|>|<|>=|<=|BETWEEN|IN|LIKE)', where_clause, re.IGNORECASE)
        return [c.lower() for c in columns]
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Get valid columns for a table from schema."""
        if table_name not in self.schema:
            return []
        
        table_info = self.schema[table_name]
        if hasattr(table_info, 'columns'):
            # Handle TableInfo object (dataclass) or dict-like object
            columns = table_info.columns
            if isinstance(columns, list):
                if columns and hasattr(columns[0], 'name'):
                    return [c.name.lower() for c in columns]
                return [str(c).lower() for c in columns]
            elif isinstance(columns, dict):
                return [c.lower() for c in columns.keys()]
                
        if isinstance(table_info, dict):
            if 'columns' in table_info:
                cols = table_info['columns']
                if isinstance(cols, dict):
                    return [c.lower() for c in cols.keys()]
                return [c.lower() for c in cols]
            return [k.lower() for k in table_info.keys()]
        elif isinstance(table_info, list):
            return [c.lower() for c in table_info]
        return []
    
    def diagnose_query(self, question: str, sql: str) -> Dict[str, Any]:
        """
        Diagnose SQL query for potential issues.
        
        Returns:
            Dict with 'valid', 'errors', 'warnings', 'suggestions'
        """
        errors = []
        warnings = []
        suggestions = []
        
        if not sql or not sql.strip():
            return {
                'valid': False,
                'errors': ['Empty SQL query'],
                'warnings': [],
                'suggestions': ['Regenerate query']
            }
        
        sql_upper = sql.upper()
        
        # Check if it's a SELECT query
        if not sql_upper.strip().startswith('SELECT'):
            errors.append('Query must start with SELECT')
        
        # Extract and validate table
        table_name = self.extract_table_name(sql)
        if table_name:
            table_lower = table_name.lower()
            if table_lower not in [t.lower() for t in self.tables]:
                errors.append(f"Table '{table_name}' not found in schema")
                # Suggest similar tables
                similar = [t for t in self.tables if table_lower in t.lower() or t.lower() in table_lower]
                if similar:
                    suggestions.append(f"Did you mean: {', '.join(similar[:3])}")
            else:
                # Validate columns
                valid_cols = self.get_table_columns(table_name)
                
                select_cols = self.extract_columns(sql)
                for col in select_cols:
                    if col != '*' and col not in valid_cols and col not in ['as']:
                        warnings.append(f"Column '{col}' may not exist in {table_name}")
                
                where_cols = self.extract_where_columns(sql)
                for col in where_cols:
                    if col not in valid_cols:
                        # Check for common issues
                        if col == 'furnace_id':
                            errors.append("Use 'furnace_no' instead of 'furnace_id'")
                        elif col == 'furnace_no_id':
                            errors.append("Use 'furnace_no' instead of 'furnace_no_id'")
                        elif col == 'plant_id' and "'6v'" in sql.lower():
                            errors.append("plant_id is INTEGER, not string '6v'")
                        else:
                            warnings.append(f"WHERE column '{col}' may not exist")
        else:
            errors.append('Could not extract table name from query')
        
        # Check for common issues
        if 'furnace_id =' in sql.lower():
            warnings.append("Consider using 'furnace_no' for filtering")
        if 'furnace_no_id =' in sql.lower():
            errors.append("Use 'furnace_no' instead of 'furnace_no_id'")
        
        if '```' in sql:
            errors.append('SQL contains markdown formatting')
        
        if sql.count('SELECT') > 1:
            warnings.append('Multiple SELECT statements detected')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def suggest_fix(self, sql: str, error_type: str) -> str:
        """Suggest a fix for common errors."""
        fixes = {
            'furnace_id': sql.replace('furnace_id', 'furnace_no'),
            'furnace_no_id': sql.replace('furnace_no_id', 'furnace_no'),
            'markdown': re.sub(r'```(?:sql)?', '', sql).strip(),
        }
        return fixes.get(error_type, sql)
