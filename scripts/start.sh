#!/bin/bash

# Start script for TruScholar Compass Module

echo "🚀 Starting TruScholar Compass Module..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OPENAI_API_KEY"
    exit 1
fi

# Check if OPENAI_API_KEY is set
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY not set in .env file!"
    echo "Please edit .env and add your OpenAI API key"
    exit 1
fi

# Start services with docker-compose
echo "Starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 5

# Check service health
echo "Checking service health..."
curl -s http://localhost:8000/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ API Gateway is running at http://localhost:8000"
else
    echo "⚠️  API Gateway might still be starting..."
fi

echo ""
echo "📡 Services Status:"
docker-compose ps

echo ""
echo "🎯 Compass Module Ready!"
echo "API Gateway: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"