# Cloud Deployment Guide

This guide covers deploying TwinMind to the cloud. We'll use a hybrid approach that's cost-effective and scalable.

## 🏗️ Architecture Overview

**Recommended Setup:**
- **Backend**: Railway or Render (handles FastAPI + PostgreSQL + Redis)
- **Vector DB**: Qdrant Cloud (free tier available)
- **Storage**: AWS S3 or Railway Disk (for file storage)
- **Frontend**: Vercel (perfect for Next.js, free tier)

---

## 🚀 Option 1: Railway (Recommended - Easiest)

Railway can host everything except Qdrant. Best for quick deployment.

### Step 1: Deploy Backend to Railway

1. **Go to Railway**: https://railway.app/
2. **Sign up** (use GitHub login)
3. **New Project** → **Deploy from GitHub repo**
4. **Select your TwinMind repository**
5. **Add Service** → **Database** → **PostgreSQL** (Railway will provide connection string)
6. **Add Service** → **Database** → **Redis** (Railway will provide connection string)

7. **Configure Backend Service:**
   - **Root Directory**: `backend`
   - **Build Command**: (auto-detected from Dockerfile)
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

8. **Add Environment Variables:**
   ```
   DATABASE_URL=<from Railway PostgreSQL service>
   REDIS_URL=<from Railway Redis service>
   QDRANT_URL=<from Qdrant Cloud - see Step 2>
   QDRANT_API_KEY=<from Qdrant Cloud>
   OPENAI_API_KEY=your_openai_key_here
   S3_ENDPOINT_URL=https://s3.amazonaws.com (or use Railway Disk)
   S3_ACCESS_KEY=your_aws_access_key
   S3_SECRET_KEY=your_aws_secret_key
   S3_BUCKET_NAME=twinmind-storage
   S3_REGION=us-east-1
   STORAGE_TYPE=s3
   ALLOWED_ORIGINS=<your-frontend-url>
   ENVIRONMENT=production
   ```

### Step 2: Set Up Qdrant Cloud

1. **Go to Qdrant Cloud**: https://cloud.qdrant.io/
2. **Sign up** (free tier available)
3. **Create Cluster** → Choose region
4. **Copy Connection URL and API Key**
5. Add to Railway environment variables

### Step 3: Set Up AWS S3 (or Use Railway Disk)

**Option A: AWS S3**
1. Go to AWS Console → S3
2. Create bucket: `twinmind-storage`
3. Create IAM user with S3 access
4. Copy Access Key and Secret Key

**Option B: Railway Disk (Simpler)**
- Railway provides disk storage, but requires code changes to use local storage

### Step 4: Deploy Frontend to Vercel

1. **Go to Vercel**: https://vercel.com/
2. **Sign up** (use GitHub login)
3. **New Project** → **Import** your GitHub repo
4. **Configure:**
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next`

5. **Add Environment Variable:**
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-backend.railway.app
   ```

6. **Deploy!**

✅ **Result**: Your app is live!

---

## 🌐 Option 2: Render (Alternative to Railway)

Similar to Railway, good free tier.

### Backend on Render

1. **Go to Render**: https://render.com/
2. **New** → **Web Service**
3. **Connect GitHub** → Select repo
4. **Configure:**
   - **Name**: `twinmind-backend`
   - **Root Directory**: `backend`
   - **Build Command**: (auto-detected)
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Add PostgreSQL**: New → PostgreSQL (free tier)
6. **Add Redis**: New → Redis (free tier)
7. **Add Environment Variables** (same as Railway)

### Frontend on Vercel

Same as Option 1, Step 4.

---

## 🔧 Option 3: All-in-One on Fly.io

Fly.io can host everything including Qdrant.

### Setup

1. **Install Fly CLI**: `brew install flyctl`
2. **Login**: `fly auth login`
3. **Create app**: `fly launch` (in project root)
4. **Deploy**: `fly deploy`

**Note**: Requires more configuration for multiple services. See Fly.io docs.

---

## 📝 Environment Variables Checklist

### Backend Variables (Railway/Render)

```bash
# Database (from Railway/Render)
DATABASE_URL=postgresql+asyncpg://...

# Redis (from Railway/Render)
REDIS_URL=redis://...

# Qdrant Cloud
QDRANT_URL=https://xxx.qdrant.io
QDRANT_API_KEY=xxx

# OpenAI
OPENAI_API_KEY=sk-xxx
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_LLM_MODEL=gpt-4-turbo-preview

# Storage
STORAGE_TYPE=s3
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=xxx
S3_SECRET_KEY=xxx
S3_BUCKET_NAME=twinmind-storage
S3_REGION=us-east-1

# Application
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend.vercel.app
SECRET_KEY=generate-random-key
```

### Frontend Variables (Vercel)

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## 🚦 Deployment Steps (Quick Reference)

1. ✅ Push code to GitHub (already done!)
2. ✅ Set up Qdrant Cloud
3. ✅ Set up AWS S3 bucket
4. ⏳ Deploy backend to Railway/Render
5. ⏳ Deploy frontend to Vercel
6. ⏳ Update CORS settings
7. ⏳ Test deployment

---

## 🔍 Post-Deployment Checklist

- [ ] Backend is accessible at production URL
- [ ] Frontend is accessible at production URL
- [ ] CORS is configured correctly
- [ ] Environment variables are set
- [ ] Database migrations ran successfully
- [ ] Qdrant collection is created
- [ ] S3 bucket is accessible
- [ ] Test upload/ingestion
- [ ] Test querying

---

## 💰 Cost Estimate (Monthly)

**Free Tier (Small Usage):**
- Railway Backend: Free (500 hours/month)
- Vercel Frontend: Free
- Qdrant Cloud: Free tier (1GB)
- AWS S3: ~$0.023/GB/month
- **Total: ~$0-5/month**

**Paid (Production):**
- Railway: $5-20/month
- Vercel: Free (or $20/month Pro)
- Qdrant: $25/month (starter)
- AWS S3: ~$5/month
- **Total: ~$35-70/month**

---

## 🐛 Troubleshooting

### CORS Errors
- Make sure `ALLOWED_ORIGINS` includes your frontend URL
- No trailing slashes in URLs

### Database Connection Issues
- Check connection string format
- Ensure PostgreSQL/Redis services are running
- Check firewall/network settings

### Qdrant Connection
- Verify Qdrant URL and API key
- Check if collection exists (will be created on first use)

### File Upload Issues
- Verify S3 credentials
- Check bucket permissions
- Ensure bucket exists

---

## 📚 Additional Resources

- [Railway Docs](https://docs.railway.app/)
- [Vercel Docs](https://vercel.com/docs)
- [Qdrant Cloud](https://cloud.qdrant.io/)
- [AWS S3 Setup](https://aws.amazon.com/s3/)

---

## 🎯 Next Steps

See the individual deployment scripts below for step-by-step instructions for each platform.

