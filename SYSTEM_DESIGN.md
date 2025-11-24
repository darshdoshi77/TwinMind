# System Design Document: "Second Brain" AI Companion

## Executive Summary

This document outlines the architecture for a "Second Brain" AI Companion—a personal AI system that ingests, processes, and intelligently retrieves information from multiple modalities (audio, documents, web content, text, images) to provide contextual, time-aware answers through natural language interaction.

**Core Architectural Principles:**
- **Hybrid Retrieval Strategy**: Combines semantic vector search with keyword-based search for optimal recall and precision
- **Modular Data Pipeline**: Extensible architecture supporting multiple data modalities
- **Temporal-Aware Indexing**: All data is timestamped and queriable by time ranges
- **Privacy-First Design**: Architecture supports both cloud and local-first deployments
- **Scalable Storage**: Multi-database approach using PostgreSQL for metadata and Qdrant/Pinecone for vector embeddings

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Next.js React App (Chat UI with Streaming Responses)    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend (REST + WebSocket)          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────┬──────────────┬──────────────┬──────────────┬──────────────┘
      │              │              │              │
┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
│ Ingestion │  │  Retrieval │  │    LLM    │  │   Auth    │
│  Service  │  │  Service   │  │  Service  │  │  Service  │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └───────────┘
      │              │              │
┌─────▼─────────────────────────────▼─────────────────────────────┐
│                    Data Processing Pipeline                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Audio   │  │ Document │  │   Web    │  │   Text   │       │
│  │Processor │  │Processor │  │Processor │  │Processor │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │              │              │             │
│  ┌────▼─────────────▼──────────────▼─────────────▼──────┐     │
│  │         Chunking & Embedding Service                  │     │
│  └────────────────────┬──────────────────────────────────┘     │
└───────────────────────┼────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼────┐  ┌───────▼────┐  ┌───────▼────┐
│PostgreSQL  │  │  Qdrant    │  │   Object   │
│(Metadata)  │  │(Vectors)   │  │  Storage   │
│            │  │            │  │  (S3/MinIO)│
└────────────┘  └────────────┘  └────────────┘
```

### 1.2 Technology Stack

**Backend:**
- **API Framework**: FastAPI (async, high-performance, automatic OpenAPI docs)
- **Data Processing**: Async task queue (Celery + Redis or FastAPI BackgroundTasks)
- **Vector Database**: Qdrant (self-hosted or cloud) for high-performance similarity search
- **Metadata Database**: PostgreSQL with pgvector extension (hybrid approach)
- **Object Storage**: MinIO (S3-compatible) for raw files and images
- **LLM Provider**: OpenAI GPT-4 or Anthropic Claude (API)

**Frontend:**
- **Framework**: Next.js 14 (App Router) with React
- **UI Components**: Tailwind CSS + shadcn/ui
- **Streaming**: Server-Sent Events (SSE) or WebSocket for real-time responses

**AI/ML:**
- **Embeddings**: OpenAI `text-embedding-3-large` or `text-embedding-ada-002`
- **Audio Transcription**: OpenAI Whisper API or Whisper.cpp for local processing
- **Document Parsing**: PyPDF2, python-docx, markdown parser
- **Web Scraping**: BeautifulSoup4 + readability-lxml

---

## 2. Multi-Modal Data Ingestion Pipeline

### 2.1 Pipeline Architecture

All data ingestion follows a unified pipeline pattern:

```
Input → Validation → Processing → Chunking → Embedding → Storage
  │         │            │           │          │           │
  │         │            │           │          │           └─→ Metadata DB
  │         │            │           │          └─→ Vector DB
  │         │            │           └─→ Chunk Metadata
  │         │            └─→ Raw Content (Object Storage)
  │         └─→ Error Handling
  └─→ Job Queue (Async Processing)
```

### 2.2 Audio Processing Pipeline

**Flow:**
1. **Upload**: User uploads audio file (.mp3, .m4a, .wav)
2. **Storage**: Store raw file in MinIO/S3 bucket: `audio/{user_id}/{file_id}.{ext}`
3. **Transcription**: Use Whisper API to transcribe audio to text
4. **Metadata Extraction**:
   - Duration
   - Sample rate
   - Speaker detection (if available)
   - Timestamps for each segment
5. **Chunking**: Split transcript by natural pauses/sentences (max 1000 tokens per chunk)
6. **Embedding**: Generate embeddings for each chunk
7. **Storage**: Store chunks with metadata linking to original audio file

**Implementation Details:**
```python
class AudioProcessor:
    async def process(self, file: UploadFile, user_id: str) -> List[Chunk]:
        # 1. Store raw file
        file_id = await storage.save(file, bucket="audio", user_id=user_id)
        
        # 2. Transcribe
        transcript = await whisper_api.transcribe(file)
        
        # 3. Extract metadata
        metadata = {
            "duration": transcript.duration,
            "segments": transcript.segments,
            "source_type": "audio",
            "source_id": file_id
        }
        
        # 4. Chunk transcript
        chunks = chunk_text(transcript.text, strategy="sentence", max_tokens=1000)
        
        # 5. Generate embeddings and store
        return await self._store_chunks(chunks, metadata, user_id)
```

### 2.3 Document Processing Pipeline

**Supported Formats**: PDF, Markdown, DOCX, TXT

**Flow:**
1. **Upload**: User uploads document
2. **Storage**: Store in MinIO: `documents/{user_id}/{file_id}.{ext}`
3. **Text Extraction**: Use format-specific parsers
   - PDF: PyPDF2 or pdfplumber (preserve structure)
   - Markdown: Direct text extraction + markdown parsing for structure
   - DOCX: python-docx
4. **Metadata Extraction**:
   - Title, author, creation date
   - Page numbers (for PDF)
   - Table of contents (if available)
5. **Chunking Strategy**: 
   - **PDF**: By page or by section (semantic boundaries)
   - **Markdown**: By heading hierarchy
   - **DOCX**: By paragraph/section
6. **Embedding & Storage**: Same as audio pipeline

**Chunking Strategy:**
- **Overlap**: 100 tokens between chunks to preserve context
- **Max Size**: 1000 tokens per chunk
- **Boundary Respect**: Prefer natural boundaries (paragraphs, sections)

### 2.4 Web Content Processing Pipeline

**Flow:**
1. **Input**: User provides URL
2. **Fetching**: HTTP request with proper headers (respect robots.txt)
3. **Content Extraction**: 
   - Use readability algorithm to extract main content
   - Remove navigation, ads, footers
   - Preserve article structure
4. **Metadata Extraction**:
   - Title, author, publish date
   - URL, domain
   - Meta description
5. **Chunking**: Similar to documents, respect article structure
6. **Storage**: Store HTML/text in object storage, chunks in databases

### 2.5 Plain Text Processing

**Flow:**
1. **Input**: Direct text input or note
2. **Metadata**: Timestamp, user-provided tags/categories
3. **Chunking**: By paragraph or sentence groups
4. **Storage**: Standard pipeline

### 2.6 Image Processing Strategy

**Approach**: 
- **Storage**: Images stored in MinIO: `images/{user_id}/{file_id}.{ext}`
- **Searchability**: Two-pronged approach:
  1. **OCR**: Extract text from images using Tesseract or cloud OCR
  2. **Metadata**: User-provided captions, tags, or GPT-4 Vision API descriptions
- **Embedding**: Generate embeddings from extracted text + metadata
- **Retrieval**: Images retrieved via associated text embeddings, then displayed

**Trade-off**: Full image-to-vector (CLIP) embeddings can be added later for visual similarity search, but for MVP, text-based retrieval is sufficient.

---

## 3. Information Retrieval & Querying Strategy

### 3.1 Hybrid Retrieval Approach

We employ a **hybrid retrieval strategy** combining:
1. **Semantic Search** (Vector Similarity): Primary method for understanding intent
2. **Keyword Search** (Full-Text): Secondary method for exact matches and term precision
3. **Temporal Filtering**: Time-based constraints on results
4. **Re-ranking**: Combine scores from multiple sources

### 3.2 Retrieval Pipeline

```
User Query
    │
    ├─→ Generate Query Embedding
    │       │
    │       └─→ Vector Search (Qdrant) ──┐
    │                                     │
    ├─→ Extract Keywords ─────────────────┼─→ Hybrid Scoring
    │       │                             │       │
    │       └─→ Full-Text Search (PG) ────┘       │
    │                                             │
    ├─→ Parse Temporal Filters ───────────────→ Temporal Filter
    │                                             │
    └─→ Combine & Re-rank ───────────────────────┘
                        │
                    Top-K Chunks
                        │
                    └─→ LLM Context Window
```

### 3.3 Semantic Search (Vector Embeddings)

**Why Vector Search:**
- Captures semantic meaning beyond keywords
- Handles synonyms, paraphrasing, and conceptual queries
- Enables natural language queries

**Implementation:**
- **Embedding Model**: OpenAI `text-embedding-3-large` (1536 dimensions)
- **Similarity Metric**: Cosine similarity
- **Top-K Retrieval**: Retrieve top 20-30 chunks by similarity

**Query Embedding:**
```python
query_embedding = await embedding_model.encode(user_query)
results = await vector_db.search(
    query_vector=query_embedding,
    top_k=30,
    filters={
        "user_id": user_id,
        "timestamp_range": parse_temporal_query(query)
    }
)
```

### 3.4 Keyword-Based Search

**Why Keyword Search:**
- Handles exact term matches (e.g., product names, codes)
- Complements vector search for precision
- Fast full-text search on PostgreSQL

**Implementation:**
- PostgreSQL full-text search with tsvector/tsquery
- Search on chunk text + metadata fields
- BM25-like scoring

### 3.5 Hybrid Scoring & Re-ranking

**Combined Score Formula:**
```
final_score = α × vector_similarity + β × keyword_score + γ × temporal_relevance
```

Where:
- `α = 0.7` (semantic weight)
- `β = 0.2` (keyword weight)
- `γ = 0.1` (temporal relevance boost)

**Temporal Relevance:**
- Recent content gets a small boost (decay function)
- Explicit time queries filter strictly by timestamp

### 3.6 Temporal Querying

**Time Associations:**
- **Ingestion Timestamp**: When data was added to the system
- **Source Timestamp**: Original creation time (from metadata)
- **Event Timestamp**: User-defined events (meetings, deadlines)

**Query Parsing:**
- NLP-based parsing: "last Tuesday", "this month", "in 2024"
- Structured queries: "timestamp > '2024-01-01' AND timestamp < '2024-01-31'"

**Implementation:**
```python
def parse_temporal_query(query: str) -> Optional[TimeRange]:
    # Use LLM or rule-based parser to extract time references
    # Examples:
    # "last Tuesday" → date_range(start="2024-01-16", end="2024-01-16")
    # "this month" → date_range(start="2024-01-01", end="2024-01-31")
    # "before March" → date_range(end="2024-03-01")
```

---

## 4. Data Indexing & Storage Model

### 4.1 Database Schema Design

#### PostgreSQL Schema (Metadata & Relationships)

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sources table (tracks original data sources)
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL, -- 'audio', 'document', 'web', 'text', 'image'
    source_name VARCHAR(500),
    source_url TEXT, -- For web sources or file path
    ingestion_timestamp TIMESTAMP DEFAULT NOW(),
    source_timestamp TIMESTAMP, -- Original creation time
    metadata JSONB, -- Flexible schema for type-specific metadata
    object_storage_key TEXT, -- Path in MinIO/S3
    INDEX idx_user_source_type (user_id, source_type),
    INDEX idx_ingestion_timestamp (ingestion_timestamp),
    INDEX idx_source_timestamp (source_timestamp)
);

-- Chunks table (text chunks with metadata)
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL, -- Order within source
    text TEXT NOT NULL,
    token_count INTEGER,
    start_char_offset INTEGER,
    end_char_offset INTEGER,
    metadata JSONB, -- Chunk-specific metadata (e.g., page number, speaker)
    created_at TIMESTAMP DEFAULT NOW(),
    -- Full-text search index
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
    INDEX idx_source_chunk (source_id, chunk_index),
    INDEX idx_search_vector USING GIN (search_vector),
    INDEX idx_created_at (created_at)
);

-- Vector embeddings (stored in Qdrant, metadata linked in PostgreSQL)
-- Qdrant Collection Schema:
-- {
--   "id": UUID (matches chunks.id),
--   "vector": [1536 floats],
--   "payload": {
--     "user_id": UUID,
--     "source_id": UUID,
--     "chunk_text": str (first 500 chars),
--     "timestamp": ISO timestamp,
--     "source_type": str
--   }
-- }
```

### 4.2 Chunking Strategy

**Principles:**
1. **Semantic Boundaries**: Respect paragraph, section, and sentence boundaries
2. **Overlap**: 100 tokens overlap between consecutive chunks to preserve context
3. **Size Limits**: Max 1000 tokens per chunk (optimal for embeddings and LLM context)

**Chunking Algorithm:**
```python
def chunk_text(
    text: str,
    max_tokens: int = 1000,
    overlap_tokens: int = 100,
    strategy: str = "sentence"
) -> List[Chunk]:
    """
    Chunk text respecting semantic boundaries.
    """
    if strategy == "sentence":
        sentences = split_sentences(text)
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = count_tokens(sentence)
            if current_tokens + sentence_tokens > max_tokens and current_chunk:
                chunks.append(join_chunk(current_chunk))
                # Start new chunk with overlap
                overlap_sentences = get_last_n_sentences(
                    current_chunk, overlap_tokens
                )
                current_chunk = overlap_sentences + [sentence]
                current_tokens = sum(count_tokens(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        if current_chunk:
            chunks.append(join_chunk(current_chunk))
        
        return chunks
```

### 4.3 Indexing Strategy

**Vector Indexing (Qdrant):**
- **HNSW Index**: Hierarchical Navigable Small World graph for fast approximate nearest neighbor search
- **Payload Indexing**: Index user_id, timestamp, source_type for filtering
- **Collection Settings**:
  ```python
  {
      "vector_size": 1536,
      "distance": "Cosine",
      "hnsw_config": {
          "m": 16,
          "ef_construct": 200
      }
  }
  ```

**PostgreSQL Indexing:**
- **GIN Index**: Full-text search on chunk text
- **B-tree Indexes**: On user_id, timestamps, source_id for fast filtering
- **JSONB Indexes**: On metadata fields for flexible querying

### 4.4 Storage Trade-offs

| Storage Type | Use Case | Pros | Cons |
|--------------|----------|------|------|
| **PostgreSQL** | Metadata, relationships, full-text | ACID, relational queries, mature | Not optimized for vector search |
| **Qdrant** | Vector embeddings | Fast similarity search, filtering | Additional infrastructure |
| **MinIO/S3** | Raw files | Scalable, cost-effective | Not queryable directly |
| **Hybrid (PG + pgvector)** | Simpler architecture | Single database, good for small scale | Less performant than dedicated vector DB |

**Our Choice: PostgreSQL + Qdrant**
- **Justification**: PostgreSQL handles complex relational queries and metadata, while Qdrant provides high-performance vector search. This separation allows each system to excel at its strengths. For MVP, we could use pgvector in PostgreSQL, but Qdrant offers better scalability and performance for production.

---

## 5. Temporal Querying Support

### 5.1 Timestamp Strategy

**Three-Level Timestamp System:**

1. **Ingestion Timestamp** (`ingestion_timestamp`): When the data entered the system
   - Always available
   - Useful for "what did I add recently?"

2. **Source Timestamp** (`source_timestamp`): Original creation/modification time
   - Extracted from metadata (file creation date, article publish date, etc.)
   - Useful for "what did I work on last month?" (even if added recently)

3. **Event Timestamp**: User-defined temporal events
   - Stored in chunk metadata or separate events table
   - For calendar integrations or manual tagging

### 5.2 Temporal Query Parsing

**Natural Language Parsing:**
- Use LLM to extract temporal expressions from queries
- Map to structured time ranges
- Examples:
  - "last Tuesday" → `date_range(start='2024-01-16', end='2024-01-16')`
  - "this month" → `date_range(start='2024-01-01', end='2024-01-31')`
  - "in the past week" → `date_range(start='NOW() - 7 days', end='NOW()')`

**Implementation:**
```python
async def parse_temporal_query(query: str) -> Optional[TimeRange]:
    prompt = f"""
    Extract temporal information from this query: "{query}"
    Return JSON with start_date and end_date (ISO format) or null if no time reference.
    """
    response = await llm.complete(prompt)
    return TimeRange.from_json(response)
```

### 5.3 Temporal Filtering in Retrieval

**Vector Search Filtering:**
```python
filters = {
    "must": [
        {"key": "user_id", "match": {"value": user_id}},
        {"key": "timestamp", "range": {
            "gte": time_range.start.isoformat(),
            "lte": time_range.end.isoformat()
        }}
    ]
}
results = await vector_db.search(query_vector, filters=filters, top_k=30)
```

**PostgreSQL Filtering:**
```sql
SELECT * FROM chunks
WHERE source_id IN (
    SELECT id FROM sources
    WHERE user_id = $1
    AND (
        ingestion_timestamp BETWEEN $2 AND $3
        OR source_timestamp BETWEEN $2 AND $3
    )
)
ORDER BY ts_rank(search_vector, query) DESC;
```

---

## 6. Scalability and Privacy

### 6.1 Scalability Considerations

**Current Design Scales To:**
- **Thousands of documents per user**: Vector DB and PostgreSQL can handle millions of chunks
- **Concurrent users**: Async FastAPI + horizontal scaling
- **Large files**: Streaming processing, chunked uploads

**Scaling Strategies:**

1. **Horizontal Scaling:**
   - API servers: Stateless, scale behind load balancer
   - Vector DB: Qdrant cluster mode
   - PostgreSQL: Read replicas for queries, primary for writes

2. **Caching Layer:**
   - Redis for frequently accessed chunks
   - Cache query results with TTL
   - Embedding cache for repeated queries

3. **Async Processing:**
   - Background job queue (Celery + Redis) for ingestion
   - Don't block API responses

4. **Database Optimization:**
   - Partition chunks table by user_id or timestamp
   - Archive old data to cold storage
   - Vector DB: Increase HNSW ef_construct for larger datasets

**Estimated Capacity (per user):**
- 10,000 documents × 50 chunks/doc = 500,000 chunks
- Storage: ~50GB (with embeddings and metadata)
- Query latency: <500ms for semantic search

### 6.2 Privacy by Design

**Privacy Principles:**

1. **Data Isolation:**
   - All data partitioned by `user_id` at database level
   - Row-level security in PostgreSQL
   - Vector DB collections per user (or filtering by user_id)

2. **Encryption:**
   - **At Rest**: Encrypt database and object storage
   - **In Transit**: TLS/HTTPS for all communications
   - **End-to-End**: Optional client-side encryption before upload

3. **Local-First Option:**
   - Architecture supports running entirely on-premises
   - All components can be self-hosted:
     - PostgreSQL (local or managed)
     - Qdrant (self-hosted)
     - MinIO (local S3-compatible storage)
     - LLM: Use local models (Llama, Mistral) or secure API connections

4. **Cloud vs. Local Trade-offs:**

| Aspect | Cloud-Hosted | Local-First |
|--------|--------------|-------------|
| **Scalability** | ✅ Easier horizontal scaling | ⚠️ Requires self-management |
| **Privacy** | ⚠️ Data in cloud provider | ✅ Full control |
| **Cost** | 💰 Pay-per-use, operational overhead | 💰 Hardware costs, but no per-user fees |
| **Maintenance** | ✅ Managed services | ⚠️ Self-maintenance required |
| **Performance** | ✅ Global CDN, low latency | ⚠️ Limited by local hardware |
| **Compliance** | ⚠️ Depends on provider | ✅ Full control over compliance |

**Hybrid Approach (Recommended):**
- Core data processing and storage: User's choice (cloud or local)
- LLM API: Encrypted API calls, no data retention
- Metadata: Store only necessary metadata, anonymize where possible

**Implementation:**
```python
# Configuration supports both modes
class Config:
    STORAGE_BACKEND = "s3" | "local"  # User configurable
    VECTOR_DB_URL = "cloud.qdrant.io" | "localhost:6333"
    LLM_PROVIDER = "openai" | "local_llm"
    ENCRYPT_AT_REST = True
```

---

## 7. API Design

### 7.1 Endpoints

```
POST   /api/v1/ingest/audio          - Upload and process audio file
POST   /api/v1/ingest/document       - Upload and process document
POST   /api/v1/ingest/web            - Process web URL
POST   /api/v1/ingest/text           - Ingest plain text
GET    /api/v1/ingest/status/{job_id} - Check ingestion status

POST   /api/v1/query                 - Query the knowledge base
WS     /api/v1/query/stream          - Streaming query endpoint

GET    /api/v1/sources               - List all sources
GET    /api/v1/sources/{id}          - Get source details
DELETE /api/v1/sources/{id}          - Delete source and chunks

GET    /api/v1/health                - Health check
```

### 7.2 Query API Example

```json
POST /api/v1/query
{
  "query": "What were the key concerns raised in the project meeting last Tuesday?",
  "user_id": "uuid",
  "max_results": 10,
  "stream": false
}

Response:
{
  "answer": "Based on the meeting transcript from Tuesday, January 16th, the key concerns were...",
  "sources": [
    {
      "source_id": "uuid",
      "source_name": "project_meeting_audio.mp3",
      "chunks": [{"chunk_id": "uuid", "text": "..."}],
      "relevance_score": 0.92
    }
  ],
  "query_metadata": {
    "temporal_range": {"start": "2024-01-16", "end": "2024-01-16"},
    "retrieval_strategy": "hybrid"
  }
}
```

---

## 8. Error Handling & Resilience

### 8.1 Error Handling Strategy

- **Ingestion Failures**: Store failure reason, allow retry
- **API Errors**: Graceful degradation, informative error messages
- **LLM Failures**: Fallback to keyword-only search
- **Vector DB Failures**: Fallback to PostgreSQL full-text search

### 8.2 Monitoring & Observability

- **Logging**: Structured logging (JSON) for all operations
- **Metrics**: Query latency, ingestion throughput, error rates
- **Tracing**: Distributed tracing for request flows
- **Alerts**: Failed ingestions, high error rates, slow queries

---

## 9. Future Enhancements

1. **Multi-user Collaboration**: Shared knowledge bases, permissions
2. **Graph-based Relationships**: Extract entities and relationships, build knowledge graph
3. **Real-time Sync**: WebSocket for live updates
4. **Advanced Temporal Queries**: Time-series analysis, trend detection
5. **Image Understanding**: CLIP embeddings for visual search
6. **Voice Interface**: Voice queries and responses
7. **Calendar Integration**: Link events to ingested content automatically

---

## 10. Conclusion

This architecture provides a robust, scalable foundation for a "Second Brain" AI Companion. The hybrid retrieval strategy ensures both semantic understanding and keyword precision, while the modular pipeline supports extensibility to new data modalities. The design prioritizes privacy and scalability, making it suitable for both individual use and enterprise deployment.

**Key Strengths:**
- Clear separation of concerns
- Extensible architecture
- Privacy-first design
- Temporal awareness
- Production-ready scalability

**Trade-offs Made:**
- Added complexity of multiple databases vs. simplicity of single DB
- Cloud dependencies (LLM API) vs. fully local deployment
- Processing latency vs. real-time updates (chose async processing for scalability)

---

*End of System Design Document*

