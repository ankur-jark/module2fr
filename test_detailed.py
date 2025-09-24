#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1/compass"

def test_full_flow():
    print("Testing full journey flow with analysis...")
    
    # 1. Start journey
    start_response = requests.post(f"{BASE_URL}/start", json={
        "user_id": "test_analysis",
        "demographics": {"age": 25, "education_level": "bachelor", "current_status": "working"},
        "preferences": {"question_style": "casual"}
    })
    
    journey_data = start_response.json()
    journey_id = journey_data.get('journey_id')
    print(f"✓ Journey started: {journey_id}")
    
    # 2. Get and submit 3 responses
    for i in range(3):
        print(f"\n--- Question {i+1} ---")
        
        # Get question
        question_response = requests.post(f"{BASE_URL}/journey/{journey_id}/next-question")
        question_data = question_response.json()
        question_id = question_data.get('question_id')
        
        print(f"Question ID: {question_id}")
        
        # Submit response
        response_result = requests.post(
            f"{BASE_URL}/journey/{journey_id}/response",
            json={
                "question_id": question_id,
                "response_text": ["A", "B", "C", "D"][i % 4],  # Vary responses
                "response_time_seconds": 5,
                "skipped": False
            }
        )
        
        if response_result.status_code == 200:
            decision = response_result.json()
            print(f"✓ Response submitted: {decision.get('decision')}")
        else:
            print(f"✗ Response failed: {response_result.status_code}")
            
        # Get updated journey state
        state_response = requests.get(f"{BASE_URL}/journey/{journey_id}")
        if state_response.status_code == 200:
            state = state_response.json()
            
            # Check analysis data
            profile = state.get('current_profile', {})
            confidence = state.get('current_confidence', {})
            
            print(f"\nCurrent Profile:")
            print(f"  Realistic: {profile.get('realistic', 0):.1f}")
            print(f"  Investigative: {profile.get('investigative', 0):.1f}")
            print(f"  Artistic: {profile.get('artistic', 0):.1f}")
            print(f"  Social: {profile.get('social', 0):.1f}")
            print(f"  Enterprising: {profile.get('enterprising', 0):.1f}")
            print(f"  Conventional: {profile.get('conventional', 0):.1f}")
            
            if confidence:
                print(f"\nConfidence:")
                print(f"  Overall: {confidence.get('overall_confidence', 0):.1f}%")
                
            motivators = state.get('identified_motivators', [])
            print(f"\nMotivators identified: {len(motivators)}")
            for m in motivators[:3]:
                print(f"  - {m.get('type')}: {m.get('strength', 0):.1f}")
                
            interests = state.get('identified_interests', [])
            print(f"\nInterests identified: {len(interests)}")
            for i in interests[:3]:
                print(f"  - {i.get('category')}: {i.get('enthusiasm', 0):.1f}")
        
        time.sleep(2)  # Don't overwhelm the API

if __name__ == "__main__":
    test_full_flow()