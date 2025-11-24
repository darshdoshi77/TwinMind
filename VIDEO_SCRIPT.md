# Video Walkthrough Script

**Target Duration:** 5-10 minutes  
**Format:** Screen recording with voiceover

---

## 🎬 Part 1: Introduction (1-2 minutes)

### Script:
"Hi! I'm [Your Name], and today I'm excited to walk you through **TwinMind** - my implementation of a Second Brain AI Companion.

TwinMind is a full-stack AI system that serves as your personal knowledge assistant. It can ingest information from multiple sources - audio files, documents, web articles, and text notes - and then intelligently answer your questions using natural language.

What makes TwinMind special is its hybrid retrieval approach: it combines semantic vector search with keyword-based search and temporal awareness, giving you accurate, context-aware answers that understand both what you're asking and when the information was relevant."

### Screen Actions:
- Show the TwinMind interface (http://localhost:3000)
- Show the chat interface
- Show the "Add Content" button

---

## 🏗️ Part 2: System Architecture (2-3 minutes)

### Script:
"Let me walk you through the key architectural decisions I made, and why I made them.

First, the overall architecture: I chose a modern, async-first stack - FastAPI for the backend and Next.js for the frontend. This gives us excellent performance for handling concurrent requests, which is crucial when processing large files or handling multiple users.

**Hybrid Retrieval Strategy:**

I implemented a three-pronged retrieval approach:
1. **Semantic Search (70% weight)** - Uses vector embeddings to understand the meaning and intent behind queries
2. **Keyword Search (20% weight)** - Full-text search for exact matches and specific terms
3. **Temporal Relevance (10% weight)** - Boosts results based on recency and time-based queries

This hybrid approach ensures we get both semantic understanding and precision - something pure vector search sometimes misses.

**Multi-Database Architecture:**

For storage, I chose a multi-database approach:
- **PostgreSQL** for metadata, relationships, and full-text search
- **Qdrant** for vector embeddings and similarity search
- **MinIO** (S3-compatible) for raw file storage

This separation of concerns allows each database to excel at what it does best, rather than forcing everything into one system."

### Screen Actions:
- Open `SYSTEM_DESIGN.md` document
- Point to the architecture diagram
- Show the retrieval strategy section
- Show the storage architecture section

---

## 🤔 Part 3: Key Trade-offs & Decisions (2-3 minutes)

### Script:
"Now let me explain some of the key trade-offs I considered and the decisions I made.

**Trade-off 1: Vector Database Choice**

I chose Qdrant over Pinecone for several reasons:
- **Self-hosting capability**: Qdrant can run locally, which is important for privacy-sensitive data
- **Open source**: Full control and no vendor lock-in
- **Performance**: Excellent performance for our use case, with the ability to scale horizontally

The trade-off is that we need to manage the infrastructure ourselves, but for a personal second brain, this gives users more control.

**Trade-off 2: Retrieval Strategy Weighting**

The 70/20/10 weighting (semantic/keyword/temporal) was chosen based on testing:
- **70% semantic** because most queries are conceptual - users ask "what did I learn about X?" not just "find the word X"
- **20% keyword** because sometimes you need exact matches, especially for names, dates, or specific terms
- **10% temporal** because recency matters, but shouldn't override relevance

This weighting can be adjusted per-user, but these defaults work well for most queries.

**Trade-off 3: Chunking Strategy**

I use different chunking strategies for different content types:
- **Audio transcripts**: Sentence-based chunking to preserve conversational flow
- **Documents**: Paragraph-based chunking to maintain document structure
- **Web content**: Section-based chunking following HTML structure

The challenge here is balancing chunk size - too large, and we lose precision; too small, and we lose context. I settled on ~1000 tokens per chunk with 100-token overlap between chunks."

### Screen Actions:
- Show `backend/app/services/retrieval.py` (hybrid search implementation)
- Show chunking code in processors
- Explain the weighting logic

---

## 🎯 Part 4: Live Demo (3-4 minutes)

### Script:
"Now let's see TwinMind in action! I'll demonstrate ingesting different types of content and then querying the system.

**Step 1: Ingest Audio**

First, let me upload an audio file - maybe a meeting recording or voice memo. [Upload audio file]

The system will transcribe this using OpenAI's Whisper API. This happens in the background, so we get immediate feedback. You can see the status update in real-time.

[Wait for transcription to complete or show it processing]

**Step 2: Ingest Document**

Now let me upload a document - maybe a PDF of an article or research paper. [Upload PDF]

The system extracts the text, preserves structure like page numbers and headings, and chunks it intelligently.

**Step 3: Add Web Content**

I can also add web articles. Let me add an article about AI. [Add URL]

The system scrapes the main content, filters out ads and navigation, and ingests the core content.

**Step 4: Add Text Note**

Finally, I can add plain text notes directly. [Add text note]

Now that we have content in the system, let's query it.

**Query 1: Recent Content**

'What did I add recently?'

The system understands temporal queries and retrieves the most recent additions.

**Query 2: Specific Query**

'Summarize the audio I uploaded'

This uses semantic search to find the relevant audio transcript and provides a summary.

**Query 3: Temporal Query**

'What did I work on this week?'

The system filters by time range and retrieves relevant information from the specified period.

As you can see, the responses are contextual, accurate, and cite their sources - you can see where each piece of information came from."

### Screen Actions:
- Upload audio file, show processing status
- Upload document
- Add web URL
- Add text note
- Show the Sources panel with all ingested content
- Run queries and show streaming responses
- Show source citations

---

## 💻 Part 5: Code Highlights (1-2 minutes)

### Script:
"Let me quickly highlight some key parts of the implementation.

The retrieval service implements our hybrid search - notice how it combines vector similarity, keyword matching, and temporal relevance into a single score.

The processors are modular - each data type has its own processor, making it easy to add new types in the future. They all inherit from a base processor that handles common tasks like chunking and embedding.

The frontend uses React Server Components and streaming to provide a responsive, real-time experience. When you ask a question, you see the response stream in token by token, just like ChatGPT."

### Screen Actions:
- Show `backend/app/services/retrieval.py` - highlight hybrid search logic
- Show processor base class and one example processor
- Show frontend streaming implementation in `ChatInterface.tsx`

---

## 🎬 Part 6: Conclusion (30 seconds)

### Script:
"So to summarize, TwinMind is a complete, production-ready system that demonstrates:

1. **Solid architecture**: Modular, scalable, and well-thought-out
2. **Smart retrieval**: Hybrid approach that balances semantic understanding with precision
3. **Multi-modal support**: Handles audio, documents, web, and text seamlessly
4. **Great UX**: Clean interface with real-time feedback and streaming responses

If I had more time, I'd add:
- Authentication and multi-user support
- Image processing with OCR
- More sophisticated temporal parsing
- Rate limiting and caching layers

But even as-is, TwinMind showcases the key architectural principles and trade-offs involved in building a production AI system.

Thank you for watching, and I'm happy to answer any questions!"

### Screen Actions:
- Show final overview of the application
- Show the SYSTEM_DESIGN.md document
- Close with a nice view of the chat interface

---

## 📝 Recording Tips

1. **Before Recording:**
   - Make sure all services are running (`docker-compose up -d`)
   - Have test files ready (audio, PDF, web URL)
   - Close unnecessary applications
   - Test your microphone

2. **During Recording:**
   - Speak clearly and at a moderate pace
   - Pause between sections
   - Don't worry about mistakes - you can edit later
   - Show the code, don't just talk about it

3. **Editing:**
   - Trim long pauses
   - Add text overlays for key points (optional)
   - Ensure audio is clear throughout

4. **Upload:**
   - Upload to YouTube as unlisted
   - Or upload to Vimeo
   - Or provide download link

**Good luck with your recording! 🎥**

