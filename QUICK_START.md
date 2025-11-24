# Quick Start Guide

Get TwinMind running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

## Steps

1. **Clone and navigate:**
```bash
cd TwinMind
```

2. **Create environment file:**
```bash
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. **Start services:**
```bash
cd ..
docker-compose up -d
```

4. **Wait for services to be ready** (about 30 seconds)

5. **Initialize MinIO bucket:**
- Open http://localhost:9001
- Login: minioadmin / minioadmin
- Create bucket: `twinmind-storage`

6. **Access the application:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Test It Out

1. **Add some content:**
   - Click "Add Content" in the frontend
   - Upload a PDF or audio file
   - Or paste some text

2. **Ask a question:**
   - Type a question in the chat
   - Example: "What did I just upload?"

3. **Try temporal queries:**
   - "What did I add today?"
   - "Show me content from this week"

## Troubleshooting

**Services not starting?**
```bash
docker-compose logs
```

**Database errors?**
- Wait a bit longer for PostgreSQL to initialize
- Check `docker-compose ps` to see service status

**API errors?**
- Verify OPENAI_API_KEY in backend/.env
- Check logs: `docker-compose logs backend`

**Frontend can't connect?**
- Verify backend is running: http://localhost:8000/api/v1/health
- Check NEXT_PUBLIC_API_URL in frontend/.env.local

## Next Steps

- Read [README.md](./README.md) for detailed documentation
- Check [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) for architecture details
- See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment

