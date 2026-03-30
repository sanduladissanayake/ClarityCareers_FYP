@echo off
REM =============================================================================
REM CLARITYCAREERS - COMPLETE FRESH RESTART
REM Kills all processes, clears cache, and starts fresh with new fixes
REM =============================================================================

echo.
echo ========================================
echo CLARITYCAREERS - FRESH START
echo ========================================
echo.
echo Step 1: Killing all existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cmd.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo ✓ Processes killed

echo.
echo Step 2: Clearing Python cache (__pycache__ and .pyc files)...
powershell -Command "Get-ChildItem -Path '%~dp0' -Filter '__pycache__' -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue; Get-ChildItem -Path '%~dp0' -Filter '*.pyc' -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue"
timeout /t 2 /nobreak >nul
echo ✓ Cache cleared

echo.
echo Step 3: Starting backend with FIXED CODE...
echo.
start "" cmd /k "%~dp0start_backend_fresh.bat"

echo.
echo Waiting 20 seconds for backend to start...
timeout /t 20 /nobreak >nul

echo.
echo Step 4: Starting frontend...
start "" "%~dp0start_frontend.bat"

echo.
echo ========================================
echo ✓ ClarityCareers Started (FRESH)
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: Opening in browser...
echo.
echo WAIT FOR: "API READY - Server running!" in backend window
echo.
echo CHECKING: Backend should now have:
echo   1. _is_valid_atomic_skill filtering
echo   2. recruiter_alert section in responses
echo   3. NO fake skill gaps (machine learning systems, etc)
echo.
pause
