from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from utils.prompts.behavioral_prompts import BEHAVIORAL_EVALUATION_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    print("Warning: GOOGLE_API_KEY not found. Mock evaluations will be used.")
    llm = None
else:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7, google_api_key=google_api_key)

class BehavioralCoachAgent:
    def __init__(self):
        self.prompt = PromptTemplate(input_variables=["user_answers"], template=BEHAVIORAL_EVALUATION_PROMPT)
        
        if not llm:
            print("Warning: GOOGLE_API_KEY not found. Mock evaluations will be used.")
            self.llm = None
        else:
            self.llm = llm

    def evaluate_behavioral(self, user_answers):
        if not user_answers:
            return "- Strengths: [None]\n- Weaknesses: [No answers provided]\n- Suggestions: [Answer behavioral questions]"
        answers_str = ", ".join(user_answers)
        formatted_prompt = self.prompt.format(user_answers=answers_str)
        response = self.llm.invoke(formatted_prompt)
        return response.content