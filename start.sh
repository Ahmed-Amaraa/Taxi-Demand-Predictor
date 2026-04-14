#!/bin/bash

# Script de démarrage pour l'application Taxi Demand Prediction

echo ""
echo "============================================================"
echo "  Taxi Demand Prediction - Application Launcher"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    exit 1
fi

echo "[1/4] Checking environment..."
echo "  - Python: OK"
echo "  - Node.js: OK"
echo ""

# Install backend dependencies
echo "[2/4] Installing backend dependencies..."
cd src/api
pip install -r requirements.txt > /dev/null 2>&1
echo "  - Requirements installed: OK"
cd ../..
echo ""

# Install frontend dependencies
echo "[3/4] Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "  - Installing npm packages..."
    npm install > /dev/null 2>&1
fi
echo "  - Dependencies ready: OK"
cd ..
echo ""

echo "[4/4] Starting application..."
echo ""
echo "============================================================"
echo "  Services starting..."
echo "============================================================"
echo ""
echo "  API will be available at: http://localhost:8000"
echo "  Frontend will be available at: http://localhost:3000"
echo "  API Docs at: http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all services"
echo ""
echo "============================================================"
echo ""

# Start backend
cd src/api
python main.py &
API_PID=$!
cd ../..

# Wait for API to start
sleep 3

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait $API_PID $FRONTEND_PID
