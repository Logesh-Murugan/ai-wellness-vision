# session_manager.py - Streamlit session management
import streamlit as st
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions and authentication state in Streamlit"""
    
    def __init__(self):
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        
        if 'user_info' not in st.session_state:
            st.session_state.user_info = {}
        
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
        
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {
                'language': 'en',
                'theme': 'light',
                'voice_enabled': True,
                'notifications': True
            }
        
        if 'last_activity' not in st.session_state:
            st.session_state.last_activity = datetime.now()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        # Check session timeout (30 minutes)
        if st.session_state.authenticated:
            time_since_activity = datetime.now() - st.session_state.last_activity
            if time_since_activity > timedelta(minutes=30):
                self.logout()
                return False
            
            # Update last activity
            st.session_state.last_activity = datetime.now()
        
        return st.session_state.authenticated
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user with credentials"""
        try:
            # Simple demo authentication - replace with real auth in production
            demo_users = {
                "admin": {"password": "admin123", "email": "admin@wellnessvision.ai", "roles": ["admin", "user"]},
                "testuser": {"password": "user123", "email": "test@wellnessvision.ai", "roles": ["user"]},
                "demo": {"password": "demo", "email": "demo@wellnessvision.ai", "roles": ["user"]}
            }
            
            if username in demo_users and demo_users[username]["password"] == password:
                user_data = demo_users[username]
                
                # Store user info in session
                st.session_state.authenticated = True
                st.session_state.user_info = {
                    'username': username,
                    'email': user_data["email"],
                    'roles': user_data["roles"],
                    'access_token': f"demo_token_{username}"
                }
                st.session_state.last_activity = datetime.now()
                
                logger.info(f"User authenticated: {username}")
                return True
            else:
                logger.warning(f"Authentication failed for user: {username}")
                return False
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def logout(self):
        """Logout user and clear session"""
        st.session_state.authenticated = False
        st.session_state.user_info = {}
        st.session_state.conversation_history = []
        st.session_state.analysis_history = []
        logger.info("User logged out")
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        return st.session_state.user_info
    
    def get_session_id(self) -> str:
        """Get current session ID"""
        return st.session_state.session_id
    
    def add_conversation(self, user_message: str, ai_response: str, 
                        message_type: str = "text", metadata: Dict = None):
        """Add conversation to history"""
        conversation_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now(),
            'user_message': user_message,
            'ai_response': ai_response,
            'message_type': message_type,
            'metadata': metadata or {}
        }
        
        st.session_state.conversation_history.append(conversation_entry)
        
        # Keep only last 100 conversations
        if len(st.session_state.conversation_history) > 100:
            st.session_state.conversation_history = st.session_state.conversation_history[-100:]
    
    def add_analysis(self, analysis_type: str, result: Dict[str, Any], 
                    image_path: str = None):
        """Add analysis to history"""
        analysis_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now(),
            'analysis_type': analysis_type,
            'result': result,
            'image_path': image_path
        }
        
        st.session_state.analysis_history.append(analysis_entry)
        
        # Keep only last 50 analyses
        if len(st.session_state.analysis_history) > 50:
            st.session_state.analysis_history = st.session_state.analysis_history[-50:]
    
    def get_conversation_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get conversation history"""
        history = st.session_state.conversation_history
        if limit:
            return history[-limit:]
        return history
    
    def get_analysis_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get analysis history"""
        history = st.session_state.analysis_history
        if limit:
            return history[-limit:]
        return history
    
    def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics"""
        return {
            'total_conversations': len(st.session_state.conversation_history),
            'total_analyses': len(st.session_state.analysis_history),
            'total_chats': len([c for c in st.session_state.conversation_history 
                              if c.get('message_type') == 'text']),
            'total_voice_interactions': len([c for c in st.session_state.conversation_history 
                                           if c.get('message_type') == 'voice'])
        }
    
    def update_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences"""
        st.session_state.user_preferences.update(preferences)
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        return st.session_state.user_preferences
    
    def clear_history(self, history_type: str = "all"):
        """Clear conversation or analysis history"""
        if history_type in ["all", "conversations"]:
            st.session_state.conversation_history = []
        
        if history_type in ["all", "analyses"]:
            st.session_state.analysis_history = []
        
        logger.info(f"Cleared {history_type} history")
    
    def export_data(self) -> Dict[str, Any]:
        """Export user data for download"""
        return {
            'user_info': st.session_state.user_info,
            'session_id': st.session_state.session_id,
            'conversation_history': st.session_state.conversation_history,
            'analysis_history': st.session_state.analysis_history,
            'preferences': st.session_state.user_preferences,
            'export_timestamp': datetime.now().isoformat()
        }