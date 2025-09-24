#!/bin/bash

# Development start script - runs services locally without Docker

echo "🚀 Starting TruScholar Compass Module (Development Mode)..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OPENAI_API_KEY"
    exit 1
fi

# Load environment variables
source .env

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY not set in .env file!"
    exit 1
fi

# Check if Redis is running
redis-cli ping > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

echo "✅ Redis is running"

# Install dependencies if needed
echo "Checking Python dependencies..."

# Function to start a service in background
start_service() {
    local service_name=$1
    local service_dir=$2
    local port=$3
    
    echo "Starting $service_name on port $port..."
    cd services/$service_dir
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment for $service_name..."
        python3 -m venv venv
    fi
    
    # Activate venv and install dependencies
    source venv/bin/activate
    pip install -q -r requirements.txt
    
    # Start the service
    nohup uvicorn main:app --reload --port $port > ../../logs/${service_name}.log 2>&1 &
    echo $! > ../../logs/${service_name}.pid
    
    cd ../..
    sleep 2
}

# Create logs directory
mkdir -p logs

# Start services
start_service "compass-service" "compass-service" 8001
start_service "user-profile-service" "user-profile-service" 8002
start_service "api-gateway" "api-gateway" 8000

echo ""
echo "✅ All services started!"
echo ""
echo "📡 Services:"
echo "  API Gateway: http://localhost:8000"
echo "  Compass Service: http://localhost:8001"
echo "  Profile Service: http://localhost:8002"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "📝 Logs are in ./logs/"
echo ""
echo "To stop all services: ./stop-dev.sh"