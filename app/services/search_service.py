"""Search Service for indexing events in Qdrant and executing semantic searches.
"""

import uuid
from typing import List, Dict, Any, Optional
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchAny, MatchValue, Range

from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.status_service import JobStatusService

class SearchService:
    """Service to connect to Qdrant, configure collections, index events, and query similar events."""
    
    _client: Optional[QdrantClient] = None

    @classmethod
    def get_client(cls) -> QdrantClient:
        """Retrieve or initialize the Qdrant client."""
        if cls._client is not None:
            return cls._client

        # Use local persistent Qdrant or in-memory fallback
        if settings.ENV == "testing" or settings.MOCK_MODEL:
            logger.info("Initializing local in-memory Qdrant client fallback.")
            cls._client = QdrantClient(location=":memory:")
        elif settings.USE_LOCAL_QDRANT:
            db_path = settings.DATA_DIR / "qdrant_db"
            db_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initializing local persistent Qdrant client at {db_path}")
            cls._client = QdrantClient(path=str(db_path))
        else:
            logger.info(f"Connecting to remote Qdrant server at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
            cls._client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

        cls.initialize_collection()
        return cls._client

    @classmethod
    def initialize_collection(cls):
        """Creates the collection in Qdrant if it doesn't already exist."""
        client = cls._client
        if client is None:
            return

        collection_name = settings.QDRANT_COLLECTION
        model_id = settings.EMBEDDING_MODEL_ID.lower()
        vector_size = 1024 if "bge-m3" in model_id else 384

        try:
            if not client.collection_exists(collection_name):
                logger.info(f"Creating Qdrant collection: {collection_name} (size: {vector_size}, distance: COSINE)")
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )
            else:
                logger.debug(f"Qdrant collection '{collection_name}' already exists.")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {e}")

    @classmethod
    def index_events(cls, video_id: str, events: List[Dict[str, Any]]) -> bool:
        """Generates embeddings for a list of events and indexes them into Qdrant."""
        if not events:
            logger.warning(f"No events provided to index for video {video_id}.")
            return False

        try:
            client = cls.get_client()
            
            JobStatusService.update(video_id, current_step="Generating embeddings...", progress_percent=90.0)

            # Prepare textual description strings to be embedded (combine summary with unified text)
            descriptions = []
            for e in events:
                desc = e.get("summary", e.get("description", ""))
                unified = e.get("unified_text", "")
                full_text = f"{desc} {unified}".strip()
                descriptions.append(full_text)
            
            # Generate embeddings vectors
            embeddings = EmbeddingService.generate_embeddings(descriptions)
            
            JobStatusService.update(video_id, current_step="Indexing vectors...", progress_percent=95.0)
            
            points = []
            for idx, (event, vector) in enumerate(zip(events, embeddings)):
                # Generate stable UUID based on video_id + event_id to prevent duplicates on re-ingestion
                stable_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{video_id}_{event['event_id']}"))
                
                # Align event parameters to the index payloads
                payload = {
                    "event_id": event["event_id"],
                    "video_id": video_id,
                    "event_type": event["event_type"],
                    "event_severity": event.get("event_severity", 15),
                    "description": event.get("summary", event.get("description", "")),
                    "start_time": event.get("timestamp_start_human", event.get("start_time", "00:00:00")),
                    "end_time": event.get("timestamp_end_human", event.get("end_time", "00:00:00")),
                    "duration_seconds": float(event.get("duration_seconds", 0.0)),
                    "objects": event.get("objects", []),
                    "activities": event.get("activities", []),
                    "thumbnail_path": event.get("thumbnail_path")
                }
                
                points.append(
                    PointStruct(
                        id=stable_id,
                        vector=vector,
                        payload=payload
                    )
                )

            client.upsert(
                collection_name=settings.QDRANT_COLLECTION,
                points=points
            )
            logger.info(f"Successfully indexed {len(points)} events in Qdrant for video {video_id}.")
            JobStatusService.update(video_id, status="complete", current_step="Processing complete", progress_percent=100.0)
            return True
            
        except Exception as e:
            logger.error(f"Failed to index events in Qdrant for video {video_id}: {e}")
            JobStatusService.update(video_id, status="failed", current_step="Failed during vector indexing")
            return False

    @classmethod
    def auto_index_existing_events(cls) -> None:
        """Scan the metadata directory for any existing events files and index them into Qdrant."""
        import json
        try:
            logger.info("Scanning metadata directory to auto-index existing events in Qdrant...")
            indexed_count = 0
            for path in settings.METADATA_DIR.glob("*_events.json"):
                stem = path.name
                if stem == "mock-video-id_events.json":
                    video_id = "mock-video-id"
                else:
                    video_id = stem.replace("_events.json", "")
                
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        events = json.load(f)
                    
                    if events:
                        cls.index_events(video_id, events)
                        indexed_count += 1
                except Exception as e:
                    logger.error(f"Failed to auto-index events for file {path.name}: {e}")
            logger.info(f"Auto-indexing complete. Successfully indexed events for {indexed_count} videos.")
        except Exception as e:
            logger.error(f"Error during auto-indexing of existing events: {e}")

    @staticmethod
    def normalize_score(raw: float) -> float:
        """Scales raw BGE-M3 cosine similarity scores (~0.35-0.70) to a user-friendly 0.0-1.0 range."""
        return max(0.0, min(1.0, (raw - 0.35) * 2.0))

    @classmethod
    def search_events(
        cls,
        query: str,
        limit: int = 10,
        video_ids: Optional[List[str]] = None,
        start_after: Optional[str] = None,  # ISO datetime string, inclusive
        end_before: Optional[str] = None,   # ISO datetime string, inclusive
        score_threshold: float = 0.0        # Minimum similarity score (0-1)
    ) -> List[Dict[str, Any]]:
        """Executes a semantic similarity search across video events.

        Optional filters:
        * `video_ids` – restrict to specific videos.
        * `start_after` – only events with `start_time` >= this value.
        * `end_before` – only events with `end_time` <= this value.
        """
        try:
            client = cls.get_client()

            # Vectorize query
            query_vector = EmbeddingService.generate_embeddings(query)

            # Build filter conditions dynamically
            conditions: List[FieldCondition] = []
            if video_ids:
                # Match any of the provided video IDs
                conditions.append(
                    FieldCondition(
                        key="video_id",
                        match=MatchAny(any=video_ids)
                    )
                )
            if start_after:
                conditions.append(
                    FieldCondition(
                        key="start_time",
                        match=Range(gte=start_after)
                    )
                )
            if end_before:
                conditions.append(
                    FieldCondition(
                        key="end_time",
                        match=Range(lte=end_before)
                    )
                )

            search_filter = Filter(must=conditions) if conditions else None

            raw_results = client.query_points(
                collection_name=settings.QDRANT_COLLECTION,
                query=query_vector,
                query_filter=search_filter,
                limit=limit * 3,  # fetch extra to allow threshold filtering
                with_payload=True
            ).points

            # Apply score threshold and limit
            filtered = []
            for hit in raw_results:
                normalized = cls.normalize_score(float(hit.score))
                if normalized >= score_threshold:
                    filtered.append({
                        "score": normalized,
                        "event_id": hit.payload.get("event_id"),
                        "video_id": hit.payload.get("video_id"),
                        "event_type": hit.payload.get("event_type"),
                        "description": hit.payload.get("description"),
                        "start_time": hit.payload.get("start_time"),
                        "end_time": hit.payload.get("end_time"),
                        "duration_seconds": hit.payload.get("duration_seconds"),
                        "objects": hit.payload.get("objects", []),
                        "activities": hit.payload.get("activities", [])
                    })
                if len(filtered) >= limit:
                    break

            logger.info(f"Semantic search query '{query}' retrieved {len(filtered)} results after threshold filtering.")
            return filtered

        except Exception as e:
            logger.error(f"Failed to search events in Qdrant: {e}")
            return []
