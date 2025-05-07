import sentry_sdk
from flask import current_app, request
from flask_jwt_extended import get_jwt_identity, get_jwt
import logging
import functools

logger = logging.getLogger(__name__)

def set_sentry_user():
    """Set user information for Sentry based on JWT token"""
    try:
        # Check if JWT identity exists
        user_id = get_jwt_identity()
        if not user_id:
            return
            
        # Get claims from JWT
        claims = get_jwt()
        
        # Set user data in Sentry
        sentry_sdk.set_user({
            'id': user_id,
            'email': claims.get('email'),
            'role': claims.get('role', 'user'),
            'admin': claims.get('is_admin', False),
            'ip_address': request.remote_addr
        })
    except Exception as e:
        logger.warning(f"Failed to set Sentry user context: {str(e)}")

def add_sentry_context(name, data):
    """Add additional context data to Sentry
    
    Args:
        name: Context name
        data: Context data (dict)
    """
    try:
        sentry_sdk.set_context(name, data)
    except Exception as e:
        logger.warning(f"Failed to add Sentry context: {str(e)}")

def add_sentry_tag(key, value):
    """Add a tag to Sentry events
    
    Args:
        key: Tag key
        value: Tag value
    """
    try:
        sentry_sdk.set_tag(key, value)
    except Exception as e:
        logger.warning(f"Failed to add Sentry tag: {str(e)}")

def capture_exception(exception, **kwargs):
    """Capture an exception with additional context
    
    Args:
        exception: Exception to capture
        **kwargs: Additional context data
    """
    try:
        # Add any additional context
        for key, value in kwargs.items():
            add_sentry_context(key, value)
            
        # Capture the exception
        sentry_sdk.capture_exception(exception)
    except Exception as e:
        logger.warning(f"Failed to capture exception in Sentry: {str(e)}")

def capture_message(message, level='info', **kwargs):
    """Capture a message with additional context
    
    Args:
        message: Message to capture
        level: Error level (info, warning, error)
        **kwargs: Additional context data
    """
    try:
        # Add any additional context
        for key, value in kwargs.items():
            add_sentry_context(key, value)
            
        # Capture the message
        sentry_sdk.capture_message(message, level=level)
    except Exception as e:
        logger.warning(f"Failed to capture message in Sentry: {str(e)}")

def with_sentry_transaction(name=None, operation=None):
    """Decorator to create a Sentry transaction for function execution
    
    Args:
        name: Transaction name (defaults to function name)
        operation: Operation type
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Set the function name as the transaction name if not provided
            transaction_name = name or f"{func.__module__}.{func.__name__}"
            
            try:
                # Set transaction name as a tag instead of trying to use transactions API
                sentry_sdk.set_tag("transaction", transaction_name)
                
                # Add the operation type as a tag if provided
                if operation:
                    sentry_sdk.set_tag("operation", operation)
                
                # Execute the function
                return func(*args, **kwargs)
            except Exception as e:
                # Capture the exception with transaction info
                sentry_sdk.set_tag("error", "true")
                sentry_sdk.capture_exception(e)
                raise
                
        return wrapper
    return decorator 