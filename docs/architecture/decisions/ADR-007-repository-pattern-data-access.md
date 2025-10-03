# ADR-007: Repository Pattern for Data Access

## Status

Accepted

## Context

LangPlug's service layer needs to persist and retrieve data:

- Users, videos, vocabulary entries, subtitles, study sessions
- Complex queries (e.g., "get all vocabulary for user X in video Y")
- Transactions (e.g., create video + subtitles atomically)
- Testing (mock data access without real database)

Directly using SQLAlchemy ORM in the service layer creates several problems:

- Service layer becomes tightly coupled to database implementation
- Testing requires complex database setup/teardown
- Hard to swap data sources (e.g., switch from SQL to NoSQL)
- Business logic mixes with SQL query construction
- Violation of Single Responsibility Principle

## Decision

We will implement the **Repository Pattern** to abstract data access.

**Repository Interface:**

```python
class VideoRepository(ABC):
    @abstractmethod
    async def create(self, video: Video) -> Video:
        pass

    @abstractmethod
    async def get_by_id(self, video_id: int) -> Optional[Video]:
        pass

    @abstractmethod
    async def get_by_user(self, user_id: int) -> List[Video]:
        pass

    @abstractmethod
    async def update(self, video: Video) -> Video:
        pass

    @abstractmethod
    async def delete(self, video_id: int) -> None:
        pass
```

**SQLAlchemy Implementation:**

```python
class SQLAlchemyVideoRepository(VideoRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, video: Video) -> Video:
        self.session.add(video)
        await self.session.commit()
        await self.session.refresh(video)
        return video

    async def get_by_id(self, video_id: int) -> Optional[Video]:
        result = await self.session.execute(
            select(Video).where(Video.id == video_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> List[Video]:
        result = await self.session.execute(
            select(Video)
            .where(Video.user_id == user_id)
            .order_by(Video.created_at.desc())
        )
        return result.scalars().all()
```

**Service Layer Integration:**

```python
class VideoService:
    def __init__(
        self,
        video_repo: VideoRepository,
        vocabulary_repo: VocabularyRepository,
    ):
        self.video_repo = video_repo
        self.vocabulary_repo = vocabulary_repo

    async def get_user_videos(self, user_id: int) -> List[VideoDTO]:
        # Service layer doesn't know about SQLAlchemy
        videos = await self.video_repo.get_by_user(user_id)
        return [VideoDTO.from_orm(v) for v in videos]
```

**Testing with Mock Repository:**

```python
class MockVideoRepository(VideoRepository):
    def __init__(self):
        self.videos: Dict[int, Video] = {}
        self.next_id = 1

    async def create(self, video: Video) -> Video:
        video.id = self.next_id
        self.videos[self.next_id] = video
        self.next_id += 1
        return video

    async def get_by_id(self, video_id: int) -> Optional[Video]:
        return self.videos.get(video_id)

# In tests
async def test_video_service():
    mock_repo = MockVideoRepository()
    service = VideoService(video_repo=mock_repo)

    video = await service.create_video(...)
    assert video.id is not None
```

**Transaction Management:**

```python
# Repositories use injected session for transaction control
async def create_video_with_subtitles(
    video_data: VideoCreate,
    subtitles: List[SubtitleCreate],
    session: AsyncSession,
):
    video_repo = SQLAlchemyVideoRepository(session)
    subtitle_repo = SQLAlchemySubtitleRepository(session)

    # Both operations in same session/transaction
    video = await video_repo.create(video_data)
    for subtitle in subtitles:
        subtitle.video_id = video.id
        await subtitle_repo.create(subtitle)

    await session.commit()  # Atomic commit
```

## Consequences

**Positive:**

- Service layer is decoupled from database implementation
- Easy to test: use in-memory mock repositories
- Database-agnostic: can switch from SQLAlchemy to raw SQL, MongoDB, etc.
- Clear separation of concerns: repositories handle data access, services handle business logic
- Transaction management is explicit and controlled
- Complex queries are encapsulated in repository methods with descriptive names
- Improved maintainability: database changes don't ripple through service layer

**Negative:**

- More boilerplate: repository interfaces + implementations + mocks
- Potential performance overhead from abstraction
- Can lead to anemic domain models (just data containers)
- Repository methods can proliferate (get_by_x, get_by_y, etc.)
- Learning curve for developers unfamiliar with pattern

**Risks:**

- Over-abstraction: wrapping simple CRUD in unnecessary layers
- Repository becomes a "god object" with too many methods
- Leaky abstraction: repository interface exposes database-specific concepts (e.g., eager loading)
- Performance issues if repositories don't support batch operations

## Alternatives Considered

- **Alternative 1: Active Record pattern (SQLAlchemy models with built-in CRUD)**
  - _Why rejected_: Couples business logic to database models. Hard to test. Violates Single Responsibility Principle.

- **Alternative 2: Data Mapper pattern (separate mapper classes)**
  - _Why rejected_: More complex than Repository. SQLAlchemy ORM already provides mapping. Repository is simpler abstraction.

- **Alternative 3: Direct SQLAlchemy in service layer**
  - _Why rejected_: Tight coupling, hard to test, mixes concerns. Service layer shouldn't know about SQLAlchemy sessions and queries.

- **Alternative 4: CQRS (Command Query Responsibility Segregation)**
  - _Why rejected_: Too complex for current scale. CQRS makes sense with event sourcing and read/write model separation. Overkill for LangPlug.

## References

- Repository base classes: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/repositories/base.py`
- Video repository: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/repositories/video_repository.py`
- Vocabulary repository: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/repositories/vocabulary_repository.py`
- Service integration: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/services/video_service.py`
- Related: ADR-001 (Layered Architecture), ADR-003 (Database Choice)
