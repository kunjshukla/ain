# routes/async_processing.py - FastAPI routes for asynchronous resume processing
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import uuid

# Import Celery tasks
from tasks import (
    submit_resume_for_processing, 
    get_task_status, 
    process_resume_file,
    get_resume_analysis,
    health_check,
    analyze_resume  # Add the new task
)
from services.resume_parser import resume_parser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/async", tags=["Asynchronous Processing"])

# Request/Response Models
class ProcessResumeRequest(BaseModel):
    resume_text: str
    metadata: Optional[Dict[str, Any]] = None

class TaskStatusResponse(BaseModel):
    task_id: str
    state: str
    progress: int
    stage: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ProcessingResponse(BaseModel):
    success: bool
    task_id: str
    message: str
    tracking_url: str

class AnalyzeResumeRequest(BaseModel):
    resume_text: str

@router.post("/process-resume-text", response_model=ProcessingResponse)
async def process_resume_text_async(request: ProcessResumeRequest):
    """
    Submit resume text for asynchronous processing with Ollama and MongoDB
    
    Args:
        request: Resume text and optional metadata
        
    Returns:
        Task ID for tracking processing status
    """
    try:
        if not request.resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Resume text cannot be empty"
            )
        
        # Submit task for processing
        task_id = submit_resume_for_processing(
            resume_text=request.resume_text,
            metadata=request.metadata
        )
        
        return ProcessingResponse(
            success=True,
            task_id=task_id,
            message="Resume submitted for processing",
            tracking_url=f"/api/async/status/{task_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to submit resume for processing: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit resume: {str(e)}"
        )

@router.post("/process-resume-file", response_model=ProcessingResponse)
async def process_resume_file_async(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload and process resume PDF file asynchronously
    
    Args:
        file: PDF file upload
        
    Returns:
        Task ID for tracking processing status
    """
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Read and validate file content
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Extract text first to validate PDF
        text = resume_parser.extract_text_from_pdf(file_content)
        if not text:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from PDF"
            )
        
        # Prepare metadata
        metadata = {
            "filename": file.filename,
            "file_size": len(file_content),
            "content_type": file.content_type,
            "upload_method": "fastapi_upload"
        }
        
        # Submit for processing
        task_id = submit_resume_for_processing(
            resume_text=text,
            metadata=metadata
        )
        
        return ProcessingResponse(
            success=True,
            task_id=task_id,
            message=f"File '{file.filename}' submitted for processing",
            tracking_url=f"/api/async/status/{task_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_processing_status(task_id: str):
    """
    Get the status of a resume processing task
    
    Args:
        task_id: The Celery task ID
        
    Returns:
        Current status and progress of the task
    """
    try:
        status = get_task_status(task_id)
        
        return TaskStatusResponse(
            task_id=task_id,
            state=status['state'],
            progress=status['progress'],
            stage=status['stage'],
            result=status.get('result'),
            error=status.get('error')
        )
        
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )

@router.get("/result/{document_id}")
async def get_analysis_result(document_id: str):
    """
    Retrieve resume analysis result from MongoDB
    
    Args:
        document_id: MongoDB document ID
        
    Returns:
        Complete resume analysis data
    """
    try:
        # Submit Celery task to retrieve data
        task = get_resume_analysis.delay(document_id)
        result = task.get(timeout=10)  # Wait up to 10 seconds
        
        if not result['success']:
            raise HTTPException(
                status_code=404,
                detail=result['error']
            )
        
        return {
            "success": True,
            "document_id": document_id,
            "data": result['data']
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analysis: {str(e)}"
        )

@router.get("/health")
async def async_system_health():
    """
    Check health of asynchronous processing system
    
    Returns:
        Health status of all components
    """
    try:
        # Submit health check task
        task = health_check.delay()
        health_status = task.get(timeout=5)
        
        return {
            "service": "Asynchronous Processing",
            "status": "healthy",
            "components": health_status,
            "features": {
                "resume_text_processing": True,
                "file_upload_processing": True,
                "ollama_integration": True,
                "mongodb_storage": True,
                "progress_tracking": True
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "service": "Asynchronous Processing",
            "status": "unhealthy",
            "error": str(e),
            "components": {
                "celery": "unknown",
                "ollama": "unknown", 
                "mongodb": "unknown"
            }
        }

@router.get("/tasks/active")
async def get_active_tasks():
    """
    Get list of currently active processing tasks
    
    Returns:
        List of active tasks and their status
    """
    try:
        from tasks import celery_app
        
        # Get active tasks from Celery
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        if not active_tasks:
            return {
                "active_tasks": [],
                "total_active": 0,
                "message": "No active tasks"
            }
        
        # Format task information
        formatted_tasks = []
        total_active = 0
        
        for worker, tasks in active_tasks.items():
            total_active += len(tasks)
            for task in tasks:
                formatted_tasks.append({
                    "task_id": task['id'],
                    "task_name": task['name'],
                    "worker": worker,
                    "args": task.get('args', []),
                    "kwargs": task.get('kwargs', {})
                })
        
        return {
            "active_tasks": formatted_tasks,
            "total_active": total_active,
            "workers": list(active_tasks.keys())
        }
        
    except Exception as e:
        logger.error(f"Failed to get active tasks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active tasks: {str(e)}"
        )

@router.delete("/task/{task_id}")
async def cancel_task(task_id: str):
    """
    Cancel a running task
    
    Args:
        task_id: The Celery task ID to cancel
        
    Returns:
        Cancellation status
    """
    try:
        from tasks import celery_app
        
        # Revoke the task
        celery_app.control.revoke(task_id, terminate=True)
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "Task cancellation requested"
        }
        
    except Exception as e:
        logger.error(f"Failed to cancel task: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel task: {str(e)}"
        )

@router.post("/analyze-resume", response_model=ProcessingResponse)
async def analyze_resume_async(request: AnalyzeResumeRequest):
    """
    Analyze resume text using Ollama to extract skills and experience as JSON
    
    Args:
        request: Resume text to analyze
        
    Returns:
        Task ID for tracking analysis status
    """
    try:
        if not request.resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Resume text cannot be empty"
            )
        
        # Submit task for analysis
        task = analyze_resume.delay(request.resume_text)
        task_id = task.id
        
        return ProcessingResponse(
            success=True,
            task_id=task_id,
            message="Resume submitted for analysis",
            tracking_url=f"/api/async/status/{task_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to submit resume for analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit resume for analysis: {str(e)}"
        )
