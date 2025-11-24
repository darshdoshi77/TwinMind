# ✅ Simple Setup Guide - 3 Steps

## Step 1: Create MinIO Bucket (2 minutes)

1. **Open browser:** http://localhost:9001

2. **Login:**
   - Username: `minioadmin`
   - Password: `minioadmin`

3. **Create bucket:**
   - Click **"Create Bucket"** or **"+"** button
   - Name: `twinmind-storage`
   - Click **"Create"**

✅ Done!

---

## Step 2: Start Frontend (if not running)

In terminal:
```bash
cd /Users/darshdoshi/Documents/TwinMind
docker-compose up -d frontend
```

Wait 30 seconds, then open: http://localhost:3000

---

## Step 3: Test It!

1. **Open:** http://localhost:3000

2. **Add content:**
   - Click "Add Content"
   - Type: `I love Python`
   - Save

3. **Ask question:**
   - Type: `What do I love?`
   - Get answer!

✅ If it works → You're done! 🎉

---

## Quick Commands Reference

```bash
# Check all services
docker-compose ps

# Start frontend if missing
docker-compose up -d frontend

# Check backend health
curl http://localhost:8000/api/v1/health

# View logs if something breaks
docker-compose logs backend
docker-compose logs frontend
```

