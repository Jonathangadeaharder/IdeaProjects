@echo off
echo Starting LangPlug SRT Filter GUI...
echo.

REM Activate virtual environment
call api_venv\Scripts\activate

REM Run the SRT filter Tkinter GUI
python scripts\srt_filter_gui.py

REM If something went wrong, keep the window open so you can read the error
if errorlevel 1 (
    echo.
    echo [ERROR] SRT filter GUI exited with error code %errorlevel%.
    pause
)
