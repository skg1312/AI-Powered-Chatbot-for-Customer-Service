"""
Web Search Agent for Medical AI Chatbot Service.
Handles queries requiring current medical information from trusted web sources.
"""

from typing import Dict, Any, List
from tavily import TavilyClient
from app.core.config import config

class WebSearchAgent:
    """Agent that searches the web for current medical information using Tavily."""
    
    def __init__(self):
        """Initialize the web search agent with Tavily client."""
        try:
            tavily_api_key = config.get_tavily_api_key()
            if tavily_api_key and tavily_api_key != "dummy-key":
                self.client = TavilyClient(api_key=tavily_api_key)
                print("✅ Tavily client initialized successfully")
            else:
                print("⚠️  Tavily API key not configured")
                self.client = None
        except Exception as e:
            print(f"⚠️  Web search agent initialized with limited functionality: {str(e)}")
            self.client = None
    
    def search_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search the web for current medical information.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            Dict[str, Any]: Search results with context and sources
        """
        if not self.client:
            return {
                "context": "Web search temporarily unavailable. Please check back later.",
                "sources": [],
                "success": False,
                "message": "Web search service not configured",
                "query": query
            }
        
        try:
            # Define trusted medical websites
            curated_sites = [
                "mayoclinic.org",
                "webmd.com",
                "healthline.com",
                "medlineplus.gov",
                "who.int",
                "cdc.gov",
                "nih.gov",
                "pubmed.ncbi.nlm.nih.gov"
            ]
            
            # Enhance query for medical context
            medical_query = f"medical health {query}"
            
            # Search with Tavily
            search_results = self.client.search(
                query=medical_query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=curated_sites
            )
            
            if not search_results.get("results"):
                return {
                    "context": "No current web information found for this query.",
                    "sources": [],
                    "success": True,
                    "message": "No relevant web results found",
                    "query": query
                }
            
            # Process and format results
            context_parts = []
            sources = []
            
            for result in search_results["results"][:max_results]:
                title = result.get("title", "")
                content = result.get("content", "")
                url = result.get("url", "")
                
                if content:
                    # Format the content
                    formatted_content = f"**{title}**\n{content}"
                    context_parts.append(formatted_content)
                    
                    sources.append({
                        "title": title,
                        "url": url,
                        "content": content[:300] + "..." if len(content) > 300 else content
                    })
            
            # Combine all context
            combined_context = "\n\n".join(context_parts)
            
            print(f"🌐 Found {len(sources)} web sources for query: {query[:50]}...")
            
            return {
                "context": combined_context,
                "sources": sources,
                "success": True,
                "message": f"Found {len(sources)} current web sources",
                "query": query
            }
            
        except Exception as e:
            print(f"❌ Error in web search: {str(e)}")
            return {
                "context": "Web search encountered an error. Please try again later.",
                "sources": [],
                "success": False,
                "message": f"Web search error: {str(e)}",
                "query": query
            }
    
    def search_curated_sites(self, query: str, sites: List[str]) -> Dict[str, Any]:
        """
        Search specific curated medical websites.
        
        Args:
            query (str): Search query
            sites (List[str]): List of websites to search
            
        Returns:
            Dict[str, Any]: Search results from curated sites
        """
        if not self.client:
            return {
                "context": "Curated search temporarily unavailable.",
                "sources": [],
                "success": False,
                "message": "Search service not configured"
            }
        
        try:
            # Search with domain restriction
            search_results = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_domains=sites
            )
            
            if not search_results.get("results"):
                return {
                    "context": "No information found on the specified medical websites.",
                    "sources": [],
                    "success": True,
                    "message": "No results from curated sites"
                }
            
            context_parts = []
            sources = []
            
            for result in search_results["results"]:
                title = result.get("title", "")
                content = result.get("content", "")
                url = result.get("url", "")
                
                if content:
                    formatted_content = f"**{title}** (from {url})\n{content}"
                    context_parts.append(formatted_content)
                    
                    sources.append({
                        "title": title,
                        "url": url,
                        "content": content,
                        "site": url.split('/')[2] if '/' in url else url
                    })
            
            combined_context = "\n\n".join(context_parts)
            
            return {
                "context": combined_context,
                "sources": sources,
                "success": True,
                "message": f"Found {len(sources)} results from curated sites"
            }
            
        except Exception as e:
            print(f"❌ Error in curated site search: {str(e)}")
            return {
                "context": "Error searching curated medical websites.",
                "sources": [],
                "success": False,
                "message": f"Curated search error: {str(e)}"
            }
