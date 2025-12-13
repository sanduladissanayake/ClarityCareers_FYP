"""
Job posting routes for ClarityCareers
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.db import get_db
from app.models.database import User, Job
from app.routes.auth import get_current_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# Pydantic models
class JobCreate(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    description: str
    requirements: Optional[str] = None
    job_type: str = "Full-time"
    salary_range: Optional[str] = None

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str]
    description: str
    requirements: Optional[str]
    job_type: str
    salary_range: Optional[str]
    recruiter_id: int
    is_active: bool
    created_at: datetime
    application_count: int = 0
    
    class Config:
        from_attributes = True

# Routes
@router.post("/", response_model=dict)
def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job posting (recruiters only)"""
    if current_user.user_type != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can post jobs")
    
    try:
        new_job = Job(
            **job_data.dict(),
            recruiter_id=current_user.id
        )
        
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        return {
            "id": new_job.id,
            "title": new_job.title,
            "company": new_job.company,
            "location": new_job.location or None,
            "description": new_job.description,
            "requirements": new_job.requirements or None,
            "job_type": new_job.job_type or "Full-time",
            "salary_range": new_job.salary_range or None,
            "recruiter_id": new_job.recruiter_id,
            "is_active": new_job.is_active,
            "created_at": new_job.created_at.isoformat() if new_job.created_at else None,
            "application_count": 0
        }
    except Exception as e:
        print(f"Error in create_job: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating job: {str(e)}")

@router.get("/", response_model=List[dict])
def list_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all active jobs"""
    try:
        jobs = db.query(Job).filter(Job.is_active == True).offset(skip).limit(limit).all()
        
        response_jobs = []
        for job in jobs:
            response_jobs.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location or None,
                "description": job.description,
                "requirements": job.requirements or None,
                "job_type": job.job_type or "Full-time",
                "salary_range": job.salary_range or None,
                "recruiter_id": job.recruiter_id,
                "is_active": job.is_active,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "application_count": 0
            })
        
        return response_jobs
    except Exception as e:
        print(f"Error in list_jobs: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")

@router.get("/my-jobs", response_model=List[dict])
def get_my_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get jobs posted by current recruiter"""
    if current_user.user_type != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can access this")
    
    try:
        jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).all()
        
        response_jobs = []
        for job in jobs:
            response_jobs.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location or None,
                "description": job.description,
                "requirements": job.requirements or None,
                "job_type": job.job_type or "Full-time",
                "salary_range": job.salary_range or None,
                "recruiter_id": job.recruiter_id,
                "is_active": job.is_active,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "application_count": 0
            })
        
        return response_jobs
    except Exception as e:
        print(f"Error in get_my_jobs: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")

@router.get("/{job_id}", response_model=dict)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job details"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location or None,
            "description": job.description,
            "requirements": job.requirements or None,
            "job_type": job.job_type or "Full-time",
            "salary_range": job.salary_range or None,
            "recruiter_id": job.recruiter_id,
            "is_active": job.is_active,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "application_count": 0
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_job: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching job: {str(e)}")

@router.put("/{job_id}", response_model=dict)
def update_job(
    job_id: int,
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a job posting"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.recruiter_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this job")
        
        for key, value in job_data.dict().items():
            setattr(job, key, value)
        
        db.commit()
        db.refresh(job)
        
        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location or None,
            "description": job.description,
            "requirements": job.requirements or None,
            "job_type": job.job_type or "Full-time",
            "salary_range": job.salary_range or None,
            "recruiter_id": job.recruiter_id,
            "is_active": job.is_active,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "application_count": 0
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_job: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating job: {str(e)}")

@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a job posting"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this job")
    
    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}
