#!/usr/bin/env python3
"""
Create the missing messages table in Supabase
"""
import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def create_messages_table():
    """Create the messages table in Supabase"""
    print("🔧 Creating messages table in Supabase...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    # SQL to create messages table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        message_id VARCHAR(255) UNIQUE NOT NULL,
        session_id VARCHAR(255) NOT NULL,
        user_id VARCHAR(255),
        role VARCHAR(50) NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMPTZ DEFAULT NOW(),
        message_order INTEGER DEFAULT 0
    );
    """
    
    # SQL to create indexes
    create_indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
    CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
    CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
    CREATE INDEX IF NOT EXISTS idx_messages_message_id ON messages(message_id);
    """
    
    # SQL to add message_count column to chat_sessions
    add_column_sql = """
    ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS message_count INTEGER DEFAULT 0;
    """
    
    try:
        # Try to create the table using direct SQL execution
        print("📝 Creating messages table...")
        
        # First, let's check if the table already exists
        try:
            result = supabase.table("messages").select("*").limit(1).execute()
            print("✅ Messages table already exists!")
            return True
        except Exception:
            print("📝 Messages table doesn't exist, creating it...")
        
        # Since we can't execute raw SQL easily, let's try using supabase-py's table creation
        # This won't work directly, but let's check what tables exist first
        
        # Let's check existing tables by trying to query them
        tables_to_check = ["users", "chat_sessions", "messages", "project_configs"]
        existing_tables = []
        
        for table in tables_to_check:
            try:
                supabase.table(table).select("*").limit(1).execute()
                existing_tables.append(table)
                print(f"✅ Table '{table}' exists")
            except Exception as e:
                print(f"❌ Table '{table}' missing: {str(e)[:100]}...")
        
        if "messages" not in existing_tables:
            print("❌ Messages table is missing and cannot be created via Python client")
            print("📋 Please run this SQL manually in your Supabase SQL editor:")
            print(create_table_sql)
            print(create_indexes_sql)
            print(add_column_sql)
            return False
        else:
            print("✅ All required tables exist!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_messages_table()
