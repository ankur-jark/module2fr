#!/bin/bash
echo "Starting TruScholar services..."

# Kill any existing services
pkill -f "uvicorn\|main.py" 2>/dev/null
sleep 2

# Load environment
source .env

# Start services
echo "Starting Compass Service..."
cd services/compass-service && OPENAI_API_KEY=$OPENAI_API_KEY python3 main.py > /tmp/compass.log 2>&1 &
cd ../..
sleep 2

echo "Starting Profile Service..."
cd services/user-profile-service && python3 main.py > /tmp/profile.log 2>&1 &
cd ../..
sleep 2

echo "Starting API Gateway..."
cd services/api-gateway && python3 main.py > /tmp/gateway.log 2>&1 &
cd ../..
sleep 2

echo "Services started!"
echo "API Gateway: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"