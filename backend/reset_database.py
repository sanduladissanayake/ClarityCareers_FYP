"""
Database Reset Script
Run this to fix MySQL error 1932 (InnoDB tablespace mismatch after manual file copy).
This drops the corrupted database and recreates it with all tables fresh.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import pymysql
from sqlalchemy import create_engine, text
from app.models.database import Base

MYSQL_ROOT_URL = "mysql+pymysql://root:@localhost:3306"
DB_NAME = "claritycareers"
DATABASE_URL = f"mysql+pymysql://root:@localhost:3306/{DB_NAME}"


def reset_database():
    print("=" * 60)
    print("  ClarityCareers Database Reset")
    print("=" * 60)
    print("\nThis will DROP and RECREATE the database to fix error 1932.")

    engine = create_engine(MYSQL_ROOT_URL)
    try:
        with engine.connect() as conn:
            print(f"\nDropping database '{DB_NAME}' if it exists...")
            conn.execute(text(f"DROP DATABASE IF EXISTS `{DB_NAME}`"))
            conn.commit()
            print(f"  Dropped '{DB_NAME}'.")

            print(f"Creating fresh database '{DB_NAME}'...")
            conn.execute(text(f"CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
            print(f"  Created '{DB_NAME}'.")
    except Exception as e:
        print(f"\nERROR connecting to MySQL: {e}")
        print("\nMake sure XAMPP MySQL is running (port 3306).")
        sys.exit(1)
    finally:
        engine.dispose()

    print("\nCreating all tables...")
    db_engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )
    try:
        Base.metadata.create_all(bind=db_engine)
        print("  All tables created successfully!")
    except Exception as e:
        print(f"\nERROR creating tables: {e}")
        sys.exit(1)
    finally:
        db_engine.dispose()

    print("\n" + "=" * 60)
    print("  Database reset complete! You can now start the backend.")
    print("=" * 60)


if __name__ == "__main__":
    reset_database()
