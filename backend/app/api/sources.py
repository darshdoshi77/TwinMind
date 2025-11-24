"""
Sources API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import uuid

from app.database import get_db
from app.models import Source, Chunk
from app.services.storage import storage_service

router = APIRouter()


@router.get("")
async def list_sources(
    user_id: str = Query(..., description="User ID to list sources for"),
    db: AsyncSession = Depends(get_db)
):
    """List all sources for a user."""
    result = await db.execute(
        select(Source).where(Source.user_id == uuid.UUID(user_id))
        .order_by(Source.ingestion_timestamp.desc())
    )
    sources = result.scalars().all()
    
    # Build response with chunk counts
    response = []
    for source in sources:
        # Get chunk count for each source
        chunk_count_result = await db.execute(
            select(func.count(Chunk.id)).where(Chunk.source_id == source.id)
        )
        chunk_count = chunk_count_result.scalar() or 0
        
        # Determine status
        meta = source.meta or {}
        if "status" in meta:
            status = meta["status"]
        else:
            status = "completed" if chunk_count > 0 else "processing"
        
        response.append({
            "id": str(source.id),
            "source_type": source.source_type,
            "source_name": source.source_name,
            "source_url": source.source_url,
            "ingestion_timestamp": source.ingestion_timestamp.isoformat(),
            "source_timestamp": source.source_timestamp.isoformat() if source.source_timestamp else None,
            "metadata": meta,
            "status": status,
            "chunk_count": chunk_count
        })
    
    return response


@router.get("/{source_id}")
async def get_source(
    source_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get source details."""
    result = await db.execute(
        select(Source).where(
            Source.id == uuid.UUID(source_id),
            Source.user_id == uuid.UUID(user_id)
        )
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Get chunk count
    chunk_count_result = await db.execute(
        select(func.count(Chunk.id)).where(Chunk.source_id == source.id)
    )
    chunk_count = chunk_count_result.scalar()
    
    return {
        "id": str(source.id),
        "source_type": source.source_type,
        "source_name": source.source_name,
        "source_url": source.source_url,
        "ingestion_timestamp": source.ingestion_timestamp.isoformat(),
        "source_timestamp": source.source_timestamp.isoformat() if source.source_timestamp else None,
        "metadata": source.meta or {},
        "chunk_count": chunk_count,
        "status": (source.meta or {}).get("status", "completed" if chunk_count > 0 else "processing")
    }


@router.delete("/{source_id}")
async def delete_source(
    source_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a source and all its chunks."""
    result = await db.execute(
        select(Source).where(
            Source.id == uuid.UUID(source_id),
            Source.user_id == uuid.UUID(user_id)
        )
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Delete from object storage if exists
    if source.object_storage_key:
        await storage_service.delete_file(source.object_storage_key)
    
    # Delete from database (cascade will delete chunks)
    await db.delete(source)
    await db.commit()
    
    return {"status": "deleted", "source_id": source_id}

