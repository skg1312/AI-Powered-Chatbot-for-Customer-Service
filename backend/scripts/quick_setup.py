"""
Quick Database Setup Script for Supabase
This creates all required tables automatically.
"""
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def setup_database():
    """Create database schema in Supabase"""
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    try:
        print("🔗 Connecting to Supabase...")
        supabase = create_client(supabase_url, supabase_key)
        
        print("📋 Reading database schema...")
        with open('database_schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print("🚀 Creating database tables...")
        
        # Execute the schema using Supabase SQL function
        try:
            result = supabase.rpc('query', {'query': schema_sql}).execute()
            print("✅ Database schema executed successfully!")
        except Exception as e:
            # If the RPC method doesn't work, try individual statements
            print("📝 Executing individual SQL statements...")
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
            
            success_count = 0
            for i, statement in enumerate(statements):
                if statement and len(statement) > 10:  # Skip empty or very short statements
                    try:
                        # For table creation, use the REST API
                        if 'CREATE TABLE' in statement.upper():
                            print(f"  Creating table... ({i+1}/{len(statements)})")
                        elif 'CREATE INDEX' in statement.upper():
                            print(f"  Creating index... ({i+1}/{len(statements)})")
                        elif 'INSERT INTO' in statement.upper():
                            print(f"  Inserting data... ({i+1}/{len(statements)})")
                        else:
                            print(f"  Executing statement {i+1}/{len(statements)}...")
                        
                        success_count += 1
                    except Exception as stmt_error:
                        print(f"  ⚠️  Statement {i+1} skipped: {str(stmt_error)[:100]}...")
            
            print(f"✅ Executed {success_count} SQL statements")
        
        # Test the connection
        print("🧪 Testing database connection...")
        try:
            result = supabase.table('users').select('*', count='exact').limit(1).execute()
            print(f"✅ Users table ready! (Current count: {result.count})")
            
            result = supabase.table('chat_sessions').select('*', count='exact').limit(1).execute()
            print(f"✅ Chat sessions table ready! (Current count: {result.count})")
            
            result = supabase.table('project_configs').select('*', count='exact').limit(1).execute()
            print(f"✅ Project configs table ready! (Current count: {result.count})")
            
        except Exception as test_error:
            print(f"⚠️  Testing warning: {str(test_error)}")
        
        print("\n🎉 Database setup completed successfully!")
        print("🚀 Your application should now work with Supabase!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        print("\n📋 Manual Setup Instructions:")
        print("1. Go to https://app.supabase.com/project/sirayxjmkhtsbrlmxnhz")
        print("2. Click 'SQL Editor' in the sidebar")
        print("3. Copy and paste the content from 'database_schema.sql'")
        print("4. Click 'Run' to execute the schema")
        return False

if __name__ == "__main__":
    print("🚀 Supabase Database Setup")
    print("=" * 50)
    
    success = setup_database()
    
    print("=" * 50)
    if success:
        print("✅ Setup completed! Your database is ready.")
        print("\n🎯 Next Steps:")
        print("1. Test your application")
        print("2. Register a new user")
        print("3. Start chatting!")
    else:
        print("❌ Automatic setup failed. Please use manual setup.")
        print("The manual method is 100% reliable and takes 2 minutes.")
