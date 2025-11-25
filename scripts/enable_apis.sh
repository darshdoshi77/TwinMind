#!/bin/bash

# Enable all required GCP APIs for TwinMind

PROJECT_ID="twinmind-take-home"

echo "Enabling GCP APIs for TwinMind..."

gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    storage-component.googleapis.com \
    redis.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    --project=$PROJECT_ID

echo "✅ All APIs enabled!"

