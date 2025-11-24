"""
Query API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import json

from app.database import get_db
from app.services.retrieval import retrieval_service
from app.services.llm import llm_service

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    user_id: str
    max_results: int = 10
    stream: bool = False


class QueryResponse(BaseModel):
    answer: str
    sources: list
    query_metadata: dict


@router.post("", response_model=QueryResponse)
async def query_knowledge_base(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Query the knowledge base."""
    # Retrieve relevant chunks
    chunks = await retrieval_service.retrieve(
        query=request.query,
        user_id=request.user_id,
        db=db,
        top_k=request.max_results
    )
    
    if not chunks:
        return QueryResponse(
            answer="I couldn't find any relevant information in your knowledge base to answer this question.",
            sources=[],
            query_metadata={"retrieval_strategy": "hybrid"}
        )
    
    # Format chunks for LLM
    context_chunks = [
        {
            "text": chunk["text"],
            "source_name": chunk["source"]["name"],
            "source_type": chunk["source"]["type"]
        }
        for chunk in chunks
    ]
    
    # Generate answer
    if request.stream:
        # Streaming response
        return StreamingResponse(
            _stream_answer(request.query, context_chunks),
            media_type="text/event-stream"
        )
    else:
        # Non-streaming response
        answer = await llm_service.generate_answer(
            query=request.query,
            context_chunks=context_chunks,
            stream=False
        )
        
        return QueryResponse(
            answer=answer,
            sources=[
                {
                    "source_id": chunk["source"]["id"],
                    "source_name": chunk["source"]["name"],
                    "source_type": chunk["source"]["type"],
                    "chunks": [{"chunk_id": chunk["id"], "text": chunk["text"][:200]}],
                    "relevance_score": chunk.get("relevance_score", 0.0)
                }
                for chunk in chunks
            ],
            query_metadata={
                "retrieval_strategy": "hybrid",
                "chunk_count": len(chunks)
            }
        )


@router.post("/stream")
async def query_stream(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Stream query response."""
    # Retrieve relevant chunks
    chunks = await retrieval_service.retrieve(
        query=request.query,
        user_id=request.user_id,
        db=db,
        top_k=request.max_results
    )
    
    if not chunks:
        async def empty_stream():
            message = json.dumps({'content': "I couldn't find any relevant information."})
            yield f"data: {message}\n\n"
        return StreamingResponse(empty_stream(), media_type="text/event-stream")
    
    # Format chunks for LLM
    context_chunks = [
        {
            "text": chunk["text"],
            "source_name": chunk["source"]["name"],
            "source_type": chunk["source"]["type"]
        }
        for chunk in chunks
    ]
    
    # Stream answer
    async def stream_generator():
        try:
            # generate_answer with stream=True returns an async generator function
            # Call it to get the async generator
            stream_gen_func = llm_service.generate_answer(
                query=request.query,
                context_chunks=context_chunks,
                stream=True
            )
            # This is a coroutine that returns an async generator, so await it
            stream_gen = await stream_gen_func
            # Now iterate over the async generator
            async for token in stream_gen:
                yield f"data: {json.dumps({'content': token})}\n\n"
            yield f"data: {json.dumps({'done': True, 'sources': [{'name': c['source']['name']} for c in chunks]})}\n\n"
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}"
            print(f"Streaming error: {error_msg}")
            print(traceback.format_exc())
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    return StreamingResponse(stream_generator(), media_type="text/event-stream")


async def _stream_answer(query: str, context_chunks: list):
    """Helper to stream answer."""
    async for token in llm_service.generate_answer(
        query=query,
        context_chunks=context_chunks,
        stream=True
    ):
        yield f"data: {json.dumps({'content': token})}\n\n"

