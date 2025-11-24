import asyncio
import logging
import time
import uuid
from typing import Dict, Any
from config.config import Config

class SessionManager:
    """Manages user sessions"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("butler.session")
        self.sessions = {}
        self.current_session_id = None
        
    async def initialize(self):
        """Initialize session manager"""
        self.logger.info("Session manager initialized")
        return True
    
    async def get_current_session(self) -> Dict[str, Any]:
        """Get or create current session"""
        if not self.current_session_id or self.current_session_id not in self.sessions:
            await self._create_new_session()
        
        session = self.sessions[self.current_session_id]
        
        # Check if session expired (1 hour)
        if time.time() - session['created_at'] > 3600:
            self.logger.info("Session expired, creating new one")
            await self._create_new_session()
            session = self.sessions[self.current_session_id]
        
        return session
    
    async def _create_new_session(self):
        """Create a new session"""
        session_id = str(uuid.uuid4())
        
        session = {
            'session_id': session_id,
            'created_at': time.time(),
            'last_activity': time.time(),
            'history': [],
            'current_services': None,
            'service_type': None,
            'location': None,
            'user_preferences': {}
        }
        
        self.sessions[session_id] = session
        self.current_session_id = session_id
        
        self.logger.info(f"New session created: {session_id}")
    
    async def update_session(self, session: Dict[str, Any]):
        """Update session data"""
        session['last_activity'] = time.time()
        self.sessions[session['session_id']] = session
    
    async def clear_current_session(self):
        """Clear current session"""
        if self.current_session_id:
            if self.current_session_id in self.sessions:
                del self.sessions[self.current_session_id]
            self.current_session_id = None
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session['last_activity'] > 3600:  # 1 hour
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    async def shutdown(self):
        """Cleanup resources"""
        self.logger.info(f"Shutting down session manager with {len(self.sessions)} active sessions")
        self.sessions.clear()