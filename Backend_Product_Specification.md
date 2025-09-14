# LangPlug Backend Product Specification

## Overview

LangPlug is a German language learning platform that combines video content with intelligent subtitle filtering and vocabulary tracking. The backend provides RESTful APIs for video processing, vocabulary management, user authentication, and learning analytics.

## System Architecture

### Technology Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT-based token authentication
- **Video Processing**: Integration with Whisper for transcription, NLLB for translation
- **Frontend Communication**: JSON REST APIs

### Core Components

#### 1. Authentication Service
- User registration and login
- JWT token generation and validation
- Session management
- Password hashing and security

#### 2. Video Management Service
- Video upload and storage
- Episode/series organization
- Video streaming with range requests
- Subtitle file management

#### 3. Processing Pipeline
- **Transcription**: Speech-to-text conversion using Whisper
- **Filtering**: Vocabulary-based subtitle filtering
- **Translation**: German-to-English translation using NLLB
- **Chunking**: Segment-based learning processing

#### 4. Vocabulary Service
- Vocabulary database management
- User vocabulary tracking
- Word difficulty classification
- Known/unknown word tracking

#### 5. Learning Analytics
- Progress tracking
- Vocabulary mastery metrics
- Learning statistics

## API Endpoints

### Authentication
```
POST /auth/login - User login
POST /auth/register - User registration
POST /auth/logout - User logout
GET /auth/me - Get current user info
```

### Video Management
```
GET /videos - List available videos
GET /videos/{series}/{episode} - Stream video file
GET /videos/subtitles/{subtitle_path} - Serve subtitle files
POST /videos/upload/{series} - Upload new video
POST /videos/subtitle/upload - Upload subtitle file
```

### Processing Pipeline
```
POST /process/transcribe - Transcribe video to generate subtitles
POST /process/filter-subtitles - Filter subtitles based on user vocabulary
POST /process/translate-subtitles - Translate subtitles between languages
POST /process/chunk - Process specific video segment for learning
POST /process/prepare-episode - Full episode processing pipeline
GET /process/progress/{task_id} - Get background task progress
```

### Vocabulary Management
```
GET /vocabulary/blocking-words - Get difficult vocabulary words
POST /vocabulary/mark-known - Mark word as known/unknown
POST /vocabulary/preload - Preload vocabulary database
GET /vocabulary/library/{level} - Get vocabulary by level (A1, A2, etc.)
POST /vocabulary/library/bulk-mark - Bulk mark words as known
GET /vocabulary/library/stats - Get vocabulary statistics
```

### User Profile
```
GET /profile - Get user profile
PUT /profile - Update user profile
GET /profile/progress - Get learning progress
```

## Data Models

### User
```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "created_at": "datetime",
  "last_login": "datetime"
}
```

### VideoInfo
```json
{
  "series": "string",
  "season": "string",
  "episode": "string",
  "title": "string",
  "path": "string",
  "has_subtitles": "boolean"
}
```

### VocabularyWord
```json
{
  "word": "string",
  "lemma": "string",
  "pos": "string",
  "frequency": "number",
  "difficulty": "string",
  "cefr_level": "string",
  "definition": "string",
  "examples": ["string"]
}
```

### ProcessingStatus
```json
{
  "status": "string", // pending, processing, completed, error
  "progress": "number", // 0-100
  "current_step": "string",
  "message": "string",
  "result": "object"
}
```

## Processing Pipeline

### 1. Transcription Stage
- Extract audio from video file
- Process audio through Whisper model
- Generate SRT subtitle file
- Save transcription results

### 2. Filtering Stage
- Load subtitle file
- Parse subtitle segments
- Check each word against user's vocabulary
- Identify "blocking words" (unknown/difficult vocabulary)
- Generate filtered subtitle sets

### 3. Translation Stage
- Extract text from subtitle segments
- Translate German text to English using NLLB
- Generate dual-language subtitle files
- Save translation results

### 4. Chunking Stage
- Process specific time segments
- Generate learning-optimized subtitles
- Create vocabulary lists for segment
- Generate both German and English subtitle files
- Validate authentication and fail fast on errors

## Vocabulary System

### CEFR Levels
- **A1**: Beginner
- **A2**: Elementary
- **B1**: Intermediate
- **B2**: Upper Intermediate
- **C1**: Advanced
- **C2**: Proficiency

### Word Classification
- **Known**: Words marked by user as known
- **Learning**: Words currently being studied
- **Blocked**: Unknown words that block comprehension
- **Ignored**: Words user chooses to ignore

Authentication is required to access user-specific vocabulary data. Processing will fail if valid authentication cannot be established.

### Difficulty Scoring
- Based on word frequency in German corpus
- CEFR level classification
- User-specific tracking
- Context-aware filtering

## Configuration

### Environment Variables
```
LANGPLUG_HOST=0.0.0.0
LANGPLUG_PORT=8000
LANGPLUG_DEBUG=True
LANGPLUG_VIDEOS_PATH=/path/to/videos
LANGPLUG_DATA_PATH=/path/to/data
LANGPLUG_LOGS_PATH=/path/to/logs
LANGPLUG_TRANSCRIPTION_SERVICE=whisper
LANGPLUG_TRANSLATION_SERVICE=nllb
LANGPLUG_DEFAULT_LANGUAGE=de
LANGPLUG_SESSION_TIMEOUT_HOURS=24
LANGPLUG_LOG_LEVEL=INFO
```

### File Structure
```
/videos/                    # Video storage
  /{series}/
    /{episode}.mp4
    /{episode}.srt
/data/                      # Application data
  /subtitles/               # Processed subtitles
  /vocabulary.db            # Vocabulary database
/logs/                      # Log files
  /langplug-backend.log
```

## Performance Requirements

### Response Times
- **API Endpoints**: < 500ms for simple operations
- **Video Streaming**: Real-time with range request support
- **Background Processing**: Asynchronous with progress tracking
- **Database Queries**: < 100ms for typical operations

### Scalability
- **Concurrent Users**: 100+ simultaneous users
- **Video Processing**: Queue-based processing
- **Database**: SQLite with connection pooling
- **Caching**: In-memory caching for frequent operations

## Security

### Authentication
- JWT tokens with expiration
- Password hashing with bcrypt
- Session timeout enforcement
- CORS protection

### Data Protection
- User data encryption at rest
- Secure password storage
- Input validation and sanitization
- Rate limiting for API endpoints

## Error Handling

### HTTP Status Codes
- **200**: Success
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **500**: Internal Server Error

### Error Response Format
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "ISO8601 datetime"
}
```

### Authentication Errors
- **SessionExpiredError**: Raised when session tokens are invalid or expired
- **InvalidCredentialsError**: Raised when login credentials are incorrect
- **UserAlreadyExistsError**: Raised when attempting to register an existing user

### Error Handling Strategy
The system uses explicit error handling to ensure issues are properly identified:
- Authentication failures result in immediate error responses
- Missing user data causes processing to halt with clear error messages
- Invalid session tokens are rejected rather than silently ignored

## Monitoring and Logging

### Log Levels
- **DEBUG**: Development information
- **INFO**: General operational messages
- **WARNING**: Warning conditions
- **ERROR**: Error conditions
- **CRITICAL**: Critical conditions

### Metrics Tracked
- API response times
- Processing pipeline success/failure rates
- User activity and engagement
- System resource usage

## Deployment

### Requirements
- Python 3.11+
- FFmpeg for audio processing
- GPU support recommended for Whisper/NLLB
- 4GB+ RAM recommended
- 50GB+ storage for video content

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload

# Run production server
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Docker Support
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Future Enhancements

### Planned Features
- Multi-language support
- Mobile app integration
- Social learning features
- Advanced analytics dashboard
- AI-powered pronunciation training
- Spaced repetition system integration

### Technical Improvements
- PostgreSQL migration for better scalability
- Redis caching for performance
- Message queue for processing tasks
- Microservices architecture
- Real-time collaboration features