@echo off
echo Stopping LangPlug services...

REM Kill Python processes with "LangPlug Backend" window title
taskkill /F /FI "WINDOWTITLE eq LangPlug Backend*" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Backend stopped.
) else (
    echo Backend was not running or already stopped.
)

REM Kill Node processes with "LangPlug Frontend" window title
taskkill /F /FI "WINDOWTITLE eq LangPlug Frontend*" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Frontend stopped.
) else (
    echo Frontend was not running or already stopped.
)

echo All services stopped.
pause
