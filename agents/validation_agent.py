"""
Validation Agent - Validates and enhances procedures
"""
from typing import Dict, Any
import structlog
from agents.base_agent import BaseAgent
from tools.custom_tools import (
    ProcedureValidatorTool,
    ContextEnhancerTool,
    EquipmentCheckerTool
)

logger = structlog.get_logger()


class ValidationAgent(BaseAgent):
    """Agent responsible for validating and enhancing procedures"""
    
    def __init__(self, agent_id: str = "validation_agent_1"):
        super().__init__(agent_id, "validation")
        self.validator = ProcedureValidatorTool()
        self.enhancer = ContextEnhancerTool()
        self.equipment_checker = EquipmentCheckerTool()
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation and enhancement"""
        self.status = "validating"
        self.log_action("start_validation", input_data)
        
        try:
            procedure = input_data.get("procedure", {})
            setting = input_data.get("setting", "Hospital")
            
            if not procedure:
                raise ValueError("procedure is required")
            
            # Validate procedure
            validation = self.validator.validate(procedure, setting)
            
            # Enhance with context
            enhanced = self.enhancer.enhance(procedure, setting)
            
            # Check equipment
            equipment_info = self.equipment_checker.check_equipment(procedure, setting)
            
            self.status = "completed"
            self.log_action("validation_completed")
            
            return {
                "success": True,
                "agent_id": self.agent_id,
                "validation": validation,
                "enhanced_procedure": enhanced,
                "equipment": equipment_info
            }
            
        except Exception as e:
            self.status = "error"
            self.log_action("validation_error", {"error": str(e)})
            logger.error("Validation agent error", error=str(e), exc_info=True)
            return {
                "success": False,
                "agent_id": self.agent_id,
                "error": str(e)
            }

