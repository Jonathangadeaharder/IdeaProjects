@echo off
REM LangPlug Translation GUI Launcher
REM Activates virtual environment and runs the translation GUI

echo Starting LangPlug Translation GUI...
echo.

REM Activate virtual environment
call api_venv\Scripts\activate.bat

REM Run the GUI
python scripts\translation_gui.py

REM Deactivate on exit
deactivate

pause
