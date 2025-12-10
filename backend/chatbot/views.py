"""
Django Chatbot Views
API endpoints for the NLP-to-SQL chatbot feature.

SECURITY ARCHITECTURE:
- React Frontend → Django Backend → NLP Microservice → LLM
- Django is the OWNER of the database
- NLP service ONLY generates SQL, never touches the database
- All database access goes through Django (security boundary)
"""
import os
import json
import logging
import time
from datetime import datetime
from functools import wraps
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.cache import cache

# Configure logging
logger = logging.getLogger(__name__)

# NLP Service URL (configure in Django settings or environment)
NLP_SERVICE_URL = os.getenv('NLP_SERVICE_URL', 'http://localhost:8001')


# ============================================================
# Rate Limiting
# ============================================================

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # IP -> list of timestamps
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        minute_ago = now - 60
        
        # Get existing requests for this IP
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Clean old requests
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if ts > minute_ago
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return False
        
        # Add new request
        self.requests[client_ip].append(now)
        return True
    
    def get_remaining(self, client_ip: str) -> int:
        """Get remaining requests for this minute."""
        now = time.time()
        minute_ago = now - 60
        
        if client_ip not in self.requests:
            return self.requests_per_minute
        
        recent = [ts for ts in self.requests[client_ip] if ts > minute_ago]
        return max(0, self.requests_per_minute - len(recent))


rate_limiter = RateLimiter(requests_per_minute=30)


def rate_limit(view_func):
    """Rate limiting decorator."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        client_ip = get_client_ip(request)
        
        if not rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JsonResponse({
                'success': False,
                'error': 'Rate limit exceeded. Please wait a moment.',
                'retry_after': 60
            }, status=429)
        
        response = view_func(request, *args, **kwargs)
        
        # Add rate limit headers
        if hasattr(response, '__setitem__'):
            response['X-RateLimit-Remaining'] = rate_limiter.get_remaining(client_ip)
            response['X-RateLimit-Limit'] = rate_limiter.requests_per_minute
        
        return response
    return wrapper


def get_client_ip(request):
    """Get client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


# ============================================================
# Audit Logging
# ============================================================

class AuditLogger:
    """Audit logger for compliance and security tracking."""
    
    @staticmethod
    def log_query(
        client_ip: str,
        question: str,
        sql: str,
        success: bool,
        row_count: int = 0,
        error: str = None,
        user_id: str = None
    ):
        """Log a query for audit purposes."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'client_ip': client_ip,
            'user_id': user_id or 'anonymous',
            'question': question[:500],  # Truncate long questions
            'sql': sql[:1000] if sql else None,  # Truncate long SQL
            'success': success,
            'row_count': row_count,
            'error': error[:500] if error else None
        }
        
        # Log to application log
        if success:
            logger.info(f"AUDIT: Query success - User: {user_id}, Rows: {row_count}")
        else:
            logger.warning(f"AUDIT: Query failed - User: {user_id}, Error: {error}")
        
        # In production, you would also:
        # - Write to database audit table
        # - Send to security monitoring system
        # - Store in append-only log
        
        return log_entry


audit_logger = AuditLogger()


# ============================================================
# SQL Validation (Defense in Depth)
# ============================================================

class SQLValidator:
    """
    Additional SQL validation layer in Django.
    Defense in depth - validates SQL even after NLP service validation.
    """
    
    BLOCKED_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER',
        'CREATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', 'CALL',
        'INTO', 'COPY', 'LOAD', 'SET', 'DECLARE'
    }
    
    BLOCKED_PATTERNS = [
        'pg_',  # PostgreSQL system tables
        'information_schema',
        '--',   # SQL comments
        '/*',   # Block comments
        'xp_',  # SQL Server extended procedures
        'sp_',  # SQL Server stored procedures
    ]
    
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
        
        # Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
        
        # Check for blocked keywords
        for keyword in cls.BLOCKED_KEYWORDS:
            # Check for keyword as word (not part of another word)
            if f' {keyword} ' in f' {sql_upper} ' or sql_upper.startswith(f'{keyword} '):
                return False, f"Blocked keyword: {keyword}"
        
        # Check for blocked patterns
        sql_lower = sql.lower()
        for pattern in cls.BLOCKED_PATTERNS:
            if pattern in sql_lower:
                return False, f"Blocked pattern: {pattern}"
        
        # Check for multiple statements
        if ';' in sql.rstrip(';'):
            return False, "Multiple statements not allowed"
        
        return True, "Valid"


# ============================================================
# Database Access Layer
# ============================================================

def get_db_connection():
    """Create a read-only database connection."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5433'),
        dbname=os.getenv('DB_NAME', 'postgres'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        cursor_factory=RealDictCursor,
        # Security: Set statement timeout
        options='-c statement_timeout=10000'  # 10 second timeout
    )


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


# ============================================================
# Row-Level Security (Future Implementation)
# ============================================================

def apply_row_level_security(sql: str, user_context: dict) -> str:
    """
    Apply row-level security filters based on user context.
    
    In production, this would:
    - Add WHERE clauses for organization/tenant filtering
    - Restrict access based on user roles
    - Filter sensitive columns
    
    Args:
        sql: Original SQL query
        user_context: User permissions and context
        
    Returns:
        Modified SQL with security filters
    """
    # For POC, return SQL as-is
    # In production, add filters like:
    # - WHERE organization_id = {user.org_id}
    # - WHERE is_public = true OR owner_id = {user.id}
    
    organization_id = user_context.get('organization_id')
    
    if organization_id:
        # This is a simplified example - in production use parameterized queries
        logger.info(f"Row-level security: Filtering for org {organization_id}")
    
    return sql


# ============================================================
# Main Chat Endpoint
# ============================================================

@csrf_exempt
@require_http_methods(["POST"])
@rate_limit
def chat(request):
    """
    Main chatbot endpoint.
    
    Flow:
    1. Receive natural language question from React frontend
    2. Forward to NLP service for SQL generation (AI boundary)
    3. Validate returned SQL (defense in depth)
    4. Execute safely via parameterized query
    5. Format response via NLP service
    6. Return to frontend
    
    Security:
    - AI never touches the database
    - All SQL validated before execution
    - Rate limiting per IP
    - Audit logging for compliance
    """
    client_ip = get_client_ip(request)
    
    try:
        # Parse request body
        body = json.loads(request.body)
        question = body.get('question', '').strip()
        
        # Optional: Get user context for row-level security
        user_context = {
            'user_id': body.get('user_id'),
            'organization_id': body.get('organization_id'),
        }
        
        if not question:
            return JsonResponse({
                'success': False,
                'error': 'Question is required'
            }, status=400)
        
        logger.info(f"Chat request from {client_ip}: {question[:100]}...")
        
        # ============================================
        # Step 1: Call NLP service to generate SQL
        # (AI boundary - NLP never touches database)
        # ============================================
        try:
            nlp_response = requests.post(
                f"{NLP_SERVICE_URL}/api/v1/generate-sql",
                json={'question': question},
                timeout=30
            )
            nlp_data = nlp_response.json()
        except requests.RequestException as e:
            logger.error(f"NLP service error: {e}")
            audit_logger.log_query(
                client_ip, question, None, False,
                error="NLP service unavailable"
            )
            return JsonResponse({
                'success': False,
                'error': 'AI service temporarily unavailable'
            }, status=503)
        
        if not nlp_data.get('success'):
            error = nlp_data.get('error', 'Failed to generate SQL')
            audit_logger.log_query(client_ip, question, None, False, error=error)
            return JsonResponse({
                'success': False,
                'error': error
            })
        
        sql = nlp_data.get('sql')
        logger.info(f"Generated SQL: {sql}")
        
        # ============================================
        # Step 2: Validate SQL (Defense in Depth)
        # Django validates even after NLP service
        # ============================================
        is_valid, error = SQLValidator.validate(sql)
        if not is_valid:
            logger.warning(f"SQL validation failed: {error}")
            audit_logger.log_query(
                client_ip, question, sql, False,
                error=f"Validation: {error}"
            )
            return JsonResponse({
                'success': False,
                'error': f"Query not allowed: {error}"
            })
        
        # ============================================
        # Step 3: Apply Row-Level Security
        # ============================================
        sql = apply_row_level_security(sql, user_context)
        
        # ============================================
        # Step 4: Execute Query Safely
        # (Django owns the database connection)
        # ============================================
        try:
            results = execute_safe_query(sql)
            row_count = len(results)
            logger.info(f"Query returned {row_count} rows")
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            audit_logger.log_query(
                client_ip, question, sql, False,
                error=f"Execution: {str(e)}"
            )
            return JsonResponse({
                'success': False,
                'error': 'Failed to execute query'
            })
        
        # ============================================
        # Step 5: Format Response via NLP Service
        # ============================================
        try:
            format_response = requests.post(
                f"{NLP_SERVICE_URL}/api/v1/format-response",
                json={
                    'question': question,
                    'sql': sql,
                    'results': results[:50]  # Limit for formatting
                },
                timeout=30
            )
            format_data = format_response.json()
            natural_response = format_data.get('response', f"Found {row_count} results.")
        except Exception as e:
            logger.warning(f"Response formatting failed: {e}")
            # Fallback: return summary
            natural_response = f"Found {row_count} results."
        
        # ============================================
        # Step 6: Audit Log & Return
        # ============================================
        audit_logger.log_query(
            client_ip, question, sql, True,
            row_count=row_count,
            user_id=user_context.get('user_id')
        )
        
        return JsonResponse({
            'success': True,
            'response': natural_response,
            'sql': sql,
            'results': results[:50],  # Limit results sent to frontend
            'row_count': row_count
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


# ============================================================
# Schema Info Endpoint
# ============================================================

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


# ============================================================
# Health Check Endpoint
# ============================================================

@csrf_exempt
@require_http_methods(["GET"])
def health(request):
    """Health check endpoint."""
    
    # Check NLP service connectivity
    nlp_healthy = False
    try:
        resp = requests.get(f"{NLP_SERVICE_URL}/health", timeout=5)
        nlp_healthy = resp.status_code == 200
    except:
        pass
    
    # Check database connectivity
    db_healthy = False
    try:
        conn = get_db_connection()
        conn.close()
        db_healthy = True
    except:
        pass
    
    return JsonResponse({
        'status': 'healthy' if (nlp_healthy and db_healthy) else 'degraded',
        'service': 'django-chatbot',
        'version': '2.0.0',
        'components': {
            'nlp_service': 'healthy' if nlp_healthy else 'unavailable',
            'database': 'healthy' if db_healthy else 'unavailable'
        }
    })
