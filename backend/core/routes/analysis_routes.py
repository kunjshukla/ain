"""
Analysis Routes Module
Handles resume analysis, interview analysis, and code analysis endpoints
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Import models
try:
    from orchestrator_schema import ResumeRequest, InterviewRequest, CodeRequest
except ImportError:
    from backend.orchestrator_schema import ResumeRequest, InterviewRequest, CodeRequest

# Import core services
try:
    from core.services.ai_service import ai_service
    from core.error_handling import error_handler, handle_errors
except ImportError:
    from backend.core.services.ai_service import ai_service
    from backend.core.error_handling import error_handler, handle_errors

# Import PDF parser
try:
    from utils.pdf_parser import parse_resume_pdf, extract_text_from_pdf
    pdf_parser_available = True
except ImportError:
    try:
        from backend.utils.pdf_parser import parse_resume_pdf, extract_text_from_pdf
        pdf_parser_available = True
    except ImportError as e:
        print(f"Warning: PDF parser not available: {e}")
        pdf_parser_available = False
        
        def extract_text_from_pdf(pdf_content):
            return "[PDF text extraction not available]"

router = APIRouter()

@router.post("/resume")
@handle_errors("resume_analysis")
async def analyze_resume(request: ResumeRequest):
    """Analyze resume text and extract skills, role matches, and suggestions"""
    return ai_service.analyze_resume(request.text)

@router.post("/resume/pdf")
async def analyze_resume_pdf(file: UploadFile = File(...)):
    """Analyze PDF resume and extract skills, role matches, and suggestions"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Check if PDF parser is available
        if not pdf_parser_available:
            return error_handler.create_fallback_response(
                "pdf_resume_analysis",
                {
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
                    "extracted_text": "PDF parsing not available in this deployment."
                }
            )
        
        # Read and process the file
        file_content = await file.read()
        resume_text = extract_text_from_pdf(file_content)
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text from the PDF or the PDF contains too little text"
            )
        
        # Analyze the resume
        analysis = ai_service.analyze_resume(resume_text)
        analysis["extracted_text"] = resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        error_id = error_handler.log_error(e, "pdf_resume_analysis")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.post("/interview")
@handle_errors("interview_analysis")
async def analyze_interview(request: InterviewRequest):
    """Analyze interview responses and provide feedback"""
    return ai_service.evaluate_interview(request.responses)

@router.post("/code")
@handle_errors("code_analysis")
async def analyze_code(request: CodeRequest):
    """Analyze code solution and provide feedback on correctness, complexity, and style"""
    return ai_service.evaluate_code(request.code, request.problem)

@router.post("/combined")
async def analyze_combined(request: dict):
    """Combined analysis endpoint for comprehensive evaluation"""
    try:
        results = {}
        
        # Resume analysis if provided
        if "resume_text" in request:
            resume_req = ResumeRequest(text=request["resume_text"])
            results["resume"] = await analyze_resume(resume_req)
        
        # Interview analysis if provided
        if "interview_responses" in request:
            interview_req = InterviewRequest(responses=request["interview_responses"])
            results["interview"] = await analyze_interview(interview_req)
        
        # Code analysis if provided
        if "code" in request and "problem" in request:
            code_req = CodeRequest(code=request["code"], problem=request["problem"])
            results["code"] = await analyze_code(code_req)
        
        return {
            "combined_analysis": results,
            "timestamp": "2024-12-08T12:00:00Z"
        }
    except Exception as e:
        print(f"Error in analyze_combined: {e}")
        return {
            "error": str(e),
            "combined_analysis": {},
            "timestamp": "2024-12-08T12:00:00Z"
        }
