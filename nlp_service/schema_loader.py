"""
Database Schema Loader
Fetches and caches database schema information for LLM context.
"""
import psycopg2
from typing import Dict, List, Optional
from dataclasses import dataclass
from config import settings


@dataclass
class ColumnInfo:
    """Information about a database column."""
    name: str
    data_type: str
    is_nullable: bool
    column_default: Optional[str] = None


@dataclass
class TableInfo:
    """Information about a database table."""
    name: str
    schema: str
    columns: List[ColumnInfo]


class SchemaLoader:
    """
    Loads and caches database schema information.
    Used to provide context to the LLM for SQL generation.
    """
    
    def __init__(self, connection_string: str = None):
        """
        Initialize schema loader.
        
        Args:
            connection_string: PostgreSQL connection URL
        """
        self.connection_string = connection_string or settings.database_url
        self._schema_cache: Dict[str, TableInfo] = {}
        self._allowed_tables: set = set()
    
    def get_connection(self):
        """Create a database connection."""
        return psycopg2.connect(self.connection_string)
    
    def load_schema(self, tables: List[str] = None, schema: str = 'public') -> Dict[str, TableInfo]:
        """
        Load schema information for specified tables.
        
        Args:
            tables: List of table names to load (None = all tables)
            schema: Database schema name (default: public)
            
        Returns:
            Dictionary of table name to TableInfo
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get all tables if none specified
            if tables is None:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """, (schema,))
                tables = [row[0] for row in cursor.fetchall()]
            
            # Load column info for each table
            for table in tables:
                cursor.execute("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                """, (schema, table))
                
                columns = [
                    ColumnInfo(
                        name=row[0],
                        data_type=row[1],
                        is_nullable=row[2] == 'YES',
                        column_default=row[3]
                    )
                    for row in cursor.fetchall()
                ]
                
                self._schema_cache[table] = TableInfo(
                    name=table,
                    schema=schema,
                    columns=columns
                )
                self._allowed_tables.add(table)
            
            return self._schema_cache
            
        finally:
            conn.close()
    
    def get_schema_context(self, tables: List[str] = None, compact: bool = False) -> str:
        """
        Generate schema context string for LLM prompt.
        """
        if not self._schema_cache:
            self.load_schema(tables)
        
        tables_to_include = tables or list(self._schema_cache.keys())
        
        # If too many tables, force compact mode
        if len(tables_to_include) > 20:
            compact = True
            
        lines = ["Database Schema:", "=" * 50, ""]
        
        if compact:
            lines.append("Note: Displaying compact schema. Only key tables show columns.")
            lines.append("")
            
            # Key tables for Manufacturing domain
            PRIORITY_TABLES = {
                'log_book_tap_hole_log',
                'additive_additionalinformation',
                'assistant_analysisresult',
                'core_process_tap_production',
                'furnace_config_tap_hole',
                'utils_globalunit'
            }
            
            for table_name in tables_to_include:
                if table_name not in self._schema_cache: continue
                table = self._schema_cache[table_name]
                
                # Show columns only for priority tables or KPI tables
                if table.name.startswith('kpi_') or any(p in table.name for p in PRIORITY_TABLES):
                    cols = ", ".join([c.name for c in table.columns])
                    lines.append(f"Table: {table.name}({cols})")
                else:
                    lines.append(f"Table: {table.name}")
        else:
            for table_name in tables_to_include:
                if table_name not in self._schema_cache:
                    continue
                    
                table = self._schema_cache[table_name]
                lines.append(f"Table: {table.name}")
                lines.append("-" * 40)
                
                for col in table.columns:
                    nullable = "NULL" if col.is_nullable else "NOT NULL"
                    lines.append(f"  - {col.name}: {col.data_type} {nullable}")
                
                lines.append("")
        
        return "\n".join(lines)
    
    def get_ddl_context(self, tables: List[str] = None) -> str:
        """
        Generate CREATE TABLE DDL statements for LLM context.
        
        Args:
            tables: Specific tables to include (None = all cached)
            
        Returns:
            DDL statements as string
        """
        if not self._schema_cache:
            self.load_schema(tables)
        
        tables_to_include = tables or list(self._schema_cache.keys())
        ddl_statements = []
        
        for table_name in tables_to_include:
            if table_name not in self._schema_cache:
                continue
                
            table = self._schema_cache[table_name]
            columns_ddl = []
            
            for col in table.columns:
                nullable = "" if col.is_nullable else " NOT NULL"
                columns_ddl.append(f"    {col.name} {col.data_type.upper()}{nullable}")
            
            ddl = f"CREATE TABLE {table.name} (\n"
            ddl += ",\n".join(columns_ddl)
            ddl += "\n);"
            ddl_statements.append(ddl)
        
        return "\n\n".join(ddl_statements)
    
    @property
    def allowed_tables(self) -> set:
        """Get set of allowed table names."""
        return self._allowed_tables
    
    def get_table_names(self) -> List[str]:
        """Get list of all loaded table names."""
        return list(self._schema_cache.keys())


# Singleton instance
schema_loader = SchemaLoader()
