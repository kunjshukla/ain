from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agents.resume_analyzer import ResumeAnalyzerAgent
from agents.mock_interviewer import MockInterviewerAgent
from agents.dsa_evaluator import DSAEvaluatorAgent
from agents.behavioural_coach import BehavioralCoachAgent
from agents.performance_tracker import PerformanceTrackerAgent
from database.models import init_db, save_session, get_session
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database
init_db()

@app.post("/analyze")
async def analyze(request: Request):
    data = await request.json()
    resume = data.get("resume", "")
    user_answers = data.get("user_answers", [])
    code_solution = data.get("code_solution", "")
    session_id = str(uuid.uuid4())

    # Step 1: Resume Analysis
    resume_agent = ResumeAnalyzerAgent()
    resume_feedback = resume_agent.analyze_resume(resume)

    # Step 2: Mock Interview
    interviewer_agent = MockInterviewerAgent()
    interview_results = interviewer_agent.conduct_interview(user_answers)

    # Step 3: DSA Evaluation
    dsa_agent = DSAEvaluatorAgent()
    dsa_results = dsa_agent.evaluate_code(code_solution)

    # Step 4: Behavioral Q&A
    behavioral_agent = BehavioralCoachAgent()
    behavioral_results = behavioral_agent.evaluate_behavioral(user_answers)

    # Step 5: Performance Tracking
    performance_agent = PerformanceTrackerAgent()
    final_report = performance_agent.generate_report(
        resume_feedback, interview_results, dsa_results, behavioral_results
    )

    # Save session
    session_data = {
        "session_id": session_id,
        "resume": resume,
        "user_answers": user_answers,
        "code_solution": code_solution,
        "resume_feedback": resume_feedback,
        "interview_results": interview_results,
        "dsa_results": dsa_results,
        "behavioral_results": behavioral_results,
        "final_report": final_report
    }
    save_session(session_data)

    return {
        "session_id": session_id,
        "resume_feedback": resume_feedback,
        "interview_results": interview_results,
        "dsa_results": dsa_results,
        "behavioral_results": behavioral_results,
        "final_report": final_report
    }

@app.get("/session/{session_id}")
async def get_session_data(session_id: str):
    session = get_session(session_id)
    if not session:
        return {"error": "Session not found"}
    return session


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)