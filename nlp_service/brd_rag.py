"""
BRD RAG Query Handler
Answers questions using retrieved BRD document context.
"""
import logging
from typing import Optional, Dict, List

from brd_loader import brd_loader

logger = logging.getLogger(__name__)


class BRDQueryHandler:
    """
    Handles RAG-based queries against BRD documents.
    """
    
    def __init__(self):
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize the BRD loader and vector store."""
        try:
            logger.info("Initializing BRD RAG system...")
            success = brd_loader.initialize_vectorstore()
            self._initialized = success
            return success
        except Exception as e:
            logger.error(f"Failed to initialize BRD RAG: {e}")
            return False
    
    def query(self, question: str, llm=None, top_k: int = 5) -> Dict:
        """
        Answer a question using BRD document context.
        
        Args:
            question: User's question
            llm: LangChain LLM instance
            top_k: Number of document chunks to retrieve
            
        Returns:
            Dict with success, response, sources
        """
        if not self._initialized:
            return {
                "success": False,
                "error": "BRD RAG system not initialized",
                "response": None,
                "sources": []
            }
        
        try:
            # Retrieve relevant chunks
            results = brd_loader.search(question, top_k=top_k)
            
            if not results:
                return {
                    "success": True,
                    "response": "I couldn't find relevant information in the BRD documents for your question.",
                    "sources": []
                }
            
            # Build context from retrieved chunks (without source citations in text)
            context_parts = []
            sources = []
            
            for i, result in enumerate(results):
                source = result['metadata'].get('source', 'Unknown')
                content = result['content']
                context_parts.append(content)  # Don't include source in text
                if source not in sources:
                    sources.append(source)
            
            context = "\n\n---\n\n".join(context_parts)
            
            # Generate answer using LLM
            if llm:
                prompt = self._build_rag_prompt(question, context)
                try:
                    from langchain_core.messages import HumanMessage
                    response = llm.invoke([HumanMessage(content=prompt)])
                    answer = response.content.strip()
                except Exception as e:
                    logger.error(f"LLM generation failed: {e}")
                    answer = f"Based on the BRD documents:\n\n{context[:1500]}..."
            else:
                # Fallback: return context directly
                answer = f"Based on the BRD documents:\n\n{context[:2000]}..."
            
            return {
                "success": True,
                "response": answer,
                "sources": sources,
                "context_used": len(results)
            }
            
        except Exception as e:
            logger.error(f"BRD query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "sources": []
            }
    
    def _build_rag_prompt(self, question: str, context: str) -> str:
        """Build the RAG prompt for answer generation."""
        return f"""You are a helpful assistant that answers questions based on Business Requirement Documents (BRDs) for a manufacturing system.

Use ONLY the following context from BRD documents to answer the question. If the context doesn't contain enough information, say so.

CONTEXT FROM BRD DOCUMENTS:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
- Answer based ONLY on the provided context
- DO NOT include source citations or references like "(Source: ...)" in your answer
- If the context doesn't fully answer the question, acknowledge what's missing
- Keep your answer concise but complete
- Write in a natural, conversational tone

YOUR ANSWER:"""
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized


# Singleton instance
brd_handler = BRDQueryHandler()
