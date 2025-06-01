# main.py
from fastapi import FastAPI, HTTPException, Body, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import json
import io
import base64
import time
import os

# Load environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not found. Using environment variables as is.")

# Import agents with try/except to handle missing dependencies
try:
    from agents.resume_analyzer import ResumeAnalyzerAgent
    resume_agent_available = True
except ImportError as e:
    print(f"Warning: ResumeAnalyzerAgent not available: {e}")
    resume_agent_available = False

try:
    from agents.mock_interviewer import MockInterviewerAgent
    interview_agent_available = True
except ImportError as e:
    print(f"Warning: MockInterviewerAgent not available: {e}")
    interview_agent_available = False

try:
    from agents.dsa_evaluator import DSAEvaluatorAgent
    dsa_agent_available = True
except ImportError as e:
    print(f"Warning: DSAEvaluatorAgent not available: {e}")
    dsa_agent_available = False

try:
    from agents.behavioural_coach import BehavioralCoachAgent
    behavioral_coach_available = True
except ImportError as e:
    print(f"Warning: BehavioralCoachAgent not available: {e}")
    behavioral_coach_available = False

try:
    from agents.performance_tracker import PerformanceTrackerAgent
    performance_tracker_available = True
except ImportError as e:
    print(f"Warning: PerformanceTrackerAgent not available: {e}")
    performance_tracker_available = False

# Video integration removed

try:
    from database import save_session, get_session, track_user_session, get_user_performance
    database_available = True
except ImportError as e:
    print(f"Warning: Database functions not available: {e}")
    database_available = False

try:
    from utils.pdf_parser import parse_resume_pdf, extract_text_from_pdf
    pdf_parser_available = True
except ImportError as e:
    print(f"Warning: PDF parser not available: {e}")
    pdf_parser_available = False

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ResumeRequest(BaseModel):
    text: str
    format: str = "text"

class InterviewRequest(BaseModel):
    responses: List[str]
    question_set: str = "default"

class CodeRequest(BaseModel):
    code: str
    problem: str = "reverse_string"
    
class SessionRequest(BaseModel):
    user_id: str
    session_data: Dict[str, Any]
    
# Initialize agents with fallback mechanisms
resume_agent = None
if resume_agent_available:
    try:
        resume_agent = ResumeAnalyzerAgent()
        print("ResumeAnalyzerAgent initialized successfully")
    except Exception as e:
        print(f"Error initializing ResumeAnalyzerAgent: {e}")
        resume_agent_available = False

interview_agent = None
if interview_agent_available:
    try:
        interview_agent = MockInterviewerAgent()
        print("MockInterviewerAgent initialized successfully")
    except Exception as e:
        print(f"Error initializing MockInterviewerAgent: {e}")
        interview_agent_available = False

dsa_agent = None
if dsa_agent_available:
    try:
        dsa_agent = DSAEvaluatorAgent()
        print("DSAEvaluatorAgent initialized successfully")
    except Exception as e:
        print(f"Error initializing DSAEvaluatorAgent: {e}")
        dsa_agent_available = False

behavioral_coach = None
if behavioral_coach_available:
    try:
        behavioral_coach = BehavioralCoachAgent()
        print("BehavioralCoachAgent initialized successfully")
    except Exception as e:
        print(f"Error initializing BehavioralCoachAgent: {e}")
        behavioral_coach_available = False

performance_tracker = None
if performance_tracker_available:
    try:
        performance_tracker = PerformanceTrackerAgent()
        print("PerformanceTrackerAgent initialized successfully")
    except Exception as e:
        print(f"Error initializing PerformanceTrackerAgent: {e}")
        performance_tracker_available = False

# Video agent initialization removed

# Endpoints
@app.post("/analyze/resume")
async def analyze_resume(request: ResumeRequest):
    try:
        if not resume_agent_available or resume_agent is None:
            # Fallback response with simulated data
            return {
                "skills": {
                    "technical": ["Python", "Data Analysis", "Machine Learning"],
                    "soft": ["Communication", "Teamwork", "Problem Solving"]
                },
                "role_match": [
                    {"role": "Data Scientist", "match_score": 85},
                    {"role": "Software Engineer", "match_score": 75},
                    {"role": "ML Engineer", "match_score": 80}
                ],
                "suggested_questions": [
                    "Tell me about your experience with Python programming.",
                    "How have you applied machine learning in your projects?",
                    "Describe a challenging problem you solved recently."
                ],
                "strengths": ["Strong technical skills", "Good problem-solving abilities", "Experience with data analysis"],
                "weaknesses": ["Could improve on cloud technologies", "Limited experience with deployment"],
                "fallback": True
            }
        
        # If agent is available, use it
        analysis = resume_agent.analyze(request.text)
        analysis["fallback"] = False
        return analysis
    except Exception as e:
        print(f"Error in analyze_resume: {e}")
        # Fallback response
        return {
            "skills": {"technical": [], "soft": []},
            "role_match": [],
            "suggested_questions": ["Tell me about yourself."],
            "strengths": [],
            "weaknesses": [],
            "error": str(e),
            "fallback": True
        }

@app.post("/analyze/resume/pdf")
async def analyze_resume_pdf(file: UploadFile = File(...)):
    try:
        # Check if required components are available
        if not resume_agent_available or resume_agent is None or not pdf_parser_available:
            # Fallback response
            return {
                "skills": {
                    "technical": ["Python", "Data Analysis", "Machine Learning"],
                    "soft": ["Communication", "Teamwork", "Problem Solving"]
                },
                "role_match": [
                    {"role": "Data Scientist", "match_score": 85},
                    {"role": "Software Engineer", "match_score": 75}
                ],
                "suggested_questions": [
                    "Tell me about your experience with Python programming.",
                    "How have you applied machine learning in your projects?"
                ],
                "strengths": ["Strong technical skills", "Good problem-solving abilities"],
                "weaknesses": ["Could improve on cloud technologies"],
                "extracted_text": "PDF parsing not available in this deployment.",
                "fallback": True
            }
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
            
        # Read the file content
        file_content = await file.read()
        
        # Parse the PDF
        resume_text = extract_text_from_pdf(file_content)
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF or the PDF contains too little text")
        
        # Analyze the resume
        analysis = resume_agent.analyze(resume_text)
        analysis["extracted_text"] = resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
        analysis["fallback"] = False
        return analysis
    except Exception as e:
        print(f"Error in analyze_resume_pdf: {e}")
        # Fallback response
        return {
            "skills": {"technical": [], "soft": []},
            "role_match": [],
            "suggested_questions": ["Tell me about yourself."],
            "strengths": [],
            "weaknesses": [],
            "extracted_text": "Error processing PDF.",
            "error": str(e),
            "fallback": True
        }

@app.post("/analyze/interview")
async def analyze_interview(request: InterviewRequest):
    try:
        if not interview_agent_available or interview_agent is None:
            # Fallback response with simulated data
            return {
                "evaluations": [
                    {"question": "Tell me about yourself", "score": 8, "feedback": "Good introduction with clear structure."},
                    {"question": "Describe a challenging project", "score": 7, "feedback": "Good details but could improve on outcome description."},
                    {"question": "How do you handle conflicts?", "score": 9, "feedback": "Excellent conflict resolution approach."}
                ],
                "average_score": 8.0,
                "improvement_areas": ["Provide more specific examples", "Quantify achievements where possible"],
                "overall_feedback": "Strong interview performance with good communication skills. Continue to practice with more specific examples.",
                "fallback": True
            }
        
        # If agent is available, use it
        evaluation = interview_agent.evaluate(request.responses)
        evaluation["fallback"] = False
        return evaluation
    except Exception as e:
        print(f"Error in analyze_interview: {e}")
        # Fallback response
        return {
            "evaluations": [],
            "average_score": 5.0,
            "improvement_areas": ["Practice more interview questions"],
            "overall_feedback": "Unable to provide detailed feedback due to system limitations.",
            "error": str(e),
            "fallback": True
        }

@app.post("/analyze/code")
async def analyze_code(request: CodeRequest):
    try:
        if not dsa_agent_available or dsa_agent is None:
            # Fallback response with simulated data
            return {
                "correctness": 8,
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "style": 7,
                "suggestions": ["Consider adding more comments", "Variable names could be more descriptive"],
                "fallback": True
            }
        
        # If agent is available, use it
        evaluation = dsa_agent.evaluate(request.code, request.problem)
        evaluation["fallback"] = False
        return evaluation
    except Exception as e:
        print(f"Error in analyze_code: {e}")
        # Fallback response
        return {
            "correctness": 0,
            "time_complexity": "Unknown",
            "space_complexity": "Unknown",
            "style": 0,
            "suggestions": ["Unable to evaluate code due to system limitations."],
            "error": str(e),
            "fallback": True
        }

@app.get("/performance/{user_id}")
async def get_performance(user_id: str):
    try:
        # Check if required components are available
        if (not performance_tracker_available or performance_tracker is None) and not database_available:
            # Fallback response with simulated data
            return {
                "user_id": user_id,
                "activity": {"total_sessions": 3, "last_active": "2023-06-01T12:00:00Z"},
                "metrics": {"average_interview_score": 7.5, "average_code_score": 8.0},
                "insights": ["Good progress in interview skills", "Strong in algorithm implementation"],
                "recommendations": ["Practice more system design questions", "Work on behavioral questions"],
                "fallback": True
            }
        
        # Try to get data from both sources if available
        perf_agent_data = None
        db_performance = None
        
        if performance_tracker_available and performance_tracker is not None:
            try:
                perf_agent_data = performance_tracker.get_user_performance(user_id)
            except Exception as e:
                print(f"Error getting performance from agent: {e}")
        
        if database_available:
            try:
                db_performance = get_user_performance(user_id)
            except Exception as e:
                print(f"Error getting performance from database: {e}")
        
        # Prioritize database data if available
        if db_performance and "error" not in db_performance:
            db_performance["fallback"] = False
            return db_performance
        elif perf_agent_data:
            perf_agent_data["fallback"] = False
            return perf_agent_data
        else:
            raise Exception("No performance data available from any source")
    except Exception as e:
        print(f"Error in get_performance: {e}")
        # Fallback response
        return {
            "user_id": user_id,
            "activity": {"total_sessions": 0},
            "metrics": {},
            "insights": [],
            "recommendations": ["Start practicing to build performance data."],
            "error": str(e),
            "fallback": True
        }

# Combined analysis endpoint (legacy support)
@app.post("/analyze/combined")
async def analyze_combined(resume: str = Body(...), 
                         answers: List[str] = Body(...),
                         code: str = Body(...)):
    try:
        session_id = str(uuid.uuid4())
        user_id = f"user_{session_id[:8]}"
        using_fallback = False
        
        # Run all analyses with fallback mechanisms
        resume_analysis = {}
        interview_eval = {}
        code_eval = {}
        behavior_analysis = {}
        performance = {}
        
        # Resume analysis
        if resume_agent_available and resume_agent is not None:
            try:
                resume_analysis = resume_agent.analyze(resume)
            except Exception as e:
                print(f"Error in resume analysis: {e}")
                resume_analysis = {
                    "skills": {"technical": ["Python", "Data Analysis"], "soft": ["Communication"]},
                    "role_match": [{"role": "Data Scientist", "match_score": 80}],
                    "suggested_questions": ["Tell me about your experience."],
                    "strengths": ["Technical skills"],
                    "weaknesses": ["Could improve on specific technologies"],
                    "fallback": True
                }
                using_fallback = True
        else:
            resume_analysis = {
                "skills": {"technical": ["Python", "Data Analysis"], "soft": ["Communication"]},
                "role_match": [{"role": "Data Scientist", "match_score": 80}],
                "suggested_questions": ["Tell me about your experience."],
                "strengths": ["Technical skills"],
                "weaknesses": ["Could improve on specific technologies"],
                "fallback": True
            }
            using_fallback = True
        
        # Interview evaluation
        if interview_agent_available and interview_agent is not None:
            try:
                interview_eval = interview_agent.evaluate(answers)
            except Exception as e:
                print(f"Error in interview evaluation: {e}")
                interview_eval = {
                    "evaluations": [{"question": "General", "score": 7, "feedback": "Good responses overall."}],
                    "average_score": 7.0,
                    "improvement_areas": ["Provide more specific examples"],
                    "overall_feedback": "Good communication skills.",
                    "fallback": True
                }
                using_fallback = True
        else:
            interview_eval = {
                "evaluations": [{"question": "General", "score": 7, "feedback": "Good responses overall."}],
                "average_score": 7.0,
                "improvement_areas": ["Provide more specific examples"],
                "overall_feedback": "Good communication skills.",
                "fallback": True
            }
            using_fallback = True
        
        # Code evaluation
        if dsa_agent_available and dsa_agent is not None:
            try:
                code_eval = dsa_agent.evaluate(code)
            except Exception as e:
                print(f"Error in code evaluation: {e}")
                code_eval = {
                    "correctness": 7,
                    "time_complexity": "O(n)",
                    "space_complexity": "O(1)",
                    "style": 8,
                    "suggestions": ["Add more comments"],
                    "fallback": True
                }
                using_fallback = True
        else:
            code_eval = {
                "correctness": 7,
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "style": 8,
                "suggestions": ["Add more comments"],
                "fallback": True
            }
            using_fallback = True
        
        # Behavioral analysis
        if behavioral_coach_available and behavioral_coach is not None:
            try:
                behavior_analysis = {"evaluation": behavioral_coach.evaluate_behavioral(answers)}
            except Exception as e:
                print(f"Error in behavioral analysis: {e}")
                behavior_analysis = {
                    "evaluation": "Good behavioral responses showing teamwork and problem-solving skills.",
                    "fallback": True
                }
                using_fallback = True
        else:
            behavior_analysis = {
                "evaluation": "Good behavioral responses showing teamwork and problem-solving skills.",
                "fallback": True
            }
            using_fallback = True
        
        # Create session data
        session_data = {
            "session_id": session_id,
            "interview_score": interview_eval.get("average_score", 0),
            "code_correctness": code_eval.get("correctness", 0),
            "resume_skills": resume_analysis.get("skills", {}).get("technical", [])
        }
        
        # Track the session if available
        if performance_tracker_available and performance_tracker is not None:
            try:
                performance_tracker.track_session(user_id, session_data)
            except Exception as e:
                print(f"Error tracking session with performance tracker: {e}")
        
        # Get performance data
        if performance_tracker_available and performance_tracker is not None:
            try:
                performance = performance_tracker.get_user_performance(user_id)
            except Exception as e:
                print(f"Error getting performance data: {e}")
                performance = {
                    "user_id": user_id,
                    "activity": {"total_sessions": 1},
                    "metrics": {},
                    "insights": {},
                    "recommendations": ["Continue practicing to build more performance data."],
                    "fallback": True
                }
                using_fallback = True
        else:
            performance = {
                "user_id": user_id,
                "activity": {"total_sessions": 1},
                "metrics": {},
                "insights": {},
                "recommendations": ["Continue practicing to build more performance data."],
                "fallback": True
            }
            using_fallback = True
        
        # Save to database if available
        full_session_data = {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "resume_analysis": resume_analysis,
            "interview_evaluation": interview_eval,
            "code_evaluation": code_eval,
            "performance": performance
        }
        
        if database_available:
            try:
                save_session(full_session_data)
                
                # Also track in user performance system
                track_user_session(
                    user_id,
                    session_id,
                    "combined",
                    {
                        "resume_score": resume_analysis.get("score", 0),
                        "interview_score": interview_eval.get("average_score", 0),
                        "code_correctness": code_eval.get("correctness", 0),
                    }
                )
            except Exception as e:
                print(f"Error saving session to database: {e}")
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "resume_analysis": resume_analysis,
            "interview_evaluation": interview_eval,
            "code_evaluation": code_eval,
            "behavioral_analysis": behavior_analysis,
            "performance": performance,
            "using_fallback": using_fallback
        }
    except Exception as e:
        print(f"Error in analyze_combined: {e}")
        # Complete fallback response
        session_id = str(uuid.uuid4())
        user_id = f"user_{session_id[:8]}"
        return {
            "session_id": session_id,
            "user_id": user_id,
            "resume_analysis": {
                "skills": {"technical": [], "soft": []},
                "role_match": [],
                "suggested_questions": ["Tell me about yourself."],
                "strengths": [],
                "weaknesses": [],
                "fallback": True
            },
            "interview_evaluation": {
                "evaluations": [],
                "average_score": 5.0,
                "improvement_areas": ["Practice more interview questions"],
                "overall_feedback": "Unable to provide detailed feedback.",
                "fallback": True
            },
            "code_evaluation": {
                "correctness": 0,
                "time_complexity": "Unknown",
                "space_complexity": "Unknown",
                "style": 0,
                "suggestions": ["Unable to evaluate code."],
                "fallback": True
            },
            "behavioral_analysis": {
                "evaluation": "Unable to provide behavioral analysis.",
                "fallback": True
            },
            "performance": {
                "user_id": user_id,
                "activity": {"total_sessions": 0},
                "metrics": {},
                "insights": {},
                "recommendations": ["Start practicing to build performance data."],
                "fallback": True
            },
            "error": str(e),
            "using_fallback": True
        }

@app.post("/track/session")
def track_session(request: SessionRequest):
    try:
        # Call the performance tracker to record the session
        tracker = PerformanceTrackerAgent()
        session_id = tracker.track_session(request.user_id, request.session_data)
        
        # Also save to SQLite database
        session_type = "unknown"
        if "interview_score" in request.session_data:
            session_type = "interview"
        elif "code_correctness" in request.session_data:
            session_type = "dsa"
        elif "resume_skills" in request.session_data:
            session_type = "resume"
            
        track_user_session(
            request.user_id,
            request.session_data.get("session_id", session_id),
            session_type,
            request.session_data
        )
        
        return {"status": "success", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Video interview endpoint removed

# Video interview questions endpoint removed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)