# AGENTS.md

# AI Video Review & Investigation System

This file contains mandatory instructions for all coding agents, AI assistants, contributors, and automation tools working within this repository.

Before making any code changes, read:

1. docs/PROJECT_CONTEXT.md
2. docs/CURRENT_STATUS.md
3. docs/ROADMAP.md
4. docs/DECISIONS.md (if available)

Failure to follow these documents may result in architectural drift.

---

# Project Identity

This project is an:

**AI Video Review & Investigation System**

This project is NOT:

* A video captioning system
* A video description generator
* A video summarization application
* A simple VLM metadata pipeline

The objective is to build an enterprise-grade video intelligence platform capable of:

* Video understanding
* Event detection
* Investigation summaries
* Natural language search
* Appearance search
* Multi-camera investigations
* Area analytics
* Path analytics
* Dwell analytics
* Speed analytics
* Investigation dashboards

---

# Primary Architectural Principle

## Event-Centric Architecture

Events are the source of truth.

All downstream services must operate on events whenever possible.

Correct:

```text
Video
→ Metadata
→ Events
→ Search
→ Investigation
```

Incorrect:

```text
Video
→ Metadata
→ Search
```

Frame metadata is an intermediate artifact.

Events are the primary intelligence artifact.

---

# Current System Status

Before making any implementation decisions:

Read:

```text
docs/CURRENT_STATUS.md
```

to determine:

* Current phase
* Completed features
* In-progress work
* Known issues
* Next priorities

Do not assume the project state.

---

# Current Development Priority

Follow the roadmap.

Current expected progression:

```text
Phase 1
Event-Centric Summaries

↓

Phase 2
Embeddings + Qdrant Search

↓

Phase 3
Object Tracking

↓

Phase 4
Analytics

↓

Phase 5
Person ReID & Vehicle ReID

↓

Phase 6
Multi-Camera Investigation

↓

Phase 7
Dashboard
```

Do not skip phases without explicit approval.

---

# Development Priorities

Priority Order:

1. Event Quality
2. Search
3. Tracking
4. Analytics
5. ReID
6. Multi-Camera Investigation
7. Dashboard

Do not spend significant effort optimizing ingestion unless a measurable bottleneck exists.

Current profiling shows:

* Qwen inference is the dominant bottleneck.
* OCR is not the primary bottleneck.
* Storage is not the primary bottleneck.

---

# Event Requirements

All events should follow a consistent schema.

Example:

```json
{
  "event_id": "evt_001",
  "event_type": "pedestrian_crossing",
  "description": "Pedestrian crossed the road carrying a white bag",
  "start_time": "00:00:00",
  "end_time": "00:00:05",
  "duration_seconds": 5
}
```

Avoid introducing incompatible event formats.

If event schemas change:

1. Update the schema definition.
2. Update all consumers.
3. Update documentation.

---

# Summary Requirements

Summaries must be generated from events.

Never generate summaries directly from frame metadata.

Correct:

```text
Events
↓
Summary
```

Incorrect:

```text
Frames
↓
Summary
```

Investigation summaries must contain:

* Overview
* Statistics
* Timeline
* Peak Activity
* Notable Events

---

# Search Requirements

Future search functionality must index:

```text
Events
```

not raw frame metadata.

Preferred architecture:

```text
Events
↓
Embeddings
↓
Qdrant
↓
Semantic Search
```

Search examples:

* Find red motorcycle
* Find person carrying backpack
* Find white truck
* Find person wearing hat
* Find vehicle entering gate

---

# Tracking Requirements

Tracking must precede:

* Dwell Analytics
* Path Analytics
* Speed Analytics
* Area Analytics

Recommended stack:

```text
YOLO
+
ByteTrack
```

Do not implement dwell, path, or speed analytics without object tracking.

---

# ReID Requirements

Person ReID and Vehicle ReID are Phase 5 features.

Do not introduce ReID systems before:

* Event summaries
* Search
* Tracking

are stable.

---

# Documentation Maintenance

Documentation is part of the implementation.

A task is not complete until documentation is updated.

---

## When Features Are Completed

Update:

```text
docs/CURRENT_STATUS.md
```

Required updates:

* Completed work
* Current phase
* New blockers
* Next priorities

---

## When Architecture Changes

Update:

```text
docs/PROJECT_CONTEXT.md
```

Document:

* What changed
* Why it changed

---

## When Priorities Change

Update:

```text
docs/ROADMAP.md
```

Ensure roadmap reflects reality.

---

## When Major Decisions Are Made

Update:

```text
docs/DECISIONS.md
```

Example:

```md
Date: 2026-06-04

Decision:
Use Qdrant instead of FAISS.

Reason:
Need filtering and distributed deployment.

Status:
Accepted.
```

---

# Code Quality Requirements

All new code should be:

* Production-grade
* Type-hinted
* Tested
* Modular
* Documented

Prefer:

* FastAPI
* Pydantic
* Dependency Injection
* Structured Logging

Avoid:

* Hardcoded paths
* Global mutable state
* Tight coupling

---

# Before Completing Any Task

Verify:

* Tests pass
* No architectural violations introduced
* Documentation updated
* Event-centric architecture preserved

---

# Agent Completion Checklist

Before marking work complete:

* Read PROJECT_CONTEXT.md
* Read CURRENT_STATUS.md
* Follow ROADMAP.md
* Preserve event-centric architecture
* Update documentation
* Run tests
* Verify API compatibility
* Record major decisions

Only then consider the task complete.

---
# Documentation Maintenance Rules

Whenever work is completed:

1. Update docs/CURRENT_STATUS.md
2. Mark completed tasks.
3. Add newly discovered blockers.
4. Update current active phase.

Whenever architecture changes:

1. Update docs/PROJECT_CONTEXT.md
2. Explain the reason for the change.

Whenever roadmap priorities change:

1. Update docs/ROADMAP.md

Documentation must always reflect the current state of the project.

Code changes are not complete until documentation is updated.


# Final Rule

If there is a conflict between a proposed implementation and the event-centric architecture:

The event-centric architecture wins.

Events are the source of truth.
