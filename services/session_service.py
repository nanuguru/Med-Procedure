"""
Session and State Management Service
"""
from typing import Dict, Any, Optional
import uuid
import asyncio
from datetime import datetime
import structlog

logger = structlog.get_logger()


class InMemorySessionService:
    """
    In-memory session service for managing agent sessions and state
    """
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.lock = asyncio.Lock()
    
    async def create_session(self, initial_data: Optional[Dict[str, Any]] = None) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        async with self.lock:
            self.sessions[session_id] = {
                "session_id": session_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "created",
                "data": initial_data or {},
                "state": {},
                "history": []
            }
        logger.info("Session created", session_id=session_id)
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        async with self.lock:
            return self.sessions.get(session_id)
    
    async def update_session(
        self,
        session_id: str,
        data: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update session data"""
        async with self.lock:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            if data:
                session["data"].update(data)
            if status:
                session["status"] = status
            if state:
                session["state"].update(state)
            
            session["updated_at"] = datetime.utcnow().isoformat()
            return True
    
    async def add_to_history(self, session_id: str, entry: Dict[str, Any]) -> bool:
        """Add entry to session history"""
        async with self.lock:
            if session_id not in self.sessions:
                return False
            
            self.sessions[session_id]["history"].append({
                **entry,
                "timestamp": datetime.utcnow().isoformat()
            })
            return True
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        async with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info("Session deleted", session_id=session_id)
                return True
            return False
    
    async def list_sessions(self) -> list:
        """List all sessions"""
        async with self.lock:
            return list(self.sessions.keys())

