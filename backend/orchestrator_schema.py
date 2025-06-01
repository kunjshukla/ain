from pydantic import BaseModel
from typing import Optional, List

class OrchestratorRequest(BaseModel):
    user_id: str
    goal: str
    resume_text: Optional[str] = None
    code: Optional[str] = None
    interview_answers: Optional[List[str]] = None

class OrchestratorResponse(BaseModel):
    goal: str
    resume: Optional[dict]
    dsa: Optional[dict]
    interview: Optional[dict]
    performance: Optional[dict]
    behavioral: Optional[dict]
