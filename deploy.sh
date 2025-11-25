#!/bin/bash

# TwinMind Deployment Script
# This script helps deploy to Railway and Vercel

set -e

echo "🚀 TwinMind Cloud Deployment"
echo "============================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI not found${NC}"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI not authenticated${NC}"
    echo "Running: gh auth login"
    gh auth login
fi

echo -e "${GREEN}✅ GitHub CLI ready${NC}"

# Check if OpenAI key exists
if [ -f backend/.env ] && grep -q "OPENAI_API_KEY=sk-" backend/.env; then
    OPENAI_KEY=$(grep "OPENAI_API_KEY=" backend/.env | cut -d '=' -f2)
    echo -e "${GREEN}✅ OpenAI API key found${NC}"
else
    echo -e "${RED}❌ OpenAI API key not found in backend/.env${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "  DEPLOYMENT SETUP"
echo "=========================================="
echo ""
echo "We'll deploy using:"
echo "  • Railway (Backend + Databases)"
echo "  • Vercel (Frontend)"
echo ""
echo "You'll need to:"
echo "  1. Sign up for Railway (free): https://railway.app/"
echo "  2. Sign up for Vercel (free): https://vercel.com/"
echo "  3. Sign up for Qdrant Cloud (free): https://cloud.qdrant.io/"
echo ""
read -p "Press Enter when you're ready to continue..."
echo ""

# Install Railway CLI
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    curl -fsSL https://railway.app/install.sh | sh
else
    echo -e "${GREEN}✅ Railway CLI already installed${NC}"
fi

# Install Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
else
    echo -e "${GREEN}✅ Vercel CLI already installed${NC}"
fi

echo ""
echo "=========================================="
echo "  DEPLOYMENT STEPS"
echo "=========================================="
echo ""
echo "Follow these steps:"
echo ""
echo "1️⃣  BACKEND (Railway):"
echo "   • I'll open Railway in your browser"
echo "   • Connect your GitHub repo"
echo "   • Add PostgreSQL and Redis databases"
echo "   • Set environment variables"
echo ""
echo "2️⃣  VECTOR DB (Qdrant Cloud):"
echo "   • I'll open Qdrant Cloud in your browser"
echo "   • Create a free cluster"
echo "   • Copy the URL and API key"
echo ""
echo "3️⃣  FRONTEND (Vercel):"
echo "   • I'll deploy via Vercel CLI"
echo ""
read -p "Press Enter to start deployment..."

# Open Railway
echo ""
echo "🌐 Opening Railway..."
open "https://railway.app/new" || xdg-open "https://railway.app/new" || echo "Please visit: https://railway.app/new"

echo ""
echo "✅ Deployment script ready!"
echo ""
echo "Next: Follow the manual steps in the deployment guide or I can help you through each step."
echo ""
echo "For quick deployment, visit:"
echo "  • Railway: https://railway.app/new"
echo "  • Vercel: https://vercel.com/new"
echo "  • Qdrant: https://cloud.qdrant.io/"

