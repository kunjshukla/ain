# File: backend/services/resume_parser.py
# Enhanced PDF text extraction with comprehensive error handling and multiple extraction methods

import PyPDF2
import io
import os
import logging
from typing import Optional, Dict, Any, Union
from pathlib import Path

# Enhanced imports for better PDF processing
try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False
    logging.warning("PDFMiner not available. Only PyPDF2 will be used for PDF extraction.")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParsingError(Exception):
    """Custom exception for resume parsing errors"""
    pass

class ResumeParser:
    """
    Enhanced resume parser with multiple extraction methods and robust error handling
    Supports both file paths and file content (bytes)
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        
    def extract_text_from_pdf(self, source: Union[str, bytes, io.BytesIO], 
                             method: str = "auto") -> Optional[str]:
        """
        Extract text from PDF using multiple methods with fallback
        
        Args:
            source: File path (str), bytes content, or BytesIO object
            method: Extraction method ("pypdf2", "pdfminer", "auto")
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            # Convert source to BytesIO
            pdf_content = self._prepare_pdf_content(source)
            
            if method == "auto":
                return self._extract_with_fallback(pdf_content)
            elif method == "pypdf2":
                return self._extract_with_pypdf2(pdf_content)
            elif method == "pdfminer" and PDFMINER_AVAILABLE:
                return self._extract_with_pdfminer(pdf_content)
            else:
                raise ResumeParsingError(f"Unsupported extraction method: {method}")
                
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return None
    
    def _prepare_pdf_content(self, source: Union[str, bytes, io.BytesIO]) -> io.BytesIO:
        """Convert various input types to BytesIO object"""
        
        if isinstance(source, str):
            # File path
            if not os.path.exists(source):
                raise FileNotFoundError(f"PDF file not found: {source}")
                
            if not source.lower().endswith('.pdf'):
                raise ResumeParsingError(f"File is not a PDF: {source}")
                
            with open(source, 'rb') as file:
                return io.BytesIO(file.read())
                
        elif isinstance(source, bytes):
            # Raw bytes
            return io.BytesIO(source)
            
        elif isinstance(source, io.BytesIO):
            # Already BytesIO
            source.seek(0)  # Reset position
            return source
            
        else:
            raise ResumeParsingError(f"Unsupported source type: {type(source)}")
    
    def _extract_with_fallback(self, pdf_content: io.BytesIO) -> Optional[str]:
        """
        Try multiple extraction methods in order of preference
        """
        methods = [
            ("PyPDF2", self._extract_with_pypdf2),
        ]
        
        if PDFMINER_AVAILABLE:
            methods.append(("PDFMiner", self._extract_with_pdfminer))
            methods.append(("PDFMiner High-Level", self._extract_with_pdfminer_highlevel))
        
        for method_name, method_func in methods:
            try:
                pdf_content.seek(0)  # Reset position for each attempt
                text = method_func(pdf_content)
                
                if text and len(text.strip()) > 10:  # Ensure some content (lowered threshold)
                    logger.info(f"Successfully extracted text using {method_name}")
                    return self._clean_text(text)
                    
            except Exception as e:
                logger.warning(f"{method_name} extraction failed: {e}")
                continue
        
        logger.error("All extraction methods failed")
        return None
    
    def _extract_with_pypdf2(self, pdf_content: io.BytesIO) -> str:
        """Enhanced PyPDF2 extraction with better error handling"""
        try:
            reader = PyPDF2.PdfReader(pdf_content)
            
            if reader.is_encrypted:
                # Try to decrypt with empty password
                if not reader.decrypt(""):
                    raise ResumeParsingError("PDF is password protected")
            
            text_parts = []
            total_pages = len(reader.pages)
            
            if total_pages == 0:
                raise ResumeParsingError("PDF has no pages")
            
            logger.info(f"Extracting from {total_pages} pages using PyPDF2")
            
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"Failed to extract from page {page_num + 1}: {e}")
                    continue
            
            if not text_parts:
                raise ResumeParsingError("No text could be extracted from any page")
            
            return "\n".join(text_parts)
            
        except PyPDF2.errors.PdfReadError as e:
            raise ResumeParsingError(f"PDF read error: {e}")
        except Exception as e:
            raise ResumeParsingError(f"PyPDF2 extraction error: {e}")
    
    def _extract_with_pdfminer(self, pdf_content: io.BytesIO) -> str:
        """Enhanced PDFMiner extraction"""
        if not PDFMINER_AVAILABLE:
            raise ResumeParsingError("PDFMiner not available")
        
        try:
            resource_manager = PDFResourceManager()
            output_string = io.StringIO()
            codec = 'utf-8'
            laparams = LAParams(
                all_texts=True,
                detect_vertical=True,
                word_margin=0.1,
                char_margin=2.0,
                line_margin=0.5,
                boxes_flow=0.5
            )
            
            converter = TextConverter(resource_manager, output_string, 
                                    codec=codec, laparams=laparams)
            interpreter = PDFPageInterpreter(resource_manager, converter)
            
            page_count = 0
            for page in PDFPage.get_pages(pdf_content, check_extractable=True):
                interpreter.process_page(page)
                page_count += 1
            
            text = output_string.getvalue()
            converter.close()
            output_string.close()
            
            logger.info(f"Extracted from {page_count} pages using PDFMiner")
            return text
            
        except Exception as e:
            raise ResumeParsingError(f"PDFMiner extraction error: {e}")
    
    def _extract_with_pdfminer_highlevel(self, pdf_content: io.BytesIO) -> str:
        """PDFMiner high-level API extraction"""
        if not PDFMINER_AVAILABLE:
            raise ResumeParsingError("PDFMiner not available")
        
        try:
            pdf_content.seek(0)
            text = pdfminer_extract_text(pdf_content)
            logger.info("Extracted using PDFMiner high-level API")
            return text
        except Exception as e:
            raise ResumeParsingError(f"PDFMiner high-level extraction error: {e}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                cleaned_lines.append(line)
        
        # Join with single newlines
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove excessive consecutive newlines
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
        return cleaned_text
    
    def parse_resume(self, source: Union[str, bytes, io.BytesIO]) -> Dict[str, Any]:
        """
        Parse a resume and return structured information
        
        Args:
            source: File path, bytes content, or BytesIO object
            
        Returns:
            Dictionary with parsed resume information
        """
        try:
            # Extract text
            text = self.extract_text_from_pdf(source)
            
            if not text:
                return {
                    "success": False,
                    "error": "Could not extract text from PDF",
                    "text": "",
                    "metadata": {}
                }
            
            # Basic metadata
            metadata = {
                "char_count": len(text),
                "line_count": len(text.split('\n')),
                "word_count": len(text.split()),
                "extraction_method": "auto"
            }
            
            # Extract structured information using Ollama
            ollama_data = self.extract_skills_with_ollama(text)
            
            # Combine basic structure with Ollama extraction
            structured_data = self._extract_basic_structure(text)
            structured_data.update({
                "skills": ollama_data.get("skills", []),
                "experience_years": ollama_data.get("experience_years", 0),
                "roles": ollama_data.get("roles", [])
            })
            
            # Update metadata with extraction info
            metadata.update({
                "skills_count": len(ollama_data.get("skills", [])),
                "roles_count": len(ollama_data.get("roles", [])),
                "experience_years": ollama_data.get("experience_years", 0)
            })
            
            return {
                "success": True,
                "text": text,
                "metadata": metadata,
                "structured_data": structured_data,
                "ollama_extraction": ollama_data
            }
            
        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "metadata": {}
            }
    
    def _extract_basic_structure(self, text: str) -> Dict[str, Any]:
        """
        Extract basic structured information from text
        This is a simple implementation - could be enhanced with NLP
        """
        text_lower = text.lower()
        
        # Simple keyword-based extraction
        structure = {
            "has_contact_info": any(keyword in text_lower for keyword in 
                                  ['email', 'phone', 'linkedin', '@']),
            "has_experience": any(keyword in text_lower for keyword in 
                                ['experience', 'work', 'employment', 'job']),
            "has_education": any(keyword in text_lower for keyword in 
                               ['education', 'degree', 'university', 'college']),
            "has_skills": any(keyword in text_lower for keyword in 
                            ['skills', 'technologies', 'programming', 'languages']),
            "estimated_sections": []
        }
        
        # Identify potential sections
        lines = text.split('\n')
        for line in lines:
            line_clean = line.strip().lower()
            if len(line_clean) < 50 and any(keyword in line_clean for keyword in 
                                          ['experience', 'education', 'skills', 'projects']):
                structure["estimated_sections"].append(line.strip())
        
        return structure
    
    def validate_pdf(self, source: Union[str, bytes, io.BytesIO]) -> Dict[str, Any]:
        """
        Validate PDF file and return diagnostic information
        """
        try:
            pdf_content = self._prepare_pdf_content(source)
            reader = PyPDF2.PdfReader(pdf_content)
            
            return {
                "valid": True,
                "page_count": len(reader.pages),
                "encrypted": reader.is_encrypted,
                "metadata": reader.metadata or {},
                "can_extract": True
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "page_count": 0,
                "encrypted": False,
                "metadata": {},
                "can_extract": False
            }

    def extract_skills_with_ollama(self, resume_text: str) -> dict:
        """
        Extract structured information from resume using Ollama LLM
        
        Args:
            resume_text: The extracted text from the resume
            
        Returns:
            Dictionary with skills, experience_years, and roles
        """
        try:
            import requests
            import json
            
            # Enhanced prompt for better skill extraction
            prompt = f"""Analyze this resume and extract key information. Return ONLY a valid JSON object with no additional text or markdown formatting.

Resume Text:
{resume_text[:3000]}  # Limit text to avoid token limits

Required JSON format:
{{
  "skills": ["Python", "JavaScript", "React", "SQL"],
  "experience_years": 5,
  "roles": ["Software Engineer", "Full Stack Developer"]
}}

Guidelines:
- skills: Extract ALL technical skills, programming languages, frameworks, tools
- experience_years: Calculate total years of professional experience
- roles: Extract job titles and positions held

JSON Response:"""

            # Make request to Ollama
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": "llama3.2",  # Use available model
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent output
                        "top_p": 0.9,
                        "max_tokens": 500
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ollama_response = result.get('response', '{}')
                
                # Clean up response and parse JSON
                try:
                    # Remove any markdown formatting or extra text
                    clean_response = ollama_response.strip()
                    if clean_response.startswith('```json'):
                        clean_response = clean_response.replace('```json', '').replace('```', '').strip()
                    elif clean_response.startswith('```'):
                        clean_response = clean_response.replace('```', '').strip()
                    
                    # Parse JSON
                    parsed_data = json.loads(clean_response)
                    
                    # Validate and clean the data
                    skills = parsed_data.get('skills', [])
                    if isinstance(skills, list):
                        # Remove duplicates and clean skill names
                        skills = list(set([skill.strip() for skill in skills if skill.strip()]))
                    else:
                        skills = []
                    
                    experience_years = parsed_data.get('experience_years', 0)
                    if not isinstance(experience_years, (int, float)) or experience_years < 0:
                        experience_years = 0
                    
                    roles = parsed_data.get('roles', [])
                    if isinstance(roles, list):
                        # Remove duplicates and clean role names
                        roles = list(set([role.strip() for role in roles if role.strip()]))
                    else:
                        roles = []
                    
                    return {
                        "skills": skills[:20],  # Limit to top 20 skills
                        "experience_years": int(experience_years),
                        "roles": roles[:10]  # Limit to top 10 roles
                    }
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Ollama JSON response: {e}")
                    logger.error(f"Raw response: {ollama_response}")
                    return self._fallback_extraction(resume_text)
                    
            else:
                logger.error(f"Ollama request failed with status {response.status_code}")
                return self._fallback_extraction(resume_text)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama connection failed: {e}")
            return self._fallback_extraction(resume_text)
        except Exception as e:
            logger.error(f"Ollama skill extraction failed: {e}")
            return self._fallback_extraction(resume_text)
    
    def _fallback_extraction(self, resume_text: str) -> dict:
        """
        Fallback skill extraction using keyword matching
        Used when Ollama is unavailable
        """
        import re
        
        # Common technical skills and keywords
        skill_keywords = [
            # Programming Languages
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift',
            'TypeScript', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl', 'Shell', 'Bash',
            
            # Web Technologies
            'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask', 'Spring',
            'Laravel', 'Rails', 'HTML', 'CSS', 'SASS', 'LESS', 'Bootstrap', 'Tailwind',
            'jQuery', 'Redux', 'GraphQL', 'REST', 'API',
            
            # Databases
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server',
            'Elasticsearch', 'Cassandra', 'DynamoDB', 'Firebase',
            
            # Cloud & DevOps
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab', 'GitHub',
            'Terraform', 'Ansible', 'Chef', 'Puppet', 'CircleCI', 'Travis CI',
            
            # Data Science & ML
            'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn', 'Jupyter',
            'Tableau', 'Power BI', 'Apache Spark', 'Hadoop', 'Kafka',
            
            # Tools & Others
            'Git', 'Linux', 'Windows', 'macOS', 'Vim', 'VSCode', 'IntelliJ', 'Eclipse',
            'Jira', 'Confluence', 'Slack', 'Teams', 'Figma', 'Sketch'
        ]
        
        # Extract skills using keyword matching
        found_skills = []
        text_lower = resume_text.lower()
        
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Extract experience years using regex
        experience_years = 0
        year_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+in',
            r'experience.*?(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s+experience'
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    experience_years = max(experience_years, int(matches[0]))
                except (ValueError, IndexError):
                    continue
        
        # Extract job titles using common patterns
        role_patterns = [
            r'(software engineer|developer|programmer|architect)',
            r'(data scientist|data analyst|data engineer)',
            r'(product manager|project manager|scrum master)',
            r'(designer|ui/ux|frontend|backend|fullstack|full stack)',
            r'(devops|sre|system administrator|network engineer)',
            r'(analyst|consultant|specialist|lead|senior|junior)'
        ]
        
        found_roles = []
        for pattern in role_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            found_roles.extend(matches)
        
        # Clean and deduplicate roles
        cleaned_roles = list(set([role.title() for role in found_roles if role]))
        
        return {
            "skills": found_skills[:15],  # Limit fallback skills
            "experience_years": min(experience_years, 50),  # Cap at 50 years
            "roles": cleaned_roles[:8]  # Limit fallback roles
        }


# Create singleton instance for import
resume_parser = ResumeParser()
