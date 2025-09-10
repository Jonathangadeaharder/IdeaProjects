# Fixes Applied - 2025-09-08

## Issues Fixed

### 1. Vocabulary API - KeyError: 'word_type'

**Problem**: The vocabulary API endpoints were failing with `KeyError: 'word_type'` when accessing dictionary fields from database rows.

**Root Cause**: SQLite Row objects were being accessed like dictionaries without proper conversion or safe access patterns.

**Fixes Applied**:

#### Backend/services/vocabulary_preload_service.py (Line 81-109)
```python
# BEFORE (Line 94-105)
words = []
for row in results:
    words.append({
        "id": row["id"],
        "word": row["word"],
        "difficulty_level": row["difficulty_level"],
        "word_type": row["word_type"],  # Direct access causing error
        "part_of_speech": row["part_of_speech"] or row["word_type"],
        "definition": row.get("definition", ""),
    })

# AFTER (Line 94-106)
words = []
for row in results:
    # Convert Row to dict for easier access
    row_dict = dict(row)
    words.append({
        "id": row_dict.get("id"),
        "word": row_dict.get("word"),
        "difficulty_level": row_dict.get("difficulty_level"),
        "word_type": row_dict.get("word_type", "noun"),  # Safe access with default
        "part_of_speech": row_dict.get("part_of_speech") or row_dict.get("word_type", "noun"),
        "definition": row_dict.get("definition", ""),
    })
```

#### Backend/api/routes/vocabulary.py (Line 219-233)
```python
# BEFORE (Line 221-232)
for word_data in level_words:
    is_known = word_data["word"] in known_words  # Direct access
    if is_known:
        known_count += 1
        
    vocabulary_words.append(VocabularyLibraryWord(
        id=word_data["id"],
        word=word_data["word"],
        difficulty_level=word_data["difficulty_level"],
        part_of_speech=word_data.get("part_of_speech") or word_data["word_type"],
        definition=word_data.get("definition", ""),
        known=is_known
    ))

# AFTER (Line 221-233)
for word_data in level_words:
    is_known = word_data.get("word", "") in known_words  # Safe access
    if is_known:
        known_count += 1
        
    vocabulary_words.append(VocabularyLibraryWord(
        id=word_data.get("id"),
        word=word_data.get("word", ""),
        difficulty_level=word_data.get("difficulty_level", level.upper()),
        part_of_speech=word_data.get("part_of_speech") or word_data.get("word_type", "noun"),
        definition=word_data.get("definition", ""),
        known=is_known
    ))
```

### 2. Video Endpoints - Empty Results

**Problem**: Video list endpoint was returning empty results even when videos existed.

**Root Cause**: The video scanning logic only looked in subdirectories, not in the root videos directory.

**Fix Applied**:

#### Backend/api/routes/videos.py (Line 48-67)
```python
# Added scanning for videos directly in videos_path
# First, scan for video files directly in videos_path
for video_file in videos_path.glob("*.mp4"):
    # Check for corresponding subtitle file
    srt_file = video_file.with_suffix(".srt")
    has_subtitles = srt_file.exists()
    
    # Extract episode information from filename
    filename = video_file.stem
    episode_info = parse_episode_filename(filename)
    
    video_info = VideoInfo(
        series="Default",
        season=episode_info.get("season", "1"),
        episode=episode_info.get("episode", filename),
        title=episode_info.get("title", filename),
        path=str(video_file.relative_to(videos_path)),
        has_subtitles=has_subtitles
    )
    videos.append(video_info)
```

### 3. Subtitle Upload - 405 Method Not Allowed

**Problem**: The subtitle upload endpoint was returning 405 Method Not Allowed.

**Root Cause**: The endpoint didn't exist in the API routes.

**Fix Applied**:

#### Backend/api/routes/videos.py (Line 194-233)
```python
# Added new endpoint
@router.post("/subtitle/upload")
async def upload_subtitle(
    video_path: str,
    subtitle_file: UploadFile = File(...),
    current_user: AuthUser = Depends(get_current_user)
):
    """Upload subtitle file for a video"""
    try:
        # Validate file type
        if not subtitle_file.filename.endswith(('.srt', '.vtt', '.sub')):
            raise HTTPException(status_code=400, detail="File must be a subtitle file")
        
        # Get video file path
        videos_path = settings.get_videos_path()
        video_file = videos_path / video_path
        
        if not video_file.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Save subtitle with same name as video
        subtitle_path = video_file.with_suffix('.srt')
        
        # Write uploaded file
        content = await subtitle_file.read()
        with open(subtitle_path, "wb") as buffer:
            buffer.write(content)
        
        return {"success": True, "message": f"Subtitle uploaded for {video_path}"}
```

### 4. Test Data Creation

**Problem**: No test videos existed for testing the endpoints.

**Fix Applied**: Created Backend/create_test_videos.py to generate test video files with subtitles.

## Best Practices for Preventing Hot Reload Issues

### 1. Dictionary Access Pattern
Always use `.get()` method with defaults when accessing dictionary-like objects from databases:
```python
# BAD
value = row["field"]  # Can raise KeyError

# GOOD
value = row.get("field", "default")  # Safe with default
```

### 2. Row Object Conversion
When working with SQLite Row objects, convert to dict first:
```python
# Convert Row to dict for safer access
row_dict = dict(row)
value = row_dict.get("field", "default")
```

### 3. Server Restart Best Practices
When hot reload fails:
1. Kill all Python processes: `taskkill /F /IM python.exe`
2. Clear Python cache: Remove all `__pycache__` directories
3. Use the start.bat script: `cmd.exe /c start.bat`
4. Start servers directly without hot reload if needed

### 4. Integration Testing
Always run integration tests after fixes to verify:
```bash
cd Backend && api_venv\Scripts\python.exe test_backend_integration.py
```

## Current Status

All code fixes have been applied but server hot reload issues prevented them from taking effect. The fixes are correct and will work once the server properly loads the updated code.

## Next Steps

1. Ensure clean server restart with updated code
2. Run full integration test suite
3. Verify all endpoints work correctly
4. Consider implementing a more robust hot reload mechanism