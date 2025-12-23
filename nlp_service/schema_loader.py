"""
Database Schema Loader
Fetches and caches database schema information from the Django Backend.
Maintains the security boundary by not accessing the DB directly.
"""
import requests
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from config import settings

logger = logging.getLogger(__name__)

@dataclass
class ColumnInfo:
    """Information about a database column."""
    name: str
    type: str  # Kept simple as per Django API response
    description: Optional[str] = None
    foreign_key: Optional[str] = None


@dataclass
class TableInfo:
    """Information about a database table."""
    name: str
    description: str
    columns: List[ColumnInfo]


class SchemaLoader:
    """
    Loads and caches database schema information from the Django API.
    """
    
    def __init__(self):
        self._schema_cache: Dict[str, TableInfo] = {}
        self._allowed_tables: set = set()
    
    def load_schema(self, tables: List[str] = None) -> Dict[str, TableInfo]:
        """
        Load schema information from Django API.
        
        Args:
            tables: Ignored in this implementation as we fetch the full allowed context provided by Django.
            
        Returns:
            Dictionary of table name to TableInfo
        """
        try:
            # Fetch schema from Django Backend
            url = f"{settings.django_api_url}/api/chatbot/schema/"
            logger.info(f"Fetching schema from: {url}")
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("success"):
                raise ValueError("API returned success=False")
                
            raw_schema = data.get("schema", {})
            
            # Clear existing cache
            self._schema_cache.clear()
            self._allowed_tables.clear()
            
            # Parse response into internal structures
            for table_name, table_data in raw_schema.items():
                
                columns = []
                for field in table_data.get("columns", []):
                    columns.append(ColumnInfo(
                        name=field.get("name"),
                        type=field.get("type"),
                        description=field.get("description"),
                        foreign_key=field.get("foreign_key")
                    ))
                
                self._schema_cache[table_name] = TableInfo(
                    name=table_name,
                    description=table_data.get("description", ""),
                    columns=columns
                )
                self._allowed_tables.add(table_name)
                
            logger.info(f"Successfully loaded {len(self._schema_cache)} tables from backend.")
            return self._schema_cache
            
        except Exception as e:
            logger.error(f"Failed to load schema from backend: {e}")
            # In a real scenario, we might retry or fail startup
            # For now, we return empty or existing cache
            return self._schema_cache
    
    def get_schema_context(self, tables: List[str] = None) -> str:
        """
        Generate schema context string for LLM prompt.
        """
        if not self._schema_cache:
            self.load_schema()
        
        # If specific tables requested, filter them. Else use all allowed.
        tables_to_include = tables or list(self._schema_cache.keys())
        
        lines = ["Database Schema (Allowed Context):", "=" * 50, ""]
        
        for table_name in tables_to_include:
            if table_name not in self._schema_cache:
                continue
                
            table = self._schema_cache[table_name]
            lines.append(f"Table: {table.name}")
            if table.description:
                lines.append(f"Description: {table.description}")
            lines.append("-" * 40)
            
            for col in table.columns:
                desc = f" ({col.description})" if col.description else ""
                fk = f" -> FK to {col.foreign_key}" if col.foreign_key else ""
                lines.append(f"  - {col.name}: {col.type}{desc}{fk}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    @property
    def allowed_tables(self) -> set:
        """Get set of allowed table names."""
        return self._allowed_tables
    
    def get_schema_dict(self) -> Dict[str, any]:
        """
        Get schema as a dictionary for use with prompts_v2 and diagnostic modules.
        Returns: {table_name: {columns: {col_name: col_type}}}
        """
        if not self._schema_cache:
            self.load_schema()
        
        result = {}
        for table_name, table_info in self._schema_cache.items():
            result[table_name] = {
                "description": table_info.description,
                "columns": {col.name: col.type for col in table_info.columns}
            }
        return result
    
    def get_table_names(self) -> List[str]:
        """Get list of all loaded table names."""
        return list(self._schema_cache.keys())

# Singleton instance
schema_loader = SchemaLoader()
