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
        # Check database type
        with app.app_context():
            is_sqlite = 'sqlite' in db.engine.url.drivername
            
        # Read the appropriate SQL file
        sql_file_path = 'add_user_sessions_sqlite.sql' if is_sqlite else 'add_user_sessions.sql'
        
        logger.info(f"Using SQL file: {sql_file_path} for database type: {'SQLite' if is_sqlite else 'MySQL/PostgreSQL'}")
        
        try:
            with open(sql_file_path, 'r') as sql_file:
                sql_content = sql_file.read()
        except FileNotFoundError:
            logger.error(f"SQL file {sql_file_path} not found. Creating one...")
            if is_sqlite:
                # Create SQLite migration
                with open('add_user_sessions_sqlite.sql', 'w') as f:
                    f.write("""-- Add user sessions table for SQLite

-- Create user_sessions table
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token VARCHAR(64) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    user_agent VARCHAR(255),
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Add indexes
CREATE INDEX idx_user_sessions_user_active ON user_sessions(user_id, is_active);
CREATE INDEX idx_user_sessions_token ON user_sessions(token);""")
            else:
                # Create MySQL/PostgreSQL migration
                with open('add_user_sessions.sql', 'w') as f:
                    f.write("""-- Add user sessions table for session management

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
);

-- Add indexes
CREATE INDEX idx_user_sessions_user_active ON user_sessions(user_id, is_active);
CREATE INDEX idx_user_sessions_token ON user_sessions(token);""")
            
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
    logger.info("Starting user sessions migration for session management")
    success = apply_migration()
    if success:
        logger.info("Migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Migration failed")
        sys.exit(1) 