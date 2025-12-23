"""
NLP Service Client
Client for calling the NLP microservice for SQL generation.
"""
import logging
import requests
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class NLPServiceClient:
    """
    Client for calling NLP microservice.
    Generates SQL from natural language questions.
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'NLP_SERVICE_URL', 'http://localhost:8003')
        self.timeout = 120  # Increased for local LLM
    
    def generate_sql(self, question: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate SQL from natural language question.
        
        Args:
            question: Natural language question
            schema: Optional schema context
            
        Returns:
            Dict with sql, success, error, tables_used
        """
        try:
            payload = {'question': question}
            if schema:
                payload['schema'] = schema
            
            response = requests.post(
                f'{self.base_url}/api/v1/generate-sql',
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': data.get('success', False),
                'sql': data.get('sql'),
                'tables_used': data.get('tables_used', []),
                'explanation': data.get('explanation'),
                'validation_warnings': data.get('validation_warnings', []),
                'error': data.get('error')
            }
            
        except requests.Timeout:
            logger.error("NLP service timeout")
            return {
                'success': False,
                'sql': None,
                'error': 'NLP service timeout - please try again',
                'tables_used': []
            }
        except requests.RequestException as e:
            logger.error(f"NLP service error: {e}")
            return {
                'success': False,
                'sql': None,
                'error': f'NLP service unavailable: {str(e)}',
                'tables_used': []
            }
        except Exception as e:
            logger.error(f"Unexpected NLP client error: {e}")
            return {
                'success': False,
                'sql': None,
                'error': str(e),
                'tables_used': []
            }
    
    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """
        Validate SQL query against security rules.
        
        Args:
            sql: SQL query to validate
            
        Returns:
            Dict with valid, error
        """
        try:
            response = requests.post(
                f'{self.base_url}/api/v1/validate',
                json={'sql': sql},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'valid': data.get('valid', False),
                'error': data.get('error')
            }
            
        except Exception as e:
            logger.error(f"SQL validation error: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def check_health(self) -> bool:
        """Check if NLP service is healthy."""
        try:
            response = requests.get(
                f'{self.base_url}/health',
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


# Singleton instance
nlp_client = NLPServiceClient()
