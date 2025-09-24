#!/usr/bin/env python3
"""Test script to verify all services are working"""

import asyncio
import httpx
import json
import sys
from datetime import datetime

async def test_services():
    async with httpx.AsyncClient() as client:
        base_url = "http://localhost:8000"
        
        # Test 1: Health check
        print("1. Testing API Gateway health...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ API Gateway is healthy")
            else:
                print(f"❌ API Gateway health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Cannot connect to API Gateway: {e}")
            print("Please ensure services are running: ./start-dev.sh")
            return False
        
        # Test 2: Start Compass journey
        print("\n2. Testing Compass journey start...")
        journey_data = {
            "user_id": f"test_user_{datetime.now().timestamp()}",
            "demographics": {
                "age": 25,
                "education_level": "bachelor",
                "current_status": "working"
            },
            "preferences": {
                "language": "en",
                "question_style": "casual"
            }
        }
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/compass/start",
                json=journey_data
            )
            if response.status_code == 200:
                journey = response.json()
                journey_id = journey.get("journey_id")
                print(f"✅ Journey started: {journey_id}")
                
                # Test 3: Get journey status
                print("\n3. Testing journey status retrieval...")
                response = await client.get(f"{base_url}/api/v1/compass/journey/{journey_id}")
                if response.status_code == 200:
                    print("✅ Journey status retrieved successfully")
                    status = response.json()
                    print(f"   Status: {status.get('status')}")
                    print(f"   Questions asked: {status.get('current_question_number', 0)}")
                else:
                    print(f"❌ Failed to get journey status: {response.status_code}")
                
                # Test 4: Submit a response
                print("\n4. Testing response submission...")
                # First get the first question
                response = await client.post(
                    f"{base_url}/api/v1/compass/journey/{journey_id}/next-question"
                )
                if response.status_code == 200:
                    question = response.json()
                    question_id = question.get("question_id")
                    print(f"✅ Got question: {question.get('question_text', '')[:100]}...")
                    
                    # Submit response
                    response_data = {
                        "question_id": question_id,
                        "response_text": "I enjoy solving complex technical problems and building software solutions.",
                        "response_time_seconds": 30
                    }
                    
                    response = await client.post(
                        f"{base_url}/api/v1/compass/journey/{journey_id}/respond",
                        json=response_data
                    )
                    if response.status_code == 200:
                        decision = response.json()
                        print("✅ Response submitted successfully")
                        print(f"   Decision: {decision.get('decision')}")
                        print(f"   Confidence: {decision.get('confidence_score', {}).get('overall_confidence', 0):.1f}%")
                    else:
                        print(f"❌ Failed to submit response: {response.status_code}")
                        print(f"   Error: {response.text}")
                else:
                    print(f"❌ Failed to get question: {response.status_code}")
                    
            else:
                print(f"❌ Failed to start journey: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing Compass service: {e}")
            return False
        
        # Test 5: Check all services health
        print("\n5. Testing all services health...")
        try:
            response = await client.post(f"{base_url}/api/v1/admin/services/health")
            if response.status_code == 200:
                services = response.json()
                print("✅ Services health check:")
                for service, health in services.items():
                    status = health.get("status", "unknown")
                    emoji = "✅" if status == "healthy" else "❌"
                    print(f"   {emoji} {service}: {status}")
            else:
                print(f"❌ Failed to check services health: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking services health: {e}")
        
        print("\n" + "="*50)
        print("✅ All tests completed successfully!")
        return True

if __name__ == "__main__":
    success = asyncio.run(test_services())
    sys.exit(0 if success else 1)