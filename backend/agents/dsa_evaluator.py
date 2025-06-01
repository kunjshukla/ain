from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from utils.prompts.dsa_prompts import DSA_EVALUATION_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

class DSAEvaluatorAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["code_solution"],
            template=DSA_EVALUATION_PROMPT
        )
        
        if not google_api_key:
            print("Warning: GOOGLE_API_KEY not found. Mock evaluations will be used.")
            self.llm = None
        else:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=0.7,
                google_api_key=google_api_key
            )

    def evaluate_code(self, code_solution):
        if not code_solution:
            return "- Correctness: [No]\n- Feedback: [No code provided]\n- Score: [0]"
            
        if not self.llm:
            return "- Correctness: [Yes]\n- Feedback: [Sample feedback - please provide API key for real evaluation]\n- Score: [8/10]"
            
        formatted_prompt = self.prompt.format(code_solution=code_solution)
        response = self.llm.invoke(formatted_prompt)
        return response.content