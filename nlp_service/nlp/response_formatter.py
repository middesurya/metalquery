"""
Response Formatter
Formats SQL query results as natural language responses.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Format database results as natural language."""
    
    @staticmethod
    def format_results(question: str, results: List[Dict], row_count: int = None) -> str:
        """
        Convert database results to natural language.
        
        Args:
            question: Original user question
            results: List of result dictionaries
            row_count: Total row count (may differ from len(results) if truncated)
            
        Returns:
            Formatted response string
        """
        if not results:
            return ResponseFormatter._format_no_results(question)
        
        actual_count = row_count or len(results)
        
        if actual_count == 1:
            return ResponseFormatter._format_single_row(results[0], question)
        
        if actual_count <= 5:
            return ResponseFormatter._format_multiple_rows(results, question)
        
        return ResponseFormatter._format_table_results(results, actual_count, question)
    
    @staticmethod
    def _format_no_results(question: str) -> str:
        """Format response when no results found."""
        return f"No data found for: '{question}'. Please check if the date range or filters are correct."
    
    @staticmethod
    def _format_single_row(row: Dict, question: str = None) -> str:
        """Format a single row result."""
        parts = []
        
        for key, value in row.items():
            if key.startswith('_') or key == 'id':
                continue
            
            readable_key = key.replace('_', ' ').title()
            formatted_value = ResponseFormatter._format_value(value, key)
            parts.append(f"**{readable_key}**: {formatted_value}")
        
        return "Here's what I found:\n\n" + "\n".join(parts)
    
    @staticmethod
    def _format_multiple_rows(rows: List[Dict], question: str = None) -> str:
        """Format multiple rows as a list."""
        response = f"Found **{len(rows)}** results:\n\n"
        
        for i, row in enumerate(rows, 1):
            row_parts = []
            for key, value in row.items():
                if key.startswith('_') or key == 'id':
                    continue
                readable_key = key.replace('_', ' ').title()
                formatted_value = ResponseFormatter._format_value(value, key)
                row_parts.append(f"{readable_key}: {formatted_value}")
            
            response += f"{i}. {' | '.join(row_parts)}\n"
        
        return response
    
    @staticmethod
    def _format_table_results(results: List[Dict], total_count: int, question: str = None) -> str:
        """Format large result sets with summary."""
        preview_count = min(len(results), 5)
        
        response = f"Found **{total_count}** results. Showing first {preview_count}:\n\n"
        
        # Create ASCII table header
        if results:
            columns = [k for k in results[0].keys() if not k.startswith('_') and k != 'id'][:5]
            
            # Header with column names
            header = " | ".join(col.replace('_', ' ').title()[:15] for col in columns)
            separator = "-" * len(header)
            response += f"{header}\n{separator}\n"
            
            # Data rows
            for row in results[:preview_count]:
                row_values = []
                for col in columns:
                    val = ResponseFormatter._format_value(row.get(col), col)
                    row_values.append(str(val)[:15])
                response += " | ".join(row_values) + "\n"
        
        if total_count > preview_count:
            response += f"\n... and **{total_count - preview_count}** more rows."
        
        return response
    
    @staticmethod
    def _format_value(value: Any, key: str = None) -> str:
        """Format individual values based on type and context."""
        if value is None:
            return "N/A"
        
        # Handle datetime
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M')
        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')
        
        # Handle numeric values
        if isinstance(value, (float, Decimal)):
            # Detect percentage columns
            if key and any(p in key.lower() for p in ['percentage', 'rate', 'efficiency', 'yield', 'oee', 'compliance']):
                return f"{float(value):.2f}%"
            # Detect time columns
            if key and any(t in key.lower() for t in ['hours', 'time', 'duration', 'mtbf', 'mttr', 'mtbs']):
                return f"{float(value):.2f} hours"
            # Detect energy columns
            if key and any(e in key.lower() for e in ['energy', 'kwh', 'power']):
                return f"{float(value):,.2f} kWh"
            # Detect weight columns
            if key and any(w in key.lower() for w in ['weight', 'tons', 'production', 'quantity']):
                return f"{float(value):,.2f} tons"
            # Default numeric formatting
            return f"{float(value):,.2f}"
        
        if isinstance(value, int):
            return f"{value:,}"
        
        if isinstance(value, bool):
            return "Yes" if value else "No"
        
        return str(value)
    
    @staticmethod
    def format_error(error: str) -> str:
        """Format error message for user display."""
        user_friendly_errors = {
            'timeout': "The query took too long. Please try a simpler question.",
            'connection': "Unable to connect to the database. Please try again.",
            'validation': "Your question couldn't be processed. Please rephrase.",
            'insufficient_schema': "I don't have enough information to answer that question.",
        }
        
        error_lower = error.lower()
        for key, message in user_friendly_errors.items():
            if key in error_lower:
                return message
        
        return f"Sorry, I couldn't process that: {error}"
    
    @staticmethod
    def create_ascii_table(rows: List[Dict], max_rows: int = 10) -> str:
        """Create an ASCII table from rows."""
        if not rows:
            return ""
        
        # Get columns (exclude internal fields)
        columns = [k for k in rows[0].keys() if not k.startswith('_') and k != 'id']
        
        # Calculate column widths
        widths = {}
        for col in columns:
            header_len = len(col.replace('_', ' ').title())
            max_val_len = max(len(str(row.get(col, ''))[:20]) for row in rows[:max_rows])
            widths[col] = max(header_len, max_val_len, 8)
        
        # Build table
        lines = []
        
        # Header
        header = " | ".join(col.replace('_', ' ').title().ljust(widths[col]) for col in columns)
        lines.append(header)
        lines.append("-" * len(header))
        
        # Rows
        for row in rows[:max_rows]:
            values = []
            for col in columns:
                val = str(row.get(col, 'N/A'))[:widths[col]]
                values.append(val.ljust(widths[col]))
            lines.append(" | ".join(values))
        
        return "\n".join(lines)


# Convenience function
def format_response(question: str, results: List[Dict], row_count: int = None) -> str:
    """Format results as natural language."""
    return ResponseFormatter.format_results(question, results, row_count)
