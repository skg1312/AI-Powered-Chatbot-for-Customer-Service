#!/usr/bin/env python3
"""
Test the fixed chat history and user registration functionality
"""
import asyncio
import requests
import json
import time

def test_backend_endpoints():
    """Test the backend endpoints to see if they work"""
    
    print("🧪 Testing Backend Endpoints")
    print("="*40)
    
    base_url = "http://localhost:8001"
    
    # Test 1: Debug users endpoint
    print("1. Testing debug users endpoint...")
    try:
        response = requests.get(f"{base_url}/api/debug/users", timeout=5)
        data = response.json()
        print(f"   ✅ Users endpoint works: {data['total_users']} users")
    except Exception as e:
        print(f"   ❌ Users endpoint failed: {str(e)}")
    
    # Test 2: Debug sessions endpoint  
    print("2. Testing debug sessions endpoint...")
    try:
        response = requests.get(f"{base_url}/api/debug/sessions", timeout=5)
        data = response.json()
        print(f"   ✅ Sessions endpoint works: {data['total_sessions']} sessions")
        
        if data['sessions']:
            project_ids = set(s.get('project_id') for s in data['sessions'])
            print(f"   Project IDs in database: {list(project_ids)}")
    except Exception as e:
        print(f"   ❌ Sessions endpoint failed: {str(e)}")
    
    # Test 3: Fixed chat history endpoint
    print("3. Testing fixed chat history endpoint...")
    try:
        response = requests.get(f"{base_url}/api/projects/main/chat-history", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Chat history endpoint works: {data.get('total_sessions', 0)} sessions for 'main'")
        else:
            print(f"   ⚠️  Chat history endpoint returned status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Chat history endpoint failed: {str(e)}")
    
    # Test 4: General chat history endpoint
    print("4. Testing general chat history endpoint...")
    try:
        response = requests.get(f"{base_url}/api/chat/history", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ General chat history works: {data.get('total_sessions', 0)} sessions")
            print(f"   Success: {data.get('success', False)}")
        else:
            print(f"   ⚠️  General chat history returned status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ General chat history failed: {str(e)}")
    
    # Test 5: Test user registration
    print("5. Testing user registration...")
    try:
        test_user = {
            "name": "API Test User",
            "email": f"apitest{int(time.time())}@example.com",
            "password": "testpass123",
            "phone": "+1234567890",
            "age": 25
        }
        
        response = requests.post(
            f"{base_url}/api/users/register", 
            json=test_user,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ User registration works: {data.get('message', 'Success')}")
            print(f"   User ID: {data.get('user_id', 'N/A')}")
        else:
            print(f"   ⚠️  User registration returned status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ User registration failed: {str(e)}")
    
    print("\n🎯 Summary:")
    print("   - If all tests pass, the backend is working correctly")
    print("   - If some fail, check if the backend server is running")
    print("   - Run: python -m uvicorn app.main:app --reload --port 8001")

if __name__ == "__main__":
    test_backend_endpoints()
