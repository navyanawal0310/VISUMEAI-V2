import re
import logging
import math
from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import httpx
from ..models.schemas import (
    RoleMatchResult, JobDescription,
    ResumeAnalysisResult, TranscriptAnalysisResult,
)
from ..config.settings import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scoring constants
# ---------------------------------------------------------------------------

# Weights for overall match_percentage — must sum to 1.0
_W_TECHNICAL     = 0.40
_W_EXPERIENCE    = 0.20
_W_COMMUNICATION = 0.15
_W_ATS           = 0.10
_W_VIDEO         = 0.15

# Experience scoring thresholds
_EXP_FULL_CREDIT_RATIO  = 1.0   # meets or exceeds requirement
_EXP_PARTIAL_FLOOR      = 0.30  # minimum score when exp is 0 vs large requirement
_EXP_ABOVE_BONUS        = 5.0   # flat bonus points for exceeding by ≥1 year (capped at 100)

# Preferred-skill bonus to technical score
_PREFERRED_BONUS_PER_SKILL = 2.0   # points per preferred skill matched
_PREFERRED_BONUS_CAP        = 10.0  # maximum bonus


class RoleMatcher:
    """Match candidate profiles against job requirements."""

    def __init__(self):
        try:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer loaded")
        except Exception as e:
            logger.warning(f"SentenceTransformer unavailable: {e}")
            self.model = None

    # ── Public API ─────────────────────────────────────────────────────────

    async def match_role(
        self,
        job_description,
        resume_analysis=None,
        transcript_analysis=None,
        video_score: float = 0.0,
    ) -> RoleMatchResult:
        """Return a fully-populated RoleMatchResult."""
        try:
            logger.info(f"Matching against role: {job_description.title}")

            # Ensure required_skills is populated
            if not job_description.required_skills:
                job_description = await self._extract_jd_requirements(job_description)

            required_skills = {s.lower() for s in job_description.required_skills}
            preferred_skills = {s.lower() for s in (job_description.preferred_skills or [])}

            # Gather all candidate skills
            candidate_skills: set = set()
            if resume_analysis:
                candidate_skills.update(s.lower() for s in resume_analysis.skills)
                candidate_skills.update(s.lower() for s in resume_analysis.tools)
            if transcript_analysis:
                candidate_skills.update(t.lower() for t in transcript_analysis.technical_terms)

            # Skill overlap
            matching_skills = sorted(candidate_skills & required_skills)
            missing_skills  = sorted(required_skills - candidate_skills)

            # ── Component scores ──────────────────────────────────────────

            technical_score = self._score_technical(
                required_skills, preferred_skills, candidate_skills
            )

            experience_score, experience_match = self._score_experience(
                job_description.experience_years,
                resume_analysis.experience_years if resume_analysis else None,
            )

            communication_score = await self._score_communication(
                job_description, resume_analysis, transcript_analysis
            )

            ats_score = self._score_ats(
                required_skills, candidate_skills,
                resume_analysis, transcript_analysis
            )

            # ── Overall ───────────────────────────────────────────────────
            match_percentage = (
                technical_score      * _W_TECHNICAL +
                experience_score     * _W_EXPERIENCE +
                communication_score  * _W_COMMUNICATION +
                ats_score            * _W_ATS +
                video_score          * _W_VIDEO
                )
            match_percentage = round(min(100.0, max(0.0, match_percentage)), 1)

            # ── Semantic similarity (informational only) ──────────────────
            semantic_similarity = communication_score / 100.0

            # ── Narrative ────────────────────────────────────────────────
            strengths = self._build_strengths(
                matching_skills, preferred_skills,
                experience_match, technical_score,
            )
            gaps = self._build_gaps(
                missing_skills, experience_match,
                job_description.experience_years,
                resume_analysis.experience_years if resume_analysis else None,
            )
            feedback = self._build_feedback(
                match_percentage, technical_score, experience_score,
                communication_score, strengths, gaps,
            )

            result = RoleMatchResult(
                match_percentage=match_percentage,
                video_score=round(video_score, 1),
                technical_score=round(technical_score, 1),
                experience_score=round(experience_score, 1),
                ats_score=round(ats_score, 1),
                communication_score=round(communication_score, 1),
                matching_skills=matching_skills,
                missing_skills=missing_skills[:10],
                experience_match=experience_match,
                semantic_similarity=round(semantic_similarity, 3),
                strengths=strengths,
                gaps=gaps,
                feedback=feedback,
            )

            logger.info(
                f"Match complete — overall:{result.match_percentage} "
                f"tech:{result.technical_score} exp:{result.experience_score} "
                f"comm:{result.communication_score} ats:{result.ats_score}"
            )
            return result

        except Exception as e:
            logger.error(f"match_role error: {e}")
            raise

    # ── Scoring helpers ────────────────────────────────────────────────────

    def _score_technical(
        self,
        required: set,
        preferred: set,
        candidate: set,
    ) -> float:
        """
        Base score = % of required skills matched (0–100).
        Bonus = preferred skills matched * 2 pts, capped at 10.
        Total is capped at 100.
        """
        if not required:
            # No required skills defined: use preferred coverage as proxy
            if not preferred:
                return 50.0
            covered = len(candidate & preferred) / len(preferred) * 100
            return round(min(100.0, covered), 1)

        base = len(candidate & required) / len(required) * 100

        bonus = min(
            len(candidate & preferred) * _PREFERRED_BONUS_PER_SKILL,
            _PREFERRED_BONUS_CAP,
        )
        return round(min(100.0, base + bonus), 1)

    def _score_experience(
        self,
        required_years: Optional[int],
        candidate_years: Optional[float],
    ) -> tuple:
        """
        Returns (score: float, match: bool).

        Scoring curve:
        - candidate_years >= required_years  → 100 (+ small overqualification bonus)
        - candidate_years == 0               → 30
        - in between                         → linear interpolation 30 → 100
        - required_years is None             → 80 (unspecified; no penalty)
        - candidate_years is None            → 50 (unknown; conservative)
        """
        if required_years is None:
            # No requirement stated — benefit of the doubt
            return 80.0, True

        if candidate_years is None:
            # Cannot verify — conservative default
            return 50.0, False

        match = candidate_years >= required_years

        if required_years == 0:
            return 100.0, True

        ratio = candidate_years / required_years
        if ratio >= 1.0:
            # Meets or exceeds — award full credit plus a small bonus for seniority
            score = min(100.0, 95.0 + min(candidate_years - required_years, 1.0) * 5.0)
        else:
            # Linear ramp from 30 (0 years) to 95 (meets requirement)
            score = 30.0 + ratio * 65.0

        return round(score, 1), match

    def _score_ats(
        self,
        required_skills: set,
        candidate_skills: set,
        resume_analysis: Optional[ResumeAnalysisResult],
        transcript_analysis: Optional[TranscriptAnalysisResult],
    ) -> float:
        """
        ATS score based on three signals (each weighted):
        1. Keyword coverage    (50 pts) — % of required skills present
        2. Section completeness (30 pts) — skills / education / experience / projects
        3. Resume length        (20 pts) — optimal 300–1 200 words
        """
        # 1. Keyword coverage
        if required_skills:
            kw_score = len(candidate_skills & required_skills) / len(required_skills) * 50
        else:
            kw_score = 35.0  # no JD to compare; partial credit

        # 2. Section completeness
        section_score = 0.0
        if resume_analysis:
            if resume_analysis.skills:
                section_score += 10
            if resume_analysis.education:
                section_score += 7
            if resume_analysis.experience_years and resume_analysis.experience_years > 0:
                section_score += 8
            if resume_analysis.projects:
                section_score += 5

        # 3. Resume length
        length_score = 0.0
        if resume_analysis:
            word_count = len(resume_analysis.parsed_text.split())
            if 300 <= word_count <= 1200:
                length_score = 20.0
            elif word_count < 300:
                length_score = (word_count / 300) * 20.0
            else:
                # Diminishing score above 1 200, hits 0 at 2 400
                excess = min(word_count - 1200, 1200)
                length_score = max(0.0, (1 - excess / 1200) * 20.0)

        total = kw_score + section_score + length_score
        return round(min(100.0, total), 1)

    async def _score_communication(
        self,
        jd: JobDescription,
        resume_analysis: Optional[ResumeAnalysisResult],
        transcript_analysis: Optional[TranscriptAnalysisResult],
    ) -> float:
        """
        Semantic similarity between JD and candidate content, scaled 0–100.
        Falls back to a content-based heuristic when the model is unavailable
        so the score remains informative rather than a flat constant.
        """
        if self.model:
            try:
                jd_text = f"{jd.title}. {jd.description}"
                parts: List[str] = []
                if resume_analysis:
                    parts.append(resume_analysis.parsed_text[:1500])
                if transcript_analysis:
                    parts.append(transcript_analysis.transcript[:1000])
                if not parts:
                    return 50.0

                candidate_text = " ".join(parts)
                jd_emb   = self.model.encode([jd_text])
                cand_emb = self.model.encode([candidate_text])
                sim = float(cosine_similarity(jd_emb, cand_emb)[0][0])
                # Cosine similarity for text embeddings typically sits in 0.2–0.9;
                # rescale to 0–100 so the full range is usable in the UI
                rescaled = (max(0.0, sim - 0.15) / 0.75) * 100
                return round(min(100.0, max(0.0, rescaled)), 1)
            except Exception as e:
                logger.error(f"Semantic similarity error: {e}")

        # ── Heuristic fallback (no model) ─────────────────────────────────
        # Count how many JD tokens appear in the resume text
        if not resume_analysis:
            return 45.0
        jd_tokens = set(re.findall(r"\b\w{4,}\b", jd.description.lower()))
        resume_tokens = set(re.findall(r"\b\w{4,}\b", resume_analysis.parsed_text.lower()))
        if not jd_tokens:
            return 45.0
        overlap = len(jd_tokens & resume_tokens) / len(jd_tokens)
        # Map 0→20, 0.5→65, 1.0→90
        score = 20 + overlap * 70
        return round(min(90.0, score), 1)

    # ── Narrative builders ────────────────────────────────────────────────

    def _build_strengths(
        self,
        matching_skills: List[str],
        preferred: set,
        experience_match: bool,
        technical_score: float,
    ) -> List[str]:
        out: List[str] = []
        if technical_score >= 80:
            out.append(
                f"Strong technical alignment — {len(matching_skills)} of "
                f"{len(matching_skills) + 0} required skills matched"
            )
        elif len(matching_skills) >= 3:
            out.append(f"Solid overlap: {len(matching_skills)} required skills matched")

        bonus = [s for s in matching_skills if s in preferred]
        if bonus:
            out.append(f"Also has preferred skills: {', '.join(bonus[:3])}")

        if experience_match:
            out.append("Meets or exceeds the required years of experience")

        return out

    def _build_gaps(
        self,
        missing_skills: List[str],
        experience_match: bool,
        required_years: Optional[int],
        candidate_years: Optional[float],
    ) -> List[str]:
        out: List[str] = []
        if missing_skills:
            top = missing_skills[:4]
            out.append(
                f"{len(missing_skills)} required skill(s) not found — "
                f"top gaps: {', '.join(top)}"
            )
        if not experience_match and required_years is not None and candidate_years is not None:
            deficit = required_years - candidate_years
            out.append(
                f"Experience gap: {candidate_years:.1f} yrs detected, "
                f"{required_years} yrs required (deficit ≈ {deficit:.1f} yrs)"
            )
        return out

    def _build_feedback(
        self,
        overall: float,
        technical: float,
        experience: float,
        communication: float,
        strengths: List[str],
        gaps: List[str],
    ) -> str:
        parts: List[str] = []

        if overall >= 80:
            parts.append("Strong overall match — recommend advancing to interview.")
        elif overall >= 60:
            parts.append("Moderate match — worth a screening call to clarify gaps.")
        else:
            parts.append("Below threshold for this role — significant gaps identified.")

        if strengths:
            parts.append("Strengths: " + "; ".join(strengths) + ".")
        if gaps:
            parts.append("Gaps to address: " + "; ".join(gaps) + ".")

        # Dimension callouts
        if technical < 50:
            parts.append("Technical skill coverage needs improvement for this role.")
        if experience < 60:
            parts.append("Candidate may be under-experienced for this position.")
        if communication < 50:
            parts.append("Resume content alignment with the job description is low.")

        return " ".join(parts)

    # ── JD requirement extraction ─────────────────────────────────────────

    async def _extract_jd_requirements(self, jd: JobDescription) -> JobDescription:
        try:
            if settings.LLAMA_API_URL:
                skills = await self._extract_with_llama(jd.description)
                if skills:
                    jd.required_skills = skills
                    return jd
            jd.required_skills = self._extract_skills_keywords(jd.description)
            return jd
        except Exception as e:
            logger.error(f"JD extraction error: {e}")
            return jd

    async def _extract_with_llama(self, jd_text: str) -> List[str]:
        try:
            prompt = (
                "Extract a list of technical skills and requirements from the job description below. "
                "Return only skill names, one per line, no explanations.\n\n"
                f"Job Description:\n{jd_text}\n\nSkills:"
            )
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(
                    settings.LLAMA_API_URL,
                    json={"model": "llama3.2", "prompt": prompt, "stream": False},
                )
                if r.status_code == 200:
                    skills_text = r.json().get("response", "")
                    return [s.strip() for s in skills_text.splitlines() if s.strip()][:20]
        except Exception as e:
            logger.warning(f"Llama extraction failed: {e}")
        return []

    def _extract_skills_keywords(self, text: str) -> List[str]:
        """Lightweight fallback keyword extraction from JD text."""
        keywords = {
            "python", "java", "javascript", "react", "angular", "vue", "node.js",
            "django", "flask", "spring", "docker", "kubernetes", "aws", "azure",
            "sql", "nosql", "mongodb", "postgresql", "git", "agile", "scrum",
            "machine learning", "deep learning", "nlp", "computer vision", "api",
            "microservices", "rest", "graphql", "ci/cd", "devops", "linux",
            "tensorflow", "pytorch", "spark", "hadoop", "typescript", "golang",
        }
        text_l = text.lower()
        return [kw for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", text_l)]