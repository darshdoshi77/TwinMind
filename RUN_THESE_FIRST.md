# 🎯 Run These Commands FIRST

## Quick Answer: YES, you need to run setup commands before testing!

---

## 📝 Step-by-Step (Copy & Paste)

### Step 1: Add Your OpenAI API Key

```bash
cd /Users/darshdoshi/Documents/TwinMind/backend
nano .env
```

**OR create the file:**
```bash
cat > backend/.env << 'EOF'
OPENAI_API_KEY=sk-YOUR_ACTUAL_KEY_HERE
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/twinmind
QDRANT_URL=http://localhost:6333
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=twinmind-storage
EOF
```

**⚠️ REPLACE `sk-YOUR_ACTUAL_KEY_HERE` with your real OpenAI API key!**

Get key: https://platform.openai.com/api-keys

### Step 2: Setup Frontend

```bash
cd /Users/darshdoshi/Documents/TwinMind/frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### Step 3: Start Services

```bash
cd /Users/darshdoshi/Documents/TwinMind
docker-compose up -d
```

**Wait 30-60 seconds** ⏳

### Step 4: Create MinIO Bucket

1. Open browser: **http://localhost:9001**
2. Login: `minioadmin` / `minioadmin`
3. Click **"Create Bucket"**
4. Name: `twinmind-storage`
5. Click **"Create Bucket"**

---

## 🚀 OR Use the Automated Setup Script

```bash
cd /Users/darshdoshi/Documents/TwinMind
./setup.sh
```

This will:
- ✅ Create .env files
- ✅ Start Docker services
- ✅ Remind you to add API key
- ✅ Tell you to create MinIO bucket

**After running setup.sh:**
1. Edit `backend/.env` and add your OpenAI API key
2. Create MinIO bucket at http://localhost:9001

---

## ✅ Verify Setup Complete

```bash
# Check services are running
docker-compose ps

# Check backend is healthy
curl http://localhost:8000/api/v1/health
```

**Expected output:**
```
{"status":"healthy","service":"twinmind-api"}
```

---

## 🎉 NOW You Can Test!

**Option 1: Automated test**
```bash
./test_api.sh
```

**Option 2: Browser test**
- Open http://localhost:3000
- Add content → Ask questions

---

## ❌ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Wait 30-60 seconds after `docker-compose up -d` |
| "API key invalid" | Add your OpenAI API key to `backend/.env` |
| "Bucket not found" | Create bucket at http://localhost:9001 |
| Services not starting | Run `docker-compose logs` to see errors |

---

## 📋 Quick Checklist

Before testing, make sure:

- [ ] ✅ Added OpenAI API key to `backend/.env`
- [ ] ✅ Created `frontend/.env.local`
- [ ] ✅ Ran `docker-compose up -d`
- [ ] ✅ Waited 30 seconds
- [ ] ✅ Created MinIO bucket `twinmind-storage`
- [ ] ✅ `docker-compose ps` shows all "Up"

**All checked? → You're ready!** 🎉

