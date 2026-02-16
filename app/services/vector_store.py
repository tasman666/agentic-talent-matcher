from qdrant_client import QdrantClient, models
from uuid import uuid4

from app.config import get_settings


class VectorStoreService:
    def __init__(self):
        settings = get_settings()
        self.client = QdrantClient(":memory:")
        self.client.set_model(settings.embedding_model_name)
        self.client.set_sparse_model(settings.sparse_embedding_model_name)
        self.collection_name = settings.vector_store_collection

    def upsert_chunks(self, chunks: list[str], filename: str):
        ids = [str(uuid4()) for _ in chunks]
        metadata = [{"filename": filename, "chunk_index": i} for i in range(len(chunks))]
        
        self.client.add(
            collection_name=self.collection_name,
            documents=chunks,
            metadata=metadata,
            ids=ids,
            batch_size=32
        )
        return ids

    def search_hybrid(self, query: str, limit: int = 5):
        """
        Perform a hybrid search (Dense + Sparse) fused with RRF.
        Uses client.query() which is fastembed-aware and automatically
        handles vector field names and encoding.
        """
        results = self.client.query(
            collection_name=self.collection_name,
            query_text=query,
            limit=limit,
        )

        return results