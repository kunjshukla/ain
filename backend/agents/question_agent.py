# agents/question_agent.py - Voice-enabled Question Generation Agent
from services.ollama_service import generate_response, is_ollama_ready
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionRequest(BaseModel):
    domain: str = "Software Engineering"
    difficulty: str = "Medium"
    topic: Optional[str] = None
    previous_questions: Optional[list] = None
    user_level: str = "Intermediate"

class QuestionResponse(BaseModel):
    question: str
    domain: str
    difficulty: str
    topic: str
    success: bool
    error: Optional[str] = None

class QuestionAgent:
    """Agent responsible for generating interview questions"""
    
    def __init__(self):
        self.name = "QuestionAgent"
        self.model = "mistral"  # Default Ollama model
    
    def generate_question(self, request: QuestionRequest) -> QuestionResponse:
        """Generate a contextual interview question"""
        
        # Check if Ollama is available
        if not is_ollama_ready():
            logger.warning("Ollama is not available, using fallback question")
            fallback_question = self._get_fallback_question(request.domain, request.difficulty)
            return QuestionResponse(
                question=fallback_question,
                domain=request.domain,
                difficulty=request.difficulty,
                topic=request.topic or "General",
                success=True,  # Still successful, just using fallback
                error=None
            )
        
        try:
            
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(request)
            
            logger.info(f"Generating {request.difficulty} question for {request.domain}")
            
            # Generate question using new Ollama service
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = generate_response(full_prompt)
            
            if not response:
                return QuestionResponse(
                    question="Could not generate question. Please try again.",
                    domain=request.domain,
                    difficulty=request.difficulty,
                    topic=request.topic or "General",
                    success=False,
                    error="Question generation failed"
                )
            
            # Parse and clean the response
            question = self._parse_question_response(response)
            
            return QuestionResponse(
                question=question,
                domain=request.domain,
                difficulty=request.difficulty,
                topic=request.topic or "General",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            fallback_question = self._get_fallback_question(request.domain, request.difficulty)
            
            return QuestionResponse(
                question=fallback_question,
                domain=request.domain,
                difficulty=request.difficulty,
                topic=request.topic or "General",
                success=False,
                error=str(e)
            )
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the question agent"""
        return """You are an expert technical interviewer for a voice-based interview system. 
Your role is to generate challenging, realistic interview questions that test both technical knowledge and problem-solving skills.

Guidelines:
- Generate clear, concise questions suitable for voice interaction
- Avoid questions requiring complex visual diagrams or extensive code writing
- Focus on concepts, problem-solving approaches, and verbal explanations
- Questions should be answerable in 2-3 minutes of speaking
- Adapt difficulty based on the specified level
- Make questions engaging and realistic to actual interviews

Response format: Return ONLY the question text, nothing else."""
    
    def _build_user_prompt(self, request: QuestionRequest) -> str:
        """Build user prompt based on request parameters"""
        
        prompt = f"""Generate a {request.difficulty.lower()} level interview question for {request.domain}.

Target Level: {request.user_level}
"""
        
        if request.topic:
            prompt += f"Specific Topic: {request.topic}\n"
        
        if request.previous_questions:
            prompt += f"\nAvoid repeating these previous questions:\n"
            for i, q in enumerate(request.previous_questions[-3:], 1):  # Last 3 questions
                prompt += f"{i}. {q}\n"
        
        # Add domain-specific guidance
        domain_guidance = self._get_domain_guidance(request.domain)
        prompt += f"\n{domain_guidance}\n"
        
        prompt += "\nGenerate ONE interview question:"
        
        return prompt
    
    def _get_domain_guidance(self, domain: str) -> str:
        """Get domain-specific guidance for question generation"""
        
        guidance_map = {
            "Software Engineering": """Focus on: algorithms, data structures, system design, coding best practices, 
debugging, software architecture, testing, or problem-solving approaches.""",
            
            "Data Science": """Focus on: statistical concepts, machine learning algorithms, data preprocessing, 
model evaluation, hypothesis testing, or data interpretation.""",
            
            "Product Management": """Focus on: product strategy, user research, prioritization frameworks, 
stakeholder management, metrics, or product launch strategies.""",
            
            "System Design": """Focus on: scalability, distributed systems, database design, caching, 
load balancing, microservices, or architecture patterns.""",
            
            "Behavioral": """Focus on: leadership scenarios, conflict resolution, teamwork, 
communication skills, decision-making, or past experiences."""
        }
        
        return guidance_map.get(domain, "Focus on core concepts and practical problem-solving.")
    
    def _parse_question_response(self, response: str) -> str:
        """Parse and clean the question response from LLM"""
        
        # Clean up the response
        question = response.strip()
        
        # Remove any prefixes like "Question:" or numbering
        question = question.replace("Question:", "").strip()
        question = question.replace("Q:", "").strip()
        
        # Remove any numbering at the start
        if question and question[0].isdigit():
            question = ". ".join(question.split(". ")[1:])
        
        # Ensure it ends with a question mark
        if question and not question.endswith("?"):
            question += "?"
        
        return question
    
    def _get_fallback_question(self, domain: str, difficulty: str) -> str:
        """Get fallback questions when LLM is unavailable"""
        
        fallback_questions = {
            "Software Engineering": {
                "Easy": [
                    "What is the difference between a stack and a queue?",
                    "Explain what an API is and how it works.",
                    "What is the purpose of version control systems like Git?",
                    "Describe what a database index is and why it's useful."
                ],
                "Medium": [
                    "How would you approach debugging a performance issue in a web application?",
                    "Explain the concept of RESTful APIs and their key principles.",
                    "What are the trade-offs between SQL and NoSQL databases?",
                    "How would you design a URL shortener service like bit.ly?"
                ],
                "Hard": [
                    "Design the architecture for a real-time chat application that can handle millions of users.",
                    "How would you implement a distributed caching system?",
                    "Explain how you would design a rate limiting system for an API.",
                    "Describe your approach to building a scalable microservices architecture."
                ]
            },
            "Data Science": {
                "Easy": [
                    "What is the difference between supervised and unsupervised learning?",
                    "Explain what overfitting is and how to prevent it.",
                    "What is the difference between classification and regression?",
                    "Describe what feature engineering is and why it's important."
                ],
                "Medium": [
                    "How would you handle missing data in a dataset?",
                    "Explain cross-validation and why it's used in machine learning.",
                    "What are some techniques to prevent overfitting in neural networks?",
                    "How would you approach building a predictive model from scratch?"
                ],
                "Hard": [
                    "Explain how you would build a recommendation system for an e-commerce platform.",
                    "How would you design an A/B testing framework for a large-scale application?",
                    "Describe your approach to detecting anomalies in time-series data.",
                    "How would you build a real-time fraud detection system?"
                ]
            },
            "Behavioral": {
                "Easy": [
                    "Tell me about a challenging project you worked on.",
                    "What motivates you as a software engineer?",
                    "Describe your ideal work environment.",
                    "What technical skills are you currently working to improve?"
                ],
                "Medium": [
                    "Describe a time when you had to work with a difficult team member.",
                    "Tell me about a time when you had to learn a new technology quickly.",
                    "How do you prioritize tasks when you have multiple deadlines?",
                    "Describe a situation where you had to make a difficult technical decision."
                ],
                "Hard": [
                    "How do you handle competing priorities and tight deadlines?",
                    "Tell me about a time when a project failed and what you learned from it.",
                    "Describe how you would approach leading a team on a high-stakes project.",
                    "How do you handle disagreements with your manager or senior engineers?"
                ]
            }
        }
        
        import random
        domain_questions = fallback_questions.get(domain, fallback_questions["Software Engineering"])
        questions_list = domain_questions.get(difficulty, domain_questions["Medium"])
        return random.choice(questions_list)

# Global instance
question_agent = QuestionAgent()

# Convenience function
def generate_question(domain: str = "Software Engineering", 
                     difficulty: str = "Medium",
                     topic: str = None,
                     previous_questions: list = None,
                     user_level: str = "Intermediate") -> str:
    """Generate a question and return just the text"""
    
    request = QuestionRequest(
        domain=domain,
        difficulty=difficulty,
        topic=topic,
        previous_questions=previous_questions,
        user_level=user_level
    )
    
    response = question_agent.generate_question(request)
    return response.question
