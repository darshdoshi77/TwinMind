# Testing Guide for TwinMind

## 🎯 What is TwinMind?

**TwinMind** is a "Second Brain" AI Companion - think of it as a personal AI assistant with perfect memory. It can:

1. **Ingest Information** from multiple sources:
   - 📎 Documents (PDFs, Markdown, Word docs, text files)
   - 🎵 Audio files (transcribes meetings, podcasts, voice notes)
   - 🌐 Web articles (scrapes and saves web content)
   - 📝 Plain text notes

2. **Remember Everything**: All your content is processed, chunked, and stored with embeddings for semantic search

3. **Answer Questions Intelligently**: Ask natural language questions and get answers based on your entire knowledge base, with source citations

4. **Time-Aware**: Ask questions like "What did I work on last week?" and it knows what content you added when

---

## 🧪 Testing Guide

### Prerequisites Setup

1. **Install Docker Desktop** (if not already installed)
   - Download from: https://www.docker.com/products/docker-desktop

2. **Get OpenAI API Key**
   - Sign up at: https://platform.openai.com/
   - Create API key at: https://platform.openai.com/api-keys

3. **Clone/Navigate to Project**
```bash
cd /Users/darshdoshi/Documents/TwinMind
```

### Step 1: Environment Setup

1. **Create backend environment file:**
```bash
cd backend
cp .env.example .env
# Or create .env manually
```

2. **Edit `backend/.env` and add your OpenAI API key:**
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/twinmind
QDRANT_URL=http://localhost:6333
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=twinmind-storage
```

3. **Create frontend environment file:**
```bash
cd ../frontend
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### Step 2: Start Services

1. **Start all services with Docker Compose:**
```bash
cd /Users/darshdoshi/Documents/TwinMind
docker-compose up -d
```

This starts:
- PostgreSQL (database)
- Qdrant (vector database)
- MinIO (object storage)
- Redis (caching)
- Backend API
- Frontend UI

2. **Wait for services to be ready** (check status):
```bash
docker-compose ps
```

All services should show "Up" status. Wait about 30 seconds for full initialization.

3. **Initialize MinIO Bucket:**
   - Open browser: http://localhost:9001
   - Login: `minioadmin` / `minioadmin`
   - Click "Create Bucket"
   - Bucket name: `twinmind-storage`
   - Click "Create Bucket"

### Step 3: Verify Services

1. **Check Backend Health:**
```bash
curl http://localhost:8000/api/v1/health
```

Should return: `{"status":"healthy","service":"twinmind-api"}`

2. **Check Frontend:**
   - Open browser: http://localhost:3000
   - Should see TwinMind interface

3. **Check API Docs:**
   - Open: http://localhost:8000/docs
   - Should see interactive API documentation

---

## 📝 Testing Scenarios

### Test 1: Ingest a Text Note

**Goal**: Add some text content to the knowledge base

**Steps**:
1. Open http://localhost:3000
2. Click "Add Content" button (top right)
3. Click "Text" tab
4. Enter title: "My First Note"
5. Enter text:
   ```
   Today I learned about vector embeddings. They are numerical representations of text that capture semantic meaning. Similar texts have similar embeddings, which allows for semantic search.
   ```
6. Click "Save Text"

**Expected**: Success message, text is saved and processed

**Verify via API**:
```bash
# Replace YOUR_USER_ID with actual user ID (check browser localStorage or use any UUID)
curl http://localhost:8000/api/v1/sources?user_id=YOUR_USER_ID
```

### Test 2: Query the Knowledge Base

**Goal**: Ask a question about ingested content

**Steps**:
1. In the chat interface, type: "What did I learn about today?"
2. Click Send

**Expected**: 
- Streaming response appears word-by-word
- Answer mentions vector embeddings
- Sources are cited at the bottom

**Alternative - Test via API**:
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What did I learn about today?",
    "user_id": "YOUR_USER_ID",
    "max_results": 5
  }'
```

### Test 3: Ingest a Web Article

**Goal**: Scrape and save web content

**Steps**:
1. Click "Add Content"
2. Click "Web" tab
3. Enter URL: `https://en.wikipedia.org/wiki/Vector_space_model`
4. Click "Ingest Web Content"

**Expected**: Success message, article content is saved

**Then query**:
```
"Explain vector spaces in simple terms"
```

### Test 4: Upload a Document (PDF)

**Goal**: Process a document file

**Steps**:
1. Create a simple PDF or text file with some content
2. Click "Add Content"
3. Click "File" tab
4. Choose your PDF/text file
5. Upload

**Expected**: File uploads and processing begins

**Note**: Processing happens in background, check sources list after a few seconds

### Test 5: Temporal Query

**Goal**: Test time-aware queries

**Steps**:
1. Add multiple text notes on different days (or simulate by adding notes now)
2. Wait a moment for processing
3. Ask: "What did I add today?"

**Expected**: Lists content added today

**Alternative**:
- Ask: "Show me content from this week"
- Ask: "What did I work on recently?"

### Test 6: Audio Transcription (Requires Audio File)

**Goal**: Transcribe audio and make it searchable

**Steps**:
1. Prepare an audio file (.mp3, .m4a, or .wav)
2. Click "Add Content"
3. Click "File" tab
4. Upload audio file

**Expected**: 
- File uploads
- Transcription happens in background (may take time)
- Once processed, you can ask questions about the audio content

**Example queries after transcription**:
- "What was discussed in the meeting?"
- "Summarize the audio I just uploaded"

---

## 🔍 Advanced Testing

### Test API Endpoints Directly

1. **List Sources:**
```bash
curl "http://localhost:8000/api/v1/sources?user_id=YOUR_USER_ID"
```

2. **Get Source Details:**
```bash
curl "http://localhost:8000/api/v1/sources/SOURCE_ID?user_id=YOUR_USER_ID"
```

3. **Query with Streaming:**
```bash
curl -N -X POST "http://localhost:8000/api/v1/query/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is in my knowledge base?",
    "user_id": "YOUR_USER_ID",
    "max_results": 10
  }'
```

The `-N` flag shows streaming output in real-time.

### Test Database Directly

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d twinmind

# Check users
SELECT * FROM users;

# Check sources
SELECT id, source_type, source_name, ingestion_timestamp FROM sources;

# Check chunks
SELECT id, chunk_index, LEFT(text, 50) as text_preview FROM chunks LIMIT 5;

# Exit
\q
```

### Test Vector Database

```bash
# Check Qdrant collections
curl http://localhost:6333/collections
```

---

## 🐛 Troubleshooting

### Issue: Services won't start

**Solution**:
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d

# Check if ports are already in use
lsof -i :8000
lsof -i :3000
```

### Issue: "Connection refused" errors

**Solution**:
- Wait longer for services to initialize (30-60 seconds)
- Check service health: `docker-compose ps`
- Verify environment variables are set correctly

### Issue: OpenAI API errors

**Solution**:
- Verify API key is correct in `backend/.env`
- Check API key has credits/quota
- Test API key directly:
  ```bash
  curl https://api.openai.com/v1/models \
    -H "Authorization: Bearer YOUR_API_KEY"
  ```

### Issue: MinIO bucket errors

**Solution**:
- Ensure bucket `twinmind-storage` is created
- Check MinIO is accessible: http://localhost:9000
- Verify credentials in `.env` match MinIO console

### Issue: No responses in chat

**Solution**:
- Check browser console for errors (F12)
- Verify backend is running: http://localhost:8000/api/v1/health
- Check CORS settings in backend
- Ensure `NEXT_PUBLIC_API_URL` is set in frontend `.env.local`

### Issue: Empty query results

**Solution**:
- Ensure content has been ingested first
- Wait a few seconds after ingestion for processing
- Check sources list to verify content is saved
- Try broader queries

---

## 📊 Expected Test Results

### Successful Test Flow:

1. ✅ Services start without errors
2. ✅ Can ingest text content
3. ✅ Can query and get relevant answers
4. ✅ Answers cite sources
5. ✅ Streaming responses work smoothly
6. ✅ Web content ingestion works
7. ✅ File uploads work
8. ✅ Temporal queries return filtered results

### Performance Expectations:

- **Text ingestion**: < 2 seconds
- **Query response**: < 3 seconds (first token), full response in 5-15 seconds
- **Streaming**: Real-time, token-by-token
- **Document processing**: 5-30 seconds depending on size
- **Audio transcription**: 30 seconds - 5 minutes depending on length

---

## 🎬 Demo Flow Recommendation

For video walkthrough, demonstrate:

1. **Architecture Overview** (2 min)
   - Show system design document
   - Explain hybrid retrieval
   - Show component diagram

2. **Ingestion** (2 min)
   - Add text note
   - Upload a document
   - Ingest web article

3. **Querying** (3 min)
   - Basic query
   - Temporal query ("what did I add today?")
   - Complex query ("summarize everything about X")

4. **Technical Deep Dive** (3 min)
   - Show API docs
   - Explain retrieval strategy
   - Discuss trade-offs (PostgreSQL + Qdrant)

---

## 🚀 Next Steps After Testing

1. **Customize**: Modify chunking strategies, retrieval weights
2. **Scale**: Test with larger datasets
3. **Extend**: Add image processing, calendar integration
4. **Deploy**: Follow DEPLOYMENT.md for production setup

Happy Testing! 🎉

