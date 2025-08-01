#!/usr/bin/env python3
"""
Simple test server to debug registration issues
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting test server on port 8003...")
    uvicorn.run(app, host="0.0.0.0", port=8003)
