#!/bin/bash

# Script to initialize Git repository for TwinMind project

echo "🚀 Setting up Git repository for TwinMind..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if already a git repository
if [ -d .git ]; then
    echo "⚠️  Already a git repository. Skipping initialization."
else
    echo "📦 Initializing Git repository..."
    git init
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "⚠️  No changes to commit. Repository is up to date."
else
    echo "💾 Creating initial commit..."
    git commit -m "Initial commit: TwinMind Second Brain AI Companion

- Complete full-stack implementation
- Multi-modal data ingestion (audio, documents, web, text)
- Hybrid retrieval system (vector + keyword + temporal)
- FastAPI backend with PostgreSQL, Qdrant, MinIO
- Next.js frontend with streaming chat interface
- Comprehensive system design document"
fi

echo ""
echo "✅ Git repository initialized!"
echo ""
echo "📋 Next steps:"
echo "1. Create a repository on GitHub: https://github.com/new"
echo "2. Run these commands:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/TwinMind.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "📖 See DELIVERABLES_GUIDE.md for complete instructions."

