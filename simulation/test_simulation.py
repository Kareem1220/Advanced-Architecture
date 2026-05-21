"""
Quick Test Script
Verifies all modules work correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all modules can be imported"""
    logger.info("Testing module imports...")

    try:
        from rag_baseline import CPUBaseline, ANNBaseline, EmbeddingGenerator
        from hardware_model import NMRAGAccelerator, HardwareConfig
        from quantization import SimpleQuantizer
        from metrics import RetrievalEvaluator
        logger.info("✓ All modules imported successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_cpu_baseline():
    """Test CPU baseline functionality"""
    logger.info("\nTesting CPU baseline...")

    try:
        from rag_baseline import CPUBaseline

        # Create sample data
        num_docs = 1000
        embedding_dim = 384
        doc_embeddings = np.random.randn(num_docs, embedding_dim).astype('float32')
        query_embeddings = np.random.randn(1, embedding_dim).astype('float32')

        # Test
        baseline = CPUBaseline(embedding_dim)
        baseline.add_documents(doc_embeddings, list(range(num_docs)))
        scores, indices = baseline.search(query_embeddings, k=10)

        assert scores.shape == (1, 10), f"Expected shape (1, 10), got {scores.shape}"
        assert indices.shape == (1, 10), f"Expected shape (1, 10), got {indices.shape}"

        logger.info("✓ CPU baseline works correctly")
        return True
    except Exception as e:
        logger.error(f"✗ CPU baseline failed: {e}")
        return False


def test_quantization():
    """Test quantization module"""
    logger.info("\nTesting quantization...")

    try:
        from quantization import SimpleQuantizer

        # Create sample data
        num_docs = 1000
        original_dim = 768
        quantized_dim = 128
        embeddings = np.random.randn(num_docs, original_dim).astype('float32')

        # Test
        quantizer = SimpleQuantizer(original_dim, quantized_dim)
        quantizer.train(embeddings)
        quantized = quantizer.encode(embeddings)

        assert quantized.shape == (num_docs, quantized_dim), \
            f"Expected shape ({num_docs}, {quantized_dim}), got {quantized.shape}"

        logger.info("✓ Quantization works correctly")
        return True
    except Exception as e:
        logger.error(f"✗ Quantization failed: {e}")
        return False


def test_hardware_model():
    """Test NM-RAG hardware model"""
    logger.info("\nTesting NM-RAG hardware model...")

    try:
        from hardware_model import NMRAGAccelerator, HardwareConfig

        # Create sample data
        num_docs = 10000
        embedding_dim = 128
        doc_embeddings = np.random.randn(num_docs, embedding_dim).astype('float32')
        query_embeddings = np.random.randn(1, embedding_dim).astype('float32')

        # Test
        config = HardwareConfig.get_config('baseline')
        accelerator = NMRAGAccelerator(**config)
        accelerator.add_documents(doc_embeddings, list(range(num_docs)))

        scores, indices = accelerator.search(query_embeddings, k=100)
        latency = accelerator.measure_latency(query_embeddings, k=100)
        stats = accelerator.get_performance_stats(num_queries=1, k=100)

        assert scores.shape == (1, 100), f"Expected shape (1, 100), got {scores.shape}"
        assert latency > 0, f"Expected positive latency, got {latency}"
        assert 'energy_joules' in stats, "Missing energy in stats"

        logger.info(f"  Simulated latency: {latency:.2f} ms")
        logger.info(f"  Simulated energy: {stats['energy_joules']:.4f} J")
        logger.info("✓ Hardware model works correctly")
        return True
    except Exception as e:
        logger.error(f"✗ Hardware model failed: {e}")
        return False


def test_metrics():
    """Test evaluation metrics"""
    logger.info("\nTesting evaluation metrics...")

    try:
        from metrics import recall_at_k, mean_reciprocal_rank, RetrievalEvaluator

        # Sample data
        retrieved = np.array([1, 3, 5, 7, 9, 2, 4, 6, 8, 10])
        relevant = [1, 2, 3, 4, 5]

        # Test recall
        recall = recall_at_k(retrieved, relevant, k=10)
        assert 0 <= recall <= 1, f"Recall should be in [0,1], got {recall}"

        # Test evaluator
        evaluator = RetrievalEvaluator(k_values=[10])
        results = evaluator.evaluate([retrieved], [relevant])

        assert 'Recall@10' in results, "Missing Recall@10"
        assert 'MRR' in results, "Missing MRR"

        logger.info(f"  Recall@10: {results['Recall@10'] * 100:.2f}%")
        logger.info("✓ Metrics work correctly")
        return True
    except Exception as e:
        logger.error(f"✗ Metrics failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("RUNNING SIMULATION FRAMEWORK TESTS")
    logger.info("=" * 60)

    tests = [
        ("Module Imports", test_imports),
        ("CPU Baseline", test_cpu_baseline),
        ("Quantization", test_quantization),
        ("Hardware Model", test_hardware_model),
        ("Metrics", test_metrics),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status:8s} - {test_name}")

    logger.info("=" * 60)
    logger.info(f"TOTAL: {passed}/{total} tests passed")
    logger.info("=" * 60)

    if passed == total:
        logger.info("\n🎉 All tests passed! Simulation framework is ready to use.")
        logger.info("\nNext steps:")
        logger.info("1. Run experiments: python experiments/run_all_experiments.py")
        logger.info("2. Generate plots: python visualization/generate_plots.py")
        return True
    else:
        logger.error("\n⚠️  Some tests failed. Please check the errors above.")
        logger.info("\nTroubleshooting:")
        logger.info("- Make sure all dependencies are installed: pip install -r requirements.txt")
        logger.info("- Check that you're in the simulation/ directory")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
