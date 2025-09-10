@echo off
REM Professional LangPlug Server Stopper
REM Cleanly stops all servers

cd /d "%~dp0"
echo ========================================
echo  Stopping LangPlug Servers
echo ========================================
echo.

REM Stop servers with the professional manager
Backend\api_venv\Scripts\python.exe server_manager.py stop

echo.
echo All servers stopped.
pause
exit /b 0