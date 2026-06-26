from fastapi import FastAPI, UploadFile, File, Form, Depends
import uuid
import os
from app.services.resume_parser import ResumeParser
from app.services.role_matcher import RoleMatcher
from app.models.schemas import JobDescription
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
from app.config.settings import settings
from app.api.routes import router
from app.services.jd_parser import parse as parse_jd
from app.services.improvement_engine import generate as generate_recommendations
from app.services.video_analyzer import analyze as analyze_video
from app.services.pdf_generator import PDFGenerator
from app.models.schemas import CandidateEvaluation
from app.database.db import engine, get_db, Base
from app.database.models import CandidateRecord  # noqa: F401 — registers the table
from app.database import crud

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="VisumeAI API",
    description="AI-driven video resume analysis and role-matching system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for reports
if os.path.exists(os.path.join(settings.UPLOAD_DIR, 'reports')):
    app.mount(
        "/reports",
        StaticFiles(directory=os.path.join(settings.UPLOAD_DIR, 'reports')),
        name="reports"
    )

# Include routers
app.include_router(router, prefix="/api/v1", tags=["VisumeAI"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting VisumeAI Backend...")
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")
    
    # Download spaCy model if not present
    try:
        import spacy
        try:
            spacy.load(settings.SPACY_MODEL)
            logger.info(f"spaCy model '{settings.SPACY_MODEL}' loaded successfully")
        except:
            logger.warning(f"spaCy model '{settings.SPACY_MODEL}' not found. Please install with:")
            logger.warning(f"python -m spacy download {settings.SPACY_MODEL}")
    except ImportError:
        logger.warning("spaCy not installed")

# Upload directory setup
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "reports"), exist_ok=True)

# Create database tables (no-op if they already exist)
Base.metadata.create_all(bind=engine)


@app.get("/candidates")
def list_candidates(db=Depends(get_db)):
    """Return all stored candidate evaluations, newest first."""
    records = crud.get_all_evaluations(db)
    return [
        {
            "id":                   r.id,
            "candidate_name":       r.candidate_name,
            "resume_filename":      r.resume_filename,
            "job_title":            r.job_title,
            "overall_score":        r.overall_score,
            "technical_score":      r.technical_score,
            "experience_score":     r.experience_score,
            "ats_score":            r.ats_score,
            "communication_score":  r.communication_score,
            "matched_skills":       [s.strip() for s in r.matched_skills.split(",") if s.strip()],
            "missing_skills":       [s.strip() for s in r.missing_skills.split(",") if s.strip()],
            "report_url":           r.report_url,
            "created_at":           r.created_at.isoformat(),
        }
        for r in records
    ]

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    jd_text: str = Form(""),
    video: UploadFile = File(None),
):
    try:
        # Save file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Parse resume
        parser = ResumeParser()
        parsed = await parser.parse_resume(file_path, file_id)

        logger.info(f"PARSED — skills:{len(parsed.skills)} exp:{parsed.experience_years}")

        # Build JobDescription from submitted JD text (or safe defaults when absent)
        jd_data = parse_jd(jd_text)
        job = JobDescription(**jd_data)
        logger.info(
            f"JD parsed — title:'{job.title}' "
            f"required:{len(job.required_skills)} "
            f"preferred:{len(job.preferred_skills)} "
            f"exp:{job.experience_years}"
        )
        
        # Analyze video resume (optional — non-fatal if absent or fails)
        video_score    = None
        video_feedback = []
        if video and video.filename:
            try:
                vid_id   = str(uuid.uuid4())
                vid_path = os.path.join(UPLOAD_DIR, f"{vid_id}_{video.filename}")
                vid_content = await video.read()
                with open(vid_path, "wb") as vf:
                    vf.write(vid_content)
                video_result   = analyze_video(vid_path)
                video_score    = video_result.get("video_score")
                video_feedback = video_result.get("video_feedback", [])
                logger.info(f"VIDEO — score:{video_score} feedback_count:{len(video_feedback)}")
            except Exception as vid_err:
                logger.error(f"Video analysis failed (non-fatal): {vid_err}")

        # ✅ Match role
        matcher = RoleMatcher()
        match = await matcher.match_role(
            job_description=job,
            resume_analysis=parsed,
            video_score=video_score or 0.0
            )

        logger.info(f"MATCH — overall:{match.match_percentage} tech:{match.technical_score}")

        # Build ATS analysis block for the frontend ATS section
        ats_issues: list = []
        ats_recs: list = []
        if not parsed.skills:
            ats_issues.append("No skills section detected")
            ats_recs.append("Add a dedicated skills section")
        if not parsed.education:
            ats_issues.append("No education section detected")
            ats_recs.append("Add an education section")
        if not parsed.projects:
            ats_issues.append("No projects detected")
            ats_recs.append("Add a projects section to show applied experience")
        if match.missing_skills:
            top_missing = match.missing_skills[:3]
            ats_issues.append(
                f"Missing high-value keywords: {', '.join(top_missing)}"
            )
            ats_recs.append(
                "Mirror key terms from the job description in your resume"
            )
        word_count = len(parsed.parsed_text.split())
        if word_count < 300:
            ats_issues.append(f"Resume too short ({word_count} words; aim for 300–1 200)")
            ats_recs.append("Expand bullet points with quantified achievements")
        elif word_count > 1200:
            ats_issues.append(f"Resume too long ({word_count} words; trim to under 1 200)")
            ats_recs.append("Remove older or less-relevant roles to a single line each")

        # Generate improvement recommendations
        improvement_recommendations = generate_recommendations(
            technical_score=match.technical_score,
            ats_score=match.ats_score,
            experience_score=match.experience_score,
            communication_score=match.communication_score,
            missing_skills=match.missing_skills,
            strengths=match.strengths,
            gaps=match.gaps,
        )


        # Generate PDF report
        report_url = None
        try:
            evaluation_obj = CandidateEvaluation(
                evaluation_id=file_id,
                candidate_name="Candidate",
                resume_analysis=parsed,
                role_match=match,
                overall_score=round(match.match_percentage, 1),
                recommendation=(
                    "Highly Recommended" if match.match_percentage >= 80
                    else "Recommended" if match.match_percentage >= 60
                    else "Needs Further Review"
                ),
            )
            pdf_path = PDFGenerator().generate_evaluation_pdf(
                evaluation=evaluation_obj,
                job_title=job.title,
            )
            report_url = "/reports/" + os.path.basename(pdf_path)
            logger.info(f"PDF report saved: {pdf_path}")
        except Exception as pdf_err:
            logger.error(f"PDF generation failed (non-fatal): {pdf_err}")

        # Persist evaluation to database
        with next(get_db()) as db_session:
            crud.save_evaluation(
                db_session,
                candidate_name="Candidate",
                resume_filename=file.filename or file_path,
                job_title=job.title,
                overall_score=round(match.match_percentage, 2),
                technical_score=round(match.technical_score, 2),
                experience_score=round(match.experience_score, 2),
                ats_score=round(match.ats_score, 2),
                communication_score=round(match.communication_score, 2),
                matched_skills=match.matching_skills,
                missing_skills=match.missing_skills,
                report_url=report_url,
            )

        return {
            "match_percentage":   round(match.match_percentage, 2),
            "technical_score":    round(match.technical_score, 2),
            "experience_score":   round(match.experience_score, 2),
            "ats_score":          round(match.ats_score, 2),
            "communication_score": round(match.communication_score, 2),

            "matching_skills":    match.matching_skills,
            "missing_skills":     match.missing_skills,

            "experience_match":   match.experience_match,
            "semantic_similarity": match.semantic_similarity,

            "strengths":          match.strengths,
            "gaps":               match.gaps,
            "feedback":           match.feedback,

            "ats_analysis": {
                "ats_score":          round(match.ats_score, 2),
                "issues":             ats_issues,
                "recommendations":    ats_recs,
            },

            "improvement_recommendations": improvement_recommendations,

            "report_url": report_url,

            "video_score": round(match.video_score, 2),
            "video_feedback": video_feedback,
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {"error": str(e)}

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down VisumeAI Backend...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "VisumeAI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )