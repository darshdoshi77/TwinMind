# ⚙️ Setup Before Testing - REQUIRED STEPS

## 🔴 Before You Can Test, You MUST:

### Step 1: Set Up Environment Variables

**Backend needs your OpenAI API key:**

```bash
cd /Users/darshdoshi/Documents/TwinMind/backend

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=sk-your-actual-api-key-here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/twinmind
QDRANT_URL=http://localhost:6333
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=twinmind-storage
EOF
```

**⚠️ IMPORTANT**: Replace `sk-your-actual-api-key-here` with your real OpenAI API key!

Get one at: https://platform.openai.com/api-keys

**Frontend needs API URL:**

```bash
cd /Users/darshdoshi/Documents/TwinMind/frontend

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### Step 2: Start Docker Services

```bash
cd /Users/darshdoshi/Documents/TwinMind
docker-compose up -d
```

**Wait 30-60 seconds** for all services to start.

### Step 3: Initialize MinIO Bucket

1. Open browser: http://localhost:9001
2. Login:
   - Username: `minioadmin`
   - Password: `minioadmin`
3. Click "Create Bucket"
4. Bucket name: `twinmind-storage`
5. Click "Create Bucket"

### Step 4: Verify Services Started

```bash
docker-compose ps
```

All services should show "Up" status.

---

## ✅ Complete Setup Script

Run this all at once:

```bash
cd /Users/darshdoshi/Documents/TwinMind

# 1. Setup backend .env (EDIT THE API KEY!)
cd backend
cat > .env << 'EOF'
OPENAI_API_KEY=sk-YOUR_KEY_HERE
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/twinmind
QDRANT_URL=http://localhost:6333
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=twinmind-storage
EOF
echo "⚠️  EDIT backend/.env AND ADD YOUR OPENAI API KEY!"

# 2. Setup frontend .env.local
cd ../frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# 3. Start services
cd ..
docker-compose up -d

echo ""
echo "✅ Services starting... wait 30 seconds"
echo ""
echo "📋 Next steps:"
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Open http://localhost:9001 and create bucket 'twinmind-storage'"
echo "3. Wait 30 seconds, then run: ./test_api.sh"
```

---

## 🔍 Quick Setup Verification

After setup, verify everything is ready:

```bash
# Check if backend has API key
grep "OPENAI_API_KEY=sk-" backend/.env
# Should show your key (not empty)

# Check if services are running
docker-compose ps | grep "Up"
# Should show 6 services

# Check backend health
curl http://localhost:8000/api/v1/health
# Should return: {"status":"healthy","service":"twinmind-api"}
```

---

## 🚀 NOW You Can Test!

Once all steps above are done:

**Option 1: Automated Test**
```bash
./test_api.sh
```

**Option 2: Browser Test**
- Open http://localhost:3000
- Click "Add Content"
- Add text
- Ask a question

---

## ❌ Common Issues

### "OPENAI_API_KEY not found"
- You didn't edit `backend/.env` with your API key
- **Fix**: Edit the file and add your key

### "Connection refused"
- Services aren't running yet
- **Fix**: Wait 30-60 seconds after `docker-compose up -d`

### "Bucket does not exist"
- You didn't create the MinIO bucket
- **Fix**: Go to http://localhost:9001 and create `twinmind-storage` bucket

### Frontend can't connect
- Backend isn't running
- **Fix**: Check `docker-compose ps` and `docker-compose logs backend`

---

## 📋 Setup Checklist

Before testing, make sure:

- [ ] OpenAI API key added to `backend/.env`
- [ ] Frontend `.env.local` created with API URL
- [ ] `docker-compose up -d` has been run
- [ ] Waited 30-60 seconds for services to start
- [ ] MinIO bucket `twinmind-storage` created at http://localhost:9001
- [ ] `docker-compose ps` shows all services "Up"
- [ ] `curl http://localhost:8000/api/v1/health` returns healthy

**Once all checked ✅ → You're ready to test!**

