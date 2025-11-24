# Quick Verification - Is TwinMind Working?

## 🚀 Fast 5-Step Check

### Step 1: Start Services (if not already running)
```bash
cd /Users/darshdoshi/Documents/TwinMind
docker-compose up -d
```

Wait 30 seconds for services to start.

### Step 2: Run Verification Script
```bash
chmod +x verify_working.sh
./verify_working.sh
```

Or manually check each service:

---

## ✅ Manual Verification

### Check 1: Are Services Running?
```bash
docker-compose ps
```
**Expected**: All services show "Up" status

### Check 2: Is Backend Working?
```bash
curl http://localhost:8000/api/v1/health
```
**Expected**: `{"status":"healthy","service":"twinmind-api"}`

### Check 3: Is Frontend Working?
Open in browser: http://localhost:3000

**Expected**: You see the TwinMind chat interface

### Check 4: Can You Add Content?
1. Click "Add Content" button (top right)
2. Go to "Text" tab
3. Enter: "This is a test message"
4. Click "Save Text"

**Expected**: Success message appears

### Check 5: Can You Query?
1. Wait 5 seconds after adding content
2. In chat, type: "What did I just add?"
3. Click Send

**Expected**: 
- Response streams in real-time
- Answer mentions "test message"
- Sources are shown

---

## 🔧 If Something Doesn't Work

### Backend Not Responding?
```bash
# Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Frontend Not Loading?
```bash
# Check if backend is accessible
curl http://localhost:8000/api/v1/health

# Check frontend logs
docker-compose logs frontend
```

### API Errors?
```bash
# Check if OpenAI API key is set
cat backend/.env | grep OPENAI_API_KEY

# Should show: OPENAI_API_KEY=sk-...
# If empty, add your API key to backend/.env
```

### No Responses to Queries?
- Make sure you've added content first
- Wait a few seconds for processing to complete
- Check browser console (F12) for errors
- Try simpler queries first

---

## 📋 Complete Test Flow

Run these commands in order:

```bash
# 1. Verify services are up
docker-compose ps

# 2. Check backend health
curl http://localhost:8000/api/v1/health

# 3. Test adding content (replace USER_ID with any UUID)
curl -X POST "http://localhost:8000/api/v1/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Python is a programming language. Machine learning uses Python extensively.",
    "user_id": "test-user-123"
  }'

# Expected response:
# {"status":"processing","source_id":"...","chunk_count":1}

# 4. Wait 3 seconds, then query
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python?",
    "user_id": "test-user-123",
    "max_results": 5
  }'

# Expected: JSON response with answer and sources
```

---

## ✅ Success Indicators

You'll know it's working if:

1. ✅ `docker-compose ps` shows all services "Up"
2. ✅ Backend health check returns `{"status":"healthy"}`
3. ✅ Frontend loads at http://localhost:3000
4. ✅ You can add text content via UI
5. ✅ Queries return answers (even if generic)
6. ✅ Responses stream in real-time (token by token)
7. ✅ Sources are cited in responses

---

## 🎯 Quick Visual Check

Open http://localhost:3000 and verify:

1. **UI Loads**: You see "TwinMind" header and chat interface
2. **Add Content Button Works**: Click it, modal opens
3. **Can Add Text**: Add content, get success message
4. **Chat Works**: Type question, see response

If all 4 work → **System is functional!** ✅

---

## 🐛 Common Issues

| Issue | Quick Fix |
|-------|-----------|
| "Connection refused" | Wait 30-60 seconds after `docker-compose up` |
| "Cannot find module" | Run `cd frontend && npm install` |
| Empty responses | Add content first, wait for processing |
| API errors | Check OpenAI API key in `backend/.env` |
| Port already in use | Stop other services or change ports in `docker-compose.yml` |

---

## 💡 Pro Tip

The easiest way to verify:
1. Open http://localhost:3000
2. Add some text content
3. Ask "What did I just add?"
4. If you get an answer → **It's working!** 🎉

