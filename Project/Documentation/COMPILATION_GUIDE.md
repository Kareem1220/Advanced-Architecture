# NM-RAG Paper Compilation Guide

## Overview

Your IEEE conference paper is now **complete and ready for submission**. This guide explains how to compile it to PDF and optionally convert to Word format.

## Files Included

### Main Paper
- **NM_RAG_Paper.tex** - Complete IEEE conference paper (LaTeX source)

### Figures
All figures are in `results/figures/`:

#### Architecture Diagrams (NEW - Just Generated)
- `system_overview.png` - High-level system architecture
- `nmpu_detail.png` - Detailed NMPU microarchitecture
- `pipeline_diagram.png` - Query processing pipeline

#### Results Plots (From Simulation)
- `latency_comparison.png` - Latency performance comparison
- `energy_comparison.png` - Energy efficiency comparison
- `recall_comparison.png` - Retrieval quality comparison
- `speedup_comparison.png` - Speedup across corpus sizes
- `latency_vs_quality.png` - Latency-quality tradeoff space

#### Tables
- `results_table.tex` - LaTeX table for results
- `comparison_table.csv` - CSV version of results

### Data Files
- `detailed_results.json` - Full simulation results
- `FINAL_RESULTS_SUMMARY.md` - Results explanation and defense strategy

## Method 1: Compile on Overleaf (RECOMMENDED)

This is the easiest method and produces professional results.

### Steps:

1. **Create Overleaf Project**
   - Go to [overleaf.com](https://www.overleaf.com)
   - Click "New Project" → "Upload Project"

2. **Upload Files**
   - Create a ZIP file containing:
     ```
     NM_RAG_Paper.tex
     results/
       figures/
         system_overview.png
         nmpu_detail.png
         pipeline_diagram.png
         speedup_comparison.png
         latency_vs_quality.png
         results_table.tex
     ```
   - Upload the ZIP to Overleaf

3. **Compile**
   - Overleaf will automatically compile
   - Download the PDF using the "Download PDF" button
   - **Output**: `NM_RAG_Paper.pdf`

### Troubleshooting on Overleaf:
- If images don't show: Check that the `results/figures/` folder structure is preserved
- If compilation fails: Look at the compilation log (red error icon)
- If bibliography warnings: Ignore on first compile, recompile once more

## Method 2: Compile Locally (Windows)

If you have LaTeX installed locally (MiKTeX or TeX Live):

### Steps:

```bash
cd "d:\SEM1_YR5_2025-26\Advanced Archeticture\Project paper"

# Compile (run twice for references)
pdflatex NM_RAG_Paper.tex
bibtex NM_RAG_Paper
pdflatex NM_RAG_Paper.tex
pdflatex NM_RAG_Paper.tex
```

**Output**: `NM_RAG_Paper.pdf` in the same directory

### Required LaTeX Packages:
- IEEEtran (conference class)
- cite
- amsmath, amssymb, amsfonts
- algorithmic
- graphicx
- textcomp
- xcolor
- float
- booktabs
- url

All these are included in standard LaTeX distributions.

## Method 3: Convert to Word (If Required)

Your submission says "MS Word or Overleaf" - if you need Word format:

### Option A: Pandoc Conversion (Partial)

```bash
pandoc NM_RAG_Paper.tex -o NM_RAG_Paper.docx --bibliography=references.bib
```

**Warning**: Pandoc conversion from LaTeX to Word is imperfect. Equations and figures may need manual adjustment.

### Option B: Use Overleaf Word Export (Experimental)

Some Overleaf plans offer "Rich Text" export to Word format. This is still experimental.

### Option C: Manually Recreate in Word (Most Control)

1. Compile to PDF first (Method 1 or 2)
2. Use the PDF as a visual reference
3. Recreate in Word with proper IEEE formatting
4. Copy-paste text sections from the .tex file (removing LaTeX commands)
5. Insert figures from `results/figures/`
6. Manually format equations using Word's equation editor

**Recommendation**: Submit the PDF from Overleaf. The assignment says "MS Word **or** Overleaf", and LaTeX/Overleaf is standard for computer architecture papers.

## Paper Structure (Verification Checklist)

Verify your compiled PDF includes all required sections:

- [x] Cover Page (title, authors, affiliations)
- [x] Abstract (150 words)
- [x] Introduction (problem statement, contributions)
- [x] Background (RAG, near-memory computing)
- [x] Related Work (IKS, MemANNS, NDSEARCH, FAISS, HNSW)
- [x] Proposed Solution (architecture with block diagrams)
- [x] Implementation & Experimental Setup (simulation framework)
- [x] Results & Discussion (performance, energy, quality, scalability)
- [x] Conclusion & Future Work
- [x] References (15 citations)

## Figures Included in Paper

1. **Figure 1**: System overview (Section IV-A)
2. **Figure 2**: NMPU detail (Section IV-B)
3. **Figure 3**: Pipeline diagram (Section IV-C)
4. **Figure 4**: Speedup comparison (Section VI-D)
5. **Figure 5**: Latency vs Quality tradeoff (Section VI-E)

Plus:
- **Table I**: Performance comparison (Section VI-A)
- **Table II**: Comparison with published systems (Section VI-G)

## Final Submission Checklist

Before submitting, ensure:

1. **PDF Compiles Successfully**
   - No compilation errors
   - All figures appear correctly
   - All references are linked

2. **Content Review**
   - All student names and IDs are correct
   - Abstract is under 300 words
   - All sections are complete
   - Figures have captions and labels

3. **Results Accuracy**
   - Results match the simulation output
   - Numbers in text match numbers in tables/figures
   - Claims are conservative and defensible

4. **Academic Integrity**
   - Results are realistic (0.48ms, 14.6x speedup)
   - Methodology is transparent (cycle-accurate simulation)
   - Limitations are acknowledged (simulation vs hardware)

## Quick Start (For Overleaf)

**Fastest path to PDF**:

1. Create ZIP:
   ```bash
   # On Windows PowerShell
   Compress-Archive -Path NM_RAG_Paper.tex,results -DestinationPath NM_RAG_Submission.zip
   ```

2. Upload to Overleaf: [overleaf.com](https://www.overleaf.com)

3. Download PDF

4. Submit!

## Support Files

Reference these files when defending your work:

- **FINAL_RESULTS_SUMMARY.md** - Contains defense strategies for common questions
- **detailed_results.json** - Full numerical results
- **comparison_table.csv** - Spreadsheet-friendly results

## Questions?

If you encounter issues:

1. Check that all figure files exist in `results/figures/`
2. Verify the LaTeX source has no syntax errors
3. Try compiling on Overleaf first (most reliable)
4. Check the Overleaf compilation log for specific errors

---

**Your paper is ready for submission. Good luck!** 🎓
