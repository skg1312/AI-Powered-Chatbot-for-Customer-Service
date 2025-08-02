#!/usr/bin/env python3
"""
Comprehensive data consistency diagnostic script
"""
import asyncio
import sys
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.supabase_db import SupabaseDB

async def diagnose_data_consistency():
    """Comprehensive diagnosis of data consistency issues"""
    print("🔍 COMPREHENSIVE DATA CONSISTENCY DIAGNOSIS")
    print("=" * 60)
    
    try:
        db = SupabaseDB()
        
        # 1. Get all users
        print("\n1️⃣ USER DATA:")
        users_data = await db.get_all_users()
        users = users_data.get("users", [])
        print(f"   Total users in database: {len(users)}")
        
        for user in users:
            print(f"   👤 {user.get('email', 'No email')[:40]}")
            print(f"      - user_id: {user.get('user_id')}")
            print(f"      - total_sessions: {user.get('total_sessions', 0)}")
            print(f"      - created_at: {user.get('created_at')}")
            print(f"      - last_active: {user.get('last_active')}")
            print()
        
        # 2. Get all sessions
        print("\n2️⃣ SESSION DATA:")
        sessions_data = await db.get_all_sessions()
        sessions = sessions_data.get("sessions", [])
        print(f"   Total sessions in database: {len(sessions)}")
        
        # Group sessions by user_id
        sessions_by_user = {}
        anonymous_sessions = []
        
        for session in sessions:
            user_id = session.get("user_id")
            if user_id and user_id != "anonymous":
                if user_id not in sessions_by_user:
                    sessions_by_user[user_id] = []
                sessions_by_user[user_id].append(session)
            else:
                anonymous_sessions.append(session)
        
        print(f"   Sessions with user_id: {sum(len(sessions) for sessions in sessions_by_user.values())}")
        print(f"   Anonymous sessions: {len(anonymous_sessions)}")
        
        # Show sessions per user
        for user_id, user_sessions in sessions_by_user.items():
            print(f"   👤 User {user_id}: {len(user_sessions)} sessions")
            for i, session in enumerate(user_sessions, 1):
                print(f"      {i}. Session {session.get('session_id', 'No ID')[:20]}")
                print(f"         - created: {session.get('created_at')}")
                print(f"         - messages: {session.get('message_count', 0)}")
        
        # Show anonymous sessions
        if anonymous_sessions:
            print(f"   🔓 Anonymous sessions: {len(anonymous_sessions)}")
            for i, session in enumerate(anonymous_sessions, 1):
                print(f"      {i}. Session {session.get('session_id', 'No ID')[:20]}")
                print(f"         - created: {session.get('created_at')}")
                print(f"         - messages: {session.get('message_count', 0)}")
        
        # 3. Cross-reference data
        print("\n3️⃣ DATA CONSISTENCY CHECK:")
        for user in users:
            user_id = user.get('user_id')
            user_email = user.get('email', 'No email')
            stored_sessions = user.get('total_sessions', 0)
            actual_sessions = len(sessions_by_user.get(user_id, []))
            
            status = "✅ MATCH" if stored_sessions == actual_sessions else "❌ MISMATCH"
            print(f"   {status} {user_email[:30]}: stored={stored_sessions}, actual={actual_sessions}")
        
        # 4. Get all messages for verification
        print("\n4️⃣ MESSAGE DATA:")
        
        # Try to get messages directly from Supabase
        from supabase import create_client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if supabase_url and supabase_key:
            supabase = create_client(supabase_url, supabase_key)
            
            # Get all messages
            response = supabase.table("messages").select("*").execute()
            messages = response.data if response.data else []
            print(f"   Total messages in database: {len(messages)}")
            
            # Group messages by session_id
            messages_by_session = {}
            for message in messages:
                session_id = message.get("session_id")
                if session_id:
                    if session_id not in messages_by_session:
                        messages_by_session[session_id] = []
                    messages_by_session[session_id].append(message)
            
            print(f"   Unique sessions with messages: {len(messages_by_session)}")
            
            # Verify session message counts
            print("\n5️⃣ SESSION MESSAGE COUNT VERIFICATION:")
            for session in sessions:
                session_id = session.get("session_id")
                stored_count = session.get("message_count", 0)
                actual_count = len(messages_by_session.get(session_id, []))
                
                status = "✅" if stored_count == actual_count else "❌"
                print(f"   {status} Session {session_id[:20]}: stored={stored_count}, actual={actual_count}")
        
        print("\n" + "=" * 60)
        print("🎯 SUMMARY:")
        print(f"   Users: {len(users)}")
        print(f"   Sessions: {len(sessions)}")
        print(f"   Sessions with user_id: {sum(len(sessions) for sessions in sessions_by_user.values())}")
        print(f"   Anonymous sessions: {len(anonymous_sessions)}")
        
        # Calculate total mismatches
        mismatches = 0
        for user in users:
            user_id = user.get('user_id')
            stored_sessions = user.get('total_sessions', 0)
            actual_sessions = len(sessions_by_user.get(user_id, []))
            if stored_sessions != actual_sessions:
                mismatches += 1
        
        print(f"   Users with session count mismatches: {mismatches}")
        
        if mismatches > 0:
            print("\n⚠️  RECOMMENDATION: Run fix_session_counts.py to fix mismatches")
        else:
            print("\n✅ All session counts are accurate!")
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose_data_consistency())
