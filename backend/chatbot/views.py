"""
Django Chatbot Views
API endpoints for the NLP-to-SQL chatbot feature.
"""
import os
import json
import logging
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

# NLP Service URL (configure in Django settings or environment)
NLP_SERVICE_URL = os.getenv('NLP_SERVICE_URL', 'http://localhost:8001')


def get_db_connection():
    """Create a read-only database connection."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'davinci'),
        user=os.getenv('DB_USER', 'davinci'),
        password=os.getenv('DB_PASSWORD', ''),
        cursor_factory=RealDictCursor
    )


class SQLValidator:
    """
    Additional SQL validation layer in Django.
    Defense in depth - validates SQL even after NLP service validation.
    """
    
    BLOCKED_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER',
        'CREATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
    }
    
    @classmethod
    def validate(cls, sql: str) -> tuple:
        """
        Validate SQL query.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not sql or not sql.strip():
            return False, "Empty SQL query"
        
        sql_upper = sql.upper().strip()
        
        # Must be SELECT
        if not sql_upper.startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
        
        # Check for blocked keywords
        for keyword in cls.BLOCKED_KEYWORDS:
            if f' {keyword} ' in f' {sql_upper} ':
                return False, f"Blocked keyword: {keyword}"
        
        return True, "Valid"


def execute_safe_query(sql: str, limit: int = 100) -> list:
    """
    Execute a validated SQL query safely.
    
    Args:
        sql: The SQL query to execute
        limit: Maximum rows to return
        
    Returns:
        List of result dictionaries
    """
    # Add LIMIT if not present
    sql_upper = sql.upper()
    if 'LIMIT' not in sql_upper:
        sql = f"{sql.rstrip(';')} LIMIT {limit}"
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    finally:
        conn.close()


@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """
    Main chatbot endpoint.
    
    Receives natural language question, converts to SQL via NLP service,
    executes safely, and returns natural language response.
    """
    try:
        # Parse request body
        body = json.loads(request.body)
        question = body.get('question', '').strip()
        
        if not question:
            return JsonResponse({
                'success': False,
                'error': 'Question is required'
            }, status=400)
        
        logger.info(f"Received question: {question}")
        
        # Step 1: Call NLP service to generate SQL
        try:
            nlp_response = requests.post(
                f"{NLP_SERVICE_URL}/api/v1/generate-sql",
                json={'question': question},
                timeout=30
            )
            nlp_data = nlp_response.json()
        except requests.RequestException as e:
            logger.error(f"NLP service error: {e}")
            return JsonResponse({
                'success': False,
                'error': 'NLP service unavailable'
            }, status=503)
        
        if not nlp_data.get('success'):
            return JsonResponse({
                'success': False,
                'error': nlp_data.get('error', 'Failed to generate SQL')
            })
        
        sql = nlp_data.get('sql')
        logger.info(f"Generated SQL: {sql}")
        
        # Step 2: Validate SQL again (defense in depth)
        is_valid, error = SQLValidator.validate(sql)
        if not is_valid:
            logger.warning(f"SQL validation failed: {error}")
            return JsonResponse({
                'success': False,
                'error': f"Query not allowed: {error}"
            })
        
        # Step 3: Execute query safely
        try:
            results = execute_safe_query(sql)
            logger.info(f"Query returned {len(results)} rows")
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to execute query'
            })
        
        # Step 4: Format response via NLP service
        try:
            format_response = requests.post(
                f"{NLP_SERVICE_URL}/api/v1/format-response",
                json={
                    'question': question,
                    'sql': sql,
                    'results': results
                },
                timeout=30
            )
            format_data = format_response.json()
            natural_response = format_data.get('response', str(results))
        except Exception as e:
            logger.warning(f"Response formatting failed: {e}")
            # Fallback: return raw results
            natural_response = f"Found {len(results)} results."
        
        return JsonResponse({
            'success': True,
            'response': natural_response,
            'sql': sql,  # Optional: include for debugging
            'row_count': len(results)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def schema_info(request):
    """Get available database schema information."""
    try:
        response = requests.get(
            f"{NLP_SERVICE_URL}/api/v1/schema",
            timeout=10
        )
        return JsonResponse(response.json())
    except Exception as e:
        logger.error(f"Schema fetch error: {e}")
        return JsonResponse({
            'error': 'Failed to fetch schema'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def health(request):
    """Health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'django-chatbot'
    })
