# ADR-006: Strategy Pattern for AI Model Integration

## Status

Accepted

## Context

LangPlug integrates multiple AI models for different tasks:

**Transcription Models:**

- OpenAI Whisper (multiple sizes: tiny, base, small, medium, large)
- NVIDIA Parakeet (NeMo framework)
- Future: Google Chirp, Assembly AI, custom models

**Translation Models:**

- Helsinki-NLP OPUS-MT (language-pair specific)
- Meta NLLB-200 (multilingual)
- Future: Google Translate API, DeepL API, GPT-4

Each model has different:

- Initialization requirements (model loading, GPU/CPU)
- Input/output formats
- Performance characteristics (speed, accuracy, memory)
- Dependencies (PyTorch, Transformers, NeMo)

We need an architecture that:

- Allows hot-swapping models without changing business logic
- Makes testing easy (mock models for unit tests)
- Supports model selection at runtime (user preference or auto-selection)
- Isolates model-specific code from service layer

## Decision

We will use the **Factory + Strategy Pattern** for AI model integration.

**Strategy Pattern:**
Each model type implements a common interface:

```python
# Abstract base classes (Strategy interfaces)
class TranscriptionService(ABC):
    @abstractmethod
    async def transcribe(
        self,
        audio_path: Path,
        language: str,
        progress_callback: Optional[Callable] = None
    ) -> TranscriptionResult:
        pass

class TranslationService(ABC):
    @abstractmethod
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        pass
```

**Concrete Implementations:**

```python
class WhisperTranscriptionService(TranscriptionService):
    def __init__(self, model_size: str = "base"):
        self.model = whisper.load_model(model_size)

    async def transcribe(self, audio_path, language, progress_callback):
        # Whisper-specific implementation
        pass

class ParakeetTranscriptionService(TranscriptionService):
    def __init__(self):
        self.model = nemo.load_model("parakeet-rnnt")

    async def transcribe(self, audio_path, language, progress_callback):
        # Parakeet-specific implementation
        pass
```

**Factory Pattern:**

```python
class TranscriptionServiceFactory:
    @staticmethod
    def create(model_name: str) -> TranscriptionService:
        match model_name:
            case "whisper-tiny":
                return WhisperTranscriptionService("tiny")
            case "whisper-base":
                return WhisperTranscriptionService("base")
            case "parakeet":
                return ParakeetTranscriptionService()
            case _:
                raise ValueError(f"Unknown model: {model_name}")
```

**Service Layer Integration:**

```python
class VideoProcessingService:
    def __init__(
        self,
        transcription_factory: TranscriptionServiceFactory,
        translation_factory: TranslationServiceFactory,
    ):
        self.transcription_factory = transcription_factory
        self.translation_factory = translation_factory

    async def process_video(self, video: Video, user_prefs: UserPreferences):
        # Get model based on user preference
        transcription_service = self.transcription_factory.create(
            user_prefs.transcription_model
        )

        # Use strategy interface - no knowledge of implementation
        result = await transcription_service.transcribe(
            audio_path=video.audio_path,
            language=video.language,
        )
```

## Consequences

**Positive:**

- Clean separation: service layer doesn't know about model implementation details
- Easy to add new models: implement interface, register in factory
- Testability: mock strategy interfaces for unit tests
- Hot-swappable: change models at runtime via factory
- User choice: let users select models based on accuracy/speed tradeoff
- Fail-fast: factory raises error for unknown models
- Type safety: interfaces enforce contract via abstract base classes
- Concurrent models: run multiple models in parallel for comparison

**Negative:**

- More boilerplate: abstract base classes, factory, concrete implementations
- Indirection: two layers (factory + strategy) vs direct model usage
- Complexity: new developers must understand factory and strategy patterns
- Potential over-engineering for simple cases

**Risks:**

- Interface becomes too generic and loses type safety
- Factory grows too complex with many model configurations
- Performance overhead from abstraction layers (mitigation: async, caching)

## Alternatives Considered

- **Alternative 1: Direct model usage in service layer**
  - _Why rejected_: Tight coupling. Changing models requires modifying service layer. Hard to test. No way to swap models at runtime.

- **Alternative 2: Adapter pattern per model**
  - _Why rejected_: Similar to Strategy but more complex. Adapters wrap existing interfaces; we're defining our own interfaces.

- **Alternative 3: Plugin system with dynamic loading**
  - _Why rejected_: Overkill. We control all models. Dynamic loading adds complexity (importlib, discovery) without benefit.

- **Alternative 4: Model registry with string-based dispatch**
  - _Why rejected_: Loses type safety. String-based lookup is error-prone. Factory provides type-checked model selection.

## References

- Transcription service interface: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/services/transcription/base.py`
- Whisper implementation: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/services/transcription/whisper_service.py`
- Translation service interface: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/services/translation/base.py`
- OPUS-MT implementation: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/services/translation/opus_service.py`
- Factory implementation: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/services/factories.py`
- Related: ADR-001 (Layered Architecture)
