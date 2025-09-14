@echo off
REM Professional LangPlug Server Stopper
REM Cleanly stops all servers

cd /d "%~dp0"
echo ========================================
echo  Stopping LangPlug Servers
echo ========================================
echo.

REM Stop servers with the professional manager
echo Stopping servers via management system...
Backend\api_venv\Scripts\python.exe management\cli.py stop

REM Force kill any remaining processes on ports 8000 and 3000
echo Cleaning up ports 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Killing process on port 8000: %%a
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    echo Killing process on port 3000: %%a
    taskkill /f /pid %%a >nul 2>&1
)

REM Close any LangPlug terminal windows
echo Closing LangPlug terminal windows...
taskkill /f /fi "WINDOWTITLE eq LangPlug Backend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq LangPlug Frontend*" >nul 2>&1

REM Kill any remaining Python processes that might be running LangPlug
echo Cleaning up any remaining LangPlug processes...
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr "run_backend\|main.py\|uvicorn"') do (
    taskkill /f /pid %%a >nul 2>&1
)

REM Kill any remaining Node.js processes that might be running the frontend
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq node.exe" /fo csv ^| findstr "npm\|vite"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo All servers and processes stopped.
echo Ports 8000 and 3000 are now available.
pause
exit /b 0