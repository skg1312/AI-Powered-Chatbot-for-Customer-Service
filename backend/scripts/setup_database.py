"""
Database Schema Setup for Supabase
This script will create all required tables in your Supabase database.
"""
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

async def setup_database():
    """Create database schema in Supabase"""
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')  # Use service key for admin operations
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    try:
        print("🔗 Connecting to Supabase...")
        supabase = create_client(supabase_url, supabase_key)
        
        print("📋 Creating database tables...")
        
        # Read the SQL schema file
        with open('database_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Split into individual statements and execute
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            if statement:
                try:
                    print(f"  Executing statement {i+1}/{len(statements)}...")
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"  ✅ Statement {i+1} executed successfully")
                except Exception as e:
                    print(f"  ⚠️  Statement {i+1} failed (might already exist): {str(e)}")
        
        print("🎉 Database schema setup completed!")
        
        # Test the connection
        print("🧪 Testing database connection...")
        result = supabase.table('users').select('count', count='exact').execute()
        print(f"✅ Users table ready (current count: {result.count})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        print("\n📋 Manual Setup Required:")
        print("1. Go to https://app.supabase.com/project/sirayxjmkhtsbrlmxnhz")
        print("2. Click 'SQL Editor' in the sidebar")
        print("3. Copy and paste the content from 'database_schema.sql'")
        print("4. Click 'Run' to execute the schema")
        return False

if __name__ == "__main__":
    print("🚀 Starting Supabase Database Setup")
    print("=" * 50)
    
    success = asyncio.run(setup_database())
    
    if success:
        print("\n✅ Setup completed! Your database is ready.")
        print("🚀 You can now start your application:")
        print("   python -m uvicorn app.main:app --reload --port 8001")
    else:
        print("\n❌ Automatic setup failed. Please use manual setup.")
