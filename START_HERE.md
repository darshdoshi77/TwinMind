# 👋 START HERE - TwinMind Quick Overview

## 📖 What is TwinMind?

**TwinMind** is your "Second Brain" - an AI companion that:
- 💾 Remembers everything you show it (documents, audio, web articles, notes)
- 🧠 Understands what you mean (semantic search, not just keywords)
- ⏰ Knows when things happened (time-aware queries)
- 💬 Answers your questions intelligently (with source citations)

### Real Example:
```
You: "What did we discuss in the project meeting last Tuesday?"
TwinMind: "Based on the meeting transcript from Tuesday, January 16th, 
the key points discussed were: 1) Timeline for Q2 features... 
[Source: project_meeting_audio.mp3]"
```

---

## 🚀 Quick Start (5 Minutes)

### 1. Prerequisites
- ✅ Docker Desktop installed
- ✅ OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### 2. Setup
```bash
# 1. Set your OpenAI API key
cd backend
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/twinmind" >> .env
echo "QDRANT_URL=http://localhost:6333" >> .env
echo "S3_ENDPOINT_URL=http://localhost:9000" >> .env
echo "S3_ACCESS_KEY=minioadmin" >> .env
echo "S3_SECRET_KEY=minioadmin" >> .env
echo "S3_BUCKET_NAME=twinmind-storage" >> .env

# 2. Setup frontend
cd ../frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# 3. Start everything
cd ..
docker-compose up -d

# 4. Wait 30 seconds, then create MinIO bucket
# Open http://localhost:9001
# Login: minioadmin / minioadmin
# Create bucket: twinmind-storage
```

### 3. Test It!
1. Open http://localhost:3000
2. Click "Add Content" → "Text" tab
3. Add some text (e.g., "I learned about Python today")
4. Ask: "What did I learn about today?"

---

## 📚 Documentation

- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Complete testing instructions with examples
- **[PROJECT_EXPLANATION.md](./PROJECT_EXPLANATION.md)** - Deep dive into what TwinMind is and how it works
- **[SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md)** - Full architecture and technical design
- **[README.md](./README.md)** - Technical documentation
- **[QUICK_START.md](./QUICK_START.md)** - Alternative quick start guide
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment guide

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Modal Ingestion** | Audio, PDFs, web articles, text notes |
| **Hybrid Search** | Vector (semantic) + keyword search combined |
| **Temporal Queries** | "What did I add last week?" |
| **Streaming Responses** | Real-time token-by-token answers |
| **Source Citation** | Always shows where information came from |

---

## 🏗️ Architecture in 30 Seconds

```
User Input → FastAPI Backend → Processing Pipeline
                                ↓
                    ┌───────────┴───────────┐
                    ↓                       ↓
            PostgreSQL (metadata)    Qdrant (vectors)
                    ↓                       ↓
                    └───────────┬───────────┘
                                ↓
                    Hybrid Retrieval
                                ↓
                    LLM Synthesis
                                ↓
                    Streaming Response
```

---

## 🧪 Quick Test Checklist

- [ ] Services start (`docker-compose ps` shows all "Up")
- [ ] Backend health check works (`curl http://localhost:8000/api/v1/health`)
- [ ] Frontend loads (http://localhost:3000)
- [ ] Can add text content
- [ ] Can query and get answer
- [ ] Streaming responses work

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for detailed test scenarios.

---

## ❓ Common Questions

**Q: How do I test without Docker?**  
A: See [DEPLOYMENT.md](./DEPLOYMENT.md) for manual setup instructions.

**Q: What if I get connection errors?**  
A: Wait 30-60 seconds after starting, services need time to initialize.

**Q: How do I see what's in my knowledge base?**  
A: Use the API: `curl http://localhost:8000/api/v1/sources?user_id=YOUR_ID`

**Q: Can I use a different LLM?**  
A: Yes! Change `LLM_PROVIDER` in `.env` to "anthropic" for Claude.

---

## 🎓 Understanding the Project

**New to the project?** Read:
1. **[PROJECT_EXPLANATION.md](./PROJECT_EXPLANATION.md)** - What TwinMind is and why it exists
2. **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - How to test and use it
3. **[SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md)** - Technical deep dive

**Ready to code?** Check:
- `backend/app/` - API and business logic
- `frontend/components/` - UI components
- `backend/app/services/` - Core services (retrieval, LLM, embeddings)

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Services won't start | `docker-compose down && docker-compose up -d` |
| API errors | Check OpenAI API key in `backend/.env` |
| No responses | Wait for processing, check browser console |
| MinIO errors | Create bucket at http://localhost:9001 |

---

## 📞 Next Steps

1. ✅ Run quick start above
2. ✅ Test basic functionality
3. ✅ Read PROJECT_EXPLANATION.md for understanding
4. ✅ Explore codebase
5. ✅ Customize and extend!

**Happy building! 🚀**

