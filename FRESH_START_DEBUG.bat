@echo off
REM =============================================================================
REM FRESH START - DEBUG VERSION
REM Shows each step clearly so you can see what's happening
REM =============================================================================

echo.
echo ========================================
echo FRESH START - DEBUG MODE
echo ========================================
echo.

REM Check if virtual environment exists
if exist "%~dp0.venv\Scripts\activate.bat" (
    echo ✓ Virtual environment found
) else (
    echo ✗ ERROR: Virtual environment NOT found
    echo  Please run: python -m venv .venv
    pause
    exit /b 1
)

echo.
echo Step 1: Killing existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Killed existing Python processes
) else (
    echo ℹ No existing Python processes to kill
)
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Clearing Python cache...
powershell -Command "Get-ChildItem -Path '%~dp0' -Filter '__pycache__' -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
echo ✓ Cache cleared

echo.
echo Step 3: Starting Backend Server...
echo.
echo ** WAIT FOR MESSAGE: 'API READY - Server running!' **
echo ** This window will stay open - DO NOT CLOSE IT **
echo.
cd /d "%~dp0backend"
call "%~dp0.venv\Scripts\activate.bat"
echo.
echo Loading with FIXED CODE:
echo - _is_valid_atomic_skill filtering fake skills
echo - recruiter_alert showing hard requirements
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
