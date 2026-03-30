@echo off
cd /d "%~dp0"
echo ========================================
echo Starting ClarityCareers Backend Server
echo ========================================
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat
echo.
echo Checking dependencies...
pip install email-validator > nul 2>&1
echo Dependencies installed!
echo.
echo Starting server...
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
