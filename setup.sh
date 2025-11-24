#!/bin/bash

echo "🚀 TwinMind Setup Script"
echo "========================"
echo ""

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env file..."
    cat > backend/.env << 'ENVEOF'
OPENAI_API_KEY=sk-YOUR_KEY_HERE
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/twinmind
QDRANT_URL=http://localhost:6333
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=twinmind-storage
ENVEOF
    echo "✅ Created backend/.env"
else
    echo "ℹ️  backend/.env already exists"
fi

# Check if OpenAI key is set
if grep -q "OPENAI_API_KEY=sk-YOUR_KEY_HERE" backend/.env || ! grep -q "OPENAI_API_KEY=sk-" backend/.env; then
    echo ""
    echo "⚠️  ⚠️  ⚠️  IMPORTANT ⚠️  ⚠️  ⚠️"
    echo "You need to add your OpenAI API key to backend/.env"
    echo ""
    echo "1. Edit backend/.env"
    echo "2. Replace 'sk-YOUR_KEY_HERE' with your actual API key"
    echo "3. Get a key at: https://platform.openai.com/api-keys"
    echo ""
    read -p "Press Enter when you've added your API key..."
fi

# Setup frontend .env.local
echo ""
echo "📝 Setting up frontend..."
if [ ! -f frontend/.env.local ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
    echo "✅ Created frontend/.env.local"
else
    echo "ℹ️  frontend/.env.local already exists"
fi

# Start Docker services
echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d

echo ""
echo "⏳ Waiting 30 seconds for services to start..."
sleep 30

# Check services
echo ""
echo "🔍 Checking services..."
docker-compose ps

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 IMPORTANT NEXT STEP:"
echo "1. Open http://localhost:9001 in your browser"
echo "2. Login: minioadmin / minioadmin"
echo "3. Create bucket: twinmind-storage"
echo ""
echo "Then run: ./test_api.sh"
