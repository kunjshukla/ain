from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from utils.prompts.performance_prompts import PERFORMANCE_REPORT_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

class PerformanceTrackerAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["resume_feedback", "interview_results", "dsa_results", "behavioral_results"],
            template=PERFORMANCE_REPORT_PROMPT
        )
        
        if not google_api_key:
            print("Warning: GOOGLE_API_KEY not found. Mock reports will be generated.")
            self.llm = None
        else:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=0.7,
                google_api_key=google_api_key
            )

    def generate_report(self, resume_feedback, interview_results, dsa_results, behavioral_results):
        interview_results_str = "\n".join(
            [f"Question: {r['question']}\nAnswer: {r['answer']}" for r in interview_results.get("responses", [])]
        ) + f"\n\nFeedback: {interview_results.get('feedback', 'None')}"
        
        if not self.llm:
            return """# Performance Report (Sample)

## Interview Results
Mock interview results will appear here when you provide a valid API key.

## DSA Evaluation
Mock DSA evaluation will appear here when you provide a valid API key.

## Behavioral Assessment
Mock behavioral assessment will appear here when you provide a valid API key.

## Overall Score: 8/10"""
            
        formatted_prompt = self.prompt.format(
            resume_feedback=resume_feedback,
            interview_results=interview_results_str,
            dsa_results=dsa_results,
            behavioral_results=behavioral_results
        )
        response = self.llm.invoke(formatted_prompt)
        return response.content