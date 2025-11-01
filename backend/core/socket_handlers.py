"""
Socket.io Event Handlers for AI NinjaCoach
Modularized from main.py for better organization
"""

import socketio
import redis
import json
import requests
from datetime import datetime
from typing import Dict, Any
import uuid

# Import services
try:
    from services.conversation_orchestrator import ConversationOrchestrator
except ImportError:
    try:
        from backend.services.conversation_orchestrator import ConversationOrchestrator
    except ImportError:
        print("Warning: ConversationOrchestrator not available")
        ConversationOrchestrator = None

# Redis client setup
def get_redis_client():
    """Get Redis client with error handling"""
    try:
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_timeout=5)
        redis_client.ping()  # Test connection
        return redis_client
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return None

class SocketHandlers:
    """Centralized Socket.io event handlers"""
    
    def __init__(self, sio: socketio.AsyncServer):
        self.sio = sio
        self.setup_handlers()
    
    def setup_handlers(self):
        """Register all Socket.io event handlers"""
        
        @self.sio.event
        async def connect(sid, environ, auth):
            """Handle client connection"""
            print(f"Client connected: {sid}")
            await self.sio.emit('connection_response', {
                'status': 'connected',
                'message': 'Successfully connected to AI NinjaCoach',
                'client_id': sid
            }, room=sid)

        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection"""
            print(f"Client disconnected: {sid}")

        @self.sio.event
        async def interview_start(sid, data):
            """Handle interview session start"""
            print(f"Interview started for client {sid}: {data}")
            await self.sio.emit('interview_started', {
                'status': 'started',
                'session_id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat()
            }, room=sid)

        @self.sio.event
        async def interview_response(sid, data):
            """Handle interview response from client"""
            print(f"Interview response from {sid}: {data}")
            await self.sio.emit('response_received', {
                'status': 'received',
                'message': 'Response recorded successfully'
            }, room=sid)

        @self.sio.event
        async def start_interview(sid, data):
            """Enhanced interview start handler"""
            try:
                session_id = data.get('session_id', str(uuid.uuid4()))
                job_role = data.get('job_role', 'Software Engineer')
                
                print(f"Starting interview: {session_id} for role: {job_role}")
                
                await self.sio.emit('interview_session_created', {
                    'session_id': session_id,
                    'job_role': job_role,
                    'status': 'ready',
                    'timestamp': datetime.utcnow().isoformat()
                }, room=sid)
                
            except Exception as e:
                print(f"Error starting interview: {e}")
                await self.sio.emit('error', {'message': str(e)}, room=sid)

        @self.sio.event
        async def voice_input(sid, data):
            """Handle voice input from client with ConversationOrchestrator and streaming"""
            try:
                user_text = data.get('transcript', '').strip()
                session_id = data.get('session_id', sid)
                job_role = data.get('job_role', 'Software Engineer')
                
                print(f"Voice input received from {sid}: {user_text[:100]}...")
                
                if not user_text:
                    await self.sio.emit('error', {'message': 'No transcript provided'}, room=sid)
                    return
                
                # Get Redis client
                redis_client = get_redis_client()
                
                # Load or create orchestrator
                orchestrator = None
                if redis_client:
                    try:
                        orch_data = redis_client.get(f"orch:{session_id}")
                        if orch_data and ConversationOrchestrator:
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
                
                if not orchestrator and ConversationOrchestrator:
                    # Create new orchestrator with enhanced default skills
                    skills = data.get('resume_skills')
                    if not skills:
                        skills = self._get_default_skills(job_role)
                    
                    orchestrator = ConversationOrchestrator(job_role, skills)
                    print(f"Created new orchestrator for {session_id} with {len(skills)} skills")
                
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
                
                # Process with orchestrator if available
                if orchestrator:
                    await self._process_with_orchestrator(
                        sid, session_id, job_role, user_text, messages, orchestrator, redis_client
                    )
                else:
                    # Fallback without orchestrator
                    await self._process_fallback(sid, user_text)
                
            except Exception as e:
                print(f"Error processing voice input: {e}")
                import traceback
                traceback.print_exc()
                await self.sio.emit('error', {'message': f'Failed to process voice input: {str(e)}'}, room=sid)

        @self.sio.event
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

    def _get_default_skills(self, job_role: str) -> list:
        """Get default skills based on job role"""
        job_role_lower = job_role.lower()
        
        if 'data scientist' in job_role_lower:
            return ['Python', 'Pandas', 'NumPy', 'Scikit-learn', 'SQL', 'Jupyter', 'TensorFlow']
        elif 'frontend' in job_role_lower:
            return ['JavaScript', 'React', 'HTML', 'CSS', 'TypeScript', 'Vue.js', 'Angular']
        elif 'backend' in job_role_lower:
            return ['Python', 'Node.js', 'FastAPI', 'Django', 'PostgreSQL', 'MongoDB', 'Redis']
        elif 'fullstack' in job_role_lower or 'full stack' in job_role_lower:
            return ['JavaScript', 'React', 'Node.js', 'Python', 'FastAPI', 'PostgreSQL', 'AWS']
        else:
            return ['Python', 'JavaScript', 'React', 'FastAPI', 'SQL', 'Git']

    async def _process_with_orchestrator(self, sid, session_id, job_role, user_text, messages, orchestrator, redis_client):
        """Process voice input with ConversationOrchestrator"""
        try:
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
                await self.sio.emit('ai_streaming_start', {
                    'stage': orchestrator.STAGES[orchestrator.current_stage],
                    'stage_progress': orchestrator.get_stage_progress()
                }, room=sid)
                
                # Make streaming request to Ollama
                response = requests.post(
                    'http://localhost:11434/api/chat',
                    json={
                        "model": "llama3.2",
                        "messages": ollama_messages,
                        "stream": True,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 150
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
                                        await self.sio.emit('ai_token', {
                                            'token': token,
                                            'stage': orchestrator.STAGES[orchestrator.current_stage],
                                            'is_followup': needs_followup
                                        }, room=sid)
                                
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
                        await self.sio.emit('ai_token', {
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
                    await self.sio.emit('ai_token', {
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
                    redis_client.setex(history_key, 3600, json.dumps(messages))
                    
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
            await self.sio.emit('ai_complete', {
                'stage': orchestrator.STAGES[orchestrator.current_stage],
                'stage_number': orchestrator.current_stage + 1,
                'total_stages': len(orchestrator.STAGES),
                'is_final': orchestrator.is_interview_complete(),
                'needs_followup': needs_followup,
                'follow_up_count': orchestrator.follow_up_count,
                'full_response': full_response,
                'progress': orchestrator.get_stage_progress()
            }, room=sid)
            
        except Exception as e:
            print(f"Error in orchestrator processing: {e}")
            await self._process_fallback(sid, user_text)

    async def _process_fallback(self, sid, user_text):
        """Fallback processing when orchestrator is unavailable"""
        fallback_response = f"Thank you for sharing: '{user_text}'. Can you tell me more about your experience with this?"
        
        # Emit response token by token
        for word in fallback_response.split():
            await self.sio.emit('ai_token', {
                'token': word + ' ',
                'stage': 'general',
                'is_followup': False
            }, room=sid)
        
        await self.sio.emit('ai_complete', {
            'stage': 'general',
            'stage_number': 1,
            'total_stages': 1,
            'is_final': False,
            'needs_followup': False,
            'follow_up_count': 0,
            'full_response': fallback_response
        }, room=sid)
