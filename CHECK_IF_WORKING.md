# ✅ How to Check if TwinMind is Working

## 🎯 Super Quick Test (2 minutes)

### Option 1: Run Automated Test Script
```bash
./test_api.sh
```

This will:
- ✅ Check if backend is running
- ✅ Add test content
- ✅ Query the knowledge base
- ✅ Show you results

**If script succeeds → System is working!** ✅

---

### Option 2: Manual Browser Test (Easiest!)

**Step 1: Open the app**
```
Open: http://localhost:3000
```
You should see the TwinMind chat interface.

**Step 2: Add content**
1. Click "Add Content" button (top right)
2. Click "Text" tab
3. Type: `I love Python programming`
4. Click "Save Text"
5. ✅ Should see success message

**Step 3: Ask a question**
1. In the chat box, type: `What programming language do I love?`
2. Click Send
3. ✅ Should see streaming response mentioning Python

**If Step 3 works → Everything is working!** 🎉

---

## 🔍 Detailed Verification

### Check 1: Services Running?
```bash
docker-compose ps
```
**Look for**: All services show "Up" (green)

**If not running:**
```bash
docker-compose up -d
# Wait 30 seconds
```

### Check 2: Backend Health?
```bash
curl http://localhost:8000/api/v1/health
```
**Expected output:**
```json
{"status":"healthy","service":"twinmind-api"}
```

**If error:** Backend isn't running or isn't ready yet

### Check 3: Frontend Accessible?
Open: http://localhost:3000

**You should see:**
- TwinMind header
- "Add Content" button
- Chat interface with input box

**If blank page:**
- Check browser console (F12)
- Check: `docker-compose logs frontend`

### Check 4: Can Add Content?
```bash
curl -X POST "http://localhost:8000/api/v1/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test message for verification",
    "user_id": "test-123"
  }'
```

**Expected:**
```json
{"status":"processing","source_id":"...","chunk_count":1}
```

**If error:** Check OpenAI API key in `backend/.env`

### Check 5: Can Query?
Wait 3 seconds after Step 4, then:

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What was the test message?",
    "user_id": "test-123",
    "max_results": 5
  }'
```

**Expected:** JSON with an "answer" field containing text

---

## ✅ Success Checklist

Mark these as you verify:

- [ ] `docker-compose ps` shows all services "Up"
- [ ] Backend health returns `{"status":"healthy"}`
- [ ] Frontend loads at http://localhost:3000
- [ ] Can click "Add Content" button
- [ ] Can add text via UI
- [ ] Can see chat interface
- [ ] Can type and send messages
- [ ] Queries return responses (even if generic)

**If all checked → System is working!** ✅

---

## 🐛 Quick Troubleshooting

### "Connection refused" errors?
```bash
# Services might still be starting
# Wait 30-60 seconds and try again
docker-compose ps
```

### No responses to queries?
1. Make sure you added content first
2. Wait 3-5 seconds for processing
3. Try simpler query: "What is in my knowledge base?"

### API errors about OpenAI?
```bash
# Check if API key is set
cat backend/.env | grep OPENAI_API_KEY

# Should show: OPENAI_API_KEY=sk-...
# If not, add your key to backend/.env
```

### Frontend can't connect to backend?
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Check frontend environment
cat frontend/.env.local

# Should show: NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🎬 Visual Verification Guide

### What You Should See:

**1. Terminal (Services Running):**
```
NAME          STATUS
postgres      Up
qdrant        Up  
minio         Up
backend       Up
frontend      Up
```

**2. Browser (Frontend):**
```
┌─────────────────────────────────┐
│  TwinMind    [Add Content]      │
│  Your Second Brain AI Companion  │
├─────────────────────────────────┤
│                                 │
│  [Chat messages appear here]    │
│                                 │
├─────────────────────────────────┤
│  [Ask a question...]  [Send]   │
└─────────────────────────────────┘
```

**3. Backend Response (Health Check):**
```json
{
  "status": "healthy",
  "service": "twinmind-api"
}
```

**4. Query Response:**
```json
{
  "answer": "Based on your knowledge base...",
  "sources": [...],
  "query_metadata": {...}
}
```

---

## 💡 The Easiest Test

**Just do this:**

1. Open http://localhost:3000
2. Click "Add Content"
3. Add text: "My favorite color is blue"
4. Wait 3 seconds
5. Ask: "What is my favorite color?"
6. Get answer mentioning "blue"

**✅ If Step 6 works → System is fully functional!**

---

## 📞 Still Not Working?

Run the full verification script:
```bash
./verify_working.sh
```

This will check everything and tell you what's wrong.

Or check logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

Look for error messages in the output.

---

**Remember**: The simplest test is adding content via the UI and then asking about it. If that works, everything is working! 🎉

