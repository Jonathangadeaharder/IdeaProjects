# 🚀 LangPlug Startup Guide

## Simple Startup Scripts (Clean & Logged)

### 🎯 **Main Startup Script:**

| Script | Purpose | Behavior |
|--------|---------|----------|
| `start.bat` | Starts both servers with cleanup | Performs cleanup, starts both servers in separate windows, then closes itself |

### 📝 **Management Scripts:**

| Script | Purpose |
|--------|---------|
| `status.bat` | Check status of running servers |
| `stop.bat` | Stop all running servers |
| `view_logs.bat` | Interactive log viewer with live monitoring |

---

## 🔧 **Usage:**

### Start Both Servers (Recommended):
```batch
start.bat
```
- Performs cleanup of any existing server processes
- Starts both backend and frontend servers in separate windows
- Automatically closes the startup window
- Backend API: http://localhost:8000
- Frontend App: http://localhost:3000

### Check Server Status:
```batch
status.bat
```
- Shows current status of all servers

### Stop All Servers:
```batch
stop.bat
```
- Cleanly stops all running servers

### View Logs:
```batch
view_logs.bat
```
- Interactive menu for viewing logs
- Live monitoring option
- View both logs side-by-side

---

## 📊 **Log Features:**

✅ **Timestamped entries**  
✅ **Startup information logged**  
✅ **Real-time server output**  
✅ **Error logging included**  
✅ **Previous logs cleared on restart**  
✅ **Live monitoring available**  

---

## 🎯 **Simplified Project:**

**REMOVED:** 12+ old startup scripts  
**KEPT:** 4 essential scripts with logging  
**RESULT:** Clean, simple, reliable startup system  

---

## 🔍 **Troubleshooting:**

1. **Server won't start:** Check the respective log file
2. **Frontend esbuild errors:** Scripts use Windows npm directly
3. **Backend import errors:** Uses `Backend/api_venv` directly
4. **View real-time logs:** Use `view_logs.bat` option 4 or 5

---

## 💡 **Best Practices:**

- **Development:** Use `start_both.bat` 
- **Production:** Use individual scripts
- **Debugging:** Monitor logs with `view_logs.bat`
- **Quick check:** `type logs\backend.log` or `type logs\frontend.log`