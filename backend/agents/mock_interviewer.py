# agents/mock_interviewer.py
from typing import List, Dict, Any, Optional
import spacy
from spacy.language import Language

class MockInterviewerAgent:
    def __init__(self):
        self.nlp = self._get_nlp_model()
        self.questions = [
            "Tell me about yourself",
            "What is your greatest strength?",
            "Describe a challenge you faced and how you overcame it"
        ]
        
    def _get_nlp_model(self) -> Optional[Language]:
        """Try multiple fallback options for NLP model"""
        try:
            print("Attempting to load en_core_web_lg model...")
            return spacy.load("en_core_web_lg")
        except OSError:
            try:
                print("Warning: Falling back to small English model (en_core_web_sm)")
                return spacy.load("en_core_web_sm")
            except OSError:
                print("Critical: No spaCy model available. Using basic text matching.")
                return None
        
    def evaluate(self, answers: List[str]) -> Dict[str, Any]:
        # Handle any number of answers by using available questions or generating defaults
        questions = []
        
        # Use predefined questions if available, otherwise use generic ones
        for i in range(len(answers)):
            if i < len(self.questions):
                questions.append(self.questions[i])
            else:
                questions.append(f"Question {i+1}")
                
        # Truncate questions to match answers if needed
        questions = questions[:len(answers)]
            
        evaluations = []
        total_score = 0
        
        for i, (question, answer) in enumerate(zip(questions, answers)):
            evaluation = self._evaluate_answer(question, answer)
            evaluations.append({
                "question": question,
                "answer": answer,
                "evaluation": evaluation
            })
            total_score += evaluation["score"]
            
        avg_score = total_score / len(answers) if answers else 0
            
        return {
            "evaluations": evaluations,
            "average_score": avg_score,
            "improvement_areas": self._identify_improvement_areas(evaluations),
            "overall_feedback": self._generate_overall_feedback(avg_score)
        }
        
    def _evaluate_answer(self, question: str, answer: str) -> Dict[str, Any]:
        # Basic evaluation logic that works without NLP
        answer_length = len(answer.split())
        
        # Simple metrics based on answer length and keyword matching
        clarity = min(1.0, answer_length / 100) # Assumes longer answers are clearer up to a point
        
        # Check for question relevance by simple keyword matching
        question_keywords = set(question.lower().split())
        answer_keywords = set(answer.lower().split())
        common_keywords = question_keywords.intersection(answer_keywords)
        relevance = min(1.0, len(common_keywords) / max(1, len(question_keywords) * 0.5))
        
        # Depth based on answer length
        depth = min(1.0, answer_length / 150)  # Assumes deeper answers are longer up to a point
        
        # Calculate overall score
        score = (clarity + relevance + depth) / 3
        
        # Generate feedback based on scores
        feedback = self._generate_feedback(clarity, relevance, depth)
        
        return {
            "clarity": round(clarity, 2),
            "relevance": round(relevance, 2),
            "depth": round(depth, 2),
            "score": round(score, 2),
            "feedback": feedback
        }
        
    def _generate_feedback(self, clarity: float, relevance: float, depth: float) -> str:
        """Generate feedback based on the evaluation metrics"""
        feedback_parts = []
        
        if clarity < 0.5:
            feedback_parts.append("Your answer could be clearer and more structured.")
        elif clarity < 0.8:
            feedback_parts.append("Your answer is reasonably clear, but could be more concise.")
        else:
            feedback_parts.append("Your answer is very clear and well-structured.")
            
        if relevance < 0.5:
            feedback_parts.append("Your response doesn't fully address the question asked.")
        elif relevance < 0.8:
            feedback_parts.append("Your answer is relevant but could focus more on the specific question.")
        else:
            feedback_parts.append("Your answer directly addresses the question.")
            
        if depth < 0.5:
            feedback_parts.append("Consider providing more details and examples.")
        elif depth < 0.8:
            feedback_parts.append("Good depth, but could include more specific examples.")
        else:
            feedback_parts.append("Excellent depth with good examples and details.")
            
        return " ".join(feedback_parts)
        
    def _identify_improvement_areas(self, evaluations: List[Dict[str, Any]]) -> List[str]:
        """Identify areas for improvement based on evaluations"""
        areas = []
        avg_clarity = sum(e["evaluation"]["clarity"] for e in evaluations) / len(evaluations)
        avg_relevance = sum(e["evaluation"]["relevance"] for e in evaluations) / len(evaluations)
        avg_depth = sum(e["evaluation"]["depth"] for e in evaluations) / len(evaluations)
        
        if avg_clarity < 0.7:
            areas.append("Improve clarity and structure in your responses")
        if avg_relevance < 0.7:
            areas.append("Focus more on directly answering the questions asked")
        if avg_depth < 0.7:
            areas.append("Provide more specific examples and details in your answers")
            
        return areas
        
    def _generate_overall_feedback(self, avg_score: float) -> str:
        """Generate overall feedback based on average score"""
        if avg_score < 0.5:
            return "Your interview responses need significant improvement. Focus on addressing questions more directly and providing concrete examples."
        elif avg_score < 0.7:
            return "Your interview responses are satisfactory but could be improved. Work on clarity and providing more detailed examples."
        elif avg_score < 0.9:
            return "Your interview responses are good. Continue to refine your answers with more specific examples and concise delivery."
        else:
            return "Your interview responses are excellent. You communicate clearly, directly address questions, and provide strong examples."