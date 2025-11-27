@echo off
echo Running Contract Tests (Schemathesis)...

cd /d "%~dp0\.."
call api_venv\Scripts\activate

echo Starting backend for contract testing...
set LANGPLUG_VIDEOS_PATH=%~dp0\..\..\..\videos
set LANGPLUG_PORT=8000
set LANGPLUG_RELOAD=0
set LANGPLUG_TRANSCRIPTION_SERVICE=whisper-tiny
set LANGPLUG_TRANSLATION_SERVICE=opus-de-es
set STRICT_CONTRACTS=1

start /B python run_backend.py
echo Waiting for backend...
timeout /t 10 /nobreak >nul

echo Running Schemathesis...
st run http://localhost:8000/openapi.json --checks all --hypothesis-max-examples=10

echo Stopping backend...
taskkill /F /IM python.exe
