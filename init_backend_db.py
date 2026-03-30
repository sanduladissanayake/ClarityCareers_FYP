#!/usr/bin/env python
"""
Initialize ClarityCareers backend database with proper error handling
Run this ONCE before starting the backend server
"""
import sys
import time
import pymysql

def init_database():
    """Initialize the MySQL database for ClarityCareers"""
    
    print("=" * 80)
    print("CLARITYCAREERS DATABASE INITIALIZATION")
    print("=" * 80)
    
    # Step 1: Connect to MySQL server
    print("\n[1/4] Connecting to MySQL server...")
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                port=3306,
                connect_timeout=5
            )
            print("✓ Connected to MySQL")
            break
        except pymysql.Error as e:
            if attempt < max_retries - 1:
                print(f"  Attempt {attempt + 1}/{max_retries} failed, retrying in 2 seconds...")
                time.sleep(2)
            else:
                print(f"✗ Failed to connect to MySQL after {max_retries} attempts")
                print(f"  Error: {e}")
                print("\nMake sure:")
                print("  - XAMPP MySQL is running (check XAMPP Control Panel)")
                print("  - MySQL is listening on localhost:3306")
                sys.exit(1)
    
    try:
        cursor = conn.cursor()
        
        # Step 2: Create database if it doesn't exist
        print("\n[2/4] Creating/checking claritycareers database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS claritycareers CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        print("✓ Database ready: claritycareers")
        
        # Step 3: Select the database
        print("\n[3/4] Initializing database schema...")
        cursor.execute("USE claritycareers")
        conn.commit()
        
        # Step 4: Create tables using SQLAlchemy models
        print("  Creating tables with SQLAlchemy...")
        
        # Import after ensuring database exists
        from app.models.database import Base
        from sqlalchemy import create_engine
        
        DATABASE_URL = "mysql+pymysql://root:@localhost:3306/claritycareers"
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database schema initialized")
        
        # Step 5: Verify tables
        print("\n[4/4] Verifying database tables...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print(f"✓ Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("⚠ No tables found (will be created on first API call)")
        
        # Verify user accounts
        print("\n" + "=" * 80)
        print("DATABASE INITIALIZATION COMPLETE")
        print("=" * 80)
        print("\nMySQL Status:")
        print(f"  Host: localhost")
        print(f"  Port: 3306")
        print(f"  Database: claritycareers")
        print(f"  User: root")
        print(f"  Tables: {len(tables)}")
        print("\nYou can now start the backend server with:")
        print("  python -m uvicorn app.main:app --reload")
        print("=" * 80)
        
        conn.close()
        return True
        
    except pymysql.Error as e:
        print(f"✗ Database error: {e}")
        conn.close()
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        if conn:
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    init_database()
