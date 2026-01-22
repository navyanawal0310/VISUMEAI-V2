import re
import logging
from typing import List, Dict, Optional
from PyPDF2 import PdfReader
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from ..models.schemas import ResumeAnalysisResult
import spacy
from ..config.settings import settings

logger = logging.getLogger(__name__)

class ResumeParser:
    """Parse and analyze resume documents"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load(settings.SPACY_MODEL)
        except:
            logger.warning("Using blank spaCy model for resume parsing")
            self.nlp = spacy.blank("en")
        
        # Skill keywords database
        self.skill_keywords = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go',
                'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'express',
                'spring', 'node.js', 'laravel', '.net', 'tensorflow', 'pytorch'
            ],
            'databases': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra',
                'dynamodb', 'oracle', 'elasticsearch', 'neo4j'
            ],
            'cloud_devops': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab',
                'terraform', 'ansible', 'ci/cd', 'github actions'
            ],
            'tools': [
                'git', 'jira', 'confluence', 'linux', 'unix', 'bash', 'powershell'
            ],
            'methodologies': [
                'agile', 'scrum', 'kanban', 'tdd', 'bdd', 'devops', 'microservices'
            ]
        }
    
    async def parse_resume(self, file_path: str, resume_id: str) -> ResumeAnalysisResult:
        """Parse resume and extract structured information"""
        try:
            logger.info(f"Parsing resume: {file_path}")
            
            # Extract text based on file type
            if file_path.endswith('.pdf'):
                text = self._extract_pdf_text(file_path)
            elif file_path.endswith('.docx'):
                text = self._extract_docx_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            # Parse sections
            skills = self._extract_skills(text)
            experience_years = self._extract_experience_years(text)
            education = self._extract_education(text)
            certifications = self._extract_certifications(text)
            tools = self._extract_tools(text)
            
            result = ResumeAnalysisResult(
                resume_id=resume_id,
                parsed_text=text,
                skills=skills,
                experience_years=experience_years,
                education=education,
                certifications=certifications,
                tools=tools
            )
            
            logger.info(f"Resume parsing complete: {len(skills)} skills found")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}")
            raise
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX: {str(e)}")
            raise
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills using keyword matching and NER"""
        text_lower = text.lower()
        found_skills = set()
        
        # Keyword-based extraction
        for category, keywords in self.skill_keywords.items():
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.add(keyword)
        
        # Use NER to find additional entities
        doc = self.nlp(text[:1000000])  # Limit for performance
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT']:
                # Check if it looks like a technology
                if len(ent.text) > 2 and len(ent.text) < 30:
                    found_skills.add(ent.text.lower())
        
        return sorted(list(found_skills))
    
    def _extract_experience_years(self, text: str) -> Optional[float]:
        """Extract years of experience from text"""
        # Look for patterns like "X years of experience", "X+ years"
        patterns = [
            r'(\d+)[\+]?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)',
            r'experience[:\s]+(\d+)[\+]?\s*(?:years?|yrs?)',
            r'(\d+)[\+]?\s*(?:years?|yrs?)\s+(?:in|of)',
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            years.extend([float(m) for m in matches])
        
        return max(years) if years else None
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education = []
        
        # Degree patterns
        degree_patterns = [
            r'(?:bachelor|b\.?s\.?|b\.?a\.?|b\.?tech|b\.?e\.?)\s+(?:of|in|degree)?\s*([^\n,\.]+)',
            r'(?:master|m\.?s\.?|m\.?a\.?|m\.?tech|m\.?b\.?a\.?)\s+(?:of|in|degree)?\s*([^\n,\.]+)',
            r'(?:phd|ph\.?d\.?|doctorate)\s+(?:in)?\s*([^\n,\.]+)',
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                degree = match.group(0).strip()
                if degree and len(degree) < 100:
                    education.append(degree.title())
        
        return education
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        
        # Common certification patterns
        cert_keywords = [
            'aws certified', 'azure certified', 'google cloud certified',
            'pmp', 'scrum master', 'cissp', 'comptia', 'ccna', 'ccnp',
            'oracle certified', 'microsoft certified', 'certified'
        ]
        
        lines = text.lower().split('\n')
        for line in lines:
            for keyword in cert_keywords:
                if keyword in line:
                    # Extract the line containing certification
                    cert = line.strip()
                    if cert and len(cert) < 200:
                        certifications.append(cert.title())
                        break
        
        return list(set(certifications))[:10]  # Limit to 10 unique certs
    
    def _extract_tools(self, text: str) -> List[str]:
        """Extract tools and technologies"""
        # This is similar to skills but focuses on specific tools
        all_tools = []
        for category in ['tools', 'cloud_devops', 'frameworks']:
            if category in self.skill_keywords:
                all_tools.extend(self.skill_keywords[category])
        
        text_lower = text.lower()
        found_tools = []
        
        for tool in all_tools:
            if tool in text_lower:
                found_tools.append(tool)
        
        return sorted(list(set(found_tools)))
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information"""
        contact_info = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None
        }
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group(0)
        
        # Phone
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group(0)
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text.lower())
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group(0)
        
        # GitHub
        github_pattern = r'github\.com/[\w-]+'
        github_match = re.search(github_pattern, text.lower())
        if github_match:
            contact_info['github'] = github_match.group(0)
        
        return contact_info
