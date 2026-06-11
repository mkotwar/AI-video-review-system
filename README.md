# AI Video Search Engine Boilerplate

A production-grade, highly structured FastAPI backend designed for building powerful AI-driven video search, frame indexing, and semantic search systems.

---

## 🚀 Key Features

*   **Production-Grade Logging**: Utilizes `loguru` with custom rotational rules, structured outputs (text/JSON), and interceptors for standard Python loggers (including `uvicorn` and `fastapi`).
*   **Segmented Multi-Log Outputs**:
    *   `app.log`: General logs of configured level and above.
    *   `metadata.log`: Dedicated domain log for tracking video ingestion, processing, and storage events.
    *   `errors.log`: Filtered log capture for system warnings and errors (`WARNING` and above).
*   **Centralized Configuration**: Strongly-typed schema management via `pydantic-settings` to auto-parse environment values and resolve absolute paths.
*   **Robust Framework Base**: Lifespan-driven startup checks ensuring directory health and storage read/write accessibility.
*   **Extensible Folder Structure**: Pre-segmented layers for models, services, schemas, and API routers.

---

## 📂 Project Directory Structure

```text
video-search-engine/
├── app/
│   ├── api/             # API routes, endpoint controllers, and routers
│   ├── core/            # Centralized configurations and logging handlers
│   │   ├── config.py    # Configuration loader using pydantic-settings
│   │   └── logging.py   # Multi-sink loguru configuration and library interceptors
│   ├── models/          # Database definitions and machine learning model integrations
│   ├── schemas/         # Strongly-typed Pydantic validation schemas
│   ├── services/        # core business logic, frame extraction, vectorizing services
│   ├── utils/           # Shared utility tools and helper functions
│   ├── main.py          # FastAPI instance declaration & lifespan logic
│   └── __init__.py
├── data/                # Data storage directory (automatically generated on startup)
│   ├── frames/          # Extracted video frames
│   ├── logs/            # App logs (app.log, errors.log, metadata.log)
│   ├── metadata/        # DB metadata or JSON sidecar files
│   └── videos/          # Uploaded and raw video files
├── tests/               # Unit and integration test suites
│   ├── __init__.py
│   └── test_main.py     # Main endpoints & configuration integrity tests
├── .env.example         # System configurations variables template
├── README.md            # Extensive documentation
└── requirements.txt     # Locked production and dev requirements
```

---

## ⚙️ Configuration (.env)

Duplicate `.env.example` to create `.env` and adjust the variables:

```bash
cp .env.example .env
```

| Key | Type | Default | Description |
|---|---|---|---|
| `APP_NAME` | `str` | `"AI Video Search Engine"` | API title returned in swagger documentation. |
| `ENV` | `str` | `"development"` | Environment level (`development`, `production`, `testing`). |
| `DEBUG` | `bool` | `true` | Enable standard interactive debugging. |
| `HOST` | `str` | `"127.0.0.1"` | Bind host for development server. |
| `PORT` | `int` | `8000` | Bind port for development server. |
| `LOG_LEVEL` | `str` | `"INFO"` | Standard minimum console logging level (`DEBUG`/`INFO`/`WARNING`/`ERROR`). |
| `LOG_FORMAT` | `str` | `"text"` | Log formatting. Options: `text` or `json`. |
| `DATA_DIR` | `str` | `"data"` | Path to parent application data storage. |

---

## 🛠️ Quick Start

### 1. Requirements

*   Python 3.9+
*   Virtual environment tool (`venv`, `conda`)

### 2. Set Up Environment

Create and activate a virtual environment, then install requirements:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Unix/macOS
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch Development Server

Run the application using the integrated uvicorn server:

```bash
cd video-search-engine
python -m uvicorn app.main:app --reload
```

Alternatively, run from the root workspace:

```bash
python -m uvicorn video-search-engine.app.main:app --reload
```

*   **API documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
*   **System Health status**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🎯 Structured Logging Details

All logging actions utilize `loguru`. Standard stdout print statements or traditional `logging` methods from libraries are automatically intercepted and routed to the corresponding output channels.

### File Rotations and Retention
*   Files are rotated when they exceed **10 MB**.
*   The system retains a maximum backup history of **10 logs** per log category.

### Routing Domain Logs
To route logs to `metadata.log`, explicitly bind `context="metadata"` during logging:

```python
from loguru import logger

# App logs
logger.info("General processing message")  # Writes to app.log & stdout

# Specific domain metadata logs
meta_logger = logger.bind(context="metadata")
meta_logger.info("Ingesting video chunk metadata")  # Writes to metadata.log, app.log & stdout

# System errors
logger.error("A critical resource was not found")  # Writes to errors.log, app.log & stdout
```

---

## 🧪 Testing

Run standard tests via pytest:

```bash
pytest tests/
```
