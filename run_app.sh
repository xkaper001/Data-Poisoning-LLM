#!/bin/bash

echo "Starting LLM Data Poisoning Demo App..."
echo "--------------------------------------"

# Start the Flask backend server
echo "Starting Flask backend server..."
cd /workspaces/Data-Poisoning-LLM/backend
python run.py &
BACKEND_PID=$!
echo "Backend started with PID $BACKEND_PID"

# Wait for backend to initialize
echo "Waiting for backend to initialize..."
sleep 5

# Start the Flutter frontend
echo "Starting Flutter frontend..."
cd /workspaces/Data-Poisoning-LLM/frontend
flutter run -d web &
FRONTEND_PID=$!
echo "Frontend started with PID $FRONTEND_PID"

# Function to handle script termination
cleanup() {
  echo "Shutting down servers..."
  kill $BACKEND_PID $FRONTEND_PID
  exit 0
}

# Set up signal trapping
trap cleanup INT TERM

echo ""
echo "Both services started. Press Ctrl+C to stop both servers."
echo "--------------------------------------"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:8080"
echo "--------------------------------------"

# Wait for user to terminate
wait