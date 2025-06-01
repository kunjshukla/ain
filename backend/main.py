# main.py
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from datetime import datetime
import spacy
import json
from agents.resume_analyzer import ResumeAnalyzerAgent
from agents.mock_interviewer import MockInterviewerAgent
from agents.dsa_evaluator import DSAEvaluatorAgent
from agents.behavioural_coach import BehavioralCoachAgent
from agents.performance_tracker import PerformanceTrackerAgent

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

# Initialize agents
resume_agent = ResumeAnalyzerAgent()
interview_agent = MockInterviewerAgent()
dsa_agent = DSAEvaluatorAgent()
behavior_agent = BehavioralCoachAgent()
perf_agent = PerformanceTrackerAgent()

# Endpoints
@app.post("/analyze/resume")
async def analyze_resume(request: ResumeRequest):
    try:
        analysis = resume_agent.analyze(request.text)
        return {
            "skills": analysis["skills"],
            "role_match": analysis["role_match"],
            "suggested_questions": analysis["suggested_questions"],
            "strengths": analysis["strengths"],
            "weaknesses": analysis["weaknesses"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/interview")
async def analyze_interview(request: InterviewRequest):
    try:
        evaluation = interview_agent.evaluate(request.responses)
        return {
            "feedback": evaluation["feedback"],
            "scores": evaluation["scores"],
            "improvement_areas": evaluation["improvement_areas"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/code")
async def analyze_code(request: CodeRequest):
    try:
        evaluation = dsa_agent.evaluate(request.code, request.problem)
        return {
            "correctness": evaluation["correctness"],
            "time_complexity": evaluation["time_complexity"],
            "space_complexity": evaluation["space_complexity"],
            "style": evaluation["style"],
            "suggestions": evaluation["suggestions"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance/{user_id}")
async def get_performance(user_id: str):
    try:
        report = perf_agent.generate_report(user_id)
        return {
            "progress": report["progress"],
            "weak_areas": report["weak_areas"],
            "strengths": report["strengths"],
            "suggestions": report["suggestions"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Combined analysis endpoint (legacy support)
@app.post("/analyze")
async def analyze_combined(resume: str = Body(...), 
                         answers: List[str] = Body(...),
                         code: str = Body(...)):
    try:
        session_id = str(uuid.uuid4())
        
        # Run all analyses
        resume_analysis = resume_agent.analyze(resume)
        interview_eval = interview_agent.evaluate(answers)
        code_eval = dsa_agent.evaluate(code)
        behavior_analysis = behavior_agent.analyze(answers)
        
        # Generate performance report
        performance = perf_agent.generate_combined_report(
            resume_analysis, 
            interview_eval,
            code_eval,
            behavior_analysis
        )
        
        # Save session (implement your database logic here)
        session_data = {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "resume_analysis": resume_analysis,
            "interview_evaluation": interview_eval,
            "code_evaluation": code_eval,
            "performance": performance
        }
        # save_to_database(session_data)
        
        return {
            "session_id": session_id,
            "resume": resume_analysis,
            "interview": interview_eval,
            "code": code_eval,
            "behavior": behavior_analysis,
            "performance": performance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)