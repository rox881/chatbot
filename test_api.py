"""
Test Flask API using Python requests
"""

import requests
import json

print("=" * 70)
print("FLASK API TEST")
print("=" * 70)

base_url = "http://127.0.0.1:5000"

# Test 1: Health check
print("\n[Test 1] Health Check")
try:
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Chat endpoint
print("\n[Test 2] Chat Endpoint - Weight Loss Request")
try:
    payload = {
        "message": "I want to lose weight",
        "user_id": "api_test_user_001"
    }
    response = requests.post(
        f"{base_url}/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if result['status'] == 'success':
        print(f"Intent: {result['intent']}")
        print(f"Week: {result['user_state']['week']}")
        print(f"Target Calories: {result['roadmap']['target_calories']}")
        print(f"\nResponse Preview:")
        print(result['response'][:200] + "...")
    else:
        print(f"Error: {result.get('error', 'Unknown')}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Get user profile
print("\n[Test 3] Get User Profile")
try:
    response = requests.get(f"{base_url}/user/api_test_user_001")
    print(f"Status: {response.status_code}")
    result = response.json()
    if result['status'] == 'success':
        user = result['user']
        print(f"Week: {user['week']}, Goal: {user['fitness_goal']}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("API TESTS COMPLETE")
print("=" * 70)
