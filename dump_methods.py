from qdrant_client import QdrantClient
import os

with open("qdrant_methods.txt", "w") as f:
    f.write(f"Search in QdrantClient: {'search' in dir(QdrantClient)}\n")
    f.write(f"Query Points in QdrantClient: {'query_points' in dir(QdrantClient)}\n")
