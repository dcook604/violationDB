#!/bin/bash

echo "===== STOPPING PROCESSES ====="
# Kill backend and frontend processes
echo "Stopping backend on port 5004..."
fuser -k 5004/tcp || echo "No process on port 5004"
echo "Stopping frontend on port 3001..."
fuser -k 3001/tcp || echo "No process on port 3001"

echo "===== CLEARING OLD PROCESSES ====="
# Find and kill any stray Python processes running our app
pkill -f "python run.py" || echo "No Python processes running run.py"
# Find and kill any stray npm/node processes for our frontend
pkill -f "react-scripts start" || echo "No React processes running"

echo "===== CHECKING PORT STATUS ====="
# Double check ports are free
if lsof -i:5004 > /dev/null || lsof -i:3001 > /dev/null; then
  echo "ERROR: Ports still in use. Please close all processes manually."
  lsof -i:5004
  lsof -i:3001
  exit 1
fi

echo "===== STARTING SERVERS ====="
# Start backend server
echo "Starting backend on port 5004..."
source .venv/bin/activate
python run.py > flask.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to start
sleep 2
echo "Checking backend..."
if curl -s "http://localhost:5004/api/auth/session" > /dev/null; then
  echo "Backend is running!"
else
  echo "WARNING: Backend may not be running correctly. Check flask.log for errors."
  tail -n 20 flask.log
fi

# Start frontend server
echo "Starting frontend on port 3001..."
cd frontend
npm start > react.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo "===== SETUP COMPLETE ====="
echo "Backend running on http://localhost:5004"
echo "Frontend running on http://localhost:3001"
echo "Backend logs: flask.log"
echo "Frontend logs: frontend/react.log"
echo ""
echo "To test backend, go to: http://localhost:5004/api/auth/session"
echo "To test frontend, go to: http://localhost:3001" 