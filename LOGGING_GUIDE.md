# 🔍 LangPlug Debug Logging Guide

This guide explains how to use the comprehensive logging system to debug issues when clicking through the app.

## 📋 Log Files Location

**Backend Logs** (in `Backend/logs/`):
- `langplug_debug.log` - All debug information (most detailed)
- `langplug_api.log` - API requests and responses
- `langplug.log` - General application logs
- `langplug_errors.log` - Errors only

**Frontend Logs**:
- Browser console (F12 -> Console tab)
- Also sent to backend and stored in `langplug_debug.log`

## 🚀 Quick Start

### 1. View Logs in Real-Time
```bash
# From project root directory
python view_logs.py
```

### 2. View Specific Log Files
```bash
# View recent debug logs
tail -f Backend/logs/langplug_debug.log

# View API requests only
tail -f Backend/logs/langplug_api.log

# View errors only
tail -f Backend/logs/langplug_errors.log
```

### 3. Browser Console
1. Press F12 to open developer tools
2. Go to Console tab
3. Look for colored log messages:
   - 🐛 DEBUG (cyan)
   - ℹ️ INFO (green)
   - ⚠️ WARN (yellow)
   - ❌ ERROR (red)

## 📊 What Gets Logged

### Frontend Events:
- **User Actions**: Button clicks, form submissions, navigation
- **API Calls**: All requests/responses with timing
- **Component Lifecycle**: Loading, mounting, updates
- **Errors**: JavaScript errors, API failures
- **Performance**: Load times, render performance

### Backend Events:
- **API Requests**: Method, URL, headers, body
- **API Responses**: Status code, data, processing time
- **Database Operations**: Queries, results, errors
- **Service Events**: Authentication, file processing, vocabulary updates
- **System Events**: Startup, configuration, errors

## 🎯 Common Debugging Scenarios

### 1. Frontend Not Loading
**Check**: Browser console + `langplug_debug.log`
```bash
# Look for startup errors
grep -A5 -B5 "Frontend starting up" Backend/logs/langplug_debug.log
```

### 2. API Call Failing
**Check**: `langplug_api.log` + Browser console
```bash
# Monitor API calls in real-time
tail -f Backend/logs/langplug_api.log | grep "ERROR"
```

### 3. Vocabulary System Issues
**Check**: Search for vocabulary-related logs
```bash
# Find vocabulary operations
grep "VocabularyLibrary\|vocabulary" Backend/logs/langplug_debug.log
```

### 4. Authentication Issues
**Check**: Auth-related logs
```bash
# Find auth events
grep "auth\|login\|session" Backend/logs/langplug_debug.log
```

## 📱 Frontend Logging Examples

### In Browser Console:
```javascript
// View recent logs
logger.getRecentLogs(20)

// Clear logs
logger.clearLogs()

// Export logs to JSON
console.log(logger.exportLogs())
```

### User Action Logs:
```
ℹ️ [User Action] word-toggle in VocabularyLibrary | Data: {word: "schwierig", level: "B2", fromKnown: false, toKnown: true}
ℹ️ [API] Request: POST /vocabulary/mark-known
✅ [API] Response: 200 POST /vocabulary/mark-known | Duration: 145ms
```

## 🔧 Log Analysis Tips

### 1. Follow a Complete User Flow
1. Clear browser console
2. Start log monitoring: `python view_logs.py`
3. Perform the action that's causing issues
4. Check both browser console and file logs

### 2. Look for Error Patterns
```bash
# Find all errors from the last hour
grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" Backend/logs/langplug_errors.log
```

### 3. API Performance Issues
```bash
# Find slow API calls (>1000ms)
grep "process_time.*[0-9]\{4\}" Backend/logs/langplug_api.log
```

### 4. Frontend-Backend Sync Issues
- Check if frontend sends request: Browser console
- Check if backend receives request: `langplug_api.log`
- Check if backend processes correctly: `langplug_debug.log`
- Check if frontend receives response: Browser console

## 🎛️ Log Configuration

### Change Log Level (Backend)
Edit `Backend/.env`:
```bash
# More verbose logging
LANGPLUG_LOG_LEVEL=DEBUG

# Less verbose logging
LANGPLUG_LOG_LEVEL=INFO
```

### Change Frontend Log Level
Add to `Frontend/.env.local`:
```bash
VITE_LOG_LEVEL=DEBUG
VITE_ENABLE_LOG_API=true
```

## 📈 Log File Management

### Automatic Rotation
- Files rotate when they reach size limits (10-50MB)
- Old logs are kept as `.log.1`, `.log.2`, etc.
- Up to 5-10 backup files are maintained

### Manual Cleanup
```bash
# Clean old logs (optional)
find Backend/logs -name "*.log.*" -mtime +7 -delete
```

## 🆘 Troubleshooting the Logger

### If logs aren't appearing:
1. Check if `Backend/logs/` directory exists
2. Check file permissions
3. Verify log level settings
4. Check if backend server is running

### If frontend logs aren't in backend files:
1. Check browser console for logger initialization
2. Verify API endpoint `/debug/frontend-logs` is accessible
3. Check network tab for failed log requests

## 💡 Pro Tips

1. **Use multiple terminals**: One for backend logs, one for running the app
2. **Filter by category**: Use grep to find specific types of events
3. **Watch timing**: Look at `process_time` to find performance bottlenecks
4. **Check sequence**: Follow the complete request/response cycle
5. **Use browser dev tools**: Network tab shows all HTTP requests/responses