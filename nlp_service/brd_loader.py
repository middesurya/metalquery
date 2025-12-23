"""
BRD Document Loader
Extracts text from PDF documents and stores in ChromaDB vector database.
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# BRD folder path
BRD_FOLDER = Path(__file__).parent / "brd"
CHROMA_PERSIST_DIR = Path(__file__).parent / "chroma_db"


class BRDDocument:
    """Represents a chunk of a BRD document."""
    def __init__(self, content: str, metadata: Dict):
        self.content = content
        self.metadata = metadata


class BRDLoader:
    """
    Loads and indexes BRD PDF documents for RAG.
    """
    
    def __init__(self):
        self.documents: List[BRDDocument] = []
        self.vectorstore = None
        self._initialized = False
    
    def load_pdfs(self) -> List[BRDDocument]:
        """Extract text from all PDFs in the BRD folder."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.error("PyMuPDF not installed. Run: pip install pymupdf")
            return []
        
        documents = []
        pdf_files = list(BRD_FOLDER.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {BRD_FOLDER}")
        
        for pdf_path in pdf_files:
            try:
                doc = fitz.open(pdf_path)
                full_text = ""
                
                for page_num, page in enumerate(doc):
                    text = page.get_text()
                    full_text += text + "\n"
                
                doc.close()
                
                # Chunk the document
                chunks = self._chunk_text(full_text, chunk_size=1000, overlap=200)
                
                for i, chunk in enumerate(chunks):
                    documents.append(BRDDocument(
                        content=chunk,
                        metadata={
                            "source": pdf_path.name,
                            "chunk_id": i,
                            "total_chunks": len(chunks)
                        }
                    ))
                
                logger.info(f"Loaded {pdf_path.name}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to load {pdf_path.name}: {e}")
        
        self.documents = documents
        logger.info(f"Total documents loaded: {len(documents)} chunks")
        return documents
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        text = text.strip()
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > chunk_size // 2:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start = end - overlap
            if start < 0:
                start = 0
            if start >= len(text):
                break
        
        return chunks
    
    def initialize_vectorstore(self):
        """Create ChromaDB vectorstore from documents."""
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            logger.error("ChromaDB not installed. Run: pip install chromadb")
            return False
        
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
            return False
        
        if not self.documents:
            self.load_pdfs()
        
        if not self.documents:
            logger.warning("No documents to index")
            return False
        
        try:
            # Initialize embedding model
            logger.info("Loading embedding model...")
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize ChromaDB
            logger.info("Initializing ChromaDB...")
            CHROMA_PERSIST_DIR.mkdir(exist_ok=True)
            
            client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
            
            # Delete existing collection if exists
            try:
                client.delete_collection("brd_documents")
            except:
                pass
            
            collection = client.create_collection(
                name="brd_documents",
                metadata={"description": "BRD PDF documents for RAG"}
            )
            
            # Add documents in batches
            batch_size = 100
            for i in range(0, len(self.documents), batch_size):
                batch = self.documents[i:i + batch_size]
                
                texts = [doc.content for doc in batch]
                metadatas = [doc.metadata for doc in batch]
                ids = [f"doc_{i + j}" for j in range(len(batch))]
                
                # Generate embeddings
                embeddings = model.encode(texts).tolist()
                
                collection.add(
                    documents=texts,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
                
                logger.info(f"Indexed batch {i // batch_size + 1}")
            
            self.vectorstore = collection
            self._initialized = True
            logger.info(f"✓ Vector store initialized with {len(self.documents)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vectorstore: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant document chunks."""
        if not self._initialized:
            logger.warning("Vector store not initialized")
            return []
        
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            query_embedding = model.encode([query]).tolist()
            
            results = self.vectorstore.query(
                query_embeddings=query_embedding,
                n_results=top_k
            )
            
            search_results = []
            for i, doc in enumerate(results['documents'][0]):
                search_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized


# Singleton instance
brd_loader = BRDLoader()
