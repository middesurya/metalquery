"""
IGNIS Schema Module
Schema definitions and exposed tables for NLP-to-SQL system.
"""
from .exposed_tables import EXPOSED_TABLES, TABLE_DESCRIPTIONS
from .schema_definitions import get_schema_definitions

__all__ = [
    'EXPOSED_TABLES',
    'TABLE_DESCRIPTIONS',
    'get_schema_definitions',
]
