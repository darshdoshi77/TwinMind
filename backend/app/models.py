"""
Database models.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.database import Base


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Source(Base):
    """Source model - tracks original data sources."""
    __tablename__ = "sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(String(50), nullable=False)  # 'audio', 'document', 'web', 'text', 'image'
    source_name = Column(String(500))
    source_url = Column(Text)  # For web sources or file path
    ingestion_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source_timestamp = Column(DateTime(timezone=True))  # Original creation time
    meta = Column(JSONB)  # Flexible schema for type-specific metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    object_storage_key = Column(Text)  # Path in MinIO/S3
    
    # Relationships
    chunks = relationship("Chunk", back_populates="source", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_source_type", "user_id", "source_type"),
        Index("idx_ingestion_timestamp", "ingestion_timestamp"),
        Index("idx_source_timestamp", "source_timestamp"),
    )


class Chunk(Base):
    """Chunk model - text chunks with metadata."""
    __tablename__ = "chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order within source
    text = Column(Text, nullable=False)
    token_count = Column(Integer)
    start_char_offset = Column(Integer)
    end_char_offset = Column(Integer)
    meta = Column(JSON)  # Chunk-specific metadata (renamed to avoid SQLAlchemy conflict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    source = relationship("Source", back_populates="chunks")
    
    # Indexes
    __table_args__ = (
        Index("idx_source_chunk", "source_id", "chunk_index"),
        Index("idx_created_at", "created_at"),
    )

