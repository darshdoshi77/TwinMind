# Deployment Guide

## Local Development Setup

### Option 1: Using Docker Compose (Recommended)

1. **Start all services:**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Qdrant (port 6333)
- MinIO (ports 9000, 9001)
- Redis (port 6379)
- Backend API (port 8000)
- Frontend (port 3000)

2. **Set environment variables:**
Create `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/twinmind
QDRANT_URL=http://localhost:6333
OPENAI_API_KEY=your_key_here
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=twinmind-storage
```

3. **Initialize MinIO bucket:**
Visit http://localhost:9001 and create bucket `twinmind-storage`

4. **Access the application:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend

1. Install Python dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Set up PostgreSQL:
```bash
createdb twinmind
```

3. Set up Qdrant:
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

4. Set up MinIO (optional, or use local storage):
```bash
docker run -d -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

5. Run backend:
```bash
uvicorn app.main:app --reload
```

#### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run frontend:
```bash
npm run dev
```

## Production Deployment

### Backend Deployment

#### Using Docker

1. Build image:
```bash
cd backend
docker build -t twinmind-backend .
```

2. Run container:
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://... \
  -e OPENAI_API_KEY=... \
  -e QDRANT_URL=... \
  twinmind-backend
```

#### Using Cloud Platforms

**Heroku:**
```bash
heroku create twinmind-api
heroku addons:create heroku-postgresql
heroku config:set OPENAI_API_KEY=...
git push heroku main
```

**AWS/GCP/Azure:**
- Use container services (ECS, Cloud Run, Container Apps)
- Set up managed PostgreSQL
- Use managed vector DB or deploy Qdrant
- Configure environment variables

### Frontend Deployment

#### Vercel (Recommended for Next.js)

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

#### Other Platforms

**Docker:**
```bash
cd frontend
docker build -t twinmind-frontend .
docker run -d -p 3000:3000 -e NEXT_PUBLIC_API_URL=... twinmind-frontend
```

**Static Export:**
```bash
npm run build
npm run export
# Serve the 'out' directory
```

### Infrastructure Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 20GB storage

**Recommended:**
- 4 CPU cores
- 8GB RAM
- 100GB storage (for vector DB + object storage)

### Environment Variables Checklist

**Backend:**
- [ ] `DATABASE_URL`
- [ ] `QDRANT_URL` (and `QDRANT_API_KEY` if using cloud)
- [ ] `OPENAI_API_KEY`
- [ ] `OPENAI_EMBEDDING_MODEL`
- [ ] `OPENAI_LLM_MODEL`
- [ ] `STORAGE_TYPE` (s3 or local)
- [ ] S3/MinIO credentials if using S3
- [ ] `SECRET_KEY` (generate secure random key)

**Frontend:**
- [ ] `NEXT_PUBLIC_API_URL`

### Security Checklist

- [ ] Use HTTPS in production
- [ ] Set strong `SECRET_KEY`
- [ ] Enable CORS only for your domain
- [ ] Use environment variables for secrets
- [ ] Enable database SSL
- [ ] Set up rate limiting
- [ ] Add authentication/authorization
- [ ] Enable logging and monitoring

### Monitoring

Recommended tools:
- **Application**: Sentry, Datadog
- **Infrastructure**: Prometheus, Grafana
- **Logs**: ELK Stack, CloudWatch

### Scaling

**Horizontal Scaling:**
- Use load balancer for multiple API instances
- Qdrant cluster mode
- PostgreSQL read replicas
- Redis cluster for caching

**Vertical Scaling:**
- Increase resources for vector DB (most critical)
- More CPU/RAM for embedding generation
- Larger storage for object storage

## Troubleshooting

### Database Connection Issues
- Check `DATABASE_URL` format
- Verify PostgreSQL is running
- Check network connectivity

### Vector DB Issues
- Verify Qdrant is accessible
- Check collection exists (auto-created on first use)
- Verify API key if using cloud

### Storage Issues
- Check S3/MinIO credentials
- Verify bucket exists
- Check permissions

### API Errors
- Check logs: `docker-compose logs backend`
- Verify environment variables
- Check OpenAI API key and quota

