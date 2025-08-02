#!/usr/bin/env python3
"""
Fix user session counts - synchronize user.total_sessions with actual chat sessions
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.supabase_db import SupabaseDB

async def fix_user_session_counts():
    """Fix user session counts by counting actual chat sessions per user"""
    print("🔧 Fixing user session counts...")
    
    try:
        db = SupabaseDB()
        
        # Get all users
        users_data = await db.get_all_users()
        users = users_data.get("users", [])
        print(f"📊 Found {len(users)} users")
        
        # Get all sessions
        sessions_data = await db.get_all_sessions()
        sessions = sessions_data.get("sessions", [])
        print(f"📊 Found {len(sessions)} total sessions")
        
        # Count sessions per user
        user_session_counts = {}
        for session in sessions:
            user_id = session.get("user_id")
            if user_id:
                user_session_counts[user_id] = user_session_counts.get(user_id, 0) + 1
        
        print(f"📊 Session counts per user: {user_session_counts}")
        
        # Update each user's total_sessions count
        for user in users:
            user_id = user.get("user_id")
            if user_id:
                actual_sessions = user_session_counts.get(user_id, 0)
                current_sessions = user.get("total_sessions", 0)
                
                print(f"👤 User {user.get('email', user_id)[:30]}:")
                print(f"   Current: {current_sessions} sessions")
                print(f"   Actual:  {actual_sessions} sessions")
                
                if actual_sessions != current_sessions:
                    # Update the user's session count
                    update_success = await db.update_user(user_id, {
                        "total_sessions": actual_sessions
                    })
                    
                    if update_success:
                        print(f"   ✅ Updated to {actual_sessions} sessions")
                    else:
                        print(f"   ❌ Failed to update session count")
                else:
                    print(f"   ✅ Already correct")
        
        # Verify the fix
        print("\n🧪 Verifying fix...")
        updated_users = await db.get_all_users()
        total_user_sessions = sum(user.get("total_sessions", 0) for user in updated_users.get("users", []))
        total_sessions = len(sessions)
        
        print(f"📊 Total sessions: {total_sessions}")
        print(f"📊 Sum of user sessions: {total_user_sessions}")
        
        if total_user_sessions == total_sessions:
            print("✅ Session counts are now synchronized!")
        else:
            print("⚠️ There might be some anonymous sessions or data inconsistencies")
            
        return True
        
    except Exception as e:
        print(f"❌ Error fixing session counts: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def show_detailed_stats():
    """Show detailed statistics breakdown"""
    print("\n📊 Detailed Statistics Breakdown:")
    print("=" * 50)
    
    try:
        db = SupabaseDB()
        
        # Users
        users_data = await db.get_all_users()
        users = users_data.get("users", [])
        print(f"👥 Users: {len(users)}")
        for user in users:
            email = user.get("email", "No email")[:30]
            sessions = user.get("total_sessions", 0)
            print(f"   - {email}: {sessions} sessions")
        
        # Sessions
        sessions_data = await db.get_all_sessions()
        sessions = sessions_data.get("sessions", [])
        print(f"\n💬 Chat Sessions: {len(sessions)}")
        
        # Group sessions by user
        session_by_user = {}
        anonymous_sessions = 0
        
        for session in sessions:
            user_id = session.get("user_id")
            if user_id and user_id != "anonymous":
                session_by_user[user_id] = session_by_user.get(user_id, 0) + 1
            else:
                anonymous_sessions += 1
        
        print(f"   - Anonymous sessions: {anonymous_sessions}")
        for user_id, count in session_by_user.items():
            # Find user email
            user_email = "Unknown"
            for user in users:
                if user.get("user_id") == user_id:
                    user_email = user.get("email", "No email")[:30]
                    break
            print(f"   - {user_email} ({user_id[:8]}...): {count} sessions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error getting detailed stats: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting User Session Count Fix")
    print("=" * 50)
    
    async def run_fix():
        # Show current stats
        await show_detailed_stats()
        
        print("\n" + "=" * 50)
        # Fix the session counts
        success = await fix_user_session_counts()
        
        if success:
            print("\n" + "=" * 50)
            # Show updated stats
            await show_detailed_stats()
            print("\n✅ User session counts have been fixed!")
        else:
            print("\n❌ Failed to fix session counts!")
    
    asyncio.run(run_fix())
