"""
Vector database service using Qdrant.
"""
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, Range, MatchValue
from app.config import settings
import uuid


class VectorDB:
    """Vector database client for Qdrant."""
    
    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
        )
        self.collection_name = "twinmind_chunks"
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the collection exists."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=3072,  # text-embedding-3-large returns 3072 dimensions
                        distance=Distance.COSINE
                    )
                )
        except Exception:
            # If check fails, try to create anyway (will fail if exists)
            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=3072,  # text-embedding-3-large returns 3072 dimensions
                        distance=Distance.COSINE
                    )
                )
            except Exception:
                # Collection already exists, that's fine
                pass
    
    async def upsert_chunk(
        self,
        chunk_id: str,
        vector: List[float],
        payload: Dict[str, Any]
    ):
        """Insert or update a chunk vector."""
        point = PointStruct(
            id=chunk_id,
            vector=vector,
            payload=payload
        )
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
    
    async def search(
        self,
        query_vector: List[float],
        user_id: str,
        top_k: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks."""
        # Build filter
        must_conditions = [
            FieldCondition(key="user_id", match=MatchValue(value=str(user_id)))
        ]
        
        # Add temporal filter if provided
        if filters and "timestamp_range" in filters:
            time_range = filters["timestamp_range"]
            timestamp_filter = FieldCondition(
                key="timestamp",
                range=Range(
                    gte=time_range.get("start"),
                    lte=time_range.get("end")
                )
            )
            must_conditions.append(timestamp_filter)
        
        query_filter = Filter(must=must_conditions) if must_conditions else None
        
        # Perform search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter
        )
        
        return [
            {
                "chunk_id": str(result.id),
                "score": result.score,
                "payload": result.payload
            }
            for result in results
        ]
    
    async def delete_chunks_by_source(self, source_id: str):
        """Delete all chunks associated with a source."""
        # Qdrant doesn't support direct deletion by payload, so we need to
        # find and delete points. For now, we'll mark for deletion or handle at application level.
        # In production, we'd use scroll + delete or maintain an index.
        pass


vector_db = VectorDB()

