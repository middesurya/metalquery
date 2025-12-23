"""
Response Formatter
Formats database results as natural language responses.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal

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
            return "No data found for your query."
        
        actual_count = row_count or len(results)
        
        if actual_count == 1:
            return ResponseFormatter._format_single_row(results[0])
        
        if actual_count <= 5:
            return ResponseFormatter._format_multiple_rows(results)
        
        return ResponseFormatter._format_summary(results, actual_count)
    
    @staticmethod
    def _format_single_row(row: Dict) -> str:
        """Format a single row result."""
        parts = []
        for key, value in row.items():
            if key.startswith('_') or key == 'id':
                continue
            readable_key = key.replace('_', ' ').title()
            formatted_value = ResponseFormatter._format_value(value, key)
            parts.append(f"**{readable_key}**: {formatted_value}")
        
        return "\n".join(parts)
    
    @staticmethod
    def _format_multiple_rows(rows: List[Dict]) -> str:
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
    def _format_summary(results: List[Dict], total_count: int) -> str:
        """Format large result sets with summary."""
        preview_count = min(len(results), 5)
        
        response = f"Found **{total_count}** results. Showing first {preview_count}:\n\n"
        
        for i, row in enumerate(results[:preview_count], 1):
            row_parts = []
            for key, value in list(row.items())[:4]:  # Limit columns shown
                if key.startswith('_') or key == 'id':
                    continue
                readable_key = key.replace('_', ' ').title()
                formatted_value = ResponseFormatter._format_value(value, key)
                row_parts.append(f"{readable_key}: {formatted_value}")
            
            response += f"{i}. {' | '.join(row_parts)}\n"
        
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
            if key and any(p in key.lower() for p in ['percentage', 'rate', 'efficiency', 'yield', 'oee']):
                return f"{float(value):.2f}%"
            # Detect time columns
            if key and any(t in key.lower() for t in ['hours', 'time', 'duration']):
                return f"{float(value):.2f} hrs"
            # Detect energy columns
            if key and any(e in key.lower() for e in ['energy', 'kwh']):
                return f"{float(value):,.2f} kWh"
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
        # Remove technical details for end users
        user_friendly_errors = {
            'timeout': "The query took too long. Please try a simpler question.",
            'connection': "Unable to connect to the database. Please try again.",
            'validation': "Your question couldn't be processed. Please rephrase.",
        }
        
        error_lower = error.lower()
        for key, message in user_friendly_errors.items():
            if key in error_lower:
                return message
        
        return f"Sorry, I couldn't process that: {error}"


# Convenience function
def format_response(question: str, results: List[Dict], row_count: int = None) -> str:
    """Format results as natural language."""
    return ResponseFormatter.format_results(question, results, row_count)
