"""
BRD Document Loader - Multi-Modal Version
Extracts BOTH text and images from PDF documents and stores in ChromaDB vector database.
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
import base64

logger = logging.getLogger(__name__)

# BRD folder paths
BRD_FOLDER = Path(__file__).parent / "brd"
BRD_IMAGES_FOLDER = Path(__file__).parent / "brd_images"
CHROMA_PERSIST_DIR = Path(__file__).parent / "chroma_db"

# Ensure images folder exists
BRD_IMAGES_FOLDER.mkdir(exist_ok=True)


class BRDDocument:
    """Represents a chunk of a BRD document."""
    def __init__(self, content: str, metadata: Dict):
        self.content = content
        self.metadata = metadata


class BRDImage:
    """Represents an extracted image from a BRD document."""
    def __init__(self, filename: str, context: str, metadata: Dict):
        self.filename = filename  # Path to saved image file
        self.context = context    # Surrounding text for embedding
        self.metadata = metadata  # Source PDF, page number, etc.


class BRDLoader:
    """
    Loads and indexes BRD PDF documents for RAG.
    Extracts both text chunks and images.
    """
    
    def __init__(self):
        self.documents: List[BRDDocument] = []
        self.images: List[BRDImage] = []
        self.vectorstore = None
        self.image_collection = None
        self._initialized = False
        self._embedding_model = None
    
    def _get_embedding_model(self):
        """Lazy load the embedding model."""
        if self._embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self._embedding_model
    
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
                            "total_chunks": len(chunks),
                            "type": "text"
                        }
                    ))
                
                logger.info(f"Loaded {pdf_path.name}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to load {pdf_path.name}: {e}")
        
        self.documents = documents
        logger.info(f"Total documents loaded: {len(documents)} chunks")
        return documents
    
    def load_images(self) -> List[BRDImage]:
        """Extract images from all PDFs in the BRD folder.
        
        Filters out:
        - Very small images (< 10KB) - likely icons
        - Logo-shaped images (wide aspect ratio, small height)
        - Images appearing too frequently (likely headers/footers)
        """
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.error("PyMuPDF not installed. Run: pip install pymupdf")
            return []
        
        images = []
        pdf_files = list(BRD_FOLDER.glob("*.pdf"))
        logger.info(f"Extracting images from {len(pdf_files)} PDF files...")
        
        # Track image hashes to detect duplicates (logos appear on every page)
        seen_sizes = {}  # size -> count
        
        for pdf_path in pdf_files:
            try:
                doc = fitz.open(pdf_path)
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    
                    # Get text from this page for context
                    page_text = page.get_text()
                    
                    # Get list of images on this page
                    image_list = page.get_images(full=True)
                    
                    for img_idx, img in enumerate(image_list):
                        try:
                            xref = img[0]  # Image reference number
                            base_image = doc.extract_image(xref)
                            
                            if base_image is None:
                                continue
                            
                            image_bytes = base_image.get("image")
                            image_ext = base_image.get("ext", "png")
                            width = base_image.get("width", 0)
                            height = base_image.get("height", 0)
                            
                            if not image_bytes:
                                continue
                            
                            image_size = len(image_bytes)
                            
                            # ============================================
                            # ENHANCED LOGO FILTERING: Skip unwanted images
                            # ============================================
                            
                            # Skip very small images (< 15KB) - likely icons/logos
                            if image_size < 15000:
                                continue
                            
                            # Skip images with small dimensions (likely icons/logos)
                            # Logos typically have height < 150px
                            if height > 0 and height < 150:
                                continue
                            
                            # Skip images with small width (likely vertical logos)
                            if width > 0 and width < 150:
                                continue
                            
                            # Skip very wide aspect ratio images (logos, headers, footers)
                            if width > 0 and height > 0:
                                aspect_ratio = width / height
                                # Logos often have aspect ratio > 3:1 or < 1:3
                                if aspect_ratio > 3 or aspect_ratio < 0.33:
                                    continue
                            
                            # Skip small total pixel area (likely logos)
                            if width > 0 and height > 0:
                                pixel_area = width * height
                                if pixel_area < 50000:  # Less than ~224x224
                                    continue
                            
                            # Track image sizes to detect repeated logos
                            size_key = f"{width}x{height}_{image_size}"
                            seen_sizes[size_key] = seen_sizes.get(size_key, 0) + 1
                            
                            # Skip if this exact size appears more than 5 times (likely logo)
                            if seen_sizes[size_key] > 5:
                                continue
                            
                            # Generate unique filename
                            image_filename = f"{pdf_path.stem}_p{page_num}_{img_idx}.{image_ext}"
                            image_path = BRD_IMAGES_FOLDER / image_filename
                            
                            # Save image to disk
                            with open(image_path, "wb") as f:
                                f.write(image_bytes)
                            
                            # ============================================
                            # IMPROVED CONTEXT EXTRACTION for better relevance
                            # ============================================
                            
                            # Try to get text blocks with position info
                            try:
                                # Get text blocks with their positions
                                text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
                                blocks = text_dict.get("blocks", [])
                                
                                # Get image bounding box for position matching
                                img_rect = page.get_image_rects(xref)
                                if img_rect:
                                    img_bbox = img_rect[0]
                                    img_center_y = (img_bbox.y0 + img_bbox.y1) / 2
                                    
                                    # Collect text blocks and sort by proximity to image
                                    text_blocks_with_distance = []
                                    for block in blocks:
                                        if block.get("type") == 0:  # text block
                                            block_y = (block.get("bbox", [0, 0, 0, 0])[1] + block.get("bbox", [0, 0, 0, 0])[3]) / 2
                                            distance = abs(block_y - img_center_y)
                                            
                                            # Extract text from lines in block
                                            block_text = ""
                                            for line in block.get("lines", []):
                                                for span in line.get("spans", []):
                                                    block_text += span.get("text", "") + " "
                                            
                                            if block_text.strip():
                                                text_blocks_with_distance.append((distance, block_text.strip()))
                                    
                                    # Sort by distance and take closest blocks
                                    text_blocks_with_distance.sort(key=lambda x: x[0])
                                    
                                    # Look for figure captions (text containing "Figure", "Fig.", "Image", "Chart", "Diagram")
                                    caption_keywords = ["figure", "fig.", "fig:", "image", "chart", "diagram", "table", "screenshot", "screen shot"]
                                    caption_text = ""
                                    surrounding_text = ""
                                    
                                    for dist, text in text_blocks_with_distance[:5]:  # Check closest 5 blocks
                                        text_lower = text.lower()
                                        # Check for caption
                                        if any(kw in text_lower for kw in caption_keywords):
                                            caption_text = text[:300]
                                            break
                                        elif not surrounding_text:
                                            surrounding_text = text[:400]
                                    
                                    # Build context with priority: caption > surrounding text > page intro
                                    if caption_text:
                                        context_text = f"[Source: {pdf_path.stem}, Page {page_num+1}] {caption_text}"
                                    elif surrounding_text:
                                        context_text = f"[Source: {pdf_path.stem}, Page {page_num+1}] {surrounding_text}"
                                    else:
                                        # Fallback to page beginning but with better context
                                        context_text = f"[Source: {pdf_path.stem}, Page {page_num+1}] {page_text[:400].strip()}"
                                else:
                                    # No image rect found, use enhanced fallback
                                    context_text = f"[Source: {pdf_path.stem}, Page {page_num+1}] {page_text[:400].strip()}"
                            except Exception as ctx_err:
                                # Fallback in case the enhanced extraction fails
                                logger.debug(f"Enhanced context extraction failed: {ctx_err}")
                                context_text = f"[Source: {pdf_path.stem}, Page {page_num+1}] {page_text[:400].strip()}" if page_text else f"Image from {pdf_path.name} page {page_num+1}"
                            
                            images.append(BRDImage(
                                filename=image_filename,
                                context=context_text,
                                metadata={
                                    "source": pdf_path.name,
                                    "page": page_num,
                                    "image_idx": img_idx,
                                    "type": "image",
                                    "file_path": str(image_path),
                                    "dimensions": f"{width}x{height}"
                                }
                            ))
                            
                        except Exception as e:
                            logger.warning(f"Failed to extract image {img_idx} from {pdf_path.name} page {page_num}: {e}")
                
                doc.close()
                
            except Exception as e:
                logger.error(f"Failed to process images from {pdf_path.name}: {e}")
        
        self.images = images
        logger.info(f"Total images extracted: {len(images)}")
        return images
    
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
    
    def initialize_vectorstore(self, include_images: bool = True):
        """Create ChromaDB vectorstore from documents and optionally images."""
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
        
        # Load documents if not already loaded
        if not self.documents:
            self.load_pdfs()
        
        if not self.documents:
            logger.warning("No documents to index")
            return False
        
        try:
            # Initialize embedding model
            logger.info("Loading embedding model...")
            model = self._get_embedding_model()
            
            # Initialize ChromaDB
            logger.info("Initializing ChromaDB...")
            CHROMA_PERSIST_DIR.mkdir(exist_ok=True)
            
            client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
            
            # Delete existing text collection if exists
            try:
                client.delete_collection("brd_documents")
            except:
                pass
            
            # Create text collection
            collection = client.create_collection(
                name="brd_documents",
                metadata={"description": "BRD PDF documents for RAG"}
            )
            
            # Add text documents in batches
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
                
                logger.info(f"Indexed text batch {i // batch_size + 1}")
            
            self.vectorstore = collection
            logger.info(f"✓ Text vector store initialized with {len(self.documents)} chunks")
            
            # Initialize image collection if requested
            if include_images:
                self._initialize_image_collection(client, model)
            
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vectorstore: {e}")
            return False
    
    def _initialize_image_collection(self, client, model):
        """Create separate collection for images."""
        # Load images if not already loaded
        if not self.images:
            self.load_images()
        
        if not self.images:
            logger.warning("No images to index")
            return False
        
        try:
            # Delete existing image collection if exists
            try:
                client.delete_collection("brd_images")
            except:
                pass
            
            # Create image collection
            image_collection = client.create_collection(
                name="brd_images",
                metadata={"description": "BRD PDF images with text context"}
            )
            
            # Add images in batches
            batch_size = 50
            for i in range(0, len(self.images), batch_size):
                batch = self.images[i:i + batch_size]
                
                # Use context text for embeddings
                contexts = [img.context for img in batch]
                metadatas = [img.metadata for img in batch]
                ids = [f"img_{i + j}" for j in range(len(batch))]
                
                # Generate embeddings from context
                embeddings = model.encode(contexts).tolist()
                
                image_collection.add(
                    documents=contexts,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
                
                logger.info(f"Indexed image batch {i // batch_size + 1}")
            
            self.image_collection = image_collection
            logger.info(f"✓ Image collection initialized with {len(self.images)} images")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize image collection: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant document chunks (text only)."""
        logger.info(f"Search called with query='{query}', top_k={top_k}")
        logger.info(f"_initialized={self._initialized}, vectorstore={self.vectorstore is not None}")

        if not self._initialized:
            logger.warning("Vector store not initialized")
            return []

        try:
            model = self._get_embedding_model()
            logger.info(f"Got embedding model: {model}")
            query_embedding = model.encode([query]).tolist()
            logger.info(f"Generated embedding with shape: {len(query_embedding)}x{len(query_embedding[0]) if query_embedding else 0}")

            logger.info(f"Querying vectorstore: {self.vectorstore}")
            results = self.vectorstore.query(
                query_embeddings=query_embedding,
                n_results=top_k
            )
            logger.info(f"Query returned: documents={len(results.get('documents', [[]])[0])}")

            search_results = []
            for i, doc in enumerate(results['documents'][0]):
                search_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })

            logger.info(f"Returning {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return []
    
    def search_images(self, query: str, top_k: int = 3, min_relevance: float = 0.5) -> List[Dict]:
        """
        Search for relevant images based on context.
        
        Args:
            query: Search query
            top_k: Maximum number of images to return
            min_relevance: Minimum relevance score (0-1). Higher = more strict. 
                          ChromaDB returns distance, so we convert: relevance = 1 - (distance / 2)
        """
        if not self._initialized or not self.image_collection:
            logger.warning("Image collection not initialized")
            return []
        
        try:
            model = self._get_embedding_model()
            query_embedding = model.encode([query]).tolist()
            
            # Fetch more results so we can filter
            results = self.image_collection.query(
                query_embeddings=query_embedding,
                n_results=min(top_k * 3, 20)  # Fetch extra for filtering
            )
            
            image_results = []
            seen_sources = set()  # Avoid duplicate images from same source+page
            
            for i, context in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 2.0
                
                # Convert distance to relevance score (0-1)
                # ChromaDB uses L2 distance, typical range is 0-2 for normalized embeddings
                relevance = max(0, 1 - (distance / 2))
                
                # Skip low-relevance results
                if relevance < min_relevance:
                    logger.debug(f"Skipping image with low relevance: {relevance:.3f}")
                    continue
                
                # Get image filename from metadata
                source = metadata.get('source', 'unknown')
                page = metadata.get('page', 0)
                img_idx = metadata.get('image_idx', 0)
                
                # Dedupe: skip if we already have an image from same source+page
                source_key = f"{source}_p{page}"
                if source_key in seen_sources:
                    continue
                seen_sources.add(source_key)
                
                # Find the matching image
                for img in self.images:
                    if (img.metadata.get('source') == source and 
                        img.metadata.get('page') == page and
                        img.metadata.get('image_idx') == img_idx):
                        
                        image_results.append({
                            'filename': img.filename,
                            'context': context[:200],  # Truncated context
                            'source': source,
                            'page': page,
                            'distance': distance,
                            'relevance': round(relevance, 3)  # Include relevance score
                        })
                        break
                
                # Stop if we have enough relevant results
                if len(image_results) >= top_k:
                    break
            
            logger.info(f"Image search: found {len(image_results)} relevant images for query: {query[:50]}...")
            return image_results
            
        except Exception as e:
            logger.error(f"Image search failed: {e}")
            return []
    
    def search_all(self, query: str, text_k: int = 5, image_k: int = 3) -> Dict:
        """Search both text and images, returning combined results."""
        text_results = self.search(query, top_k=text_k)
        image_results = self.search_images(query, top_k=image_k)
        
        return {
            'text': text_results,
            'images': image_results
        }
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    @property
    def image_count(self) -> int:
        return len(self.images)


# Singleton instance
brd_loader = BRDLoader()
