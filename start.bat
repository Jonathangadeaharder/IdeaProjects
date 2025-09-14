@echo off
REM Professional LangPlug Server Starter
REM Performs cleanup, starts both backend and frontend, then closes itself

cd /d "%~dp0"
echo ========================================
echo  LangPlug Professional Server Manager
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

REM Comprehensive cleanup of existing processes and terminals
echo Performing comprehensive cleanup...

REM Kill any existing LangPlug processes
echo Stopping existing servers...
Backend\api_venv\Scripts\python.exe management\cli.py stop >nul 2>&1

REM Kill processes on ports 8000 and 3000 to ensure clean start
echo Cleaning up ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /f /pid %%a >nul 2>&1

REM Close any existing LangPlug terminal windows
echo Closing existing terminal windows...
taskkill /f /fi "WINDOWTITLE eq LangPlug Backend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq LangPlug Frontend*" >nul 2>&1

REM Wait for cleanup to complete
timeout /t 2 /nobreak >nul

REM Start both backend and frontend servers in separate windows
echo Starting backend server...
start "LangPlug Backend" cmd /c "cd /d %~dp0\Backend && echo Backend starting... && api_venv\Scripts\python.exe run_backend.py && echo Backend stopped. Press any key to close... && pause >nul"

echo Starting frontend server...
timeout /t 5 /nobreak >nul
start "LangPlug Frontend" cmd /c "cd /d %~dp0\Frontend && echo Frontend starting... && npm run dev && echo Frontend stopped. Press any key to close... && pause >nul"

echo.
echo Servers are starting in separate windows:
echo  - Backend: http://localhost:8000
echo  - Frontend: http://localhost:3000
echo.
echo This window will now close automatically.

timeout /t 3 /nobreak >nul
exit