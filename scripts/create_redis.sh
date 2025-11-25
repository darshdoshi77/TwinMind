#!/bin/bash

# Create Memorystore Redis instance

PROJECT_ID="twinmind-take-home"
REGION="us-central1"
INSTANCE_NAME="twinmind-redis"

echo "🔴 Creating Redis instance (this may take 10-15 minutes)..."

# Check if instance exists
if gcloud redis instances describe $INSTANCE_NAME --region=$REGION --project=$PROJECT_ID 2>/dev/null; then
    echo "✅ Instance already exists: $INSTANCE_NAME"
else
    gcloud redis instances create $INSTANCE_NAME \
        --size=1 \
        --region=$REGION \
        --redis-version=redis_7_0 \
        --project=$PROJECT_ID
    
    echo "✅ Instance created!"
fi

# Get Redis host
REDIS_HOST=$(gcloud redis instances describe $INSTANCE_NAME --region=$REGION --format="value(host)" --project=$PROJECT_ID)

echo ""
echo "✅ Setup complete!"
echo "📋 Redis host: $REDIS_HOST"
echo "📋 Use this for REDIS_URL in Cloud Run (format: redis://$REDIS_HOST:6379/0)"

