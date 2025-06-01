from backend.agents.resume_analyzer import ResumeAnalyzerAgent
from backend.agents.dsa_evaluator import DSAEvaluatorAgent
from backend.agents.mock_interviewer import MockInterviewerAgent
from backend.agents.performance_tracker import PerformanceTrackerAgent
from backend.agents.behavioural_coach import BehavioralCoachAgent

class OrchestratorAgent:
    def __init__(self):
        self.resume_agent = ResumeAnalyzerAgent()
        self.dsa_agent = DSAEvaluatorAgent()
        self.mock_agent = MockInterviewerAgent()
        self.performance_agent = PerformanceTrackerAgent()
        self.behavioural_agent = BehavioralCoachAgent()

    def run_workflow(self, user_id, goal, resume_text=None, code=None, interview_answers=None):
        results = {}
        # 1. Resume analysis
        if resume_text:
            results['resume'] = self.resume_agent.analyze(resume_text)
        # 2. Coding evaluation
        if code:
            results['dsa'] = self.dsa_agent.evaluate(code)
        # 3. Mock interview (if answers provided)
        if interview_answers:
            results['interview'] = self.mock_agent.evaluate(interview_answers)
        # 4. Performance summary
        results['performance'] = self.performance_agent.get_user_performance(user_id)
        # 5. Behavioral feedback (if resume or answers)
        if resume_text or interview_answers:
            results['behavioral'] = self.behavioural_agent.evaluate_behavioral(interview_answers)
        # 6. Goal echo
        results['goal'] = goal
        return results
