@echo off
echo ============================================================
echo           Stopping All LangPlug Services
echo ============================================================
echo.

REM Kill ONLY terminal windows specifically titled for LangPlug services
echo [1/7] Closing LangPlug terminal windows...
taskkill /F /FI "WINDOWTITLE eq LangPlug Backend" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq LangPlug Frontend" >nul 2>&1

REM Close terminal windows that contain LangPlug paths or commands (even after process ended)
echo [2/7] Closing LangPlug-related terminal windows...
powershell -Command "& { $targets = @('LangPlug Backend','LangPlug Frontend','LangPlug Backend (api_venv)','LangPlug Frontend (npm run dev)'); $active = $env:LANGPLUG_ACTIVE_CMD_PID; Get-Process cmd,powershell -ErrorAction SilentlyContinue | Where-Object { $title = $_.MainWindowTitle; $cmdLine = $_.CommandLine; $title -and ($targets -contains $title) -and ($cmdLine -notmatch 'start-all\.bat') -and ($title -notlike '*Launcher*') -and (-not $active -or $_.Id -ne [int]$active) } | Stop-Process -Force -ErrorAction SilentlyContinue }"

REM Also close windows showing the directory paths
powershell -Command "& { $targets = @('LangPlug Backend','LangPlug Frontend'); $active = $env:LANGPLUG_ACTIVE_CMD_PID; Get-Process cmd,powershell -ErrorAction SilentlyContinue | Where-Object { $title = $_.MainWindowTitle; $cmdLine = $_.CommandLine; if (-not $title) { $false } else { (($targets | Where-Object { $title.StartsWith($_) }).Count -gt 0) -and ($cmdLine -notmatch 'start-all\.bat') -and ($title -notlike '*Launcher*') -and (-not $active -or $_.Id -ne [int]$active) } } | Stop-Process -Force -ErrorAction SilentlyContinue }"

REM Kill cmd windows started by start-all.bat (identified by their command line)
powershell -Command "& { $active = $env:LANGPLUG_ACTIVE_CMD_PID; Get-WmiObject Win32_Process -Filter \"Name='cmd.exe'\" | Where-Object { ($_.CommandLine -match 'LangPlug\\Backend.*start_backend' -or $_.CommandLine -match 'LangPlug\\Frontend.*npm run dev') -and (-not $active -or $_.ProcessId -ne [int]$active) } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue } }"

REM Kill Python processes ONLY if they're running LangPlug-related scripts
echo [3/7] Killing LangPlug Python processes...
powershell -Command "& { Get-Process python* | Where-Object { $_.CommandLine -match 'backend|uvicorn|langplug|start_backend' } | Stop-Process -Force -ErrorAction SilentlyContinue }"

REM Kill Node processes ONLY if they're running in LangPlug directories
echo [4/7] Killing LangPlug Node.js processes...
powershell -Command "& { Get-Process node | Where-Object { $_.CommandLine -match 'LangPlug|vite' } | Stop-Process -Force -ErrorAction SilentlyContinue }"

REM Special cleanup for windows showing "(api_venv)" or directory paths after process ends
echo [4.5/7] Closing orphaned LangPlug terminal windows...
powershell -Command "& { Get-Process cmd | Where-Object { $_.MainWindowTitle -match '\(api_venv\)' -or $_.MainWindowTitle -match 'C:\\.*\\LangPlug\\(Backend|Frontend)' -or $_.MainWindowTitle -eq 'C:\Users\Jonandrop\IdeaProjects\LangPlug\Backend' -or $_.MainWindowTitle -eq 'C:\Users\Jonandrop\IdeaProjects\LangPlug\Frontend' } | Stop-Process -Force -ErrorAction SilentlyContinue }"

REM Kill processes on all common ports (8000-8003, 3000-3002, 5173)
echo [5/7] Clearing LangPlug ports...
powershell -Command "& { $ports = @(8000, 8001, 8002, 8003, 3000, 3001, 3002, 5173); foreach ($port in $ports) { Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | ForEach-Object { $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue; if ($proc.ProcessName -match 'python|node|npm') { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } } } }"

REM Kill any uvicorn or vite processes specifically
echo [6/7] Killing web server processes...
powershell -Command "& { Get-Process | Where-Object { $_.ProcessName -match 'python' -and $_.CommandLine -match 'uvicorn' } | Stop-Process -Force -ErrorAction SilentlyContinue }"
powershell -Command "& { Get-Process | Where-Object { $_.ProcessName -match 'node' -and $_.CommandLine -match 'vite' } | Stop-Process -Force -ErrorAction SilentlyContinue }"

REM Kill WSL LangPlug processes if WSL is installed
echo [7/7] Cleaning up WSL LangPlug processes (if applicable)...
powershell -Command "& { if (Get-Command wsl -ErrorAction SilentlyContinue) { wsl pkill -f 'langplug' 2>$null; wsl pkill -f 'uvicorn.*8000' 2>$null; wsl pkill -f 'vite.*3000' 2>$null } }"

echo.
echo ============================================================
echo           All LangPlug services stopped!
echo ============================================================
echo.
