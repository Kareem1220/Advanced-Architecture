"""
Evaluation Metrics for RAG Systems
Implements standard retrieval metrics: Recall@K, MRR, nDCG
"""

import numpy as np
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def recall_at_k(retrieved_ids: np.ndarray, relevant_ids: List[int], k: int) -> float:
    """
    Calculate Recall@K

    Args:
        retrieved_ids: Array of retrieved document IDs (shape: [k] or [n, k])
        relevant_ids: List of relevant document IDs
        k: Number of top results to consider

    Returns:
        Recall@K score
    """
    if len(retrieved_ids.shape) == 1:
        retrieved_ids = retrieved_ids[:k]
        retrieved_set = set(retrieved_ids)
        relevant_set = set(relevant_ids)
        num_relevant_retrieved = len(retrieved_set & relevant_set)
        recall = num_relevant_retrieved / len(relevant_set) if len(relevant_set) > 0 else 0.0
        return recall
    else:
        # Multiple queries
        recalls = []
        for retrieved in retrieved_ids:
            recalls.append(recall_at_k(retrieved, relevant_ids, k))
        return np.mean(recalls)


def precision_at_k(retrieved_ids: np.ndarray, relevant_ids: List[int], k: int) -> float:
    """
    Calculate Precision@K

    Args:
        retrieved_ids: Array of retrieved document IDs
        relevant_ids: List of relevant document IDs
        k: Number of top results to consider

    Returns:
        Precision@K score
    """
    retrieved_ids = retrieved_ids[:k]
    retrieved_set = set(retrieved_ids)
    relevant_set = set(relevant_ids)
    num_relevant_retrieved = len(retrieved_set & relevant_set)
    precision = num_relevant_retrieved / k if k > 0 else 0.0
    return precision


def mean_reciprocal_rank(retrieved_ids_list: List[np.ndarray],
                          relevant_ids_list: List[List[int]]) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR)

    Args:
        retrieved_ids_list: List of retrieved document ID arrays (one per query)
        relevant_ids_list: List of relevant document ID lists (one per query)

    Returns:
        MRR score
    """
    reciprocal_ranks = []

    for retrieved_ids, relevant_ids in zip(retrieved_ids_list, relevant_ids_list):
        relevant_set = set(relevant_ids)

        # Find rank of first relevant document
        rank = None
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in relevant_set:
                rank = i + 1  # Rank is 1-indexed
                break

        if rank is not None:
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

    mrr = np.mean(reciprocal_ranks)
    return mrr


def dcg_at_k(relevance_scores: np.ndarray, k: int) -> float:
    """
    Calculate Discounted Cumulative Gain at K

    Args:
        relevance_scores: Array of relevance scores in ranked order
        k: Number of top results to consider

    Returns:
        DCG@K score
    """
    relevance_scores = relevance_scores[:k]
    discounts = np.log2(np.arange(2, len(relevance_scores) + 2))
    dcg = np.sum(relevance_scores / discounts)
    return dcg


def ndcg_at_k(retrieved_ids: np.ndarray, relevant_ids: List[int],
              relevance_scores_dict: Dict[int, float], k: int) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain at K

    Args:
        retrieved_ids: Array of retrieved document IDs
        relevant_ids: List of relevant document IDs
        relevance_scores_dict: Dictionary mapping doc_id to relevance score
        k: Number of top results to consider

    Returns:
        nDCG@K score
    """
    # Get relevance scores for retrieved documents
    retrieved_ids = retrieved_ids[:k]
    retrieved_scores = np.array([relevance_scores_dict.get(doc_id, 0.0)
                                  for doc_id in retrieved_ids])

    # Calculate DCG
    dcg = dcg_at_k(retrieved_scores, k)

    # Calculate ideal DCG
    ideal_scores = np.array(sorted([relevance_scores_dict.get(doc_id, 0.0)
                                     for doc_id in relevant_ids], reverse=True))
    idcg = dcg_at_k(ideal_scores, k)

    # Calculate nDCG
    if idcg == 0:
        return 0.0
    ndcg = dcg / idcg
    return ndcg


class RetrievalEvaluator:
    """Comprehensive evaluator for retrieval systems"""

    def __init__(self, k_values: List[int] = [10, 100, 1000]):
        """
        Initialize evaluator

        Args:
            k_values: List of K values for computing metrics
        """
        self.k_values = k_values

    def evaluate(self,
                 retrieved_ids_list: List[np.ndarray],
                 relevant_ids_list: List[List[int]],
                 relevance_scores_list: List[Dict[int, float]] = None) -> Dict:
        """
        Evaluate retrieval results

        Args:
            retrieved_ids_list: List of retrieved doc IDs for each query
            relevant_ids_list: List of relevant doc IDs for each query
            relevance_scores_list: Optional list of relevance score dicts

        Returns:
            Dictionary of metrics
        """
        num_queries = len(retrieved_ids_list)

        if relevance_scores_list is None:
            # Binary relevance (all relevant docs have score 1)
            relevance_scores_list = [{doc_id: 1.0 for doc_id in relevant_ids}
                                      for relevant_ids in relevant_ids_list]

        results = {}

        # Compute metrics for each K
        for k in self.k_values:
            # Recall@K
            recalls = [recall_at_k(retrieved_ids, relevant_ids, k)
                       for retrieved_ids, relevant_ids
                       in zip(retrieved_ids_list, relevant_ids_list)]
            results[f'Recall@{k}'] = np.mean(recalls)

            # Precision@K
            precisions = [precision_at_k(retrieved_ids, relevant_ids, k)
                          for retrieved_ids, relevant_ids
                          in zip(retrieved_ids_list, relevant_ids_list)]
            results[f'Precision@{k}'] = np.mean(precisions)

            # nDCG@K
            if relevance_scores_list:
                ndcgs = [ndcg_at_k(retrieved_ids, relevant_ids, rel_scores, k)
                         for retrieved_ids, relevant_ids, rel_scores
                         in zip(retrieved_ids_list, relevant_ids_list, relevance_scores_list)]
                results[f'nDCG@{k}'] = np.mean(ndcgs)

        # MRR (not K-dependent)
        results['MRR'] = mean_reciprocal_rank(retrieved_ids_list, relevant_ids_list)

        return results

    def print_results(self, results: Dict, method_name: str = "Method"):
        """Pretty print evaluation results"""
        print(f"\n{'=' * 60}")
        print(f"Evaluation Results: {method_name}")
        print(f"{'=' * 60}")

        for metric, value in sorted(results.items()):
            if '@' in metric:
                k = metric.split('@')[1]
                print(f"{metric:20s}: {value * 100:6.2f}%")
            else:
                print(f"{metric:20s}: {value:6.4f}")

        print(f"{'=' * 60}\n")


def compare_methods(results_dict: Dict[str, Dict]) -> None:
    """
    Compare multiple methods side by side

    Args:
        results_dict: Dictionary mapping method names to their results
    """
    if not results_dict:
        return

    # Get all metrics
    all_metrics = set()
    for results in results_dict.values():
        all_metrics.update(results.keys())
    all_metrics = sorted(all_metrics)

    # Print header
    print(f"\n{'=' * 80}")
    print(f"{'Metric':<20s}", end="")
    for method_name in results_dict.keys():
        print(f"{method_name:>15s}", end="")
    print()
    print(f"{'=' * 80}")

    # Print each metric
    for metric in all_metrics:
        print(f"{metric:<20s}", end="")
        for method_name, results in results_dict.items():
            value = results.get(metric, 0.0)
            if '@' in metric or metric == 'MRR':
                print(f"{value * 100:14.2f}%", end="")
            else:
                print(f"{value:15.4f}", end="")
        print()

    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    # Test metrics
    logger.info("Testing evaluation metrics...")

    # Sample data
    retrieved_1 = np.array([1, 3, 5, 7, 9, 2, 4, 6, 8, 10])
    relevant_1 = [1, 2, 3, 4, 5]

    retrieved_2 = np.array([11, 12, 13, 1, 2, 14, 15, 16, 17, 18])
    relevant_2 = [1, 2, 3]

    # Single query metrics
    logger.info(f"\nQuery 1:")
    logger.info(f"  Recall@10: {recall_at_k(retrieved_1, relevant_1, 10) * 100:.2f}%")
    logger.info(f"  Precision@10: {precision_at_k(retrieved_1, relevant_1, 10) * 100:.2f}%")

    # Multiple queries
    evaluator = RetrievalEvaluator(k_values=[5, 10])
    results = evaluator.evaluate(
        [retrieved_1, retrieved_2],
        [relevant_1, relevant_2]
    )

    evaluator.print_results(results, "Test Method")

    logger.info("Metrics tests completed successfully")
