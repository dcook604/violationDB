#!/usr/bin/env python3
"""
Check Database Connectivity Script

This script:
1. Attempts to connect to the MariaDB database
2. Verifies SQLAlchemy can communicate with the database
3. Checks if the necessary tables exist

Usage:
python check_db.py
"""

from app import create_app, db
from sqlalchemy import inspect
import sys

def check_database_connection():
    """Check database connection and print status"""
    app = create_app()
    
    try:
        with app.app_context():
            # Get database dialect
            dialect = db.engine.dialect.name
            print(f"Connected to database. Dialect: {dialect}")
            
            # Check if connection is working
            result = db.session.execute(db.text("SELECT 1")).scalar()
            print(f"Database query test: {result}")
            
            # Get list of tables using Inspector
            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()
            print(f"Tables in database: {len(table_names)}")
            for table in table_names:
                print(f"  - {table}")
                
            # Check alembic version
            version = db.session.execute(db.text("SELECT version_num FROM alembic_version")).scalar()
            print(f"Alembic version: {version}")
            
            print("\nDatabase connection test successful!")
            return True
    except Exception as e:
        print(f"Error connecting to database: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = check_database_connection()
    sys.exit(0 if success else 1) 