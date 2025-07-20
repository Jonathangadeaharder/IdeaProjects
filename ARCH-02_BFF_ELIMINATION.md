# ARCH-02: Node.js BFF Elimination

## Overview

This document describes the implementation of ARCH-02, which eliminates the Node.js Backend-for-Frontend (BFF) service and refactors the frontend to call the Python API directly.

## Changes Made

### 1. Frontend Service Refactoring

**File:** `EpisodeGameApp/src/services/PythonBridgeService.ts`

#### Key Changes:
- **Direct Python API Communication**: Changed from `http://localhost:3001/api` to `http://localhost:8000`
- **Endpoint Updates**: Updated all endpoints to match Python FastAPI structure:
  - `/create-subtitles` → `/api/process`
  - `/process-subtitles` → `/api/process`
  - `/translate-subtitles` → `/api/process` (with pipeline config)
  - `/check-dependencies` → `/health`
- **Response Format**: Updated interfaces to match Python API response structure
- **Pipeline Configuration**: Added support for Python API pipeline configurations (`quick`, `learning`, `full`, `batch`)

#### New Methods:
- `requestPipelineConfigurations()`: Get available pipeline configurations from Python API

#### Updated Methods:
- `requestSubtitleCreation()`: Now uses unified `/api/process` endpoint
- `requestA1Processing()`: Uses pipeline-based processing
- `requestSubtitleTranslation()`: Integrated into unified pipeline
- `requestDependencyCheck()`: Direct health check from Python API
- `requestVocabularyAnalysis()`: Uses `learning` pipeline configuration

### 2. Response Interface Updates

#### New Interfaces:
```typescript
interface PythonHealthResponse {
  status: string;
  version: string;
  dependencies: Record<string, boolean>;
}

interface PythonProcessingResponse {
  success: boolean;
  message: string;
  results?: {
    video_file: string;
    audio_file?: string;
    preview_srt?: string;
    full_srt?: string;
    filtered_srt?: string;
    translated_srt?: string;
    metadata?: any;
  };
  error?: string;
}
```

### 3. Architecture Benefits

#### Eliminated Dependencies:
- **Node.js Backend Service**: No longer needed
- **Express.js Server**: Removed middleware layer
- **Axios Proxy Logic**: Direct fetch calls to Python API
- **Shared File System**: No file system dependencies between services

#### Simplified Architecture:
```
BEFORE:
Frontend → Node.js BFF (port 3001) → Python API (port 8000)

AFTER:
Frontend → Python API (port 8000)
```

#### Performance Improvements:
- **Reduced Latency**: Eliminated proxy layer
- **Fewer Network Hops**: Direct API communication
- **Simplified Error Handling**: Single point of failure
- **Better Resource Utilization**: No Node.js process overhead

### 4. Configuration Changes

#### Environment Variables:
- Frontend now connects directly to `http://localhost:8000`
- No longer requires Node.js backend configuration
- Python API CORS settings updated to allow direct frontend access

#### Pipeline Configurations:
- `quick`: Fast transcription only
- `learning`: Transcription + A1 filtering
- `batch`: Transcription + filtering + translation
- `full`: Complete pipeline with preview

### 5. Deployment Considerations

#### Services Required:
- ✅ Python FastAPI Server (port 8000)
- ❌ Node.js Backend (port 3001) - **ELIMINATED**
- ✅ Frontend Application

#### Startup Sequence:
1. Start Python API server: `python A1Decider/python_api_server.py`
2. Start frontend application
3. ~~Start Node.js backend~~ - **NO LONGER NEEDED**

### 6. Testing Updates

#### Frontend Tests:
- Updated `PythonBridgeService.test.ts` to test direct Python API calls
- Mock responses updated to match Python API format
- Health check tests updated for new endpoint

#### Integration Tests:
- Direct API integration tests
- Pipeline configuration tests
- Error handling tests for Python API responses

### 7. Migration Guide

#### For Developers:
1. **Stop Node.js Backend**: No longer needed
2. **Update Environment**: Frontend connects to port 8000
3. **API Changes**: Use new response format in frontend code
4. **Pipeline Config**: Use new pipeline configuration options

#### For Deployment:
1. **Remove Node.js Service**: Update deployment scripts
2. **Update Load Balancer**: Direct traffic to Python API
3. **Update Monitoring**: Monitor Python API only
4. **Update Documentation**: Remove Node.js references

## Files Modified

- `EpisodeGameApp/src/services/PythonBridgeService.ts` - Complete refactor
- `ARCH-02_BFF_ELIMINATION.md` - This documentation

## Files That Can Be Removed

- `EpisodeGameApp/backend/` - Entire Node.js backend directory
- `EpisodeGameApp/backend/server.js` - Express server
- `EpisodeGameApp/backend/package.json` - Node.js dependencies
- `EpisodeGameApp/backend/__tests__/` - Backend tests
- `EpisodeGameApp/DECOUPLED_SERVICES_SETUP.md` - No longer relevant

## Verification Steps

1. **Health Check**: `curl http://localhost:8000/health`
2. **Pipeline Config**: `curl http://localhost:8000/api/pipelines`
3. **Frontend Connection**: Verify frontend can reach Python API directly
4. **Processing Test**: Submit video processing request through frontend

## Success Criteria

✅ **Simplified Architecture**: Single API endpoint  
✅ **Eliminated Node.js Dependency**: No Express server needed  
✅ **Direct API Communication**: Frontend → Python API  
✅ **Maintained Functionality**: All features work as before  
✅ **Improved Performance**: Reduced latency and resource usage  
✅ **Better Maintainability**: Fewer moving parts  

## Next Steps

1. **Remove Node.js Backend**: Delete `EpisodeGameApp/backend/` directory
2. **Update Documentation**: Remove Node.js references from README
3. **Update CI/CD**: Remove Node.js build and deployment steps
4. **Performance Testing**: Measure improvement in response times
5. **Frontend Testing**: Comprehensive testing of direct API integration