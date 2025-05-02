#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine, Column, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment or use default
db_url = os.environ.get('DATABASE_URL', 'mariadb://violationuser:viopass@127.0.0.1:3306/violationdb')

# Create SQLAlchemy engine and session
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Check if the columns already exist
def check_columns():
    try:
        # Simple query to check if columns exist
        result = session.execute(text("SHOW COLUMNS FROM violations LIKE 'html_path'"))
        html_exists = result.rowcount > 0
        
        result = session.execute(text("SHOW COLUMNS FROM violations LIKE 'pdf_path'"))
        pdf_exists = result.rowcount > 0
        
        return html_exists and pdf_exists
    except Exception as e:
        print(f"Error checking columns: {e}")
        return False

# Add the columns if they don't exist
def add_columns():
    try:
        if not check_columns():
            print("Adding html_path and pdf_path columns to violations table...")
            session.execute(text("ALTER TABLE violations ADD COLUMN html_path VARCHAR(255)"))
            session.execute(text("ALTER TABLE violations ADD COLUMN pdf_path VARCHAR(255)"))
            session.commit()
            print("Columns added successfully.")
        else:
            print("Columns already exist. No changes needed.")
    except Exception as e:
        session.rollback()
        print(f"Error adding columns: {e}")

if __name__ == "__main__":
    add_columns()
    session.close() 