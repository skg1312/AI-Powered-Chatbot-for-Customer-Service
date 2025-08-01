#!/usr/bin/env python3
"""
Test user registration directly
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.supabase_db import SupabaseDB
from app.main import create_user_db, get_user_by_id_db, get_all_users_db
import uuid

async def test_user_registration():
    """Test user registration functionality"""
    print("🧪 Testing user registration...")
    
    # Test data
    test_user_data = {
        "user_id": str(uuid.uuid4()),
        "name": "Test User",
        "email": f"test_{uuid.uuid4()}@example.com",
        "password_hash": "test_hash_123",
        "phone": "+1234567890",
        "age": 25,
        "medical_conditions": "None",
        "emergency_contact": "Emergency Contact"
    }
    
    print(f"📝 Creating user: {test_user_data['email']}")
    
    try:
        # Test create user
        user_id = await create_user_db(test_user_data)
        print(f"✅ User created with ID: {user_id}")
        
        # Test get user by ID
        retrieved_user = await get_user_by_id_db(user_id)
        if retrieved_user:
            print(f"✅ User retrieved successfully: {retrieved_user['email']}")
        else:
            print("❌ Failed to retrieve user by ID")
            
        # Test get all users
        all_users = await get_all_users_db()
        print(f"📊 Total users in database: {all_users['total_users']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during registration test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_connection():
    """Test basic database connection"""
    print("🔗 Testing database connection...")
    
    try:
        db = SupabaseDB()
        print("✅ Database connection successful")
        
        # Test getting all users
        result = await db.get_all_users()
        print(f"📊 Current users count: {result['total_users']}")
        
        for user in result['users'][:3]:  # Show first 3 users
            print(f"  - {user.get('email', 'No email')} (ID: {user.get('user_id', 'No ID')})")
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting registration debug tests")
    print("=" * 50)
    
    async def run_tests():
        # Test database connection first
        db_ok = await test_database_connection()
        
        if db_ok:
            print("\n" + "=" * 50)
            # Test user registration
            reg_ok = await test_user_registration()
            
            if reg_ok:
                print("\n✅ All tests passed!")
            else:
                print("\n❌ Registration test failed!")
        else:
            print("\n❌ Database connection failed!")
    
    asyncio.run(run_tests())
