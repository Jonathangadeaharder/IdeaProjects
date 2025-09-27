# 🚀 LangPlug Setup Guide

## 🎯 Quick Start (EASIEST METHOD)

### **Super Easy Startup - Just Double-Click!**

**Windows Users:**
1. Double-click `start.bat`
2. Both servers will start automatically in separate windows
3. Backend: http://localhost:8000 | Frontend: http://localhost:3000

**Alternative:**
```bash
python server_manager.py start
```
This will start both servers with health monitoring

## ✨ **Automatic Virtual Environment System**

✅ **No manual activation required**
✅ **Auto-detects correct Python environment**
✅ **Cross-platform (Windows/Linux/Mac/WSL)**
✅ **Smart dependency checking**
✅ **Works even if some AI features are missing**

## Prerequisites

- Python 3.8+ *(already installed)*
- Node.js 18+ and npm *(for frontend)*

### Install Node.js (if needed):
1. **Download**: Visit https://nodejs.org/
2. **Install**: Node.js 18+ LTS version
3. **Verify**: `node --version`

## Alternative: Start Each Service Separately

### Backend Only:
```bash
cd Backend
python -m venv api_venv
# On Windows:
api_venv\Scripts\activate
# On Mac/Linux:
source api_venv/bin/activate

pip install fastapi uvicorn pydantic python-multipart
python main.py
```

### Frontend Only (after Node.js is installed):
```bash
cd Frontend
npm install
npm run dev
```

## Troubleshooting

### "pip install failed"
- **Solution**: Use `python install_dependencies.py` instead
- **Cause**: Some packages have version conflicts

### "npm/yarn not found"
- **Solution**: Install Node.js from nodejs.org
- **Verify**: Run `node --version` and `npm --version`

### "Import errors in Python"
- **Solution**: The backend will run with limited functionality
- **Fix**: Install dependencies: `pip install fastapi uvicorn`

### "Videos not found"
- **Solution**: Create directory structure:
  ```
  videos/
  └── Superstore/
      ├── Episode1.mp4
      └── Episode2.mp4
  ```

## Minimal Working Setup

For a basic working version:

1. **Install Node.js** (required)
2. **Install basic Python deps**:
   ```bash
   pip install fastapi uvicorn pydantic python-multipart
   ```
3. **Install frontend deps**:
   ```bash
   cd Frontend && npm install
   ```
4. **Start both servers**:
   ```bash
   python start.py
   ```

## What Should Work

Even with minimal setup:
- ✅ Frontend UI (login, video selection)
- ✅ Basic backend API
- ✅ User registration/login
- ✅ Video file detection
- ❌ AI transcription (requires whisper)
- ❌ Vocabulary filtering (requires spacy)

The UI will work perfectly, and you can add AI features later by installing the full dependencies.

## Next Steps

1. **Get the UI working first** with minimal setup
2. **Add your video files** to test the interface
3. **Install AI dependencies** for full functionality:
   ```bash
   pip install openai-whisper transformers spacy
   python -m spacy download de_core_news_lg
   ```

## Support

If you encounter issues:
1. Check this guide first
2. Try the manual installation: `python install_dependencies.py`
3. Start with minimal setup to test the UI
4. Add AI features incrementally
