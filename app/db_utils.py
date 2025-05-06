"""
Database Utilities Module

This module provides utility functions for database operations with robust error handling.
It helps ensure database connections are properly managed and errors are handled gracefully.
"""

import logging
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DisconnectionError, DatabaseError
from pymysql.err import MySQLError, OperationalError as PyMySQLOperationalError
from flask import current_app
from . import db

logger = logging.getLogger(__name__)

def handle_db_errors(f):
    """
    Decorator to handle database errors in model methods.
    Provides consistent error handling for database operations.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except OperationalError as e:
            # Connection issues, server gone, etc.
            logger.error(f"Database operational error: {str(e)}")
            # Check if connection lost and try to reconnect
            if "Lost connection" in str(e) or "server has gone away" in str(e):
                try:
                    db.session.rollback()
                    # Attempt the operation once more
                    return f(*args, **kwargs)
                except Exception as retry_error:
                    logger.error(f"Failed reconnection attempt: {str(retry_error)}")
                    raise DatabaseConnectionError("Database connection lost and reconnection failed")
            raise DatabaseConnectionError(f"Database operational error: {str(e)}")
        
        except DisconnectionError as e:
            # Explicitly disconnected
            logger.error(f"Database disconnection error: {str(e)}")
            db.session.rollback()
            raise DatabaseConnectionError(f"Database disconnection: {str(e)}")
            
        except (MySQLError, PyMySQLOperationalError) as e:
            # Driver-specific errors
            logger.error(f"MySQL error: {str(e)}")
            db.session.rollback()
            raise DatabaseConnectionError(f"MySQL error: {str(e)}")
            
        except SQLAlchemyError as e:
            # More general SQLAlchemy errors
            logger.error(f"Database error: {str(e)}")
            db.session.rollback()
            raise DatabaseError(f"Database error: {str(e)}")
            
        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error during database operation: {str(e)}")
            db.session.rollback()
            raise
    
    return decorated_function


class DatabaseConnectionError(Exception):
    """Exception raised for database connection errors"""
    pass


def safe_commit():
    """
    Safely commit changes to the database with error handling.
    
    Returns:
        bool: True if commit was successful, False otherwise
    """
    try:
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error committing to database: {str(e)}")
        return False
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error during commit: {str(e)}")
        return False


def with_transaction(f):
    """
    Decorator to handle database transactions.
    Commits on success, rolls back on error.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            logger.error(f"Transaction error: {str(e)}")
            raise
    
    return decorated_function


def check_database_connection():
    """
    Check if database connection is alive.
    
    Returns:
        bool: True if connection is alive, False otherwise
    """
    try:
        # Execute a simple query to check connection
        db.session.execute(db.text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False 