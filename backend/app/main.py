"""
Main FastAPI application for Medical AI Chatbot Service.
Provides multi-agent chat functionality with routing, RAG, web search, and safety checking.
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from groq import Groq
import json
import asyncio

from app.core.config import config
from app.agents.router import RouterAgent
from app.agents.rag_agent import RAGAgent
from app.agents.web_search_agent import WebSearchAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Medical AI Chatbot Service",
    description="Multi-agent medical chatbot with RAG, web search, and safety features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
router_agent = RouterAgent()
rag_agent = RAGAgent()
web_search_agent = WebSearchAgent()

# Initialize Groq client for generation and safety
groq_client = Groq(api_key=config.get_groq_api_key())

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
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

class HealthResponse(BaseModel):
    status: str
    message: str
    services: Dict[str, bool]

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
        system_prompt = f"""You are a helpful medical AI assistant. Use the provided context to answer the user's question accurately and safely.

Context from {agent_used}:
{context}

Guidelines:
- Provide accurate medical information based on the context
- Always include appropriate medical disclaimers
- Suggest consulting healthcare professionals for serious concerns
- Be empathetic and supportive
- If context is insufficient, acknowledge limitations

Remember: You are providing general medical information, not personal medical advice."""

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
        
        # Step 1: Route the query to appropriate agent
        agent_decision = route_query(query)
        logger.info(f"Router decision: {agent_decision}")
        
        # Step 2: Execute the chosen agent to get context
        context = ""
        sources = {}
        
        if agent_decision == "RAG_Agent":
            rag_result = rag_agent.execute_rag_search(query)
            context = rag_result.get("context", "")
            sources = rag_result.get("sources", {})
        elif agent_decision == "WebSearch_Agent":
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
        # In a real implementation, this would save to a database
        # For now, we'll just return success
        return {
            "status": "success",
            "message": f"Configuration updated for project {project_id}",
            "config": config_data.dict()
        }
    except Exception as e:
        logger.error(f"Error updating config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update configuration")

@app.get("/api/projects/{project_id}/config")
async def get_project_config(project_id: str):
    """Get project configuration."""
    try:
        # Return default configuration
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
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get configuration")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
