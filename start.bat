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

REM Cleanup any existing server processes
echo Performing cleanup...
Backend\api_venv\Scripts\python.exe server_manager.py stop >nul 2>&1

REM Start both backend and frontend servers in separate windows
echo Starting backend server...
start "LangPlug Backend" cmd /k "cd /d %~dp0\Backend && echo Backend starting... && api_venv\Scripts\python.exe run_backend.py"

echo Starting frontend server...
timeout /t 5 /nobreak >nul
start "LangPlug Frontend" cmd /k "cd /d %~dp0\Frontend && echo Frontend starting... && npm run dev"

echo.
echo Servers are starting in separate windows:
echo  - Backend: http://localhost:8000
echo  - Frontend: http://localhost:3000
echo.
echo This window will now close automatically.

timeout /t 3 /nobreak >nul
exit