"""
Custom Tools for NurseSOP Live
"""
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger()


class ProcedureValidatorTool:
    """Tool to validate clinical procedures"""
    
    def validate(self, procedure: Dict[str, Any], setting: str) -> Dict[str, Any]:
        """
        Validate procedure for safety and completeness
        
        Args:
            procedure: Procedure data to validate
            setting: Hospital or Home setting
        """
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "safety_score": 1.0
        }
        
        # Check for required fields
        required_fields = ["service_name", "procedures"]
        for field in required_fields:
            if field not in procedure:
                validation_results["errors"].append(f"Missing required field: {field}")
                validation_results["valid"] = False
        
        # Setting-specific validation
        if setting.lower() == "home":
            # Check for equipment requirements
            if "equipment" in procedure:
                equipment = procedure["equipment"]
                if isinstance(equipment, list) and len(equipment) > 5:
                    validation_results["warnings"].append(
                        "Home setting may have limited equipment availability"
                    )
                    validation_results["safety_score"] -= 0.1
        
        # Safety checks
        safety_keywords = ["sterile", "disinfect", "gloves", "safety", "precautions"]
        procedure_text = str(procedure.get("procedures", "")).lower()
        
        safety_found = sum(1 for keyword in safety_keywords if keyword in procedure_text)
        if safety_found < 2:
            validation_results["warnings"].append(
                "Procedure may be missing important safety considerations"
            )
            validation_results["safety_score"] -= 0.2
        
        validation_results["safety_score"] = max(0.0, validation_results["safety_score"])
        
        return validation_results


class ContextEnhancerTool:
    """Tool to enhance context based on setting"""
    
    def enhance(self, procedure: Dict[str, Any], setting: str) -> Dict[str, Any]:
        """
        Enhance procedure with setting-specific context
        
        Args:
            procedure: Procedure data
            setting: Hospital or Home setting
        """
        enhanced = procedure.copy()
        
        if setting.lower() == "home":
            enhanced["context"] = {
                "environment": "Patient's residence",
                "equipment_availability": "Limited",
                "support_staff": "Minimal",
                "considerations": [
                    "Ensure adequate lighting",
                    "Maintain privacy",
                    "Have emergency contact information available",
                    "Consider patient comfort and home environment"
                ]
            }
        else:  # Hospital
            enhanced["context"] = {
                "environment": "Clinical facility",
                "equipment_availability": "Full",
                "support_staff": "Available",
                "considerations": [
                    "Follow hospital protocols",
                    "Use sterile techniques",
                    "Document in medical records",
                    "Coordinate with healthcare team"
                ]
            }
        
        return enhanced


class EquipmentCheckerTool:
    """Tool to check equipment requirements"""
    
    def check_equipment(
        self,
        procedure: Dict[str, Any],
        setting: str
    ) -> Dict[str, Any]:
        """
        Check equipment requirements for procedure
        
        Args:
            procedure: Procedure data
            setting: Hospital or Home setting
        """
        equipment_list = []
        
        # Extract equipment from procedure text
        procedure_text = str(procedure.get("procedures", "")).lower()
        
        # Common medical equipment
        common_equipment = [
            "gloves", "syringe", "needle", "gauze", "bandage",
            "alcohol swab", "stethoscope", "blood pressure cuff",
            "thermometer", "sterile field", "disinfectant"
        ]
        
        for equipment in common_equipment:
            if equipment in procedure_text:
                equipment_list.append(equipment)
        
        result = {
            "required_equipment": equipment_list,
            "setting": setting,
            "availability": "full" if setting.lower() == "hospital" else "limited",
            "recommendations": []
        }
        
        if setting.lower() == "home" and len(equipment_list) > 5:
            result["recommendations"].append(
                "Consider preparing equipment checklist before procedure"
            )
        
        return result

