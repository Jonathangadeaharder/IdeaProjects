# Port Coordination Between Frontend and Backend

## The Problem
The Frontend and Backend need to communicate on the same port, but they were misconfigured:
- Frontend was hardcoded to use port 8000
- Backend startup scripts were using port 8003
- Tests didn't catch this because they mock API calls

## Why Tests Didn't Catch This
1. **Unit tests mock everything** - They don't make real HTTP calls
2. **Contract tests use mocked responses** - They validate shapes, not connections
3. **No integration tests for port connectivity** - We weren't testing actual HTTP connections
4. **Test environment uses same hardcoded port** - Tests assumed port 8000

## The Solution

### 1. Coordinated Startup Scripts
- `run-dev.bat` - Starts both services with matching ports
- `start-all.bat` - Full control over port configuration

### 2. Environment Variable Support
Both Frontend and Backend now respect environment variables:

**Frontend**: `VITE_API_URL`
```javascript
baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

**Backend**: `LANGPLUG_PORT`
```python
port = int(os.environ.get("LANGPLUG_PORT", settings.port))
```

### 3. Automatic Port Cleanup
All startup scripts now:
1. Kill processes on target ports before starting
2. Use consistent default port (8000)
3. Pass port configuration via environment variables

## How to Start Services

### Quick Development (Recommended)
```batch
# From project root
run-dev.bat
```
- Automatically cleans ports
- Starts Backend on port 8000
- Starts Frontend configured for port 8000
- Opens browser automatically

### Manual Start with Port Coordination
```batch
# Terminal 1 - Backend
cd Backend
set LANGPLUG_PORT=8000
python start_backend_fast.py

# Terminal 2 - Frontend
cd Frontend
set VITE_API_URL=http://localhost:8000
npm run dev
```

### Full Featured Start
```batch
# From project root
start-all.bat
# Choose mode (fast or with models)
```

## Port Configuration Table

| Script | Default Port | Environment Variable | Auto-cleanup |
|--------|-------------|---------------------|--------------|
| `run-dev.bat` | 8000 | Yes | Yes |
| `start-all.bat` | 8000 | Yes | Yes |
| `start_backend_fast.py` | 8000 | LANGPLUG_PORT | Yes |
| `start_backend_with_models.py` | 8000 | LANGPLUG_PORT | Yes |
| Frontend dev server | 3000 | VITE_API_URL for Backend | No |

## Testing Port Coordination
New test added: `Frontend/src/test/integration/api-connection.test.ts`
- Verifies environment variable usage
- Documents expected port ranges
- Will fail if misconfigured

## Debugging Port Issues

1. **Check what's using a port:**
```powershell
netstat -ano | findstr :8000
```

2. **Kill process on specific port:**
```powershell
Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

3. **Nuclear option - kill everything:**
```batch
scripts\stop-all.bat
```

## Best Practices
1. Always use coordinated startup scripts for development
2. Never hardcode ports in application code
3. Use environment variables for port configuration
4. Add integration tests that verify actual connectivity
5. Document port requirements in README