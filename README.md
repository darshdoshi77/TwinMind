# TwinMind - Second Brain AI Companion

A full-stack AI system that serves as your "second brain" - ingesting, processing, and intelligently retrieving information from multiple modalities (audio, documents, web content, text) to provide contextual, time-aware answers through natural language interaction.

## 🏗️ Architecture Overview

This system implements a hybrid retrieval strategy combining:
- **Semantic Search**: Vector embeddings for understanding intent
- **Keyword Search**: Full-text search for exact matches
- **Temporal Filtering**: Time-aware queries
- **Multi-Modal Processing**: Audio transcription, document parsing, web scraping

See [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) for comprehensive architectural details.

## 📁 Project Structure

```
TwinMind/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   ├── processors/     # Data processors
│   │   ├── services/       # Core services (LLM, embeddings, vector DB)
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database setup
│   │   └── main.py         # FastAPI app
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── app/               # Next.js app router
│   ├── components/        # React components
│   └── package.json
└── SYSTEM_DESIGN.md       # Comprehensive system design document
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Qdrant (vector database)
- MinIO or S3-compatible storage (optional, can use local storage)
- OpenAI API key (for embeddings and LLM)
- Redis (optional, for background tasks)

### Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Set up databases:**
```bash
# PostgreSQL
createdb twinmind

# Qdrant (using Docker)
docker run -p 6333:6333 qdrant/qdrant
```

5. **Run database migrations:**
The database tables will be created automatically on first run.

6. **Start the backend:**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Set up environment variables:**
```bash
cp .env.local.example .env.local
# Edit .env.local with your API URL
```

3. **Start the development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📖 Usage

### Ingesting Content

1. **Audio Files**: Upload .mp3, .m4a, .wav files. They will be transcribed automatically.
2. **Documents**: Upload .pdf, .md, .txt, .docx files.
3. **Web Content**: Provide a URL to scrape and ingest.
4. **Plain Text**: Add text notes directly.

### Querying

Ask natural language questions such as:
- "What were the key concerns raised in the project meeting last Tuesday?"
- "Summarize the main points from that article I saved about quantum computing"
- "What did I work on last month?"

The system will:
1. Retrieve relevant chunks using hybrid search
2. Generate contextual answers using an LLM
3. Cite sources for transparency

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
- `DATABASE_URL`: PostgreSQL connection string
- `QDRANT_URL`: Qdrant server URL
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_EMBEDDING_MODEL`: Embedding model (default: text-embedding-3-large)
- `OPENAI_LLM_MODEL`: LLM model (default: gpt-4-turbo-preview)
- `STORAGE_TYPE`: s3 or local
- `S3_*`: S3/MinIO configuration

**Frontend (.env.local):**
- `NEXT_PUBLIC_API_URL`: Backend API URL

## 🏛️ System Design Highlights

### Multi-Modal Processing

- **Audio**: Whisper API for transcription, chunked by sentences
- **Documents**: Format-specific parsers preserving structure
- **Web**: Readability-based content extraction
- **Text**: Direct chunking with semantic boundaries

### Hybrid Retrieval

1. **Vector Search** (70% weight): Semantic similarity using embeddings
2. **Keyword Search** (20% weight): Full-text search on PostgreSQL
3. **Temporal Relevance** (10% weight): Time-based boosting

### Storage Architecture

- **PostgreSQL**: Metadata, relationships, full-text search
- **Qdrant**: Vector embeddings for similarity search
- **Object Storage**: Raw files (S3/MinIO or local)

### Temporal Querying

Supports natural language time queries:
- "last Tuesday"
- "this month"
- "before March 2024"
- "in 2024"

## 🧪 Testing

### Backend API Testing

Use the interactive API docs at `http://localhost:8000/docs` or:

```bash
# Test query endpoint
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is in my knowledge base?",
    "user_id": "your-user-id",
    "max_results": 10
  }'
```

## 📊 API Endpoints

- `POST /api/v1/ingest/audio` - Upload audio file
- `POST /api/v1/ingest/document` - Upload document
- `POST /api/v1/ingest/web` - Ingest web URL
- `POST /api/v1/ingest/text` - Ingest plain text
- `POST /api/v1/query` - Query knowledge base
- `POST /api/v1/query/stream` - Stream query response
- `GET /api/v1/sources` - List sources
- `GET /api/v1/sources/{id}` - Get source details
- `DELETE /api/v1/sources/{id}` - Delete source

## 🔐 Privacy & Security

- All data is partitioned by user_id
- Supports local-first deployment
- Encrypted storage options
- No data sharing between users

## 📈 Scalability

- Horizontal scaling of API servers
- Async processing for ingestion
- Vector DB clustering support
- Caching layer ready (Redis)

## 🛠️ Development

### Adding New Processors

1. Create a new processor class in `app/processors/`
2. Inherit from `BaseProcessor`
3. Implement the `process()` method
4. Add route in `app/api/ingest.py`

### Customizing Retrieval

Modify `app/services/retrieval.py` to adjust:
- Retrieval weights
- Chunking strategies
- Temporal parsing logic

## 📝 License

MIT

## 🤝 Contributing

This is a take-home assignment. For production use, consider:
- Adding authentication/authorization
- Implementing rate limiting
- Adding comprehensive error handling
- Setting up monitoring and logging
- Adding unit and integration tests

## 📚 Additional Documentation

- [System Design Document](./SYSTEM_DESIGN.md) - Comprehensive architecture details
- [API Documentation](http://localhost:8000/docs) - Interactive API docs

