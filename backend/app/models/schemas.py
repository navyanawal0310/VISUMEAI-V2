from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
import uuid

class UserRole(str, Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    ADMIN = "admin"

class User(BaseModel):
    id: Optional[int] = None
    email: str
    name: str
    role: UserRole
    created_at: Optional[datetime] = None

class VideoUploadResponse(BaseModel):
    video_id: str
    filename: str
    status: str
    message: str

class ResumeUploadResponse(BaseModel):
    resume_id: str
    filename: str
    status: str
    message: str

class JobDescription(BaseModel):
    title: str
    description: str
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    experience_years: Optional[int] = None

class JobPosting(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    experience_years: Optional[int] = None
    status: str = "active"  # active, closed, draft
    created_by: str = "system"  # recruiter_id
    created_at: datetime = Field(default_factory=datetime.now)
    applications_count: int = 0

class JobPostingCreate(BaseModel):
    title: str
    description: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    experience_years: Optional[int] = None

class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    status: Optional[str] = None

class VideoAnalysisResult(BaseModel):
    video_id: str
    confidence_score: float = Field(..., ge=0, le=1)
    eye_contact_score: float = Field(..., ge=0, le=1)
    posture_score: float = Field(..., ge=0, le=1)
    gesture_score: float = Field(..., ge=0, le=1)
    expressiveness_score: float = Field(..., ge=0, le=1)
    engagement_score: float = Field(default=0.0, ge=0, le=1)  # New: holistic engagement
    frame_count: int
    duration_seconds: float
    # Confidence intervals for transparency
    eye_contact_confidence: Optional[Dict[str, float]] = None  # {lower, upper}
    posture_confidence: Optional[Dict[str, float]] = None
    measurement_notes: Optional[List[str]] = []  # Contextual notes

class TranscriptAnalysisResult(BaseModel):
    transcript: str
    clarity_score: float = Field(..., ge=0, le=1)
    vocabulary_diversity: float = Field(..., ge=0, le=1)
    coherence_score: float = Field(..., ge=0, le=1)
    technical_terms: List[str]
    word_count: int
    sentiment: str

class ResumeAnalysisResult(BaseModel):
    resume_id: str
    parsed_text: str
    skills: List[str]
    experience_years: Optional[float] = None
    education: List[str]
    certifications: List[str]
    tools: List[str]

class RoleMatchResult(BaseModel):
    match_percentage: float = Field(..., ge=0, le=100)
    matching_skills: List[str]
    missing_skills: List[str]
    experience_match: bool
    semantic_similarity: float = Field(..., ge=0, le=1)
    strengths: List[str]
    gaps: List[str]

class SoftSkillIndex(BaseModel):
    communication: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    engagement: float = Field(..., ge=0, le=1)
    professionalism: float = Field(..., ge=0, le=1)
    overall_score: float = Field(..., ge=0, le=1)

class CandidateEvaluation(BaseModel):
    evaluation_id: str
    candidate_name: str
    video_analysis: Optional[VideoAnalysisResult] = None
    transcript_analysis: Optional[TranscriptAnalysisResult] = None
    resume_analysis: Optional[ResumeAnalysisResult] = None
    role_match: Optional[RoleMatchResult] = None
    soft_skill_index: Optional[SoftSkillIndex] = None
    overall_score: float = Field(..., ge=0, le=100)
    recommendation: str
    created_at: datetime = Field(default_factory=datetime.now)
    accessibility_mode_used: bool = False  # Track if accessibility mode was used
    recruiter_override: Optional[Dict[str, float]] = None  # Allow manual score adjustments
    override_reason: Optional[str] = None
    # NEW: Version tracking
    job_id: Optional[str] = None  # Which job was this for
    submission_version: int = 1  # Which attempt is this (1, 2, 3, etc.)
    previous_evaluation_id: Optional[str] = None  # Link to previous attempt

class ImprovementComparison(BaseModel):
    """Comparison between two evaluations showing improvement"""
    candidate_name: str
    job_title: str
    previous_version: int
    current_version: int
    previous_score: float
    current_score: float
    score_change: float  # Positive = improvement
    score_change_percentage: float
    improvements: Dict[str, Dict[str, float]]  # Category → {old, new, change}
    areas_improved: List[str]
    areas_declined: List[str]
    overall_improvement_summary: str
    recommendation_change: str  # e.g., "Improved from 'Recommended' to 'Highly Recommended'"

class FeedbackReport(BaseModel):
    evaluation_id: str
    candidate_name: str
    role_title: str
    overall_score: float
    technical_score: float
    soft_skill_score: float
    role_match_score: float
    strengths: List[str]
    areas_for_improvement: List[str]
    detailed_feedback: Dict[str, str]
    recommendations: List[str]
    report_url: Optional[str] = None

class EvaluationRequest(BaseModel):
    video_id: Optional[str] = None
    resume_id: Optional[str] = None
    candidate_name: str
    job_id: Optional[str] = None  # New: reference to job posting
    job_description: Optional[JobDescription] = None  # Deprecated: for backward compatibility
    accessibility_mode: bool = False  # Disable visual analysis if True
