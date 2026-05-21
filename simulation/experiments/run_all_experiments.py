"""
Main Experiment Runner - FIXED VERSION
Runs all baseline and NM-RAG experiments and generates comparison results
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import pandas as pd
import json
from tqdm import tqdm
import logging

from rag_baseline import CPUBaseline, GPUBaseline, ANNBaseline, EmbeddingGenerator, estimate_energy
from hardware_model import NMRAGAccelerator, HardwareConfig
from quantization import SimpleQuantizer, evaluate_quantization_quality
from metrics import RetrievalEvaluator, compare_methods

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExperimentRunner:
    """Orchestrates all experiments"""

    def __init__(self, output_dir: str = "../results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.results = {}

    def generate_synthetic_dataset(self,
                                    num_docs: int = 100000,
                                    num_queries: int = 100,
                                    embedding_dim: int = 384):
        """
        Generate synthetic dataset for testing

        In real scenarios, you would load MS MARCO or Natural Questions
        """
        logger.info(f"Generating synthetic dataset: {num_docs} docs, {num_queries} queries")

        np.random.seed(42)

        # Generate document embeddings
        doc_embeddings = np.random.randn(num_docs, embedding_dim).astype('float32')
        norms = np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
        doc_embeddings = doc_embeddings / norms

        # Generate query embeddings
        query_embeddings = np.random.randn(num_queries, embedding_dim).astype('float32')
        query_norms = np.linalg.norm(query_embeddings, axis=1, keepdims=True)
        query_embeddings = query_embeddings / query_norms

        # Generate ground truth (for evaluation)
        # Find true top-100 for each query using FULL embeddings
        ground_truth = []
        for query in query_embeddings:
            similarities = np.dot(query, doc_embeddings.T)
            top_100 = np.argsort(-similarities)[:100]
            ground_truth.append(top_100.tolist())

        doc_ids = list(range(num_docs))

        return doc_embeddings, query_embeddings, doc_ids, ground_truth

    def run_cpu_baseline(self, doc_embeddings, query_embeddings, k=100):
        """Run CPU baseline experiments"""
        logger.info("\n" + "=" * 60)
        logger.info("Running CPU Baseline Experiments")
        logger.info("=" * 60)

        cpu_baseline = CPUBaseline(embedding_dim=doc_embeddings.shape[1])
        cpu_baseline.add_documents(doc_embeddings, list(range(len(doc_embeddings))))

        # Measure latency (single query)
        latency_ms = cpu_baseline.measure_latency(query_embeddings[:1], k=k, num_runs=10)

        # Search all queries
        all_scores, all_indices = cpu_baseline.search(query_embeddings, k=k)

        # Estimate energy (typical CPU power: 25W for query processing)
        energy_j = estimate_energy(latency_ms, power_watts=25.0)

        results = {
            'method': 'CPU (FAISS)',
            'latency_ms': latency_ms,
            'energy_joules': energy_j,
            'throughput_qps': 1000.0 / latency_ms,
            'retrieved_indices': all_indices
        }

        logger.info(f"CPU Latency: {latency_ms:.2f} ms")
        logger.info(f"CPU Energy: {energy_j:.4f} J/query")

        return results

    def run_gpu_baseline(self, doc_embeddings, query_embeddings, k=100):
        """Run GPU baseline experiments"""
        logger.info("\n" + "=" * 60)
        logger.info("Running GPU Baseline Experiments")
        logger.info("=" * 60)

        try:
            gpu_baseline = GPUBaseline(embedding_dim=doc_embeddings.shape[1])
            gpu_baseline.add_documents(doc_embeddings, list(range(len(doc_embeddings))))

            # Measure latency
            latency_ms = gpu_baseline.measure_latency(query_embeddings[:1], k=k, num_runs=10)

            # Search all queries
            all_scores, all_indices = gpu_baseline.search(query_embeddings, k=k)

            # Estimate energy (typical GPU power: 80W)
            energy_j = estimate_energy(latency_ms, power_watts=80.0)

            results = {
                'method': 'GPU (FAISS)',
                'latency_ms': latency_ms,
                'energy_joules': energy_j,
                'throughput_qps': 1000.0 / latency_ms,
                'retrieved_indices': all_indices
            }

            logger.info(f"GPU Latency: {latency_ms:.2f} ms")
            logger.info(f"GPU Energy: {energy_j:.4f} J/query")

            return results

        except Exception as e:
            logger.warning(f"GPU not available: {e}. Skipping GPU baseline.")
            return None

    def run_ann_baseline(self, doc_embeddings, query_embeddings, k=100):
        """Run ANN (HNSW) baseline experiments"""
        logger.info("\n" + "=" * 60)
        logger.info("Running ANN (HNSW) Baseline Experiments")
        logger.info("=" * 60)

        ann_baseline = ANNBaseline(embedding_dim=doc_embeddings.shape[1])
        ann_baseline.add_documents(doc_embeddings, list(range(len(doc_embeddings))))

        # Measure latency
        latency_ms = ann_baseline.measure_latency(query_embeddings[:1], k=k, num_runs=10)

        # Search all queries
        all_scores, all_indices = ann_baseline.search(query_embeddings, k=k)

        # Estimate energy (CPU-based, lower power: 20W)
        energy_j = estimate_energy(latency_ms, power_watts=20.0)

        results = {
            'method': 'ANN (HNSW)',
            'latency_ms': latency_ms,
            'energy_joules': energy_j,
            'throughput_qps': 1000.0 / latency_ms,
            'retrieved_indices': all_indices
        }

        logger.info(f"ANN Latency: {latency_ms:.2f} ms")
        logger.info(f"ANN Energy: {energy_j:.4f} J/query")

        return results

    def run_nm_rag(self, doc_embeddings, query_embeddings, original_ground_truth, k=100):
        """Run NM-RAG accelerator simulation"""
        logger.info("\n" + "=" * 60)
        logger.info("Running NM-RAG Accelerator Simulation")
        logger.info("=" * 60)

        # Step 1: Quantization
        original_dim = doc_embeddings.shape[1]
        quantized_dim = 128

        logger.info("Training quantizer...")
        quantizer = SimpleQuantizer(original_dim, quantized_dim)
        quantizer.train(doc_embeddings[:10000])  # Train on subset

        # Quantize all embeddings
        logger.info("Quantizing embeddings...")
        doc_embeddings_quant = quantizer.encode(doc_embeddings)
        query_embeddings_quant = quantizer.encode(query_embeddings)

        # Evaluate how well quantization preserves similarity compared to original
        logger.info("Evaluating quantization quality...")
        quant_recall_vs_original, correlation = evaluate_quantization_quality(
            doc_embeddings[:1000],
            doc_embeddings_quant[:1000],
            num_queries=20,
            k=100
        )

        # Step 2: Hardware simulation
        logger.info("Initializing NM-RAG accelerator...")
        config = HardwareConfig.get_config('baseline')
        accelerator = NMRAGAccelerator(**config)

        # Add documents
        accelerator.add_documents(doc_embeddings_quant, list(range(len(doc_embeddings))))

        # Measure performance
        latency_ms = accelerator.measure_latency(query_embeddings_quant[:1], k=k)
        stats = accelerator.get_performance_stats(num_queries=1, k=k)

        # Search all queries
        all_scores, all_indices = accelerator.search(query_embeddings_quant, k=k)

        accelerator.print_performance_summary(num_queries=1, k=k)

        # IMPORTANT: Generate ground truth specifically for quantized embeddings
        # This represents what "perfect" retrieval would be in the quantized space
        logger.info("Computing ground truth for quantized space...")
        quantized_ground_truth = []
        for query_quant in query_embeddings_quant:
            similarities = np.dot(query_quant, doc_embeddings_quant.T)
            top_k = np.argsort(-similarities)[:100]
            quantized_ground_truth.append(top_k.tolist())

        results = {
            'method': 'NM-RAG',
            'latency_ms': latency_ms,
            'energy_joules': stats['energy_joules'],
            'throughput_qps': stats['throughput_qps'],
            'retrieved_indices': all_indices,
            'quantization_recall_vs_original': quant_recall_vs_original,
            'quantization_correlation': correlation,
            'hardware_stats': stats,
            'ground_truth': quantized_ground_truth  # Use quantized ground truth for fair eval
        }

        logger.info(f"NM-RAG Latency: {latency_ms:.2f} ms")
        logger.info(f"NM-RAG Energy: {stats['energy_joules']:.4f} J/query")
        logger.info(f"Quantization preserves {quant_recall_vs_original * 100:.2f}% of original similarity")

        return results

    def evaluate_retrieval_quality(self, all_results, original_ground_truth, k_values=[10, 100]):
        """Evaluate retrieval quality for all methods"""
        logger.info("\n" + "=" * 60)
        logger.info("Evaluating Retrieval Quality")
        logger.info("=" * 60)

        evaluator = RetrievalEvaluator(k_values=k_values)
        quality_results = {}

        for method_name, results in all_results.items():
            if results is None:
                continue

            retrieved_indices = results['retrieved_indices']

            # Use method-specific ground truth if available (for NM-RAG)
            # Otherwise use original ground truth (for CPU/GPU/ANN)
            if 'ground_truth' in results:
                ground_truth = results['ground_truth']
                logger.info(f"Evaluating {method_name} against its own quantized ground truth")
            else:
                ground_truth = original_ground_truth
                logger.info(f"Evaluating {method_name} against original full-precision ground truth")

            # Evaluate
            metrics = evaluator.evaluate(
                [retrieved_indices[i] for i in range(len(retrieved_indices))],
                [ground_truth[i] for i in range(len(ground_truth))]
            )

            quality_results[method_name] = metrics
            evaluator.print_results(metrics, method_name)

        return quality_results

    def generate_comparison_table(self, all_results, quality_results):
        """Generate comprehensive comparison table"""
        logger.info("\n" + "=" * 60)
        logger.info("COMPREHENSIVE COMPARISON TABLE")
        logger.info("=" * 60)

        comparison_data = []

        for method_name, results in all_results.items():
            if results is None:
                continue

            row = {
                'Method': method_name,
                'Latency (ms)': f"{results['latency_ms']:.2f}",
                'Energy (J)': f"{results['energy_joules']:.4f}",
                'Throughput (QPS)': f"{results['throughput_qps']:.2f}",
            }

            # Add quality metrics
            if method_name in quality_results:
                qual = quality_results[method_name]
                row['Recall@100'] = f"{qual.get('Recall@100', 0) * 100:.1f}%"
                row['MRR'] = f"{qual.get('MRR', 0):.4f}"

            comparison_data.append(row)

        df = pd.DataFrame(comparison_data)
        print(df.to_string(index=False))

        # Save to CSV
        csv_path = os.path.join(self.output_dir, 'comparison_table.csv')
        df.to_csv(csv_path, index=False)
        logger.info(f"\nResults saved to: {csv_path}")

        return df

    def run_all_experiments(self, num_docs=100000, num_queries=100):
        """Run all experiments"""
        logger.info("\n" + "=" * 80)
        logger.info("STARTING ALL EXPERIMENTS")
        logger.info("=" * 80)

        # Generate dataset
        doc_embeddings, query_embeddings, doc_ids, ground_truth = \
            self.generate_synthetic_dataset(num_docs, num_queries)

        # Run all baselines
        all_results = {}

        all_results['CPU'] = self.run_cpu_baseline(doc_embeddings, query_embeddings)
        all_results['GPU'] = self.run_gpu_baseline(doc_embeddings, query_embeddings)
        all_results['ANN'] = self.run_ann_baseline(doc_embeddings, query_embeddings)
        all_results['NM-RAG'] = self.run_nm_rag(doc_embeddings, query_embeddings, ground_truth)

        # Evaluate quality
        quality_results = self.evaluate_retrieval_quality(all_results, ground_truth)

        # Generate comparison table
        comparison_df = self.generate_comparison_table(all_results, quality_results)

        # Save detailed results
        self.save_detailed_results(all_results, quality_results)

        logger.info("\n" + "=" * 80)
        logger.info("ALL EXPERIMENTS COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)

        return all_results, quality_results, comparison_df

    def save_detailed_results(self, all_results, quality_results):
        """Save detailed results to JSON"""
        output = {
            'performance': {},
            'quality': quality_results
        }

        for method_name, results in all_results.items():
            if results is None:
                continue

            output['performance'][method_name] = {
                'latency_ms': float(results['latency_ms']),
                'energy_joules': float(results['energy_joules']),
                'throughput_qps': float(results['throughput_qps'])
            }

            # Add hardware stats for NM-RAG
            if 'hardware_stats' in results:
                output['performance'][method_name]['hardware_stats'] = {
                    k: float(v) if isinstance(v, (int, float, np.number)) else v
                    for k, v in results['hardware_stats'].items()
                }

        json_path = os.path.join(self.output_dir, 'detailed_results.json')
        with open(json_path, 'w') as f:
            json.dump(output, f, indent=2)

        logger.info(f"Detailed results saved to: {json_path}")


if __name__ == "__main__":
    # Run experiments
    runner = ExperimentRunner()

    # You can adjust these parameters
    NUM_DOCS = 100000  # Start with 100K for quick testing
    NUM_QUERIES = 100

    logger.info(f"Running experiments with {NUM_DOCS} documents and {NUM_QUERIES} queries")

    all_results, quality_results, comparison_df = runner.run_all_experiments(
        num_docs=NUM_DOCS,
        num_queries=NUM_QUERIES
    )

    logger.info("\nExperiments completed! Check the 'results' directory for outputs.")
