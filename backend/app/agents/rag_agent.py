"""
RAG Agent for Medical AI Chatbot Service.
Handles queries that require information from the knowledge base using Retrieval-Augmented Generation.
"""

import requests
import json
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from app.core.config import config

class RAGAgent:
    """Agent that handles knowledge base queries using RAG (Retrieval-Augmented Generation)."""
    
    def __init__(self):
        """Initialize the RAG agent with Pinecone and HuggingFace connections."""
        try:
            self.hf_token = config.get_hf_token()
            self.embedding_model = config.EMBEDDING_MODEL
            
            # Initialize Pinecone
            pinecone_config = config.get_pinecone_config()
            self.pc = Pinecone(api_key=pinecone_config["api_key"])
            self.index_name = pinecone_config["index_name"]
            
            # Initialize or connect to index
            try:
                self._setup_pinecone_index()
                print("✅ Pinecone initialized successfully")
            except Exception as e:
                print(f"⚠️  Pinecone not configured: {str(e)}")
                self.index = None
            
            # HuggingFace API endpoints
            self.embedding_url = f"https://api-inference.huggingface.co/models/{self.embedding_model}"
            self.headers = {"Authorization": f"Bearer {self.hf_token}"}
        except Exception as e:
            print(f"⚠️  RAG Agent initialized without proper configuration: {str(e)}")
            self.pc = None
            self.index = None
    
    def _setup_pinecone_index(self):
        """Setup Pinecone index for vector storage."""
        try:
            # Check if index exists
            if self.index_name not in self.pc.list_indexes().names():
                print(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # sentence-transformers/all-MiniLM-L6-v2 dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            
            # Connect to the index
            self.index = self.pc.Index(self.index_name)
            print(f"✅ Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            print(f"❌ Error setting up Pinecone index: {str(e)}")
            self.index = None
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for text using HuggingFace API.
        
        Args:
            texts (List[str]): List of texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        try:
            # Use the feature extraction API with BGE model
            feature_extraction_url = f"https://api-inference.huggingface.co/models/{self.embedding_model}"
            
            # For single text or multiple texts
            if isinstance(texts, list) and len(texts) == 1:
                payload = {"inputs": texts[0]}
            else:
                payload = {"inputs": texts}
                
            response = requests.post(
                feature_extraction_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                embeddings = response.json()
                
                # Handle different response formats
                if isinstance(embeddings, list) and len(embeddings) > 0:
                    if isinstance(embeddings[0], list):
                        return embeddings
                    else:
                        return [embeddings]
                else:
                    raise ValueError("Unexpected embedding response format")
            else:
                raise Exception(f"HuggingFace API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error getting embeddings: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the knowledge base.
        
        Args:
            documents (List[Dict[str, Any]]): List of documents with text and metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.index:
            print("⚠️  Pinecone index not available")
            return False
        
        try:
            vectors_to_upsert = []
            
            for i, doc in enumerate(documents):
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})
                
                if not text:
                    continue
                
                # Get embedding for the text
                embedding = self.get_embeddings([text])[0]
                
                # Create vector with unique ID
                vector_id = f"doc_{hash(text)}_{i}"
                vectors_to_upsert.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        **metadata,
                        "text": text[:1000]  # Store first 1000 chars in metadata
                    }
                })
            
            if vectors_to_upsert:
                # Upsert to Pinecone
                self.index.upsert(vectors=vectors_to_upsert)
                print(f"✅ Added {len(vectors_to_upsert)} documents to knowledge base")
                return True
            else:
                print("⚠️  No valid documents to add")
                return False
                
        except Exception as e:
            print(f"❌ Error adding documents: {str(e)}")
            return False
    
    def search_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant documents.
        
        Args:
            query (str): Search query
            top_k (int): Number of top results to return
            
        Returns:
            List[Dict[str, Any]]: List of relevant documents with scores
        """
        if not self.index:
            print("⚠️  Pinecone index not available")
            return []
        
        try:
            # Get query embedding
            query_embedding = self.get_embeddings([query])[0]
            
            # Search Pinecone
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            relevant_docs = []
            for match in search_results["matches"]:
                if match["score"] > 0.7:  # Similarity threshold
                    doc = {
                        "text": match["metadata"].get("text", ""),
                        "score": match["score"],
                        "metadata": match["metadata"]
                    }
                    relevant_docs.append(doc)
            
            print(f"🔍 Found {len(relevant_docs)} relevant documents for query: {query[:50]}...")
            return relevant_docs
            
        except Exception as e:
            print(f"❌ Error searching knowledge base: {str(e)}")
            return []
    
    def execute_rag_search(self, query: str, context_limit: int = 3000) -> Dict[str, Any]:
        """
        Execute RAG search and return formatted context.
        
        Args:
            query (str): User's query
            context_limit (int): Maximum characters in context
            
        Returns:
            Dict[str, Any]: Search results with context and sources
        """
        try:
            # Search knowledge base
            relevant_docs = self.search_knowledge_base(query)
            
            if not relevant_docs:
                return {
                    "context": "No specific information found in knowledge base. Providing general medical knowledge.",
                    "sources": {"type": "general", "description": "No relevant documents found"},
                    "success": True,
                    "message": "Using general medical knowledge",
                    "query": query
                }
            
            # Combine relevant documents into context
            context_parts = []
            source_list = []
            current_length = 0
            
            for doc in relevant_docs:
                doc_text = doc["text"]
                if current_length + len(doc_text) > context_limit:
                    break
                
                context_parts.append(doc_text)
                source_list.append({
                    "text": doc_text[:200] + "..." if len(doc_text) > 200 else doc_text,
                    "score": doc["score"],
                    "metadata": doc["metadata"]
                })
                current_length += len(doc_text)
            
            # Combine all context
            combined_context = "\n\n".join(context_parts)
            
            return {
                "context": combined_context,
                "sources": {
                    "type": "knowledge_base",
                    "count": len(source_list),
                    "documents": source_list
                },
                "success": True,
                "message": f"Found {len(source_list)} relevant documents",
                "query": query
            }
            
        except Exception as e:
            print(f"❌ Error in RAG search execution: {str(e)}")
            # Provide a helpful fallback response when knowledge base is not available
            return {
                "context": "Knowledge base temporarily unavailable. Providing general medical information.",
                "sources": {"type": "error", "description": "Knowledge base connection failed"},
                "success": False,
                "message": "Using general medical knowledge - knowledge base connection failed"
            }
