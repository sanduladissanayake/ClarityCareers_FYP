"""
Application routes for ClarityCareers
Handles CV analysis, job applications, and application management
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import os
from pathlib import Path
import uuid

from app.db import get_db
from app.models.database import User, Job, Application, Message
from app.routes.auth import get_current_user
from app.services.nlp_service import get_model_service, get_pro_model_service
from app.utils.pdf_extractor import extract_text_from_pdf, validate_pdf_file

router = APIRouter(prefix="/applications", tags=["Applications"])

# Pydantic models
class ApplicationSubmit(BaseModel):
    job_id: int
    resume_text: str
    analysis_report: Optional[Dict] = None
    pdf_file_path: Optional[str] = None  # Path to PDF file from analysis

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    applicant_id: int
    resume_text: Optional[str]
    match_percentage: float
    prediction: str
    confidence: str
    status: str
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    subject: str
    content: str

class SkillSimulationRequest(BaseModel):
    job_id: int
    resume_text: str
    added_skills: List[str]
    original_match_percentage: float
    use_pro_model: bool = False

# GET resume text endpoint
@router.get("/{application_id}/resume")
def get_resume_text(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get resume text for an application"""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return {
        "application_id": application.id,
        "resume_text": application.resume_text or ""
    }

# GET download PDF endpoint
@router.get("/{application_id}/resume-pdf")
def download_resume_pdf(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Download the original PDF resume for an application"""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if not application.pdf_file_path or not os.path.exists(application.pdf_file_path):
        raise HTTPException(status_code=404, detail="Resume PDF not found")
    
    return FileResponse(
        path=application.pdf_file_path,
        media_type="application/pdf",
        filename="resume.pdf"
    )

# POST analyze CV endpoint
@router.post("/analyze-cv")
async def analyze_cv_preview(
    job_id: int,
    cv_file: UploadFile = File(...),
    use_pro_model: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze CV against job description WITHOUT submitting application
    Returns preview of match score, explanations, and recommendations
    """
    try:
        if current_user.user_type != "job_seeker":
            raise HTTPException(status_code=403, detail="Only job seekers can analyze CVs")
        
        # Validate job exists
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Read file content
        file_content = await cv_file.read()
        
        # Validate PDF file
        is_valid, error_message = validate_pdf_file(
            filename=cv_file.filename,
            file_size=len(file_content)
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Extract text from PDF
        try:
            resume_text = extract_text_from_pdf(file_content)
            print(f"Extracted {len(resume_text)} characters from PDF")
            print(f"First 200 chars: {resume_text[:200]}...")
        except ValueError as ve:
            # User-friendly error for extraction issues
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            print(f"PDF extraction error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")
        
        # Use NLP model to calculate match and get detailed analysis
        try:
            nlp_service = get_pro_model_service() if use_pro_model else get_model_service()
            print(f"Using {'pro' if use_pro_model else 'standard'} model for analysis")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to load analysis model: {str(e)}")

        # Get match score
        try:
            match_result = nlp_service.calculate_match(
                resume=resume_text.strip(),
                job_description=(job.description or "").strip()
            )
            print(f"Match score calculated: {match_result['match_percentage']}")
        except Exception as e:
            print(f"Error calculating match: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to calculate match: {str(e)}")
        
        # Get skill gap analysis FIRST so we can cache it for SHAP and recommendations
        # OPTIMIZATION #1: Cache skill extraction results to avoid redundant calls
        try:
            # Make sure we have valid strings
            job_desc = job.description if job.description else ""
            skill_gap = nlp_service.analyze_skills(
                resume=resume_text.strip(),
                job_description=job_desc.strip()
            )
        except Exception as e:
            print(f"Error analyzing skills: {str(e)}")
            import traceback
            traceback.print_exc()
            skill_gap = {"matched_skills": [], "missing_skills": []}
        
        # Get SHAP explanations - make this optional
        # OPTIMIZATION #3: Pass cached skills to avoid re-extraction
        try:
            shap_explanation = nlp_service.generate_shap_explanation(
                resume=resume_text,
                job_description=job.description if job.description else "",
                match_score=match_result["match_percentage"] / 100.0,  # Convert percentage to decimal for calculation
                cached_skills=skill_gap
            )
        except Exception as e:
            print(f"Warning - Error generating SHAP explanation: {str(e)}")
            shap_explanation = {"key_matches": [], "missing_keywords": []}
        
        # Get recommendations
        try:
            recommendations = nlp_service.generate_recommendations(
                missing_skills=skill_gap.get("missing_skills", []),
                job_description=job.description if job.description else "",
                match_score=match_result["match_percentage"],
                resume=resume_text.strip()  # Pass resume for simulator impact checking
            )
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            import traceback
            traceback.print_exc()
            recommendations = []
        
        # Extract and check hard requirements
        hard_requirements_extracted = {}
        hard_requirements_check = {}
        critical_gaps = []
        # Initialize hard requirements variables
        hard_requirements_extracted = {}
        hard_requirements_check = {}
        hard_reqs_points = 0
        hard_reqs_score = 0
        
        try:
            hard_requirements_extracted = nlp_service.extract_hard_requirements(
                job_description=job.description if job.description else ""
            )
            
            hard_requirements_check = nlp_service.check_candidate_against_requirements(
                resume=resume_text.strip(),
                requirements=hard_requirements_extracted
            )
            
            # Create detailed hard requirements status (NOT combined with skill gaps)
            # This provides clear visibility to recruiter without inflating missing skills list
        except Exception as e:
            print(f"Error extracting/checking hard requirements: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # DO NOT combine critical gaps with skill gaps - keep them separate!
        # This fixes the issue where hard requirement gaps inflated the missing skills list
        all_missing_skills = skill_gap.get("missing_skills", [])
        
        # CALCULATE WEIGHTED SCORE (Option 3: Hard Requirements Vector)
        # Final Score = (SBert * 0.70) + (Skill Match * 0.20) + (Hard Reqs * 0.10)
        try:
            sbert_score = match_result["match_percentage"]
            
            # Calculate skill match score (0-100)
            matched_count = len(skill_gap.get("matched_skills", []))
            total_jd_skills = matched_count + len(combined_gaps)
            skill_match_score = (matched_count / total_jd_skills * 100) if total_jd_skills > 0 else 0
            
            # Calculate hard requirements score (0-20, normalized to 0-100)
            hard_reqs_points = nlp_service.calculate_hard_requirements_score(hard_requirements_check)
            hard_reqs_score = (hard_reqs_points / 20 * 100)  # Normalize to 100
            
            # Weighted final score
            final_match_percentage = (sbert_score * 0.70) + (skill_match_score * 0.20) + (hard_reqs_score * 0.10)
            final_match_percentage = min(100, max(0, final_match_percentage))  # Clamp 0-100
            
            # Update prediction and confidence based on final score
            if final_match_percentage >= 50:
                final_prediction = "Match"
            else:
                final_prediction = "No Match"
            
            if final_match_percentage >= 70:
                final_confidence = "High"
            elif final_match_percentage >= 50:
                final_confidence = "Medium"
            else:
                final_confidence = "Low"
                
        except Exception as e:
            print(f"Error calculating weighted score: {str(e)}")
            final_match_percentage = match_result["match_percentage"]
            final_prediction = match_result["prediction"]
            final_confidence = match_result["confidence"]
            sbert_score = match_result["match_percentage"]
            skill_match_score = 0
            hard_reqs_score = 0
            hard_reqs_points = 0
        
        existing_applications = db.query(Application).filter(
            Application.job_id == job_id
        ).all()
        
        percentile_estimate = None
        if existing_applications:
            match_scores = [app.match_percentage for app in existing_applications if app.match_percentage]
            if match_scores:
                better_count = sum(1 for score in match_scores if match_result["match_percentage"] > score)
                percentile_estimate = (better_count / len(match_scores)) * 100
        
        # Save PDF file to storage
        pdf_file_path = None
        try:
            upload_dir = Path("backend/uploads/resumes")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename with UUID
            file_extension = ".pdf"
            filename = f"{uuid.uuid4()}{file_extension}"
            pdf_file_path = str(upload_dir / filename)
            
            # Write PDF file to disk
            with open(pdf_file_path, "wb") as f:
                f.write(file_content)
            print(f"PDF saved to {pdf_file_path}")
        except Exception as e:
            print(f"Warning: Failed to save PDF file: {str(e)}")
            pdf_file_path = None
        
        # Return comprehensive analysis preview
        preview_response = {
            "extracted_text": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,  # Preview
            "match_percentage": final_match_percentage,  # WEIGHTED FINAL SCORE (70% SBert + 20% Skills + 10% Hard Reqs)
            "sbert_score": sbert_score,  # Original SBert score (70% weight)
            "skill_match_score": skill_match_score,  # Skill match (20% weight)
            "hard_requirements_score": hard_reqs_score,  # Hard requirements (10% weight)
            "prediction": final_prediction,
            "confidence": final_confidence,
            "shap_explanations": shap_explanation,
            "skill_gap_analysis": {
                "matched_skills": skill_gap.get("matched_skills", []),
                "missing_skills": all_missing_skills,  # FIXED: NO longer mixed with hard requirements
                "skill_gap_percentage": skill_gap.get("skill_gap_percentage", 0),
                "note": "Skill gaps only - hard requirements checked separately below"
            },
            "recruiter_alert": {
                "title": "HARD REQUIREMENTS STATUS - REVIEW REQUIRED",
                "description": "These are mandatory requirements from the job description. Candidates missing these should be reviewed carefully.",
                "education": {
                    "required": hard_requirements_check.get('education', {}).get('required', 'Not specified'),
                    "met": hard_requirements_check.get('education', {}).get('met', False),
                    "status": "✓ MEETS" if hard_requirements_check.get('education', {}).get('met') else "✗ MISSING"
                },
                "experience": {
                    "required": hard_requirements_check.get('experience', {}).get('required', 'Not specified'),
                    "met": hard_requirements_check.get('experience', {}).get('met', False),
                    "status": "✓ MEETS" if hard_requirements_check.get('experience', {}).get('met') else "✗ MISSING"
                },
                "certifications": [
                    {
                        "name": cert['name'],
                        "met": cert.get('met', False),
                        "status": "✓" if cert.get('met') else "✗"
                    }
                    for cert in hard_requirements_check.get('certifications', [])
                ] if hard_requirements_check.get('certifications') else [],
                "other_requirements": [
                    {
                        "name": other['name'],
                        "met": other.get('met', False),
                        "status": "✓" if other.get('met') else "✗"
                    }
                    for other in hard_requirements_check.get('other', [])
                ] if hard_requirements_check.get('other') else [],
                "summary": f"Overall: {sum(1 for x in [hard_requirements_check.get('education', {}).get('met', False), hard_requirements_check.get('experience', {}).get('met', False)] + [c.get('met', False) for c in hard_requirements_check.get('certifications', [])])}/{2 + len(hard_requirements_check.get('certifications', []))} requirements met"
            },
            "recommendations": recommendations,
            "hard_requirements": {
                "extracted": hard_requirements_extracted,
                "check": hard_requirements_check,
                "hard_requirements_score": hard_reqs_points  # 0-20 points breakdown
            },
            "score_breakdown": {
                "sbert_component": f"{sbert_score * 0.70:.1f}% (SBert: {sbert_score:.1f}% × 0.70)",
                "skill_component": f"{skill_match_score * 0.20:.1f}% (Skills: {skill_match_score:.1f}% × 0.20)",
                "hard_req_component": f"{hard_reqs_score * 0.10:.1f}% (Hard Reqs: {hard_reqs_score:.1f}% × 0.10)",
                "final_score": f"{final_match_percentage:.1f}%"
            },
            "percentile_estimate": percentile_estimate,
            "total_existing_applicants": len(existing_applications),
            "pdf_file_path": pdf_file_path  # Include PDF path for future application submission
        }
        return preview_response
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in analyze_cv_preview: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# POST submit application endpoint
@router.post("/submit", response_model=ApplicationResponse)
def submit_application(
    application_data: ApplicationSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a job application with full analysis report"""
    if current_user.user_type != "job_seeker":
        raise HTTPException(status_code=403, detail="Only job seekers can apply")
    
    # Check if job exists
    job = db.query(Job).filter(Job.id == application_data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already applied
    existing = db.query(Application).filter(
        Application.job_id == application_data.job_id,
        Application.applicant_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")
    
    # Use NLP model to calculate match score (or use provided from analysis)
    if not application_data.analysis_report:
        nlp_service = get_model_service()
        match_result = nlp_service.calculate_match(
            resume=application_data.resume_text,
            job_description=job.description
        )
    else:
        # Use pre-analyzed results
        match_result = {
            "match_percentage": application_data.analysis_report.get("match_percentage"),
            "prediction": application_data.analysis_report.get("prediction"),
            "confidence": application_data.analysis_report.get("confidence")
        }
    
    # Create application with real NLP matching and analysis report
    new_application = Application(
        job_id=application_data.job_id,
        applicant_id=current_user.id,
        resume_text=application_data.resume_text,
        pdf_file_path=application_data.pdf_file_path,  # Store PDF path
        status="pending",
        match_percentage=match_result["match_percentage"],
        prediction=match_result["prediction"],
        confidence=match_result["confidence"],
        analysis_report=json.dumps(application_data.analysis_report) if application_data.analysis_report else None
    )
    
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    
    return new_application

# GET applications for a job (recruiter only)
@router.get("/job/{job_id}")
def get_job_applications(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all applications for a specific job (recruiter only)"""
    if current_user.user_type != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view applications")
    
    # Check if job exists and belongs to recruiter
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own job applications")
    
    applications = db.query(Application).filter(Application.job_id == job_id).all()
    
    # Serialize applications to list of dictionaries
    import json
    result = []
    for app in applications:
        app_dict = {
            "id": app.id,
            "job_id": app.job_id,
            "applicant_id": app.applicant_id,
            "resume_text": app.resume_text,
            "match_percentage": app.match_percentage,
            "prediction": app.prediction,
            "confidence": app.confidence,
            "status": app.status,
            "applied_at": app.created_at.isoformat() if hasattr(app, 'created_at') and app.created_at else None,
            "analysis_report": None
        }
        # Parse analysis_report if it exists
        if app.analysis_report:
            try:
                app_dict["analysis_report"] = json.loads(app.analysis_report)
            except:
                app_dict["analysis_report"] = None
        result.append(app_dict)
    
    return result

# GET all applications for logged in user
@router.get("/")
def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all applications for the logged in user"""
    if current_user.user_type == "job_seeker":
        # Job seeker - show their own applications
        applications = db.query(Application).filter(Application.applicant_id == current_user.id).all()
        return {
            "user_type": "job_seeker",
            "applications": applications
        }
    else:
        # Recruiter - show applications for their jobs
        jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).all()
        job_ids = [job.id for job in jobs]
        applications = db.query(Application).filter(Application.job_id.in_(job_ids)).all() if job_ids else []
        return {
            "user_type": "recruiter",
            "jobs": jobs,
            "applications": applications
        }

# PUT update application status (recruiter only)
@router.put("/{application_id}/status")
def update_application_status(
    application_id: int,
    new_status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update application status (recruiter only)"""
    if current_user.user_type != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can update application status")
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check if recruiter owns this job
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update applications for your own jobs")
    
    # Update status
    valid_statuses = ["pending", "reviewed", "rejected", "accepted"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    application.status = new_status
    db.commit()
    db.refresh(application)
    
    return {
        "message": "Application status updated",
        "application_id": application.id,
        "new_status": application.status
    }

# POST send message to applicant
@router.post("/{application_id}/messages")
def send_message(
    application_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to an applicant (recruiter only)"""
    if current_user.user_type != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can send messages")
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check if recruiter owns this job
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only message applicants for your own jobs")
    
    # Create message
    new_message = Message(
        application_id=application_id,
        sender_id=current_user.id,
        content=message_data.content
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return {
        "message_id": new_message.id,
        "sent_at": new_message.created_at,
        "content": new_message.content
    }

# GET messages for an application
@router.get("/{application_id}/messages")
def get_application_messages(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages for an application"""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check if user is recruiter or applicant
    if current_user.id != application.applicant_id:
        job = db.query(Job).filter(Job.id == application.job_id).first()
        if job.recruiter_id != current_user.id:
            raise HTTPException(status_code=403, detail="You don't have access to these messages")
    
    messages = db.query(Message).filter(Message.application_id == application_id).all()
    return {"application_id": application_id, "messages": messages}

# POST simulate skills addition
@router.post("/simulate-skills")
def simulate_skills(
    simulation_request: SkillSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Simulate adding skills to resume and see how match percentage changes
    Uses skill-based calculation instead of re-embedding entire resume
    """
    try:
        if current_user.user_type != "job_seeker":
            raise HTTPException(status_code=403, detail="Only job seekers can run simulations")
        
        # Validate job exists
        job = db.query(Job).filter(Job.id == simulation_request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Load NLP model (based on user's pro model preference)
        nlp_service = get_pro_model_service() if simulation_request.use_pro_model else get_model_service()
        
        # Use the proper simulate_impact() method which has HYBRID calculation
        # This method: uses semantic + keyword matching, NO artificial repetition, honest scores
        try:
            simulation_result = nlp_service.simulate_impact(
                resume=simulation_request.resume_text.strip(),
                job_description=(job.description or "").strip(),
                added_skills=simulation_request.added_skills,
                original_match_percentage=simulation_request.original_match_percentage
            )
            
            new_match_percentage = simulation_result['simulated_percentage']
            improvement = simulation_result['improvement']
            skill_impacts = simulation_result['skill_impacts']
            
        except Exception as e:
            print(f"Error in simulate_impact: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to calculate match: {str(e)}")
        
        # Build response from proper simulation result
        return {
            "original_match_percentage": simulation_request.original_match_percentage,
            "new_match_percentage": float(new_match_percentage),
            "improvement": float(improvement),
            "improvement_percentage": float((improvement / simulation_request.original_match_percentage * 100) if simulation_request.original_match_percentage > 0 else 0),
            "added_skills": simulation_request.added_skills,
            "skill_impacts": skill_impacts,  # Individual skill impact breakdown
            "recommendation": simulation_result.get('recommendation', ''),  # Intelligent feedback
            "new_prediction": "Match" if new_match_percentage >= 50 else "No Match"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Simulation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")
