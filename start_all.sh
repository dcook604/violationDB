#!/bin/bash

# Kill anything on 5004 (backend) and 3001 (frontend)
fuser -k 5004/tcp
fuser -k 3001/tcp

# Start backend
source .venv/bin/activate
python run.py &

# Start frontend
cd frontend
npm start > react.log 2>&1 &
cd ..

echo "Backend running on http://localhost:5004"
echo "Frontend running on http://localhost:3001" 
