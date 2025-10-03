# ADR-005: WebSocket for Real-Time Communication

## Status

Accepted

## Context

LangPlug performs long-running video processing tasks:

- Video transcription (can take minutes for long videos)
- Subtitle generation
- Translation of subtitle segments
- Vocabulary extraction

Users need real-time feedback on processing progress:

- Current processing stage (downloading, transcribing, translating)
- Progress percentage
- Estimated time remaining
- Error notifications if processing fails

Without real-time updates, users are left staring at a loading spinner with no feedback, leading to poor user experience and uncertainty about whether processing is actually happening.

## Decision

We will use **WebSocket** for bidirectional real-time communication between frontend and backend.

**Architecture:**

1. **ConnectionManager Pattern:**

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def send_progress(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
```

2. **WebSocket Endpoint:**

```python
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    current_user: User = Depends(get_current_user_ws)
):
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(user_id)
```

3. **Progress Reporting:**

```python
# In video processing service
await connection_manager.send_progress(
    user_id=user.id,
    message={
        "stage": "transcription",
        "progress": 45,
        "eta_seconds": 120,
    }
)
```

4. **Frontend Integration:**

```typescript
const ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateProgress(data.stage, data.progress, data.eta_seconds);
};
```

## Consequences

**Positive:**

- Real-time progress updates without polling
- Low latency (milliseconds vs seconds with polling)
- Bidirectional communication (future: cancel processing, pause/resume)
- Efficient: single persistent connection vs many HTTP requests
- Native browser support (no external libraries required)
- Better user experience with live feedback
- Server can push error notifications immediately

**Negative:**

- More complex than REST APIs (connection lifecycle, reconnection logic)
- Requires connection state management on both client and server
- Debugging WebSocket connections is harder than HTTP requests
- Load balancing requires sticky sessions or Redis pub/sub
- Not RESTful (different paradigm from HTTP APIs)

**Risks:**

- Connection drops require reconnection logic on frontend
- Memory leaks if connections aren't cleaned up properly
- Scalability concerns with many concurrent connections (mitigation: use async WebSockets, connection pooling)
- Corporate firewalls may block WebSocket connections (mitigation: fallback to polling)

## Alternatives Considered

- **Alternative 1: HTTP polling (request every N seconds)**
  - _Why rejected_: Inefficient (many unnecessary requests), high latency (up to N seconds delay), poor battery life on mobile, server load.

- **Alternative 2: Server-Sent Events (SSE)**
  - _Why rejected_: Unidirectional (server → client only). Can't cancel processing from client. WebSocket provides full bidirectional communication for future features.

- **Alternative 3: Long polling**
  - _Why rejected_: Complex to implement correctly, still less efficient than WebSockets, requires HTTP/2 server push or similar hacks.

- **Alternative 4: GraphQL subscriptions**
  - _Why rejected_: Adds GraphQL dependency when we're using REST. WebSocket is simpler and more direct for our use case.

## References

- WebSocket ConnectionManager: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/core/websocket.py`
- WebSocket routes: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/routes/websocket.py`
- Frontend WebSocket client: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Frontend/src/services/websocket.ts`
- Related: ADR-002 (FastAPI + React Stack)
