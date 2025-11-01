# routes/interview.py - Voice Interview Orchestration
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import uuid
from datetime import datetime

# Import voice-enabled agents
from agents.question_agent import generate_question, QuestionRequest
from agents.evaluator_agent import evaluate_answer, EvaluationRequest
from agents.feedback_agent import generate_feedback, FeedbackRequest

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class InterviewStartRequest(BaseModel):
    domain: str = "Software Engineering"
    difficulty: str = "Medium"
    user_level: str = "Intermediate"
    session_id: Optional[str] = None

class InterviewAnswerRequest(BaseModel):
    session_id: str
    user_answer: str
    question: str
    domain: str = "Software Engineering"
    difficulty: str = "Medium"

class InterviewResponse(BaseModel):
    session_id: str
    question: str
    domain: str
    difficulty: str
    success: bool
    message: str

class InterviewEvaluationResponse(BaseModel):
    session_id: str
    evaluation: Dict[str, Any]
    feedback: Dict[str, Any]
    next_question: str
    success: bool
    message: str

# In-memory session storage (replace with database in production)
interview_sessions = {}

@router.post("/interview/start", response_model=InterviewResponse)
async def start_interview(request: InterviewStartRequest):
    """Start a new voice interview session"""
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Starting interview session {session_id} for {request.domain}")
        
        # Generate first question
        first_question = generate_question(
            domain=request.domain,
            difficulty=request.difficulty,
            user_level=request.user_level
        )
        
        # Initialize session data
        session_data = {
            "session_id": session_id,
            "domain": request.domain,
            "difficulty": request.difficulty,
            "user_level": request.user_level,
            "start_time": datetime.now().isoformat(),
            "questions": [first_question],
            "answers": [],
            "evaluations": [],
            "current_question": first_question,
            "question_count": 1
        }
        
        # Store session
        interview_sessions[session_id] = session_data
        
        return InterviewResponse(
            session_id=session_id,
            question=first_question,
            domain=request.domain,
            difficulty=request.difficulty,
            success=True,
            message=f"Interview session started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start interview: {str(e)}"
        )

@router.post("/interview/answer", response_model=InterviewEvaluationResponse)
async def process_answer(request: InterviewAnswerRequest):
    """Process user's voice answer and provide feedback with next question"""
    
    # Validate session
    if request.session_id not in interview_sessions:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found"
        )
    
    session = interview_sessions[request.session_id]
    
    try:
        logger.info(f"Processing answer for session {request.session_id}")
        
        # Evaluate the user's answer
        evaluation_result = evaluate_answer(
            user_answer=request.user_answer,
            question=request.question,
            domain=request.domain,
            difficulty=request.difficulty
        )
        
        # Generate feedback based on evaluation
        feedback_result = generate_feedback(
            user_answer=request.user_answer,
            question=request.question,
            evaluation_score=evaluation_result["score"],
            evaluation_feedback=evaluation_result["feedback"],
            strengths=evaluation_result["strengths"],
            areas_for_improvement=evaluation_result["areas_for_improvement"],
            domain=request.domain,
            user_level=session["user_level"]
        )
        
        # Generate next question
        previous_questions = session["questions"]
        next_question = generate_question(
            domain=request.domain,
            difficulty=request.difficulty,
            user_level=session["user_level"],
            previous_questions=previous_questions
        )
        
        # Update session data
        session["answers"].append({
            "question": request.question,
            "answer": request.user_answer,
            "timestamp": datetime.now().isoformat()
        })
        session["evaluations"].append(evaluation_result)
        session["questions"].append(next_question)
        session["current_question"] = next_question
        session["question_count"] += 1
        
        return InterviewEvaluationResponse(
            session_id=request.session_id,
            evaluation=evaluation_result,
            feedback=feedback_result,
            next_question=next_question,
            success=True,
            message="Answer processed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error processing answer: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process answer: {str(e)}"
        )

@router.get("/interview/{session_id}/status")
async def get_interview_status(session_id: str):
    """Get current status of an interview session"""
    
    if session_id not in interview_sessions:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found"
        )
    
    session = interview_sessions[session_id]
    
    return {
        "session_id": session_id,
        "domain": session["domain"],
        "difficulty": session["difficulty"],
        "user_level": session["user_level"],
        "question_count": session["question_count"],
        "current_question": session["current_question"],
        "start_time": session["start_time"],
        "status": "active"
    }

@router.get("/interview/{session_id}/summary")
async def get_interview_summary(session_id: str):
    """Get summary of interview performance"""
    
    if session_id not in interview_sessions:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found"
        )
    
    session = interview_sessions[session_id]
    evaluations = session.get("evaluations", [])
    
    if not evaluations:
        return {
            "session_id": session_id,
            "message": "No evaluations available yet",
            "questions_answered": 0
        }
    
    # Calculate summary statistics
    scores = [eval_data["score"] for eval_data in evaluations]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    all_strengths = []
    all_improvements = []
    
    for eval_data in evaluations:
        all_strengths.extend(eval_data.get("strengths", []))
        all_improvements.extend(eval_data.get("areas_for_improvement", []))
    
    # Count most common strengths and improvements
    from collections import Counter
    common_strengths = Counter(all_strengths).most_common(3)
    common_improvements = Counter(all_improvements).most_common(3)
    
    return {
        "session_id": session_id,
        "questions_answered": len(evaluations),
        "average_score": round(avg_score, 1),
        "score_trend": scores,
        "top_strengths": [item[0] for item in common_strengths],
        "key_improvement_areas": [item[0] for item in common_improvements],
        "domain": session["domain"],
        "difficulty": session["difficulty"],
        "session_duration": session["start_time"]
    }

@router.post("/interview/{session_id}/end")
async def end_interview(session_id: str):
    """End an interview session and get final summary"""
    
    if session_id not in interview_sessions:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found"
        )
    
    # Get final summary
    summary = await get_interview_summary(session_id)
    
    # Mark session as ended
    session = interview_sessions[session_id]
    session["end_time"] = datetime.now().isoformat()
    session["status"] = "completed"
    
    return {
        "message": "Interview session ended successfully",
        "final_summary": summary
    }

@router.get("/interview/health")
def interview_health_check():
    """Health check for interview service"""
    
    # Check if all agents are working
    try:
        test_question = generate_question("Software Engineering", "Easy")
        test_evaluation = evaluate_answer(
            "This is a test answer", 
            "What is programming?", 
            "Software Engineering"
        )
        
        agents_healthy = bool(test_question and test_evaluation)
        
        return {
            "service": "Voice Interview",
            "agents_available": agents_healthy,
            "active_sessions": len(interview_sessions),
            "status": "healthy" if agents_healthy else "agents_unavailable"
        }
        
    except Exception as e:
        return {
            "service": "Voice Interview",
            "agents_available": False,
            "status": "error",
            "error": str(e)
        }

# Cleanup endpoint for development (remove in production)
@router.delete("/interview/sessions/cleanup")
async def cleanup_sessions():
    """Clean up all interview sessions (development only)"""
    global interview_sessions
    session_count = len(interview_sessions)
    interview_sessions.clear()
    
    return {
        "message": f"Cleaned up {session_count} interview sessions",
        "remaining_sessions": len(interview_sessions)
    }
