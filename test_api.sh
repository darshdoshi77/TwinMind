#!/bin/bash

# Simple API test script - Test if TwinMind API is working

echo "🧪 Testing TwinMind API"
echo "========================"
echo ""

# Generate a test user ID
USER_ID="test-user-$(date +%s)"

echo "Using test user ID: $USER_ID"
echo ""

# Test 1: Health Check
echo "1. Testing health endpoint..."
HEALTH=$(curl -s http://localhost:8000/api/v1/health)
echo "   Response: $HEALTH"
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Backend is healthy"
else
    echo "   ❌ Backend is not healthy"
    exit 1
fi
echo ""

# Test 2: Add Text Content
echo "2. Testing text ingestion..."
INGEST_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/ingest/text" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"Machine learning is a subset of artificial intelligence. It enables computers to learn from data without being explicitly programmed.\",
    \"user_id\": \"$USER_ID\"
  }")

echo "   Response: $INGEST_RESPONSE"
if echo "$INGEST_RESPONSE" | grep -q "source_id"; then
    SOURCE_ID=$(echo "$INGEST_RESPONSE" | grep -o '"source_id":"[^"]*"' | cut -d'"' -f4)
    echo "   ✅ Content ingested successfully"
    echo "   Source ID: $SOURCE_ID"
else
    echo "   ❌ Failed to ingest content"
    echo "   Make sure OpenAI API key is set in backend/.env"
    exit 1
fi
echo ""

# Wait for processing
echo "3. Waiting 5 seconds for processing..."
sleep 5
echo ""

# Test 3: Query
echo "4. Testing query..."
QUERY_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"What is machine learning?\",
    \"user_id\": \"$USER_ID\",
    \"max_results\": 5
  }")

echo "   Response preview:"
echo "$QUERY_RESPONSE" | head -c 500
echo "..."
echo ""

if echo "$QUERY_RESPONSE" | grep -q "answer"; then
    echo "   ✅ Query successful!"
    echo ""
    echo "   Full answer:"
    echo "$QUERY_RESPONSE" | grep -o '"answer":"[^"]*"' | cut -d'"' -f4
else
    echo "   ⚠️  Query returned, but format unexpected"
    echo "   This might still work - check the full response above"
fi
echo ""

# Test 4: List Sources
echo "5. Testing sources list..."
SOURCES=$(curl -s "http://localhost:8000/api/v1/sources?user_id=$USER_ID")
echo "   Sources: $SOURCES"
if echo "$SOURCES" | grep -q "$SOURCE_ID"; then
    echo "   ✅ Sources endpoint working"
else
    echo "   ⚠️  Source not found yet (might still be processing)"
fi
echo ""

echo "========================"
echo "✅ API Testing Complete!"
echo "========================"
echo ""
echo "If all tests passed, TwinMind is working correctly!"
echo ""
echo "Next: Try the web UI at http://localhost:3000"

