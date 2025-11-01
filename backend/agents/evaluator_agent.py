# agents/evaluator_agent.py - Voice-enabled Answer Evaluation Agent
from utils.ollama_client import query_ollama, check_ollama_health
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluationRequest(BaseModel):
    user_answer: str
    question: str
    domain: str = "Software Engineering"
    expected_topics: Optional[list] = None
    difficulty: str = "Medium"

class EvaluationResponse(BaseModel):
    score: float  # 0-10 scale
    feedback: str
    strengths: list
    areas_for_improvement: list
    domain: str
    success: bool
    error: Optional[str] = None

class EvaluatorAgent:
    """Agent responsible for evaluating user answers in voice interviews"""
    
    def __init__(self):
        self.name = "EvaluatorAgent"
        self.model = "mistral"
    
    def evaluate_answer(self, request: EvaluationRequest) -> EvaluationResponse:
        """Evaluate user's spoken answer to an interview question"""
        
        # Check if Ollama is available
        if not check_ollama_health():
            logger.error("Ollama is not available for evaluation")
            return self._fallback_evaluation(request)
        
        try:
            # Build evaluation prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_evaluation_prompt(request)
            
            logger.info(f"Evaluating answer for {request.domain} question")
            
            # Query Ollama for evaluation
            response = query_ollama(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3  # Lower temperature for consistent evaluation
            )
            
            # Parse the evaluation response
            evaluation = self._parse_evaluation_response(response, request)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
            return self._fallback_evaluation(request, str(e))
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the evaluator agent"""
        return """You are an expert technical interviewer evaluating answers in a voice-based interview system.

Your job is to:
1. Assess technical accuracy and depth of understanding
2. Evaluate communication clarity and structure
3. Identify strengths and areas for improvement
4. Provide constructive, actionable feedback
5. Score answers on a 0-10 scale where:
   - 9-10: Exceptional (detailed, accurate, well-structured)
   - 7-8: Good (mostly correct with clear communication)
   - 5-6: Average (basic understanding, some gaps)
   - 3-4: Below Average (significant gaps or unclear)
   - 0-2: Poor (major misconceptions or very unclear)

Response format: Return a JSON object with:
{
  "score": [numeric score 0-10],
  "feedback": "[detailed feedback paragraph]",
  "strengths": ["strength 1", "strength 2", ...],
  "areas_for_improvement": ["area 1", "area 2", ...]
}"""
    
    def _build_evaluation_prompt(self, request: EvaluationRequest) -> str:
        """Build evaluation prompt based on the request"""
        
        prompt = f"""Evaluate this interview answer:

QUESTION: {request.question}

USER'S ANSWER: {request.user_answer}

CONTEXT:
- Domain: {request.domain}
- Difficulty Level: {request.difficulty}
"""
        
        if request.expected_topics:
            prompt += f"- Expected Topics: {', '.join(request.expected_topics)}\n"
        
        prompt += f"""
EVALUATION CRITERIA:
- Technical accuracy and completeness
- Communication clarity and organization
- Depth of understanding
- Practical relevance
- Problem-solving approach

Provide evaluation in JSON format as specified in the system prompt."""
        
        return prompt
    
    def _parse_evaluation_response(self, response: str, request: EvaluationRequest) -> EvaluationResponse:
        """Parse LLM evaluation response into structured format"""
        
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                evaluation_data = json.loads(json_str)
                
                return EvaluationResponse(
                    score=float(evaluation_data.get('score', 5.0)),
                    feedback=evaluation_data.get('feedback', 'Evaluation completed'),
                    strengths=evaluation_data.get('strengths', []),
                    areas_for_improvement=evaluation_data.get('areas_for_improvement', []),
                    domain=request.domain,
                    success=True
                )
            else:
                # Fallback parsing if JSON not found
                return self._parse_text_evaluation(response, request)
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON evaluation, using text parsing")
            return self._parse_text_evaluation(response, request)
        except Exception as e:
            logger.error(f"Error parsing evaluation: {e}")
            return self._fallback_evaluation(request, str(e))
    
    def _parse_text_evaluation(self, response: str, request: EvaluationRequest) -> EvaluationResponse:
        """Parse text-based evaluation when JSON parsing fails"""
        
        # Extract score (look for patterns like "Score: 7" or "7/10")
        score = 5.0  # default
        lines = response.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if 'score' in line_lower or '/10' in line:
                # Try to extract numeric score
                import re
                numbers = re.findall(r'\d+\.?\d*', line)
                if numbers:
                    potential_score = float(numbers[0])
                    if 0 <= potential_score <= 10:
                        score = potential_score
                        break
        
        # Use entire response as feedback
        feedback = response.strip()
        
        # Basic strengths and improvements extraction
        strengths = []
        areas_for_improvement = []
        
        if "strength" in response.lower() or "good" in response.lower():
            strengths.append("Demonstrates understanding of key concepts")
        
        if "improve" in response.lower() or "consider" in response.lower():
            areas_for_improvement.append("Consider expanding on technical details")
        
        return EvaluationResponse(
            score=score,
            feedback=feedback,
            strengths=strengths,
            areas_for_improvement=areas_for_improvement,
            domain=request.domain,
            success=True
        )
    
    def _fallback_evaluation(self, request: EvaluationRequest, error: str = None) -> EvaluationResponse:
        """Provide fallback evaluation when LLM is unavailable"""
        
        # Simple keyword-based evaluation
        answer_lower = request.user_answer.lower()
        answer_length = len(request.user_answer.split())
        
        # Basic scoring based on answer length and keywords
        score = 5.0  # neutral starting point
        
        if answer_length < 10:
            score = max(2.0, score - 2.0)
        elif answer_length > 50:
            score = min(8.0, score + 1.0)
        
        # Domain-specific keyword checking
        domain_keywords = self._get_domain_keywords(request.domain)
        keyword_matches = sum(1 for keyword in domain_keywords if keyword in answer_lower)
        
        if keyword_matches > 0:
            score = min(10.0, score + keyword_matches * 0.5)
        
        feedback = f"Your answer demonstrates {'good' if score >= 6 else 'basic'} understanding. "
        feedback += f"Answer length: {answer_length} words. "
        
        if keyword_matches > 0:
            feedback += f"Good use of relevant terminology ({keyword_matches} key terms identified)."
        else:
            feedback += "Consider using more specific technical terminology."
        
        return EvaluationResponse(
            score=round(score, 1),
            feedback=feedback,
            strengths=["Provided a response", "Engaged with the question"] if answer_length > 5 else [],
            areas_for_improvement=["Expand on technical details", "Provide more specific examples"],
            domain=request.domain,
            success=False,
            error=error or "LLM evaluation unavailable - using basic analysis"
        )
    
    def _get_domain_keywords(self, domain: str) -> list:
        """Get relevant keywords for domain-specific evaluation"""
        
        domain_keywords = {
            "Software Engineering": [
                "algorithm", "data structure", "complexity", "performance", "scalability",
                "testing", "debugging", "architecture", "design pattern", "database",
                "api", "framework", "library", "optimization", "security"
            ],
            "Data Science": [
                "model", "algorithm", "feature", "training", "validation", "dataset",
                "correlation", "regression", "classification", "clustering", "statistics",
                "machine learning", "neural network", "accuracy", "precision", "recall"
            ],
            "System Design": [
                "scalability", "load balancer", "database", "cache", "microservices",
                "distributed", "consistency", "availability", "partition", "replication",
                "sharding", "queue", "api gateway", "monitoring", "fault tolerance"
            ],
            "Behavioral": [
                "team", "leadership", "communication", "conflict", "challenge", "solution",
                "collaboration", "problem", "decision", "stakeholder", "priority", "deadline"
            ]
        }
        
        return domain_keywords.get(domain, [])

# Global instance
evaluator_agent = EvaluatorAgent()

# Convenience function
def evaluate_answer(user_answer: str, 
                   question: str,
                   domain: str = "Software Engineering",
                   difficulty: str = "Medium") -> Dict[str, Any]:
    """Evaluate an answer and return evaluation data"""
    
    request = EvaluationRequest(
        user_answer=user_answer,
        question=question,
        domain=domain,
        difficulty=difficulty
    )
    
    response = evaluator_agent.evaluate_answer(request)
    
    return {
        "score": response.score,
        "feedback": response.feedback,
        "strengths": response.strengths,
        "areas_for_improvement": response.areas_for_improvement,
        "success": response.success
    }
