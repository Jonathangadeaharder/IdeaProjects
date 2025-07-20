# Archived Legacy Projects - 2025-07-20

This directory contains legacy Python projects that were consolidated into the unified processing engine as part of **ARCH-03: Legacy Python Projects Consolidation**.

## Archived Projects

### 1. SubtitleMaker/
**Original Location:** `c:\Users\Jonandrop\IdeaProjects\SubtitleMaker\`  
**Archive Reason:** Functionality fully integrated into unified processor  
**Replacement:** A1Decider API with `pipeline_config: "quick"`

**Original Functionality:**
- Video transcription using Whisper
- 10-minute preview generation
- Full subtitle generation
- Audio extraction and processing

**Migration Path:**
```bash
# Old usage
python SubtitleMaker/subtitle_maker.py de --no-preview

# New usage
curl -X POST "http://localhost:8000/api/process" \
  -H "Content-Type: application/json" \
  -d '{"video_file_path": "/path/to/video.mp4", "language": "de", "pipeline_config": "quick", "no_preview": true}'
```

### 2. SubtitleTranslate/
**Original Location:** `c:\Users\Jonandrop\IdeaProjects\SubtitleTranslate\`  
**Archive Reason:** Functionality fully integrated into unified processor  
**Replacement:** A1Decider API with `pipeline_config: "full"`

**Original Functionality:**
- Batch subtitle translation
- Multiple language support
- Translation model management
- SRT file processing

**Migration Path:**
```bash
# Old usage
python SubtitleTranslate/subtitle_translate.py

# New usage
curl -X POST "http://localhost:8000/api/process" \
  -H "Content-Type: application/json" \
  -d '{"video_file_path": "/path/to/video.mp4", "src_lang": "de", "tgt_lang": "es", "pipeline_config": "full"}'
```

### 3. A1Decider_interactive_ui/
**Original Location:** `c:\Users\Jonandrop\IdeaProjects\A1Decider\a1decider.py`  
**Archive Reason:** Interactive UI preserved while core filtering logic integrated  
**Replacement:** A1Decider API with `pipeline_config: "learning"` (for automated processing)

**Original Functionality:**
- Interactive vocabulary learning game
- Real-time progress display
- Keyboard-driven learning interface
- A1-level word filtering

**Usage Notes:**
- This interactive UI can still be used standalone for vocabulary learning sessions
- For automated A1 filtering, use the unified API
- The core filtering logic is now available via API without the interactive interface

**Standalone Usage:**
```bash
# Still functional for interactive learning
python archived_legacy_projects/20250720_183800/A1Decider_interactive_ui/a1decider.py
```

**API Alternative:**
```bash
# Automated A1 filtering via API
curl -X POST "http://localhost:8000/api/process" \
  -H "Content-Type: application/json" \
  -d '{"video_file_path": "/path/to/video.mp4", "language": "de", "pipeline_config": "learning"}'
```

## Unified Processing Engine

**Current Location:** `c:\Users\Jonandrop\IdeaProjects\A1Decider\`

**Key Components:**
- `python_api_server.py` - FastAPI server with all endpoints
- `unified_subtitle_processor.py` - Main processing pipeline
- `concrete_processing_steps.py` - All processing steps
- `config.py` - Centralized configuration
- `shared_utils/` - Shared utilities and model management

**Available Pipelines:**
1. **Quick** (`"quick"`) - Transcription only (replaces SubtitleMaker)
2. **Learning** (`"learning"`) - Transcription + A1 filtering (replaces A1Decider core)
3. **Full** (`"full"`) - Transcription + filtering + translation (replaces SubtitleTranslate)
4. **Batch** (`"batch"`) - Optimized for multiple files

## Benefits of Consolidation

- ✅ **Reduced Code Duplication:** Single model management, unified configuration
- ✅ **Improved Maintainability:** Single codebase, centralized dependencies
- ✅ **Enhanced Scalability:** RESTful API, configurable pipelines
- ✅ **Better Integration:** Direct frontend integration, standardized formats

## Restoration Instructions

If you need to restore any of these projects:

1. **Copy the archived project back to the main directory:**
   ```bash
   Copy-Item -Path "archived_legacy_projects/20250720_183800/ProjectName" -Destination "c:\Users\Jonandrop\IdeaProjects\ProjectName" -Recurse
   ```

2. **Install dependencies:**
   ```bash
   cd ProjectName
   pip install -r requirements.txt
   ```

3. **Update import paths if needed** (shared_utils references may need adjustment)

## Documentation References

- **ARCH-03_LEGACY_CONSOLIDATION.md** - Complete consolidation documentation
- **ARCH-02_BFF_ELIMINATION.md** - Previous architectural changes
- **README.md** - Updated project overview

---

**Archive Date:** 2025-07-20 18:38:00  
**Consolidation Phase:** ARCH-03  
**Status:** Completed Successfully