from qdrant_client import QdrantClient, models
from uuid import uuid4


class VectorStoreService:
    def __init__(self, collection_name: str = "candidates"):
        self.client = QdrantClient(":memory:")
        self.client.set_model("sentence-transformers/all-MiniLM-L6-v2")
        self.client.set_sparse_model("prithivida/Splade_PP_en_v1")
        self.collection_name = collection_name

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