#!/bin/bash

# TwinMind GCP Deployment Script
set -e

PROJECT_ID="twinmind-take-home"
REGION="us-central1"

echo "🚀 Deploying TwinMind to GCP"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Step 1: Enable Required APIs
echo "📋 Step 1: Enabling required GCP APIs..."
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    storage-component.googleapis.com \
    redis.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    --project=$PROJECT_ID

echo "✅ APIs enabled!"
echo ""

# Step 2: Create Artifact Registry
echo "📋 Step 2: Creating Artifact Registry..."
gcloud artifacts repositories create twinmind-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="TwinMind Docker images" \
    --project=$PROJECT_ID 2>/dev/null || echo "Repository already exists"

echo "✅ Artifact Registry ready!"
echo ""

# Step 3: Configure Docker
echo "📋 Step 3: Configuring Docker for GCP..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

echo "✅ Docker configured!"
echo ""

echo "=========================================="
echo "Next steps:"
echo ""
echo "1. Create Cloud SQL instance:"
echo "   ./scripts/create_sql.sh"
echo ""
echo "2. Create Redis instance:"
echo "   ./scripts/create_redis.sh"
echo ""
echo "3. Create Cloud Storage bucket:"
echo "   ./scripts/create_storage.sh"
echo ""
echo "4. Build and deploy backend:"
echo "   ./scripts/deploy_backend.sh"
echo ""
echo "5. Build and deploy frontend:"
echo "   ./scripts/deploy_frontend.sh"
echo ""
echo "Or run the full deployment:"
echo "   ./deploy_all_gcp.sh"
echo "=========================================="

