# 🚀 Deploy TwinMind to Cloud - Quick Start

Follow these steps to deploy your app. This will take about 15-20 minutes.

---

## 📋 Prerequisites Checklist

Before starting, you'll need:
- [ ] GitHub account (already have ✅)
- [ ] OpenAI API key (you should have this)
- [ ] Railway account (we'll create)
- [ ] Vercel account (we'll create)
- [ ] Qdrant Cloud account (we'll create)
- [ ] AWS account for S3 (or we can use Railway storage)

---

## Step 1: Set Up Qdrant Cloud (Vector Database) - 5 min

1. **Go to**: https://cloud.qdrant.io/
2. **Sign up** (free tier available - 1GB free)
3. **Create a Cluster**:
   - Choose a region close to you
   - Select the free tier
   - Name it: `twinmind-cluster`
4. **Get your credentials**:
   - Click on your cluster
   - Copy the **URL** (looks like: `https://xxx.qdrant.io`)
   - Copy the **API Key** (click "Generate API Key" if needed)
5. **Save these** - you'll need them in Step 3

✅ **Done!** You have: `QDRANT_URL` and `QDRANT_API_KEY`

---

## Step 2: Set Up AWS S3 (File Storage) - 5 min

### Option A: AWS S3 (Recommended)

1. **Go to**: https://aws.amazon.com/s3/
2. **Sign in** to AWS Console
3. **Create S3 Bucket**:
   - Click "Create bucket"
   - Bucket name: `twinmind-storage` (must be globally unique, add your name)
   - Region: `us-east-1` (or your preferred)
   - **Uncheck** "Block all public access" (we'll set permissions)
   - Click "Create bucket"
4. **Create IAM User for S3 Access**:
   - Go to IAM → Users → Add user
   - Username: `twinmind-s3-user`
   - Access type: Programmatic access
   - Permissions: Attach policy `AmazonS3FullAccess` (or create custom policy)
   - Click "Create user"
   - **IMPORTANT**: Copy the **Access Key ID** and **Secret Access Key** (you can only see this once!)

✅ **Done!** You have: `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET_NAME`, `S3_REGION`

### Option B: Skip S3 for Now (Use Local Storage)

You can use local storage on Railway, but files won't persist across restarts. We'll use S3 for production.

---

## Step 3: Deploy Backend to Railway - 10 min

1. **Go to**: https://railway.app/
2. **Sign up** using GitHub (click "Start a New Project")
3. **New Project** → **Deploy from GitHub repo**
4. **Select** your `TwinMind` repository
5. **Add PostgreSQL Database**:
   - Click "+ New" → "Database" → "Add PostgreSQL"
   - Railway will auto-create the database
   - Copy the `DATABASE_URL` (or Railway will auto-inject it)
6. **Add Redis**:
   - Click "+ New" → "Database" → "Add Redis"
   - Copy the `REDIS_URL` (or Railway will auto-inject it)
7. **Configure Backend Service**:
   - Railway should detect your Dockerfile
   - If not, go to service settings:
     - **Root Directory**: `backend`
     - **Build Command**: (auto from Dockerfile)
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
8. **Add Environment Variables**:
   Click on your backend service → "Variables" tab → Add these:

   ```bash
   # Qdrant (from Step 1)
   QDRANT_URL=https://xxx.qdrant.io
   QDRANT_API_KEY=your_qdrant_api_key

   # OpenAI
   OPENAI_API_KEY=sk-your-openai-key

   # Storage (from Step 2)
   STORAGE_TYPE=s3
   S3_ENDPOINT_URL=https://s3.amazonaws.com
   S3_ACCESS_KEY=your_aws_access_key
   S3_SECRET_KEY=your_aws_secret_key
   S3_BUCKET_NAME=twinmind-storage
   S3_REGION=us-east-1

   # Application
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
   SECRET_KEY=generate-a-random-secret-key-here
   ```

   **Note**: Railway automatically provides `DATABASE_URL` and `REDIS_URL` - you don't need to add them manually!

9. **Deploy**:
   - Railway will automatically deploy when you push to GitHub
   - Or click "Deploy" button
   - Wait for build to complete (2-3 minutes)

10. **Get Your Backend URL**:
    - Click on your service → "Settings" → "Generate Domain"
    - Copy the URL (e.g., `https://twinmind-production.railway.app`)
    - Or use the default domain

✅ **Done!** Your backend is live at: `https://your-backend.railway.app`

---

## Step 4: Deploy Frontend to Vercel - 5 min

1. **Go to**: https://vercel.com/
2. **Sign up** using GitHub
3. **New Project** → **Import** your GitHub repository
4. **Select** `TwinMind` repository
5. **Configure Project**:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto)
   - **Output Directory**: `.next` (auto)
   - **Install Command**: `npm install` (auto)

6. **Add Environment Variable**:
   - Click "Environment Variables"
   - Add:
     ```
     Name: NEXT_PUBLIC_API_URL
     Value: https://your-backend.railway.app
     ```
   (Use your Railway backend URL from Step 3)

7. **Deploy**:
   - Click "Deploy"
   - Wait for build (1-2 minutes)

8. **Get Your Frontend URL**:
   - Vercel will give you a URL like: `https://twinmind.vercel.app`
   - Copy this URL

✅ **Done!** Your frontend is live at: `https://your-frontend.vercel.app`

---

## Step 5: Update CORS Settings - 2 min

1. Go back to **Railway** → Your backend service → Variables
2. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.vercel.app
   ```
3. Railway will auto-redeploy

---

## Step 6: Test Your Deployment! 🎉

1. **Visit your frontend**: `https://your-frontend.vercel.app`
2. **Test features**:
   - Upload a file
   - Add text
   - Add web URL
   - Ask a question

---

## 🎯 Your Live URLs

- **Frontend**: `https://your-frontend.vercel.app`
- **Backend**: `https://your-backend.railway.app`
- **API Docs**: `https://your-backend.railway.app/docs`

---

## 🐛 Troubleshooting

### Backend Not Working?
- Check Railway logs: Service → "Deployments" → Click latest deployment → "View Logs"
- Verify all environment variables are set
- Check if database connection is working

### Frontend Can't Connect to Backend?
- Verify `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Check CORS settings in Railway (`ALLOWED_ORIGINS`)
- Open browser console to see errors

### File Upload Issues?
- Verify S3 credentials are correct
- Check S3 bucket permissions
- Verify bucket name is correct

### Database Errors?
- Check Railway PostgreSQL service is running
- Verify `DATABASE_URL` is automatically set by Railway
- Check connection in Railway logs

---

## 💡 Pro Tips

1. **Custom Domain**: You can add custom domains in Railway/Vercel settings
2. **Environment Variables**: Use Railway/Vercel's environment variable UI (easier than .env files)
3. **Monitoring**: Railway and Vercel provide basic monitoring and logs
4. **Automatic Deploys**: Both platforms auto-deploy on git push to main branch

---

## ✅ Next Steps

After deployment:
1. Test all features thoroughly
2. Add your deployment URL to deliverables
3. Update README.md with deployment info
4. Consider adding custom domain (optional)

**You're live! 🚀**

