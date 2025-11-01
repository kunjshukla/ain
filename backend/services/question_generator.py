# File: backend/services/question_generator.py
# Service to generate interview questions based on job role and resume skills using Ollama

import json
import logging
from typing import List, Dict, Any, Optional
from services.ollama_service import generate_response, is_ollama_ready

# Set up logging
logger = logging.getLogger(__name__)

class QuestionGenerator:
    """
    Service to generate interview questions using Ollama based on job role and resume skills
    """
    
    def __init__(self):
        self.default_questions = [
            "Tell me about yourself and your background.",
            "What interests you about this role?", 
            "Describe a challenging project you've worked on.",
            "How do you handle working under pressure?",
            "Where do you see yourself in 5 years?"
        ]
    
    def generate_questions(self, job_role: str, resume_skills: List[str], num_questions: int = 5) -> List[Dict[str, str]]:
        """
        Generate interview questions based on job role and resume skills
        
        Args:
            job_role: The target job role/position
            resume_skills: List of skills extracted from resume
            num_questions: Number of questions to generate (default: 5)
            
        Returns:
            List of dictionaries with 'question' field
        """
        try:
            # Check if Ollama is available
            if not is_ollama_ready():
                logger.warning("Ollama not available, using default questions")
                return self._get_default_questions(num_questions)
            
            # Create prompt for Ollama
            skills_text = ", ".join(resume_skills[:10])  # Limit to first 10 skills
            
            prompt = f"""Generate {num_questions} interview questions for a {job_role} position.

The candidate has the following skills: {skills_text}

Create questions that:
1. Test technical knowledge relevant to the role
2. Assess experience with their listed skills
3. Evaluate problem-solving abilities
4. Check cultural fit and motivation
5. Include both behavioral and technical questions

Return ONLY a valid JSON array in this exact format:
[
  {{"question": "Question 1 text here"}},
  {{"question": "Question 2 text here"}},
  {{"question": "Question 3 text here"}},
  {{"question": "Question 4 text here"}},
  {{"question": "Question 5 text here"}}
]

Make sure the JSON is valid and contains exactly {num_questions} questions."""

            logger.info(f"Generating {num_questions} questions for {job_role} role")
            
            # Call Ollama
            response = generate_response(prompt)
            
            if not response:
                logger.warning("No response from Ollama, using default questions")
                return self._get_default_questions(num_questions)
            
            # Parse JSON response
            questions = self._parse_questions_response(response, num_questions)
            
            if not questions:
                logger.warning("Failed to parse Ollama response, using default questions")
                return self._get_default_questions(num_questions)
            
            logger.info(f"Successfully generated {len(questions)} questions")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return self._get_default_questions(num_questions)
    
    def _parse_questions_response(self, response: str, expected_count: int) -> Optional[List[Dict[str, str]]]:
        """
        Parse Ollama response to extract questions JSON
        
        Args:
            response: Raw response from Ollama
            expected_count: Expected number of questions
            
        Returns:
            List of question dictionaries or None if parsing fails
        """
        try:
            # Find JSON array in response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON array found in Ollama response")
                return None
            
            json_str = response[json_start:json_end]
            questions_data = json.loads(json_str)
            
            # Validate structure
            if not isinstance(questions_data, list):
                logger.warning("Response is not a JSON array")
                return None
            
            # Validate each question
            validated_questions = []
            for item in questions_data:
                if isinstance(item, dict) and 'question' in item and item['question'].strip():
                    validated_questions.append({
                        'question': item['question'].strip()
                    })
            
            if len(validated_questions) != expected_count:
                logger.warning(f"Expected {expected_count} questions, got {len(validated_questions)}")
            
            return validated_questions if validated_questions else None
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing questions response: {e}")
            return None
    
    def _get_default_questions(self, num_questions: int) -> List[Dict[str, str]]:
        """
        Get default fallback questions
        
        Args:
            num_questions: Number of questions needed
            
        Returns:
            List of default question dictionaries
        """
        # Extend default questions if needed
        extended_questions = self.default_questions + [
            "What's your greatest professional achievement?",
            "How do you stay updated with industry trends?",
            "Describe your ideal work environment.",
            "What motivates you in your career?",
            "How do you approach learning new technologies?"
        ]
        
        # Return the requested number of questions
        selected_questions = extended_questions[:num_questions]
        
        return [{'question': q} for q in selected_questions]
    
    def generate_role_specific_questions(self, job_role: str, num_questions: int = 5) -> List[Dict[str, str]]:
        """
        Generate questions specific to a job role without considering resume skills
        
        Args:
            job_role: The target job role/position
            num_questions: Number of questions to generate
            
        Returns:
            List of role-specific question dictionaries
        """
        # Common skills for different roles
        role_skills_map = {
            "software engineer": ["programming", "algorithms", "system design", "debugging"],
            "data scientist": ["machine learning", "statistics", "python", "data analysis"],
            "product manager": ["strategy", "roadmap", "stakeholder management", "analytics"],
            "designer": ["user experience", "prototyping", "design thinking", "visual design"],
            "marketing": ["campaigns", "analytics", "content creation", "market research"],
            "sales": ["negotiation", "relationship building", "pipeline management", "closing"],
        }
        
        # Get relevant skills for the role
        role_lower = job_role.lower()
        relevant_skills = []
        
        for role_key, skills in role_skills_map.items():
            if role_key in role_lower:
                relevant_skills = skills
                break
        
        if not relevant_skills:
            relevant_skills = ["problem solving", "communication", "teamwork", "leadership"]
        
        return self.generate_questions(job_role, relevant_skills, num_questions)
    
    def generate_technical_questions(self, skills: List[str], num_questions: int = 3) -> List[Dict[str, str]]:
        """
        Generate technical questions focused on specific skills
        
        Args:
            skills: List of technical skills to focus on
            num_questions: Number of technical questions to generate
            
        Returns:
            List of technical question dictionaries
        """
        if not skills:
            return self._get_default_technical_questions(num_questions)
        
        try:
            if not is_ollama_ready():
                return self._get_default_technical_questions(num_questions)
            
            skills_text = ", ".join(skills[:8])  # Limit to first 8 skills
            
            prompt = f"""Generate {num_questions} technical interview questions focused on these skills: {skills_text}

Create questions that:
1. Test practical knowledge and implementation
2. Assess problem-solving with these technologies
3. Evaluate depth of understanding
4. Include scenario-based questions

Return ONLY a valid JSON array:
[
  {{"question": "Technical question 1"}},
  {{"question": "Technical question 2"}},
  {{"question": "Technical question 3"}}
]

Make the questions specific and practical."""
            
            response = generate_response(prompt)
            
            if response:
                questions = self._parse_questions_response(response, num_questions)
                if questions:
                    return questions
            
            return self._get_default_technical_questions(num_questions)
            
        except Exception as e:
            logger.error(f"Error generating technical questions: {e}")
            return self._get_default_technical_questions(num_questions)
    
    def _get_default_technical_questions(self, num_questions: int) -> List[Dict[str, str]]:
        """Get default technical questions"""
        default_tech_questions = [
            "Describe your approach to debugging a complex issue.",
            "How do you ensure code quality in your projects?",
            "Explain a technical challenge you overcame recently.",
            "How do you stay current with new technologies?",
            "Describe your experience with version control and collaboration."
        ]
        
        selected = default_tech_questions[:num_questions]
        return [{'question': q} for q in selected]

# Global instance
question_generator = QuestionGenerator()

# Convenience functions
def generate_interview_questions(job_role: str, resume_skills: List[str], num_questions: int = 5) -> List[Dict[str, str]]:
    """
    Generate interview questions based on job role and resume skills
    
    Args:
        job_role: Target job position
        resume_skills: Skills from candidate's resume
        num_questions: Number of questions to generate
        
    Returns:
        List of question dictionaries with 'question' field
    """
    return question_generator.generate_questions(job_role, resume_skills, num_questions)

def generate_role_questions(job_role: str, num_questions: int = 5) -> List[Dict[str, str]]:
    """
    Generate role-specific questions without resume context
    
    Args:
        job_role: Target job position
        num_questions: Number of questions to generate
        
    Returns:
        List of question dictionaries
    """
    return question_generator.generate_role_specific_questions(job_role, num_questions)

def generate_tech_questions(skills: List[str], num_questions: int = 3) -> List[Dict[str, str]]:
    """
    Generate technical questions for specific skills
    
    Args:
        skills: Technical skills to focus on
        num_questions: Number of questions to generate
        
    Returns:
        List of technical question dictionaries
    """
    return question_generator.generate_technical_questions(skills, num_questions)

# Test function
def test_question_generator():
    """Test the question generator functionality"""
    print("🧪 Testing Question Generator")
    print("=" * 40)
    
    # Test 1: Basic question generation
    print("\n1. Testing basic question generation...")
    job_role = "Software Engineer"
    skills = ["Python", "Django", "React", "AWS", "Docker"]
    
    questions = generate_interview_questions(job_role, skills, 3)
    
    print(f"Generated {len(questions)} questions:")
    for i, q in enumerate(questions, 1):
        print(f"   {i}. {q['question']}")
    
    # Test 2: Role-specific questions
    print("\n2. Testing role-specific questions...")
    role_questions = generate_role_questions("Data Scientist", 2)
    
    print(f"Role-specific questions:")
    for i, q in enumerate(role_questions, 1):
        print(f"   {i}. {q['question']}")
    
    # Test 3: Technical questions
    print("\n3. Testing technical questions...")
    tech_skills = ["Machine Learning", "Python", "TensorFlow"]
    tech_questions = generate_tech_questions(tech_skills, 2)
    
    print(f"Technical questions:")
    for i, q in enumerate(tech_questions, 1):
        print(f"   {i}. {q['question']}")
    
    print("\n✅ Question generator test completed!")

if __name__ == "__main__":
    test_question_generator()
