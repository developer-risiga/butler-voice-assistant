import asyncio
import logging
import time
import uuid
from typing import Dict, Any, Optional
from config.config import Config
from .session_manager import SessionManager
from .response_builder import ResponseBuilder

class ConversationManager:
    """Manages conversation state and context"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("butler.conversation")
        self.session_manager = SessionManager()
        self.response_builder = ResponseBuilder()
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize conversation manager"""
        self.logger.info("Initializing conversation manager...")
        
        try:
            await self.session_manager.initialize()
            self.is_initialized = True
            self.logger.info("✅ Conversation manager initialized")
            return True
        except Exception as e:
            self.logger.error(f"❌ Conversation manager initialization failed: {e}")
            return False
    
    async def update_context(self, user_input: str, system_response: str, data: Dict = None) -> Dict[str, Any]:
        """Update conversation context with new interaction"""
        session = await self.session_manager.get_current_session()
        
        # Update conversation history
        session['history'].append({
            'timestamp': time.time(),
            'user': user_input,
            'system': system_response
        })
        
        # Keep only last 5 interactions
        session['history'] = session['history'][-5:]
        
        # Update context data
        if data and 'vendors' in data:
            session['current_services'] = data['vendors']
            session['service_type'] = data.get('service_type')
            session['location'] = data.get('location')
        
        session['last_activity'] = time.time()
        
        await self.session_manager.update_session(session)
        return session
    
    async def get_context(self) -> Dict[str, Any]:
        """Get current conversation context"""
        return await self.session_manager.get_current_session()
    
    async def clear_context(self):
        """Clear current conversation context"""
        await self.session_manager.clear_current_session()
        self.logger.info("Conversation context cleared")
    
    async def format_response(self, intent: str, entities: Dict, context: Dict) -> str:
        """Format response based on intent and context"""
        return await self.response_builder.build_response(intent, entities, context)
    
    async def shutdown(self):
        """Cleanup resources"""
        await self.session_manager.shutdown()
        self.logger.info("Conversation manager shut down")