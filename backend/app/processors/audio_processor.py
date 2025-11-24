"""
Audio processor using OpenAI Whisper API.
"""
from typing import Dict, Any, List
from openai import AsyncOpenAI
from app.processors.base import BaseProcessor, Chunk
from app.config import settings
import uuid
import io


class AudioProcessor(BaseProcessor):
    """Processor for audio files."""
    
    def __init__(self):
        """Initialize audio processor."""
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.supported_formats = [".mp3", ".m4a", ".wav", ".mp4", ".webm"]
    
    async def process(
        self,
        audio_file: bytes,
        filename: str,
        user_id: str,
        metadata: Dict[str, Any] = None
    ) -> tuple[str, List[Chunk], Dict[str, Any]]:
        """
        Process audio file.
        Returns: (transcript_text, chunks, audio_metadata)
        """
        # Transcribe audio using Whisper API
        audio_file_obj = io.BytesIO(audio_file)
        audio_file_obj.name = filename
        
        transcript = await self.openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file_obj,
            response_format="verbose_json"
        )
        
        transcript_text = transcript.text
        
        # Extract metadata
        audio_metadata = {
            "duration": transcript.duration if hasattr(transcript, 'duration') else None,
            "language": transcript.language if hasattr(transcript, 'language') else None,
            "segments": getattr(transcript, 'segments', []),
            "source_type": "audio",
            "filename": filename
        }
        if metadata:
            audio_metadata.update(metadata)
        
        # Chunk transcript
        chunks = self.chunk_text(transcript_text, strategy="sentence")
        
        # Add chunk-specific metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_type": "audio_transcript",
                "source_type": "audio"
            })
        
        return transcript_text, chunks, audio_metadata

