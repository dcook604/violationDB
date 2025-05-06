#!/usr/bin/env python3
"""
Apply account lockout and Argon2id password hashing migration
"""
import os
import sys
import re
from app import create_app, db
from sqlalchemy import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create app context
app = create_app()

def apply_migration():
    """Apply the database migration for account lockout and Argon2id support"""
    try:
        sql_file_path = 'add_account_lockout.sql'
        
        logger.info(f"Using SQL file: {sql_file_path} for MariaDB database")
        
        with open(sql_file_path, 'r') as sql_file:
            sql_content = sql_file.read()
        
        # Execute the SQL
        logger.info("Starting migration")
        
        with app.app_context():
            conn = db.engine.connect()
            transaction = conn.begin()
            
            try:
                # Split SQL into individual statements, removing comments and empty lines
                # This regex matches SQL statements terminated by semicolons, ignoring semicolons in comments
                statements = []
                for statement in re.split(r';(?=[^-])', sql_content):
                    # Remove comments and empty lines
                    clean_statement = '\n'.join([line for line in statement.split('\n') 
                                              if not line.strip().startswith('--') and line.strip()])
                    if clean_statement.strip():
                        statements.append(clean_statement)
                
                # Execute each statement
                for statement in statements:
                    logger.info(f"Executing: {statement.strip()}")
                    conn.execute(text(statement.strip()))
                
                transaction.commit()
                logger.info("Transaction committed successfully")
            except Exception as e:
                transaction.rollback()
                logger.error(f"Transaction rolled back due to error: {str(e)}")
                raise e
            finally:
                conn.close()
            
        logger.info("Migration completed successfully")
        return True
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
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