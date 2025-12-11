"""
Database Migration: Add analysis_report column to applications table
Run this script to update your existing database
"""
import sys
sys.path.append('..')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Replace mysql:// with mysql+pymysql:// for compatibility
if DATABASE_URL.startswith('mysql://'):
    DATABASE_URL = DATABASE_URL.replace('mysql://', 'mysql+pymysql://')

def migrate():
    """Add analysis_report column to applications table"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Add analysis_report column (JSON type)
            print("Adding analysis_report column to applications table...")
            conn.execute(text("""
                ALTER TABLE applications 
                ADD COLUMN analysis_report JSON DEFAULT NULL
            """))
            conn.commit()
            print("✅ Migration completed successfully!")
            print("   - Added 'analysis_report' column to 'applications' table")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠️  Column 'analysis_report' already exists. Skipping...")
            else:
                print(f"❌ Migration failed: {e}")
                raise

if __name__ == "__main__":
    print("="*60)
    print("DATABASE MIGRATION: Add analysis_report column")
    print("="*60)
    migrate()
    print("\n✅ Database is up to date!")
