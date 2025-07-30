"""
Configuration module for the Medical AI Chatbot Service.
Loads environment variables and provides configuration settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class containing all environment variables and settings."""
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "medical-chatbot-index")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # Application Settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Model Configuration
    ROUTER_MODEL: str = "llama-3.3-70b-versatile"
    GENERATION_MODEL: str = "llama-3.3-70b-versatile"
    SAFETY_MODEL: str = "llama-3.3-70b-versatile"  # Using main model for safety checks
    EMBEDDING_MODEL: str = "microsoft/DialoGPT-medium"
    
    # Validation
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required environment variables are set."""
        required_vars = [
            "GROQ_API_KEY",
            "PINECONE_API_KEY", 
            "HF_TOKEN",
            "TAVILY_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
            print("✅ Will continue with graceful fallbacks")
            return False
        
        print("✅ Configuration validated successfully!")
        return True
    
    @classmethod
    def get_groq_api_key(cls) -> str:
        """Get Groq API key with fallback."""
        return cls.GROQ_API_KEY or "dummy-key"
    
    @classmethod
    def get_pinecone_config(cls) -> dict:
        """Get Pinecone configuration with fallbacks."""
        return {
            "api_key": cls.PINECONE_API_KEY or "dummy-key",
            "environment": cls.PINECONE_ENVIRONMENT or "dummy-env",
            "index_name": cls.PINECONE_INDEX_NAME
        }
    
    @classmethod
    def get_hf_token(cls) -> str:
        """Get HuggingFace token with fallback."""
        return cls.HF_TOKEN or "dummy-token"
    
    @classmethod
    def get_tavily_api_key(cls) -> str:
        """Get Tavily API key with fallback."""
        return cls.TAVILY_API_KEY or "dummy-key"

# Create global config instance
config = Config()

# Validate configuration on import
config.validate_config()
