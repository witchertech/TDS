#!/bin/bash

# LLM Code Deployment API Startup Script

echo "🚀 Starting LLM Code Deployment API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please copy .env.example to .env and configure it"
    echo ""
    echo "cp .env.example .env"
    echo ""
    exit 1
fi

# Create logs directory
mkdir -p logs

# Run the application
echo "✅ Starting Flask server..."
echo ""
python app.py
