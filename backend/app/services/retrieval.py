"""
Hybrid retrieval service combining vector and keyword search.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.models import Chunk, Source
from app.services.vector_db import vector_db
from app.services.embeddings import embedding_service
import re


class TimeRange:
    """Represents a time range for filtering."""
    def __init__(self, start: Optional[datetime] = None, end: Optional[datetime] = None):
        self.start = start
        self.end = end


class RetrievalService:
    """Service for retrieving relevant chunks using hybrid search."""
    
    async def retrieve(
        self,
        query: str,
        user_id: str,
        db: AsyncSession,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks using hybrid search.
        Returns list of chunks with relevance scores.
        """
        from uuid import UUID
        # Validate user_id is a valid UUID
        try:
            user_uuid = UUID(user_id)
        except (ValueError, TypeError):
            # Invalid UUID - return empty results
            return []
        
        # Parse temporal query if present
        time_range = await self._parse_temporal_query(query)
        
        # Generate query embedding
        query_embedding = await embedding_service.embed_text(query)
        
        # Vector search
        vector_results = await vector_db.search(
            query_vector=query_embedding,
            user_id=str(user_uuid),
            top_k=top_k * 2,  # Get more for re-ranking
            filters={"timestamp_range": {
                "start": time_range.start.isoformat() if time_range.start else None,
                "end": time_range.end.isoformat() if time_range.end else None
            }} if time_range else None
        )
        
        # Keyword search (full-text search on PostgreSQL)
        keyword_results = await self._keyword_search(
            query=query,
            user_id=str(user_uuid),
            db=db,
            time_range=time_range,
            top_k=top_k * 2
        )
        
        # Combine and re-rank
        combined_results = self._combine_results(
            vector_results=vector_results,
            keyword_results=keyword_results,
            top_k=top_k
        )
        
        # Fetch full chunk data
        chunk_ids = [r["chunk_id"] for r in combined_results]
        chunks = await self._fetch_chunks(db, chunk_ids, str(user_uuid))
        
        # Add source information
        for chunk in chunks:
            chunk["relevance_score"] = next(
                (r["score"] for r in combined_results if str(r["chunk_id"]) == str(chunk["id"])),
                0.0
            )
        
        return chunks
    
    async def _parse_temporal_query(self, query: str) -> Optional[TimeRange]:
        """Parse temporal expressions from query."""
        # Simple rule-based parsing (can be enhanced with LLM)
        query_lower = query.lower()
        
        # Patterns
        patterns = {
            r"last\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)": self._parse_last_weekday,
            r"last\s+week": lambda: TimeRange(
                start=datetime.now() - timedelta(days=7),
                end=datetime.now()
            ),
            r"last\s+month": lambda: TimeRange(
                start=datetime.now() - timedelta(days=30),
                end=datetime.now()
            ),
            r"this\s+month": lambda: TimeRange(
                start=datetime.now().replace(day=1),
                end=datetime.now()
            ),
            r"this\s+week": lambda: TimeRange(
                start=datetime.now() - timedelta(days=datetime.now().weekday()),
                end=datetime.now()
            ),
            r"in\s+(\d{4})": self._parse_year,
            r"before\s+(\w+\s+\d{1,2},?\s+\d{4})": self._parse_before_date,
            r"after\s+(\w+\s+\d{1,2},?\s+\d{4})": self._parse_after_date,
        }
        
        for pattern, parser_func in patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                try:
                    return parser_func(match)
                except:
                    continue
        
        return None
    
    def _parse_last_weekday(self, match) -> TimeRange:
        """Parse 'last Tuesday' etc."""
        weekday_name = match.group(1)
        weekdays = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }
        target_weekday = weekdays[weekday_name.lower()]
        
        today = datetime.now()
        days_ahead = target_weekday - today.weekday()
        if days_ahead >= 0:
            days_ahead -= 7
        
        target_date = today + timedelta(days=days_ahead)
        start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        return TimeRange(start=start, end=end)
    
    def _parse_year(self, match) -> TimeRange:
        """Parse year like 'in 2024'."""
        year = int(match.group(1))
        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31, 23, 59, 59)
        return TimeRange(start=start, end=end)
    
    def _parse_before_date(self, match) -> TimeRange:
        """Parse 'before March 15, 2024'."""
        date_str = match.group(1)
        try:
            end_date = date_parser.parse(date_str)
            return TimeRange(end=end_date)
        except:
            return None
    
    def _parse_after_date(self, match) -> TimeRange:
        """Parse 'after March 15, 2024'."""
        date_str = match.group(1)
        try:
            start_date = date_parser.parse(date_str)
            return TimeRange(start=start_date)
        except:
            return None
    
    async def _keyword_search(
        self,
        query: str,
        user_id: str,
        db: AsyncSession,
        time_range: Optional[TimeRange],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Full-text keyword search on PostgreSQL."""
        from uuid import UUID
        # Convert user_id to UUID if it's a string
        try:
            user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        except ValueError:
            # Invalid UUID format - return empty results
            return []
        
        # Build query
        query_stmt = select(Chunk).join(Source).where(Source.user_id == user_uuid)
        
        # Add temporal filter
        if time_range:
            conditions = []
            if time_range.start:
                conditions.append(Source.ingestion_timestamp >= time_range.start)
                conditions.append(Source.source_timestamp >= time_range.start)
            if time_range.end:
                conditions.append(Source.ingestion_timestamp <= time_range.end)
                conditions.append(Source.source_timestamp <= time_range.end)
            if conditions:
                query_stmt = query_stmt.where(or_(*conditions))
        
        # Add full-text search using text column directly
        # Use PostgreSQL's to_tsvector on the fly since search_vector might not be populated
        query_terms = query.split()
        if query_terms:
            # Simple text search using ILIKE for now (can be improved with proper tsvector)
            text_search_conditions = [
                Chunk.text.ilike(f'%{term}%')
                for term in query_terms
            ]
            if text_search_conditions:
                query_stmt = query_stmt.where(or_(*text_search_conditions))
        
        query_stmt = query_stmt.limit(top_k)
        
        result = await db.execute(query_stmt)
        chunks = result.scalars().all()
        
        return [
            {
                "chunk_id": str(chunk.id),
                "score": 0.5,  # Base score for keyword matches
                "text": chunk.text,
                "source_id": str(chunk.source_id)
            }
            for chunk in chunks
        ]
    
    def _combine_results(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Combine and re-rank results from vector and keyword search."""
        # Normalize scores
        vector_max = max((r["score"] for r in vector_results), default=1.0)
        keyword_max = max((r["score"] for r in keyword_results), default=1.0)
        
        # Combine results by chunk_id
        combined = {}
        
        # Add vector results (weight: 0.7)
        for result in vector_results:
            chunk_id = result["chunk_id"]
            normalized_score = result["score"] / vector_max if vector_max > 0 else 0
            combined[chunk_id] = {
                "chunk_id": chunk_id,
                "score": normalized_score * 0.7,
                "vector_score": normalized_score
            }
        
        # Add keyword results (weight: 0.2)
        for result in keyword_results:
            chunk_id = result["chunk_id"]
            normalized_score = result["score"] / keyword_max if keyword_max > 0 else 0
            if chunk_id in combined:
                combined[chunk_id]["score"] += normalized_score * 0.2
                combined[chunk_id]["keyword_score"] = normalized_score
            else:
                combined[chunk_id] = {
                    "chunk_id": chunk_id,
                    "score": normalized_score * 0.2,
                    "keyword_score": normalized_score
                }
        
        # Sort by combined score
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        
        return sorted_results[:top_k]
    
    async def _fetch_chunks(
        self,
        db: AsyncSession,
        chunk_ids: List[str],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Fetch full chunk data from database."""
        from uuid import UUID
        
        try:
            user_uuid = UUID(user_id)
        except (ValueError, TypeError):
            return []
        
        uuids = [UUID(id) for id in chunk_ids]
        query = select(Chunk, Source).join(Source).where(
            Chunk.id.in_(uuids),
            Source.user_id == user_uuid
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        chunks = []
        for chunk, source in rows:
            chunks.append({
                "id": str(chunk.id),
                "text": chunk.text,
                "chunk_index": chunk.chunk_index,
                "metadata": chunk.metadata or {},
                "source": {
                    "id": str(source.id),
                    "name": source.source_name,
                    "type": source.source_type,
                    "url": source.source_url,
                    "metadata": source.metadata or {}
                }
            })
        
        return chunks


retrieval_service = RetrievalService()

