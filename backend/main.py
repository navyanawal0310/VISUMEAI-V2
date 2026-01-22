from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
from app.config.settings import settings
from app.api.routes import router

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
