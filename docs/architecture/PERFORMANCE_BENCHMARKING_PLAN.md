# Performance Benchmarking Plan for LangPlug

## Document Status

- **Version:** 1.0.0
- **Last Updated:** 2025-10-02
- **Status:** Draft
- **Owner:** Development Team

## Executive Summary

This document outlines a comprehensive performance benchmarking strategy for the LangPlug language learning platform. The plan covers backend API performance, frontend load times, database query optimization, AI model inference latency, and end-to-end user experience metrics. The goal is to establish baseline measurements, identify bottlenecks, and implement continuous performance monitoring to ensure the platform scales efficiently with growing user demand.

## Table of Contents

1. [Performance Metrics Definition](#1-performance-metrics-definition)
2. [Benchmarking Tools and Setup](#2-benchmarking-tools-and-setup)
3. [Test Scenarios](#3-test-scenarios)
4. [Baseline Measurements](#4-baseline-measurements)
5. [Performance Targets](#5-performance-targets)
6. [Continuous Performance Testing](#6-continuous-performance-testing)
7. [Optimization Strategies](#7-optimization-strategies)
8. [Implementation Timeline](#8-implementation-timeline)
9. [Appendices](#9-appendices)

---

## 1. Performance Metrics Definition

### 1.1 Backend API Metrics

#### Response Time Metrics

- **P50 (Median)**: 50th percentile response time
- **P95**: 95th percentile response time (acceptable worst case)
- **P99**: 99th percentile response time (critical worst case)
- **Mean Response Time**: Average across all requests

#### Throughput Metrics

- **Requests per Second (RPS)**: Total throughput capacity
- **Concurrent Users**: Maximum simultaneous active sessions
- **Transaction Rate**: Business operations completed per second

#### Resource Utilization

- **CPU Usage**: Percentage utilization under load
  - Idle: < 20%
  - Normal: 20-50%
  - Peak: 50-80%
  - Critical: > 80%
- **Memory Usage**: RAM consumption patterns
  - Baseline memory footprint
  - Memory growth under load
  - Memory leak detection
- **Network I/O**: Bandwidth consumption
  - Request payload sizes
  - Response payload sizes
  - Video streaming bandwidth

#### Endpoint-Specific Metrics

**Authentication Endpoints** (`/api/auth/*`)

- Login response time
- Registration response time
- Token refresh latency
- Session validation overhead

**Video Processing Endpoints** (`/api/process/*`)

- Video upload time (per MB)
- Transcription job submission latency
- Translation job submission latency
- Processing status poll frequency

**Vocabulary Endpoints** (`/api/vocabulary/*`)

- Vocabulary list retrieval time
- Word definition lookup latency
- User vocabulary update time
- Search query response time

**Streaming Endpoints** (`/api/videos/*`)

- Video metadata retrieval time
- Subtitle file retrieval time
- Chunk delivery latency
- Streaming start time

### 1.2 Frontend Performance Metrics

#### Loading Metrics (Web Vitals)

- **First Contentful Paint (FCP)**: Time to first visual content
  - Target: < 1.0s (Good), < 2.5s (Needs Improvement), > 2.5s (Poor)
- **Largest Contentful Paint (LCP)**: Time to main content
  - Target: < 2.5s (Good), < 4.0s (Needs Improvement), > 4.0s (Poor)
- **Time to Interactive (TTI)**: Time until page is fully interactive
  - Target: < 3.5s (Good), < 7.3s (Needs Improvement), > 7.3s (Poor)
- **Total Blocking Time (TBT)**: Sum of blocking time periods
  - Target: < 200ms (Good), < 600ms (Needs Improvement), > 600ms (Poor)
- **Cumulative Layout Shift (CLS)**: Visual stability score
  - Target: < 0.1 (Good), < 0.25 (Needs Improvement), > 0.25 (Poor)

#### Bundle Size Metrics

- **Initial Bundle Size**: Main JavaScript bundle
  - Target: < 200KB gzipped
- **Vendor Bundle Size**: Third-party dependencies
  - Target: < 300KB gzipped
- **Code Splitting Effectiveness**: Lazy-loaded chunks
  - Measure: % of code loaded on demand
- **Asset Optimization**: Images, fonts, CSS
  - Image optimization ratio
  - Font loading strategy effectiveness

#### Runtime Performance

- **React Render Time**: Component mount/update duration
- **State Management Overhead**: Zustand store operation latency
- **API Call Latency**: Frontend → Backend round trip time
- **Video Player Performance**:
  - Subtitle rendering latency
  - Chunk transition smoothness
  - Vocabulary overlay rendering time

### 1.3 Database Performance Metrics

#### Query Performance

- **Query Execution Time**: Individual query duration
  - Simple SELECT: < 10ms
  - Complex JOIN: < 50ms
  - Aggregation: < 100ms
- **Query Plan Analysis**: EXPLAIN output for slow queries
- **Index Effectiveness**: Index usage statistics

#### Connection Pool Metrics

- **Active Connections**: Current open connections
- **Connection Wait Time**: Time to acquire connection
- **Pool Saturation**: % of pool capacity used
- **Connection Churn**: Rate of connection open/close

#### Transaction Metrics

- **Transaction Duration**: Time from BEGIN to COMMIT
- **Lock Wait Time**: Time waiting for locks
- **Deadlock Frequency**: Rate of deadlock occurrences
- **Rollback Rate**: % of transactions rolled back

#### Database-Specific Metrics

**PostgreSQL (Production)**

- Cache hit ratio (target: > 99%)
- Bloat percentage (target: < 20%)
- Vacuum frequency and duration
- WAL generation rate

**SQLite (Development/Testing)**

- Journal mode (WAL recommended)
- Cache size effectiveness
- Checkpoint frequency
- Database file size growth

### 1.4 AI Model Performance Metrics

#### Transcription Service Metrics (Whisper)

- **Model Loading Time**: Time to load model into memory
  - whisper-tiny: < 2s
  - whisper-base: < 5s
  - whisper-small/medium: < 10s
- **Inference Latency**: Time per audio minute
  - Target: < 1 minute processing per 1 minute audio (real-time or better)
- **GPU Utilization**: CUDA usage patterns
  - GPU memory consumption
  - Compute utilization %
- **Batch Processing Efficiency**: Throughput with batching

#### Translation Service Metrics (Opus-MT / NLLB)

- **Model Loading Time**: Initial model load duration
  - opus-de-es: < 3s
  - nllb-distilled-600m: < 5s
- **Translation Latency**: Time per subtitle segment
  - Target: < 100ms per segment (average 10-20 words)
- **Batch Translation Throughput**: Segments processed per second
- **GPU/CPU Affinity**: Optimal execution device

#### Vocabulary Extraction Metrics (spaCy)

- **Model Loading Time**: SpaCy model initialization
  - de_core_news_lg: < 2s
  - en_core_web_sm: < 1s
- **NLP Processing Latency**: Time per document
  - Target: < 50ms per subtitle segment
- **Entity Recognition Accuracy**: % of valid vocabulary words extracted

#### Resource Usage

- **VRAM Consumption**: GPU memory per model
  - Monitor for multi-model scenarios
- **System RAM**: CPU fallback memory requirements
- **Model Cache Hit Rate**: Frequency of cached model reuse

---

## 2. Benchmarking Tools and Setup

### 2.1 Backend Load Testing Tools

#### Locust (Primary Tool)

**Why Locust:**

- Python-based (matches backend stack)
- Distributed load generation
- Real-time web UI for monitoring
- Scriptable user behavior simulation

**Installation:**

```bash
pip install locust==2.31.0
```

**Sample Locustfile:**

```python
# Backend/tests/performance/locustfile.py
from locust import HttpUser, task, between
import random

class LangPlugUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login and get auth token"""
        response = self.client.post("/api/auth/login", json={
            "username": "test@example.com",
            "password": "testpass123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def get_videos(self):
        """List available videos"""
        self.client.get("/api/videos", headers=self.headers)

    @task(2)
    def get_vocabulary(self):
        """Retrieve user vocabulary"""
        self.client.get("/api/vocabulary", headers=self.headers)

    @task(1)
    def submit_progress(self):
        """Update learning progress"""
        self.client.post("/api/progress", json={
            "video_id": random.randint(1, 100),
            "timestamp": random.randint(0, 3600),
            "words_learned": random.randint(1, 10)
        }, headers=self.headers)
```

**Running Locust:**

```bash
# Start Locust web interface
locust -f Backend/tests/performance/locustfile.py --host=http://localhost:8000

# Headless mode with 100 users, 10 spawn rate, 5 min test
locust -f Backend/tests/performance/locustfile.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 --run-time 5m --headless \
       --csv=results/locust_baseline
```

#### Apache Bench (ab) - Quick Spot Checks

**Use Cases:**

- Quick response time verification
- Single endpoint stress testing
- CI/CD integration

**Example Commands:**

```bash
# Test authentication endpoint
ab -n 1000 -c 10 -H "Content-Type: application/json" \
   -p auth_payload.json http://localhost:8000/api/auth/login

# Test video list endpoint with auth
ab -n 5000 -c 50 -H "Authorization: Bearer ${TOKEN}" \
   http://localhost:8000/api/videos
```

#### Alternative: k6 (Optional)

**Advantages:**

- JavaScript-based scripting
- Cloud execution support
- Excellent Grafana integration

**Installation:**

```bash
# macOS
brew install k6

# Windows
choco install k6

# Linux
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
  --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | \
  sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### 2.2 Frontend Performance Tools

#### Lighthouse (Primary Tool)

**Installation:**

```bash
npm install -g lighthouse
```

**Usage:**

```bash
# Run Lighthouse audit
lighthouse http://localhost:3000 --output html --output-path ./reports/lighthouse-baseline.html

# Run with specific device emulation
lighthouse http://localhost:3000 --preset=desktop --output json --output-path ./reports/desktop.json
lighthouse http://localhost:3000 --preset=mobile --output json --output-path ./reports/mobile.json

# CI mode (no Chrome instance)
lighthouse http://localhost:3000 --chrome-flags="--headless" --quiet --output json
```

**Automated Lighthouse Checks:**

```javascript
// Frontend/scripts/lighthouse-check.js
const lighthouse = require("lighthouse");
const chromeLauncher = require("chrome-launcher");

async function runLighthouse(url) {
  const chrome = await chromeLauncher.launch({ chromeFlags: ["--headless"] });
  const options = {
    logLevel: "info",
    output: "json",
    port: chrome.port,
    onlyCategories: ["performance"],
  };

  const runnerResult = await lighthouse(url, options);
  await chrome.kill();

  const score = runnerResult.lhr.categories.performance.score * 100;
  console.log(`Performance Score: ${score}`);

  if (score < 80) {
    throw new Error(`Performance score ${score} below threshold 80`);
  }
}

runLighthouse("http://localhost:3000");
```

#### WebPageTest (In-Depth Analysis)

**Use Cases:**

- Real-world network condition testing
- Multi-location testing
- Filmstrip view of loading

**Setup:**

```bash
# Use WebPageTest API
npm install webpagetest
```

```javascript
// Frontend/scripts/webpagetest-check.js
const WebPageTest = require("webpagetest");
const wpt = new WebPageTest("www.webpagetest.org", "YOUR_API_KEY");

wpt.runTest(
  "http://localhost:3000",
  {
    location: "Dulles:Chrome",
    connectivity: "Cable",
    firstViewOnly: false,
  },
  (err, result) => {
    console.log(result.data);
  },
);
```

#### Bundle Analyzer

**Webpack Bundle Analyzer (if using Webpack):**

```bash
npm install --save-dev webpack-bundle-analyzer
```

**Vite Plugin Visualizer (for Vite):**

```bash
npm install --save-dev rollup-plugin-visualizer
```

**Vite Config:**

```typescript
// Frontend/vite.config.ts
import { visualizer } from "rollup-plugin-visualizer";

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true,
      filename: "./dist/stats.html",
    }),
  ],
});
```

### 2.3 Database Performance Tools

#### PostgreSQL Tools

**pg_stat_statements (Query Monitoring):**

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- View slowest queries
SELECT
  query,
  calls,
  total_exec_time,
  mean_exec_time,
  max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

**EXPLAIN ANALYZE (Query Plan Analysis):**

```sql
-- Analyze specific queries
EXPLAIN ANALYZE
SELECT v.id, v.title, u.username
FROM videos v
JOIN users u ON v.user_id = u.id
WHERE v.status = 'processed'
ORDER BY v.created_at DESC
LIMIT 20;
```

**pgBench (Database Load Testing):**

```bash
# Initialize test database
pgbench -i -s 50 langplug_test

# Run benchmark: 10 clients, 100 transactions each
pgbench -c 10 -t 100 langplug_test

# Custom SQL script
pgbench -c 10 -t 100 -f custom_queries.sql langplug_test
```

#### SQLite Tools

**EXPLAIN QUERY PLAN:**

```sql
-- Analyze query execution
EXPLAIN QUERY PLAN
SELECT * FROM vocabulary WHERE user_id = 1 AND word LIKE 'test%';
```

**SQLite3 CLI Performance Metrics:**

```bash
sqlite3 langplug.db

.timer on
.stats on

SELECT COUNT(*) FROM vocabulary;
```

**Python Profiling:**

```python
# Backend/tests/performance/db_profiling.py
import sqlite3
import time

def profile_query(query, params=()):
    conn = sqlite3.connect('langplug.db')
    cursor = conn.cursor()

    start = time.time()
    cursor.execute(query, params)
    results = cursor.fetchall()
    duration = time.time() - start

    print(f"Query: {query}")
    print(f"Duration: {duration:.4f}s")
    print(f"Rows: {len(results)}")

    conn.close()

profile_query("SELECT * FROM vocabulary WHERE user_id = ?", (1,))
```

### 2.4 AI Model Profiling Tools

#### PyTorch Profiler

**Installation:**

```bash
pip install torch-tb-profiler
```

**Usage:**

```python
# Backend/services/transcriptionservice/profiling.py
import torch
from torch.profiler import profile, record_function, ProfilerActivity

def profile_transcription(audio_path):
    with profile(
        activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
        record_shapes=True,
        profile_memory=True,
        with_stack=True
    ) as prof:
        with record_function("transcription"):
            result = transcribe_audio(audio_path)

    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))
    prof.export_chrome_trace("trace.json")
```

#### Memory Profiler

**Installation:**

```bash
pip install memory-profiler
```

**Usage:**

```python
# Backend/services/translationservice/profiling.py
from memory_profiler import profile

@profile
def translate_subtitles(segments):
    """Profile memory usage during translation"""
    translations = []
    for segment in segments:
        translated = model.translate(segment.text)
        translations.append(translated)
    return translations
```

#### Custom Timing Decorators

```python
# Backend/utils/profiling.py
import time
import functools
import logging

logger = logging.getLogger(__name__)

def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.4f}s")
        return result
    return wrapper

# Usage
@timing_decorator
def transcribe_audio(audio_path):
    # ... transcription logic
    pass
```

### 2.5 Monitoring and Observability

#### Prometheus + Grafana

**Prometheus Setup:**

```yaml
# docker-compose.monitoring.yml
version: "3.8"
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus

volumes:
  prometheus_data:
  grafana_data:
```

**Prometheus Configuration:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "langplug-backend"
    static_configs:
      - targets: ["backend:8000"]
    metrics_path: "/metrics"

  - job_name: "langplug-postgres"
    static_configs:
      - targets: ["postgres-exporter:9187"]

  - job_name: "node-exporter"
    static_configs:
      - targets: ["node-exporter:9100"]
```

**FastAPI Prometheus Integration:**

```python
# Backend/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator

# Custom metrics
request_count = Counter(
    'langplug_requests_total',
    'Total requests by endpoint',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'langplug_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

active_users = Gauge(
    'langplug_active_users',
    'Number of active user sessions'
)

transcription_queue_size = Gauge(
    'langplug_transcription_queue_size',
    'Number of videos in transcription queue'
)

def setup_metrics(app):
    Instrumentator().instrument(app).expose(app)
```

**Usage in App:**

```python
# Backend/core/app.py
from .metrics import setup_metrics

def create_app():
    app = FastAPI(...)
    setup_metrics(app)
    return app
```

#### Custom Application Logging

**Performance Logging Middleware:**

```python
# Backend/core/performance_logging.py
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration * 1000,
                "user_agent": request.headers.get("user-agent")
            }
        )

        response.headers["X-Response-Time"] = f"{duration:.4f}"
        return response
```

---

## 3. Test Scenarios

### 3.1 Load Testing Scenarios

#### Scenario 1: Normal User Activity (Baseline)

**Profile:**

- 100 concurrent users
- 5-minute test duration
- Mix of authenticated actions

**User Behavior:**

```python
# locustfile.py - Normal Load
class NormalUser(HttpUser):
    wait_time = between(2, 5)

    @task(5)
    def browse_videos(self):
        self.client.get("/api/videos", headers=self.headers)

    @task(3)
    def view_video_details(self):
        video_id = random.randint(1, 100)
        self.client.get(f"/api/videos/{video_id}", headers=self.headers)

    @task(2)
    def check_vocabulary(self):
        self.client.get("/api/vocabulary", headers=self.headers)

    @task(1)
    def update_progress(self):
        self.client.post("/api/progress", json={
            "video_id": random.randint(1, 100),
            "chunk_index": random.randint(0, 20),
            "score": random.uniform(0.5, 1.0)
        }, headers=self.headers)
```

**Acceptance Criteria:**

- P95 response time < 200ms for read operations
- P95 response time < 500ms for write operations
- 0% error rate
- CPU usage < 50%
- Memory growth < 10% over test duration

#### Scenario 2: Peak Traffic Load

**Profile:**

- 500 concurrent users
- 10-minute test duration
- Gradual ramp-up (50 users/minute)

**User Behavior:**

- Same as Scenario 1, but with higher concurrency

**Acceptance Criteria:**

- P95 response time < 500ms for read operations
- P95 response time < 1000ms for write operations
- Error rate < 1%
- CPU usage < 80%
- No memory leaks

#### Scenario 3: Spike Test (Burst Traffic)

**Profile:**

- Sudden spike from 50 to 1000 users in 30 seconds
- Sustained for 5 minutes
- Gradual ramp-down

**User Behavior:**

- Heavy read operations (video browsing)

**Acceptance Criteria:**

- System remains responsive during spike
- No cascading failures
- Graceful degradation if capacity exceeded
- Recovery within 2 minutes after spike ends

#### Scenario 4: Video Processing Load

**Profile:**

- 10 concurrent video uploads
- Each video 5-10 minutes long
- Mixed transcription + translation requests

**User Behavior:**

```python
class VideoProcessingUser(HttpUser):
    @task
    def upload_and_process_video(self):
        # Upload video
        with open("test_video.mp4", "rb") as f:
            response = self.client.post(
                "/api/videos/upload",
                files={"file": f},
                headers=self.headers
            )

        video_id = response.json()["id"]

        # Request transcription
        self.client.post(f"/api/process/{video_id}/transcribe", headers=self.headers)

        # Poll for completion
        while True:
            status = self.client.get(f"/api/process/{video_id}/status", headers=self.headers)
            if status.json()["status"] == "completed":
                break
            time.sleep(5)
```

**Acceptance Criteria:**

- All videos processed within 2x video duration
- No processing failures
- Queue management works correctly
- Resource usage within limits

#### Scenario 5: Database Stress Test

**Profile:**

- Heavy read/write operations on vocabulary
- 200 concurrent users
- Each user performs 100 vocabulary operations

**User Behavior:**

```python
class DatabaseStressUser(HttpUser):
    @task(5)
    def search_vocabulary(self):
        self.client.get(
            "/api/vocabulary/search",
            params={"q": random.choice(["test", "der", "haben", "sein"])},
            headers=self.headers
        )

    @task(3)
    def add_vocabulary(self):
        self.client.post("/api/vocabulary", json={
            "word": f"word_{random.randint(1, 10000)}",
            "translation": "translation",
            "context": "example context"
        }, headers=self.headers)

    @task(2)
    def update_vocabulary_status(self):
        word_id = random.randint(1, 1000)
        self.client.patch(f"/api/vocabulary/{word_id}", json={
            "mastery_level": random.randint(1, 5)
        }, headers=self.headers)
```

**Acceptance Criteria:**

- Database connection pool never exhausted
- Query response time < 50ms (p95)
- No deadlocks or lock timeouts
- Transaction rollback rate < 0.1%

### 3.2 Frontend Performance Scenarios

#### Scenario 1: Initial Page Load

**Profile:**

- Cold cache (first visit)
- Desktop and mobile

**Metrics:**

- FCP, LCP, TTI, TBT, CLS
- Bundle download time
- Time to first API call

**Test Script:**

```javascript
// Frontend/tests/performance/page-load.spec.ts
import { test, expect } from "@playwright/test";

test("measure initial page load performance", async ({ page }) => {
  const metrics = await page.evaluate(() => {
    const perfData = window.performance.getEntriesByType("navigation")[0];
    return {
      domContentLoaded: perfData.domContentLoadedEventEnd - perfData.fetchStart,
      loadComplete: perfData.loadEventEnd - perfData.fetchStart,
      firstPaint: performance
        .getEntriesByType("paint")
        .find((e) => e.name === "first-paint")?.startTime,
    };
  });

  console.log(metrics);
  expect(metrics.domContentLoaded).toBeLessThan(3000);
});
```

#### Scenario 2: Video Player Interaction

**Profile:**

- Playing video with subtitles
- Vocabulary overlay interactions
- Chunk transitions

**Metrics:**

- Subtitle rendering latency
- Frame drops
- Memory consumption over time

**Test Script:**

```javascript
test("video player performance", async ({ page }) => {
  await page.goto("http://localhost:3000/player/video-1");

  // Start performance monitoring
  await page.evaluate(() => {
    window.performanceMarks = [];
    window.addEventListener("subtitle-render", (e) => {
      window.performanceMarks.push({
        type: "subtitle",
        timestamp: performance.now(),
      });
    });
  });

  // Play video for 2 minutes
  await page.click('[data-testid="play-button"]');
  await page.waitForTimeout(120000);

  const marks = await page.evaluate(() => window.performanceMarks);
  console.log(`Subtitle renders: ${marks.length}`);
});
```

#### Scenario 3: Navigation and State Management

**Profile:**

- Navigating between pages
- State persistence
- API caching effectiveness

**Metrics:**

- Route transition time
- State hydration time
- Cache hit rate

### 3.3 AI Model Performance Scenarios

#### Scenario 1: Transcription Benchmarks

**Small Model (whisper-tiny):**

```python
# Backend/tests/performance/test_transcription.py
import pytest
import time
from services.transcriptionservice import get_service

def test_whisper_tiny_performance():
    service = get_service("whisper-tiny")

    # 5-minute audio file
    audio_path = "test_audio_5min.wav"

    start = time.time()
    result = service.transcribe(audio_path)
    duration = time.time() - start

    # Should process faster than real-time
    assert duration < 300  # 5 minutes
    assert len(result.segments) > 0
```

**Large Model (whisper-medium):**

```python
def test_whisper_medium_performance():
    service = get_service("whisper-medium")

    audio_path = "test_audio_5min.wav"

    start = time.time()
    result = service.transcribe(audio_path)
    duration = time.time() - start

    # May take longer, but should be < 2x real-time
    assert duration < 600  # 10 minutes
```

#### Scenario 2: Translation Benchmarks

**Batch Translation:**

```python
def test_translation_batch_performance():
    service = get_service("opus-de-es")

    # 100 subtitle segments
    segments = ["Test sentence " + str(i) for i in range(100)]

    start = time.time()
    results = service.translate_batch(segments)
    duration = time.time() - start

    # Should process 100 segments in < 10 seconds
    assert duration < 10
    assert len(results) == 100
```

#### Scenario 3: Multi-Model Load

**Concurrent Model Usage:**

```python
def test_concurrent_model_load():
    import asyncio

    async def process_video():
        transcription = await transcribe_async("audio.wav")
        translation = await translate_async(transcription)
        vocabulary = await extract_vocabulary_async(transcription)
        return transcription, translation, vocabulary

    start = time.time()
    results = asyncio.run(process_video())
    duration = time.time() - start

    # All three models should complete in reasonable time
    assert duration < 60  # 1 minute for short video
```

---

## 4. Baseline Measurements

### 4.1 Current System Specifications

**Development Environment:**

- OS: Windows 11 / WSL2
- CPU: (To be documented)
- RAM: (To be documented)
- GPU: (To be documented if available)
- Storage: SSD / HDD (To be documented)

**Backend Stack:**

- Python 3.11+
- FastAPI
- SQLite (dev) / PostgreSQL (prod)
- Uvicorn ASGI server

**Frontend Stack:**

- React 18
- Vite 4
- TypeScript 5
- Styled Components

**AI Models:**

- Whisper (tiny/base/small/medium)
- Opus-MT (de-es)
- SpaCy (de_core_news_lg, en_core_web_sm)

### 4.2 Baseline Measurement Procedure

#### Step 1: Backend API Baseline

```bash
# Start backend
cd Backend
powershell.exe -Command ". api_venv/Scripts/activate; uvicorn core.app:app --host 0.0.0.0 --port 8000"

# Run Locust baseline test (100 users, 5 minutes)
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 --run-time 5m --headless \
       --csv=results/baseline_100users
```

**Record:**

- P50, P95, P99 response times per endpoint
- RPS (requests per second)
- Error rate
- CPU/Memory usage

#### Step 2: Frontend Baseline

```bash
# Build production bundle
cd Frontend
npm run build

# Measure bundle sizes
du -h dist/*.js

# Run Lighthouse
lighthouse http://localhost:3000 --output html --output-path reports/baseline-lighthouse.html
```

**Record:**

- FCP, LCP, TTI, TBT, CLS scores
- Bundle sizes (gzipped)
- Lighthouse performance score

#### Step 3: Database Baseline

```bash
# Run database benchmark
cd Backend
python tests/performance/db_baseline.py
```

**Record:**

- Query execution times for common patterns
- Connection pool utilization
- Transaction throughput

#### Step 4: AI Model Baseline

```bash
# Run AI model benchmarks
cd Backend
python tests/performance/ai_baseline.py
```

**Record:**

- Model loading times
- Inference latency per minute of audio
- GPU/CPU utilization
- Memory consumption

### 4.3 Baseline Results Template

**Create baseline results document:**

```markdown
# Baseline Performance Results - [Date]

## Backend API

- **Test Duration:** 5 minutes
- **Concurrent Users:** 100
- **Total Requests:** X
- **RPS:** Y req/s

### Response Times

| Endpoint             | P50 | P95 | P99 |
| -------------------- | --- | --- | --- |
| GET /api/videos      | Xms | Yms | Zms |
| POST /api/auth/login | Xms | Yms | Zms |
| GET /api/vocabulary  | Xms | Yms | Zms |

### Resource Usage

- **CPU:** X% (mean), Y% (peak)
- **Memory:** XMB (baseline), YMB (peak)
- **Network:** XMB/s

## Frontend

### Bundle Sizes

- Main bundle: XKB (gzipped)
- Vendor bundle: YKB (gzipped)
- Total: ZKB (gzipped)

### Web Vitals

- FCP: Xms
- LCP: Yms
- TTI: Zms
- TBT: Xms
- CLS: X.XX

### Lighthouse Score

- Performance: X/100
- Accessibility: Y/100
- Best Practices: Z/100

## Database

- Query execution (simple SELECT): Xms
- Query execution (complex JOIN): Yms
- Connection pool usage: X/Y connections

## AI Models

- Whisper-tiny load time: Xs
- Whisper-tiny inference: Xs per audio minute
- Translation latency: Xms per segment
- SpaCy processing: Xms per document
```

---

## 5. Performance Targets

### 5.1 Backend API Targets

| Metric                  | Good    | Acceptable | Poor     |
| ----------------------- | ------- | ---------- | -------- |
| **Authentication**      |
| Login (P95)             | < 100ms | < 200ms    | > 200ms  |
| Token refresh (P95)     | < 50ms  | < 100ms    | > 100ms  |
| **Video Operations**    |
| List videos (P95)       | < 100ms | < 200ms    | > 200ms  |
| Get video details (P95) | < 50ms  | < 100ms    | > 100ms  |
| Upload video (per MB)   | < 500ms | < 1000ms   | > 1000ms |
| **Vocabulary**          |
| Get vocabulary (P95)    | < 100ms | < 200ms    | > 200ms  |
| Search vocabulary (P95) | < 150ms | < 300ms    | > 300ms  |
| Add word (P95)          | < 100ms | < 200ms    | > 200ms  |
| **Processing**          |
| Submit job (P95)        | < 100ms | < 200ms    | > 200ms  |
| Check status (P95)      | < 50ms  | < 100ms    | > 100ms  |

**Throughput Targets:**

- Minimum: 100 RPS
- Target: 500 RPS
- Stretch: 1000 RPS

**Concurrent Users:**

- Minimum: 100 users
- Target: 500 users
- Stretch: 1000 users

### 5.2 Frontend Targets

**Web Vitals (Desktop):**
| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| FCP | < 1.0s | < 2.5s | > 2.5s |
| LCP | < 2.0s | < 3.5s | > 3.5s |
| TTI | < 3.0s | < 6.0s | > 6.0s |
| TBT | < 200ms | < 500ms | > 500ms |
| CLS | < 0.1 | < 0.25 | > 0.25 |

**Web Vitals (Mobile):**
| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| FCP | < 1.5s | < 3.0s | > 3.0s |
| LCP | < 2.5s | < 4.0s | > 4.0s |
| TTI | < 4.0s | < 7.5s | > 7.5s |
| TBT | < 300ms | < 600ms | > 600ms |
| CLS | < 0.1 | < 0.25 | > 0.25 |

**Bundle Size Targets:**

- Main bundle: < 200KB gzipped
- Vendor bundle: < 300KB gzipped
- Total JS: < 500KB gzipped
- Total assets (including images/fonts): < 2MB

**Lighthouse Scores:**

- Performance: > 90
- Accessibility: > 90
- Best Practices: > 90

### 5.3 Database Targets

| Query Type                | Target P95 |
| ------------------------- | ---------- |
| Simple SELECT (indexed)   | < 10ms     |
| Complex JOIN (2-3 tables) | < 50ms     |
| Aggregation               | < 100ms    |
| Full-text search          | < 200ms    |
| Write operations          | < 20ms     |

**Connection Pool:**

- Pool size: 10 connections (configurable)
- Max overflow: 20 connections
- Connection wait time: < 100ms
- Pool saturation: < 80%

### 5.4 AI Model Targets

**Transcription (Whisper):**
| Model | Load Time | Inference (per min audio) |
|-------|-----------|---------------------------|
| whisper-tiny | < 2s | < 30s (2x real-time) |
| whisper-base | < 5s | < 60s (1x real-time) |
| whisper-small | < 10s | < 120s (0.5x real-time) |
| whisper-medium | < 15s | < 240s (0.25x real-time) |

**Translation (Opus-MT / NLLB):**

- Model load time: < 5s
- Single segment (10-20 words): < 100ms
- Batch (100 segments): < 5s

**Vocabulary Extraction (SpaCy):**

- Model load time: < 2s
- Per subtitle segment: < 50ms
- Full document (500 segments): < 10s

### 5.5 End-to-End User Experience Targets

**Video Upload to Processing:**

- Upload 100MB video: < 2 minutes
- Transcription (5min video): < 10 minutes
- Translation: < 2 minutes
- Vocabulary extraction: < 1 minute
- Total processing time: < 15 minutes

**Learning Session:**

- Navigate to video player: < 2s
- Load video with subtitles: < 3s
- Subtitle rendering latency: < 50ms
- Vocabulary lookup: < 200ms
- Progress save: < 100ms

---

## 6. Continuous Performance Testing

### 6.1 CI/CD Integration

#### GitHub Actions Performance Workflow

**File:** `.github/workflows/performance.yml`

```yaml
name: Performance Tests

on:
  pull_request:
    branches: [main, master]
  schedule:
    # Run nightly at 2 AM UTC
    - cron: "0 2 * * *"
  workflow_dispatch:

jobs:
  backend-performance:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          cd Backend
          pip install -r requirements.txt
          pip install locust

      - name: Start backend server
        run: |
          cd Backend
          uvicorn core.app:app --host 0.0.0.0 --port 8000 &
          sleep 10

      - name: Run Locust performance test
        run: |
          cd Backend
          locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
                 --users 50 --spawn-rate 5 --run-time 2m --headless \
                 --csv=results/ci_performance

      - name: Check performance thresholds
        run: |
          cd Backend
          python tests/performance/check_thresholds.py results/ci_performance_stats.csv

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: Backend/results/

  frontend-performance:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install dependencies
        run: |
          cd Frontend
          npm ci

      - name: Build frontend
        run: |
          cd Frontend
          npm run build

      - name: Serve frontend
        run: |
          cd Frontend
          npx serve -s dist -l 3000 &
          sleep 5

      - name: Run Lighthouse
        run: |
          npm install -g lighthouse
          lighthouse http://localhost:3000 --output json --output-path lighthouse-results.json

      - name: Check Lighthouse thresholds
        run: |
          node Frontend/scripts/check-lighthouse-thresholds.js lighthouse-results.json

      - name: Upload Lighthouse results
        uses: actions/upload-artifact@v3
        with:
          name: lighthouse-results
          path: lighthouse-results.json
```

#### Threshold Checking Script

**File:** `Backend/tests/performance/check_thresholds.py`

```python
import sys
import csv

THRESHOLDS = {
    'P95_response_time': 500,  # ms
    'P99_response_time': 1000,  # ms
    'error_rate': 0.01,  # 1%
}

def check_thresholds(csv_path):
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        stats = list(reader)[0]  # Locust summary row

    failures = []

    # Check P95
    p95 = float(stats.get('95%', 0))
    if p95 > THRESHOLDS['P95_response_time']:
        failures.append(f"P95 response time {p95}ms exceeds threshold {THRESHOLDS['P95_response_time']}ms")

    # Check P99
    p99 = float(stats.get('99%', 0))
    if p99 > THRESHOLDS['P99_response_time']:
        failures.append(f"P99 response time {p99}ms exceeds threshold {THRESHOLDS['P99_response_time']}ms")

    # Check error rate
    total_requests = int(stats.get('Request Count', 0))
    failures_count = int(stats.get('Failure Count', 0))
    error_rate = failures_count / total_requests if total_requests > 0 else 0

    if error_rate > THRESHOLDS['error_rate']:
        failures.append(f"Error rate {error_rate:.2%} exceeds threshold {THRESHOLDS['error_rate']:.2%}")

    if failures:
        print("Performance test failures:")
        for failure in failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print("All performance thresholds passed!")

if __name__ == '__main__':
    check_thresholds(sys.argv[1])
```

**File:** `Frontend/scripts/check-lighthouse-thresholds.js`

```javascript
const fs = require("fs");

const THRESHOLDS = {
  performance: 80,
  accessibility: 90,
  "best-practices": 90,
};

function checkLighthouse(filePath) {
  const results = JSON.parse(fs.readFileSync(filePath, "utf8"));
  const categories = results.lhr.categories;

  const failures = [];

  for (const [category, threshold] of Object.entries(THRESHOLDS)) {
    const score = categories[category].score * 100;
    if (score < threshold) {
      failures.push(`${category}: ${score} < ${threshold}`);
    }
  }

  if (failures.length > 0) {
    console.error("Lighthouse thresholds failed:");
    failures.forEach((f) => console.error(`  - ${f}`));
    process.exit(1);
  } else {
    console.log("All Lighthouse thresholds passed!");
  }
}

checkLighthouse(process.argv[2]);
```

### 6.2 Automated Performance Regression Detection

#### Performance History Tracking

**Storage:**

- Store performance results in JSON format
- Track trends over time
- Compare against baseline

**File:** `scripts/performance-tracking.py`

```python
import json
import datetime
from pathlib import Path

HISTORY_FILE = Path("performance_history.json")

def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []

def save_result(result):
    history = load_history()

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "results": result
    }

    history.append(entry)

    # Keep last 100 results
    history = history[-100:]

    HISTORY_FILE.write_text(json.dumps(history, indent=2))

def check_regression(current_result):
    history = load_history()
    if len(history) < 5:
        print("Not enough history for regression detection")
        return False

    # Compare against last 5 results
    recent = history[-5:]
    avg_p95 = sum(r["results"]["p95"] for r in recent) / len(recent)

    # Regression if current is 20% worse than average
    if current_result["p95"] > avg_p95 * 1.2:
        print(f"Performance regression detected!")
        print(f"Current P95: {current_result['p95']}ms")
        print(f"Recent average: {avg_p95}ms")
        return True

    return False
```

### 6.3 Performance Dashboards

#### Grafana Dashboard Configuration

**File:** `grafana/dashboards/langplug-performance.json`

```json
{
  "dashboard": {
    "title": "LangPlug Performance",
    "panels": [
      {
        "title": "API Response Time (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(langplug_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Requests per Second",
        "targets": [
          {
            "expr": "rate(langplug_requests_total[1m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(langplug_requests_total{status=~\"5..\"}[5m]) / rate(langplug_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Active Users",
        "targets": [
          {
            "expr": "langplug_active_users"
          }
        ]
      },
      {
        "title": "Transcription Queue Size",
        "targets": [
          {
            "expr": "langplug_transcription_queue_size"
          }
        ]
      }
    ]
  }
}
```

### 6.4 Alert Configuration

**File:** `prometheus/alerts.yml`

```yaml
groups:
  - name: langplug_performance
    interval: 30s
    rules:
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(langplug_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API response time"
          description: "P95 response time is {{ $value }}s"

      - alert: HighErrorRate
        expr: rate(langplug_requests_total{status=~"5.."}[5m]) / rate(langplug_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: QueueBacklog
        expr: langplug_transcription_queue_size > 20
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Transcription queue backlog"
          description: "Queue size is {{ $value }}"
```

---

## 7. Optimization Strategies

### 7.1 Backend Optimizations

#### Quick Wins (1-2 weeks)

**1. Database Query Optimization**

- Add missing indexes
- Optimize N+1 queries
- Use SELECT only needed columns

```python
# Before (N+1 query)
def get_videos_with_users():
    videos = db.query(Video).all()
    for video in videos:
        user = db.query(User).filter(User.id == video.user_id).first()
        video.user = user
    return videos

# After (JOIN)
def get_videos_with_users():
    return db.query(Video).join(User).all()
```

**2. Response Caching**

- Implement Redis caching for frequently accessed data
- Cache video metadata, user vocabulary lists

```python
# Example caching decorator
from functools import wraps
import redis

redis_client = redis.Redis()

def cached(ttl=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached_result = redis_client.get(cache_key)

            if cached_result:
                return json.loads(cached_result)

            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result

        return wrapper
    return decorator

@cached(ttl=1800)
async def get_video_metadata(video_id):
    return db.query(Video).filter(Video.id == video_id).first()
```

**3. Async I/O for External Calls**

- Ensure all I/O operations are async
- Use `asyncio.gather` for parallel operations

```python
# Before (sequential)
def process_video(video_id):
    transcription = transcribe(video_id)
    translation = translate(transcription)
    vocabulary = extract_vocabulary(translation)
    return vocabulary

# After (parallel)
async def process_video(video_id):
    transcription = await transcribe_async(video_id)

    # Run translation and vocabulary extraction in parallel
    translation, vocabulary = await asyncio.gather(
        translate_async(transcription),
        extract_vocabulary_async(transcription)
    )

    return vocabulary
```

**4. Response Compression**

- Enable gzip compression for API responses

```python
# FastAPI middleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**5. Database Connection Pooling**

- Tune pool size based on load
- Monitor pool saturation

```python
# Core/database.py
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,  # Increase from default 10
    max_overflow=30,  # Increase from default 10
    pool_pre_ping=True,  # Verify connections
    pool_recycle=3600  # Recycle connections after 1 hour
)
```

#### Medium-Term Optimizations (1-2 months)

**1. Background Job Processing**

- Move heavy processing to background workers
- Use Celery or RQ for task queue

```python
# Using Celery
from celery import Celery

celery_app = Celery('langplug', broker='redis://localhost:6379/0')

@celery_app.task
def transcribe_video_task(video_id):
    # Heavy processing here
    pass

# API endpoint just enqueues task
@app.post("/api/process/{video_id}/transcribe")
async def transcribe_video(video_id: int):
    task = transcribe_video_task.delay(video_id)
    return {"task_id": task.id, "status": "queued"}
```

**2. CDN for Static Assets**

- Serve video files from CDN
- Offload bandwidth from application server

**3. Database Read Replicas**

- Separate read and write operations
- Route read-heavy queries to replicas

**4. API Rate Limiting**

- Protect against abuse
- Ensure fair resource allocation

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/videos")
@limiter.limit("100/minute")
async def get_videos(request: Request):
    pass
```

#### Long-Term Optimizations (3-6 months)

**1. Horizontal Scaling**

- Deploy multiple backend instances
- Load balancer (nginx, HAProxy)
- Session persistence (Redis)

**2. Database Sharding**

- Partition data by user ID or video ID
- Distribute load across multiple databases

**3. Microservices Architecture**

- Separate transcription service
- Separate translation service
- Independent scaling

**4. Model Serving Optimization**

- Model quantization (reduce size)
- TensorRT or ONNX optimization
- Dedicated inference server (Triton, TorchServe)

### 7.2 Frontend Optimizations

#### Quick Wins (1-2 weeks)

**1. Code Splitting**

```typescript
// Lazy load routes
import { lazy, Suspense } from 'react';

const VideoPlayer = lazy(() => import('./components/VideoPlayer'));
const VocabularyLibrary = lazy(() => import('./components/VocabularyLibrary'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/player/:id" element={<VideoPlayer />} />
        <Route path="/vocabulary" element={<VocabularyLibrary />} />
      </Routes>
    </Suspense>
  );
}
```

**2. Image Optimization**

- Use WebP format
- Responsive images
- Lazy loading

```typescript
<img
  src={`/images/${videoId}.webp`}
  srcSet={`/images/${videoId}-480w.webp 480w, /images/${videoId}-800w.webp 800w`}
  sizes="(max-width: 600px) 480px, 800px"
  loading="lazy"
  alt={videoTitle}
/>
```

**3. Memoization**

```typescript
import { useMemo, useCallback } from 'react';

function VideoList({ videos, filter }) {
  const filteredVideos = useMemo(() => {
    return videos.filter(v => v.title.includes(filter));
  }, [videos, filter]);

  const handleClick = useCallback((videoId) => {
    navigate(`/player/${videoId}`);
  }, [navigate]);

  return filteredVideos.map(v => (
    <VideoCard key={v.id} video={v} onClick={handleClick} />
  ));
}
```

**4. API Request Caching**

```typescript
// Using React Query
import { useQuery } from "@tanstack/react-query";

function useVideos() {
  return useQuery({
    queryKey: ["videos"],
    queryFn: fetchVideos,
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
}
```

**5. Bundle Size Reduction**

- Remove unused dependencies
- Tree-shaking configuration
- Dynamic imports

```typescript
// Before
import { Button, Input, Card, Modal, Dropdown } from "ui-library";

// After (tree-shakeable)
import Button from "ui-library/Button";
import Input from "ui-library/Input";
```

#### Medium-Term Optimizations (1-2 months)

**1. Service Worker for Offline Support**

```typescript
// serviceWorker.ts
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open("langplug-v1").then((cache) => {
      return cache.addAll(["/", "/static/js/main.js", "/static/css/main.css"]);
    }),
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    }),
  );
});
```

**2. Virtual Scrolling for Long Lists**

```typescript
import { FixedSizeList } from 'react-window';

function VocabularyList({ words }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={words.length}
      itemSize={50}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>
          <VocabularyWord word={words[index]} />
        </div>
      )}
    </FixedSizeList>
  );
}
```

**3. Prefetching**

```typescript
// Prefetch next video when hovering
function VideoCard({ video }) {
  const prefetchVideo = useCallback(() => {
    queryClient.prefetchQuery(['video', video.id], () => fetchVideo(video.id));
  }, [video.id]);

  return (
    <div onMouseEnter={prefetchVideo}>
      {/* ... */}
    </div>
  );
}
```

**4. Web Workers for Heavy Computation**

```typescript
// subtitleParser.worker.ts
self.onmessage = (e) => {
  const { srtContent } = e.data;
  const parsed = parseSRT(srtContent);
  self.postMessage(parsed);
};

// Usage
const worker = new Worker(
  new URL("./subtitleParser.worker.ts", import.meta.url),
);
worker.postMessage({ srtContent });
worker.onmessage = (e) => {
  setParsedSubtitles(e.data);
};
```

#### Long-Term Optimizations (3-6 months)

**1. Progressive Web App (PWA)**

- Full offline support
- Install to home screen
- Background sync

**2. Server-Side Rendering (SSR) / Static Generation**

- Next.js migration
- Improved SEO
- Faster initial load

**3. Edge Computing**

- Deploy to edge locations (Cloudflare Workers, Vercel Edge)
- Reduced latency for global users

### 7.3 Database Optimizations

#### Indexing Strategy

**Identify Missing Indexes:**

```sql
-- PostgreSQL: Find sequential scans
SELECT schemaname, tablename, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 20;

-- Create composite indexes
CREATE INDEX idx_vocabulary_user_word ON vocabulary(user_id, word);
CREATE INDEX idx_videos_status_created ON videos(status, created_at DESC);
CREATE INDEX idx_progress_user_video ON progress(user_id, video_id);
```

**Full-Text Search Optimization:**

```sql
-- PostgreSQL full-text search
CREATE INDEX idx_vocabulary_word_search ON vocabulary USING GIN(to_tsvector('german', word));

-- Query using index
SELECT * FROM vocabulary
WHERE to_tsvector('german', word) @@ to_tsquery('german', 'haben');
```

#### Query Optimization

**Use EXPLAIN ANALYZE:**

```sql
EXPLAIN ANALYZE
SELECT v.*, u.username
FROM videos v
JOIN users u ON v.user_id = u.id
WHERE v.status = 'processed'
ORDER BY v.created_at DESC
LIMIT 20;
```

**Optimize Pagination:**

```sql
-- Avoid OFFSET for large offsets (slow)
SELECT * FROM videos ORDER BY id LIMIT 20 OFFSET 10000;

-- Use cursor-based pagination (fast)
SELECT * FROM videos WHERE id > 10000 ORDER BY id LIMIT 20;
```

#### Connection Pooling

**PgBouncer for PostgreSQL:**

```ini
# pgbouncer.ini
[databases]
langplug = host=localhost port=5432 dbname=langplug

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

### 7.4 AI Model Optimizations

#### Model Quantization

**PyTorch Quantization:**

```python
import torch

# Load model
model = WhisperModel.from_pretrained("whisper-base")

# Quantize to INT8
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)

# Save quantized model
torch.save(quantized_model.state_dict(), "whisper_quantized.pth")
```

#### Batch Processing

**Batch Transcription:**

```python
def transcribe_batch(audio_files):
    # Load model once
    model = load_whisper_model()

    results = []
    for audio_file in audio_files:
        result = model.transcribe(audio_file)
        results.append(result)

    return results
```

#### Model Caching

**Persistent Model Loading:**

```python
_model_cache = {}

def get_model(model_name):
    if model_name not in _model_cache:
        _model_cache[model_name] = load_model(model_name)
    return _model_cache[model_name]
```

#### GPU Optimization

**CUDA Stream Processing:**

```python
import torch

# Enable TF32 for Ampere GPUs
torch.backends.cuda.matmul.allow_tf32 = True

# Use multiple CUDA streams
stream1 = torch.cuda.Stream()
stream2 = torch.cuda.Stream()

with torch.cuda.stream(stream1):
    result1 = model.transcribe(audio1)

with torch.cuda.stream(stream2):
    result2 = model.transcribe(audio2)
```

---

## 8. Implementation Timeline

### Phase 1: Baseline and Setup (Week 1-2)

**Week 1:**

- [ ] Set up Locust for backend load testing
- [ ] Install Lighthouse and WebPageTest tools
- [ ] Configure Prometheus + Grafana
- [ ] Document current system specifications

**Week 2:**

- [ ] Run baseline backend tests (100 users)
- [ ] Run baseline frontend tests (Lighthouse)
- [ ] Run baseline database tests
- [ ] Run baseline AI model tests
- [ ] Document baseline results

**Deliverables:**

- Baseline performance report
- Monitoring dashboards configured

### Phase 2: Quick Wins (Week 3-4)

**Backend:**

- [ ] Add database indexes
- [ ] Implement Redis caching
- [ ] Enable response compression
- [ ] Optimize N+1 queries

**Frontend:**

- [ ] Implement code splitting
- [ ] Optimize images (WebP, lazy loading)
- [ ] Add React Query caching
- [ ] Memoize expensive components

**Expected Improvements:**

- Backend P95 response time: -20%
- Frontend LCP: -30%
- Database query time: -40%

### Phase 3: CI/CD Integration (Week 5-6)

**Week 5:**

- [ ] Create GitHub Actions workflow for backend performance
- [ ] Create GitHub Actions workflow for frontend performance
- [ ] Implement threshold checking scripts
- [ ] Set up performance history tracking

**Week 6:**

- [ ] Configure alerts in Prometheus
- [ ] Create performance regression detection
- [ ] Document CI/CD process
- [ ] Train team on performance testing

**Deliverables:**

- Automated performance tests in CI/CD
- Alert system operational

### Phase 4: Medium-Term Optimizations (Week 7-12)

**Backend:**

- [ ] Implement background job processing (Celery)
- [ ] Set up CDN for video files
- [ ] Implement API rate limiting
- [ ] Optimize database connection pooling

**Frontend:**

- [ ] Implement service worker
- [ ] Add virtual scrolling for long lists
- [ ] Implement prefetching
- [ ] Create web workers for heavy computation

**AI Models:**

- [ ] Implement model quantization
- [ ] Optimize batch processing
- [ ] Implement model caching

**Expected Improvements:**

- Backend throughput: +50%
- Frontend TTI: -40%
- AI inference time: -30%

### Phase 5: Long-Term Architecture (Month 4-6)

**Infrastructure:**

- [ ] Set up horizontal scaling (multiple backend instances)
- [ ] Implement load balancing
- [ ] Set up database read replicas
- [ ] Deploy to edge locations

**Advanced Optimizations:**

- [ ] Migrate to microservices (optional)
- [ ] Implement database sharding (if needed)
- [ ] Deploy dedicated model inference servers
- [ ] Migrate to SSR/SSG (Next.js) (optional)

**Expected Improvements:**

- System capacity: +200%
- Global latency: -50%
- AI model throughput: +100%

---

## 9. Appendices

### Appendix A: Glossary

**Backend Terms:**

- **P50/P95/P99:** Percentile metrics (50th, 95th, 99th percentile)
- **RPS:** Requests Per Second
- **TPS:** Transactions Per Second
- **Latency:** Time between request and response
- **Throughput:** Number of operations per unit time

**Frontend Terms:**

- **FCP:** First Contentful Paint
- **LCP:** Largest Contentful Paint
- **TTI:** Time to Interactive
- **TBT:** Total Blocking Time
- **CLS:** Cumulative Layout Shift

**Database Terms:**

- **Query Plan:** Execution strategy for a query
- **Index:** Data structure for fast lookups
- **Connection Pool:** Reusable database connections
- **Sharding:** Horizontal data partitioning

**AI/ML Terms:**

- **Inference:** Running model on new data
- **Quantization:** Reducing model precision (FP32 → INT8)
- **Batching:** Processing multiple inputs together
- **VRAM:** Video RAM (GPU memory)

### Appendix B: Tool References

**Backend Load Testing:**

- Locust: https://locust.io/
- Apache Bench: https://httpd.apache.org/docs/2.4/programs/ab.html
- k6: https://k6.io/

**Frontend Performance:**

- Lighthouse: https://developers.google.com/web/tools/lighthouse
- WebPageTest: https://www.webpagetest.org/
- Bundle Analyzer: https://www.npmjs.com/package/webpack-bundle-analyzer

**Monitoring:**

- Prometheus: https://prometheus.io/
- Grafana: https://grafana.com/
- Sentry: https://sentry.io/

**Database:**

- pgBench: https://www.postgresql.org/docs/current/pgbench.html
- pg_stat_statements: https://www.postgresql.org/docs/current/pgstatstatements.html

**AI/ML:**

- PyTorch Profiler: https://pytorch.org/tutorials/intermediate/tensorboard_profiler_tutorial.html
- Memory Profiler: https://pypi.org/project/memory-profiler/
- TensorRT: https://developer.nvidia.com/tensorrt

### Appendix C: Sample Reports

#### Backend Performance Report Template

```markdown
# Backend Performance Test Report

**Date:** YYYY-MM-DD
**Test Duration:** 5 minutes
**Concurrent Users:** 100
**Environment:** Development / Staging / Production

## Summary

- Total Requests: X
- Successful Requests: Y (Z%)
- Failed Requests: A (B%)
- Requests per Second: C

## Response Times

| Endpoint             | P50 | P95 | P99 | Min | Max |
| -------------------- | --- | --- | --- | --- | --- |
| GET /api/videos      | Xms | Yms | Zms | Ams | Bms |
| POST /api/auth/login | Xms | Yms | Zms | Ams | Bms |
| GET /api/vocabulary  | Xms | Yms | Zms | Ams | Bms |

## Resource Utilization

- CPU Usage: X% (mean), Y% (peak)
- Memory Usage: XMB (baseline), YMB (peak)
- Network Throughput: XMB/s

## Errors

[List any errors encountered]

## Bottlenecks Identified

1. [Issue description]
2. [Issue description]

## Recommendations

1. [Optimization suggestion]
2. [Optimization suggestion]
```

#### Frontend Performance Report Template

```markdown
# Frontend Performance Test Report

**Date:** YYYY-MM-DD
**URL:** http://localhost:3000
**Device:** Desktop / Mobile
**Network:** Fast 3G / 4G / WiFi

## Lighthouse Scores

- Performance: X/100
- Accessibility: Y/100
- Best Practices: Z/100
- SEO: A/100

## Web Vitals

- First Contentful Paint: Xms
- Largest Contentful Paint: Yms
- Time to Interactive: Zms
- Total Blocking Time: Ams
- Cumulative Layout Shift: X.XX

## Bundle Sizes

- Main bundle: XKB (gzipped)
- Vendor bundle: YKB (gzipped)
- Total JavaScript: ZKB (gzipped)
- Total Assets: AMB

## Issues Identified

1. [Performance issue]
2. [Performance issue]

## Recommendations

1. [Optimization suggestion]
2. [Optimization suggestion]
```

### Appendix D: Performance Best Practices Checklist

#### Backend Best Practices

- [ ] All database queries use appropriate indexes
- [ ] N+1 queries are eliminated
- [ ] Response caching is implemented where appropriate
- [ ] Connection pooling is configured optimally
- [ ] Heavy operations are moved to background jobs
- [ ] API responses use compression (gzip)
- [ ] Rate limiting is implemented
- [ ] Logging doesn't impact performance
- [ ] Database transactions are kept short
- [ ] Async I/O is used for all blocking operations

#### Frontend Best Practices

- [ ] Code splitting is implemented
- [ ] Images are optimized (WebP, responsive, lazy loading)
- [ ] Expensive computations are memoized
- [ ] API calls are cached (React Query)
- [ ] Bundle sizes are minimized
- [ ] Service worker for offline support
- [ ] Virtual scrolling for long lists
- [ ] Prefetching for anticipated navigation
- [ ] Web workers for heavy computation
- [ ] Fonts are loaded optimally

#### Database Best Practices

- [ ] Indexes exist for frequently queried columns
- [ ] Composite indexes for multi-column queries
- [ ] Full-text search uses GIN indexes (PostgreSQL)
- [ ] Pagination uses cursor-based approach
- [ ] Queries select only needed columns
- [ ] Transactions are as short as possible
- [ ] Connection pool is sized appropriately
- [ ] Query plans are analyzed regularly
- [ ] Database statistics are up to date
- [ ] Slow query log is monitored

#### AI Model Best Practices

- [ ] Models are loaded once and cached
- [ ] Batch processing is used where possible
- [ ] Models are quantized for faster inference
- [ ] GPU is utilized if available
- [ ] CUDA streams for parallel processing
- [ ] Model serving is separated from API
- [ ] Inference results are cached
- [ ] Model versions are tracked
- [ ] Memory usage is monitored
- [ ] Fallback to CPU if GPU unavailable

### Appendix E: Contact and Escalation

**Performance Issues:**

- Severity 1 (Critical): System down or unusable
  - Response time: Immediate
  - Escalation: DevOps team lead

- Severity 2 (High): Major degradation
  - Response time: < 2 hours
  - Escalation: Backend team lead

- Severity 3 (Medium): Noticeable performance issue
  - Response time: < 1 day
  - Escalation: Development team

- Severity 4 (Low): Minor performance issue
  - Response time: < 1 week
  - Escalation: Log for sprint planning

---

## Document Change Log

| Date       | Version | Changes       | Author           |
| ---------- | ------- | ------------- | ---------------- |
| 2025-10-02 | 1.0.0   | Initial draft | Development Team |

---

## Approval

| Role           | Name | Signature | Date |
| -------------- | ---- | --------- | ---- |
| Technical Lead |      |           |      |
| DevOps Lead    |      |           |      |
| Product Owner  |      |           |      |

---

**Next Review Date:** 2025-11-02 (Monthly review recommended)
