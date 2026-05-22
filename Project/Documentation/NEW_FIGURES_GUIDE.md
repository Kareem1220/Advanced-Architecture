# New Figures Integration Guide

## Overview
Generated 7 additional figures to enhance the NM-RAG paper with visual explanations of key concepts from the REFRAG and IKS papers.

---

## New Figures and Suggested Placements

### 1. **memory_bandwidth_analysis.png**
**Location**: Section 2.3 "The Memory-Compute Mismatch"
**Purpose**: Illustrates the roofline model showing ENNS operates in memory-bound region

**LaTeX Code**:
```latex
\begin{figure}[H]
\centering
\includegraphics[width=\columnwidth]{results/figures/memory_bandwidth_analysis.png}
\caption{(Left) Roofline model showing ENNS operates in the memory-bound region where NM-RAG's high bandwidth provides significant advantages. (Right) Memory bandwidth utilization comparison across different workload types.}
\label{fig:memory_bandwidth}
\end{figure}
```

**Key Insights**:
- Left panel: Roofline model with CPU vs HBM bandwidth
- Right panel: Bandwidth utilization for different kernels
- Shows why vector retrieval benefits more from near-memory than compute-bound workloads

---

### 2. **rag_pipeline_comparison.png**
**Location**: Section 1 "Introduction" or Section 7.1 "Comparison with Alternative Approaches"
**Purpose**: Shows how NM-RAG and REFRAG optimize different pipeline stages

**LaTeX Code**:
```latex
\begin{figure}[H]
\centering
\includegraphics[width=\columnwidth]{results/figures/rag_pipeline_comparison.png}
\caption{RAG pipeline stage latencies showing complementary optimizations: NM-RAG reduces retrieval time (7ms → 0.48ms) while REFRAG reduces prefill time (120ms → 4ms). Combining both approaches yields end-to-end TTFT reduction from 332ms to 209.5ms.}
\label{fig:rag_pipeline}
\end{figure}
```

**Key Insights**:
- Baseline: 332ms total TTFT
- NM-RAG alone: 325.5ms (retrieval optimized)
- REFRAG alone: 216ms (prefill optimized)
- Combined: 209.5ms (both stages optimized)
- Demonstrates complementary nature of approaches

---

### 3. **attention_pattern_visualization.png**
**Location**: Section 2.1 "Retrieval-Augmented Generation" or Related Work Section 3.4
**Purpose**: Visualizes block-diagonal attention patterns unique to RAG contexts

**LaTeX Code**:
```latex
\begin{figure}[H]
\centering
\includegraphics[width=\columnwidth]{results/figures/attention_pattern_visualization.png}
\caption{Attention pattern comparison: (Left) Standard LLM shows dense attention across all tokens. (Right) RAG contexts exhibit block-diagonal patterns where tokens attend primarily within their source passage, motivating compression-based optimizations like REFRAG.}
\label{fig:attention_patterns}
\end{figure}
```

**Key Insights**:
- Left: Dense attention in standard LLMs
- Right: Block-diagonal structure in RAG (passages marked with blue boundaries)
- Explains why REFRAG's chunk compression is effective
- Referenced in Introduction (line 63) and Background (line 110)

---

### 4. **hardware_comparison_radar.png**
**Location**: Section 7.1 "Comparison with Alternative Approaches" or Section 3.6 "Design Gap and Positioning"
**Purpose**: Multi-dimensional comparison of different RAG acceleration approaches

**LaTeX Code**:
```latex
\begin{figure*}[t]
\centering
\includegraphics[width=0.9\textwidth]{results/figures/hardware_comparison_radar.png}
\caption{Multi-dimensional comparison of RAG acceleration approaches across six key metrics. NM-RAG excels in throughput and energy efficiency while maintaining good retrieval quality. IKS provides best scalability, while ANN methods offer easier deployment at the cost of quality.}
\label{fig:radar_comparison}
\end{figure*}
```

**Metrics Compared**:
- Throughput: NM-RAG leads (1.0)
- Energy Efficiency: NM-RAG leads (1.0)
- Retrieval Quality: CPU/GPU/IKS perfect (1.0), NM-RAG good (0.76), ANN poor (0.3)
- Scalability: IKS leads (1.0), NM-RAG good (0.7)
- Cost Effectiveness: ANN leads (0.8), CPU good (0.7)
- Ease of Deployment: CPU leads (1.0), specialized hardware harder (0.3-0.5)

---

### 5. **quantization_tradeoff.png**
**Location**: Section 4.3 "Vector Quantization Strategy"
**Purpose**: Explains the quality-performance tradeoff in dimension reduction

**LaTeX Code**:
```latex
\begin{figure}[H]
\centering
\includegraphics[width=\columnwidth]{results/figures/quantization_tradeoff.png}
\caption{(Left) Quality and compression tradeoff across different embedding dimensions. The 128D choice (circled in red) balances 75.6\% recall with 3× compression. (Right) Memory footprint comparison showing NM-RAG's choice minimizes storage while preserving acceptable quality.}
\label{fig:quantization_tradeoff}
\end{figure}
```

**Key Data Points**:
- 32D: 35% recall, 6× compression (too aggressive)
- 64D: 45% recall, 5.5× compression
- **128D: 75.6% recall, 3× compression** ← NM-RAG choice
- 192D: 88% recall, 2× compression
- 384D: 100% recall, 1× compression (baseline)

---

### 6. **scalability_projection.png**
**Location**: Section 6.4 "Scalability Analysis"
**Purpose**: Shows how performance scales with corpus size

**LaTeX Code**:
```latex
\begin{figure}[H]
\centering
\includegraphics[width=\columnwidth]{results/figures/scalability_projection.png}
\caption{(Left) Query latency vs corpus size showing NM-RAG maintains sub-100ms interactive performance up to 10M documents while CPU/GPU exceed limits at 1M documents. (Right) Throughput scaling demonstrates NM-RAG's advantage grows with corpus size.}
\label{fig:scalability}
\end{figure}
```

**Key Insights**:
- Red dashed line: 100ms interactive limit
- NM-RAG stays below limit up to 10M documents
- CPU/GPU cross threshold at ~1M documents
- ANN methods have best scaling but poor quality
- NM-RAG advantage grows: 14.6× at 100K → 35.7× at 10M

---

### 7. **cxl_hbm_architecture_comparison.png**
**Location**: Section 3.2 "Hardware Acceleration for Vector Search" or Section 2.4 "Architectural Responses"
**Purpose**: Visual comparison of IKS CXL vs NM-RAG HBM architectures

**LaTeX Code**:
```latex
\begin{figure*}[t]
\centering
\includegraphics[width=0.9\textwidth]{results/figures/cxl_hbm_architecture_comparison.png}
\caption{Architecture comparison: (Left) IKS uses CXL type-2 memory expanders with LPDDR5X for 512GB capacity and scale-out deployment. (Right) NM-RAG uses HBM3 for compact 32GB design with aggressive quantization. Both achieve 900 GB/s bandwidth with 64 near-memory accelerators but target different deployment scenarios.}
\label{fig:cxl_hbm_comparison}
\end{figure*}
```

**Comparison Highlights**:

| Feature | IKS | NM-RAG |
|---------|-----|---------|
| Memory Type | LPDDR5X | HBM3 |
| Capacity | 512 GB | 32 GB |
| Bandwidth | 900 GB/s | 900 GB/s |
| Accelerators | 64 NMAs | 64 NMPUs |
| Power | 35-65W | 3W |
| Use Case | Enterprise scale-out | Edge/compact |
| Approach | Horizontal scaling | Vertical compression |

---

## Summary Statistics

### Total Figures: 16
- **Original**: 9 figures (8 PNG + 1 TEX table)
- **New**: 7 figures (all PNG)

### Coverage
1. ✅ Introduction concepts (TTFT, pipeline, attention)
2. ✅ Background theory (roofline, bandwidth)
3. ✅ Related work comparisons (IKS, REFRAG, multi-approach)
4. ✅ Architecture details (quantization tradeoffs)
5. ✅ Results analysis (scalability projections)
6. ✅ Discussion (complementary approaches)

### File Sizes
- Smallest: results_table.tex (595 bytes)
- Largest: hardware_comparison_radar.png (584 KB)
- Total: ~3.4 MB

---

## Integration Steps

1. **Add figure references to paper**:
   - Update `\includegraphics` paths in appropriate sections
   - Ensure `\label{}` references are unique
   - Add `\ref{fig:...}` citations in text

2. **Update submission package**:
   - Run `python create_submission_package.py` to include new figures
   - Verify all figures appear in the compiled PDF

3. **Text modifications**:
   - Reference new figures in relevant paragraphs
   - Example: "Figure~\ref{fig:rag_pipeline} shows how NM-RAG and REFRAG optimize complementary stages..."

4. **Check figure quality**:
   - All figures generated at 300 DPI (publication quality)
   - Color-blind friendly palettes used
   - Clear labels and legends

---

## Next Steps

1. Review each figure and decide which ones to include
2. Add LaTeX code to appropriate sections
3. Write figure descriptions in surrounding text
4. Regenerate submission package with new figures
5. Compile and verify PDF appearance
6. Consider moving some to appendix if page limit is tight

---

## Notes

- All figures use consistent color scheme:
  - NM-RAG: Green (#2ecc71)
  - CPU: Red (#e74c3c)
  - GPU: Blue (#3498db)
  - ANN: Orange (#f39c12)
  - IKS: Purple (#9b59b6)
  - REFRAG: Teal (#1abc9c)

- Figures are designed for IEEE conference paper format
- Two-column layouts use `\columnwidth`
- Full-width figures use `\textwidth` with `figure*` environment
