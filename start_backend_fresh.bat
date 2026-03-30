@echo off
REM =============================================================================
REM CLARITYCAREERS - FORCE FRESH START (with cache clearing)
REM =============================================================================
echo.
echo Killing any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo Clearing Python cache...
powershell -Command "Get-ChildItem -Path '%~dp0' -Filter '__pycache__' -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue; Get-ChildItem -Path '%~dp0' -Filter '*.pyc' -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue"
timeout /t 2 /nobreak >nul
echo Cache cleared!

echo.
echo ========================================
echo Starting Backend Server (FRESH)
echo ========================================
echo.
cd /d "%~dp0"
call .venv\Scripts\activate.bat
cd backend
echo.
echo ** LOADING FIXED CODE **
echo ** Should show: _is_valid_atomic_skill filtering fake skills **
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
