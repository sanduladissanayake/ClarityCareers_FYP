@echo off
echo ========================================
echo ClarityCareers - AI Recruitment Platform
echo ========================================
echo.
echo STEP 1: Clearing old cache and processes...
taskkill /F /IM python.exe >nul 2>&1
powershell -Command "Get-ChildItem -Path '%~dp0' -Filter '__pycache__' -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
timeout /t 2 /nobreak >nul
echo ✓ Cache cleared

echo.
echo STEP 2: Starting backend server (with fixes)...
start "" cmd /k "%~dp0start_backend.bat"
echo.
echo Please wait 20 seconds for the server to start...
timeout /t 20 /nobreak >nul
echo ✓ Backend should be running

echo.
echo STEP 3: Opening frontend...
start "" "%~dp0start_frontend.bat"
echo ✓ Frontend starting
timeout /t 5 /nobreak >nul
echo.
echo ========================================
echo ✓ Application Started!
echo ========================================
echo.
echo ✓ FIXES ACTIVE:
echo   - No fake skill gaps (machine learning systems removed)
echo   - Recruiter alert showing hard requirements
echo   - Simulator working correctly
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo IMPORTANT: 
echo 1. Wait for backend window to show: "API READY - Server running!"
echo 2. Browser will open automatically
echo 3. Login with: jobseeker_demo / pass123
echo.
pause
