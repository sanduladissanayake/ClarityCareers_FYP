"""
Database connection and session management
"""
# Handle both MySQL and SQLite
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:@localhost:3306/claritycareers"
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# Create engine with proper SQLite configuration
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Use PyMySQL for MySQL
    import pymysql
    pymysql.install_as_MySQLdb()
    
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency for FastAPI routes
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Context manager for database sessions
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """
    Initialize database and tables
    Creates the database if it doesn't exist, then creates all tables
    """
    from app.models.database import Base
    
    # Step 1: Create the database if it doesn't exist
    try:
        # Connect to MySQL server without specifying a database
        import pymysql
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            port=3306
        )
        cursor = connection.cursor()
        
        # Create the database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS claritycareers CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        connection.commit()
        cursor.close()
        connection.close()
        print("✓ Database 'claritycareers' ready")
    except Exception as e:
        print(f"⚠ Database creation warning: {e}")
        # Continue anyway, maybe the database already exists
    
    # Step 2: Create all tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully!")
    except Exception as e:
        print(f"⚠ Table creation warning: {e}")
        # Continue - tables might already exist
