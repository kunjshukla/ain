# agents/resume_analyzer.py
import spacy
from typing import Dict, List, Any
import re

class ResumeAnalyzerAgent:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_lg")  # Try loading large model first
        except OSError:
            print("Warning: Using small English model (en_core_web_sm) instead of large model")
            self.nlp = spacy.load("en_core_web_sm")  # Fallback to small model
            
        self.tech_skills = self._load_skills("data/technical_skills.txt")
        self.soft_skills = self._load_skills("data/soft_skills.txt")
    def _load_skills(self, filepath: str) -> List[str]:
        try:
            with open(filepath, 'r') as f:
                return [line.strip().lower() for line in f if line.strip()]
        except:
            return []
            
    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        doc = self.nlp(text.lower())
        found_tech = set()
        found_soft = set()
        
        for token in doc:
            if token.text in self.tech_skills:
                found_tech.add(token.text)
            elif token.text in self.soft_skills:
                found_soft.add(token.text)
                
        return {
            "technical": list(found_tech),
            "soft": list(found_soft)
        }
        
    def _analyze_experience(self, text: str) -> Dict[str, Any]:
        # Simple regex for experience extraction
        experience = {}
        # Add more sophisticated parsing as needed
        return experience
        
    def analyze(self, text: str) -> Dict[str, Any]:
        skills = self._extract_skills(text)
        experience = self._analyze_experience(text)
        
        return {
            "skills": skills,
            "experience": experience,
            "role_match": self._match_roles(text),
            "suggested_questions": self._generate_questions(text),
            "strengths": self._identify_strengths(text),
            "weaknesses": self._identify_weaknesses(text)
        }
        
    # Additional helper methods...