#!/bin/bash

# Script to help push TwinMind code to GitHub

echo "🚀 TwinMind - Push to GitHub"
echo "============================"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "❌ Not a git repository. Please run ./setup_git.sh first."
    exit 1
fi

# Check current status
echo "📋 Current Git Status:"
git status --short
echo ""

# Check if remote exists
if git remote get-url origin &> /dev/null; then
    echo "✅ Remote 'origin' already configured:"
    git remote -v
    echo ""
    read -p "Do you want to push to existing remote? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Pushing to GitHub..."
        git push -u origin main
        echo ""
        echo "✅ Done! Your code is on GitHub."
        exit 0
    fi
fi

echo "📝 You need to create a GitHub repository first."
echo ""
echo "Step 1: Create repository on GitHub"
echo "   👉 Go to: https://github.com/new"
echo "   📦 Repository name: TwinMind"
echo "   📝 Description: Second Brain AI Companion - Full-stack AI system"
echo "   ⚠️  DO NOT initialize with README, .gitignore, or license"
echo ""
read -p "Press Enter after you've created the repository on GitHub..."
echo ""

# Get GitHub username and repo name
echo "Enter your GitHub details:"
read -p "GitHub username: " GITHUB_USERNAME
read -p "Repository name (default: TwinMind): " REPO_NAME
REPO_NAME=${REPO_NAME:-TwinMind}

# Remove existing origin if it exists
if git remote get-url origin &> /dev/null; then
    echo "⚠️  Removing existing remote..."
    git remote remove origin
fi

# Add new remote
echo "🔗 Adding remote repository..."
GITHUB_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
git remote add origin "$GITHUB_URL"

echo ""
echo "📤 Pushing code to GitHub..."
echo "   Remote: $GITHUB_URL"
echo ""

# Push
if git push -u origin main; then
    echo ""
    echo "✅ Success! Your code is now on GitHub!"
    echo ""
    echo "🌐 Repository URL: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Add repository topics: ai, llm, vector-database, fastapi, nextjs"
    echo "   2. Add a repository description"
    echo "   3. Share the URL as part of your deliverables!"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "   1. Authentication required - you may need a Personal Access Token"
    echo "   2. Repository doesn't exist or wrong URL"
    echo "   3. Permission denied"
    echo ""
    echo "💡 See PUSH_TO_GITHUB.md for troubleshooting"
    exit 1
fi

