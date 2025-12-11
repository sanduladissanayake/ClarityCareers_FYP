"""
Create MySQL Database and Tables
Run this once to set up the database from scratch
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.models.database import Base
import bcrypt

# MySQL connection without specifying database
MYSQL_URL = "mysql+pymysql://root:@localhost:3306"

def create_database():
    """Create the claritycareers database"""
    print("Creating MySQL database: claritycareers...")
    
    # Connect to MySQL without database specified
    engine = create_engine(MYSQL_URL)
    
    with engine.connect() as conn:
        try:
            # Create database if it doesn't exist
            conn.execute(text("CREATE DATABASE IF NOT EXISTS claritycareers"))
            conn.commit()
            print("✅ Database 'claritycareers' created successfully!")
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            raise

def create_tables():
    """Create all tables in the database"""
    print("\nCreating tables...")
    
    from app.db import engine
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")

def seed_sample_data():
    """Add sample data for testing"""
    print("\nSeeding sample data...")
    
    from app.db import SessionLocal
    from app.models.database import User, Job
    
    db = SessionLocal()
    try:
        # Check if sample data already exists
        existing_user = db.query(User).filter_by(username="recruiter_demo").first()
        if existing_user:
            print("⚠️  Sample data already exists. Skipping...")
            return
        
        def hash_password(password: str) -> str:
            """Hash password using bcrypt"""
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
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
        
        # Create sample job
        job = Job(
            title="Senior Python Developer",
            company="TechCorp Inc.",
            location="San Francisco, CA",
            description="We are seeking an experienced Python Developer to join our growing team.",
            requirements="5+ years of Python experience required",
            job_type="Full-time",
            salary_range="$120,000 - $160,000",
            recruiter_id=recruiter.id,
            is_active=True
        )
        db.add(job)
        db.commit()
        print(f"✅ Created sample job: {job.title}")
        
        print("\n" + "="*60)
        print("Sample accounts created:")
        print("="*60)
        print("Recruiter Account:")
        print("  Email: recruiter@example.com")
        print("  Username: recruiter_demo")
        print("  Password: pass123")
        print("\nJob Seeker Account:")
        print("  Email: jobseeker@example.com")
        print("  Username: jobseeker_demo")
        print("  Password: pass123")
        print("="*60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("DATABASE SETUP: Create Database and Tables")
    print("="*60)
    
    try:
        # Step 1: Create database
        create_database()
        
        # Step 2: Create tables
        create_tables()
        
        # Step 3: Seed sample data
        seed_sample_data()
        
        print("\n✅ Database setup complete!")
        print("\nNext step: Start the backend server")
        print("cd backend")
        print("python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
