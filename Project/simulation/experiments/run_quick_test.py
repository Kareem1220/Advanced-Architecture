"""
Quick Test - Small Dataset
Run this first to verify everything works (2-3 minutes)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from run_all_experiments import ExperimentRunner

if __name__ == "__main__":
    print("=" * 80)
    print("QUICK TEST - Running with small dataset (10K docs, 50 queries)")
    print("This should take 2-3 minutes")
    print("=" * 80)

    runner = ExperimentRunner()

    # Small dataset for quick testing
    all_results, quality_results, comparison_df = runner.run_all_experiments(
        num_docs=10000,      # 10K documents (small, fast)
        num_queries=50       # 50 queries
    )

    print("\n" + "=" * 80)
    print("QUICK TEST COMPLETED!")
    print("=" * 80)
    print("\nIf this worked, you can now run the full experiments:")
    print("  python experiments/run_all_experiments.py")
