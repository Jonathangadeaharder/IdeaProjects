# IdeaProjects - Unified Monorepo

This repository has been restructured from nested repositories into a unified monorepo structure to enable proper version control and CI/CD workflows.

## Repository Structure

This monorepo contains the following projects:

### Core Projects
- **A1Decider/** - Unified subtitle processing engine with FastAPI server
- **EpisodeGameApp/** - React Native application for episode-based vocabulary games
- **shared_utils/** - Shared utilities across projects
- **archived_legacy_projects/** - Archived legacy projects (SubtitleMaker, SubtitleTranslate, etc.)

### Unified Processing
- **unified_subtitle_processor.py** - Combined workflow for subtitle creation, filtering, and translation
- **processing_interfaces.py** - Granular processing interfaces
- **processing_steps.py** - Modular processing steps
- **pipeline_config_example.py** - Configuration examples

### Testing & Validation
- **test_granular_interfaces.py** - Interface testing
- **test_pipeline_architecture.py** - Architecture validation
- **validate_interfaces.py** - Interface validation utilities

## Recent Restructuring

### ARCH-01: Repository Unification
1. **Moved Excluded Projects**: `ImperioCasino` and `LatexStuff` have been moved to `../IdeaProjects_Excluded/` as they are not part of the core repository scope
2. **Removed Nested .git Directories**: Eliminated all nested `.git` directories from subdirectories to resolve version control conflicts
3. **Created Unified Repository**: Initialized a single git repository at the root level
4. **Added Comprehensive .gitignore**: Created a unified `.gitignore` file covering all project types (Python, Node.js, React Native, etc.)

### ARCH-02: Backend-for-Frontend Elimination
1. **Removed Node.js BFF**: Eliminated the Node.js backend service that acted as an intermediary
2. **Direct API Communication**: Frontend now communicates directly with the Python FastAPI server
3. **Simplified Architecture**: Reduced system complexity by removing the middleware layer
4. **Eliminated Dependencies**: Removed shared file system requirements between services

### ARCH-03: Legacy Python Projects Consolidation
1. **Unified Processing Engine**: Consolidated SubtitleMaker, A1Decider, and SubtitleTranslate into a single API
2. **Eliminated Code Duplication**: Single model management, unified configuration, shared utilities
3. **RESTful API Architecture**: All functionality available via FastAPI endpoints with configurable pipelines
4. **Archived Legacy Projects**: Safely preserved original projects in archived_legacy_projects/ directory

### Benefits
- ✅ Unified version control across all projects
- ✅ Simplified CI/CD pipeline setup
- ✅ Consistent dependency management
- ✅ Cross-project code sharing and refactoring
- ✅ Atomic commits across multiple projects
- ✅ Simplified architecture with direct API communication
- ✅ Reduced deployment complexity
- ✅ Eliminated tight coupling between services
- ✅ Consolidated processing engine with single API
- ✅ Eliminated code duplication across legacy projects
- ✅ Unified model management and configuration
- ✅ RESTful API architecture for all subtitle processing

## Features

### Subtitle Processing Pipeline
- **Automatic Processing**: Select a video file and the system handles subtitle creation, filtering, and translation
- **A1 Level Filtering**: Filters subtitles to show only lines containing unknown words (based on A1 German vocabulary)
- **Multi-language Translation**: Translates filtered subtitles between languages
- **GPU Acceleration**: Uses CUDA when available for faster processing
- **Multiple Formats**: Supports SRT and VTT subtitle formats

### Episode Game Application
- **React Native**: Cross-platform mobile application
- **Vocabulary Games**: Interactive learning based on subtitle content
- **Episode Management**: Organize content by episodes and series
- **Progress Tracking**: Monitor learning progress

## Requirements

### System Requirements
- Python 3.8+
- Node.js 16+
- CUDA-compatible GPU (recommended for faster processing)
- FFmpeg installed and accessible in PATH

### Python Dependencies
```bash
pip install -r requirements.txt
```

### React Native Dependencies
```bash
cd EpisodeGameApp
npm install
```

### Additional Setup

1. **SpaCy German Model**:
   ```bash
   python -m spacy download de_core_news_lg
   ```

2. **Word Lists** (for A1 filtering):
   The system expects these files in `G:/My Drive/`:
   - `a1.txt` - A1 level German vocabulary
   - `charaktere.txt` - Character names and proper nouns
   - `giuliwords.txt` - Additional known words

## Usage

### Unified Subtitle Processing
```bash
python unified_subtitle_processor.py
```

### Unified API Server
```bash
# Start the unified processing API
python A1Decider/python_api_server.py

# API endpoints available at http://localhost:8000
# - POST /api/process - Main processing endpoint
# - POST /api/upload-and-process - File upload and processing
# - GET /api/health - Health check
# - GET /api/pipelines - Available pipeline configurations
```

### Legacy Tools (Archived)
```bash
# Interactive A1 vocabulary game (preserved)
python archived_legacy_projects/*/A1Decider_interactive_ui/a1decider.py

# Note: SubtitleMaker and SubtitleTranslate functionality
# is now available via the unified API with different pipeline configs
```

### Episode Game App
```bash
cd EpisodeGameApp
npm start
```

## Development

### Running Tests
```bash
# Python tests
python -m pytest

# Interface validation
python validate_interfaces.py

# Architecture tests
python test_pipeline_architecture.py

# React Native tests
cd EpisodeGameApp
npm test
```

### Project Structure Validation
```bash
python test_granular_interfaces.py
```

## Configuration

### Default Settings
- **Language**: German (de) for subtitle creation
- **Translation**: German to Spanish (de → es)
- **Whisper Model**: turbo (good balance of speed and accuracy)
- **Device**: CUDA if available, otherwise CPU

### Customization
Refer to `pipeline_config_example.py` for configuration options and `processing_interfaces.py` for available processing modules.

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**:
   - The system will automatically fall back to CPU if CUDA fails
   - Consider using a smaller Whisper model

2. **Missing Word Lists**:
   - The system will show warnings but continue processing
   - Filtering will be less effective without proper word lists

3. **FFmpeg Not Found**:
   - Install FFmpeg and ensure it's in your system PATH

4. **SpaCy Model Missing**:
   - Run: `python -m spacy download de_core_news_lg`

### Performance Tips
- Use CUDA-compatible GPU for faster processing
- For very long videos, consider splitting them first
- Close other GPU-intensive applications during processing

## Contributing

With the unified monorepo structure, contributions can now span multiple projects and maintain consistency across the entire codebase. Please ensure all tests pass before submitting pull requests.

## Architecture

This monorepo follows a simplified modular architecture with:
- **Direct API Communication**: React Native frontend communicates directly with Python FastAPI backend
- **Shared utilities** for common functionality
- **Granular interfaces** for flexible processing pipelines
- **Unified configuration** across all projects
- **Consistent testing** and validation frameworks
- **Eliminated Middleware**: No intermediate Node.js BFF service required

For detailed architecture information, see:
- `ARCH-03_LEGACY_CONSOLIDATION.md` - Latest consolidation of legacy projects
- `ARCH-02_BFF_ELIMINATION.md` - Backend-for-Frontend elimination
- Various `*_SUMMARY.md` files in the A1Decider directory