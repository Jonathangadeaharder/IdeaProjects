# LangPlug Backend

The backend for LangPlug, a German language learning platform that combines video content with intelligent subtitle filtering and vocabulary tracking.

## Project Structure

```
Backend/
├── api/                 # API route definitions
│   └── routes/          # Individual route modules
├── core/                # Core application components
├── data/                # Data files and databases
├── database/            # Database management and migrations
├── logs/                # Application logs
├── scripts/             # Utility scripts
├── services/            # Business logic and service layers
│   ├── authservice/     # Authentication service
│   ├── dataservice/     # Data management services
│   ├── filterservice/   # Subtitle filtering services
│   ├── loggingservice/  # Logging services
│   ├── transcriptionservice/ # Audio transcription services
│   ├── translationservice/   # Language translation services
│   └── utils/           # Utility functions
├── tests/               # Unit and integration tests
├── videos/              # Video storage (symlink)
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Getting Started

### Prerequisites
- Python 3.11+
- FFmpeg
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd LangPlug/Backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (see Configuration section)

5. Run the development server:
```bash
uvicorn main:app --reload
```

### Configuration

Create a `.env` file in the Backend directory with the following variables:

```
LANGPLUG_HOST=0.0.0.0
LANGPLUG_PORT=8000
LANGPLUG_DEBUG=True
LANGPLUG_VIDEOS_PATH=../videos
LANGPLUG_DATA_PATH=./data
LANGPLUG_LOGS_PATH=./logs
LANGPLUG_TRANSCRIPTION_SERVICE=whisper
LANGPLUG_TRANSLATION_SERVICE=nllb
LANGPLUG_DEFAULT_LANGUAGE=de
LANGPLUG_SESSION_TIMEOUT_HOURS=24
LANGPLUG_LOG_LEVEL=INFO
```

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Run linter
ruff check .

# Format code
ruff format .
```

## Services

### Transcription Service
- Uses OpenAI Whisper for speech-to-text conversion
- Supports multiple model sizes (tiny, base, small, medium, large)

### Translation Service
- Uses Facebook's NLLB (No Language Left Behind) for translation
- Supports German to English translation

### Filtering Service
- Filters subtitles based on user's vocabulary knowledge
- Identifies "blocking words" that may impede comprehension

## Logging

Logs are written to the `logs/` directory with both file and console output. Log levels can be configured via the `LANGPLUG_LOG_LEVEL` environment variable.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

[License information to be added]