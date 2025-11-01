"""
Conversation Orchestrator for AI NinjaCoach
Manages interview stages and conversation flow

This orchestrator guides the interview through structured stages:
1. Greeting - Warm introduction and current role
2. Experience Probe - Deep dive into relevant experience  
3. Technical Deep Dive - Skills-based problem solving
4. Behavioral - Team dynamics and soft skills
5. Closing - Wrap up and candidate questions
"""

from typing import List, Dict, Optional
import re
import random

class ConversationOrchestrator:
    """
    Orchestrates conversation flow through structured interview stages.
    Provides intelligent follow-up detection and stage-appropriate prompts.
    """
    
    STAGES = [
        "greeting",
        "experience_probe", 
        "technical_deep_dive",
        "behavioral",
        "closing"
    ]
    
    def __init__(self, job_role: str, resume_skills: List[str]):
        """
        Initialize conversation orchestrator
        
        Args:
            job_role: Target job role (e.g., "Software Engineer", "Data Scientist")
            resume_skills: List of skills extracted from resume
        """
        self.job_role = job_role
        self.resume_skills = resume_skills or ["general technical skills"]
        self.current_stage = 0
        self.weak_areas = []
        self.follow_up_count = 0
        self.questions_asked = []
        self.conversation_history = []
        
    def get_system_prompt(self) -> str:
        """
        Generate system prompt for current interview stage
        
        Returns:
            Detailed instructions for AI interviewer based on current stage
        """
        stage = self.STAGES[self.current_stage]
        
        base = f"""You are an expert recruiter interviewing for a {self.job_role} position.
Candidate's resume skills: {', '.join(self.resume_skills)}

CRITICAL CONVERSATION RULES:
- Keep responses under 25 words maximum
- Ask ONE question at a time
- Use natural speech patterns: "I see", "Got it", "Tell me more"
- If answer is vague, ask specific follow-up questions
- Be conversational and engaging, not robotic
- Show genuine interest in their responses
- Acknowledge their answers before asking next question

INTERVIEW FLOW:
- Current stage: {stage} ({self.current_stage + 1}/{len(self.STAGES)})
- Follow-ups asked: {self.follow_up_count}
- Weak areas identified: {', '.join(self.weak_areas) if self.weak_areas else 'None yet'}
"""
        
        stage_prompts = {
            "greeting": """
GREETING STAGE:
- Start warmly and professionally
- Ask about their current role or recent experience
- Keep it brief, build rapport
- Example: "Thanks for joining! Tell me about your current role."
""",
            "experience_probe": """
EXPERIENCE PROBE STAGE:
- Deep dive into their most relevant experience
- Ask for specific examples and outcomes
- Probe for technical challenges they've solved
- Look for leadership and problem-solving examples
- Example: "Walk me through your most challenging project."
""",
            "technical_deep_dive": f"""
TECHNICAL DEEP DIVE STAGE:
- Test knowledge of {self.resume_skills[0]} and related technologies
- Ask problem-solving questions
- Present hypothetical scenarios
- Assess depth of understanding
- Example: "How would you design a system for [specific problem]?"
""",
            "behavioral": """
BEHAVIORAL STAGE:
- Ask about teamwork, conflicts, leadership situations
- Use STAR method (Situation, Task, Action, Result)
- Focus on soft skills and cultural fit
- Example: "Tell me about a time you disagreed with a team member."
""",
            "closing": """
CLOSING STAGE:
- Wrap up the interview professionally
- Ask if they have questions about the role/company
- Provide next steps information
- Thank them for their time
- Example: "That covers my questions! What would you like to know about us?"
"""
        }
        
        return base + stage_prompts.get(stage, "")
    
    def should_ask_followup(self, answer_text: str) -> bool:
        """
        Determine if a follow-up question is needed based on answer quality
        
        Args:
            answer_text: Candidate's response text
            
        Returns:
            True if answer is vague and needs follow-up
        """
        if not answer_text or len(answer_text.strip()) < 5:
            return True
            
        # Count words
        word_count = len(answer_text.split())
        
        # Check for specific details
        specificity_indicators = [
            'because', 'example', 'specifically', 'by using', 'with', 'when', 'where',
            'implemented', 'designed', 'built', 'created', 'developed', 'managed',
            'result', 'outcome', 'impact', 'achieved', 'improved', 'reduced',
            'increased', 'optimized', 'solved', 'fixed', 'handled'
        ]
        
        has_specifics = any(indicator in answer_text.lower() 
                          for indicator in specificity_indicators)
        
        # Check for technical terms (if in technical stages)
        has_technical_terms = False
        if self.current_stage >= 2:  # technical_deep_dive or later
            technical_indicators = [
                'algorithm', 'database', 'api', 'framework', 'library', 'method',
                'function', 'class', 'object', 'variable', 'query', 'server',
                'client', 'frontend', 'backend', 'architecture', 'design pattern'
            ]
            has_technical_terms = any(term in answer_text.lower() 
                                    for term in technical_indicators)
        
        # Vague if: too short OR lacks details OR (in technical stage and no technical terms)
        is_vague = (
            word_count < 15 or 
            (word_count < 30 and not has_specifics) or
            (self.current_stage >= 2 and word_count < 40 and not has_technical_terms)
        )
        
        # Limit follow-ups to avoid endless loops
        if self.follow_up_count >= 2:
            return False
            
        return is_vague
    
    def advance_stage(self):
        """
        Move to the next interview stage
        """
        if self.current_stage < len(self.STAGES) - 1:
            self.current_stage += 1
            self.follow_up_count = 0
            
    def get_stage_question(self) -> str:
        """
        Get an appropriate initial question for the current stage
        
        Returns:
            Stage-appropriate question based on job role and skills
        """
        stage = self.STAGES[self.current_stage]
        
        # Primary skill for technical questions
        primary_skill = self.resume_skills[0] if self.resume_skills else "your main technical skill"
        
        questions = {
            "greeting": [
                f"Hi! Thanks for joining. Tell me, what's your current role?",
                f"Good to meet you! Can you briefly describe what you're working on now?",
                f"Thanks for your time today! What's keeping you busy in your current position?"
            ],
            
            "experience_probe": [
                f"Great! Can you walk me through your most challenging project as a {self.job_role}?",
                f"Tell me about a recent project you're particularly proud of.",
                f"What's the most complex problem you've solved in your current role?",
                f"Describe a time when you had to learn something new quickly for a project."
            ],
            
            "technical_deep_dive": [
                f"Let's dive into {primary_skill}. How would you approach designing a scalable system?",
                f"If you had to optimize a slow {primary_skill} application, where would you start?",
                f"Walk me through how you'd architect a solution using {primary_skill}.",
                f"What's a technical challenge you faced with {primary_skill} and how did you solve it?"
            ],
            
            "behavioral": [
                "Tell me about a time you disagreed with a team member. How did you handle it?",
                "Describe a situation where you had to work under tight deadlines.",
                "Can you share an example of when you had to learn from a mistake?",
                "Tell me about a time you had to convince others to adopt your approach."
            ],
            
            "closing": [
                "That covers my questions! What would you like to know about the role?",
                "We're wrapping up. Do you have any questions about our team or company?",
                "Is there anything else you'd like me to know about your background?",
                "What questions do you have for me about this opportunity?"
            ]
        }
        
        # Get random question from stage
        stage_questions = questions.get(stage, ["Tell me more about yourself."])
        question = random.choice(stage_questions)
        
        # Track questions asked to avoid repetition
        self.questions_asked.append(question)
        
        return question
    
    def get_followup_question(self, previous_answer: str) -> str:
        """
        Generate a follow-up question based on vague answer
        
        Args:
            previous_answer: The candidate's previous response
            
        Returns:
            Appropriate follow-up question
        """
        self.follow_up_count += 1
        
        stage = self.STAGES[self.current_stage]
        
        followup_prompts = {
            "greeting": [
                "Can you tell me more about your day-to-day responsibilities?",
                "What's the most interesting part of your current work?"
            ],
            
            "experience_probe": [
                "Can you give me more specific details about that project?",
                "What technologies did you use and why?",
                "What was your specific role and contribution?",
                "What challenges did you encounter and how did you overcome them?"
            ],
            
            "technical_deep_dive": [
                "Can you walk me through your technical approach step by step?",
                "What specific tools or frameworks would you choose?",
                "How would you handle potential scaling issues?",
                "What trade-offs would you consider in your design?"
            ],
            
            "behavioral": [
                "Can you give me more details about the situation?",
                "What specific actions did you take?",
                "What was the outcome or result?",
                "What did you learn from that experience?"
            ],
            
            "closing": [
                "Is there anything specific about the role you'd like to know?",
                "What draws you to this opportunity?"
            ]
        }
        
        prompts = followup_prompts.get(stage, ["Can you elaborate on that?"])
        return random.choice(prompts)
    
    def record_interaction(self, question: str, answer: str, is_followup: bool = False):
        """
        Record question-answer interaction for context
        
        Args:
            question: Question asked
            answer: Candidate's response
            is_followup: Whether this was a follow-up question
        """
        self.conversation_history.append({
            'stage': self.STAGES[self.current_stage],
            'question': question,
            'answer': answer,
            'is_followup': is_followup,
            'word_count': len(answer.split()),
            'needed_followup': self.should_ask_followup(answer)
        })
    
    def get_stage_progress(self) -> Dict:
        """
        Get current progress information
        
        Returns:
            Dictionary with stage progress details
        """
        return {
            'current_stage': self.STAGES[self.current_stage],
            'stage_number': self.current_stage + 1,
            'total_stages': len(self.STAGES),
            'progress_percent': ((self.current_stage + 1) / len(self.STAGES)) * 100,
            'follow_up_count': self.follow_up_count,
            'questions_asked_count': len(self.questions_asked),
            'conversation_length': len(self.conversation_history)
        }
    
    def is_interview_complete(self) -> bool:
        """
        Check if interview has reached the end
        
        Returns:
            True if at closing stage with sufficient interaction
        """
        return (self.current_stage >= len(self.STAGES) - 1 and 
                len(self.conversation_history) >= 2)
    
    def get_interview_summary(self) -> Dict:
        """
        Generate summary of interview performance
        
        Returns:
            Dictionary with interview assessment
        """
        if not self.conversation_history:
            return {'status': 'no_interaction'}
            
        total_words = sum(item['word_count'] for item in self.conversation_history)
        avg_response_length = total_words / len(self.conversation_history)
        followups_needed = sum(1 for item in self.conversation_history if item['needed_followup'])
        
        return {
            'stages_completed': self.current_stage + 1,
            'total_interactions': len(self.conversation_history),
            'average_response_length': avg_response_length,
            'followups_needed': followups_needed,
            'engagement_score': min(100, (avg_response_length / 20) * 100),
            'completion_percentage': ((self.current_stage + 1) / len(self.STAGES)) * 100,
            'weak_areas': self.weak_areas,
            'strong_areas': [skill for skill in self.resume_skills 
                           if skill.lower() in ' '.join(item['answer'].lower() 
                           for item in self.conversation_history)]
        }
