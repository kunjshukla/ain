# main.py
from fastapi import FastAPI, HTTPException, Body, File, UploadFile, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import json
import io
import base64
import time
import os
import platform

# Socket.io imports
import socketio
from fastapi import Request

# Load environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not found. Using environment variables as is.")

# Import agents with try/except to handle missing dependencies
try:
    # Try relative import first
    from agents.resume_analyzer import ResumeAnalyzerAgent
    resume_agent_available = True
except ImportError as e:
    try:
        # Fallback to absolute import for local development
        from backend.agents.resume_analyzer import ResumeAnalyzerAgent
        resume_agent_available = True
    except ImportError as e:
        print(f"Warning: ResumeAnalyzerAgent not available: {e}")
        resume_agent_available = False

try:
    # Try relative import first
    from agents.mock_interviewer import MockInterviewerAgent
    interview_agent_available = True
except ImportError as e:
    try:
        # Fallback to absolute import for local development
        from backend.agents.mock_interviewer import MockInterviewerAgent
        interview_agent_available = True
    except ImportError as e:
        print(f"Warning: MockInterviewerAgent not available: {e}")
        interview_agent_available = False

try:
    # Try relative import first
    from agents.dsa_evaluator import DSAEvaluatorAgent
    dsa_agent_available = True
except ImportError as e:
    try:
        # Fallback to absolute import for local development
        from backend.agents.dsa_evaluator import DSAEvaluatorAgent
        dsa_agent_available = True
    except ImportError as e:
        print(f"Warning: DSAEvaluatorAgent not available: {e}")
        dsa_agent_available = False

try:
    # Try relative import first
    from agents.behavioural_coach import BehavioralCoachAgent
    behavioral_coach_available = True
except ImportError as e:
    try:
        # Fallback to absolute import for local development
        from backend.agents.behavioural_coach import BehavioralCoachAgent
        behavioral_coach_available = True
    except ImportError as e:
        print(f"Warning: BehavioralCoachAgent not available: {e}")
        behavioral_coach_available = False

try:
    # Try relative import first
    from agents.performance_tracker import PerformanceTrackerAgent
    performance_tracker_available = True
except ImportError as e:
    try:
        # Fallback to absolute import for local development
        from backend.agents.performance_tracker import PerformanceTrackerAgent
        performance_tracker_available = True
    except ImportError as e:
        print(f"Warning: PerformanceTrackerAgent not available: {e}")
        performance_tracker_available = False

# Video integration removed

try:
    # Try direct import first (for when running from backend directory)
    from database import save_session, get_session, track_user_session, get_user_performance
    database_available = True
except ImportError as e:
    try:
        # Try relative import
        from .database import save_session, get_session, track_user_session, get_user_performance
        database_available = True
    except (ImportError, ValueError) as e:
        try:
            # Fallback to absolute import for local development
            from backend.database import save_session, get_session, track_user_session, get_user_performance
            database_available = True
        except ImportError as e:
            print(f"Warning: Database functions not available: {e}")
            database_available = False
            
            # Define fallback functions to prevent errors
            def save_session(session_id, session_type, data):
                print(f"Mock saving session {session_id} of type {session_type}")
                return True
                
            def get_session(session_id):
                return {"session_id": session_id, "data": {}, "timestamp": datetime.now().isoformat()}
                
            def track_user_session(user_id, session_id, session_type, data):
                print(f"Mock tracking session {session_id} for user {user_id}")
                return True
                
            def get_user_performance(user_id):
                return {"user_id": user_id, "sessions": [], "metrics": {}}

try:
    # Try relative import first
    from utils.pdf_parser import parse_resume_pdf, extract_text_from_pdf
    pdf_parser_available = True
except ImportError as e:
    try:
        # Fallback to absolute import for local development
        from backend.utils.pdf_parser import parse_resume_pdf, extract_text_from_pdf
        pdf_parser_available = True
    except ImportError as e:
        print(f"Warning: PDF parser not available: {e}")
        pdf_parser_available = False
        
        # Define fallback functions to prevent errors
        def parse_resume_pdf(pdf_content):
            return {"error": "PDF parser not available"}
            
        def extract_text_from_pdf(pdf_content):
            return "[PDF text extraction not available]"

app = FastAPI(title="AI NinjaCoach API", description="API for AI NinjaCoach platform")

# Socket.io setup
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

# Create Socket.io ASGI app
socket_app = socketio.ASGIApp(sio, app)

# Socket.io event handlers
@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    print(f"Client connected: {sid}")
    await sio.emit('connection_response', {
        'status': 'connected',
        'message': 'Successfully connected to AI NinjaCoach',
        'client_id': sid
    }, room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f"Client disconnected: {sid}")

@sio.event
async def interview_start(sid, data):
    """Handle interview session start"""
    print(f"Interview started for client {sid}: {data}")
    await sio.emit('interview_started', {
        'status': 'started',
        'session_id': str(uuid.uuid4()),
        'timestamp': datetime.utcnow().isoformat()
    }, room=sid)

@sio.event
async def interview_response(sid, data):
    """Handle interview response from client"""
    print(f"Interview response from {sid}: {data}")
    # Process the response and send feedback
    await sio.emit('response_received', {
        'status': 'received',
        'message': 'Response recorded successfully'
    }, room=sid)

# Enhanced Socket.io event handlers for frontend compatibility

@sio.event
async def start_interview(sid, data):
    """Start an interview session"""
    try:
        print(f"Starting interview for client {sid}: {data}")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Initialize session data
        session_data = {
            'session_id': session_id,
            'user_id': data.get('userId'),
            'resume_id': data.get('resumeId'),
            'interview_type': data.get('interviewType', 'general'),
            'status': 'active',
            'started_at': datetime.utcnow().isoformat(),
            'current_question_id': None,
            'questions_asked': [],
            'responses': []
        }
        
        # Generate first question if interview agent is available
        first_question = None
        if interview_agent_available and interview_agent:
            try:
                first_question = await interview_agent.generate_question(
                    interview_type=data.get('interviewType', 'general'),
                    context=data.get('context', {})
                )
                session_data['current_question_id'] = str(uuid.uuid4())
                session_data['questions_asked'].append({
                    'id': session_data['current_question_id'],
                    'question': first_question,
                    'timestamp': datetime.utcnow().isoformat()
                })
            except Exception as e:
                print(f"Error generating first question: {e}")
                first_question = "Tell me about yourself and your background."
        else:
            first_question = "Tell me about yourself and your background."
            session_data['current_question_id'] = str(uuid.uuid4())
        
        # Save session if database is available
        if database_available:
            try:
                save_session(session_id, 'interview', session_data)
            except Exception as e:
                print(f"Error saving session: {e}")
        
        response = {
            'status': 'success',
            'session_id': session_id,
            'current_question': first_question,
            'current_question_id': session_data['current_question_id'],
            'interview_type': data.get('interviewType', 'general'),
            'started_at': session_data['started_at']
        }
        
        return response
        
    except Exception as e:
        print(f"Error starting interview: {e}")
        return {'error': f'Failed to start interview: {str(e)}'}

@sio.event
async def submit_answer(sid, data):
    """Submit an answer to the current question"""
    try:
        answer = data.get('answer', '')
        question_id = data.get('questionId', '')
        session_id = data.get('sessionId', '')
        
        print(f"Answer submitted by {sid}: {answer[:100]}...")
        
        # Process answer with agents if available
        feedback = None
        if interview_agent_available and interview_agent:
            try:
                feedback = await interview_agent.evaluate_response(answer, question_id)
            except Exception as e:
                print(f"Error evaluating response: {e}")
                feedback = "Thank you for your response."
        else:
            feedback = "Thank you for your response."
        
        # Update session data
        response_data = {
            'question_id': question_id,
            'answer': answer,
            'feedback': feedback,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        response = {
            'status': 'success',
            'feedback': feedback,
            'response_id': str(uuid.uuid4()),
            'timestamp': response_data['timestamp']
        }
        
        return response
        
    except Exception as e:
        print(f"Error submitting answer: {e}")
        return {'error': f'Failed to submit answer: {str(e)}'}

@sio.event
async def next_question(sid, data):
    """Request the next question in the interview"""
    try:
        session_id = data.get('sessionId', '')
        interview_type = data.get('interviewType', 'general')
        
        print(f"Next question requested by {sid}")
        
        # Generate next question
        question = None
        if interview_agent_available and interview_agent:
            try:
                question = await interview_agent.generate_question(
                    interview_type=interview_type,
                    context=data.get('context', {})
                )
            except Exception as e:
                print(f"Error generating question: {e}")
                question = "What are your career goals and how does this position align with them?"
        else:
            # Fallback questions
            fallback_questions = [
                "What are your career goals and how does this position align with them?",
                "Describe a challenging project you worked on and how you overcame obstacles.",
                "What are your strongest technical skills and how have you applied them?",
                "How do you stay updated with the latest technologies in your field?",
                "Describe a time when you had to work with a difficult team member."
            ]
            import random
            question = random.choice(fallback_questions)
        
        question_id = str(uuid.uuid4())
        
        response = {
            'status': 'success',
            'question': question,
            'question_id': question_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return response
        
    except Exception as e:
        print(f"Error getting next question: {e}")
        return {'error': f'Failed to get next question: {str(e)}'}

@sio.event
async def end_interview(sid, data):
    """End the interview session"""
    try:
        session_id = data.get('sessionId', '')
        
        print(f"Interview ended by {sid}")
        
        # Generate final feedback if available
        final_feedback = "Thank you for completing the interview. You'll receive detailed feedback soon."
        
        if interview_agent_available and interview_agent:
            try:
                final_feedback = await interview_agent.generate_final_feedback(session_id)
            except Exception as e:
                print(f"Error generating final feedback: {e}")
        
        response = {
            'status': 'success',
            'message': 'Interview completed successfully',
            'final_feedback': final_feedback,
            'session_id': session_id,
            'ended_at': datetime.utcnow().isoformat()
        }
        
        return response
        
    except Exception as e:
        print(f"Error ending interview: {e}")
        return {'error': f'Failed to end interview: {str(e)}'}

@sio.event
async def submit_resume(sid, data):
    """Submit resume for analysis"""
    try:
        resume_data = data.get('file', '')
        user_id = data.get('userId', '')
        
        print(f"Resume submitted by {sid}")
        
        # Generate job ID for tracking
        job_id = str(uuid.uuid4())
        
        # If we have resume processing capabilities, use them
        if resume_agent_available and resume_agent:
            try:
                # Trigger async resume analysis (you might want to use Celery here)
                analysis_result = await resume_agent.analyze_resume(resume_data)
                
                response = {
                    'status': 'success',
                    'job_id': job_id,
                    'message': 'Resume analysis completed',
                    'analysis': analysis_result,
                    'timestamp': datetime.utcnow().isoformat()
                }
            except Exception as e:
                print(f"Error analyzing resume: {e}")
                response = {
                    'status': 'processing',
                    'job_id': job_id,
                    'message': 'Resume submitted for analysis',
                    'timestamp': datetime.utcnow().isoformat()
                }
        else:
            response = {
                'status': 'processing',
                'job_id': job_id,
                'message': 'Resume submitted for analysis',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        return response
        
    except Exception as e:
        print(f"Error submitting resume: {e}")
        return {'error': f'Failed to submit resume: {str(e)}'}

@sio.event
async def get_resume_analysis(sid, data):
    """Get resume analysis results"""
    try:
        job_id = data.get('job_id', '')
        
        print(f"Resume analysis requested by {sid} for job {job_id}")
        
        # Mock response - in production, you'd query your database/cache
        response = {
            'status': 'completed',
            'job_id': job_id,
            'analysis': {
                'skills': ['Python', 'JavaScript', 'React', 'FastAPI'],
                'experience_years': 3,
                'education': 'Bachelor of Science in Computer Science',
                'strengths': ['Strong technical skills', 'Good communication'],
                'recommendations': ['Consider learning cloud technologies', 'Gain more leadership experience']
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return response
        
    except Exception as e:
        print(f"Error getting resume analysis: {e}")
        return {'error': f'Failed to get resume analysis: {str(e)}'}

@sio.event
async def voice_input(sid, data):
    """Handle voice input from client with ConversationOrchestrator and streaming"""
    try:
        user_text = data.get('transcript', '').strip()
        session_id = data.get('session_id', sid)
        job_role = data.get('job_role', 'Software Engineer')
        
        print(f"Voice input received from {sid}: {user_text[:100]}...")
        
        if not user_text:
            await sio.emit('error', {'message': 'No transcript provided'}, room=sid)
            return
        
        # Import dependencies
        try:
            import redis
            import json
            import requests
            from services.conversation_orchestrator import ConversationOrchestrator
        except ImportError as e:
            print(f"Missing dependencies: {e}")
            await sio.emit('error', {'message': f'Server configuration error: {e}'}, room=sid)
            return
        
        # Initialize Redis connection
        try:
            redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_timeout=5)
            redis_client.ping()  # Test connection
        except Exception as e:
            print(f"Redis connection failed: {e}")
            # Continue without Redis (use in-memory state)
            redis_client = None
        
        # Load or create orchestrator
        orchestrator = None
        if redis_client:
            try:
                orch_data = redis_client.get(f"orch:{session_id}")
                if orch_data:
                    orch_dict = json.loads(orch_data)
                    orchestrator = ConversationOrchestrator(
                        orch_dict['job_role'], 
                        orch_dict['skills']
                    )
                    orchestrator.current_stage = orch_dict['stage']
                    orchestrator.follow_up_count = orch_dict.get('follow_up_count', 0)
                    print(f"Loaded orchestrator for {session_id}: stage {orchestrator.current_stage}")
            except Exception as e:
                print(f"Error loading orchestrator: {e}")
        
        if not orchestrator:
            # First interaction or Redis unavailable - create new orchestrator
            skills = data.get('resume_skills', ['Python', 'FastAPI', 'React'])  # Default or from resume
            orchestrator = ConversationOrchestrator(job_role, skills)
            print(f"Created new orchestrator for {session_id}")
        
        # Load conversation history
        messages = []
        if redis_client:
            try:
                history_key = f"history:{session_id}"
                history = redis_client.get(history_key)
                messages = json.loads(history) if history else []
            except Exception as e:
                print(f"Error loading history: {e}")
        
        # Add user message
        messages.append({"role": "user", "content": user_text})
        
        # Check if we need follow-up or can advance stage
        needs_followup = orchestrator.should_ask_followup(user_text)
        followup_hint = ""
        
        if needs_followup and orchestrator.follow_up_count < 2:
            orchestrator.follow_up_count += 1
            followup_hint = "\n[USER GAVE VAGUE ANSWER - ASK SPECIFIC FOLLOW-UP TO GET MORE DETAILS]"
            print(f"Follow-up needed for {session_id}, count: {orchestrator.follow_up_count}")
        else:
            # Good answer or too many follow-ups - advance stage
            if orchestrator.current_stage < len(orchestrator.STAGES) - 1:
                orchestrator.advance_stage()
                print(f"Advanced to stage {orchestrator.current_stage}: {orchestrator.STAGES[orchestrator.current_stage]}")
        
        # Record interaction
        orchestrator.record_interaction(
            question=messages[-2]['content'] if len(messages) >= 2 else "Initial",
            answer=user_text,
            is_followup=needs_followup
        )
        
        # Prepare messages for Ollama
        system_prompt = orchestrator.get_system_prompt() + followup_hint
        ollama_messages = [
            {"role": "system", "content": system_prompt}
        ] + messages[-6:]  # Last 3 exchanges for context
        
        # Stream response from Ollama
        full_response = ""
        try:
            # Emit streaming start
            await sio.emit('ai_streaming_start', {
                'stage': orchestrator.STAGES[orchestrator.current_stage],
                'stage_progress': orchestrator.get_stage_progress()
            }, room=sid)
            
            # Make streaming request to Ollama
            response = requests.post(
                'http://localhost:11434/api/chat',
                json={
                    "model": "llama3.2",  # Use available model
                    "messages": ollama_messages,
                    "stream": True,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 150  # Keep responses concise
                    }
                },
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if 'message' in chunk and 'content' in chunk['message']:
                                token = chunk['message']['content']
                                if token:
                                    full_response += token
                                    await sio.emit('ai_token', {
                                        'token': token,
                                        'stage': orchestrator.STAGES[orchestrator.current_stage],
                                        'is_followup': needs_followup
                                    }, room=sid)
                            
                            # Check if response is complete
                            if chunk.get('done', False):
                                break
                                
                        except json.JSONDecodeError:
                            continue
            else:
                # Fallback if Ollama unavailable
                if needs_followup:
                    full_response = orchestrator.get_followup_question(user_text)
                else:
                    full_response = orchestrator.get_stage_question()
                
                # Emit fallback response token by token
                for char in full_response:
                    await sio.emit('ai_token', {
                        'token': char,
                        'stage': orchestrator.STAGES[orchestrator.current_stage],
                        'is_followup': needs_followup
                    }, room=sid)
                    
        except requests.exceptions.RequestException as e:
            print(f"Ollama request failed: {e}")
            # Use orchestrator fallback
            if needs_followup:
                full_response = orchestrator.get_followup_question(user_text)
            else:
                full_response = orchestrator.get_stage_question()
            
            # Emit fallback response
            for word in full_response.split():
                await sio.emit('ai_token', {
                    'token': word + ' ',
                    'stage': orchestrator.STAGES[orchestrator.current_stage],
                    'is_followup': needs_followup
                }, room=sid)
        
        # Save conversation state
        if redis_client:
            try:
                # Save conversation history
                messages.append({"role": "assistant", "content": full_response})
                history_key = f"history:{session_id}"
                redis_client.setex(history_key, 3600, json.dumps(messages))  # 1 hour expiry
                
                # Save orchestrator state
                redis_client.setex(f"orch:{session_id}", 3600, json.dumps({
                    'job_role': job_role,
                    'skills': orchestrator.resume_skills,
                    'stage': orchestrator.current_stage,
                    'follow_up_count': orchestrator.follow_up_count
                }))
                
                print(f"Saved state for {session_id}")
            except Exception as e:
                print(f"Error saving to Redis: {e}")
        
        # Signal response complete
        await sio.emit('ai_complete', {
            'stage': orchestrator.STAGES[orchestrator.current_stage],
            'stage_number': orchestrator.current_stage + 1,
            'total_stages': len(orchestrator.STAGES),
            'is_final': orchestrator.is_interview_complete(),
            'needs_followup': needs_followup,
            'follow_up_count': orchestrator.follow_up_count,
            'full_response': full_response,
            'progress': orchestrator.get_stage_progress()
        }, room=sid)
        
        print(f"Voice input processed for {sid}: {len(full_response)} chars")
        
    except Exception as e:
        print(f"Error processing voice input: {e}")
        import traceback
        traceback.print_exc()
        await sio.emit('error', {'message': f'Failed to process voice input: {str(e)}'}, room=sid)

@sio.event
async def tts_request(sid, data):
    """Handle text-to-speech request"""
    try:
        text = data.get('text', '')
        options = data.get('options', {})
        
        print(f"TTS requested by {sid}: {text[:50]}...")
        
        # Process TTS - this would integrate with your TTS service
        audio_url = None  # Would be generated by TTS service
        
        response = {
            'status': 'success',
            'audio_url': audio_url,
            'text': text,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return response
        
    except Exception as e:
        print(f"Error processing TTS request: {e}")
        return {'error': f'Failed to process TTS request: {str(e)}'}

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for Render deployment
@app.get("/health")
async def health_check():
    return {"status": "ok"}

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

# ---------------- Orchestrator Agent Endpoint ---------------- #
try:
    from agents.orchestrator_agent import OrchestratorAgent
except ImportError:
    # Fallback for local development
    try:
        from backend.agents.orchestrator_agent import OrchestratorAgent
    except ImportError:
        print("Warning: OrchestratorAgent not available")
        OrchestratorAgent = None
try:
    from orchestrator_schema import OrchestratorRequest, OrchestratorResponse
except ImportError:
    # Fallback for local development
    try:
        from backend.orchestrator_schema import OrchestratorRequest, OrchestratorResponse
    except ImportError:
        print("Warning: Orchestrator schema not available")
        # Define minimal schema classes to prevent errors
        from pydantic import BaseModel
        from typing import Dict, Any, Optional
        
        class OrchestratorRequest(BaseModel):
            user_id: str
            goal: str
            resume: Optional[str] = None
            code: Optional[str] = None
            interview_answers: Optional[Dict[str, Any]] = None
            
        class OrchestratorResponse(BaseModel):
            success: bool
            message: str
            data: Optional[Dict[str, Any]] = None

@app.post("/orchestrate", response_model=OrchestratorResponse)
def orchestrate(request: OrchestratorRequest):
    try:
        agent = OrchestratorAgent()
        results = agent.run_workflow(
            user_id=request.user_id,
            goal=request.goal,
            resume_text=request.resume_text,
            code=request.code,
            interview_answers=request.interview_answers
        )
        return OrchestratorResponse(**results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator error: {e}")

# Enhanced voice processing routes
try:
    from routes.stt import router as stt_router
    from routes.tts import router as tts_router
    from routes.interview import router as voice_interview_router
    from routes.enhanced_stt import router as enhanced_stt_router  # New enhanced STT
    
    # Include voice processing routes
    app.include_router(stt_router, prefix="/api/voice", tags=["Speech-to-Text"])
    app.include_router(enhanced_stt_router, prefix="/api", tags=["Enhanced STT"])  # New enhanced STT endpoint
    app.include_router(tts_router, prefix="/api/voice", tags=["Text-to-Speech"])
    app.include_router(voice_interview_router, prefix="/api/voice", tags=["Voice Interview"])
    
    print("Voice processing routes loaded successfully")
    print("Enhanced STT routes loaded successfully")
    voice_routes_available = True
    
except ImportError as e:
    print(f"Warning: Voice processing routes not available: {e}")
    voice_routes_available = False

# Async processing routes for resume analysis with Celery
try:
    from routes.async_processing import router as async_router
    app.include_router(async_router, tags=["Asynchronous Processing"])
    print("Async processing routes loaded successfully")
    async_routes_available = True
except ImportError as e:
    print(f"Warning: Async processing routes not available: {e}")
    async_routes_available = False

# Test routes for Ollama service
try:
    from routes.test_ollama import router as test_ollama_router
    app.include_router(test_ollama_router, tags=["Testing"])
    print("Test routes loaded successfully")
except ImportError as e:
    print(f"Warning: Test routes not available: {e}")


# Enhanced resume upload routes with session management
try:
    from routes.enhanced_resume_upload import router as enhanced_resume_router
    app.include_router(enhanced_resume_router, prefix="/api/resume", tags=["Enhanced Resume Upload"])
    print("Enhanced resume upload routes loaded successfully")
    enhanced_resume_routes_available = True
except ImportError as e:
    print(f"Warning: Enhanced resume upload routes not available: {e}")
    enhanced_resume_routes_available = False


# Interview results API routes
try:
    from routes.interview_results import router as interview_results_router
    app.include_router(interview_results_router, prefix="/api/interviews", tags=["Interview Results"])
    print("Interview results routes loaded successfully")
    interview_results_routes_available = True
except ImportError as e:
    print(f"Warning: Interview results routes not available: {e}")
    interview_results_routes_available = False


# Add proper application startup if missing
if __name__ == "__main__":
    import uvicorn
    # Use socket_app which includes both FastAPI and Socket.io
    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)
