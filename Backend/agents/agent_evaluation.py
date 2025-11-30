"""
Agent Evaluation - Evaluates agent performance and output quality
"""
from typing import Dict, Any, List
import structlog
from datetime import datetime

logger = structlog.get_logger()


class AgentEvaluator:
    """Evaluates agent performance and output quality"""
    
    def __init__(self):
        self.evaluations: List[Dict[str, Any]] = []
    
    def evaluate_agent_output(
        self,
        agent_id: str,
        agent_type: str,
        output: Dict[str, Any],
        expected_fields: List[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate agent output quality
        
        Args:
            agent_id: ID of the agent
            agent_type: Type of agent
            output: Agent output to evaluate
            expected_fields: List of expected fields in output
        """
        evaluation = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "timestamp": datetime.utcnow().isoformat(),
            "scores": {},
            "overall_score": 0.0,
            "recommendations": []
        }
        
        # Check success
        success = output.get("success", False)
        evaluation["scores"]["success"] = 1.0 if success else 0.0
        
        # Check completeness
        if expected_fields:
            completeness = self._check_completeness(output, expected_fields)
            evaluation["scores"]["completeness"] = completeness
        else:
            evaluation["scores"]["completeness"] = 1.0
        
        # Check for errors
        has_error = "error" in output
        evaluation["scores"]["error_free"] = 0.0 if has_error else 1.0
        
        # Calculate overall score
        scores = evaluation["scores"]
        evaluation["overall_score"] = (
            scores.get("success", 0) * 0.4 +
            scores.get("completeness", 0) * 0.4 +
            scores.get("error_free", 0) * 0.2
        )
        
        # Generate recommendations
        if evaluation["overall_score"] < 0.7:
            evaluation["recommendations"].append(
                "Consider improving output quality or error handling"
            )
        
        if scores.get("completeness", 1.0) < 0.8:
            evaluation["recommendations"].append(
                "Output may be missing important fields"
            )
        
        self.evaluations.append(evaluation)
        logger.info("Agent evaluated", agent_id=agent_id, score=evaluation["overall_score"])
        
        return evaluation
    
    def _check_completeness(
        self,
        output: Dict[str, Any],
        expected_fields: List[str]
    ) -> float:
        """Check completeness of output fields"""
        present_fields = sum(1 for field in expected_fields if field in output)
        return present_fields / len(expected_fields) if expected_fields else 1.0
    
    def evaluate_workflow(
        self,
        workflow_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate entire workflow"""
        workflow_evaluation = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_count": len(workflow_results),
            "successful_agents": sum(1 for r in workflow_results if r.get("success")),
            "overall_success": all(r.get("success") for r in workflow_results),
            "agent_scores": []
        }
        
        for result in workflow_results:
            agent_score = {
                "agent_id": result.get("agent_id"),
                "success": result.get("success", False)
            }
            workflow_evaluation["agent_scores"].append(agent_score)
        
        return workflow_evaluation
    
    def get_evaluation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get evaluation history"""
        return self.evaluations[-limit:]

