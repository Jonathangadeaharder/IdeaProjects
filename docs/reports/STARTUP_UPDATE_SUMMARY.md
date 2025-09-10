# LangPlug Startup Script Update Summary

## What was changed:

1. **Updated start.bat**:
   - Now performs cleanup before starting servers
   - Starts both backend and frontend servers in separate console windows
   - Automatically closes itself after launching the servers
   - Uses the correct virtual environment paths

2. **Updated documentation files**:
   - README_STARTUP.md: Updated to reflect that start.bat is the main startup script
   - SETUP_GUIDE.md: Updated to reference start.bat instead of the missing start_both_servers.bat
   - README.md: Updated the quick start instructions to use start.bat

3. **Updated management scripts**:
   - stop.bat: Now uses the correct virtual environment path
   - status.bat: Now uses the correct virtual environment path

## How to use:

### Windows Users (Recommended):
1. Double-click `start.bat` to start both servers
2. Servers will start in separate windows
3. The startup window will close automatically
4. Access the application:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000

### Alternative (Command Line):
1. Open Command Prompt in the project directory
2. Run `start.bat`

### To Stop Servers:
1. Double-click `stop.bat`
2. Or run `stop.bat` from Command Prompt

### To Check Status:
1. Double-click `status.bat`
2. Or run `status.bat` from Command Prompt