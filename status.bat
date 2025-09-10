@echo off
REM Check status of LangPlug servers

cd /d "%~dp0"
Backend\api_venv\Scripts\python.exe server_manager.py status
pause
exit /b 0