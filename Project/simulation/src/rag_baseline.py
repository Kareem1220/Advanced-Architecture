"""
RAG Baseline Implementation
Provides CPU, GPU, and ANN baseline implementations for comparison
"""

import numpy as np
import faiss
import time
import torch
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGBaseline:
    """Base class for RAG retrieval systems"""

    def __init__(self, embedding_dim: int = 768):
        self.embedding_dim = embedding_dim
        self.embeddings = None
        self.doc_ids = None

    def add_documents(self, embeddings: np.ndarray, doc_ids: List[int]):
        """Add document embeddings to the index"""
        raise NotImplementedError

    def search(self, query_embeddings: np.ndarray, k: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Search for top-k most similar documents"""
        raise NotImplementedError

    def measure_latency(self, query_embeddings: np.ndarray, k: int = 100, num_runs: int = 10) -> float:
        """Measure average query latency in milliseconds"""
        latencies = []

        # Warm-up
        for _ in range(3):
            self.search(query_embeddings, k)

        # Actual measurement
        for _ in range(num_runs):
            start = time.perf_counter()
            self.search(query_embeddings, k)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # Convert to ms

        return np.mean(latencies)


class CPUBaseline(RAGBaseline):
    """CPU-based exact search using FAISS"""

    def __init__(self, embedding_dim: int = 768):
        super().__init__(embedding_dim)
        self.index = faiss.IndexFlatIP(embedding_dim)  # Inner product (cosine similarity)
        logger.info("Initialized CPU baseline with exact search")

    def add_documents(self, embeddings: np.ndarray, doc_ids: List[int]):
        """Add documents to CPU index"""
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        self.doc_ids = np.array(doc_ids)
        logger.info(f"Added {len(doc_ids)} documents to CPU index")

    def search(self, query_embeddings: np.ndarray, k: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Exact search on CPU"""
        query_embeddings = query_embeddings.astype('float32')
        faiss.normalize_L2(query_embeddings)
        scores, indices = self.index.search(query_embeddings, k)
        return scores, indices


class GPUBaseline(RAGBaseline):
    """GPU-based exact search using FAISS"""

    def __init__(self, embedding_dim: int = 768, gpu_id: int = 0):
        super().__init__(embedding_dim)
        self.gpu_id = gpu_id

        # Check GPU availability
        if not faiss.get_num_gpus():
            logger.warning("No GPU available, falling back to CPU")
            self.index = faiss.IndexFlatIP(embedding_dim)
            self.use_gpu = False
        else:
            # Create GPU index
            res = faiss.StandardGpuResources()
            cpu_index = faiss.IndexFlatIP(embedding_dim)
            self.index = faiss.index_cpu_to_gpu(res, gpu_id, cpu_index)
            self.use_gpu = True
            logger.info(f"Initialized GPU baseline on GPU {gpu_id}")

    def add_documents(self, embeddings: np.ndarray, doc_ids: List[int]):
        """Add documents to GPU index"""
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        self.doc_ids = np.array(doc_ids)
        logger.info(f"Added {len(doc_ids)} documents to {'GPU' if self.use_gpu else 'CPU'} index")

    def search(self, query_embeddings: np.ndarray, k: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Exact search on GPU"""
        query_embeddings = query_embeddings.astype('float32')
        faiss.normalize_L2(query_embeddings)
        scores, indices = self.index.search(query_embeddings, k)
        return scores, indices


class ANNBaseline(RAGBaseline):
    """Approximate Nearest Neighbor using HNSW"""

    def __init__(self, embedding_dim: int = 768, m: int = 32, ef_construction: int = 200):
        super().__init__(embedding_dim)
        self.index = faiss.IndexHNSWFlat(embedding_dim, m)
        self.index.hnsw.efConstruction = ef_construction
        self.index.hnsw.efSearch = 128  # Search-time parameter
        logger.info(f"Initialized ANN baseline (HNSW) with M={m}, efConstruction={ef_construction}")

    def add_documents(self, embeddings: np.ndarray, doc_ids: List[int]):
        """Add documents to HNSW index"""
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        self.doc_ids = np.array(doc_ids)
        logger.info(f"Added {len(doc_ids)} documents to HNSW index")

    def search(self, query_embeddings: np.ndarray, k: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Approximate search using HNSW"""
        query_embeddings = query_embeddings.astype('float32')
        faiss.normalize_L2(query_embeddings)
        scores, indices = self.index.search(query_embeddings, k)
        return scores, indices


class EmbeddingGenerator:
    """Generate embeddings using sentence transformers"""

    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initialize embedding generator

        Args:
            model_name: HuggingFace model name
                - 'sentence-transformers/all-MiniLM-L6-v2' (384D, fast)
                - 'sentence-transformers/all-mpnet-base-v2' (768D, accurate)
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")

    def encode(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
        """
        Encode texts to embeddings

        Args:
            texts: List of text strings
            batch_size: Batch size for encoding
            show_progress: Show progress bar

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        return embeddings


def estimate_energy(latency_ms: float, power_watts: float) -> float:
    """
    Estimate energy consumption

    Args:
        latency_ms: Query latency in milliseconds
        power_watts: Average power consumption in watts

    Returns:
        Energy in joules
    """
    return (latency_ms / 1000.0) * power_watts


if __name__ == "__main__":
    # Quick test
    logger.info("Testing RAG baseline implementations...")

    # Generate sample data
    num_docs = 10000
    embedding_dim = 384
    num_queries = 10

    np.random.seed(42)
    doc_embeddings = np.random.randn(num_docs, embedding_dim).astype('float32')
    query_embeddings = np.random.randn(num_queries, embedding_dim).astype('float32')
    doc_ids = list(range(num_docs))

    # Test CPU baseline
    logger.info("\n=== Testing CPU Baseline ===")
    cpu_baseline = CPUBaseline(embedding_dim)
    cpu_baseline.add_documents(doc_embeddings, doc_ids)
    cpu_latency = cpu_baseline.measure_latency(query_embeddings[:1], k=100)
    logger.info(f"CPU Latency: {cpu_latency:.2f} ms")

    # Test ANN baseline
    logger.info("\n=== Testing ANN Baseline ===")
    ann_baseline = ANNBaseline(embedding_dim)
    ann_baseline.add_documents(doc_embeddings, doc_ids)
    ann_latency = ann_baseline.measure_latency(query_embeddings[:1], k=100)
    logger.info(f"ANN Latency: {ann_latency:.2f} ms")

    logger.info("\n=== Tests completed successfully ===")
