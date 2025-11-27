@echo off
REM LangPlug Translation GUI Launcher
REM Activates virtual environment and runs the translation GUI

echo Starting LangPlug Translation GUI...
echo.

REM Change to backend directory
cd /d "%~dp0\.."

REM Activate virtual environment
call api_venv\Scripts\activate.bat

REM Run the GUI
python scripts\translation_gui.py

REM Deactivate on exit
deactivate

pause
