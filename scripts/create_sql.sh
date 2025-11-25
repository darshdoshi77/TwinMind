#!/bin/bash

# Create Cloud SQL PostgreSQL instance

PROJECT_ID="twinmind-take-home"
REGION="us-central1"
INSTANCE_NAME="twinmind-db"
DB_NAME="twinmind"
DB_PASSWORD="${DB_PASSWORD:-CHANGE_THIS_PASSWORD}"

echo "🗄️  Creating Cloud SQL PostgreSQL instance..."

# Check if instance exists
if gcloud sql instances describe $INSTANCE_NAME --project=$PROJECT_ID 2>/dev/null; then
    echo "✅ Instance already exists: $INSTANCE_NAME"
else
    echo "Creating instance (this may take 5-10 minutes)..."
    gcloud sql instances create $INSTANCE_NAME \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=$REGION \
        --root-password=$DB_PASSWORD \
        --project=$PROJECT_ID
    
    echo "✅ Instance created!"
fi

# Create database
echo "Creating database..."
gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME --project=$PROJECT_ID 2>/dev/null || \
    echo "Database already exists"

# Get connection name
CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)" --project=$PROJECT_ID)

echo ""
echo "✅ Setup complete!"
echo "📋 Connection name: $CONNECTION_NAME"
echo "📋 Use this for DATABASE_URL in Cloud Run"

