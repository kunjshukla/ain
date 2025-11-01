"""
AI Service Module
Handles all AI-related operations and agent management
"""

from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    """Centralized service for managing AI agents and operations"""
    
    def __init__(self):
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available AI agents"""
        # Resume Analyzer Agent
        try:
            from agents.resume_analyzer import ResumeAnalyzerAgent
            self.agents['resume'] = ResumeAnalyzerAgent()
            logger.info("Resume Analyzer Agent initialized")
        except ImportError:
            try:
                from backend.agents.resume_analyzer import ResumeAnalyzerAgent
                self.agents['resume'] = ResumeAnalyzerAgent()
                logger.info("Resume Analyzer Agent initialized")
            except ImportError as e:
                logger.warning(f"Resume Analyzer Agent not available: {e}")
                self.agents['resume'] = None
        
        # Mock Interviewer Agent
        try:
            from agents.mock_interviewer import MockInterviewerAgent
            self.agents['interview'] = MockInterviewerAgent()
            logger.info("Mock Interviewer Agent initialized")
        except ImportError:
            try:
                from backend.agents.mock_interviewer import MockInterviewerAgent
                self.agents['interview'] = MockInterviewerAgent()
                logger.info("Mock Interviewer Agent initialized")
            except ImportError as e:
                logger.warning(f"Mock Interviewer Agent not available: {e}")
                self.agents['interview'] = None
        
        # DSA Evaluator Agent
        try:
            from agents.dsa_evaluator import DSAEvaluatorAgent
            self.agents['dsa'] = DSAEvaluatorAgent()
            logger.info("DSA Evaluator Agent initialized")
        except ImportError:
            try:
                from backend.agents.dsa_evaluator import DSAEvaluatorAgent
                self.agents['dsa'] = DSAEvaluatorAgent()
                logger.info("DSA Evaluator Agent initialized")
            except ImportError as e:
                logger.warning(f"DSA Evaluator Agent not available: {e}")
                self.agents['dsa'] = None
        
        # Behavioral Coach Agent
        try:
            from agents.behavioural_coach import BehavioralCoachAgent
            self.agents['behavioral'] = BehavioralCoachAgent()
            logger.info("Behavioral Coach Agent initialized")
        except ImportError:
            try:
                from backend.agents.behavioural_coach import BehavioralCoachAgent
                self.agents['behavioral'] = BehavioralCoachAgent()
                logger.info("Behavioral Coach Agent initialized")
            except ImportError as e:
                logger.warning(f"Behavioral Coach Agent not available: {e}")
                self.agents['behavioral'] = None
        
        # Performance Tracker Agent
        try:
            from agents.performance_tracker import PerformanceTrackerAgent
            self.agents['performance'] = PerformanceTrackerAgent()
            logger.info("Performance Tracker Agent initialized")
        except ImportError:
            try:
                from backend.agents.performance_tracker import PerformanceTrackerAgent
                self.agents['performance'] = PerformanceTrackerAgent()
                logger.info("Performance Tracker Agent initialized")
            except ImportError as e:
                logger.warning(f"Performance Tracker Agent not available: {e}")
                self.agents['performance'] = None
        
        # Orchestrator Agent
        try:
            from agents.orchestrator_agent import OrchestratorAgent
            self.agents['orchestrator'] = OrchestratorAgent()
            logger.info("Orchestrator Agent initialized")
        except ImportError:
            try:
                from backend.agents.orchestrator_agent import OrchestratorAgent
                self.agents['orchestrator'] = OrchestratorAgent()
                logger.info("Orchestrator Agent initialized")
            except ImportError as e:
                logger.warning(f"Orchestrator Agent not available: {e}")
                self.agents['orchestrator'] = None
    
    def is_agent_available(self, agent_type: str) -> bool:
        """Check if a specific agent is available"""
        return self.agents.get(agent_type) is not None
    
    def get_agent(self, agent_type: str):
        """Get a specific agent instance"""
        return self.agents.get(agent_type)
    
    def analyze_resume(self, text: str) -> Dict[str, Any]:
        """Analyze resume text"""
        agent = self.get_agent('resume')
        if agent:
            try:
                result = agent.analyze(text)
                result["fallback"] = False
                return result
            except Exception as e:
                logger.error(f"Error in resume analysis: {e}")
        
        # Fallback response
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
            "strengths": ["Strong technical skills", "Good problem-solving abilities"],
            "weaknesses": ["Could improve on cloud technologies"],
            "fallback": True
        }
    
    def evaluate_interview(self, responses: List[str]) -> Dict[str, Any]:
        """Evaluate interview responses"""
        agent = self.get_agent('interview')
        if agent:
            try:
                result = agent.evaluate(responses)
                result["fallback"] = False
                return result
            except Exception as e:
                logger.error(f"Error in interview evaluation: {e}")
        
        # Fallback response
        return {
            "evaluations": [
                {"question": "Tell me about yourself", "score": 8, "feedback": "Good introduction with clear structure."},
                {"question": "Describe a challenging project", "score": 7, "feedback": "Good details but could improve on outcome description."}
            ],
            "average_score": 7.5,
            "improvement_areas": ["Provide more specific examples", "Quantify achievements where possible"],
            "overall_feedback": "Strong interview performance with good communication skills.",
            "fallback": True
        }
    
    def evaluate_code(self, code: str, problem: str) -> Dict[str, Any]:
        """Evaluate code solution"""
        agent = self.get_agent('dsa')
        if agent:
            try:
                result = agent.evaluate(code, problem)
                result["fallback"] = False
                return result
            except Exception as e:
                logger.error(f"Error in code evaluation: {e}")
        
        # Fallback response
        return {
            "correctness": 8,
            "time_complexity": "O(n)",
            "space_complexity": "O(1)",
            "style": 7,
            "suggestions": ["Consider adding more comments", "Variable names could be more descriptive"],
            "fallback": True
        }
    
    def get_behavioral_coaching(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get behavioral coaching recommendations"""
        agent = self.get_agent('behavioral')
        if agent:
            try:
                result = agent.provide_coaching(user_data)
                result["fallback"] = False
                return result
            except Exception as e:
                logger.error(f"Error in behavioral coaching: {e}")
        
        # Fallback response
        return {
            "coaching_tips": [
                "Practice the STAR method for behavioral questions",
                "Prepare specific examples from your experience",
                "Focus on demonstrating leadership and problem-solving skills"
            ],
            "improvement_areas": ["Communication", "Leadership", "Conflict Resolution"],
            "recommended_practice": ["Mock interviews", "Scenario-based exercises"],
            "fallback": True
        }
    
    def track_performance(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Track user performance"""
        agent = self.get_agent('performance')
        if agent:
            try:
                return agent.track_session(user_id, session_data)
            except Exception as e:
                logger.error(f"Error in performance tracking: {e}")
        
        return f"fallback_session_{user_id}"
    
    def get_user_performance(self, user_id: str) -> Dict[str, Any]:
        """Get user performance data"""
        agent = self.get_agent('performance')
        if agent:
            try:
                result = agent.get_user_performance(user_id)
                result["fallback"] = False
                return result
            except Exception as e:
                logger.error(f"Error getting user performance: {e}")
        
        # Fallback response
        return {
            "user_id": user_id,
            "activity": {"total_sessions": 3, "last_active": "2023-06-01T12:00:00Z"},
            "metrics": {"average_interview_score": 7.5, "average_code_score": 8.0},
            "insights": ["Good progress in interview skills", "Strong in algorithm implementation"],
            "recommendations": ["Practice more system design questions", "Work on behavioral questions"],
            "fallback": True
        }
    
    def orchestrate_workflow(self, user_id: str, goal: str, **kwargs) -> Dict[str, Any]:
        """Orchestrate complex workflows"""
        agent = self.get_agent('orchestrator')
        if agent:
            try:
                return agent.run_workflow(
                    user_id=user_id,
                    goal=goal,
                    **kwargs
                )
            except Exception as e:
                logger.error(f"Error in workflow orchestration: {e}")
        
        # Fallback response
        return {
            "user_id": user_id,
            "workflow_id": "fallback_workflow",
            "status": "completed",
            "results": {
                "message": "Orchestrator not available in this deployment",
                "fallback": True
            },
            "recommendations": ["Please check system configuration"],
            "next_steps": ["Contact system administrator"]
        }

# Global AI service instance
ai_service = AIService()
