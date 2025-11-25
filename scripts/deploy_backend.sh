#!/bin/bash

# Deploy backend to Cloud Run

set -e

PROJECT_ID="twinmind-take-home"
REGION="us-central1"
SERVICE_NAME="twinmind-backend"
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/twinmind-repo/backend:latest"

echo "🚀 Deploying backend to Cloud Run..."

# Get connection details
CONNECTION_NAME=$(gcloud sql instances describe twinmind-db --format="value(connectionName)" --project=$PROJECT_ID 2>/dev/null || echo "")
REDIS_HOST=$(gcloud redis instances describe twinmind-redis --region=$REGION --format="value(host)" --project=$PROJECT_ID 2>/dev/null || echo "")

if [ -z "$CONNECTION_NAME" ]; then
    echo "❌ Cloud SQL instance not found. Run ./scripts/create_sql.sh first"
    exit 1
fi

if [ -z "$REDIS_HOST" ]; then
    echo "⚠️  Redis instance not found. Run ./scripts/create_redis.sh first"
    echo "Continuing without Redis..."
    REDIS_URL="redis://localhost:6379/0"
else
    REDIS_URL="redis://${REDIS_HOST}:6379/0"
fi

# Get DB password (you'll need to set this)
DB_PASSWORD="${DB_PASSWORD:-CHANGE_THIS_PASSWORD}"

# Build and push Docker image using Cloud Build
echo "📦 Building Docker image with Cloud Build..."
gcloud builds submit --tag $IMAGE_NAME \
    --project=$PROJECT_ID \
    backend/

echo "✅ Image built and pushed!"

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars="DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@localhost/twinmind?host=/cloudsql/${CONNECTION_NAME}" \
    --set-env-vars="REDIS_URL=${REDIS_URL}" \
    --set-env-vars="QDRANT_URL=\${QDRANT_URL:-https://d4c85a4b-2f42-44e4-8b39-8b94aa574108.europe-west3-0.gcp.cloud.qdrant.io:6333}" \
    --set-env-vars="QDRANT_API_KEY=\${QDRANT_API_KEY:-}" \
    --set-env-vars="OPENAI_API_KEY=\${OPENAI_API_KEY:-}" \
    --set-env-vars="STORAGE_TYPE=s3" \
    --set-env-vars="S3_ENDPOINT_URL=https://storage.googleapis.com" \
    --set-env-vars="S3_BUCKET_NAME=twinmind-storage" \
    --set-env-vars="S3_REGION=us-central1" \
    --set-env-vars="ENVIRONMENT=production" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 600 \
    --max-instances 10 \
    --project=$PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" --project=$PROJECT_ID)

echo ""
echo "✅ Backend deployed!"
echo "🌐 Backend URL: $SERVICE_URL"
echo ""
echo "📋 Next: Update frontend with this URL and deploy frontend"

