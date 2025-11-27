@echo off
REM LangPlug Transcription GUI Launcher
REM Activates virtual environment and runs the transcription GUI

echo Starting LangPlug Transcription GUI...
echo.

REM Change to backend directory
cd /d "%~dp0\.."

REM Activate virtual environment
call api_venv\Scripts\activate.bat

REM Run the GUI
python scripts\transcription_gui.py

REM Deactivate on exit
deactivate

pause
