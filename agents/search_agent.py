"""
Search Agent - LLM-powered agent for searching procedures
"""
from typing import Dict, Any
import structlog
from agents.base_agent import BaseAgent
from tools.search_tools import HybridSearchTool
from config import settings

logger = structlog.get_logger()


class SearchAgent(BaseAgent):
    """Agent responsible for searching clinical procedures"""
    
    def __init__(self, agent_id: str = "search_agent_1"):
        super().__init__(agent_id, "search")
        self.search_tool = HybridSearchTool()
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search for clinical procedures"""
        self.status = "searching"
        self.log_action("start_search", input_data)
        
        try:
            service_name = input_data.get("service_name", "")
            setting = input_data.get("setting", "Hospital")
            
            if not service_name:
                raise ValueError("service_name is required")
            
            # Perform search
            results = await self.search_tool.search(
                service_name=service_name,
                setting=setting
            )
            
            self.status = "completed"
            self.log_action("search_completed", {"success": results.get("success", False)})
            
            return {
                "success": True,
                "agent_id": self.agent_id,
                "results": results,
                "service_name": service_name,
                "setting": setting
            }
            
        except Exception as e:
            self.status = "error"
            self.log_action("search_error", {"error": str(e)})
            logger.error("Search agent error", error=str(e), exc_info=True)
            return {
                "success": False,
                "agent_id": self.agent_id,
                "error": str(e)
            }

