#!/bin/bash

# TwinMind System Verification Script
# This script checks if all components are working correctly

echo "🔍 TwinMind System Verification"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker-compose is running
echo "1️⃣  Checking Docker services..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓${NC} Docker services are running"
    docker-compose ps
else
    echo -e "${RED}✗${NC} Docker services are not running"
    echo "   Run: docker-compose up -d"
    exit 1
fi
echo ""

# Check backend health
echo "2️⃣  Checking Backend API..."
BACKEND_RESPONSE=$(curl -s http://localhost:8000/api/v1/health)
if echo "$BACKEND_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} Backend is healthy"
    echo "   Response: $BACKEND_RESPONSE"
else
    echo -e "${RED}✗${NC} Backend is not responding"
    echo "   Check: http://localhost:8000/api/v1/health"
    echo "   Run: docker-compose logs backend"
fi
echo ""

# Check frontend
echo "3️⃣  Checking Frontend..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓${NC} Frontend is accessible"
    echo "   URL: http://localhost:3000"
else
    echo -e "${RED}✗${NC} Frontend is not responding (HTTP $FRONTEND_RESPONSE)"
    echo "   Check: http://localhost:3000"
fi
echo ""

# Check PostgreSQL
echo "4️⃣  Checking PostgreSQL..."
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} PostgreSQL is ready"
else
    echo -e "${RED}✗${NC} PostgreSQL is not ready"
fi
echo ""

# Check Qdrant
echo "5️⃣  Checking Qdrant (Vector DB)..."
QDRANT_RESPONSE=$(curl -s http://localhost:6333/health)
if echo "$QDRANT_RESPONSE" | grep -q "ok"; then
    echo -e "${GREEN}✓${NC} Qdrant is healthy"
else
    echo -e "${YELLOW}⚠${NC}  Qdrant health check unclear"
    echo "   Response: $QDRANT_RESPONSE"
fi
echo ""

# Check MinIO
echo "6️⃣  Checking MinIO..."
MINIO_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/minio/health/live)
if [ "$MINIO_RESPONSE" == "200" ] || [ "$MINIO_RESPONSE" == "503" ]; then
    echo -e "${GREEN}✓${NC} MinIO is accessible"
    echo "   Console: http://localhost:9001"
    echo -e "${YELLOW}⚠${NC}  Make sure bucket 'twinmind-storage' exists"
else
    echo -e "${RED}✗${NC} MinIO is not responding (HTTP $MINIO_RESPONSE)"
fi
echo ""

# Test API endpoint
echo "7️⃣  Testing API endpoint..."
TEST_USER_ID="test-$(date +%s)"
API_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/ingest/text" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"This is a test message for verification.\", \"user_id\": \"$TEST_USER_ID\"}")

if echo "$API_RESPONSE" | grep -q "source_id"; then
    echo -e "${GREEN}✓${NC} API ingestion is working"
    echo "   Test user ID: $TEST_USER_ID"
    echo "   Response: $API_RESPONSE"
else
    echo -e "${RED}✗${NC} API ingestion failed"
    echo "   Response: $API_RESPONSE"
    echo -e "${YELLOW}⚠${NC}  This might be expected if OpenAI API key is missing"
fi
echo ""

# Summary
echo "================================"
echo "📊 Verification Summary"
echo "================================"
echo ""
echo "✅ All critical services should be running"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Click 'Add Content' and add some text"
echo "3. Wait a few seconds for processing"
echo "4. Ask a question in the chat interface"
echo ""
echo "For detailed testing, see TESTING_GUIDE.md"

