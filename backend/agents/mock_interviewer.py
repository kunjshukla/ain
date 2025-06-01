from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from utils.prompts.interview_prompts import INTERVIEW_QUESTION_PROMPT, INTERVIEW_FEEDBACK_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

class MockInterviewerAgent:
    def __init__(self):
        self.question_prompt = PromptTemplate(
            input_variables=["previous_answers"], 
            template=INTERVIEW_QUESTION_PROMPT
        )
        self.feedback_prompt = PromptTemplate(
            input_variables=["user_answers"], 
            template=INTERVIEW_FEEDBACK_PROMPT
        )
        
        if not google_api_key:
            print("Warning: GOOGLE_API_KEY not found. Mock responses will be used.")
            self.llm = None
        else:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", 
                temperature=0.7, 
                google_api_key=google_api_key
            )

    def get_next_question(self, previous_answers):
        if not self.llm:
            return "What experience do you have with Python?"
            
        answers_str = ", ".join(previous_answers) if previous_answers else "None"
        formatted_prompt = self.question_prompt.format(previous_answers=answers_str)
        response = self.llm.invoke(formatted_prompt)
        return response.content

    def conduct_interview(self, user_answers):
        if not user_answers:
            return [{"question": "Tell me about yourself.", "answer": "No answer provided"}]
        
        interview_results = []
        questions = [
            "Tell me about yourself.",
            self.get_next_question([user_answers[0]]),
            self.get_next_question(user_answers[:2])
        ]
        
        for i, answer in enumerate(user_answers[:3]):
            interview_results.append({
                "question": questions[i] if i < len(questions) else "No further questions.",
                "answer": answer
            })

        # Generate feedback using the LLM
        if not self.llm:
            feedback = "This is a sample feedback. Please provide a valid Google API key for personalized feedback."
        else:
            answers_str = ", ".join(user_answers)
            formatted_prompt = self.feedback_prompt.format(user_answers=answers_str)
            response = self.llm.invoke(formatted_prompt)
            feedback = response.content
            
        return {"responses": interview_results, "feedback": feedback}