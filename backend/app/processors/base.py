"""
Base processor for data ingestion.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import tiktoken


class Chunk:
    """Represents a text chunk."""
    def __init__(
        self,
        text: str,
        chunk_index: int,
        metadata: Dict[str, Any] = None,
        start_char_offset: int = None,
        end_char_offset: int = None
    ):
        self.text = text
        self.chunk_index = chunk_index
        self.metadata = metadata or {}
        self.start_char_offset = start_char_offset
        self.end_char_offset = end_char_offset
        self.token_count = self._count_tokens(text)
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except:
            # Fallback: approximate 1 token = 4 characters
            return len(text) // 4


class BaseProcessor(ABC):
    """Base class for data processors."""
    
    MAX_CHUNK_TOKENS = 1000
    OVERLAP_TOKENS = 100
    
    @abstractmethod
    async def process(self, input_data: Any, user_id: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        """Process input data and return chunks."""
        pass
    
    def chunk_text(
        self,
        text: str,
        strategy: str = "sentence"
    ) -> List[Chunk]:
        """Chunk text respecting semantic boundaries."""
        if strategy == "sentence":
            return self._chunk_by_sentence(text)
        elif strategy == "paragraph":
            return self._chunk_by_paragraph(text)
        else:
            return self._chunk_by_token_limit(text)
    
    def _chunk_by_sentence(self, text: str) -> List[Chunk]:
        """Chunk text by sentences with overlap."""
        import re
        
        # Split by sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        char_offset = 0
        
        for i, sentence in enumerate(sentences):
            sentence_tokens = Chunk("", 0)._count_tokens(sentence)
            
            if current_tokens + sentence_tokens > self.MAX_CHUNK_TOKENS and current_chunk:
                # Create chunk
                chunk_text = " ".join(current_chunk)
                chunks.append(Chunk(
                    text=chunk_text,
                    chunk_index=len(chunks),
                    start_char_offset=char_offset - len(chunk_text),
                    end_char_offset=char_offset
                ))
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + [sentence] if overlap_text else [sentence]
                current_tokens = sum(Chunk("", 0)._count_tokens(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
            
            char_offset += len(sentence) + 1
        
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(Chunk(
                text=chunk_text,
                chunk_index=len(chunks),
                start_char_offset=char_offset - len(chunk_text),
                end_char_offset=char_offset
            ))
        
        return chunks
    
    def _chunk_by_paragraph(self, text: str) -> List[Chunk]:
        """Chunk text by paragraphs."""
        paragraphs = text.split("\n\n")
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for para in paragraphs:
            para_tokens = Chunk("", 0)._count_tokens(para)
            
            if current_tokens + para_tokens > self.MAX_CHUNK_TOKENS and current_chunk:
                chunks.append(Chunk(
                    text="\n\n".join(current_chunk),
                    chunk_index=len(chunks)
                ))
                current_chunk = [para]
                current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens
        
        if current_chunk:
            chunks.append(Chunk(
                text="\n\n".join(current_chunk),
                chunk_index=len(chunks)
            ))
        
        return chunks
    
    def _chunk_by_token_limit(self, text: str) -> List[Chunk]:
        """Simple chunking by token limit."""
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        
        chunks = []
        chunk_size = self.MAX_CHUNK_TOKENS
        overlap = self.OVERLAP_TOKENS
        
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = encoding.decode(chunk_tokens)
            chunks.append(Chunk(
                text=chunk_text,
                chunk_index=len(chunks),
                start_char_offset=i,
                end_char_offset=min(i + chunk_size, len(tokens))
            ))
        
        return chunks
    
    def _get_overlap_text(self, sentences: List[str]) -> List[str]:
        """Get overlap sentences for context preservation."""
        encoding = tiktoken.get_encoding("cl100k_base")
        overlap_sentences = []
        overlap_tokens = 0
        
        for sentence in reversed(sentences):
            sentence_tokens = len(encoding.encode(sentence))
            if overlap_tokens + sentence_tokens <= self.OVERLAP_TOKENS:
                overlap_sentences.insert(0, sentence)
                overlap_tokens += sentence_tokens
            else:
                break
        
        return overlap_sentences

