from autogen import AssistantAgent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from utils.prompts.resume_prompts import RESUME_ANALYSIS_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    print("Warning: GOOGLE_API_KEY not found. Please set the GOOGLE_API_KEY environment variable to use Gemini 1.5 Pro.")
    llm = None
else:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7, google_api_key=google_api_key)

class ResumeAnalyzerAgent:
    def __init__(self):
        self.prompt = PromptTemplate(input_variables=["resume_text"], template=RESUME_ANALYSIS_PROMPT)
        if not google_api_key:
            self.agent = None
            self.llm = None
            return
        self.agent = AssistantAgent(name="ResumeAnalyzerAgent", llm_config={
            "model": "gemini-1.5-pro",
            "api_key": google_api_key,
            "api_type": "google"
        })
        self.llm = llm

    def analyze_resume(self, resume_text):
        if not google_api_key:
            return "Error: GOOGLE_API_KEY is not set. Please configure the environment variable to enable resume analysis."
        if not resume_text:
            return "- Strengths: [None]\n- Weaknesses: [No resume provided]\n- Suggestions: [Upload a resume]"
        # Format the prompt using PromptTemplate
        formatted_prompt = self.prompt.format(resume_text=resume_text)
        # Invoke the LLM directly
        response = self.llm.invoke(formatted_prompt)
        return response.content