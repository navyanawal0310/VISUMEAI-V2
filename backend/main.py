from fastapi import FastAPI, UploadFile, File, Form
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

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    jd_text: str = Form(""),
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

        # ✅ Match role
        matcher = RoleMatcher()
        match = await matcher.match_role(
            job_description=job,
            resume_analysis=parsed
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

            # Structured ATS block — consumed by the ATS section in EvaluationPage
            "ats_analysis": {
                "ats_score":          round(match.ats_score, 2),
                "issues":             ats_issues,
                "recommendations":    ats_recs,
            },
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