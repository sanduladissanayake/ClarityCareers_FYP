"""
Database Initialization Script
Creates all tables and optionally seeds sample data
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.db import engine, SessionLocal
from app.models.database import Base, User, Job
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt directly"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def seed_sample_data():
    """Add sample data for testing"""
    print("\nSeeding sample data...")
    
    db = SessionLocal()
    try:
        # Create sample recruiter
        recruiter = User(
            email="recruiter@example.com",
            username="recruiter_demo",
            hashed_password=hash_password("pass123"),
            full_name="Demo Recruiter",
            user_type="recruiter"
        )
        db.add(recruiter)
        db.commit()
        db.refresh(recruiter)
        print(f"✅ Created recruiter: {recruiter.username}")
        
        # Create sample job seeker
        job_seeker = User(
            email="jobseeker@example.com",
            username="jobseeker_demo",
            hashed_password=hash_password("pass123"),
            full_name="Demo Job Seeker",
            user_type="job_seeker"
        )
        db.add(job_seeker)
        db.commit()
        print(f"✅ Created job seeker: {job_seeker.username}")
        
        # Create sample jobs
        jobs = [
            Job(
                title="Senior Python Developer",
                company="TechCorp Inc.",
                location="San Francisco, CA",
                description="""We are seeking an experienced Python Developer to join our growing team.
                
Key Responsibilities:
- Design and implement scalable backend systems
- Write clean, maintainable code following best practices
- Collaborate with cross-functional teams
- Mentor junior developers

Required Skills:
- 5+ years of Python development experience
- Strong knowledge of Django/FastAPI frameworks
- Experience with PostgreSQL and Redis
- Understanding of microservices architecture
- Excellent problem-solving skills""",
                requirements="""Must Have:
- Bachelor's degree in Computer Science or equivalent
- 5+ years professional Python experience
- Strong understanding of OOP principles
- Experience with RESTful API design
- Proficiency in Git and CI/CD pipelines

Nice to Have:
- Experience with Docker and Kubernetes
- Knowledge of machine learning libraries
- AWS/Azure cloud experience
- Open source contributions""",
                job_type="Full-time",
                salary_range="$120,000 - $160,000",
                recruiter_id=recruiter.id,
                is_active=True
            ),
            Job(
                title="Machine Learning Engineer",
                company="AI Solutions Ltd.",
                location="Remote",
                description="""Join our innovative ML team building cutting-edge AI solutions.

We're looking for a passionate ML engineer to develop and deploy machine learning models.

What You'll Do:
- Build and train ML models using TensorFlow/PyTorch
- Deploy models to production environments
- Optimize model performance and accuracy
- Research and implement state-of-the-art algorithms""",
                requirements="""Required:
- Master's degree in CS, Statistics, or related field
- 3+ years of ML engineering experience
- Strong Python and deep learning frameworks
- Experience with NLP and computer vision
- Understanding of MLOps practices

Preferred:
- PhD in Machine Learning or AI
- Publications in top-tier conferences
- Experience with large-scale distributed training
- Knowledge of reinforcement learning""",
                job_type="Full-time",
                salary_range="$140,000 - $180,000",
                recruiter_id=recruiter.id,
                is_active=True
            ),
            Job(
                title="Full Stack Developer",
                company="StartupXYZ",
                location="New York, NY",
                description="""Fast-growing startup seeking a versatile full stack developer.

You'll work on:
- Frontend development with React/Vue
- Backend APIs with Node.js/Python
- Database design and optimization
- DevOps and deployment automation

Perfect for someone who loves wearing multiple hats and building products from scratch.""",
                requirements="""Must Have:
- 3+ years full stack development experience
- Proficiency in JavaScript/TypeScript
- Experience with modern frontend frameworks
- Backend development with Node.js or Python
- SQL and NoSQL databases

Bonus Points:
- Startup experience
- Mobile development (React Native)
- GraphQL experience
- UI/UX design skills""",
                job_type="Full-time",
                salary_range="$100,000 - $140,000",
                recruiter_id=recruiter.id,
                is_active=True
            ),
            Job(
                title="Data Scientist",
                company="DataDriven Analytics",
                location="Boston, MA",
                description="""We're hiring a Data Scientist to extract insights from complex datasets.

Responsibilities:
- Perform exploratory data analysis
- Build predictive models
- Create data visualizations and dashboards
- Communicate findings to stakeholders
- Collaborate with engineering teams on model deployment""",
                requirements="""Required Skills:
- Strong statistical analysis background
- Python (pandas, scikit-learn, matplotlib)
- SQL and data warehousing
- Experience with A/B testing
- Machine learning fundamentals

Preferred:
- Experience with big data tools (Spark, Hadoop)
- Knowledge of causal inference
- Business intelligence tools (Tableau, PowerBI)
- Domain expertise in finance or healthcare""",
                job_type="Full-time",
                salary_range="$110,000 - $150,000",
                recruiter_id=recruiter.id,
                is_active=True
            ),
            Job(
                title="Junior Software Engineer",
                company="GrowthTech",
                location="Austin, TX",
                description="""Great opportunity for new graduates or early-career developers.

What We Offer:
- Mentorship from senior engineers
- Training and skill development
- Work on real production systems
- Collaborative team environment
- Career growth opportunities

You'll Learn:
- Software development best practices
- Agile methodologies
- Code review and testing
- Production deployment""",
                requirements="""Looking For:
- Bachelor's degree in Computer Science or related field
- Strong foundation in programming (any language)
- Understanding of data structures and algorithms
- Eagerness to learn and grow
- Good communication skills

Preferred:
- Internship or project experience
- Knowledge of web development
- Familiarity with Git
- Passion for technology""",
                job_type="Full-time",
                salary_range="$70,000 - $90,000",
                recruiter_id=recruiter.id,
                is_active=True
            )
        ]
        
        for job in jobs:
            db.add(job)
        db.commit()
        print(f"✅ Created {len(jobs)} sample jobs")
        
        print("\n" + "="*60)
        print("Sample accounts created:")
        print("="*60)
        print("Recruiter Account:")
        print("  Email: recruiter@example.com")
        print("  Username: recruiter_demo")
        print("  Password: password123")
        print("")
        print("Job Seeker Account:")
        print("  Email: jobseeker@example.com")
        print("  Username: jobseeker_demo")
        print("  Password: password123")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("ClarityCareers Database Initialization")
    print("="*60)
    
    # Initialize database
    init_database()
    
    # Ask if user wants to seed data
    response = input("\nDo you want to seed sample data? (yes/no): ").lower()
    if response in ['yes', 'y']:
        seed_sample_data()
    
    print("\n✅ Database initialization complete!")
    print("\nNext steps:")
    print("1. Start the backend server: uvicorn main:app --reload")
    print("2. Open frontend/index.html in your browser")
    print("3. Login with sample accounts:")
    print("   - Job Seeker: jobseeker_demo / pass123")
    print("   - Recruiter: recruiter_demo / pass123")
