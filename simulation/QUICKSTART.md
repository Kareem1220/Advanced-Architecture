# Quick Start Guide

## Installation Steps

### Step 1: Install Dependencies

Open a terminal in the `simulation/` directory and run:

```bash
pip install -r requirements.txt
```

**Note**: This may take 5-10 minutes to download and install all packages.

### Alternative: Install with conda (recommended)

```bash
# Create a new conda environment
conda create -n nmrag python=3.9
conda activate nmrag

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
python test_simulation.py
```

You should see:
```
============================================================
RUNNING SIMULATION FRAMEWORK TESTS
============================================================
Testing module imports...
✓ All modules imported successfully

Testing CPU baseline...
✓ CPU baseline works correctly

Testing quantization...
✓ Quantization works correctly

Testing NM-RAG hardware model...
  Simulated latency: X.XX ms
  Simulated energy: X.XXXX J
✓ Hardware model works correctly

Testing evaluation metrics...
  Recall@10: XX.XX%
✓ Metrics work correctly

============================================================
TEST SUMMARY
============================================================
✓ PASS   - Module Imports
✓ PASS   - CPU Baseline
✓ PASS   - Quantization
✓ PASS   - Hardware Model
✓ PASS   - Metrics
============================================================
TOTAL: 5/5 tests passed
============================================================

🎉 All tests passed! Simulation framework is ready to use.
```

### Step 3: Run Quick Experiments (Small Scale)

For a quick test with small dataset:

```bash
# Edit run_all_experiments.py
# Change line ~380 to:
# NUM_DOCS = 10000  # Small dataset for quick testing
# NUM_QUERIES = 50

python experiments/run_all_experiments.py
```

**Expected time**: 2-5 minutes

### Step 4: Run Full Experiments

For paper-quality results:

```bash
# Edit run_all_experiments.py
# Change line ~380 to:
# NUM_DOCS = 100000  # 100K documents
# NUM_QUERIES = 100

python experiments/run_all_experiments.py
```

**Expected time**: 10-20 minutes

### Step 5: Generate Visualizations

```bash
python visualization/generate_plots.py
```

This creates plots in `results/figures/`:
- `latency_comparison.png`
- `energy_comparison.png`
- `recall_comparison.png`
- `latency_vs_quality.png`
- `speedup_comparison.png`
- `results_table.tex` (for LaTeX paper)

## What You'll Get

### 1. Performance Numbers

Example output (your numbers may vary):

| Method | Latency (ms) | Energy (J) | Recall@100 | MRR |
|--------|-------------|-----------|-----------|-----|
| CPU    | 285.23      | 7.13      | 88.2%     | 0.428 |
| GPU    | 145.67      | 11.65     | 88.2%     | 0.428 |
| ANN    | 52.34       | 1.05      | 85.1%     | 0.412 |
| NM-RAG | 9.42        | 0.028     | 87.8%     | 0.425 |

### 2. Comparison Charts

All charts are publication-ready (300 DPI PNG).

### 3. LaTeX Table

Copy-paste ready table for your paper:

```latex
\begin{table}[H]
    \centering
    \caption{Performance Comparison of RAG Acceleration Methods}
    \label{tab:results}
    \begin{tabular}{|l|c|c|c|c|}
        \hline
        \textbf{Method} & \textbf{Latency (ms)} & ...
        ...
    \end{tabular}
\end{table}
```

## Troubleshooting

### Issue: "No module named 'numpy'"

**Solution**: Install dependencies first
```bash
pip install -r requirements.txt
```

### Issue: "GPU not available"

**Solution**: This is normal if you don't have a CUDA GPU. The simulation will still work, just skip GPU baseline or it will fall back to CPU.

To enable GPU:
```bash
pip uninstall faiss-cpu
pip install faiss-gpu
```

### Issue: "Out of memory"

**Solution**: Reduce dataset size
- Edit `run_all_experiments.py`
- Change `NUM_DOCS = 10000` (smaller)

### Issue: Tests fail

**Solution**: Make sure you're in the simulation directory
```bash
cd simulation
python test_simulation.py
```

## Expected Runtime

| Task | Small Dataset (10K docs) | Large Dataset (100K docs) |
|------|-------------------------|--------------------------|
| Tests | 30 seconds | - |
| Experiments | 2-3 minutes | 10-15 minutes |
| Visualization | 10 seconds | 15 seconds |

## Next Steps

After getting results:

1. **Update your paper** with real numbers from `results/comparison_table.csv`
2. **Include figures** from `results/figures/` in your paper
3. **Use the LaTeX table** from `results/figures/results_table.tex`

## Important Notes

⚠️ **This is a simulation**, not actual hardware:
- The NM-RAG numbers are **modeled** based on hardware parameters
- CPU/GPU/ANN numbers are **real** measurements
- The comparison is valid for demonstrating the potential benefits

✅ **Academically acceptable** because:
- Hardware simulators are standard in computer architecture research
- The model is based on realistic hardware parameters
- Baselines are real, providing valid comparison points
- Your paper clearly states this is a simulation/model

## Getting Help

If you encounter issues:

1. Check the main [README.md](README.md) for detailed documentation
2. Look at the example outputs in `results/`
3. Review individual module documentation in source files

## Files Overview

### Must Run (In Order)
1. `test_simulation.py` - Verify everything works
2. `experiments/run_all_experiments.py` - Generate results
3. `visualization/generate_plots.py` - Create figures

### Don't Need to Edit
- `src/*.py` - Core modules (already complete)
- `requirements.txt` - Dependencies

### May Want to Edit
- `experiments/run_all_experiments.py` - Change dataset size (line ~380)
- `hardware_model.py` - Adjust hardware parameters (if needed)

## Success Checklist

- [ ] Installed all dependencies (`pip install -r requirements.txt`)
- [ ] Tests pass (`python test_simulation.py`)
- [ ] Experiments complete (`python experiments/run_all_experiments.py`)
- [ ] Plots generated (`python visualization/generate_plots.py`)
- [ ] Results look reasonable (check `results/` folder)
- [ ] Ready to update paper with real numbers

Good luck with your project! 🚀
