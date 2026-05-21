"""
Vector Quantization Module
Implements product quantization for dimension reduction (768D -> 128D)
"""

import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import logging
from typing import Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductQuantizer:
    """
    Product Quantization for embedding compression
    Reduces 768D embeddings to 128D while maintaining similarity
    """

    def __init__(self, original_dim: int = 768, quantized_dim: int = 128,
                 num_codebooks: int = 8, codebook_size: int = 256):
        """
        Initialize Product Quantizer

        Args:
            original_dim: Original embedding dimension (e.g., 768 for BERT)
            quantized_dim: Target dimension after quantization (e.g., 128)
            num_codebooks: Number of product quantization codebooks
            codebook_size: Number of centroids per codebook
        """
        self.original_dim = original_dim
        self.quantized_dim = quantized_dim
        self.num_codebooks = num_codebooks
        self.codebook_size = codebook_size

        # Will be trained
        self.pca = None
        self.codebooks = []
        self.is_trained = False

        logger.info(f"Initialized ProductQuantizer: {original_dim}D -> {quantized_dim}D")

    def train(self, embeddings: np.ndarray, pca_samples: int = 100000):
        """
        Train the quantizer on a sample of embeddings

        Args:
            embeddings: Training embeddings of shape (N, original_dim)
            pca_samples: Number of samples to use for PCA training
        """
        logger.info(f"Training quantizer on {len(embeddings)} embeddings...")

        # Step 1: PCA for initial dimension reduction
        logger.info(f"Training PCA: {self.original_dim}D -> {self.quantized_dim}D")

        # Sample if needed
        if len(embeddings) > pca_samples:
            sample_indices = np.random.choice(len(embeddings), pca_samples, replace=False)
            pca_train_data = embeddings[sample_indices]
        else:
            pca_train_data = embeddings

        self.pca = PCA(n_components=self.quantized_dim, random_state=42)
        self.pca.fit(pca_train_data)

        variance_retained = np.sum(self.pca.explained_variance_ratio_)
        logger.info(f"PCA variance retained: {variance_retained * 100:.2f}%")

        # Step 2: Product quantization (optional, for further compression)
        # This is a simplified version - actual PQ would split dimensions
        # For now, we just use PCA-reduced embeddings

        self.is_trained = True
        logger.info("Quantizer training complete")

    def encode(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Encode embeddings to quantized form

        Args:
            embeddings: Input embeddings of shape (N, original_dim)

        Returns:
            Quantized embeddings of shape (N, quantized_dim)
        """
        if not self.is_trained:
            raise ValueError("Quantizer must be trained before encoding")

        # Apply PCA transformation
        quantized = self.pca.transform(embeddings)

        return quantized.astype('float32')

    def get_compression_ratio(self) -> float:
        """Get the compression ratio"""
        return self.original_dim / self.quantized_dim

    def get_memory_savings(self) -> float:
        """Get memory savings percentage"""
        return (1 - self.quantized_dim / self.original_dim) * 100


class SimpleQuantizer:
    """
    Simpler quantization using just PCA
    Faster and easier to use for quick experiments
    """

    def __init__(self, original_dim: int = 768, quantized_dim: int = 128, whiten: bool = True):
        self.original_dim = original_dim
        self.quantized_dim = quantized_dim
        self.pca = PCA(n_components=quantized_dim, random_state=42, whiten=whiten)
        self.is_trained = False

    def train(self, embeddings: np.ndarray):
        """Train PCA on embeddings"""
        logger.info(f"Training simple quantizer: {self.original_dim}D -> {self.quantized_dim}D")
        self.pca.fit(embeddings)
        variance = np.sum(self.pca.explained_variance_ratio_)
        logger.info(f"Variance retained: {variance * 100:.2f}%")
        self.is_trained = True

    def encode(self, embeddings: np.ndarray) -> np.ndarray:
        """Encode to lower dimension"""
        if not self.is_trained:
            raise ValueError("Must train before encoding")
        return self.pca.transform(embeddings).astype('float32')

    def decode(self, quantized_embeddings: np.ndarray) -> np.ndarray:
        """Decode back to original dimension (approximate)"""
        if not self.is_trained:
            raise ValueError("Must train before decoding")
        return self.pca.inverse_transform(quantized_embeddings).astype('float32')


class RandomProjection:
    """
    Fast random projection for dimension reduction
    Preserves distances approximately (Johnson-Lindenstrauss lemma)
    """

    def __init__(self, original_dim: int = 768, quantized_dim: int = 128):
        self.original_dim = original_dim
        self.quantized_dim = quantized_dim

        # Create random projection matrix
        self.projection_matrix = np.random.randn(original_dim, quantized_dim).astype('float32')
        self.projection_matrix /= np.sqrt(quantized_dim)

        logger.info(f"Initialized random projection: {original_dim}D -> {quantized_dim}D")

    def encode(self, embeddings: np.ndarray) -> np.ndarray:
        """Project to lower dimension"""
        return np.dot(embeddings, self.projection_matrix)


def evaluate_quantization_quality(original_embeddings: np.ndarray,
                                   quantized_embeddings: np.ndarray,
                                   num_queries: int = 100,
                                   k: int = 100) -> Tuple[float, float]:
    """
    Evaluate quantization quality by comparing retrieval results

    Args:
        original_embeddings: Original high-dim embeddings (N, D_orig)
        quantized_embeddings: Quantized low-dim embeddings (N, D_quant)
        num_queries: Number of queries to test
        k: Number of top results to compare

    Returns:
        (recall, similarity_correlation)
    """
    logger.info(f"Evaluating quantization quality with {num_queries} queries...")

    # Randomly select queries
    query_indices = np.random.choice(len(original_embeddings), num_queries, replace=False)

    recalls = []
    correlations = []

    for idx in query_indices:
        # Original search
        orig_query = original_embeddings[idx:idx + 1]
        orig_sims = np.dot(orig_query, original_embeddings.T)[0]
        orig_top_k = np.argsort(-orig_sims)[:k]

        # Quantized search
        quant_query = quantized_embeddings[idx:idx + 1]
        quant_sims = np.dot(quant_query, quantized_embeddings.T)[0]
        quant_top_k = np.argsort(-quant_sims)[:k]

        # Calculate recall
        overlap = len(set(orig_top_k) & set(quant_top_k))
        recall = overlap / k
        recalls.append(recall)

        # Calculate correlation of similarity scores
        correlation = np.corrcoef(orig_sims, quant_sims)[0, 1]
        correlations.append(correlation)

    avg_recall = np.mean(recalls)
    avg_correlation = np.mean(correlations)

    logger.info(f"Quantization quality - Recall@{k}: {avg_recall * 100:.2f}%, "
                f"Similarity correlation: {avg_correlation:.4f}")

    return avg_recall, avg_correlation


if __name__ == "__main__":
    # Test quantization
    logger.info("Testing quantization modules...")

    # Generate sample embeddings
    num_docs = 10000
    original_dim = 768
    quantized_dim = 128

    np.random.seed(42)
    embeddings = np.random.randn(num_docs, original_dim).astype('float32')

    # Test SimpleQuantizer
    logger.info("\n=== Testing SimpleQuantizer ===")
    quantizer = SimpleQuantizer(original_dim, quantized_dim)
    quantizer.train(embeddings[:5000])  # Train on subset
    quantized = quantizer.encode(embeddings)

    logger.info(f"Original shape: {embeddings.shape}")
    logger.info(f"Quantized shape: {quantized.shape}")
    logger.info(f"Compression ratio: {original_dim / quantized_dim:.1f}x")
    logger.info(f"Memory savings: {(1 - quantized_dim / original_dim) * 100:.1f}%")

    # Evaluate quality
    recall, correlation = evaluate_quantization_quality(embeddings, quantized)

    logger.info("\n=== Testing RandomProjection ===")
    rp = RandomProjection(original_dim, quantized_dim)
    rp_quantized = rp.encode(embeddings)
    rp_recall, rp_correlation = evaluate_quantization_quality(embeddings, rp_quantized)

    logger.info("\nQuantization tests completed successfully")
