@echo off
REM Run the SRT Filter GUI with proper virtual environment activation

cd /d "%~dp0.."
echo Activating virtual environment...
call api_venv\Scripts\activate.bat

echo Starting SRT Filter GUI...
python scripts\srt_filter_gui.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Script exited with error code %errorlevel%
    pause
)
