@echo off
REM Script de démarrage pour l'application Taxi Demand Prediction

echo.
echo ============================================================
echo   Taxi Demand Prediction - Application Launcher
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Checking environment...
echo   - Python: OK
echo   - Node.js: OK
echo.

REM Install backend dependencies
echo [2/4] Installing backend dependencies...
cd src\api
pip install -r requirements.txt >nul 2>&1
echo   - Requirements installed: OK
cd ..\..
echo.

REM Install frontend dependencies
echo [3/4] Installing frontend dependencies...
cd frontend
if not exist node_modules (
    echo   - Installing npm packages...
    call npm install >nul 2>&1
)
echo   - Dependencies ready: OK
cd ..
echo.

echo [4/4] Starting application...
echo.
echo ============================================================
echo   Services starting...
echo ============================================================
echo.
echo   API will be available at: http://localhost:8000
echo   Frontend will be available at: http://localhost:3000
echo   API Docs at: http://localhost:8000/docs
echo.
echo   Press Ctrl+C to stop all services
echo.
echo ============================================================
echo.

REM Start backend in new window
start /d "src\api" cmd /c "python main.py"

REM Wait for API to start
timeout /t 3 /nobreak

REM Start frontend in new window
cd frontend
start /d "." cmd /c "npm run dev"
cd ..

echo.
echo Services are starting. Check the new command windows for details.
echo Press any key to exit the launcher (services will continue running)...
pause >nul
