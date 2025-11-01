"""
Orchestrator Routes Module
Handles workflow orchestration and coordination endpoints
"""

from fastapi import APIRouter, HTTPException

# Import models
try:
    from orchestrator_schema import OrchestratorRequest, OrchestratorResponse
except ImportError:
    from backend.orchestrator_schema import OrchestratorRequest, OrchestratorResponse

# Import core services
try:
    from core.services.ai_service import ai_service
    from core.error_handling import error_handler, handle_errors
except ImportError:
    from backend.core.services.ai_service import ai_service
    from backend.core.error_handling import error_handler, handle_errors

router = APIRouter()

@router.post("", response_model=OrchestratorResponse)
@handle_errors("orchestration")
def orchestrate(request: OrchestratorRequest):
    """Orchestrate complex workflows involving multiple AI agents"""
    results = ai_service.orchestrate_workflow(
        user_id=request.user_id,
        goal=request.goal,
        resume_text=request.resume_text,
        code=request.code,
        interview_answers=request.interview_answers
    )
    
    return OrchestratorResponse(**results)
