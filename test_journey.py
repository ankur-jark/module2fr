#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1/compass"

def test_journey():
    print("Starting journey test...")
    
    # 1. Start a journey
    start_response = requests.post(f"{BASE_URL}/start", json={
        "user_id": "test_user",
        "demographics": {
            "age": 25,
            "education_level": "bachelor",
            "current_status": "working"
        },
        "preferences": {
            "question_style": "casual"
        }
    })
    
    if start_response.status_code != 200:
        print(f"Failed to start journey: {start_response.text}")
        return
    
    journey_data = start_response.json()
    journey_id = journey_data.get('journey_id')
    print(f"✓ Journey started: {journey_id}")
    
    # 2. Get first question
    question_response = requests.post(f"{BASE_URL}/journey/{journey_id}/next-question")
    
    if question_response.status_code != 200:
        print(f"Failed to get question: {question_response.text}")
        return
    
    question_data = question_response.json()
    question_id = question_data.get('question_id')
    has_options = 'options' in question_data and len(question_data['options']) > 0
    
    print(f"✓ Got question {question_id}")
    print(f"  - Has options metadata: {has_options}")
    
    if has_options:
        option = question_data['options'][0]
        print(f"  - First option has RIASEC: {'riasec_weights' in option}")
        print(f"  - First option has motivators: {'motivators' in option}")
    
    # 3. Submit response
    print("\nSubmitting response...")
    response_result = requests.post(
        f"{BASE_URL}/journey/{journey_id}/response",
        json={
            "question_id": question_id,
            "response_text": "A",
            "response_time_seconds": 5,
            "skipped": False
        }
    )
    
    print(f"Response status: {response_result.status_code}")
    
    if response_result.status_code == 200:
        decision = response_result.json()
        print(f"✓ Response accepted")
        print(f"  - Decision: {decision.get('decision', 'N/A')}")
        print(f"  - Reasoning: {decision.get('reasoning', 'N/A')[:100]}...")
    else:
        print(f"✗ Response failed: {response_result.text[:200]}")
    
    # 4. Check journey state
    state_response = requests.get(f"{BASE_URL}/journey/{journey_id}")
    if state_response.status_code == 200:
        state = state_response.json()
        print(f"\n✓ Journey state:")
        print(f"  - Questions asked: {len(state.get('questions_asked', []))}")
        print(f"  - Responses: {len(state.get('responses', []))}")
        print(f"  - Status: {state.get('status')}")
    else:
        print(f"✗ Failed to get journey state")

if __name__ == "__main__":
    test_journey()