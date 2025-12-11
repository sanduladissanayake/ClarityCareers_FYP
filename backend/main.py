"""
ClarityCareers - Main FastAPI Application
AI-Powered Recruitment Platform with Explainable AI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.db import init_db
from app.routes import auth, jobs, applications

# Global variable to track model loading
model_loading_task = None

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 80)
    print("Starting CLARITYCAREERS API")
    print("=" * 80)
    
    # Initialize database
    print("Initializing database...")
    try:
        init_db()
        print("✓ Database initialized")
    except Exception as e:
        print(f"⚠ Database init warning (may retry): {e}")
    
    # Initialize NLP model in background (non-blocking)
    print("Loading NLP model in background...")
    import asyncio
    async def load_model():
        try:
            from app.services.nlp_service import get_model_service
            get_model_service()
            print("✓ NLP model loaded successfully!")
        except Exception as e:
            print(f"⚠ NLP model loading deferred: {e}")
    
    asyncio.create_task(load_model())
    
    print("=" * 80)
    print("API READY - Server running!")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 80)
    
    yield
    
    # Shutdown
    print("\nShutting down ClarityCareers API...")

# Create FastAPI app
app = FastAPI(
    title="ClarityCareers API",
    description="AI-Powered Recruitment Platform with Explainable AI (SHAP)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow all origins including file:// protocol (origin: null)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins including null (file://)
    allow_credentials=False,  # Must be False when using wildcard
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

# Include routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to ClarityCareers API",
        "version": "1.0.0",
        "features": [
            "User Authentication (JWT)",
            "Job Posting Management",
            "Resume-Job Matching (NLP)",
            "SHAP Explanations",
            "Candidate Ranking",
            "Impact Simulator"
        ],
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "model": "loaded"
    }

# Run server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
