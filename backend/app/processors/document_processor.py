"""
Document processor for PDF, Markdown, DOCX, TXT files.
"""
from typing import Dict, Any, List
import PyPDF2
import docx
from app.processors.base import BaseProcessor, Chunk
from io import BytesIO


class DocumentProcessor(BaseProcessor):
    """Processor for document files."""
    
    def __init__(self):
        """Initialize document processor."""
        self.supported_formats = {
            ".pdf": self._process_pdf,
            ".md": self._process_markdown,
            ".txt": self._process_text,
            ".docx": self._process_docx
        }
    
    async def process(
        self,
        file_data: bytes,
        filename: str,
        user_id: str,
        metadata: Dict[str, Any] = None
    ) -> tuple[str, List[Chunk], Dict[str, Any]]:
        """
        Process document file.
        Returns: (full_text, chunks, doc_metadata)
        """
        file_ext = filename.lower().split('.')[-1]
        if not file_ext.startswith('.'):
            file_ext = '.' + file_ext
        
        processor_func = self.supported_formats.get(file_ext)
        if not processor_func:
            raise ValueError(f"Unsupported document format: {file_ext}")
        
        full_text = await processor_func(file_data)
        
        # Extract metadata
        doc_metadata = {
            "source_type": "document",
            "filename": filename,
            "file_type": file_ext
        }
        if metadata:
            doc_metadata.update(metadata)
        
        # Chunk based on file type
        if file_ext == ".pdf":
            chunks = self._chunk_pdf_with_pages(file_data, full_text)
        elif file_ext == ".md":
            chunks = self.chunk_text(full_text, strategy="paragraph")
        else:
            chunks = self.chunk_text(full_text, strategy="paragraph")
        
        # Add chunk metadata
        for chunk in chunks:
            chunk.metadata.update({
                "chunk_type": "document",
                "source_type": "document"
            })
        
        return full_text, chunks, doc_metadata
    
    async def _process_pdf(self, file_data: bytes) -> str:
        """Extract text from PDF."""
        pdf_file = BytesIO(file_data)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_parts = []
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            text_parts.append(f"[Page {page_num + 1}]\n{text}")
        
        return "\n\n".join(text_parts)
    
    async def _process_markdown(self, file_data: bytes) -> str:
        """Extract text from Markdown."""
        return file_data.decode('utf-8')
    
    async def _process_text(self, file_data: bytes) -> str:
        """Extract text from plain text file."""
        # Try UTF-8 first, fallback to latin-1
        try:
            return file_data.decode('utf-8')
        except:
            return file_data.decode('latin-1')
    
    async def _process_docx(self, file_data: bytes) -> str:
        """Extract text from DOCX."""
        doc_file = BytesIO(file_data)
        doc = docx.Document(doc_file)
        
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        return "\n\n".join(text_parts)
    
    def _chunk_pdf_with_pages(self, file_data: bytes, full_text: str) -> List[Chunk]:
        """Chunk PDF preserving page boundaries."""
        # Split by page markers
        pages = full_text.split("[Page ")
        chunks = []
        
        for page_text in pages:
            if not page_text.strip():
                continue
            
            # Extract page number
            page_match = page_text.split("]\n", 1)
            if len(page_match) == 2:
                page_num = page_match[0]
                page_content = page_match[1]
            else:
                page_content = page_text
            
            # Further chunk if page is too long
            page_chunks = self.chunk_text(page_content, strategy="paragraph")
            for chunk in page_chunks:
                chunk.metadata["page_number"] = page_num
            chunks.extend(page_chunks)
        
        # Re-index chunks
        for i, chunk in enumerate(chunks):
            chunk.chunk_index = i
        
        return chunks

