#!/bin/bash

# Create Cloud Storage bucket for TwinMind

PROJECT_ID="twinmind-take-home"
REGION="us-central1"
BUCKET_NAME="twinmind-storage"

echo "📦 Creating Cloud Storage bucket..."

# Check if bucket exists
if gsutil ls -b gs://$BUCKET_NAME 2>/dev/null; then
    echo "✅ Bucket already exists: gs://$BUCKET_NAME"
else
    # Create bucket
    gsutil mb -p $PROJECT_ID -l $REGION gs://$BUCKET_NAME
    echo "✅ Bucket created: gs://$BUCKET_NAME"
fi

# Get project number for service account
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

echo ""
echo "📋 Next: Set IAM permissions for Cloud Run to access bucket:"
echo "   gsutil iam ch serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com:objectAdmin gs://$BUCKET_NAME"

