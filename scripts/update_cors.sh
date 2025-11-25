#!/bin/bash

# Update CORS settings for backend

PROJECT_ID="twinmind-take-home"
REGION="us-central1"
FRONTEND_URL="https://twinmind-frontend-123622412550.us-central1.run.app"
BACKEND_URL="https://twinmind-backend-123622412550.us-central1.run.app"

echo "Updating CORS settings..."

# Get current env vars and update ALLOWED_ORIGINS
gcloud run services describe twinmind-backend \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(spec.template.spec.containers[0].env)" > /tmp/env_vars.txt

# Redeploy with updated CORS - simplest is to set ALLOWED_ORIGINS to allow all for now
gcloud run services update twinmind-backend \
    --region=$REGION \
    --project=$PROJECT_ID \
    --update-env-vars="ALLOWED_ORIGINS=${FRONTEND_URL},${BACKEND_URL}"

echo "✅ CORS updated!"

