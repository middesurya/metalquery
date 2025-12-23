"""
Schema Definitions
Complete table schema definitions in JSON format for NLP context.
"""
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

CACHE_KEY = 'ignis_schema_definitions'
CACHE_TIMEOUT = 3600  # 1 hour


def get_schema_definitions(force_refresh: bool = False) -> dict:
    """
    Get complete schema definitions for all exposed tables.
    
    Args:
        force_refresh: If True, bypass cache and fetch fresh schema
        
    Returns:
        Dict of {table_name: {columns: {col_name: col_type}, description: str}}
    """
    if not force_refresh:
        cached = cache.get(CACHE_KEY)
        if cached:
            return cached
    
    from .exposed_tables import EXPOSED_TABLES, TABLE_DESCRIPTIONS
    
    schema = {}
    
    try:
        with connection.cursor() as cursor:
            # Get column information from PostgreSQL
            query = """
            SELECT 
                table_name,
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM 
                information_schema.columns
            WHERE 
                table_schema = 'public'
            ORDER BY 
                table_name, ordinal_position
            """
            
            cursor.execute(query)
            columns = cursor.fetchall()
            
            current_table = None
            table_columns = {}
            
            for col in columns:
                table_name, col_name, data_type, is_nullable, col_default = col
                
                # Only include exposed tables
                if table_name not in EXPOSED_TABLES:
                    continue
                
                # Start new table
                if current_table != table_name:
                    if current_table and table_columns:
                        schema[current_table] = {
                            'columns': table_columns,
                            'description': TABLE_DESCRIPTIONS.get(current_table, f'Table: {current_table}')
                        }
                    current_table = table_name
                    table_columns = {}
                
                # Add column
                table_columns[col_name] = {
                    'type': _normalize_type(data_type),
                    'nullable': is_nullable == 'YES',
                    'has_default': col_default is not None
                }
            
            # Don't forget last table
            if current_table and table_columns:
                schema[current_table] = {
                    'columns': table_columns,
                    'description': TABLE_DESCRIPTIONS.get(current_table, f'Table: {current_table}')
                }
        
        # Cache the result
        cache.set(CACHE_KEY, schema, CACHE_TIMEOUT)
        logger.info(f"Loaded schema for {len(schema)} tables")
        
    except Exception as e:
        logger.error(f"Failed to load schema: {e}")
        # Return minimal fallback schema
        schema = _get_fallback_schema()
    
    return schema


def _normalize_type(pg_type: str) -> str:
    """Convert PostgreSQL types to simplified types."""
    type_mapping = {
        'integer': 'INTEGER',
        'bigint': 'BIGINT',
        'smallint': 'SMALLINT',
        'numeric': 'DECIMAL',
        'double precision': 'FLOAT',
        'real': 'FLOAT',
        'character varying': 'VARCHAR',
        'character': 'CHAR',
        'text': 'TEXT',
        'timestamp without time zone': 'TIMESTAMP',
        'timestamp with time zone': 'TIMESTAMPTZ',
        'date': 'DATE',
        'time without time zone': 'TIME',
        'boolean': 'BOOLEAN',
        'uuid': 'UUID',
        'json': 'JSON',
        'jsonb': 'JSONB',
    }
    return type_mapping.get(pg_type.lower(), pg_type.upper())


def _get_fallback_schema() -> dict:
    """Return minimal fallback schema when DB is unavailable."""
    from .exposed_tables import TABLE_DESCRIPTIONS
    
    return {
        table: {
            'columns': {'id': {'type': 'BIGINT', 'nullable': False}},
            'description': desc
        }
        for table, desc in TABLE_DESCRIPTIONS.items()
    }


def get_schema_context_string(tables: list = None) -> str:
    """
    Generate schema context string for LLM prompts.
    
    Args:
        tables: Optional list of specific tables to include
        
    Returns:
        Formatted schema string
    """
    schema = get_schema_definitions()
    
    if tables:
        schema = {k: v for k, v in schema.items() if k in tables}
    
    lines = ["Database Schema:", "=" * 50, ""]
    
    for table_name, table_info in schema.items():
        lines.append(f"Table: {table_name}")
        lines.append(f"Description: {table_info['description']}")
        lines.append("-" * 40)
        
        for col_name, col_info in table_info['columns'].items():
            nullable = " (nullable)" if col_info.get('nullable') else ""
            lines.append(f"  - {col_name}: {col_info['type']}{nullable}")
        
        lines.append("")
    
    return "\n".join(lines)


def invalidate_schema_cache():
    """Invalidate the schema cache."""
    cache.delete(CACHE_KEY)
    logger.info("Schema cache invalidated")
