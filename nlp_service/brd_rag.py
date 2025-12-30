"""
BRD RAG Query Handler - Multimodal
Answers questions using retrieved BRD document context with images.
"""
import logging
from typing import Optional, Dict, List

from brd_loader import brd_loader

logger = logging.getLogger(__name__)


class BRDQueryHandler:
    """
    Handles Multimodal RAG-based queries against BRD documents.
    Returns both text responses and relevant images.
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
        Answer a question using BRD document context with images.

        Args:
            question: User's question
            llm: LangChain LLM instance
            top_k: Number of document chunks to retrieve

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
            # Retrieve relevant chunks (now includes images)
            results = brd_loader.search(question, top_k=top_k)

            if not results:
                return {
                    "success": True,
                    "response": "I couldn't find relevant information in the BRD documents for your question.",
                    "sources": [],
                    "images": []
                }

            # Build context from retrieved chunks
            context_parts = []
            sources = []
            all_images = []
            seen_images = set()

            for i, result in enumerate(results):
                source = result['metadata'].get('source', 'Unknown')
                content = result['content']
                context_parts.append(content)
                if source not in sources:
                    sources.append(source)

                # Collect unique images from this chunk
                for img_path in result.get('images', []):
                    if img_path not in seen_images:
                        seen_images.add(img_path)
                        # Convert to base64 for frontend
                        img_b64 = brd_loader.get_image_base64(img_path)
                        if img_b64:
                            all_images.append({
                                "data": img_b64,
                                "source": source,
                                "path": img_path
                            })

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

            # Limit images to avoid huge responses (max 5 most relevant)
            limited_images = all_images[:5]

            return {
                "success": True,
                "response": answer,
                "sources": sources,
                "images": limited_images,
                "context_used": len(results),
                "total_images_found": len(all_images)
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
- If the context mentions screens, forms, or UI elements, describe them clearly

YOUR ANSWER:"""

    @property
    def is_initialized(self) -> bool:
        return self._initialized


# Singleton instance
brd_handler = BRDQueryHandler()
