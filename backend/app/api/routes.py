from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import os
import uuid
import shutil
import logging
from ..models.schemas import (
    VideoUploadResponse,
    ResumeUploadResponse,
    CandidateEvaluation,
    FeedbackReport,
    EvaluationRequest,
    JobDescription,
    JobPosting,
    JobPostingCreate,
    JobPostingUpdate,
    ImprovementComparison
)
from ..services.video_processor import VideoProcessor
from ..services.audio_processor import AudioProcessor
from ..services.nlp_analyzer import NLPAnalyzer
from ..services.resume_parser import ResumeParser
from ..services.role_matcher import RoleMatcher
from ..services.soft_skill_analyzer import SoftSkillAnalyzer
from ..services.feedback_generator import FeedbackGenerator
from ..services.video_quality_checker import VideoQualityChecker
from ..services.improvement_tracker import ImprovementTracker
from ..services.pdf_generator import PDFGenerator
from ..config.settings import settings
from ..config.evaluation_config import config
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
video_processor = VideoProcessor()
audio_processor = AudioProcessor()
nlp_analyzer = NLPAnalyzer()
resume_parser = ResumeParser()
role_matcher = RoleMatcher()
soft_skill_analyzer = SoftSkillAnalyzer()
feedback_generator = FeedbackGenerator()
video_quality_checker = VideoQualityChecker()
improvement_tracker = ImprovementTracker()
pdf_generator = PDFGenerator()

# In-memory storage for demo (replace with database in production)
evaluations_db = {}
job_postings_db = {}

def initialize_sample_jobs():
    """Create sample job postings if database is empty"""
    if not job_postings_db:
        samples = [
            {
                "title": "Senior Software Engineer",
                "description": "Looking for an experienced full-stack developer to join our growing team. You'll work on cutting-edge web applications using modern technologies and collaborate with cross-functional teams to deliver high-quality solutions.",
                "required_skills": ["Python", "React", "AWS", "PostgreSQL", "Docker"],
                "preferred_skills": ["Kubernetes", "GraphQL", "TypeScript", "Microservices"],
                "experience_years": 5
            },
            {
                "title": "Data Scientist",
                "description": "Join our ML team to build cutting-edge machine learning models and data pipelines. You'll work with large datasets, develop predictive models, and help drive data-driven decision making across the organization.",
                "required_skills": ["Python", "Machine Learning", "SQL", "Statistics", "Pandas"],
                "preferred_skills": ["PyTorch", "TensorFlow", "MLOps", "Spark", "Deep Learning"],
                "experience_years": 3
            },
            {
                "title": "Frontend Developer",
                "description": "Build beautiful, responsive user interfaces that delight our users. You'll work with modern frontend technologies to create intuitive and performant web applications.",
                "required_skills": ["JavaScript", "React", "HTML", "CSS", "Git"],
                "preferred_skills": ["TypeScript", "Next.js", "Tailwind CSS", "Redux", "Testing"],
                "experience_years": 2
            },
            {
                "title": "Product Manager",
                "description": "Lead product strategy and execution for our core platform. You'll work closely with engineering, design, and business teams to define product roadmap and drive successful product launches.",
                "required_skills": ["Product Strategy", "Agile", "Analytics", "User Research", "Communication"],
                "preferred_skills": ["A/B Testing", "Figma", "SQL", "Technical Background", "Leadership"],
                "experience_years": 4
            },
            {
                "title": "DevOps Engineer",
                "description": "Build and maintain our cloud infrastructure and deployment pipelines. You'll ensure our systems are scalable, reliable, and secure while enabling rapid development and deployment.",
                "required_skills": ["AWS", "Docker", "Kubernetes", "CI/CD", "Linux"],
                "preferred_skills": ["Terraform", "Monitoring", "Security", "Python", "GitOps"],
                "experience_years": 3
            }
        ]
        
        for sample in samples:
            job = JobPosting(**sample, status="active")
            job_postings_db[job.job_id] = job
        
        logger.info(f"Created {len(samples)} sample job postings")

# Initialize sample jobs on startup
initialize_sample_jobs()

@router.post("/upload/video", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    candidate_name: str = Form(...)
):
    """Upload and process video resume"""
    try:
        # Validate file
        if not file.filename.endswith(('.mp4', '.avi', '.mov', '.webm')):
            raise HTTPException(status_code=400, detail="Invalid video format")
        
        # Generate unique ID
        video_id = str(uuid.uuid4())
        
        # Save file
        file_extension = os.path.splitext(file.filename)[1]
        video_path = os.path.join(settings.UPLOAD_DIR, 'videos', f"{video_id}{file_extension}")
        
        with open(video_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Video uploaded: {video_id} for {candidate_name}")
        
        return VideoUploadResponse(
            video_id=video_id,
            filename=file.filename,
            status="uploaded",
            message="Video uploaded successfully"
        )
        
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    candidate_name: str = Form(...)
):
    """Upload resume file"""
    try:
        # Validate file
        if not file.filename.endswith(('.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="Invalid resume format. Use PDF or DOCX")
        
        # Generate unique ID
        resume_id = str(uuid.uuid4())
        
        # Save file
        file_extension = os.path.splitext(file.filename)[1]
        resume_path = os.path.join(settings.UPLOAD_DIR, 'resumes', f"{resume_id}{file_extension}")
        
        with open(resume_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Resume uploaded: {resume_id} for {candidate_name}")
        
        return ResumeUploadResponse(
            resume_id=resume_id,
            filename=file.filename,
            status="uploaded",
            message="Resume uploaded successfully"
        )
        
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs", response_model=JobPosting)
async def create_job_posting(
    job: JobPostingCreate,
    recruiter_id: str = "default_recruiter"
):
    """Create a new job posting (recruiter only)"""
    try:
        job_posting = JobPosting(
            **job.dict(),
            created_by=recruiter_id
        )
        job_postings_db[job_posting.job_id] = job_posting
        logger.info(f"Job posting created: {job_posting.job_id} - {job_posting.title}")
        return job_posting
    except Exception as e:
        logger.error(f"Error creating job posting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs", response_model=list[JobPosting])
async def list_job_postings(
    status: str = "active",
    limit: int = 50
):
    """List all job postings"""
    try:
        postings = [
            job for job in job_postings_db.values()
            if status == "all" or job.status == status
        ]
        postings.sort(key=lambda x: x.created_at, reverse=True)
        return postings[:limit]
    except Exception as e:
        logger.error(f"Error listing job postings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}", response_model=JobPosting)
async def get_job_posting(job_id: str):
    """Get specific job posting"""
    if job_id not in job_postings_db:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job_postings_db[job_id]

@router.put("/jobs/{job_id}", response_model=JobPosting)
async def update_job_posting(
    job_id: str,
    updates: JobPostingUpdate
):
    """Update job posting (recruiter only)"""
    try:
        if job_id not in job_postings_db:
            raise HTTPException(status_code=404, detail="Job posting not found")
        
        job = job_postings_db[job_id]
        update_data = updates.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(job, field, value)
        
        logger.info(f"Job posting updated: {job_id}")
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating job posting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/jobs/{job_id}")
async def delete_job_posting(job_id: str):
    """Delete job posting (recruiter only)"""
    try:
        if job_id not in job_postings_db:
            raise HTTPException(status_code=404, detail="Job posting not found")
        
        job_title = job_postings_db[job_id].title
        del job_postings_db[job_id]
        logger.info(f"Job posting deleted: {job_id} - {job_title}")
        return {"message": "Job posting deleted successfully", "job_id": job_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job posting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-video-quality")
async def check_video_quality(file: UploadFile = File(...)):
    """Check video quality before processing"""
    try:
        # Save uploaded file temporarily
        video_id = str(uuid.uuid4())
        video_path = f"uploads/videos/{video_id}.mp4"
        
        os.makedirs(os.path.dirname(video_path), exist_ok=True)
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check video quality
        quality_result = video_quality_checker.check_video_quality(video_path)
        
        # Clean up temporary file
        os.remove(video_path)
        
        return quality_result
        
    except Exception as e:
        logger.error(f"Error checking video quality: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking video quality: {str(e)}")

@router.post("/evaluate", response_model=CandidateEvaluation)
async def evaluate_candidate(request: EvaluationRequest):
    """Evaluate candidate against job description"""
    try:
        logger.info(f"Starting evaluation for: {request.candidate_name}")
        
        evaluation_id = str(uuid.uuid4())
        
        # Get job description - either from job_id or direct input (backward compatibility)
        job_description = None
        if request.job_id:
            if request.job_id not in job_postings_db:
                raise HTTPException(status_code=404, detail="Job posting not found")
            
            job_posting = job_postings_db[request.job_id]
            job_description = JobDescription(
                title=job_posting.title,
                description=job_posting.description,
                required_skills=job_posting.required_skills,
                preferred_skills=job_posting.preferred_skills,
                experience_years=job_posting.experience_years
            )
            
            # Increment application count
            job_posting.applications_count += 1
            logger.info(f"Using job posting: {job_posting.title}")
        elif request.job_description:
            job_description = request.job_description
            logger.info("Using inline job description (deprecated)")
        else:
            raise HTTPException(status_code=400, detail="Either job_id or job_description must be provided")
        
        # Process video if provided (unless accessibility mode is enabled)
        video_analysis = None
        transcript_analysis = None
        
        if request.video_id and not request.accessibility_mode:
            # Find video file
            video_files = [
                f for f in os.listdir(os.path.join(settings.UPLOAD_DIR, 'videos'))
                if f.startswith(request.video_id)
            ]
            if video_files:
                video_path = os.path.join(settings.UPLOAD_DIR, 'videos', video_files[0])
                
                # Process video (visual analysis)
                video_analysis = await video_processor.process_video(video_path, request.video_id)
                
                # Extract and transcribe audio (always do this, even in accessibility mode)
                transcript = await audio_processor.process_video_audio(video_path)
                
                # Analyze transcript
                transcript_analysis = await nlp_analyzer.analyze_transcript(transcript)
        elif request.video_id and request.accessibility_mode:
            # Accessibility mode: Skip visual analysis, only do audio transcription
            logger.info("Accessibility mode enabled: Skipping visual analysis")
            video_files = [
                f for f in os.listdir(os.path.join(settings.UPLOAD_DIR, 'videos'))
                if f.startswith(request.video_id)
            ]
            if video_files:
                video_path = os.path.join(settings.UPLOAD_DIR, 'videos', video_files[0])
                
                # Extract and transcribe audio only
                transcript = await audio_processor.process_video_audio(video_path)
                
                # Analyze transcript
                transcript_analysis = await nlp_analyzer.analyze_transcript(transcript)
        
        # Process resume if provided
        resume_analysis = None
        if request.resume_id:
            # Find resume file
            resume_files = [
                f for f in os.listdir(os.path.join(settings.UPLOAD_DIR, 'resumes'))
                if f.startswith(request.resume_id)
            ]
            if resume_files:
                resume_path = os.path.join(settings.UPLOAD_DIR, 'resumes', resume_files[0])
                resume_analysis = await resume_parser.parse_resume(resume_path, request.resume_id)
        
        # Match against role
        role_match = await role_matcher.match_role(
            job_description,
            resume_analysis,
            transcript_analysis
        )
        
        # Analyze soft skills
        soft_skill_index = await soft_skill_analyzer.analyze_soft_skills(
            video_analysis,
            transcript_analysis
        )
        
        # Compute overall score (adjust weights if no video analysis due to accessibility mode)
        if video_analysis:
            overall_score = (
                role_match.match_percentage * 0.4 +
                soft_skill_index.overall_score * 100 * 0.3 +
                video_analysis.confidence_score * 100 * 0.3
            )
        else:
            # Accessibility mode: No video analysis, increase other weights
            overall_score = (
                role_match.match_percentage * 0.6 +      # Increased from 0.4
                soft_skill_index.overall_score * 100 * 0.4  # Increased from 0.3
            )
            logger.info(f"Overall score calculated without video analysis (accessibility mode)")
        
        # Generate recommendation
        if overall_score >= 80:
            recommendation = "Highly Recommended"
        elif overall_score >= 60:
            recommendation = "Recommended"
        elif overall_score >= 40:
            recommendation = "Consider with Reservations"
        else:
            recommendation = "Not Recommended"
        
        # Check for previous submissions (version tracking)
        previous_submissions = [
            e for e in evaluations_db.values()
            if e.candidate_name.lower() == request.candidate_name.lower() 
            and e.job_id == request.job_id
        ]
        
        submission_version = len(previous_submissions) + 1
        previous_eval_id = None
        
        if previous_submissions:
            # Sort by version and get the latest
            previous_submissions.sort(key=lambda x: x.submission_version, reverse=True)
            previous_eval_id = previous_submissions[0].evaluation_id
            logger.info(f"Found {len(previous_submissions)} previous submission(s) for {request.candidate_name}")
        
        # Create evaluation
        evaluation = CandidateEvaluation(
            evaluation_id=evaluation_id,
            candidate_name=request.candidate_name,
            video_analysis=video_analysis,
            transcript_analysis=transcript_analysis,
            resume_analysis=resume_analysis,
            role_match=role_match,
            soft_skill_index=soft_skill_index,
            overall_score=overall_score,
            recommendation=recommendation,
            accessibility_mode_used=request.accessibility_mode,
            job_id=request.job_id,
            submission_version=submission_version,
            previous_evaluation_id=previous_eval_id
        )
        
        # Store in database
        evaluations_db[evaluation_id] = evaluation
        
        logger.info(f"Evaluation complete: {evaluation_id} - Score: {overall_score:.1f}")
        
        return evaluation
        
    except Exception as e:
        logger.error(f"Error evaluating candidate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evaluation/{evaluation_id}", response_model=CandidateEvaluation)
async def get_evaluation(evaluation_id: str):
    """Get evaluation by ID"""
    if evaluation_id not in evaluations_db:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    return evaluations_db[evaluation_id]

@router.post("/feedback/{evaluation_id}", response_model=FeedbackReport)
async def generate_feedback(evaluation_id: str, job_title: str = "Software Engineer"):
    """Generate detailed feedback report"""
    try:
        if evaluation_id not in evaluations_db:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        evaluation = evaluations_db[evaluation_id]
        
        feedback = await feedback_generator.generate_feedback(evaluation, job_title)
        
        return feedback
        
    except Exception as e:
        logger.error(f"Error generating feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evaluations")
async def list_evaluations(limit: int = 10):
    """List all evaluations (for recruiter dashboard)"""
    evaluations = list(evaluations_db.values())
    
    # Sort by date (newest first)
    evaluations.sort(key=lambda x: x.created_at, reverse=True)
    
    # Return summary
    return [
        {
            "evaluation_id": e.evaluation_id,
            "candidate_name": e.candidate_name,
            "overall_score": e.overall_score,
            "recommendation": e.recommendation,
            "created_at": e.created_at.isoformat()
        }
        for e in evaluations[:limit]
    ]

@router.get("/submission-history/{candidate_name}/{job_id}")
async def get_submission_history(candidate_name: str, job_id: str):
    """Get all submissions for a candidate-job combination"""
    try:
        all_evaluations = list(evaluations_db.values())
        history = improvement_tracker.get_submission_history(
            candidate_name,
            job_id,
            all_evaluations
        )
        
        if not history:
            return {
                "candidate_name": candidate_name,
                "job_id": job_id,
                "total_submissions": 0,
                "submissions": []
            }
        
        # Calculate overall improvement stats
        stats = improvement_tracker.calculate_overall_improvement_stats(history)
        
        return {
            "candidate_name": candidate_name,
            "job_id": job_id,
            "total_submissions": len(history),
            "submissions": [
                {
                    "evaluation_id": e.evaluation_id,
                    "version": e.submission_version,
                    "score": e.overall_score,
                    "recommendation": e.recommendation,
                    "created_at": e.created_at.isoformat()
                }
                for e in history
            ],
            "improvement_stats": stats
        }
    except Exception as e:
        logger.error(f"Error fetching submission history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare-submissions/{current_id}/{previous_id}", response_model=ImprovementComparison)
async def compare_submissions(current_id: str, previous_id: str):
    """Compare two evaluations and show improvement"""
    try:
        if current_id not in evaluations_db:
            raise HTTPException(status_code=404, detail="Current evaluation not found")
        if previous_id not in evaluations_db:
            raise HTTPException(status_code=404, detail="Previous evaluation not found")
        
        current = evaluations_db[current_id]
        previous = evaluations_db[previous_id]
        
        # Get job title
        job_title = "Unknown Position"
        if current.job_id and current.job_id in job_postings_db:
            job_title = job_postings_db[current.job_id].title
        
        # Generate comparison
        comparison = improvement_tracker.compare_evaluations(
            previous,
            current,
            job_title
        )
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing submissions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest-submission/{candidate_name}/{job_id}")
async def get_latest_submission(candidate_name: str, job_id: str):
    """Get the most recent submission for a candidate-job combination"""
    try:
        all_evaluations = list(evaluations_db.values())
        history = improvement_tracker.get_submission_history(
            candidate_name,
            job_id,
            all_evaluations
        )
        
        if not history:
            return None
        
        # Return latest submission
        latest = history[-1]
        return {
            "evaluation_id": latest.evaluation_id,
            "version": latest.submission_version,
            "score": latest.overall_score,
            "recommendation": latest.recommendation,
            "created_at": latest.created_at.isoformat(),
            "has_previous": latest.submission_version > 1
        }
    except Exception as e:
        logger.error(f"Error fetching latest submission: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-pdf/{evaluation_id}")
async def export_evaluation_to_pdf(evaluation_id: str):
    """Export evaluation report as PDF"""
    try:
        if evaluation_id not in evaluations_db:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        evaluation = evaluations_db[evaluation_id]
        
        # Get job title
        job_title = "Unknown Position"
        if evaluation.job_id and evaluation.job_id in job_postings_db:
            job_title = job_postings_db[evaluation.job_id].title
        
        # Generate PDF
        pdf_path = pdf_generator.generate_evaluation_pdf(evaluation, job_title)
        
        # Return file path for download
        from fastapi.responses import FileResponse
        return FileResponse(
            pdf_path,
            media_type='application/pdf',
            filename=f"VisumeAI_Evaluation_{evaluation.candidate_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "VisumeAI Backend"}
