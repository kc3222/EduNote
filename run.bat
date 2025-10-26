@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   EduNote Quick Start
echo ========================================
echo.

:: Start database
echo Starting database...
cd /d "%~dp0database"
docker-compose up -d
if errorlevel 1 (
    echo Database start failed, but continuing...
) else (
    echo Database started
)

:: Wait a moment
timeout /t 3 /nobreak >nul

:: Go back to root
cd /d "%~dp0"

echo.
echo Starting backend services...
echo    (Installing dependencies and starting services...)

:: Start Auth Service
echo    Starting Auth Service...
start "Auth Service" cmd /k "cd /d backend\auth_service && conda activate edunote && pip install -r requirements.txt --quiet && python main.py --port 8000"
timeout /t 2 /nobreak >nul

:: Start Notes Service  
echo    Starting Notes Service...
start "Notes Service" cmd /k "cd /d backend\note_service && conda activate edunote && pip install -r requirements.txt --quiet && python main.py --port 8001"
timeout /t 2 /nobreak >nul

:: Start Document Service
echo    Starting Document Service...
start "Document Service" cmd /k "cd /d backend\document_service && conda activate edunote && pip install -r requirements.txt --quiet && python main.py --port 8002"
timeout /t 3 /nobreak >nul

echo.
echo Starting frontend...

:: Install npm dependencies if needed
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo    Installing dependencies...
    npm install
)

:: Start frontend  
start "Frontend" cmd /k "npm run dev"

:: Go back to root
cd /d "%~dp0"

echo.
echo ========================================
echo EduNote is starting up!
echo.
echo Service URLs:
echo    Main App:      http://localhost:5173
echo    Auth API:      http://localhost:8000  
echo    Notes API:     http://localhost:8001
echo    Document API:  http://localhost:8002
echo.
echo Services are running in separate windows
echo    Close those windows to stop services
echo ========================================
echo.
pause
