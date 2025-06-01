# agents/resume_analyzer.py
import spacy
from typing import Dict, List, Any, Optional
import re
import os
from spacy.language import Language

class ResumeAnalyzerAgent:
    def __init__(self):
        self.nlp = self._get_nlp_model()
        self.tech_skills = self._load_skills("data/technical_skills.txt")
        self.soft_skills = self._load_skills("data/soft_skills.txt")
        print(f"Loaded {len(self.tech_skills)} technical skills and {len(self.soft_skills)} soft skills")
        
    def _get_nlp_model(self) -> Optional[Language]:
        """Try multiple fallback options for NLP model"""
        try:
            print("Attempting to load en_core_web_sm model...")
            return spacy.load("en_core_web_sm")
        except OSError:
            try:
                print("Warning: Falling back to small English model (en_core_web_sm)")
                return spacy.load("en_core_web_sm")
            except OSError:
                print("Critical: No spaCy model available. Using basic regex matching.")
                return None
    
    def _load_skills(self, filepath: str) -> List[str]:
        try:
            # Handle both absolute and relative paths
            if not os.path.isabs(filepath):
                # Try from current directory
                current_dir_path = os.path.join(os.getcwd(), filepath)
                if os.path.exists(current_dir_path):
                    filepath = current_dir_path
                else:
                    # Try from backend directory
                    backend_path = os.path.join(os.getcwd(), 'backend', filepath)
                    if os.path.exists(backend_path):
                        filepath = backend_path
            
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return [line.strip().lower() for line in f if line.strip()]
            else:
                print(f"Warning: Skill file not found at {filepath}")
                # Return default skills if file not found
                if 'technical' in filepath:
                    return ["python", "java", "javascript", "react", "node", "sql", "mongodb", "aws", "docker"]
                else:
                    return ["communication", "teamwork", "leadership", "problem solving", "adaptability"]  
        except Exception as e:
            print(f"Error loading skills from {filepath}: {str(e)}")
            return []
            
    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        text_lower = text.lower()
        found_tech = set()
        found_soft = set()
        
        if self.nlp:
            # NLP-based extraction
            doc = self.nlp(text_lower)
            for token in doc:
                if token.text in self.tech_skills:
                    found_tech.add(token.text)
                elif token.text in self.soft_skills:
                    found_soft.add(token.text)
                    
            # Also check for multi-word skills
            for skill in self.tech_skills:
                if len(skill.split()) > 1 and skill in text_lower:
                    found_tech.add(skill)
            for skill in self.soft_skills:
                if len(skill.split()) > 1 and skill in text_lower:
                    found_soft.add(skill)
        else:
            # Fallback regex matching if no NLP model
            for skill in self.tech_skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                    found_tech.add(skill)
            for skill in self.soft_skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                    found_soft.add(skill)
                    
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
        
    def _match_roles(self, text: str) -> Dict[str, float]:
        """Match resume to potential roles based on skills"""
        roles = {
    "software_engineer": [
        "python", "java", "javascript", "c++", "c#", "software development",
        "system design", "object-oriented programming", "data structures", "algorithms",
        "git", "debugging", "unit testing", "api development", "design patterns"
    ],
    "data_scientist": [
        "python", "r", "machine learning", "deep learning", "statistics",
        "data analysis", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
        "data visualization", "matplotlib", "seaborn", "sql", "feature engineering",
        "model evaluation", "notebooks", "eda"
    ],
    "web_developer": [
        "html", "css", "javascript", "react", "node.js", "express.js", "vue.js",
        "angular", "typescript", "responsive design", "restful apis",
        "frontend", "backend", "fullstack", "webpack", "tailwind", "bootstrap", "redux"
    ],
    "devops_engineer": [
        "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "jenkins",
        "terraform", "ansible", "prometheus", "grafana", "linux", "bash scripting",
        "infrastructure as code", "monitoring", "logging", "load balancing"
    ],
    "product_manager": [
        "product management", "agile", "scrum", "kanban", "user research", "product roadmap",
        "market analysis", "stakeholder communication", "user stories", "wireframing",
        "mvp definition", "feature prioritization", "data-driven decision making", "a/b testing"
    ]
}

        
        # Extract skills from text
        skills = self._extract_skills(text)
        all_skills = skills["technical"] + skills["soft"]
        all_skills_set = set(all_skills)
        
        # Calculate match percentages
        matches = {}
        for role, role_skills in roles.items():
            role_skills_set = set(role_skills)
            if not role_skills_set:
                matches[role] = 0.0
                continue
                
            # Calculate intersection
            common_skills = all_skills_set.intersection(role_skills_set)
            match_percentage = len(common_skills) / len(role_skills_set) * 100
            matches[role] = round(match_percentage, 1)
            
        return matches
    
    def _generate_questions(self, text: str) -> List[str]:
        """Generate interview questions based on resume content"""
        # Extract skills to generate targeted questions
        skills = self._extract_skills(text)
        tech_skills = skills["technical"]
        
        questions = [
            "Tell me about your background and experience.",
            "What are your greatest strengths and weaknesses?"
        ]
        
        # Add skill-specific questions
        if tech_skills:
            for skill in tech_skills[:3]:  # Limit to top 3 skills
                questions.append(f"Can you describe a project where you used {skill}?")
                
        # Add general technical questions
        questions.extend([
            "How do you approach problem-solving?",
            "Describe a challenging project you worked on and how you overcame obstacles."
        ])
        
        return questions
    
    def _identify_strengths(self, text: str) -> List[str]:
        """Identify strengths based on resume content"""
        strengths = []
        
        # Check for technical skills diversity
        skills = self._extract_skills(text)
        if len(skills["technical"]) >= 5:
            strengths.append("Diverse technical skill set")
        
        # Check for soft skills
        if skills["soft"]:
            strengths.append("Good balance of technical and soft skills")
            
        # Add generic strengths based on common resume keywords
        if any(term in text.lower() for term in ["lead", "manage", "direct"]):
            strengths.append("Leadership experience")
            
        if any(term in text.lower() for term in ["collaborate", "team", "cross-functional"]):
            strengths.append("Team collaboration")
            
        # Ensure we return at least some strengths
        if not strengths:
            strengths = ["Technical expertise", "Professional experience"]
            
        return strengths
    
    def _identify_weaknesses(self, text: str) -> List[str]:
        """Identify potential weaknesses or improvement areas"""
        weaknesses = []
        
        # Check for missing soft skills
        skills = self._extract_skills(text)
        if not skills["soft"]:
            weaknesses.append("Limited emphasis on soft skills")
            
        # Check for potential gaps
        if not any(term in text.lower() for term in ["team", "collaborate", "group"]):
            weaknesses.append("Limited demonstration of teamwork")
            
        # Check for project outcomes
        if not any(term in text.lower() for term in ["delivered", "achieved", "resulted", "improved"]):
            weaknesses.append("Could better highlight project outcomes and achievements")
            
        # Ensure we return at least some constructive feedback
        if not weaknesses:
            weaknesses = ["Consider adding more quantifiable achievements", "Could provide more detail on project impacts"]
            
        return weaknesses