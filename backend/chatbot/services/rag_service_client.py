"""
RAG Service Client
Client for calling the RAG microservice for BRD document queries.
"""
import logging
import requests
from typing import Dict, Any, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class RAGServiceClient:
    """
    Client for calling RAG microservice.
    Answers questions from BRD documents.
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'RAG_SERVICE_URL', 'http://localhost:8004')
        self.timeout = 60
    
    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Query BRD documents for an answer.
        
        Args:
            question: User's question
            top_k: Number of document chunks to retrieve
            
        Returns:
            Dict with response, sources, success, error
        """
        try:
            response = requests.post(
                f'{self.base_url}/api/v1/answer-question',
                json={
                    'question': question,
                    'top_k': top_k
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': data.get('success', False),
                'response': data.get('response'),
                'sources': data.get('sources', []),
                'context_used': data.get('context_used', 0),
                'error': data.get('error')
            }
            
        except requests.Timeout:
            logger.error("RAG service timeout")
            return {
                'success': False,
                'response': None,
                'sources': [],
                'error': 'RAG service timeout'
            }
        except requests.RequestException as e:
            logger.error(f"RAG service error: {e}")
            return {
                'success': False,
                'response': None,
                'sources': [],
                'error': f'RAG service unavailable: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected RAG client error: {e}")
            return {
                'success': False,
                'response': None,
                'sources': [],
                'error': str(e)
            }
    
    def search_documents(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search BRD documents without generating an answer.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of document chunks with metadata
        """
        try:
            response = requests.post(
                f'{self.base_url}/api/v1/search',
                json={
                    'query': query,
                    'top_k': top_k
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get('results', [])
            
        except Exception as e:
            logger.error(f"Document search error: {e}")
            return []
    
    def check_health(self) -> bool:
        """Check if RAG service is healthy."""
        try:
            response = requests.get(
                f'{self.base_url}/health',
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def get_indexed_documents(self) -> List[str]:
        """Get list of indexed BRD documents."""
        try:
            response = requests.get(
                f'{self.base_url}/api/v1/documents',
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('documents', [])
        except Exception as e:
            logger.error(f"Failed to get documents: {e}")
            return []


# Singleton instance
rag_client = RAGServiceClient()
