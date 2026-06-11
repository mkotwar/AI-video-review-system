# AI Video Review & Investigation System Roadmap

## Vision

Build an enterprise-grade AI Video Review & Investigation Platform capable of transforming raw video footage into searchable investigation intelligence.

The final system must support:

* Automated video understanding
* Event detection
* Investigation summaries
* Natural language search
* Appearance similarity search
* Multi-camera investigations
* Area analytics
* Path analytics
* Dwell analytics
* Speed analytics
* Investigation dashboards
* Safe City operations

---

# Guiding Principles

## Event-Centric Architecture

All downstream capabilities must operate on events rather than raw frames.

```text
Video
 ↓
Frames
 ↓
Metadata
 ↓
Events
 ↓
Investigation Services
```

Events are the source of truth.

---

## Search First, Analytics Later

Priority order:

```text
Summaries
↓
Search
↓
Tracking
↓
Analytics
↓
ReID
↓
Multi-Camera Investigation
↓
Dashboard
```

---

# Phase 1 — Event-Centric Summarization

## Objective

Generate investigation-grade summaries from event catalogs.

## Input

```text
Aggregated Events
```

## Output

```text
Investigation Summary
```

Example:

* 32 vehicles entered
* 28 vehicles exited
* 14 pedestrians observed
* Peak activity between 18:05 and 18:25
* One vehicle remained stationary for 12 minutes

---

## Deliverables

### Summary Service

```text
app/services/summary_service.py
```

Responsibilities:

* Load events
* Compute statistics
* Detect peak activity
* Extract notable events
* Build timeline
* Generate overview

---

### Summary API

```http
GET /api/v1/videos/{video_id}/summary
```

---

### Statistics Engine

Generate:

* Total events
* Vehicle counts
* Pedestrian counts
* Event type counts
* Duration metrics

---

### Timeline Generation

Example:

```json
[
  {
    "time": "18:05",
    "event": "Motorcycle entered Gate 1"
  }
]
```

---

### Peak Activity Detection

Identify busiest periods.

Example:

```json
[
  {
    "start": "18:05",
    "end": "18:25",
    "event_count": 24
  }
]
```

---

### Success Criteria

* Events successfully summarized
* Timeline generated
* Statistics generated
* Investigation overview generated
* API returns valid summary

---

# Phase 2 — Semantic Search

## Objective

Make videos searchable using natural language.

---

## Architecture

```text
Events
 ↓
Embeddings
 ↓
Qdrant
 ↓
Search API
```

---

## Recommended Embedding Models

### Primary

BGE-M3

### Alternative

BGE-Large

---

## Deliverables

### Embedding Service

```text
app/services/embedding_service.py
```

Responsibilities:

* Convert events into embeddings
* Batch processing
* Metadata attachment

---

### Qdrant Integration

Store:

```json
{
  "event_id": "...",
  "description": "...",
  "camera_id": "...",
  "timestamp": "..."
}
```

---

### Search API

```http
POST /api/v1/search
```

---

## Example Queries

```text
Find red motorcycle

Find person carrying backpack

Find white truck

Find person wearing hat

Find vehicle entering gate
```

---

## Success Criteria

* Semantic retrieval working
* Sub-second search
* Cross-video search
* Event-level retrieval

---

# Phase 3 — Object Tracking

## Objective

Create persistent identities across frames.

---

## Recommended Stack

```text
YOLO
+
ByteTrack
```

---

## Architecture

```text
Video
 ↓
Detection
 ↓
Tracking
 ↓
Track IDs
 ↓
Object Timelines
```

---

## Deliverables

### Detection Service

Vehicle detection

Person detection

Object detection

---

### Tracking Service

Persistent IDs

Example:

```text
Person #17

00:01:05
00:01:07
00:01:09
00:01:12
```

---

### Timeline Storage

Track histories

Track metadata

Track durations

---

## Success Criteria

* Stable tracking IDs
* Object timelines generated
* Events linked to tracks

---

# Phase 4 — Investigation Analytics

## Objective

Enable advanced CCTV investigation capabilities.

---

## Area Analytics

Examples:

```text
Find people entering area

Find vehicles entering zone

Find restricted area violations
```

---

## Dwell Analytics

Examples:

```text
Standing longer than 5 minutes

Vehicle parked longer than 10 minutes
```

---

## Path Analytics

Examples:

```text
Gate
→ Parking
→ Exit
```

---

## Speed Analytics

Examples:

```text
Vehicle exceeding threshold speed
```

---

## Deliverables

### Zone Engine

Polygon support

Region definitions

---

### Dwell Engine

Time-in-zone calculations

---

### Path Engine

Movement sequence detection

---

### Speed Engine

Track velocity calculations

---

## Success Criteria

* Area filtering operational
* Dwell detection operational
* Path analysis operational
* Speed analytics operational

---

# Phase 5 — Person ReID & Vehicle ReID

## Objective

Enable appearance-based similarity search.

---

## Examples

```text
Find this person

Find this vehicle

Search across all videos

Search across all cameras
```

---

## Deliverables

### Person ReID

Appearance embeddings

Similarity search

---

### Vehicle ReID

Vehicle appearance embeddings

Cross-camera matching

---

### Similarity Search API

```http
POST /api/v1/reid/search
```

---

## Success Criteria

* Person matching operational
* Vehicle matching operational
* Cross-video retrieval operational

---

# Phase 6 — Multi-Camera Investigation

## Objective

Track entities across multiple cameras.

---

## Architecture

```text
Camera A
 ↓
Camera B
 ↓
Camera C
```

Unified investigation timeline.

---

## Deliverables

### Camera Correlation Engine

Cross-camera matching

---

### Investigation Timeline

Entity movement history

---

### Case Builder

Investigation workflow support

---

## Success Criteria

* Cross-camera tracking operational
* Unified timeline generated
* Investigation workflow supported

---

# Phase 7 — Investigation Dashboard

## Objective

Provide a complete web-based investigation platform.

---

## Recommended Stack

```text
React
+
FastAPI
```

---

## Dashboard Features

### Video Upload

Upload and processing status

---

### Search

Natural language search

Similarity search

Filters

---

### Event Review

Event explorer

Timeline navigation

---

### Analytics

Area analytics

Path analytics

Dwell analytics

Speed analytics

---

### Case Management

Investigation workspaces

Saved searches

Evidence review

---

## Success Criteria

* End-to-end workflow operational
* Investigation-ready UI
* Search integrated
* Analytics integrated

---

# Future Enhancements

## Real-Time Streaming

RTSP

Live CCTV

VMS integration

---

## Alerting

Suspicious activity alerts

Zone violations

Loitering detection

---

## LLM Investigation Assistant

Natural language investigation support.

Example:

```text
Show all red motorcycles entering Gate 1 between 18:00 and 19:00.
```

---

## Safe City Scale Deployment

Multi-site deployment

Distributed processing

Large-scale video indexing

Multi-tenant support

---

# Current Focus

Current Active Phase:

✅ Phase 2 — Semantic Search

Current Priority:

1. Set up remote Qdrant containerization
2. Implement hybrid search ranking (Cosine similarity + keyword/OCR matching)

Next Phase:

➡️ Phase 3 — Object Tracking
