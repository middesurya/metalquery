"""
BRD Document Loader - Multimodal RAG
Extracts text AND images from PDF documents for multimodal RAG.
"""
import os
import base64
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import hashlib

logger = logging.getLogger(__name__)

# BRD folder path
BRD_FOLDER = Path(__file__).parent / "brd"
CHROMA_PERSIST_DIR = Path(__file__).parent / "chroma_db"
IMAGES_FOLDER = Path(__file__).parent / "brd_images"


class BRDDocument:
    """Represents a chunk of a BRD document with associated images."""
    def __init__(self, content: str, metadata: Dict, images: List[str] = None):
        self.content = content
        self.metadata = metadata
        self.images = images or []  # List of image paths/base64 for this chunk


class BRDLoader:
    """
    Loads and indexes BRD PDF documents for Multimodal RAG.
    Extracts both text and images from PDFs.
    """

    def __init__(self):
        self.documents: List[BRDDocument] = []
        self.vectorstore = None
        self._initialized = False
        # Store images indexed by source PDF and page number
        self.images_index: Dict[str, Dict[int, List[str]]] = {}
        # Ensure images folder exists
        IMAGES_FOLDER.mkdir(exist_ok=True)

    def _extract_images_from_page(self, doc, page, page_num: int, pdf_name: str) -> List[str]:
        """Extract images from a PDF page and save them (filtering out logos/icons)."""
        import fitz

        # Minimum dimensions to filter out logos/icons/small graphics
        MIN_WIDTH = 200   # pixels
        MIN_HEIGHT = 150  # pixels

        images = []
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                width = base_image.get("width", 0)
                height = base_image.get("height", 0)

                # Skip small images (likely logos, icons, bullets)
                if width < MIN_WIDTH or height < MIN_HEIGHT:
                    logger.debug(f"Skipping small image {img_index} ({width}x{height}) from page {page_num}")
                    continue

                # Create unique filename
                img_hash = hashlib.md5(image_bytes).hexdigest()[:8]
                img_filename = f"{pdf_name.replace('.pdf', '')}_{page_num}_{img_index}_{img_hash}.{image_ext}"
                img_path = IMAGES_FOLDER / img_filename

                # Save image file
                with open(img_path, "wb") as f:
                    f.write(image_bytes)

                images.append(str(img_path))

            except Exception as e:
                logger.debug(f"Failed to extract image {img_index} from page {page_num}: {e}")

        return images

    def load_pdfs(self) -> List[BRDDocument]:
        """Extract text AND images from all PDFs in the BRD folder."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.error("PyMuPDF not installed. Run: pip install pymupdf")
            return []

        documents = []
        pdf_files = list(BRD_FOLDER.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {BRD_FOLDER}")

        total_images = 0

        for pdf_path in pdf_files:
            try:
                doc = fitz.open(pdf_path)
                pdf_name = pdf_path.name

                # Store page-level data: text and images per page
                page_data: List[Tuple[str, List[str]]] = []

                for page_num, page in enumerate(doc):
                    # Extract text
                    text = page.get_text()

                    # Extract images from this page
                    page_images = self._extract_images_from_page(doc, page, page_num, pdf_name)
                    total_images += len(page_images)

                    page_data.append((text, page_images))

                    # Index images by source and page
                    if pdf_name not in self.images_index:
                        self.images_index[pdf_name] = {}
                    self.images_index[pdf_name][page_num] = page_images

                doc.close()

                # Combine all text for chunking
                full_text = "\n".join([p[0] for p in page_data])

                # Chunk the document with page tracking
                chunks = self._chunk_text_with_pages(full_text, page_data, chunk_size=1000, overlap=200)

                for i, (chunk_text, chunk_images, page_range) in enumerate(chunks):
                    documents.append(BRDDocument(
                        content=chunk_text,
                        metadata={
                            "source": pdf_name,
                            "chunk_id": i,
                            "total_chunks": len(chunks),
                            "page_range": page_range,
                            "has_images": len(chunk_images) > 0
                        },
                        images=chunk_images
                    ))

                logger.info(f"Loaded {pdf_name}: {len(chunks)} chunks, {sum(len(p[1]) for p in page_data)} images")

            except Exception as e:
                logger.error(f"Failed to load {pdf_path.name}: {e}")

        self.documents = documents
        logger.info(f"Total loaded: {len(documents)} chunks, {total_images} images")
        return documents

    def _chunk_text_with_pages(
        self,
        full_text: str,
        page_data: List[Tuple[str, List[str]]],
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[Tuple[str, List[str], str]]:
        """
        Split text into chunks while tracking which pages each chunk comes from.
        Returns list of (chunk_text, chunk_images, page_range).
        """
        chunks = []

        # Build page boundaries
        page_boundaries = []
        current_pos = 0
        for page_num, (page_text, page_images) in enumerate(page_data):
            page_boundaries.append({
                "page": page_num,
                "start": current_pos,
                "end": current_pos + len(page_text) + 1,  # +1 for newline
                "images": page_images
            })
            current_pos += len(page_text) + 1

        # Chunk the text
        start = 0
        text = full_text.strip()

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
                # Find which pages this chunk spans
                chunk_start = start
                chunk_end = end
                chunk_images = []
                pages_covered = []

                for pb in page_boundaries:
                    # Check if this page overlaps with the chunk
                    if pb["start"] < chunk_end and pb["end"] > chunk_start:
                        pages_covered.append(pb["page"])
                        chunk_images.extend(pb["images"])

                # Remove duplicate images
                chunk_images = list(dict.fromkeys(chunk_images))

                page_range = f"{min(pages_covered)}-{max(pages_covered)}" if pages_covered else "0"
                chunks.append((chunk.strip(), chunk_images, page_range))

            start = end - overlap
            if start < 0:
                start = 0
            if start >= len(text):
                break

        return chunks

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks (legacy method)."""
        chunks = []
        start = 0
        text = text.strip()

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

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
                metadata={"description": "BRD PDF documents for Multimodal RAG"}
            )

            # Add documents in batches
            batch_size = 100
            for i in range(0, len(self.documents), batch_size):
                batch = self.documents[i:i + batch_size]

                texts = [doc.content for doc in batch]
                # Store image paths as comma-separated string in metadata
                metadatas = []
                for doc in batch:
                    meta = doc.metadata.copy()
                    meta["image_paths"] = ",".join(doc.images) if doc.images else ""
                    meta["image_count"] = len(doc.images)
                    metadatas.append(meta)

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
        """Search for relevant document chunks with their images."""
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
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}

                # Parse image paths from metadata
                image_paths_str = metadata.get("image_paths", "")
                image_paths = [p for p in image_paths_str.split(",") if p]

                search_results.append({
                    'content': doc,
                    'metadata': metadata,
                    'distance': results['distances'][0][i] if results['distances'] else 0,
                    'images': image_paths
                })

            return search_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_image_base64(self, image_path: str) -> Optional[str]:
        """Convert an image file to base64 for sending to frontend."""
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()

            # Detect image type from extension
            ext = Path(image_path).suffix.lower()
            mime_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".bmp": "image/bmp"
            }
            mime_type = mime_types.get(ext, "image/png")

            # Create data URL
            b64 = base64.b64encode(image_data).decode('utf-8')
            return f"data:{mime_type};base64,{b64}"

        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            return None

    @property
    def is_initialized(self) -> bool:
        return self._initialized


# Singleton instance
brd_loader = BRDLoader()
