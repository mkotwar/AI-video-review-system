from qdrant_client import QdrantClient

with open("qdrant_info.txt", "w") as f:
    f.write(str(dir(QdrantClient)))
