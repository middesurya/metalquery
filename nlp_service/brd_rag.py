"""
BRD RAG Query Handler - Multi-Modal Version
Answers questions using retrieved BRD document context (text + images).
"""
import logging
from typing import Optional, Dict, List

from brd_loader import brd_loader

logger = logging.getLogger(__name__)


class BRDQueryHandler:
    """
    Handles RAG-based queries against BRD documents.
    Returns both text responses and relevant images.
    """
    
    def __init__(self):
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize the BRD loader and vector store (including images)."""
        try:
            logger.info("Initializing BRD RAG system with multi-modal support...")
            success = brd_loader.initialize_vectorstore(include_images=True)
            self._initialized = success
            
            if success:
                image_count = brd_loader.image_count
                logger.info(f"✓ BRD RAG initialized with {image_count} images")
            
            return success
        except Exception as e:
            logger.error(f"Failed to initialize BRD RAG: {e}")
            return False
    
    def query(self, question: str, llm=None, top_k: int = 5, image_k: int = 3) -> Dict:
        """
        Answer a question using BRD document context.
        Returns text response AND relevant images.
        
        Args:
            question: User's question
            llm: LangChain LLM instance
            top_k: Number of text chunks to retrieve
            image_k: Number of images to retrieve
            
        Returns:
            Dict with success, response, sources, images
        """
        if not self._initialized:
            return {
                "success": False,
                "error": "BRD RAG system not initialized",
                "response": None,
                "sources": [],
                "images": []
            }
        
        try:
            # Retrieve relevant text chunks AND images
            all_results = brd_loader.search_all(question, text_k=top_k, image_k=image_k)
            text_results = all_results.get('text', [])
            image_results = all_results.get('images', [])
            
            if not text_results and not image_results:
                return {
                    "success": True,
                    "response": "I couldn't find relevant information in the BRD documents for your question.",
                    "sources": [],
                    "images": []
                }
            
            # Build context from retrieved text chunks
            context_parts = []
            sources = []
            
            for i, result in enumerate(text_results):
                source = result['metadata'].get('source', 'Unknown')
                content = result['content']
                context_parts.append(content)
                if source not in sources:
                    sources.append(source)
            
            context = "\n\n---\n\n".join(context_parts)
            
            # Format image results for response
            images = []
            for img in image_results:
                images.append({
                    "filename": img['filename'],
                    "url": f"/api/brd-images/{img['filename']}",
                    "source": img['source'],
                    "page": img['page'],
                    "context": img.get('context', '')
                })
                # Add image sources to sources list
                if img['source'] not in sources:
                    sources.append(img['source'])
            
            # Generate answer using LLM
            if llm and context:
                prompt = self._build_rag_prompt(question, context, len(images))
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
            
            # Add note about images if any were found
            if images:
                answer += f"\n\n📷 I found {len(images)} relevant image(s) from the BRD documents."
            
            return {
                "success": True,
                "response": answer,
                "sources": sources,
                "images": images,
                "context_used": len(text_results),
                "images_found": len(images)
            }
            
        except Exception as e:
            logger.error(f"BRD query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "sources": [],
                "images": []
            }
    
    def _build_rag_prompt(self, question: str, context: str, image_count: int = 0) -> str:
        """Build the RAG prompt for answer generation."""
        image_note = ""
        if image_count > 0:
            image_note = f"\n\nNote: {image_count} relevant image(s) were also found and will be displayed to the user."
        
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
- Write in a natural, conversational tone{image_note}

YOUR ANSWER:"""
    
    def get_stats(self) -> Dict:
        """Get statistics about the loaded BRD data."""
        return {
            "initialized": self._initialized,
            "text_chunks": len(brd_loader.documents) if brd_loader.documents else 0,
            "images": brd_loader.image_count
        }
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized


# Singleton instance
brd_handler = BRDQueryHandler()
