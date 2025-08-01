"""
Supabase Database Configuration for Medical AI Chatbot
This module handles all database operations using Supabase PostgreSQL.
"""

import os
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class SupabaseDB:
    """Supabase database handler for Medical AI Chatbot."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("✅ Supabase client initialized successfully")
    
    async def initialize(self):
        """Initialize database connection (for compatibility)."""
        # Test connection by making a simple query
        try:
            result = self.client.table('users').select('count', count='exact').execute()
            logger.info("✅ Supabase database connection verified")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            raise
    
    # User Management Operations
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user in the database."""
        try:
            # Prepare user data
            user_record = {
                "user_id": user_data["user_id"],
                "name": user_data["name"],
                "email": user_data["email"],
                "phone": user_data.get("phone"),
                "age": user_data.get("age"),
                "medical_conditions": user_data.get("medical_conditions"),
                "emergency_contact": user_data.get("emergency_contact"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_active": datetime.now(timezone.utc).isoformat(),
                "total_sessions": 0
            }
            
            # Add password_hash only if provided (for backward compatibility)
            if user_data.get("password_hash"):
                user_record["password_hash"] = user_data["password_hash"]
            
            # Insert user into database
            result = self.client.table('users').insert(user_record).execute()
            
            if result.data:
                logger.info(f"✅ User created successfully: {user_data['user_id']}")
                return user_data["user_id"]
            else:
                raise Exception("Failed to create user")
                
        except Exception as e:
            error_str = str(e)
            # If password_hash column doesn't exist, fall back to JSON file storage
            if "password_hash" in error_str and "could not find" in error_str.lower():
                logger.warning("⚠️ Supabase doesn't have password_hash column, falling back to JSON file storage")
                return await self._create_user_file_fallback(user_data)
            else:
                logger.error(f"❌ Error creating user: {error_str}")
                raise
    
    async def get_all_users(self) -> Dict[str, Any]:
        """Get all users from the database."""
        try:
            result = self.client.table('users').select('*').order('last_active', desc=True).execute()
            
            return {
                "users": result.data if result.data else [],
                "total_users": len(result.data) if result.data else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting users: {str(e)}")
            return {"users": [], "total_users": 0}
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific user by ID."""
        try:
            result = self.client.table('users').select('*').eq('user_id', user_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting user {user_id}: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a specific user by email."""
        try:
            result = self.client.table('users').select('*').eq('email', email).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            # If not found in Supabase, check file fallback
            return await self._get_user_by_email_file_fallback(email)
            
        except Exception as e:
            logger.error(f"❌ Error getting user by email {email}: {str(e)}")
            # Try file fallback on error
            return await self._get_user_by_email_file_fallback(email)
    
    async def authenticate_user(self, email: str, password_hash: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password hash."""
        try:
            # Get user by email
            user = await self.get_user_by_email(email)
            
            if user and user.get('password_hash') == password_hash:
                # Update last active
                await self.update_user(user['user_id'], {"last_active": datetime.now(timezone.utc).isoformat()})
                return user
            
            return None
            
        except Exception as e:
            error_str = str(e)
            # If there's an issue with the password_hash column, try file fallback
            if "password_hash" in error_str:
                logger.warning("⚠️ Using file fallback for authentication")
                return await self._authenticate_user_file_fallback(email, password_hash)
            else:
                logger.error(f"❌ Error authenticating user {email}: {error_str}")
                return None
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user information."""
        try:
            # Add last_active timestamp
            update_data["last_active"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table('users').update(update_data).eq('user_id', user_id).execute()
            
            if result.data:
                logger.info(f"✅ User updated successfully: {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Error updating user {user_id}: {str(e)}")
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user from the database."""
        try:
            result = self.client.table('users').delete().eq('user_id', user_id).execute()
            
            if result.data:
                logger.info(f"✅ User deleted successfully: {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Error deleting user {user_id}: {str(e)}")
            return False
    
    # Chat Session Operations
    async def create_chat_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new chat session."""
        try:
            session_record = {
                "session_id": session_data["session_id"],
                "user_id": session_data.get("user_id"),
                "project_id": session_data.get("project_id", "main"),
                "title": session_data.get("title"),
                "status": session_data.get("status", "active"),
                "messages": session_data.get("messages", []),  # Store as JSONB directly
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = self.client.table('chat_sessions').insert(session_record).execute()
            
            if result.data:
                logger.info(f"✅ Chat session created: {session_data['session_id']}")
                return session_data["session_id"]
            else:
                raise Exception("Failed to create chat session")
                
        except Exception as e:
            logger.error(f"❌ Error creating chat session: {str(e)}")
            raise
    
    async def get_all_sessions(self) -> Dict[str, Any]:
        """Get all chat sessions."""
        try:
            result = self.client.table('chat_sessions').select('*').order('created_at', desc=True).execute()
            
            # Handle messages field for each session
            sessions = []
            if result.data:
                for session in result.data:
                    session_copy = session.copy()
                    messages = session.get("messages", [])
                    if isinstance(messages, str):
                        try:
                            session_copy["messages"] = json.loads(messages)
                        except json.JSONDecodeError:
                            session_copy["messages"] = []
                    elif isinstance(messages, list):
                        session_copy["messages"] = messages
                    else:
                        session_copy["messages"] = []
                    sessions.append(session_copy)
            
            return {
                "sessions": sessions,
                "total_sessions": len(sessions)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting chat sessions: {str(e)}")
            return {"sessions": [], "total_sessions": 0}
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a specific user."""
        try:
            result = self.client.table('chat_sessions').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            
            # Handle messages field for each session
            sessions = []
            if result.data:
                for session in result.data:
                    session_copy = session.copy()
                    messages = session.get("messages", [])
                    if isinstance(messages, str):
                        try:
                            session_copy["messages"] = json.loads(messages)
                        except json.JSONDecodeError:
                            session_copy["messages"] = []
                    elif isinstance(messages, list):
                        session_copy["messages"] = messages
                    else:
                        session_copy["messages"] = []
                    sessions.append(session_copy)
            
            return sessions
            
        except Exception as e:
            logger.error(f"❌ Error getting user sessions for {user_id}: {str(e)}")
            return []
    
    async def get_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific session by ID."""
        try:
            result = self.client.table('chat_sessions').select('*').eq('session_id', session_id).execute()
            
            if result.data and len(result.data) > 0:
                session = result.data[0].copy()
                # Handle messages field - it might be stored as JSON string or JSONB
                messages = session.get("messages", [])
                if isinstance(messages, str):
                    try:
                        session["messages"] = json.loads(messages)
                    except json.JSONDecodeError:
                        session["messages"] = []
                elif isinstance(messages, list):
                    session["messages"] = messages
                else:
                    session["messages"] = []
                return session
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting session {session_id}: {str(e)}")
            return None
    
    async def update_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a chat session."""
        try:
            update_record = update_data.copy()
            
            # Handle messages field - store as JSONB directly
            if "messages" in update_record:
                messages = update_record["messages"]
                if isinstance(messages, list):
                    # Keep as list for JSONB storage
                    pass
                elif isinstance(messages, str):
                    try:
                        update_record["messages"] = json.loads(messages)
                    except json.JSONDecodeError:
                        update_record["messages"] = []
                else:
                    update_record["messages"] = []
            
            update_record["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table('chat_sessions').update(update_record).eq('session_id', session_id).execute()
            
            if result.data:
                logger.info(f"✅ Session updated successfully: {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Error updating session {session_id}: {str(e)}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        try:
            result = self.client.table('chat_sessions').delete().eq('session_id', session_id).execute()
            
            if result.data:
                logger.info(f"✅ Session deleted successfully: {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Error deleting session {session_id}: {str(e)}")
            return False
    
    # Project Configuration Operations
    async def get_project_config(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project configuration."""
        try:
            result = self.client.table('project_configs').select('*').eq('project_id', project_id).execute()
            
            if result.data and len(result.data) > 0:
                config = result.data[0].copy()
                # Parse JSON fields - but only if they're strings (not already parsed)
                for field in ['curated_sites', 'knowledge_base_files']:
                    if config.get(field):
                        # Check if it's already a list (JSONB field parsed by Supabase)
                        if isinstance(config[field], list):
                            # Already parsed, keep as is
                            pass
                        elif isinstance(config[field], str):
                            # String that needs JSON parsing
                            try:
                                config[field] = json.loads(config[field])
                            except json.JSONDecodeError:
                                config[field] = []
                        else:
                            # Other types, default to empty list
                            config[field] = []
                    else:
                        # Field doesn't exist or is None
                        config[field] = []
                return config
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting project config {project_id}: {str(e)}")
            return None
    
    async def update_project_config(self, project_id: str, config_data: Dict[str, Any]) -> bool:
        """Update or create project configuration."""
        try:
            # Convert lists to JSON strings for storage (only if needed)
            config_record = config_data.copy()
            for field in ['curated_sites', 'knowledge_base_files']:
                if field in config_record:
                    if isinstance(config_record[field], list):
                        # For Supabase JSONB, we can store lists directly
                        # No need to convert to JSON string
                        pass
                    elif isinstance(config_record[field], str):
                        try:
                            # If it's already a JSON string, parse it to list
                            config_record[field] = json.loads(config_record[field])
                        except json.JSONDecodeError:
                            # If JSON parsing fails, default to empty list
                            config_record[field] = []
                    else:
                        # For other types, default to empty list
                        config_record[field] = []
            
            config_record["project_id"] = project_id
            config_record["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Try to update first, then insert if not exists
            existing = await self.get_project_config(project_id)
            
            if existing:
                result = self.client.table('project_configs').update(config_record).eq('project_id', project_id).execute()
            else:
                config_record["created_at"] = datetime.now(timezone.utc).isoformat()
                result = self.client.table('project_configs').insert(config_record).execute()
            
            if result.data:
                logger.info(f"✅ Project config updated: {project_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Error updating project config {project_id}: {str(e)}")
            return False
    
    # Statistics Operations
    async def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            # Get user count
            users_result = await self.get_all_users()
            user_count = users_result["total_users"]
            
            # Get session count
            sessions_result = await self.get_all_sessions()
            session_count = sessions_result["total_sessions"]
            
            # Get project config for knowledge base and websites
            config = await self.get_project_config("main")
            knowledge_files = len(config.get("knowledge_base_files", [])) if config else 0
            curated_websites = len(config.get("curated_sites", [])) if config else 0
            
            return {
                "total_users": user_count,
                "total_sessions": session_count,
                "knowledge_base_files": knowledge_files,
                "curated_websites": curated_websites,
                "active_agents": 4  # Router, RAG, WebSearch, Safety
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting statistics: {str(e)}")
            return {
                "total_users": 0,
                "total_sessions": 0,
                "knowledge_base_files": 0,
                "curated_websites": 0,
                "active_agents": 4
            }
    
    async def _create_user_file_fallback(self, user_data: Dict[str, Any]) -> str:
        """Fallback method to create user in JSON file when Supabase column doesn't exist."""
        import json
        import os
        from datetime import datetime, timezone
        
        # Create users file if it doesn't exist
        users_file = os.path.join(os.path.dirname(__file__), "users_with_auth.json")
        
        # Load existing users
        users = {}
        if os.path.exists(users_file):
            try:
                with open(users_file, 'r') as f:
                    users = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                users = {}
        
        # Check if user already exists
        if user_data["email"] in [u.get("email") for u in users.values()]:
            raise Exception(f"User with email {user_data['email']} already exists")
        
        # Add timestamps if missing
        if "created_at" not in user_data:
            user_data["created_at"] = datetime.now(timezone.utc).isoformat()
        if "last_active" not in user_data:
            user_data["last_active"] = datetime.now(timezone.utc).isoformat()
        if "total_sessions" not in user_data:
            user_data["total_sessions"] = 0
        
        # Add new user
        users[user_data["user_id"]] = user_data
        
        # Save to file
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2, default=str)
        
        logger.info(f"✅ User created in file fallback: {user_data['user_id']}")
        return user_data["user_id"]
    
    async def _authenticate_user_file_fallback(self, email: str, password_hash: str):
        """Fallback method to authenticate user from JSON file."""
        import json
        import os
        
        users_file = os.path.join(os.path.dirname(__file__), "users_with_auth.json")
        
        if not os.path.exists(users_file):
            return None
        
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
            
            # Find user by email and check password
            for user_data in users.values():
                if user_data.get("email") == email and user_data.get("password_hash") == password_hash:
                    logger.info(f"✅ User authenticated from file: {email}")
                    return user_data
            
            return None
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    async def _get_user_by_email_file_fallback(self, email: str):
        """Fallback method to get user by email from JSON file."""
        import json
        import os
        
        users_file = os.path.join(os.path.dirname(__file__), "users_with_auth.json")
        
        if not os.path.exists(users_file):
            return None
        
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
            
            # Find user by email
            for user_data in users.values():
                if user_data.get("email") == email:
                    logger.info(f"✅ User found in file: {email}")
                    return user_data
            
            return None
        except (json.JSONDecodeError, FileNotFoundError):
            return None

# Global database instance
db_instance = None

def get_database() -> SupabaseDB:
    """Get the global database instance."""
    global db_instance
    if db_instance is None:
        db_instance = SupabaseDB()
    return db_instance
