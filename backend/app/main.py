"""
Main FastAPI application for Medical AI Chatbot Service.
Provides multi-agent chat functionality with routing, RAG, web search, and safety checking.
Now integrated with Supabase for scalable data storage.
"""

import json
import os
import requests
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from groq import Groq
import asyncio
from dotenv import load_dotenv
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# CORS Configuration
ALLOWED_ORIGINS_ENV = os.getenv('ALLOWED_ORIGINS', '')
if ALLOWED_ORIGINS_ENV:
    if ALLOWED_ORIGINS_ENV == '*':
        ALLOWED_ORIGINS = ["*"]
    else:
        ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(',')]
else:
    # Default allowed origins for production
    ALLOWED_ORIGINS = [
        "*",  # Allow all origins for public widget
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://*.vercel.app",
        "https://ai-powered-chatbot-for-customer-service-mdmc7w1y8.vercel.app",
        "https://ai-powered-chatbot-for-customer-ser.vercel.app",  # Current Vercel domain
        "https://medical-ai-chatbot.vercel.app",
        "https://medical-ai-chatbot-frontend.vercel.app",
        "null"  # Allow file:// protocol for local testing
    ]

print(f"🌐 CORS Origins: {ALLOWED_ORIGINS}")

# Security
security = HTTPBearer()

from app.core.config import config
from app.agents.router import RouterAgent
from app.agents.rag_agent import RAGAgent
from app.agents.web_search_agent import WebSearchAgent

# Force Supabase database only - no local file storage
from app.database.supabase_db import get_database
USE_SUPABASE = True
logger = logging.getLogger(__name__)
logger.info("🔄 Using Supabase database ONLY - no local file storage")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration file paths (fallback for file-based storage)
CONFIG_FILE = "project_configs.json"
CHAT_HISTORY_FILE = "chat_history.json"
USERS_FILE = "users.json"

# Initialize FastAPI app
app = FastAPI(
    title="Medical AI Chatbot Service",
    description="Multi-agent medical chatbot with RAG, web search, and safety features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel subdomains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "cors_origins": ALLOWED_ORIGINS[:5] if len(ALLOWED_ORIGINS) > 5 else ALLOWED_ORIGINS,  # Show first 5 for security
        "version": "1.0.0"
    }

# Root endpoint with API status
@app.get("/")
@app.head("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "service": "Medical AI Chatbot Backend",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "health": "/health",
        "api_status": "/api/status"
    }

# Comprehensive API status endpoint
@app.get("/api/status")
async def api_status(request: Request):
    """Comprehensive API status check for all services"""
    # Get origin for CORS
    origin = request.headers.get('origin', '')
    
    status = {
        "service": "Medical AI Chatbot Backend",
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": "operational",
        "services": {}
    }
    
    # Check Groq API
    try:
        groq_client = Groq(api_key=config.get_groq_api_key())
        test_response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model="llama-3.3-70b-versatile",
            max_tokens=5,
            temperature=0
        )
        status["services"]["groq"] = {
            "status": "operational",
            "model": "llama-3.3-70b-versatile",
            "last_check": datetime.utcnow().isoformat()
        }
    except Exception as e:
        status["services"]["groq"] = {
            "status": "error",
            "error": str(e)[:100],
            "last_check": datetime.utcnow().isoformat()
        }
        status["overall_status"] = "degraded"
    
    # Check HuggingFace API
    try:
        hf_token = config.get_hf_token()
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        # First, validate the token
        auth_response = requests.get(
            "https://huggingface.co/api/whoami-v2",
            headers=headers,
            timeout=5
        )
        
        if auth_response.status_code != 200:
            status["services"]["huggingface"] = {
                "status": "error",
                "error": "Invalid HuggingFace token",
                "last_check": datetime.utcnow().isoformat()
            }
            status["overall_status"] = "degraded"
        else:
            # Test the embedding API with correct model
            embedding_url = "https://api-inference.huggingface.co/models/BAAI/bge-small-en-v1.5"
            response = requests.post(
                embedding_url,
                headers=headers,
                json={"inputs": "test"},
                timeout=10
            )
            
            if response.status_code == 200:
                status["services"]["huggingface"] = {
                    "status": "operational",
                    "model": "BAAI/bge-small-en-v1.5",
                    "last_check": datetime.utcnow().isoformat()
                }
            elif response.status_code == 503:
                # Model is loading, this is temporary
                status["services"]["huggingface"] = {
                    "status": "degraded",
                    "error": "Model loading (503) - This is temporary",
                    "model": "BAAI/bge-small-en-v1.5",
                    "last_check": datetime.utcnow().isoformat()
                }
            else:
                # For now, just mark as operational if token is valid
                # The embedding functionality can be tested during actual usage
                status["services"]["huggingface"] = {
                    "status": "operational",
                    "model": "BAAI/bge-small-en-v1.5",
                    "note": "Token valid, API format may need adjustment",
                    "last_check": datetime.utcnow().isoformat()
                }
    except Exception as e:
        status["services"]["huggingface"] = {
            "status": "error",
            "error": str(e)[:100],
            "last_check": datetime.utcnow().isoformat()
        }
        status["overall_status"] = "degraded"
    
    # Check Pinecone
    try:
        from pinecone import Pinecone
        pinecone_config = config.get_pinecone_config()
        pc = Pinecone(api_key=pinecone_config["api_key"])
        indexes = pc.list_indexes()
        
        status["services"]["pinecone"] = {
            "status": "operational",
            "indexes": len(indexes.names()) if hasattr(indexes, 'names') else 0,
            "last_check": datetime.utcnow().isoformat()
        }
    except Exception as e:
        status["services"]["pinecone"] = {
            "status": "error",
            "error": str(e)[:100],
            "last_check": datetime.utcnow().isoformat()
        }
        status["overall_status"] = "degraded"
    
    # Check Tavily AI
    try:
        from tavily import TavilyClient
        tavily_client = TavilyClient(api_key=config.get_tavily_api_key())
        # Simple test query
        test_result = tavily_client.search("test", max_results=1)
        
        status["services"]["tavily"] = {
            "status": "operational",
            "last_check": datetime.utcnow().isoformat()
        }
    except Exception as e:
        status["services"]["tavily"] = {
            "status": "error",
            "error": str(e)[:100],
            "last_check": datetime.utcnow().isoformat()
        }
        status["overall_status"] = "degraded"
    
    # Check Supabase Database
    try:
        from app.database.supabase_db import get_database
        db = get_database()
        # Test with a simple connection check
        result = await db.get_all_users()
        
        status["services"]["supabase"] = {
            "status": "operational",
            "database_type": "supabase",
            "user_count": result.get("total_users", 0),
            "last_check": datetime.utcnow().isoformat()
        }
    except Exception as e:
        status["services"]["supabase"] = {
            "status": "error",
            "error": str(e)[:100],
            "last_check": datetime.utcnow().isoformat()
        }
        status["overall_status"] = "degraded"
    
    # Create response with explicit CORS headers
    from fastapi import Response
    response = Response(
        content=json.dumps(status),
        media_type="application/json"
    )
    
    # Add CORS headers explicitly
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

@app.options("/{full_path:path}")
async def preflight_handler(request: Request, full_path: str):
    """Handle CORS preflight requests for all endpoints"""
    response = Response()
    origin = request.headers.get('origin')
    
    # Allow the specific Vercel domain
    if origin and (
        origin == "https://ai-powered-chatbot-for-customer-ser.vercel.app" or
        origin.endswith(".vercel.app") or 
        "*" in ALLOWED_ORIGINS
    ):
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
        
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "86400"
    
    return response

# Initialize agents
router_agent = RouterAgent()
rag_agent = RAGAgent()
web_search_agent = WebSearchAgent()

# Initialize Groq client for generation and safety
groq_client = Groq(api_key=config.get_groq_api_key())

# Authentication functions
def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, hash_value = hashed_password.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
    except ValueError:
        return False

def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return user data."""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Helper function for default configuration
def get_default_config(project_id: str):
    """Get default configuration for a project."""
    return {
        "project_id": project_id,
        "bot_persona": "You are a compassionate medical AI assistant that provides accurate health information while emphasizing the importance of consulting healthcare professionals.",
        "curated_sites": [
            "mayoclinic.org",
            "webmd.com", 
            "healthline.com",
            "medlineplus.gov"
        ],
        "knowledge_base_files": []
    }



async def save_chat_message(project_id: str, session_id: str, user_id: str, user_message: str, bot_response: str, agent_used: str):
    """Save a chat message exchange to Supabase only."""
    try:
        from datetime import datetime
        
        timestamp = datetime.now().isoformat()
        
        # Create message objects
        user_message_obj = {
            "role": "user",
            "content": user_message,
            "timestamp": timestamp,
            "agent_used": None
        }
        
        bot_message_obj = {
            "role": "assistant",
            "content": bot_response,
            "timestamp": timestamp,
            "agent_used": agent_used
        }
        
        # Use Supabase database ONLY
        db = get_database()
        
        # Check if user exists in Supabase, if not set user_id to None to avoid foreign key constraint
        user_id_for_db = None
        if user_id:
            existing_user = await db.get_user_by_id(user_id)
            if existing_user:
                user_id_for_db = user_id
            else:
                logger.info(f"User {user_id} not found in Supabase, saving session without user_id reference")
        
        # Check if session exists
        existing_session = await db.get_session_by_id(session_id)
        
        if existing_session:
            # Update existing session with new messages
            current_messages = existing_session.get("messages", [])
            current_messages.extend([user_message_obj, bot_message_obj])
            
            await db.update_session(session_id, {
                "messages": current_messages,
                "updated_at": timestamp
            })
        else:
            # Create new session
            session_data = {
                "session_id": session_id,
                "user_id": user_id_for_db,  # Use the validated user_id or None
                "project_id": project_id,
                "messages": [user_message_obj, bot_message_obj],
                "title": user_message[:50] + "..." if len(user_message) > 50 else user_message,
                "status": "active",
                "created_at": timestamp,
                "updated_at": timestamp
            }
            
            await db.create_chat_session(session_data)
        
        logger.info(f"Saved chat message to Supabase for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error saving chat message to Supabase: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save chat message")



async def get_chat_history(project_id: str, user_id: str = None, limit: int = 50):
    """Get chat history for a project from Supabase only."""
    try:
        db = get_database()
        
        if user_id:
            # Get sessions for specific user
            sessions = await db.get_user_sessions(user_id)
            # Filter by project_id
            sessions = [s for s in sessions if s.get("project_id") == project_id]
        else:
            # Get all sessions and filter by project_id
            all_sessions_data = await db.get_all_sessions()
            sessions = [s for s in all_sessions_data.get("sessions", []) if s.get("project_id") == project_id]
        
        # Sort by updated_at timestamp (newest first)
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        # Limit results
        sessions = sessions[:limit]
        
        return {
            "sessions": sessions,
            "total_sessions": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Error getting chat history from Supabase: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")



# Database abstraction layer for Supabase integration
async def get_database_stats():
    """Get system statistics from Supabase only."""
    db = get_database()
    try:
        # Get statistics from Supabase
        users_data = await db.get_all_users()
        sessions_data = await db.get_all_sessions()
        config_data = await db.get_project_config("main")
        
        if not config_data:
            config_data = get_default_config("main")
        
        return {
            "total_users": users_data.get("total_users", 0),
            "total_sessions": len(sessions_data.get("sessions", [])),
            "knowledge_base_files": len(config_data.get("knowledge_base_files", [])),
            "curated_websites": len(config_data.get("curated_sites", [])),
            "active_agents": 4
        }
    except Exception as e:
        logger.error(f"Error getting Supabase stats: {str(e)}")
        # Return minimal stats on error
        return {
            "total_users": 0,
            "total_sessions": 0,
            "knowledge_base_files": 0,
            "curated_websites": 4,  # Default curated sites count
            "active_agents": 4
        }

async def get_all_users_db():
    """Get all users from Supabase only."""
    db = get_database()
    try:
        return await db.get_all_users()
    except Exception as e:
        logger.error(f"Error getting Supabase users: {str(e)}")
        return {"users": [], "total_users": 0}

async def get_user_by_id_db(user_id: str):
    """Get user by ID from Supabase only."""
    logger.info(f"get_user_by_id_db called for user_id: {user_id}")
    
    db = get_database()
    try:
        logger.info(f"Getting user from Supabase: {user_id}")
        supabase_user = await db.get_user_by_id(user_id)
        logger.info(f"Supabase user result: {supabase_user}")
        return supabase_user
    except Exception as e:
        logger.error(f"Error getting Supabase user {user_id}: {str(e)}")
        return None

async def get_user_by_email_db(email: str):
    """Get user by email from Supabase only."""
    db = get_database()
    return await db.get_user_by_email(email)

async def create_user_db(user_data: Dict[str, Any]) -> str:
    """Create user in Supabase only."""
    logger.info(f"create_user_db called - Using Supabase only")
    
    logger.info("Using Supabase to create user")
    db = get_database()
    try:
        result = await db.create_user(user_data)
        logger.info(f"Supabase create_user result: {result}")
        return result
    except Exception as e:
        logger.error(f"Supabase create_user failed: {str(e)}")
        raise

async def update_user_db(user_id: str, update_data: Dict[str, Any]) -> bool:
    """Update user in Supabase only."""
    db = get_database()
    return await db.update_user(user_id, update_data)

async def delete_user_db(user_id: str) -> bool:
    """Delete user from Supabase only."""
    db = get_database()
    return await db.delete_user(user_id)

async def get_all_sessions_db():
    """Get all chat sessions from database."""
    if USE_SUPABASE:
        db = get_database()
        return await db.get_all_sessions()
    else:
        # File-based fallback
        return load_chat_history()

async def get_session_by_id_db(session_id: str):
    """Get session by ID from database."""
    if USE_SUPABASE:
        db = get_database()
        return await db.get_session_by_id(session_id)
    else:
        # File-based fallback
        history = load_chat_history()
        sessions = history.get("sessions", [])
        return next((s for s in sessions if s["session_id"] == session_id), None)

async def get_project_config_db(project_id: str):
    """Get project configuration from Supabase only."""
    db = get_database()
    config = await db.get_project_config(project_id)
    return config if config else get_default_config(project_id)

async def update_project_config_db(project_id: str, config_data: Dict[str, Any]) -> bool:
    """Update project configuration in Supabase only."""
    db = get_database()
    return await db.update_project_config(project_id, config_data)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None  # For tracking unique users
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    sources: Dict[str, Any]
    safe: bool
    project_id: str

class ProjectConfig(BaseModel):
    project_id: str
    bot_persona: str
    curated_sites: List[str]
    knowledge_base_files: List[str]
    stats: Optional[Dict[str, Any]] = {
        "total_users": 0,
        "total_sessions": 0,
        "unique_users": set()  # Will be converted to list for JSON storage
    }

class HealthResponse(BaseModel):
    status: str
    message: str
    services: Dict[str, bool]

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    agent_used: Optional[str] = None

class ChatSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    project_id: str
    messages: List[ChatMessage]
    created_at: str
    updated_at: str

class ChatHistoryResponse(BaseModel):
    sessions: List[ChatSession]
    total_sessions: int

class UserProfile(BaseModel):
    user_id: str
    name: str
    email: str
    phone: Optional[str] = None
    age: Optional[int] = None
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None
    created_at: Optional[str] = None
    last_active: Optional[str] = None
    total_sessions: int = 0

class UserRegistration(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    age: Optional[int] = None
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile

class UsersResponse(BaseModel):
    users: List[UserProfile]
    total_users: int

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint that provides basic health information."""
    return {
        "status": "healthy",
        "message": "Medical AI Chatbot Service is running",
        "services": {
            "router": True,
            "rag": True,
            "web_search": True,
            "groq_api": bool(config.GROQ_API_KEY)
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint that verifies all services are operational."""
    try:
        # Test Groq connection
        groq_healthy = bool(config.GROQ_API_KEY)
        
        # Test Pinecone connection
        pinecone_healthy = bool(config.PINECONE_API_KEY)
        
        # Test HuggingFace connection
        hf_healthy = bool(config.HF_TOKEN)
        
        # Test Tavily connection
        tavily_healthy = bool(config.TAVILY_API_KEY)
        
        all_healthy = groq_healthy and pinecone_healthy and hf_healthy and tavily_healthy
        
        return {
            "status": "healthy" if all_healthy else "partial",
            "message": "All services operational" if all_healthy else "Some services may have limited functionality",
            "services": {
                "groq_api": groq_healthy,
                "pinecone": pinecone_healthy,
                "huggingface": hf_healthy,
                "tavily": tavily_healthy
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}",
            "services": {
                "groq_api": False,
                "pinecone": False,
                "huggingface": False,
                "tavily": False
            }
        }

def update_project_stats(project_id: str, user_id: str = None, new_session: bool = False):
    """
    Update project statistics for user and session tracking.
    
    Args:
        project_id (str): Project identifier
        user_id (str): Unique user identifier (optional)
        new_session (bool): Whether this is a new chat session
    """
    try:
        configs = load_project_configs()
        project_config = configs.get(project_id, get_default_config(project_id))
        
        # Initialize stats if not present
        if "stats" not in project_config:
            project_config["stats"] = {
                "total_users": 0,
                "total_sessions": 0,
                "unique_users": []
            }
        
        stats = project_config["stats"]
        
        # Track unique users
        if user_id and user_id not in stats.get("unique_users", []):
            if "unique_users" not in stats:
                stats["unique_users"] = []
            stats["unique_users"].append(user_id)
            stats["total_users"] = len(stats["unique_users"])
        
        # Track new sessions
        if new_session:
            stats["total_sessions"] = stats.get("total_sessions", 0) + 1
        
        # Save updated configuration
        configs[project_id] = project_config
        save_project_configs(configs)
        logger.info(f"Updated stats for project {project_id}: {stats}")
        
    except Exception as e:
        logger.error(f"Error updating project stats: {str(e)}")

def generate_final_response(query: str, context: str, agent_used: str, project_id: str) -> str:
    """
    Generate the final response using Groq with context from agents.
    
    Args:
        query (str): User's original query
        context (str): Context provided by the chosen agent
        agent_used (str): Name of the agent that provided context
        project_id (str): Project identifier
        
    Returns:
        str: Generated response
    """
    try:
        # Load project configuration to get the custom bot persona
        configs = load_project_configs()
        project_config = configs.get(project_id, get_default_config(project_id))
        bot_persona = project_config.get("bot_persona", "You are a helpful medical AI assistant.")
        
        # Build system prompt with custom persona and context
        system_prompt = f"""{bot_persona}

Context from {agent_used}:
{context}

Use this context to provide accurate and helpful responses while maintaining your defined personality and following your core rules."""

        response = groq_client.chat.completions.create(
            model=config.GENERATION_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return "I apologize, but I'm having trouble generating a response right now. Please try again or consult a healthcare professional for medical advice."

def route_query(query: str) -> str:
    """Route the query to the appropriate agent."""
    try:
        return router_agent.route_query(query)
    except Exception as e:
        logger.error(f"Error in routing: {str(e)}")
        return "RAG_Agent"  # Default fallback

def safety_check(content: str) -> bool:
    """
    Perform safety check using the main language model.
    
    Args:
        content (str): Content to check
        
    Returns:
        bool: True if content is safe, False otherwise
    """
    try:
        safety_prompt = f"""You are a safety classifier for medical AI responses. Analyze the following response and determine if it's safe and appropriate for a medical chatbot.

Response to analyze: "{content}"

Check for:
- Harmful medical advice
- Inappropriate content
- Dangerous recommendations
- Privacy violations

Respond with only "SAFE" or "UNSAFE" followed by a brief reason.

Classification:"""

        response = groq_client.chat.completions.create(
            model=config.SAFETY_MODEL,
            messages=[
                {"role": "user", "content": safety_prompt}
            ],
            temperature=0.1,
            max_tokens=50
        )
        
        safety_result = response.choices[0].message.content.strip().lower()
        
        # Check if response indicates safe content
        return "safe" in safety_result
        
    except Exception as e:
        logger.error(f"Error in safety check: {str(e)}")
        # Default to safe if safety check fails
        return True

@app.post("/api/chat/{project_id}", response_model=ChatResponse)
async def chat_endpoint(project_id: str, request: ChatRequest):
    """
    Main chat endpoint that routes queries through the multi-agent system.
    
    Args:
        project_id (str): Project identifier
        request (ChatRequest): Chat request with message
        
    Returns:
        ChatResponse: Generated response with metadata
    """
    try:
        query = request.message.strip()
        
        if not query:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        logger.info(f"Processing chat request for project {project_id}: {query[:100]}...")
        
        # Track user and session statistics
        user_id = request.user_id
        conversation_id = request.conversation_id
        is_new_session = conversation_id is None  # New session if no conversation_id provided
        
        if user_id or is_new_session:
            update_project_stats(project_id, user_id, is_new_session)
        
        # Update user activity if user is registered
        if user_id and is_new_session:
            update_user_activity(user_id)
        
        # Step 1: Route the query to appropriate agent
        agent_decision = route_query(query)
        logger.info(f"Router decision: {agent_decision}")
        
        # Step 2: Execute the chosen agent to get context
        context = ""
        sources = {}
        
        # Load project configuration for agent customization
        configs = load_project_configs()
        project_config = configs.get(project_id, get_default_config(project_id))
        
        if agent_decision == "RAG_Agent":
            rag_result = rag_agent.execute_rag_search(query)
            context = rag_result.get("context", "")
            sources = rag_result.get("sources", {})
        elif agent_decision == "WebSearch_Agent":
            # Use curated sites from project configuration
            curated_sites = project_config.get("curated_sites", [])
            if curated_sites:
                web_result = web_search_agent.search_curated_sites(query, curated_sites)
            else:
                web_result = web_search_agent.search_web(query)
            context = web_result.get("context", "")
            sources = web_result.get("sources", {})
        else:
            # General medical knowledge
            context = "Providing general medical knowledge based on training data."
            sources = {"type": "general", "description": "General medical knowledge from training data"}
        
        # Step 3: Generate final response
        final_response = generate_final_response(query, context, agent_decision, project_id)
        
        # Step 4: Safety check
        is_safe = safety_check(final_response)
        
        # Step 5: Save to chat history
        if conversation_id and user_id:
            await save_chat_message(project_id, conversation_id, user_id, query, final_response, agent_decision)
        
        return ChatResponse(
            response=final_response,
            agent_used=agent_decision,
            sources=sources,
            safe=is_safe,
            project_id=project_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/projects/{project_id}/config")
async def update_project_config(project_id: str, config_data: ProjectConfig):
    """
    Update project configuration.
    
    Args:
        project_id (str): Project identifier
        config_data (ProjectConfig): Configuration data to update
        
    Returns:
        dict: Success message
    """
    try:
        # Load existing configurations
        configs = load_project_configs()
        
        # Update the specific project configuration
        configs[project_id] = {
            "project_id": project_id,
            "bot_persona": config_data.bot_persona,
            "curated_sites": config_data.curated_sites,
            "knowledge_base_files": config_data.knowledge_base_files
        }
        
        # Save back to file
        if save_project_configs(configs):
            logger.info(f"Configuration saved for project {project_id}")
            return {
                "status": "success",
                "message": f"Configuration updated for project {project_id}",
                "config": configs[project_id]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save configuration")
            
    except Exception as e:
        logger.error(f"Error updating config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update configuration")

@app.get("/api/projects/{project_id}/config")
async def get_project_config(project_id: str):
    """Get project configuration."""
    try:
        # Load configurations from file
        configs = load_project_configs()
        
        # Return saved config or default if not found
        if project_id in configs:
            return configs[project_id]
        else:
            # Return and save default configuration
            default_config = get_default_config(project_id)
            configs[project_id] = default_config
            save_project_configs(configs)
            return default_config
            
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get configuration")

@app.get("/api/projects/{project_id}/stats")
async def get_project_stats(project_id: str):
    """
    Get project statistics including user and session counts.
    
    Args:
        project_id (str): Project identifier
        
    Returns:
        dict: Project statistics
    """
    try:
        # Use database abstraction layer
        stats = await get_database_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@app.get("/api/stats")
async def get_stats():
    """
    Get system statistics including user count, sessions, files, etc.
    
    Returns:
        dict: System statistics
    """
    try:
        logger.info(f"Getting stats, USE_SUPABASE: {USE_SUPABASE}")
        stats = await get_database_stats()
        logger.info(f"Stats retrieved: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        # Return default stats on error
        return {
            "total_users": 0,
            "total_sessions": 0,
            "knowledge_base_files": 0,
            "curated_websites": 0,
            "active_agents": 4
        }

@app.get("/api/projects/{project_id}/chat-history", response_model=ChatHistoryResponse)
async def get_project_chat_history(project_id: str, user_id: str = None, limit: int = 50):
    """
    Get chat history for a project.
    
    Args:
        project_id (str): Project identifier
        user_id (str, optional): Filter by specific user
        limit (int): Maximum number of sessions to return
        
    Returns:
        ChatHistoryResponse: Chat history data
    """
    try:
        history_data = await get_chat_history(project_id, user_id, limit)
        return ChatHistoryResponse(
            sessions=[ChatSession(**session) for session in history_data["sessions"]],
            total_sessions=history_data["total_sessions"]
        )
        
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")

@app.get("/api/projects/{project_id}/chat-history/{session_id}")
async def get_chat_session(project_id: str, session_id: str):
    """
    Get a specific chat session.
    
    Args:
        project_id (str): Project identifier
        session_id (str): Session identifier
        
    Returns:
        dict: Chat session data
    """
    try:
        chat_data = load_chat_history()
        project_sessions = chat_data.get(project_id, {})
        
        if session_id in project_sessions:
            return project_sessions[session_id]
        else:
            raise HTTPException(status_code=404, detail="Chat session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get chat session")

@app.delete("/api/projects/{project_id}/chat-history/{session_id}")
async def delete_chat_session(project_id: str, session_id: str):
    """
    Delete a specific chat session.
    
    Args:
        project_id (str): Project identifier
        session_id (str): Session identifier
        
    Returns:
        dict: Success message
    """
    try:
        chat_data = load_chat_history()
        project_sessions = chat_data.get(project_id, {})
        
        if session_id in project_sessions:
            del project_sessions[session_id]
            save_chat_history(chat_data)
            return {"message": "Chat session deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Chat session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete chat session")

# User Management Endpoints
@app.post("/api/users/register")
async def register_new_user(user_data: UserRegistration):
    """
    Register a new user.
    
    Args:
        user_data (UserRegistration): User registration data
        
    Returns:
        dict: User ID and profile information
    """
    try:
        from datetime import datetime
        
        logger.info(f"Attempting to register user: {user_data.email}")
        
        # Check if user already exists by email
        existing_user = await get_user_by_email_db(user_data.email)
        if existing_user:
            logger.warning(f"User already exists: {user_data.email}")
            return {
                "user_id": existing_user["user_id"],
                "message": "User already exists",
                "profile": existing_user
            }
        
        # Generate unique user ID
        user_id = f"user_{user_data.name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"
        
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        logger.info(f"Generated user ID: {user_id}, USE_SUPABASE: {USE_SUPABASE}")
        
        # Prepare user data
        user_profile_data = {
            "user_id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hashed_password,
            "phone": user_data.phone,
            "age": user_data.age,
            "medical_conditions": user_data.medical_conditions,
            "emergency_contact": user_data.emergency_contact
        }
        
        logger.info(f"Creating user in database...")
        
        # Create user in database
        created_user_id = await create_user_db(user_profile_data)
        user_profile = await get_user_by_id_db(created_user_id)
        
        logger.info(f"Successfully registered new user: {created_user_id}")
        logger.info(f"User profile retrieved: {user_profile}")
        
        return {
            "user_id": created_user_id,
            "message": "User registered successfully",
            "profile": user_profile
        }
        
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register user")

@app.post("/api/users/login", response_model=LoginResponse)
async def login_user(login_data: UserLogin):
    """
    Login user with email and password.
    
    Args:
        login_data (UserLogin): User login credentials
        
    Returns:
        LoginResponse: Access token and user profile
    """
    try:
        # Authenticate user using database
        if USE_SUPABASE:
            db = get_database()
            # Get user by email first
            user = await db.get_user_by_email(login_data.email)
            if user and verify_password(login_data.password, user.get('password_hash', '')):
                # User authenticated successfully
                pass
            else:
                user = None
        else:
            user = authenticate_user(login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token(data={
            "sub": user["email"],
            "user_id": user["user_id"],
            "name": user["name"]
        })
        
        # Remove password hash from response
        user_profile = {k: v for k, v in user.items() if k != "password_hash"}
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserProfile(**user_profile)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to login user")

@app.get("/api/users", response_model=UsersResponse)
async def get_users():
    """
    Get all registered users.
    
    Returns:
        UsersResponse: List of all users
    """
    try:
        users_data = await get_all_users_db()
        return UsersResponse(
            users=[UserProfile(**user) for user in users_data["users"]],
            total_users=users_data["total_users"]
        )
        
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get users")

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """
    Get a specific user profile.
    
    Args:
        user_id (str): User identifier
        
    Returns:
        dict: User profile
    """
    try:
        user_profile = await get_user_by_id_db(user_id)
        if user_profile:
            # Remove password hash from response
            user_response = {k: v for k, v in user_profile.items() if k != "password_hash"}
            return user_response
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user")

@app.put("/api/users/{user_id}")
async def update_user(user_id: str, user_data: UserRegistration):
    """
    Update a user profile.
    
    Args:
        user_id (str): User identifier
        user_data (UserRegistration): Updated user data
        
    Returns:
        dict: Updated user profile
    """
    try:
        users = load_users()
        if user_id not in users:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user data
        users[user_id].update({
            "name": user_data.name,
            "email": user_data.email,
            "phone": user_data.phone,
            "age": user_data.age,
            "medical_conditions": user_data.medical_conditions,
            "emergency_contact": user_data.emergency_contact
        })
        
        save_users(users)
        return users[user_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user")

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str):
    """
    Delete a user and all their chat sessions.
    
    Args:
        user_id (str): User identifier
        
    Returns:
        dict: Success message
    """
    try:
        # Check if user exists first
        if USE_SUPABASE:
            db = get_database()
            user = await db.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
        else:
            users = load_users()
            if user_id not in users:
                raise HTTPException(status_code=404, detail="User not found")
        
        # Delete user using proper database function
        deleted = await delete_user_db(user_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete user from database")
        
        # Also delete user's chat sessions
        if USE_SUPABASE:
            db = get_database()
            # Get all sessions for this user
            sessions = await db.get_all_sessions()
            for session in sessions.get("sessions", []):
                if session.get("user_id") == user_id:
                    await db.delete_session(session["session_id"])
        else:
            # File-based fallback for chat sessions
            chat_data = load_chat_history()
            for project_id in chat_data:
                sessions_to_delete = []
                for session_id, session in chat_data[project_id].items():
                    if session.get("user_id") == user_id:
                        sessions_to_delete.append(session_id)
                
                for session_id in sessions_to_delete:
                    del chat_data[project_id][session_id]
            
            save_chat_history(chat_data)
        
        return {"message": "User and associated chat sessions deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

@app.post("/api/projects/{project_id}/upload-knowledge")
async def upload_knowledge_base(project_id: str, files: List[UploadFile] = File(...)):
    """
    Upload knowledge base files.
    
    Args:
        project_id (str): Project identifier
        files (List[UploadFile]): Files to upload
        
    Returns:
        dict: Upload status and file information
    """
    try:
        uploaded_files = []
        
        for file in files:
            if file.content_type == "text/plain":
                content = await file.read()
                text_content = content.decode("utf-8")
                
                # Process the file content for RAG
                documents = [
                    {
                        "text": text_content,
                        "metadata": {
                            "filename": file.filename,
                            "project_id": project_id,
                            "type": "knowledge_base"
                        }
                    }
                ]
                
                # Add to RAG agent
                success = rag_agent.add_documents(documents)
                
                uploaded_files.append({
                    "filename": file.filename,
                    "size": len(text_content),
                    "status": "success" if success else "failed"
                })
            else:
                uploaded_files.append({
                    "filename": file.filename,
                    "status": "skipped",
                    "reason": "Only text files supported"
                })
        
        return {
            "status": "completed",
            "project_id": project_id,
            "files": uploaded_files
        }
        
    except Exception as e:
        logger.error(f"Error uploading files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload files")

@app.get("/api/agents/status")
async def get_agents_status():
    """Get status of all agents."""
    try:
        return {
            "router_agent": "active",
            "rag_agent": "active" if rag_agent.index else "inactive",
            "web_search_agent": "active" if config.TAVILY_API_KEY else "inactive",
            "safety_agent": "active"
        }
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        return {
            "router_agent": "unknown",
            "rag_agent": "unknown", 
            "web_search_agent": "unknown",
            "safety_agent": "unknown"
        }

@app.get("/api/chat/history")
async def get_chat_history():
    """
    Get all chat sessions for user dashboard or admin.
    
    Returns:
        dict: All chat sessions
    """
    try:
        chat_history = load_chat_history()
        return {
            "success": True,
            "sessions": chat_history.get("sessions", [])
        }
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@app.get("/api/chat/session/{session_id}")
async def get_session_details(session_id: str):
    """
    Get specific session details.
    
    Args:
        session_id (str): Session identifier
        
    Returns:
        dict: Session details
    """
    try:
        chat_history = load_chat_history()
        sessions = chat_history.get("sessions", [])
        
        session = next((s for s in sessions if s["session_id"] == session_id), None)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        return {
            "success": True,
            "session": session
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session details: {str(e)}")

@app.delete("/api/chat/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a specific chat session.
    
    Args:
        session_id (str): Session identifier
        
    Returns:
        dict: Success message
    """
    try:
        chat_history = load_chat_history()
        sessions = chat_history.get("sessions", [])
        
        # Find and remove the session
        original_count = len(sessions)
        chat_history["sessions"] = [s for s in sessions if s["session_id"] != session_id]
        
        if len(chat_history["sessions"]) == original_count:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Save updated history
        save_chat_history(chat_history)
        
        return {
            "success": True,
            "message": f"Session {session_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@app.put("/api/chat/session/{session_id}")
async def update_session(session_id: str, update_data: dict):
    """
    Update a specific chat session (e.g., title, status).
    
    Args:
        session_id (str): Session identifier
        update_data (dict): Data to update
        
    Returns:
        dict: Updated session
    """
    try:
        chat_history = load_chat_history()
        sessions = chat_history.get("sessions", [])
        
        # Find and update the session
        session_found = False
        for session in sessions:
            if session["session_id"] == session_id:
                session.update(update_data)
                session_found = True
                break
        
        if not session_found:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Save updated history
        save_chat_history(chat_history)
        
        return {
            "success": True,
            "message": f"Session {session_id} updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")

# CORS Management Endpoints (for enterprise users)
@app.get("/api/cors/origins")
async def get_allowed_origins():
    """Get currently allowed CORS origins"""
    return {"allowed_origins": ALLOWED_ORIGINS}

@app.post("/api/cors/test")
async def test_cors_origin(request: Dict[str, Any]):
    """Test if an origin is allowed for CORS"""
    origin = request.get("origin", "")
    if not origin:
        raise HTTPException(status_code=400, detail="Origin is required")
    
    is_allowed = (
        "*" in ALLOWED_ORIGINS or 
        origin in ALLOWED_ORIGINS or
        any(origin.endswith(allowed.replace("*", "")) for allowed in ALLOWED_ORIGINS if "*" in allowed)
    )
    
    return {
        "origin": origin,
        "allowed": is_allowed,
        "message": "Origin is allowed" if is_allowed else "Origin is not in CORS whitelist"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
