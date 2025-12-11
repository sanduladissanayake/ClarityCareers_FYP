"""
Database Models for ClarityCareers
SQLAlchemy ORM models for User, Job, Application, and Message
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class User(Base):
    """User model for both recruiters and job seekers"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    user_type = Column(String(50))  # "job_seeker" or "recruiter"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    jobs = relationship("Job", back_populates="recruiter")
    applications = relationship("Application", back_populates="applicant")
    messages = relationship("Message", back_populates="sender")

class Job(Base):
    """Job posting model"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    company = Column(String(255))
    location = Column(String(255))
    description = Column(Text)
    requirements = Column(Text, nullable=True)
    job_type = Column(String(50), default="Full-time")
    salary_range = Column(String(255), nullable=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    recruiter = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job")

class Application(Base):
    """Job application model"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    applicant_id = Column(Integer, ForeignKey("users.id"))
    resume_text = Column(Text, nullable=True)
    pdf_file_path = Column(String(500), nullable=True)  # Path to stored PDF file
    match_percentage = Column(Float, default=0.0)
    prediction = Column(String(50), default="pending")  # "good_fit", "potential", "poor_fit"
    confidence = Column(String(50), default="medium")  # "high", "medium", "low"
    status = Column(String(50), default="pending")  # "pending", "reviewed", "rejected", "accepted"
    analysis_report = Column(Text, nullable=True)  # JSON string with detailed analysis
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    applicant = relationship("User", back_populates="applications")
    messages = relationship("Message", back_populates="application")

class Message(Base):
    """Message model for recruiter-applicant communication"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("Application", back_populates="messages")
    sender = relationship("User", back_populates="messages")
