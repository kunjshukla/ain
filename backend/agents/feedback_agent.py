# agents/feedback_agent.py - Voice-enabled Feedback Generation Agent
from utils.ollama_client import query_ollama, check_ollama_health
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeedbackRequest(BaseModel):
    user_answer: str
    question: str
    evaluation_score: float
    evaluation_feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]
    domain: str = "Software Engineering"
    user_level: str = "Intermediate"

class FeedbackResponse(BaseModel):
    feedback_text: str
    follow_up_hints: List[str]
    next_steps: List[str]
    encouragement: str
    domain: str
    success: bool
    error: Optional[str] = None

class FeedbackAgent:
    """Agent responsible for generating constructive feedback and guidance"""
    
    def __init__(self):
        self.name = "FeedbackAgent"
        self.model = "mistral"
    
    def generate_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        """Generate comprehensive feedback for voice interview responses"""
        
        # Check if Ollama is available
        if not check_ollama_health():
            logger.error("Ollama is not available for feedback generation")
            return self._fallback_feedback(request)
        
        try:
            # Build feedback prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_feedback_prompt(request)
            
            logger.info(f"Generating feedback for {request.domain} answer (score: {request.evaluation_score})")
            
            # Query Ollama for feedback generation
            response = query_ollama(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7  # Moderate temperature for helpful but consistent feedback
            )
            
            # Parse and structure the feedback response
            feedback = self._parse_feedback_response(response, request)
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error during feedback generation: {e}")
            return self._fallback_feedback(request, str(e))
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the feedback agent"""
        return """You are an expert interview coach providing constructive feedback for voice-based interviews.

Your role is to:
1. Provide encouraging and constructive feedback
2. Highlight specific strengths in the candidate's response
3. Offer actionable improvement suggestions
4. Provide follow-up hints for deeper understanding
5. Suggest next steps for continued learning
6. Maintain a supportive and professional tone
7. Keep feedback concise and suitable for voice delivery

Guidelines:
- Start with positive observations when possible
- Be specific about what was done well
- Provide concrete suggestions for improvement
- Use encouraging language that motivates learning
- Keep feedback focused and actionable
- Structure feedback clearly for voice delivery

Response structure:
- Main feedback paragraph (conversational tone)
- 2-3 specific follow-up hints
- 2-3 next steps for improvement
- Encouraging closing statement"""
    
    def _build_feedback_prompt(self, request: FeedbackRequest) -> str:
        """Build feedback prompt based on evaluation results"""
        
        prompt = f"""Provide coaching feedback for this interview response:

QUESTION: {request.question}
USER'S ANSWER: {request.user_answer}

EVALUATION RESULTS:
- Score: {request.evaluation_score}/10
- Feedback: {request.evaluation_feedback}
- Strengths: {', '.join(request.strengths) if request.strengths else 'None identified'}
- Areas for Improvement: {', '.join(request.areas_for_improvement) if request.areas_for_improvement else 'None identified'}

CONTEXT:
- Domain: {request.domain}
- User Level: {request.user_level}

Please provide:

1. MAIN FEEDBACK (2-3 sentences): Constructive overview focusing on strengths and key areas for growth

2. FOLLOW-UP HINTS (2-3 specific hints): Specific questions or concepts to explore further

3. NEXT STEPS (2-3 actionable items): Concrete actions for improvement

4. ENCOURAGEMENT (1 sentence): Motivating closing statement

Keep the tone conversational and supportive, suitable for voice delivery."""
        
        return prompt
    
    def _parse_feedback_response(self, response: str, request: FeedbackRequest) -> FeedbackResponse:
        """Parse LLM feedback response into structured format"""
        
        try:
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            
            feedback_text = ""
            follow_up_hints = []
            next_steps = []
            encouragement = ""
            
            current_section = None
            
            for line in lines:
                line_lower = line.lower()
                
                # Identify sections
                if any(marker in line_lower for marker in ['main feedback', 'feedback', '1.']):
                    current_section = 'feedback'
                    if ':' in line:
                        feedback_text += line.split(':', 1)[1].strip() + " "
                elif any(marker in line_lower for marker in ['follow-up', 'hints', '2.']):
                    current_section = 'hints'
                    if ':' in line:
                        hint = line.split(':', 1)[1].strip()
                        if hint:
                            follow_up_hints.append(hint)
                elif any(marker in line_lower for marker in ['next steps', 'actions', '3.']):
                    current_section = 'steps'
                    if ':' in line:
                        step = line.split(':', 1)[1].strip()
                        if step:
                            next_steps.append(step)
                elif any(marker in line_lower for marker in ['encouragement', 'closing', '4.']):
                    current_section = 'encouragement'
                    if ':' in line:
                        encouragement += line.split(':', 1)[1].strip() + " "
                else:
                    # Continue current section
                    if current_section == 'feedback':
                        feedback_text += line + " "
                    elif current_section == 'hints' and line.startswith(('-', '•', '*')):
                        follow_up_hints.append(line.lstrip('-•* '))
                    elif current_section == 'steps' and line.startswith(('-', '•', '*')):
                        next_steps.append(line.lstrip('-•* '))
                    elif current_section == 'encouragement':
                        encouragement += line + " "
            
            # Fallback if sections not clearly identified
            if not feedback_text:
                feedback_text = " ".join(lines[:3])  # First few lines as main feedback
            
            if not follow_up_hints:
                follow_up_hints = self._generate_default_hints(request)
            
            if not next_steps:
                next_steps = self._generate_default_steps(request)
            
            if not encouragement:
                encouragement = "Keep practicing and you'll continue to improve!"
            
            return FeedbackResponse(
                feedback_text=feedback_text.strip(),
                follow_up_hints=follow_up_hints[:3],  # Limit to 3
                next_steps=next_steps[:3],  # Limit to 3
                encouragement=encouragement.strip(),
                domain=request.domain,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error parsing feedback response: {e}")
            return self._fallback_feedback(request, str(e))
    
    def _generate_default_hints(self, request: FeedbackRequest) -> List[str]:
        """Generate default follow-up hints based on domain"""
        
        domain_hints = {
            "Software Engineering": [
                "Consider the time and space complexity of your solution",
                "Think about edge cases and error handling",
                "Explore alternative approaches or optimizations"
            ],
            "Data Science": [
                "Consider the assumptions behind your approach",
                "Think about data quality and preprocessing steps",
                "Explore different evaluation metrics"
            ],
            "System Design": [
                "Consider scalability and performance bottlenecks",
                "Think about fault tolerance and reliability",
                "Explore trade-offs between consistency and availability"
            ],
            "Behavioral": [
                "Reflect on the impact of your actions",
                "Consider different stakeholder perspectives",
                "Think about lessons learned and future applications"
            ]
        }
        
        return domain_hints.get(request.domain, domain_hints["Software Engineering"])
    
    def _generate_default_steps(self, request: FeedbackRequest) -> List[str]:
        """Generate default next steps based on evaluation score"""
        
        if request.evaluation_score >= 7:
            return [
                "Practice explaining complex concepts more concisely",
                "Explore advanced topics in this area",
                "Try teaching this concept to someone else"
            ]
        elif request.evaluation_score >= 5:
            return [
                "Review the fundamental concepts covered",
                "Practice with similar questions",
                "Study real-world examples and case studies"
            ]
        else:
            return [
                "Start with basic concepts and build up gradually",
                "Find additional learning resources on this topic",
                "Practice explaining concepts out loud"
            ]
    
    def _fallback_feedback(self, request: FeedbackRequest, error: str = None) -> FeedbackResponse:
        """Provide fallback feedback when LLM is unavailable"""
        
        score = request.evaluation_score
        
        # Generate basic feedback based on score
        if score >= 8:
            feedback_text = "Excellent response! You demonstrated strong understanding and clear communication."
        elif score >= 6:
            feedback_text = "Good answer! You covered the key points well. There's room for some refinement in your explanation."
        elif score >= 4:
            feedback_text = "Your response shows basic understanding. Focus on providing more specific details and examples."
        else:
            feedback_text = "This is a good start! Let's work on building stronger foundational knowledge in this area."
        
        # Add specific feedback from evaluation
        if request.strengths:
            feedback_text += f" Your strengths include: {', '.join(request.strengths)}."
        
        follow_up_hints = self._generate_default_hints(request)
        next_steps = self._generate_default_steps(request)
        encouragement = "Every interview is a learning opportunity. Keep practicing!"
        
        return FeedbackResponse(
            feedback_text=feedback_text,
            follow_up_hints=follow_up_hints,
            next_steps=next_steps,
            encouragement=encouragement,
            domain=request.domain,
            success=False,
            error=error or "LLM feedback unavailable - using structured feedback"
        )

# Global instance
feedback_agent = FeedbackAgent()

# Convenience function
def generate_feedback(user_answer: str,
                     question: str,
                     evaluation_score: float,
                     evaluation_feedback: str,
                     strengths: List[str] = None,
                     areas_for_improvement: List[str] = None,
                     domain: str = "Software Engineering",
                     user_level: str = "Intermediate") -> Dict[str, Any]:
    """Generate feedback and return structured response"""
    
    request = FeedbackRequest(
        user_answer=user_answer,
        question=question,
        evaluation_score=evaluation_score,
        evaluation_feedback=evaluation_feedback,
        strengths=strengths or [],
        areas_for_improvement=areas_for_improvement or [],
        domain=domain,
        user_level=user_level
    )
    
    response = feedback_agent.generate_feedback(request)
    
    return {
        "feedback_text": response.feedback_text,
        "follow_up_hints": response.follow_up_hints,
        "next_steps": response.next_steps,
        "encouragement": response.encouragement,
        "success": response.success
    }
