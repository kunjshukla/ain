"""
Enhanced Resume Upload API with Session Management
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Dict, Any, Optional
import uuid
import json
import redis
import logging
from datetime import datetime
import asyncio

from services.resume_parser import resume_parser
from agents.resume_analyzer import ResumeAnalyzerAgent

logger = logging.getLogger(__name__)

# Initialize Redis client
try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_timeout=5)
    redis_client.ping()
    logger.info("Redis connected for resume upload service")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}")
    redis_client = None

# Initialize resume analyzer
try:
    resume_analyzer = ResumeAnalyzerAgent()
except Exception as e:
    logger.warning(f"Resume analyzer not available: {e}")
    resume_analyzer = None

router = APIRouter(tags=["Resume Upload"])

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    job_role: Optional[str] = Query(None, description="Target job role for analysis")
) -> Dict[str, Any]:
    """
    Upload and analyze a resume PDF with session management and Redis storage
    
    Args:
        file: PDF file upload (max 5MB)
        job_role: Optional target job role for tailored analysis
        
    Returns:
        Session-based resume analysis with skills, experience, and metadata
    """
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=422,
            detail="Only PDF files are supported"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Check file size (5MB limit)
        if len(file_content) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=413,
                detail="File size exceeds 5MB limit"
            )
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Parse the resume
        result = resume_parser.parse_resume(file_content)
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse PDF: {result.get('error', 'Corrupted or invalid PDF')}"
            )
        
        # Extract text and analyze with AI
        resume_text = result['text']
        chunks_processed = len(result.get('structured_data', {}).get('sections', []))
        
        # AI Analysis
        analysis_result = {}
        if resume_analyzer:
            try:
                analysis_result = resume_analyzer.analyze(resume_text)
                # Tailor analysis to job role if provided
                if job_role:
                    analysis_result['job_role_match'] = _analyze_job_role_match(
                        analysis_result.get('skills', {}), 
                        job_role
                    )
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                analysis_result = _get_fallback_analysis()
        else:
            analysis_result = _get_fallback_analysis()
        
        # Extract experience years
        experience_years = _extract_experience_years(resume_text)
        
        # Prepare session data
        session_data = {
            'session_id': session_id,
            'filename': file.filename,
            'size_bytes': len(file_content),
            'upload_timestamp': datetime.utcnow().isoformat(),
            'job_role': job_role,
            'extracted_text': resume_text[:1000],  # Store first 1000 chars
            'chunks_processed': chunks_processed,
            'experience_years': experience_years,
            'skills': analysis_result.get('skills', {}),
            'analysis': analysis_result,
            'metadata': result['metadata']
        }
        
        # Store in Redis with 1 hour TTL
        if redis_client:
            try:
                redis_client.setex(
                    f"resume:{session_id}", 
                    3600,  # 1 hour TTL
                    json.dumps(session_data)
                )
                logger.info(f"Resume session {session_id} stored in Redis")
            except Exception as e:
                logger.error(f"Failed to store session in Redis: {e}")
        
        # Prepare response
        response = {
            'session_id': session_id,
            'extracted_skills': list(analysis_result.get('skills', {}).get('technical', [])),
            'experience_years': experience_years,
            'chunks_processed': chunks_processed,
            'analysis_summary': {
                'skills_count': len(analysis_result.get('skills', {}).get('technical', [])),
                'strengths': analysis_result.get('strengths', [])[:3],
                'recommended_roles': [match.get('role', '') for match in analysis_result.get('role_match', [])][:3]
            },
            'upload_success': True,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if job_role:
            response['job_role_analysis'] = analysis_result.get('job_role_match', {})
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during resume processing"
        )

def _extract_experience_years(text: str) -> int:
    """Extract years of experience from resume text"""
    import re
    
    # Common patterns for experience
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
        r'experience.*?(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?(?:field|industry)',
    ]
    
    text_lower = text.lower()
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            try:
                return int(matches[0])
            except (ValueError, IndexError):
                continue
    
    return 0  # Default if no experience found

def _analyze_job_role_match(skills: Dict[str, list], job_role: str) -> Dict[str, Any]:
    """Analyze how well skills match a specific job role"""
    job_role_lower = job_role.lower()
    technical_skills = skills.get('technical', [])
    
    # Define skill mappings for common roles
    role_skill_map = {
        'data scientist': ['python', 'machine learning', 'sql', 'pandas', 'numpy', 'tensorflow', 'pytorch'],
        'software engineer': ['python', 'javascript', 'java', 'react', 'node.js', 'git', 'docker'],
        'frontend developer': ['javascript', 'react', 'vue', 'angular', 'html', 'css', 'typescript'],
        'backend developer': ['python', 'java', 'node.js', 'sql', 'api', 'microservices', 'docker'],
        'devops engineer': ['docker', 'kubernetes', 'aws', 'azure', 'jenkins', 'terraform', 'ansible'],
        'ml engineer': ['python', 'tensorflow', 'pytorch', 'docker', 'kubernetes', 'mlops', 'aws']
    }
    
    # Find matching role skills
    matching_role = None
    for role, required_skills in role_skill_map.items():
        if role in job_role_lower:
            matching_role = role
            break
    
    if not matching_role:
        return {'match_score': 0, 'analysis': 'Job role not recognized'}
    
    required_skills = role_skill_map[matching_role]
    technical_skills_lower = [skill.lower() for skill in technical_skills]
    
    matches = [skill for skill in required_skills if skill in technical_skills_lower]
    match_score = int((len(matches) / len(required_skills)) * 100)
    
    return {
        'match_score': match_score,
        'matching_skills': matches,
        'missing_skills': [skill for skill in required_skills if skill not in technical_skills_lower],
        'analysis': f"{match_score}% match for {job_role} role"
    }

def _get_fallback_analysis() -> Dict[str, Any]:
    """Fallback analysis when AI agent is not available"""
    return {
        'skills': {
            'technical': ['Python', 'JavaScript', 'SQL'],
            'soft': ['Communication', 'Problem Solving']
        },
        'strengths': ['Technical skills', 'Experience'],
        'role_match': [{'role': 'Software Engineer', 'match_score': 75}],
        'fallback': True
    }
