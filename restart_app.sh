#!/bin/bash

echo "=== Restarting Flask Application ==="
echo "This script will stop the current application and restart it with the updated mail configuration."

# Find and stop the current Flask process
echo "Stopping current Flask processes..."
pkill -f "flask run" || echo "No running Flask processes found"

# Give it a moment to shut down
sleep 2

# Check if it's still running
if pgrep -f "flask run" > /dev/null; then
    echo "Forcefully killing Flask processes..."
    pkill -9 -f "flask run"
    sleep 1
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Run the mail configuration check to verify the changes
echo "Checking mail configuration before starting..."
python check_mail_config.py

# Start the Flask application
echo "Starting Flask application..."
cd /home/violation
nohup flask run --host=0.0.0.0 --port=5004 > flask.log 2>&1 &

# Give it a moment to start
sleep 3

# Check if it's running
if pgrep -f "flask run" > /dev/null; then
    echo "✅ Flask application successfully restarted on port 5004"
    echo "You can now test sending email from the admin interface"
    echo "Log files: flask.log and flask_error.log"
else
    echo "❌ Failed to start Flask application"
    echo "Check flask.log for errors"
fi

echo "Done!" 