- always execute python with api_venv
- on WSL, run .bat files using: cmd.exe /c filename.bat (not ./filename.bat)
- to properly clean up hanging CMD processes: cmd.exe /c "taskkill /F /IM cmd.exe && taskkill /F /IM python.exe && taskkill /F /IM node.exe"
- always use browsermcp when you want to verify end to end behaviour together with reading the logs
- whenever you fail an action or tool use and later find out how to do it correctly, update this file with the lesson learned
- **IMPORTANT**: Always use `cmd.exe /c start.bat` to start both frontend and backend servers - this script handles necessary cleanup and proper initialization. Never start servers manually.

# lessons-learned-2025-09-07
- Server startup should use dynamic polling instead of fixed timeouts - backend takes ~25s due to Whisper model loading
- On Windows, npm commands need to be run with cmd.exe /c prefix for proper execution
- Health checks should poll every 2 seconds with informative progress messages

# lessons-learned-2025-09-06
- API endpoint paths must match exactly - use /process/* not /processing/*
- Authentication response field names vary - check actual response (token vs access_token) 
- When a service method doesn't exist (like set_user_id), use the underlying service directly
- Routes can be registered but still return 404 if backend crashed - always check server health first
- Use check_routes.py script to verify all registered endpoints when debugging 404s
- Backend startup can be slow - wait and verify with health check before testing
- When testing workflow, run from Backend directory: cd Backend && cmd.exe /c "api_venv\Scripts\python.exe test_workflow.py"
- VocabularyPreloadService exists and works - no need to recreate it
- Always check both frontend console (browser MCP) AND backend logs when debugging connection issues