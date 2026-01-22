import logging
from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import httpx
from ..models.schemas import RoleMatchResult, JobDescription, ResumeAnalysisResult, TranscriptAnalysisResult
from ..config.settings import settings

logger = logging.getLogger(__name__)

class RoleMatcher:
    """Match candidate profiles against job requirements"""
    
    def __init__(self):
        # Load sentence transformer for semantic similarity
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded SentenceTransformer model")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer: {e}")
            self.model = None
    
    async def match_role(
        self,
        job_description: JobDescription,
        resume_analysis: Optional[ResumeAnalysisResult] = None,
        transcript_analysis: Optional[TranscriptAnalysisResult] = None
    ) -> RoleMatchResult:
        """Match candidate against job requirements"""
        try:
            logger.info(f"Matching candidate against role: {job_description.title}")
            
            # Extract JD requirements if needed
            if not job_description.required_skills:
                job_description = await self._extract_jd_requirements(job_description)
            
            # Gather candidate skills
            candidate_skills = set()
            if resume_analysis:
                candidate_skills.update(resume_analysis.skills)
                candidate_skills.update(resume_analysis.tools)
            
            if transcript_analysis:
                candidate_skills.update([term.lower() for term in transcript_analysis.technical_terms])
            
            # Required skills matching
            required_skills = set(skill.lower() for skill in job_description.required_skills)
            matching_skills = list(candidate_skills.intersection(required_skills))
            missing_skills = list(required_skills - candidate_skills)
            
            # Calculate match percentage
            skill_match_pct = (len(matching_skills) / len(required_skills) * 100) if required_skills else 50.0
            
            # Experience matching
            experience_match = self._check_experience_match(
                job_description.experience_years,
                resume_analysis.experience_years if resume_analysis else None
            )
            
            # Semantic similarity
            semantic_similarity = await self._compute_semantic_similarity(
                job_description,
                resume_analysis,
                transcript_analysis
            )
            
            # Overall match percentage (weighted)
            match_percentage = (
                skill_match_pct * 0.5 +
                (100 if experience_match else 50) * 0.2 +
                semantic_similarity * 100 * 0.3
            )
            
            # Identify strengths and gaps
            strengths = self._identify_strengths(
                matching_skills,
                job_description.preferred_skills or []
            )
            gaps = self._identify_gaps(missing_skills)
            
            result = RoleMatchResult(
                match_percentage=min(100.0, max(0.0, match_percentage)),
                matching_skills=matching_skills,
                missing_skills=missing_skills[:10],  # Top 10 missing
                experience_match=experience_match,
                semantic_similarity=semantic_similarity,
                strengths=strengths,
                gaps=gaps
            )
            
            logger.info(f"Role match complete: {result.match_percentage:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"Error matching role: {str(e)}")
            raise
    
    async def _extract_jd_requirements(self, jd: JobDescription) -> JobDescription:
        """Extract requirements from JD using LLM"""
        try:
            # Try to use Llama 3.2 API
            if settings.LLAMA_API_URL:
                skills = await self._extract_with_llama(jd.description)
                if skills:
                    jd.required_skills = skills
                    return jd
            
            # Fallback to keyword extraction
            skills = self._extract_skills_keywords(jd.description)
            jd.required_skills = skills
            return jd
            
        except Exception as e:
            logger.error(f"Error extracting JD requirements: {str(e)}")
            return jd
    
    async def _extract_with_llama(self, jd_text: str) -> List[str]:
        """Extract skills using Llama 3.2"""
        try:
            prompt = f"""
            Extract a list of technical skills and requirements from the following job description.
            Return only skill names, one per line, without explanations.
            
            Job Description:
            {jd_text}
            
            Skills:
            """
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    settings.LLAMA_API_URL,
                    json={
                        "model": "llama3.2",
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    skills_text = result.get('response', '')
                    skills = [s.strip() for s in skills_text.split('\n') if s.strip()]
                    return skills[:20]  # Limit to top 20
            
            return []
            
        except Exception as e:
            logger.warning(f"Could not extract with Llama: {e}")
            return []
    
    def _extract_skills_keywords(self, text: str) -> List[str]:
        """Fallback keyword extraction"""
        skill_keywords = {
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'django', 'flask', 'spring', 'docker', 'kubernetes', 'aws', 'azure',
            'sql', 'nosql', 'mongodb', 'postgresql', 'git', 'agile', 'scrum',
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'api',
            'microservices', 'rest', 'graphql', 'ci/cd', 'devops', 'linux'
        }
        
        text_lower = text.lower()
        found_skills = [skill for skill in skill_keywords if skill in text_lower]
        return found_skills
    
    def _check_experience_match(
        self,
        required_years: Optional[int],
        candidate_years: Optional[float]
    ) -> bool:
        """Check if candidate experience matches requirement"""
        if required_years is None or candidate_years is None:
            return True  # Give benefit of doubt
        
        return candidate_years >= required_years
    
    async def _compute_semantic_similarity(
        self,
        jd: JobDescription,
        resume_analysis: Optional[ResumeAnalysisResult],
        transcript_analysis: Optional[TranscriptAnalysisResult]
    ) -> float:
        """Compute semantic similarity using embeddings"""
        if not self.model:
            return 0.7  # Default moderate similarity
        
        try:
            # Create JD text
            jd_text = f"{jd.title}. {jd.description}"
            
            # Create candidate text
            candidate_text_parts = []
            if resume_analysis:
                candidate_text_parts.append(resume_analysis.parsed_text[:1000])
            if transcript_analysis:
                candidate_text_parts.append(transcript_analysis.transcript[:1000])
            
            if not candidate_text_parts:
                return 0.5
            
            candidate_text = " ".join(candidate_text_parts)
            
            # Compute embeddings
            jd_embedding = self.model.encode([jd_text])
            candidate_embedding = self.model.encode([candidate_text])
            
            # Compute cosine similarity
            similarity = cosine_similarity(jd_embedding, candidate_embedding)[0][0]
            
            return float(max(0.0, min(1.0, similarity)))
            
        except Exception as e:
            logger.error(f"Error computing semantic similarity: {str(e)}")
            return 0.6
    
    def _identify_strengths(
        self,
        matching_skills: List[str],
        preferred_skills: List[str]
    ) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        if len(matching_skills) > 5:
            strengths.append(f"Strong technical skill match with {len(matching_skills)} matching skills")
        
        # Check for preferred skills
        matching_preferred = set(s.lower() for s in matching_skills).intersection(
            set(s.lower() for s in preferred_skills)
        )
        if matching_preferred:
            strengths.append(f"Has preferred skills: {', '.join(list(matching_preferred)[:3])}")
        
        return strengths
    
    def _identify_gaps(self, missing_skills: List[str]) -> List[str]:
        """Identify skill gaps"""
        gaps = []
        
        if missing_skills:
            if len(missing_skills) <= 3:
                gaps.append(f"Minor skill gaps: {', '.join(missing_skills)}")
            else:
                gaps.append(f"Multiple skill gaps including: {', '.join(missing_skills[:3])}")
        
        return gaps
