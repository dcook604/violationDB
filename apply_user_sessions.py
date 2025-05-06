#!/usr/bin/env python3
"""
Apply user sessions migration for session management
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
    """Apply the database migration for user session management"""
    try:
        sql_file_path = 'add_user_sessions.sql'
        
        logger.info(f"Using SQL file: {sql_file_path} for MariaDB database")
        
        try:
            with open(sql_file_path, 'r') as sql_file:
                sql_content = sql_file.read()
        except FileNotFoundError:
            logger.error(f"SQL file {sql_file_path} not found. Creating one...")
            
            # Create MariaDB migration file with proper engine and collation settings
            with open('add_user_sessions.sql', 'w') as f:
                f.write("""-- Add user sessions table for session management in MariaDB

-- Create user_sessions table
CREATE TABLE user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    user_agent VARCHAR(255),
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add indexes for performance optimization
CREATE INDEX idx_user_sessions_user_active ON user_sessions(user_id, is_active);
CREATE INDEX idx_user_sessions_token ON user_sessions(token);
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);""")
            
            # Read the newly created file
            with open(sql_file_path, 'r') as sql_file:
                sql_content = sql_file.read()
        
        # Execute the SQL
        logger.info("Starting migration")
        
        with app.app_context():
            conn = db.engine.connect()
            transaction = conn.begin()
            
            try:
                # Split SQL into individual statements, removing comments and empty lines
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
    logger.info("Starting user sessions migration for session management")
    success = apply_migration()
    if success:
        logger.info("Migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Migration failed")
        sys.exit(1) 