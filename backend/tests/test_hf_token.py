# Test script to check HuggingFace token validity
import requests
import os
from dotenv import load_dotenv

load_dotenv()

hf_token = os.getenv('HF_TOKEN')
print(f"Token (first 10 chars): {hf_token[:10] if hf_token else 'None'}")

if not hf_token:
    print("❌ No HuggingFace token found")
    exit(1)

headers = {"Authorization": f"Bearer {hf_token}"}

# Test 1: Check authentication
print("\n1. Testing HuggingFace authentication...")
try:
    auth_response = requests.get(
        "https://huggingface.co/api/whoami-v2",
        headers=headers,
        timeout=10
    )
    print(f"Auth status: {auth_response.status_code}")
    if auth_response.status_code == 200:
        print("✅ Token is valid")
        user_info = auth_response.json()
        print(f"User: {user_info.get('name', 'unknown')}")
    else:
        print(f"❌ Auth failed: {auth_response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Auth error: {e}")
    exit(1)

# Test 2: Test embedding API with feature extraction
print("\n2. Testing sentence-transformers embedding model...")
feature_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L12-v2"
try:
    response = requests.post(
        feature_url,
        headers=headers,
        json={"inputs": "test embedding"},
        timeout=15
    )
    print(f"Sentence-transformers status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Sentence-transformers API works")
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            print(f"Embedding dimension: {len(data)}")
        else:
            print(f"Response format: {type(data)}")
    elif response.status_code == 503:
        print("⚠️ Model is loading (503) - this is temporary")
    else:
        print(f"❌ Sentence-transformers failed: {response.text}")
        
except Exception as e:
    print(f"❌ Sentence-transformers error: {e}")

print("\n3. Testing alternative models...")
# Test a simpler model
simple_model_url = "https://api-inference.huggingface.co/models/distilbert-base-uncased"
try:
    response = requests.post(
        simple_model_url,
        headers=headers,
        json={"inputs": "test text"},
        timeout=15
    )
    print(f"DistilBERT status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Alternative model works")
    else:
        print(f"❌ Alternative model failed: {response.text}")
except Exception as e:
    print(f"❌ Alternative model error: {e}")
