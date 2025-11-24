"""
Plain text processor.
"""
from typing import Dict, Any, List
from app.processors.base import BaseProcessor, Chunk


class TextProcessor(BaseProcessor):
    """Processor for plain text input."""
    
    async def process(
        self,
        text: str,
        user_id: str,
        metadata: Dict[str, Any] = None
    ) -> tuple[str, List[Chunk], Dict[str, Any]]:
        """
        Process plain text.
        Returns: (text, chunks, text_metadata)
        """
        text_metadata = {
            "source_type": "text",
            "title": metadata.get("title", "Text Note") if metadata else "Text Note"
        }
        if metadata:
            text_metadata.update(metadata)
        
        # Chunk text
        chunks = self.chunk_text(text, strategy="paragraph")
        
        # Add chunk metadata
        for chunk in chunks:
            chunk.metadata.update({
                "chunk_type": "text",
                "source_type": "text"
            })
        
        return text, chunks, text_metadata

