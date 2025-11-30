"""
Base Agent Class for Multi-Agent System
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

logger = structlog.get_logger()


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.status = "idle"
        self.history: List[Dict[str, Any]] = []
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task"""
        pass
    
    def log_action(self, action: str, data: Optional[Dict[str, Any]] = None):
        """Log agent action"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "action": action,
            "data": data or {}
        }
        self.history.append(entry)
        logger.info("Agent action", **entry)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "history_count": len(self.history)
        }

