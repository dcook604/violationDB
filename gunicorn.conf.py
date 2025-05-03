# Gunicorn configuration file
import multiprocessing
import os

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'  # or 'gevent' if you install and need async workers

# Socket Binding
# Use a Unix socket for communication with Nginx
# The path should be adjusted based on your deployment structure
# Ensure the directory exists and the user running Gunicorn has write permissions
socket_path = os.environ.get('GUNICORN_SOCKET_PATH', '/run/violation/gunicorn.sock')
bind = f'unix:{socket_path}'
# Alternatively, bind to a TCP port (less common when using Nginx on the same host):
# bind = '127.0.0.1:8000' 

# Permissions for Unix socket
umask = 0o007 # Allows group access, set to 0o000 if Nginx user is in the same group

# Logging
# Log to stdout/stderr so systemd can capture it
accesslog = '-' 
errorlog = '-'
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# Process Naming
proc_name = 'violation-app'

# Application Loading
# Assumes you have a run.py with `app = create_app()` or similar
# Or directly reference the factory: 'app:create_app()' if using FLASK_ENV
# Check your run.py or wsgi.py file
# If you have a wsgi.py like: `from app import create_app; application = create_app()`, use 'wsgi:application'
# If using run.py: `from app import create_app; app = create_app(os.getenv('FLASK_ENV'))`, use 'run:app'
# Let's assume run:app for now
# Ensure FLASK_APP points to this if using flask commands
# pythonpath = '/path/to/your/project' # Add if needed

# Environment variables for the app factory
raw_env = [
    f"FLASK_ENV={os.environ.get('FLASK_ENV', 'production')}",
    # Add other environment variables Gunicorn should pass to Flask if needed
    # e.g., f"SECRET_KEY={os.environ.get('SECRET_KEY')}" - although systemd is better for secrets
]

# Other settings
keepalive = 5
timeout = 120 # Increase if you have long-running requests 