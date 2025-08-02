#!/usr/bin/env python3
"""
Test script to debug user registration issues
"""
import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_user_registration():
    """Test user registration and database operations"""
    print("🔍 Testing User Registration System")
    print("="*50)
    
    try:
        # Import after loading env
        from app.database.supabase_db import SupabaseDB
        
        print("1. Testing Supabase connection...")
        db = SupabaseDB()
        await db.initialize()
        print("✅ Supabase connection successful")
        
        print("\n2. Testing user creation...")
        
        # Test user data
        test_user = {
            "user_id": "test_user_12345",
            "name": "Test User",
            "email": "test@example.com", 
            "password_hash": "test_hash_12345",
            "phone": "+1234567890",
            "age": 30,
            "medical_conditions": "None",
            "emergency_contact": "Emergency Contact",
            "created_at": "2025-08-01T20:00:00",
            "last_active": "2025-08-01T20:00:00",
            "total_sessions": 0
        }
        
        try:
            # Check if user already exists
            existing = await db.get_user_by_email("test@example.com")
            if existing:
                print("⚠️  Test user already exists, deleting first...")
                await db.delete_user(existing["user_id"])
            
            # Create user
            created_id = await db.create_user(test_user)
            print(f"✅ User created with ID: {created_id}")
            
            # Verify user exists
            retrieved_user = await db.get_user_by_id(created_id)
            if retrieved_user:
                print(f"✅ User retrieved successfully: {retrieved_user['name']}")
            else:
                print("❌ Failed to retrieve created user")
                
            # Clean up
            await db.delete_user(created_id)
            print("✅ Test user cleaned up")
            
        except Exception as user_error:
            print(f"❌ User creation failed: {str(user_error)}")
            
        print("\n3. Testing session creation...")
        
        # Test session data
        test_session = {
            "session_id": "test_session_12345",
            "user_id": None,  # Anonymous session
            "project_id": "main",  # Use "main" instead of "default"
            "title": "Test Session",
            "status": "active",
            "messages": [
                {"role": "user", "content": "Hello", "timestamp": "2025-08-01T20:00:00"},
                {"role": "assistant", "content": "Hi there!", "timestamp": "2025-08-01T20:00:01", "agent_used": "general"}
            ],
            "created_at": "2025-08-01T20:00:00",
            "updated_at": "2025-08-01T20:00:00"
        }
        
        try:
            # Check if session exists and delete
            existing_session = await db.get_session_by_id("test_session_12345")
            if existing_session:
                await db.delete_session("test_session_12345")
                
            # Create session
            created_session_id = await db.create_chat_session(test_session)
            print(f"✅ Session created with ID: {created_session_id}")
            
            # Verify session exists
            retrieved_session = await db.get_session_by_id(created_session_id)
            if retrieved_session:
                print(f"✅ Session retrieved successfully: {retrieved_session['title']}")
                print(f"   Project ID: {retrieved_session.get('project_id')}")
                print(f"   Messages: {len(retrieved_session.get('messages', []))}")
            else:
                print("❌ Failed to retrieve created session")
                
            # Clean up
            await db.delete_session(created_session_id)
            print("✅ Test session cleaned up")
            
        except Exception as session_error:
            print(f"❌ Session creation failed: {str(session_error)}")
            
        print("\n4. Testing chat history retrieval...")
        
        # Get all sessions and check project IDs
        try:
            all_sessions = await db.get_all_sessions()
            print(f"✅ Total sessions in database: {all_sessions['total_sessions']}")
            
            if all_sessions['sessions']:
                project_ids = set(s.get('project_id') for s in all_sessions['sessions'])
                print(f"   Project IDs found: {list(project_ids)}")
                
                # Test filtering by project_id
                main_sessions = [s for s in all_sessions['sessions'] if s.get('project_id') == 'main']
                default_sessions = [s for s in all_sessions['sessions'] if s.get('project_id') == 'default']
                
                print(f"   Sessions with project_id='main': {len(main_sessions)}")
                print(f"   Sessions with project_id='default': {len(default_sessions)}")
            
        except Exception as history_error:
            print(f"❌ Chat history retrieval failed: {str(history_error)}")
            
        print("\n5. Testing environment variables...")
        print(f"   SUPABASE_URL: {'✅ Set' if os.getenv('SUPABASE_URL') else '❌ Missing'}")
        print(f"   SUPABASE_ANON_KEY: {'✅ Set' if os.getenv('SUPABASE_ANON_KEY') else '❌ Missing'}")
        print(f"   DATABASE_TYPE: {os.getenv('DATABASE_TYPE', 'NOT SET')}")
        
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_user_registration())
