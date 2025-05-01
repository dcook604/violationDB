#!/usr/bin/env python3
"""
Apply account lockout and Argon2id password hashing migration
"""
import os
import sys
from app import db
from sqlalchemy import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def apply_migration():
    """Apply the database migration for account lockout and Argon2id support"""
    try:
        # Read the SQL file
        with open('add_account_lockout.sql', 'r') as sql_file:
            sql_statements = sql_file.read()
        
        # Execute the SQL
        logger.info("Starting migration")
        conn = db.engine.connect()
        
        # Split and execute statements
        for statement in sql_statements.split(';'):
            if statement.strip():
                logger.info(f"Executing: {statement.strip()}")
                conn.execute(text(statement.strip()))
        
        # Commit the transaction
        conn.commit()
        conn.close()
        
        logger.info("Migration completed successfully")
        return True
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting account lockout and Argon2id password hashing migration")
    success = apply_migration()
    if success:
        logger.info("Migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Migration failed")
        sys.exit(1) 