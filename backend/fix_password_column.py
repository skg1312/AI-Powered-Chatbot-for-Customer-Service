#!/usr/bin/env python3
"""
Add password_hash column to Supabase users table
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def add_password_column():
    """Add password_hash column to users table"""
    print("🔧 Adding password_hash column to users table...")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    try:
        client = create_client(url, key)
        
        # Read the SQL file
        with open('add_password_column.sql', 'r') as f:
            sql_content = f.read()
        
        print("📝 SQL to execute:")
        print(sql_content)
        
        # Execute the SQL - note: this might not work with anon key
        # We might need to run this manually in Supabase dashboard
        try:
            # Try to execute - this likely won't work due to permissions
            result = client.rpc('exec_sql', {'sql': sql_content}).execute()
            print("✅ SQL executed successfully")
            return True
        except Exception as e:
            print(f"❌ Cannot execute SQL with anon key: {str(e)}")
            print("\n📋 MANUAL SETUP REQUIRED:")
            print("1. Go to https://app.supabase.com/project/sirayxjmkhtsbrlmxnhz")
            print("2. Click 'SQL Editor' in the sidebar")
            print("3. Copy and paste this SQL:")
            print("-" * 50)
            print(sql_content)
            print("-" * 50)
            print("4. Click 'Run' to execute the SQL")
            print("\nThis will add the missing password_hash column to your users table.")
            return False
        
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    add_password_column()
