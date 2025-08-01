#!/usr/bin/env python3
"""
Start the FastAPI server - working version
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting AI Chatbot API server...")
    print("📊 Database: Supabase (with password_hash column)")
    print("🔧 Backend running on: http://localhost:8003")
    print("🌐 Frontend should connect to this API")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8003)
