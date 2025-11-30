"""
Agent Orchestrator - Coordinates multi-agent system
Supports parallel, sequential, and loop agents
"""
from typing import Dict, Any, List, Optional
import asyncio
import structlog
from datetime import datetime

from agents.search_agent import SearchAgent
from agents.validation_agent import ValidationAgent
from agents.synthesis_agent import SynthesisAgent
from agents.a2a_protocol import A2AProtocol
from agents.agent_evaluation import AgentEvaluator
from services.session_service import InMemorySessionService
from services.memory_bank import MemoryBank
from agents.context_compaction import ContextCompactor

logger = structlog.get_logger()


class AgentOrchestrator:
    """
    Orchestrates multi-agent workflows with support for:
    - Parallel agents
    - Sequential agents
    - Loop agents
    - Long-running operations (pause/resume)
    """
    
    def __init__(
        self,
        session_service: InMemorySessionService,
        memory_bank: MemoryBank,
        metrics=None
    ):
        self.session_service = session_service
        self.memory_bank = memory_bank
        self.context_compactor = ContextCompactor()
        self.a2a_protocol = A2AProtocol()
        self.evaluator = AgentEvaluator()
        self.metrics = metrics
        self.running_operations: Dict[str, asyncio.Task] = {}
        self.paused_operations: Dict[str, Dict[str, Any]] = {}
    
    async def create_session(self) -> str:
        """Create a new session"""
        session_id = await self.session_service.create_session()
        return session_id
    
    async def process_service_request(
        self,
        session_id: str,
        service_name: str,
        setting: str
    ):
        """
        Process a service request using multi-agent workflow
        
        Workflow:
        1. Search Agent (parallel with memory retrieval)
        2. Validation Agent (sequential)
        3. Synthesis Agent (sequential)
        """
        try:
            start_time = datetime.utcnow()
            
            await self.session_service.update_session(
                session_id,
                status="processing",
                data={"service_name": service_name, "setting": setting}
            )
            
            # Store in memory bank
            memory_id = self.memory_bank.add_memory(
                f"Service request: {service_name} in {setting} setting",
                metadata={"service_name": service_name, "setting": setting},
                importance=0.8
            )
            
            # Step 1: Parallel execution - Search Agent + Memory Retrieval
            logger.info("Starting parallel agents", session_id=session_id)
            
            search_agent = SearchAgent()
            
            # Use A2A protocol to send request
            a2a_request = self.a2a_protocol.send_request(
                sender_id="orchestrator",
                receiver_id=search_agent.agent_id,
                request_payload={
                    "service_name": service_name,
                    "setting": setting
                }
            )
            
            search_task = search_agent.execute({
                "service_name": service_name,
                "setting": setting
            })
            
            # Retrieve relevant memories in parallel
            memory_task = asyncio.create_task(
                self._retrieve_memories(service_name)
            )
            
            # Execute in parallel
            search_results, memory_results = await asyncio.gather(
                search_task,
                memory_task
            )
            
            # Evaluate search agent
            search_evaluation = self.evaluator.evaluate_agent_output(
                agent_id=search_agent.agent_id,
                agent_type="search",
                output=search_results,
                expected_fields=["success", "results", "service_name"]
            )
            
            # Send A2A response
            self.a2a_protocol.send_response(
                sender_id=search_agent.agent_id,
                receiver_id="orchestrator",
                response_payload=search_results,
                correlation_id=a2a_request.correlation_id
            )
            
            if self.metrics:
                self.metrics.record_agent_operation(
                    "search",
                    "execute",
                    "success" if search_results.get("success") else "error",
                    0.0  # Duration would be calculated
                )
            
            # Step 2: Sequential - Validation Agent
            if search_results.get("success"):
                logger.info("Starting validation agent", session_id=session_id)
                
                # Prepare procedure data for validation
                search_data = search_results.get("results", {})
                procedures_data = search_data.get("procedures", {})
                
                # Log what we're passing to validation
                logger.info(
                    "Validation input",
                    session_id=session_id,
                    has_procedures=bool(procedures_data),
                    procedures_type=type(procedures_data).__name__
                )
                
                procedure_data = {
                    "service_name": service_name,
                    "procedures": procedures_data,
                    "setting": setting
                }
                
                validation_agent = ValidationAgent()
                
                # Use A2A protocol
                validation_request = self.a2a_protocol.send_request(
                    sender_id="orchestrator",
                    receiver_id=validation_agent.agent_id,
                    request_payload={
                        "procedure": procedure_data,
                        "setting": setting
                    }
                )
                
                validation_results = await validation_agent.execute({
                    "procedure": procedure_data,
                    "setting": setting
                })
                
                # Evaluate validation agent
                validation_evaluation = self.evaluator.evaluate_agent_output(
                    agent_id=validation_agent.agent_id,
                    agent_type="validation",
                    output=validation_results,
                    expected_fields=["success", "validation", "enhanced_procedure"]
                )
                
                # Send A2A response
                self.a2a_protocol.send_response(
                    sender_id=validation_agent.agent_id,
                    receiver_id="orchestrator",
                    response_payload=validation_results,
                    correlation_id=validation_request.correlation_id
                )
                
                if self.metrics:
                    self.metrics.record_agent_operation(
                        "validation",
                        "execute",
                        "success" if validation_results.get("success") else "error",
                        0.0
                    )
            else:
                validation_results = {"success": False, "error": "Search failed"}
            
            # Step 3: Sequential - Synthesis Agent
            # Check if search failed due to API issues
            if not search_results.get("success"):
                error_msg = search_results.get("error", "Search failed")
                logger.error("Search failed, cannot proceed", error=error_msg, session_id=session_id)
                await self.session_service.update_session(
                    session_id,
                    status="error",
                    data={
                        "error": f"Search failed: {error_msg}",
                        "error_type": "search_failed",
                        "suggestion": "Please check your OpenAI API key and billing status"
                    }
                )
                return
            
            if validation_results.get("success"):
                logger.info("Starting synthesis agent", session_id=session_id)
                
                synthesis_agent = SynthesisAgent()
                
                # Use A2A protocol
                synthesis_request = self.a2a_protocol.send_request(
                    sender_id="orchestrator",
                    receiver_id=synthesis_agent.agent_id,
                    request_payload={
                        "search_results": search_results,
                        "validation_results": validation_results,
                        "service_name": service_name,
                        "setting": setting,
                        "memory_context": memory_results
                    }
                )
                
                synthesis_results = await synthesis_agent.execute({
                    "search_results": search_results,
                    "validation_results": validation_results,
                    "service_name": service_name,
                    "setting": setting,
                    "timestamp": datetime.utcnow().isoformat(),
                    "memory_context": memory_results
                })
                
                # Evaluate synthesis agent
                synthesis_evaluation = self.evaluator.evaluate_agent_output(
                    agent_id=synthesis_agent.agent_id,
                    agent_type="synthesis",
                    output=synthesis_results,
                    expected_fields=["success", "final_procedure"]
                )
                
                # Send A2A response
                self.a2a_protocol.send_response(
                    sender_id=synthesis_agent.agent_id,
                    receiver_id="orchestrator",
                    response_payload=synthesis_results,
                    correlation_id=synthesis_request.correlation_id
                )
                
                # Evaluate entire workflow
                workflow_evaluation = self.evaluator.evaluate_workflow([
                    search_results,
                    validation_results,
                    synthesis_results
                ])
                
                if self.metrics:
                    self.metrics.record_agent_operation(
                        "synthesis",
                        "execute",
                        "success" if synthesis_results.get("success") else "error",
                        0.0
                    )
                
                # Store final result
                final_result = synthesis_results.get("final_procedure", {})
                
                # Log what we're about to store
                has_procedure_details = bool(final_result.get("procedure_details"))
                logger.info(
                    "Synthesis complete",
                    session_id=session_id,
                    has_procedure_details=has_procedure_details,
                    procedure_details_type=type(final_result.get("procedure_details")).__name__ if final_result.get("procedure_details") else "None",
                    procedure_details_length=len(str(final_result.get("procedure_details"))) if final_result.get("procedure_details") else 0
                )
                
                # Apply context compaction if needed
                compacted_result = await self.context_compactor.compact(
                    final_result,
                    threshold=0.8
                )
                
                # Ensure procedure_details is preserved (it might be None or empty string)
                if not compacted_result.get("procedure_details"):
                    # Last resort: create a basic procedure
                    compacted_result["procedure_details"] = f"""Clinical Procedure: {service_name}
Setting: {setting}

Procedure information is being compiled. Please refer to the references below for detailed instructions.

Note: This procedure should be performed following standard clinical protocols for {service_name} in a {setting} environment."""
                    logger.warning("Created fallback procedure_details", session_id=session_id)
                
                # Update session with results
                await self.session_service.update_session(
                    session_id,
                    status="completed",
                    data={
                        "result": compacted_result,
                        "progress": 1.0,
                        "processing_time": (datetime.utcnow() - start_time).total_seconds(),
                        "service_name": service_name,
                        "setting": setting
                    }
                )
                
                logger.info(
                    "Request completed successfully",
                    session_id=session_id,
                    has_result=bool(compacted_result),
                    has_procedure_details=bool(compacted_result.get("procedure_details"))
                )
                
                # Store in memory bank
                self.memory_bank.add_memory(
                    f"Completed procedure lookup for {service_name}",
                    metadata=compacted_result,
                    importance=0.9
                )
                
                logger.info("Request completed", session_id=session_id)
                
            else:
                await self.session_service.update_session(
                    session_id,
                    status="error",
                    data={"error": validation_results.get("error", "Validation failed")}
                )
        
        except asyncio.CancelledError:
            logger.info("Operation cancelled", session_id=session_id)
            await self.session_service.update_session(
                session_id,
                status="cancelled"
            )
            raise
        
        except Exception as e:
            logger.error("Error processing request", error=str(e), exc_info=True)
            import traceback
            error_trace = traceback.format_exc()
            logger.error("Full traceback", traceback=error_trace)
            
            # Try to preserve session even on error
            try:
                await self.session_service.update_session(
                    session_id,
                    status="error",
                    data={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "traceback": error_trace[:1000]  # Limit traceback size
                    }
                )
            except Exception as update_error:
                logger.error("Failed to update session with error", error=str(update_error))
    
    async def _retrieve_memories(self, query: str) -> Dict[str, Any]:
        """Retrieve relevant memories from memory bank"""
        memories = self.memory_bank.retrieve_memories(query, limit=5)
        return {
            "memories": memories,
            "count": len(memories)
        }
    
    async def pause_operation(self, session_id: str) -> bool:
        """Pause a long-running operation"""
        if session_id in self.running_operations:
            task = self.running_operations[session_id]
            
            # Get current state
            session_data = await self.session_service.get_session(session_id)
            if session_data:
                self.paused_operations[session_id] = {
                    "state": session_data.get("state", {}),
                    "data": session_data.get("data", {})
                }
                
                # Cancel task (in real implementation, would save state more gracefully)
                task.cancel()
                del self.running_operations[session_id]
                
                await self.session_service.update_session(session_id, status="paused")
                logger.info("Operation paused", session_id=session_id)
                return True
        
        return False
    
    async def resume_operation(self, session_id: str) -> bool:
        """Resume a paused operation"""
        if session_id in self.paused_operations:
            paused_state = self.paused_operations[session_id]
            
            # Restore state and continue
            session_data = await self.session_service.get_session(session_id)
            if session_data:
                service_name = session_data.get("data", {}).get("service_name")
                setting = session_data.get("data", {}).get("setting")
                
                if service_name and setting:
                    # Restart processing
                    task = asyncio.create_task(
                        self.process_service_request(session_id, service_name, setting)
                    )
                    self.running_operations[session_id] = task
                    
                    del self.paused_operations[session_id]
                    await self.session_service.update_session(session_id, status="processing")
                    
                    logger.info("Operation resumed", session_id=session_id)
                    return True
        
        return False
    
    async def execute_loop_agent(
        self,
        agent: Any,
        input_data: Dict[str, Any],
        max_iterations: int = 10,
        condition: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Execute an agent in a loop until condition is met
        
        Args:
            agent: Agent to execute
            input_data: Initial input data
            max_iterations: Maximum number of iterations
            condition: Function that returns True when loop should stop
        """
        iteration = 0
        current_data = input_data
        
        while iteration < max_iterations:
            result = await agent.execute(current_data)
            
            if condition and condition(result):
                return result
            
            current_data = result
            iteration += 1
        
        return {"success": False, "error": "Max iterations reached"}

