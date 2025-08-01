#!/usr/bin/env python3
"""
Test Supabase connection and table creation
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_supabase_connection():
    """Test Supabase connection and table structure"""
    print("🔗 Testing Supabase connection...")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"URL: {url}")
    print(f"Key: {key[:20]}..." if key else "Key: None")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    try:
        client = create_client(url, key)
        print("✅ Client created successfully")
        
        # Test if users table exists
        try:
            result = client.table('users').select('count', count='exact').execute()
            print(f"✅ Users table exists with {result.count} records")
        except Exception as e:
            print(f"❌ Users table error: {str(e)}")
            return False
        
        # Test creating a user to see the exact error
        test_user = {
            "user_id": "test-user-123",
            "name": "Test User",
            "email": "test@example.com",
            "password_hash": "test_hash",
            "phone": "+1234567890",
            "age": 25,
            "medical_conditions": "None",
            "emergency_contact": "Test Contact",
            "created_at": "2024-01-01T00:00:00Z",
            "last_active": "2024-01-01T00:00:00Z",
            "total_sessions": 0
        }
        
        print("🧪 Testing user creation...")
        try:
            result = client.table('users').insert(test_user).execute()
            print(f"✅ User created successfully: {result.data}")
            
            # Try to fetch the user back
            fetch_result = client.table('users').select('*').eq('user_id', 'test-user-123').execute()
            print(f"✅ User fetched: {fetch_result.data}")
            
            # Clean up - delete the test user
            delete_result = client.table('users').delete().eq('user_id', 'test-user-123').execute()
            print(f"✅ Test user deleted")
            
        except Exception as e:
            print(f"❌ User creation error: {str(e)}")
            print(f"Error type: {type(e)}")
            if hasattr(e, 'details'):
                print(f"Details: {e.details}")
            if hasattr(e, 'message'):
                print(f"Message: {e.message}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    test_supabase_connection()
