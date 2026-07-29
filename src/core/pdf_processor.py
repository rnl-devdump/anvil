import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Configure Logging
logger = logging.getLogger("RAG-Ingest")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)

# ---------------------------------------------------------------------------
# Imports with Graceful Fallback Handling
# ---------------------------------------------------------------------------
DOCLING_AVAILABLE = False
MARKER_AVAILABLE = False

try:
    from docling.document_converter import DocumentConverter
    from docling.chunking import HybridChunker
    DOCLING_AVAILABLE = True
except ImportError:
    pass

try:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    MARKER_AVAILABLE = True
except ImportError:
    pass


class RobustPDFProcessor:
    """
    Dual-engine PDF processing pipeline with Docling primary and Marker fallback.
    """
    def __init__(self, max_tokens: int = 800, min_char_threshold: int = 100):
        self.max_tokens = max_tokens
        self.min_char_threshold = min_char_threshold
        
        # Initialize Docling
        if DOCLING_AVAILABLE:
            logger.info("Initializing Docling Converter & Hybrid Chunker...")
            self.docling_converter = DocumentConverter()
            self.docling_chunker = HybridChunker(
                max_tokens=self.max_tokens,
                merge_peers=True
            )
        else:
            self.docling_converter = None
            self.docling_chunker = None

        # Initialize Marker lazy instance state
        self.marker_model_dict = None

    def _init_marker(self):
        """Lazy loader for Marker models to optimize memory overhead."""
        if self.marker_model_dict is None and MARKER_AVAILABLE:
            logger.info("Initializing Marker models...")
            self.marker_model_dict = create_model_dict()

    def process_with_docling(self, pdf_path: str) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]]]:
        """Extract text and chunks using Docling."""
        if not DOCLING_AVAILABLE:
            return None, None

        try:
            logger.info(f"[Docling] Processing document: {pdf_path}")
            result = self.docling_converter.convert(pdf_path)
            doc = result.document
            
            # Export clean Markdown
            markdown_text = doc.export_to_markdown()

            # Generate RAG chunks
            raw_chunks = list(self.docling_chunker.chunk(doc))
            formatted_chunks = []

            for idx, chunk in enumerate(raw_chunks):
                formatted_chunks.append({
                    "chunk_id": idx,
                    "text": chunk.text,
                    "metadata": {
                        "source": str(pdf_path),
                        "headings": chunk.meta.headings if hasattr(chunk.meta, 'headings') else [],
                        "doc_items": [item.self_ref for item in chunk.meta.doc_items] if hasattr(chunk.meta, 'doc_items') else []
                    }
                })

            return markdown_text, formatted_chunks

        except Exception as e:
            logger.error(f"[Docling] Processing failed: {str(e)}")
            return None, None

    def process_with_marker(self, pdf_path: str) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]]]:
        """Extract text using Marker (Fallback Engine)."""
        if not MARKER_AVAILABLE:
            logger.error("[Marker] Fallback triggered but Marker is not available.")
            return None, None

        try:
            logger.info(f"[Marker] Processing fallback for: {pdf_path}")
            self._init_marker()
            
            converter = PdfConverter(artifact_dict=self.marker_model_dict)
            rendered = converter(pdf_path)
            markdown_text, _, _ = text_from_rendered(rendered)

            # Marker outputs raw text; create basic sentence/paragraph chunks for RAG
            chunks = self._fallback_chunking(markdown_text, pdf_path)
            return markdown_text, chunks

        except Exception as e:
            logger.error(f"[Marker] Processing failed: {str(e)}")
            return None, None

    def _fallback_chunking(self, text: str, pdf_path: str) -> List[Dict[str, Any]]:
        """Simple paragraph-aware sliding window chunker for fallback text."""
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_len = 0
        chunk_id = 0

        for para in paragraphs:
            para_len = len(para.split())
            if current_len + para_len > (self.max_tokens * 0.75):  # Approx word conversion
                chunk_text = "\n\n".join(current_chunk)
                if chunk_text.strip():
                    chunks.append({
                        "chunk_id": chunk_id,
                        "text": chunk_text,
                        "metadata": {"source": str(pdf_path), "engine": "marker_fallback"}
                    })
                    chunk_id += 1
                current_chunk = [para]
                current_len = para_len
            else:
                current_chunk.append(para)
                current_len += para_len

        if current_chunk:
            chunks.append({
                "chunk_id": chunk_id,
                "text": "\n\n".join(current_chunk),
                "metadata": {"source": str(pdf_path), "engine": "marker_fallback"}
            })

        return chunks

    def is_valid_output(self, markdown_text: Optional[str]) -> bool:
        """Validates extracted text quality."""
        if not markdown_text or len(markdown_text.strip()) < self.min_char_threshold:
            return False
        return True

    def process(self, pdf_path: str, engine: str = "docling") -> Dict[str, Any]:
        """
        Executes primary ingestion via specified engine with fallback if applicable.
        """
        pdf_path = str(Path(pdf_path).resolve())
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")

        engine_used = engine
        markdown_text, chunks = None, None

        if engine == "docling" and DOCLING_AVAILABLE:
            markdown_text, chunks = self.process_with_docling(pdf_path)
        elif engine == "marker" and MARKER_AVAILABLE:
            markdown_text, chunks = self.process_with_marker(pdf_path)

        # Fallbacks
        if not self.is_valid_output(markdown_text):
            if engine == "docling" and MARKER_AVAILABLE:
                logger.warning("[Pipeline] Docling output failed. Invoking Marker fallback...")
                engine_used = "marker"
                markdown_text, chunks = self.process_with_marker(pdf_path)
            elif engine == "marker" and DOCLING_AVAILABLE:
                logger.warning("[Pipeline] Marker output failed. Invoking Docling fallback...")
                engine_used = "docling"
                markdown_text, chunks = self.process_with_docling(pdf_path)

        if not self.is_valid_output(markdown_text):
            raise RuntimeError(f"Requested engines failed to extract meaningful text from {pdf_path}")

        return {
            "status": "success",
            "engine_used": engine_used,
            "file_path": pdf_path,
            "markdown": markdown_text,
            "chunks": chunks,
            "total_chunks": len(chunks) if chunks else 0
        }
