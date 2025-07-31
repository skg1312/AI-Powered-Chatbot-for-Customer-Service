"""
Router Agent for Medical AI Chatbot Service.
Routes incoming queries to the most appropriate specialized agent.
"""

from groq import Groq
from app.core.config import config

class RouterAgent:
    """Agent that routes queries to appropriate specialized agents based on content analysis."""
    
    def __init__(self):
        """Initialize the router agent with Groq client."""
        try:
            self.client = Groq(api_key=config.get_groq_api_key())
            print("✅ Router agent initialized successfully")
        except Exception as e:
            print(f"⚠️  Router agent initialized with limited functionality: {str(e)}")
            self.client = None
    
    def route_query(self, query: str) -> str:
        """
        Analyze the query and determine which agent should handle it.
        
        Args:
            query (str): User's query to analyze
            
        Returns:
            str: Name of the agent that should handle the query
        """
        if not self.client:
            return "RAG_Agent"  # Default fallback
        
        try:
            routing_prompt = f"""Analyze this medical query and determine which specialized agent should handle it.

Query: "{query}"

Available agents:
1. RAG_Agent - For questions about medical conditions, symptoms, treatments, general health information, appointment-related queries, and facility information
2. WebSearch_Agent - For current medical news, latest research, drug recalls, recent health updates, breaking health news

Rules:
- Choose RAG_Agent for general medical knowledge questions, appointment inquiries, hospital/clinic information
- Choose WebSearch_Agent ONLY for current/recent medical information that requires up-to-date search results
- When in doubt, choose RAG_Agent

Respond with only the agent name (e.g., "RAG_Agent")."""

            response = self.client.chat.completions.create(
                model=config.ROUTER_MODEL,
                messages=[
                    {"role": "user", "content": routing_prompt}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            agent_decision = response.choices[0].message.content.strip()
            
            # Validate the response
            valid_agents = ["RAG_Agent", "WebSearch_Agent"]
            if agent_decision in valid_agents:
                return agent_decision
            else:
                print(f"⚠️  Invalid agent decision '{agent_decision}', defaulting to RAG_Agent")
                return "RAG_Agent"
                
        except Exception as e:
            print(f"⚠️  Error in routing: {str(e)}, defaulting to RAG_Agent")
            return "RAG_Agent"