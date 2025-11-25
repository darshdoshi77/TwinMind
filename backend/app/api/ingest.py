"""
Ingestion API endpoints.
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
import uuid
import io

from app.database import get_db
from app.models import User, Source, Chunk
from app.processors.audio_processor import AudioProcessor
from app.processors.document_processor import DocumentProcessor
from app.processors.web_processor import WebProcessor
from app.processors.text_processor import TextProcessor
from app.services.storage import storage_service
from app.services.embeddings import embedding_service
from app.services.vector_db import vector_db

router = APIRouter()

# Processors
audio_processor = AudioProcessor()
document_processor = DocumentProcessor()
web_processor = WebProcessor()
text_processor = TextProcessor()


class TextIngestRequest(BaseModel):
    text: str
    title: Optional[str] = None
    user_id: str


class WebIngestRequest(BaseModel):
    url: HttpUrl
    user_id: str


async def get_or_create_user(db: AsyncSession, user_id: str) -> User:
    """Get or create a user."""
    # Convert user_id to UUID - if not valid UUID, generate one deterministically
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        # If not a valid UUID, generate a deterministic UUID from the string
        import hashlib
        namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
        user_uuid = uuid.uuid5(namespace, user_id)
    
    result = await db.execute(
        select(User).where(User.id == user_uuid)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(id=user_uuid, email=f"{user_id}@twinmind.local")
        db.add(user)
        await db.flush()
    
    return user


async def store_chunks(
    db: AsyncSession,
    source: Source,
    chunks,
    user_id: str
):
    """Store chunks in database and vector DB."""
    chunk_ids = []
    for chunk in chunks:
        chunk_id = uuid.uuid4()
        chunk_ids.append(chunk_id)
        
        # Generate embedding
        embedding = await embedding_service.embed_text(chunk.text)
        
        # Store in PostgreSQL
        db_chunk = Chunk(
            id=chunk_id,
            source_id=source.id,
            chunk_index=chunk.chunk_index,
            text=chunk.text,
            token_count=chunk.token_count,
            start_char_offset=chunk.start_char_offset,
            end_char_offset=chunk.end_char_offset,
            metadata=chunk.metadata
        )
        db.add(db_chunk)
        
        # Store in vector DB
        await vector_db.upsert_chunk(
            chunk_id=str(chunk_id),
            vector=embedding,
            payload={
                "user_id": user_id,
                "source_id": str(source.id),
                "chunk_text": chunk.text[:500],  # First 500 chars for preview
                "timestamp": source.ingestion_timestamp.isoformat(),
                "source_type": source.source_type
            }
        )
    
    await db.commit()


@router.post("/audio")
async def ingest_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Ingest audio file (supports audio and video files with audio tracks)."""
    # Validate file type (case-insensitive)
    supported_extensions = [".mp3", ".m4a", ".wav", ".mp4", ".webm"]
    if not any(file.filename.lower().endswith(ext.lower()) for ext in supported_extensions):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported audio/video format. Supported formats: {', '.join(supported_extensions)}"
        )
    
    # Get or create user
    user = await get_or_create_user(db, user_id)
    
    # Read file (size check will happen after reading)
    # Note: For very large files, we read in chunks, but FastAPI UploadFile handles this
    file_data = await file.read()
    
    # Check file size after reading (max 500MB)
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    file_size = len(file_data)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024):.0f}MB, got {file_size / (1024 * 1024):.2f}MB"
        )
    
    # Save to object storage
    storage_key = f"audio/{user_id}/{uuid.uuid4()}{file.filename}"
    file_obj = io.BytesIO(file_data)
    await storage_service.save_file(file_obj, storage_key, content_type=file.content_type)
    
    # Create source record immediately (before processing)
    source = Source(
        user_id=user.id,
        source_type="audio",
        source_name=file.filename,
        object_storage_key=storage_key,
        ingestion_timestamp=datetime.utcnow(),
        meta={"status": "processing", "filename": file.filename}
    )
    db.add(source)
    await db.commit()  # Commit immediately so we can return the source_id
    
    # Process audio transcription in background (async)
    async def process_audio_background(source_id: str, audio_data: bytes, filename: str, user_id: str):
        """Background task to process audio transcription."""
        from app.database import AsyncSessionLocal
        
        session = AsyncSessionLocal()
        try:
            # Process audio transcription
            transcript_text, chunks, metadata = await audio_processor.process(
                audio_file=audio_data,
                filename=filename,
                user_id=user_id
            )
            
            # Update source metadata
            result = await session.execute(
                select(Source).where(Source.id == uuid.UUID(source_id))
            )
            source = result.scalar_one_or_none()
            if source:
                source.meta = {**metadata, "status": "completed"}
                await session.flush()
                
                # Store chunks
                await store_chunks(session, source, chunks, user_id)
            
            await session.commit()
        except Exception as e:
            print(f"Error in background audio processing: {e}")
            import traceback
            traceback.print_exc()
            # Update source to indicate failure
            try:
                result = await session.execute(
                    select(Source).where(Source.id == uuid.UUID(source_id))
                )
                source = result.scalar_one_or_none()
                if source:
                    if not source.meta:
                        source.meta = {}
                    source.meta.update({"status": "failed", "error": str(e)})
                    await session.commit()
            except Exception as update_error:
                print(f"Error updating source status: {update_error}")
        finally:
            await session.close()
    
    # Add background task for transcription
    background_tasks.add_task(process_audio_background, str(source.id), file_data, file.filename, user_id)
    
    return {
        "status": "accepted",
        "source_id": str(source.id),
        "message": "File uploaded successfully. Transcription is processing in the background."
    }


@router.post("/document")
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Ingest document file."""
    # Validate file type (case-insensitive)
    supported_extensions = [".pdf", ".md", ".txt", ".docx"]
    if not any(file.filename.lower().endswith(ext.lower()) for ext in supported_extensions):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported document format. Supported formats: {', '.join(supported_extensions)}"
        )
    
    # Get or create user
    user = await get_or_create_user(db, user_id)
    
    # Read file
    file_data = await file.read()
    
    # Save to object storage
    storage_key = f"documents/{user_id}/{uuid.uuid4()}{file.filename}"
    file_obj = io.BytesIO(file_data)
    await storage_service.save_file(file_obj, storage_key, content_type=file.content_type)
    
    # Process document
    full_text, chunks, metadata = await document_processor.process(
        file_data=file_data,
        filename=file.filename,
        user_id=user_id
    )
    
    # Create source
    source = Source(
        user_id=user.id,
        source_type="document",
        source_name=file.filename,
        object_storage_key=storage_key,
        ingestion_timestamp=datetime.utcnow(),
        metadata=metadata
    )
    db.add(source)
    await db.flush()
    
    # Store chunks (async)
    background_tasks.add_task(store_chunks, db, source, chunks, user_id)
    
    return {
        "status": "processing",
        "source_id": str(source.id),
        "chunk_count": len(chunks)
    }


@router.post("/web")
async def ingest_web(
    background_tasks: BackgroundTasks,
    request: WebIngestRequest,
    db: AsyncSession = Depends(get_db)
):
    """Ingest web content from URL."""
    # Get or create user
    user = await get_or_create_user(db, request.user_id)
    
    # Process web content
    full_text, chunks, metadata = await web_processor.process(
        url=str(request.url),
        user_id=request.user_id
    )
    
    # Create source
    source = Source(
        user_id=user.id,
        source_type="web",
        source_name=metadata.get("title", str(request.url)),
        source_url=str(request.url),
        ingestion_timestamp=datetime.utcnow(),
        source_timestamp=datetime.fromisoformat(metadata["publish_date"]) if metadata.get("publish_date") else None,
        metadata=metadata
    )
    db.add(source)
    await db.flush()
    
    # Store chunks (async)
    background_tasks.add_task(store_chunks, db, source, chunks, request.user_id)
    
    return {
        "status": "processing",
        "source_id": str(source.id),
        "chunk_count": len(chunks)
    }


@router.post("/text")
async def ingest_text(
    background_tasks: BackgroundTasks,
    request: TextIngestRequest,
    db: AsyncSession = Depends(get_db)
):
    """Ingest plain text."""
    # Get or create user
    user = await get_or_create_user(db, request.user_id)
    
    # Process text
    full_text, chunks, metadata = await text_processor.process(
        text=request.text,
        user_id=request.user_id,
        metadata={"title": request.title} if request.title else None
    )
    
    # Create source
    source = Source(
        user_id=user.id,
        source_type="text",
        source_name=metadata.get("title", "Text Note"),
        ingestion_timestamp=datetime.utcnow(),
        metadata=metadata
    )
    db.add(source)
    await db.flush()
    
    # Store chunks (async)
    background_tasks.add_task(store_chunks, db, source, chunks, request.user_id)
    
    return {
        "status": "processing",
        "source_id": str(source.id),
        "chunk_count": len(chunks)
    }

