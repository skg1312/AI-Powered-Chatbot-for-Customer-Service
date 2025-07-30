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
1. RAG_Agent - For questions about medical conditions, symptoms, treatments, general health information
2. WebSearch_Agent - For current medical news, latest research, drug recalls, recent health updates
3. Appointment_Agent - For scheduling, booking, or managing medical appointments
4. Logistics_Agent - For hospital/clinic information, directions, hours, contact details

Rules:
- Choose RAG_Agent for general medical knowledge questions
- Choose WebSearch_Agent only for current/recent medical information
- Choose Appointment_Agent for scheduling-related queries
- Choose Logistics_Agent for facility information

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
            valid_agents = ["RAG_Agent", "WebSearch_Agent", "Appointment_Agent", "Logistics_Agent"]
            if agent_decision in valid_agents:
                print(f"🔀 Router decision: {query[:50]}... → {agent_decision}")
                return agent_decision
            else:
                print(f"⚠️  Invalid router decision: {agent_decision}, defaulting to RAG_Agent")
                return "RAG_Agent"
                
        except Exception as e:
            print(f"❌ Error in routing query: {str(e)}")
            return "RAG_Agent"  # Default fallback
