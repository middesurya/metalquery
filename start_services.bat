@echo off
REM ============================================================
REM MetalQuery - Start All Services
REM ============================================================
REM This script starts all three services in separate windows
REM Make sure you have:
REM   1. Created .env file from .env.example
REM   2. Set your GROQ_API_KEY and DB_PASSWORD
REM   3. Installed dependencies in each virtual environment
REM ============================================================

echo ============================================================
echo MetalQuery - Starting All Services
echo ============================================================

REM Start NLP Service (FastAPI on port 8003)
echo Starting NLP Service on port 8003...
start "NLP Service" cmd /k "cd /d %~dp0nlp_service && ..\venv\Scripts\activate && python main.py"

REM Wait a moment for NLP service to start
timeout /t 3 /nobreak > nul

REM Start Django Backend (port 8000)
echo Starting Django Backend on port 8000...
start "Django Backend" cmd /k "cd /d %~dp0backend && ..\venv\Scripts\activate && python manage.py runserver 0.0.0.0:8000"

REM Wait a moment for Django to start
timeout /t 3 /nobreak > nul

REM Start React Frontend (port 3000)
echo Starting React Frontend on port 3000...
start "React Frontend" cmd /k "cd /d %~dp0frontend && npm start"

echo ============================================================
echo All services starting!
echo ============================================================
echo NLP Service:     http://localhost:8003/health
echo Django Backend:  http://localhost:8000/api/chatbot/health/
echo React Frontend:  http://localhost:3000
echo ============================================================
pause
