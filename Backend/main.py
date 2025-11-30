"""
Med Procedure - Main FastAPI Application
AI-agent system for nurses and certified home-health caregivers
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import structlog
import asyncio
from contextlib import asynccontextmanager

from config import settings
from agents.agent_orchestrator import AgentOrchestrator
from services.session_service import InMemorySessionService
from services.memory_bank import MemoryBank
from observability.logging import setup_logging
from observability.metrics import setup_metrics
from observability.tracing import setup_tracing

# Setup logging
logger = setup_logging()

# Setup metrics
metrics = setup_metrics()

# Setup tracing
setup_tracing()

# Initialize services
session_service = InMemorySessionService()
memory_bank = MemoryBank(max_size=settings.memory_bank_size)

# Initialize agent orchestrator
agent_orchestrator = AgentOrchestrator(
    session_service=session_service,
    memory_bank=memory_bank,
    metrics=metrics
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Med Procedure application")
    yield
    logger.info("Shutting down Med Procedure application")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ServiceRequest(BaseModel):
    """Request model for service procedure lookup"""
    user_text: str = Field(..., description="Service name or procedure name")
    setting: str = Field(..., description="Either 'Home' or 'Hospital'")


class ServiceResponse(BaseModel):
    """Response model for service procedure"""
    session_id: str
    service_name: str
    setting: str
    procedures: Dict[str, Any]
    status: str
    message: Optional[str] = None


class SessionStatusResponse(BaseModel):
    """Response model for session status"""
    session_id: str
    status: str
    progress: Optional[float] = None
    result: Optional[Dict[str, Any]] = None




@app.post("/procedures", response_model=ServiceResponse)
async def get_procedures(
    request: ServiceRequest,
    background_tasks: BackgroundTasks
):
    """
    Get clinical procedures for a given service name in Hospital or Home setting
    
    - **user_text**: Name of the service/procedure
    - **setting**: Either "Home" or "Hospital"
    """
    try:
        # Validate setting
        if request.setting.lower() not in ["home", "hospital"]:
            raise HTTPException(
                status_code=400,
                detail="Setting must be either 'Home' or 'Hospital'"
            )
        
        logger.info(
            "Processing procedure request",
            service=request.user_text,
            setting=request.setting
        )
        
        # Create session and start agent workflow
        session_id = await agent_orchestrator.create_session()
        
        # Create background task and track it
        async def process_with_error_handling():
            try:
                await agent_orchestrator.process_service_request(
                    session_id=session_id,
                    service_name=request.user_text,
                    setting=request.setting
                )
            except Exception as e:
                logger.error("Background task error", session_id=session_id, error=str(e), exc_info=True)
                await session_service.update_session(
                    session_id,
                    status="error",
                    data={"error": str(e), "error_type": type(e).__name__}
                )
        
        task = asyncio.create_task(process_with_error_handling())
        agent_orchestrator.running_operations[session_id] = task
        
        # Return initial response
        return ServiceResponse(
            session_id=session_id,
            service_name=request.user_text,
            setting=request.setting,
            procedures={},
            status="processing",
            message="Request is being processed. Use session_id to check status."
        )
        
    except Exception as e:
        logger.error("Error processing request", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """Get the status of a processing session"""
    try:
        session_data = await session_service.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get result from data field
        session_data_dict = session_data.get("data", {})
        result = session_data_dict.get("result")
        progress = session_data_dict.get("progress")
        
        return SessionStatusResponse(
            session_id=session_id,
            status=session_data.get("status", "unknown"),
            progress=progress,
            result=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting session status", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sessions/{session_id}/pause") 
async def pause_session(session_id: str):
    """Pause a long-running agent operation"""
    try:
        success = await agent_orchestrator.pause_operation(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found or cannot be paused")
        return {"status": "paused", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error pausing session", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sessions/{session_id}/resume")
async def resume_session(session_id: str):
    """Resume a paused agent operation"""
    try:
        success = await agent_orchestrator.resume_operation(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found or cannot be resumed")
        return {"status": "resumed", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error resuming session", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    return metrics.get_metrics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level=settings.log_level.lower()
    )

