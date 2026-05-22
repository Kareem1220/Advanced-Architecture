"""
Generate additional figures for the NM-RAG paper
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

OUTPUT_DIR = "results/figures"

# Color scheme
COLORS = {
    'nmrag': '#2ecc71',
    'cpu': '#e74c3c',
    'gpu': '#3498db',
    'ann': '#f39c12',
    'iks': '#9b59b6',
    'refrag': '#1abc9c'
}

def figure1_memory_bandwidth_bottleneck():
    """Figure: Memory bandwidth bottleneck analysis"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Roofline model
    flops = np.logspace(-1, 3, 100)

    # CPU roofline
    peak_perf_cpu = 100  # GFLOPS
    bandwidth_cpu = 100  # GB/s
    roofline_cpu = np.minimum(peak_perf_cpu, bandwidth_cpu * flops)

    # HBM roofline
    peak_perf_hbm = 100  # GFLOPS (same compute)
    bandwidth_hbm = 900  # GB/s
    roofline_hbm = np.minimum(peak_perf_hbm, bandwidth_hbm * flops)

    ax1.loglog(flops, roofline_cpu, 'r-', linewidth=2, label='CPU (DDR5 100GB/s)')
    ax1.loglog(flops, roofline_hbm, 'g-', linewidth=2, label='NM-RAG (HBM3 900GB/s)')

    # Mark ENNS operating point (low arithmetic intensity)
    enns_intensity = 0.5  # FLOP/byte
    enns_perf_cpu = min(peak_perf_cpu, bandwidth_cpu * enns_intensity)
    enns_perf_hbm = min(peak_perf_hbm, bandwidth_hbm * enns_intensity)

    ax1.plot(enns_intensity, enns_perf_cpu, 'ro', markersize=12, label='ENNS on CPU')
    ax1.plot(enns_intensity, enns_perf_hbm, 'go', markersize=12, label='ENNS on NM-RAG')

    ax1.set_xlabel('Arithmetic Intensity (FLOP/byte)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Performance (GFLOPS)', fontsize=12, fontweight='bold')
    ax1.set_title('Roofline Model: Memory-Bound Region', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.axvline(x=enns_intensity, color='gray', linestyle='--', alpha=0.5)
    ax1.text(enns_intensity*1.2, 2, 'ENNS\nRegion', fontsize=10, style='italic')

    # Right: Bandwidth utilization
    categories = ['Vector\nRetrieval', 'Matrix\nMultiply', 'CNN\nConv', 'Transformer\nAttention']
    cpu_util = [15, 45, 65, 55]  # % of peak bandwidth
    nmrag_util = [40, 40, 40, 40]  # Conservative estimate for NM-RAG

    x = np.arange(len(categories))
    width = 0.35

    bars1 = ax2.bar(x - width/2, cpu_util, width, label='CPU/GPU', color=COLORS['cpu'], alpha=0.8)
    bars2 = ax2.bar(x + width/2, nmrag_util, width, label='NM-RAG', color=COLORS['nmrag'], alpha=0.8)

    ax2.set_ylabel('Bandwidth Utilization (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Memory Bandwidth Efficiency', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, fontsize=10)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, 100)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}%', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/memory_bandwidth_analysis.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Generated: memory_bandwidth_analysis.png")
    plt.close()


def figure2_rag_pipeline_comparison():
    """Figure: Comparison of RAG pipeline optimizations"""
    fig, ax = plt.subplots(figsize=(14, 8))

    # Timeline components
    stages = ['Query\nEncoding', 'Vector\nRetrieval', 'Context\nPrefill', 'Token\nGeneration']

    # Baseline timings (ms)
    baseline = [5, 7, 120, 200]
    nmrag = [5, 0.48, 120, 200]  # Only retrieval improved
    refrag = [5, 7, 4, 200]  # Only prefill improved
    combined = [5, 0.48, 4, 200]  # Both optimizations

    y_pos = np.arange(4)
    height = 0.18

    # Plot bars
    ax.barh(y_pos - 1.5*height, baseline, height, label='Baseline', color=COLORS['cpu'], alpha=0.8)
    ax.barh(y_pos - 0.5*height, nmrag, height, label='NM-RAG (Retrieval opt.)', color=COLORS['nmrag'], alpha=0.8)
    ax.barh(y_pos + 0.5*height, refrag, height, label='REFRAG (Prefill opt.)', color=COLORS['refrag'], alpha=0.8)
    ax.barh(y_pos + 1.5*height, combined, height, label='Combined (Both)', color='#e67e22', alpha=0.8)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(stages, fontsize=11)
    ax.set_xlabel('Latency (ms, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('RAG Pipeline Stage Latencies: Complementary Optimizations', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3, axis='x')

    # Add total time annotations
    totals = [sum(baseline), sum(nmrag), sum(refrag), sum(combined)]
    labels = [f'Total: {t:.1f}ms' for t in totals]
    colors_list = [COLORS['cpu'], COLORS['nmrag'], COLORS['refrag'], '#e67e22']

    for i, (total, label, color) in enumerate(zip(totals, labels, colors_list)):
        ax.text(350, y_pos[0] + (i-1.5)*height, label,
               fontsize=10, fontweight='bold', color=color,
               verticalalignment='center')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/rag_pipeline_comparison.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Generated: rag_pipeline_comparison.png")
    plt.close()


def figure3_attention_pattern_visualization():
    """Figure: Block-diagonal attention patterns in RAG"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Create synthetic attention patterns
    seq_len = 64

    # Standard dense attention
    dense_attention = np.random.rand(seq_len, seq_len)
    dense_attention = (dense_attention + dense_attention.T) / 2  # Symmetric
    dense_attention = dense_attention / dense_attention.sum(axis=1, keepdims=True)  # Normalize

    # Block-diagonal RAG attention
    block_size = 16
    rag_attention = np.zeros((seq_len, seq_len))
    num_blocks = seq_len // block_size

    for i in range(num_blocks):
        start = i * block_size
        end = (i + 1) * block_size
        block = np.random.rand(block_size, block_size) * 0.8 + 0.2
        block = (block + block.T) / 2
        rag_attention[start:end, start:end] = block

    # Add small cross-block attention
    rag_attention += np.random.rand(seq_len, seq_len) * 0.05
    rag_attention = rag_attention / rag_attention.sum(axis=1, keepdims=True)

    # Plot dense attention
    im1 = ax1.imshow(dense_attention, cmap='YlOrRd', aspect='auto', interpolation='nearest')
    ax1.set_title('Standard LLM Attention\n(Dense, Full Context)', fontsize=13, fontweight='bold')
    ax1.set_xlabel('Key Position', fontsize=11)
    ax1.set_ylabel('Query Position', fontsize=11)
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

    # Plot RAG attention
    im2 = ax2.imshow(rag_attention, cmap='YlOrRd', aspect='auto', interpolation='nearest')
    ax2.set_title('RAG Context Attention\n(Block-Diagonal, Passage-Local)', fontsize=13, fontweight='bold')
    ax2.set_xlabel('Key Position', fontsize=11)
    ax2.set_ylabel('Query Position', fontsize=11)
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

    # Add passage boundaries to RAG plot
    for i in range(1, num_blocks):
        pos = i * block_size
        ax2.axhline(y=pos, color='blue', linewidth=2, linestyle='--', alpha=0.6)
        ax2.axvline(x=pos, color='blue', linewidth=2, linestyle='--', alpha=0.6)

    # Add text annotations
    ax2.text(8, 8, 'Passage 1', fontsize=9, color='white', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='blue', alpha=0.7))
    ax2.text(24, 24, 'Passage 2', fontsize=9, color='white', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='blue', alpha=0.7))
    ax2.text(40, 40, 'Passage 3', fontsize=9, color='white', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='blue', alpha=0.7))
    ax2.text(56, 56, 'Passage 4', fontsize=9, color='white', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='blue', alpha=0.7))

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/attention_pattern_visualization.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Generated: attention_pattern_visualization.png")
    plt.close()


def figure4_hardware_comparison_radar():
    """Figure: Radar chart comparing different approaches"""
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

    # Metrics (normalized 0-1, higher is better)
    categories = ['Throughput', 'Energy\nEfficiency', 'Retrieval\nQuality',
                  'Scalability', 'Cost\nEffectiveness', 'Ease of\nDeployment']
    N = len(categories)

    # Scores for each approach
    approaches = {
        'CPU Baseline': [0.1, 0.1, 1.0, 0.3, 0.7, 1.0],
        'GPU': [0.3, 0.05, 1.0, 0.4, 0.3, 0.7],
        'ANN (HNSW)': [0.6, 0.3, 0.3, 0.6, 0.8, 0.9],
        'NM-RAG': [1.0, 1.0, 0.76, 0.7, 0.6, 0.5],
        'IKS': [0.9, 0.7, 1.0, 1.0, 0.4, 0.3],
    }

    # Compute angle for each axis
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    # Plot each approach
    colors_list = [COLORS['cpu'], COLORS['gpu'], COLORS['ann'], COLORS['nmrag'], COLORS['iks']]

    for (approach, values), color in zip(approaches.items(), colors_list):
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=approach, color=color, markersize=6)
        ax.fill(angles, values, alpha=0.15, color=color)

    # Fix axis to go in the right order
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
    plt.title('Multi-Dimensional Comparison of RAG Acceleration Approaches',
             fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/hardware_comparison_radar.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Generated: hardware_comparison_radar.png")
    plt.close()


def figure5_quantization_tradeoff():
    """Figure: Quantization quality-performance tradeoff"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Recall vs Dimension
    dimensions = [32, 64, 96, 128, 160, 192, 256, 384]
    recall = [0.35, 0.45, 0.62, 0.756, 0.82, 0.88, 0.92, 1.0]
    speedup = [6.0, 5.5, 4.8, 3.0, 2.5, 2.0, 1.5, 1.0]

    ax1_twin = ax1.twinx()

    line1 = ax1.plot(dimensions, recall, 'o-', linewidth=2, markersize=8,
                     color=COLORS['nmrag'], label='Recall@100')
    line2 = ax1_twin.plot(dimensions, speedup, 's-', linewidth=2, markersize=8,
                          color=COLORS['cpu'], label='Compression Factor')

    # Highlight the chosen point
    ax1.plot(128, 0.756, 'o', markersize=15, color='red',
            markerfacecolor='none', markeredgewidth=3, label='NM-RAG Choice (128D)')

    ax1.set_xlabel('Embedding Dimension', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Recall@100', fontsize=12, fontweight='bold', color=COLORS['nmrag'])
    ax1_twin.set_ylabel('Compression Factor', fontsize=12, fontweight='bold', color=COLORS['cpu'])
    ax1.set_title('Dimension Reduction: Quality-Performance Tradeoff', fontsize=13, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=COLORS['nmrag'])
    ax1_twin.tick_params(axis='y', labelcolor=COLORS['cpu'])
    ax1.grid(True, alpha=0.3)

    # Combine legends
    lines = line1 + line2 + [ax1.get_children()[1]]  # Add the highlight
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center left', fontsize=10)

    # Right: Memory footprint comparison
    methods = ['Full\n384D', 'PCA\n256D', 'PCA\n192D', 'NM-RAG\n128D', 'Aggressive\n64D']
    memory_mb = [1536, 1024, 768, 512, 256]  # MB per 1M documents
    quality = [100, 92, 88, 75.6, 45]

    colors_gradient = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(methods)))

    bars = ax2.bar(methods, memory_mb, color=colors_gradient, alpha=0.8, edgecolor='black', linewidth=1.5)

    # Add quality labels on bars
    for bar, qual in zip(bars, quality):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 50,
                f'{qual}%\nquality', ha='center', fontsize=9, fontweight='bold')

    # Highlight NM-RAG choice
    bars[3].set_edgecolor('red')
    bars[3].set_linewidth(3)

    ax2.set_ylabel('Memory Footprint (MB per 1M docs)', fontsize=12, fontweight='bold')
    ax2.set_title('Memory vs Quality Tradeoff', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, 1800)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/quantization_tradeoff.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Generated: quantization_tradeoff.png")
    plt.close()


def figure6_scalability_projection():
    """Figure: Scalability with corpus size"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Latency vs corpus size
    corpus_sizes = np.array([1e3, 1e4, 1e5, 1e6, 1e7])

    cpu_latency = 7 * (corpus_sizes / 1e5)  # Linear scaling
    gpu_latency = 6.78 * (corpus_sizes / 1e5)
    ann_latency = 1.59 * (corpus_sizes / 1e5) ** 0.7  # Sublinear (graph indexing)
    nmrag_latency = 0.48 * (corpus_sizes / 1e5) ** 0.95  # Nearly linear but much lower base

    ax1.loglog(corpus_sizes, cpu_latency, 'o-', linewidth=2, markersize=6,
              label='CPU', color=COLORS['cpu'])
    ax1.loglog(corpus_sizes, gpu_latency, 's-', linewidth=2, markersize=6,
              label='GPU', color=COLORS['gpu'])
    ax1.loglog(corpus_sizes, ann_latency, '^-', linewidth=2, markersize=6,
              label='ANN (HNSW)', color=COLORS['ann'])
    ax1.loglog(corpus_sizes, nmrag_latency, 'd-', linewidth=2, markersize=6,
              label='NM-RAG', color=COLORS['nmrag'])

    # Add 100ms interactive threshold
    ax1.axhline(y=100, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Interactive Limit (100ms)')

    ax1.set_xlabel('Corpus Size (documents)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Query Latency (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('Scalability: Latency vs Corpus Size', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Right: Throughput (QPS) vs corpus size
    cpu_qps = 1000 / cpu_latency
    gpu_qps = 1000 / gpu_latency
    ann_qps = 1000 / ann_latency
    nmrag_qps = 1000 / nmrag_latency

    ax2.loglog(corpus_sizes, cpu_qps, 'o-', linewidth=2, markersize=6,
              label='CPU', color=COLORS['cpu'])
    ax2.loglog(corpus_sizes, gpu_qps, 's-', linewidth=2, markersize=6,
              label='GPU', color=COLORS['gpu'])
    ax2.loglog(corpus_sizes, ann_qps, '^-', linewidth=2, markersize=6,
              label='ANN (HNSW)', color=COLORS['ann'])
    ax2.loglog(corpus_sizes, nmrag_qps, 'd-', linewidth=2, markersize=6,
              label='NM-RAG', color=COLORS['nmrag'])

    ax2.set_xlabel('Corpus Size (documents)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Throughput (QPS)', fontsize=12, fontweight='bold')
    ax2.set_title('Scalability: Throughput vs Corpus Size', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/scalability_projection.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Generated: scalability_projection.png")
    plt.close()


def figure7_cxl_architecture_comparison():
    """Figure: CXL vs HBM architecture comparison"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Turn off axes
    ax1.axis('off')
    ax2.axis('off')

    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)

    # Left: IKS CXL Architecture
    ax1.text(5, 9.5, 'IKS: CXL Type-2 Architecture', ha='center', fontsize=14, fontweight='bold')

    # Host CPU
    cpu_box = FancyBboxPatch((0.5, 7), 2, 1.5, boxstyle="round,pad=0.1",
                            edgecolor='black', facecolor=COLORS['iks'], linewidth=2)
    ax1.add_patch(cpu_box)
    ax1.text(1.5, 7.75, 'Host CPU', ha='center', fontsize=11, fontweight='bold')

    # CXL Link
    arrow1 = FancyArrowPatch((2.5, 7.75), (4, 7.75), arrowstyle='->', mutation_scale=20,
                            linewidth=3, color='blue')
    ax1.add_patch(arrow1)
    ax1.text(3.25, 8.2, 'CXL 2.0', ha='center', fontsize=9, style='italic')

    # CXL Memory Expander
    cxl_box = FancyBboxPatch((4, 6.5), 5.5, 2.5, boxstyle="round,pad=0.1",
                            edgecolor='black', facecolor='lightblue', linewidth=2)
    ax1.add_patch(cxl_box)
    ax1.text(6.75, 8.5, 'CXL Type-2 Device', ha='center', fontsize=11, fontweight='bold')

    # LPDDR5X packages
    for i in range(4):
        mem_box = Rectangle((4.5 + i*1.2, 7.2), 0.8, 0.8,
                           edgecolor='black', facecolor='#95a5a6', linewidth=1)
        ax1.add_patch(mem_box)
        ax1.text(4.9 + i*1.2, 7.6, f'LP{i+1}', ha='center', fontsize=8)

    # Near-Memory Accelerators
    ax1.text(6.75, 6.9, '64 × Near-Memory Accelerators', ha='center', fontsize=9, style='italic')

    # Capacity and bandwidth
    ax1.text(1, 5.5, 'Capacity: 512 GB', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax1.text(1, 5, 'Bandwidth: 900 GB/s', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax1.text(1, 4.5, 'Power: 35-65 W', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax1.text(1, 4, 'Use Case: Scale-out', fontsize=10, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.6))

    # Right: NM-RAG HBM Architecture
    ax2.text(5, 9.5, 'NM-RAG: HBM3 Architecture', ha='center', fontsize=14, fontweight='bold')

    # Host Interface
    host_box = FancyBboxPatch((0.5, 7), 2, 1.5, boxstyle="round,pad=0.1",
                             edgecolor='black', facecolor=COLORS['nmrag'], linewidth=2)
    ax2.add_patch(host_box)
    ax2.text(1.5, 7.75, 'Host\nInterface', ha='center', fontsize=11, fontweight='bold')

    # HBM3 Stack
    hbm_box = FancyBboxPatch((4, 6), 5.5, 3.5, boxstyle="round,pad=0.1",
                            edgecolor='black', facecolor='lightgreen', linewidth=2)
    ax2.add_patch(hbm_box)
    ax2.text(6.75, 9, 'HBM3 Memory', ha='center', fontsize=11, fontweight='bold')

    # HBM stacks
    for i in range(8):
        x_pos = 4.5 + (i % 4) * 1.2
        y_pos = 8.2 if i < 4 else 7
        stack_box = Rectangle((x_pos, y_pos), 0.8, 0.8,
                             edgecolor='black', facecolor='#27ae60', linewidth=1)
        ax2.add_patch(stack_box)
        ax2.text(x_pos + 0.4, y_pos + 0.4, f'S{i+1}', ha='center', fontsize=8)

    # NMPUs
    ax2.text(6.75, 6.4, '64 × NMPUs (Near-Memory Processing Units)',
            ha='center', fontsize=9, style='italic')

    # Capacity and bandwidth
    ax2.text(1, 5.5, 'Capacity: 32 GB', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax2.text(1, 5, 'Bandwidth: 900 GB/s', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax2.text(1, 4.5, 'Power: 3 W', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax2.text(1, 4, 'Use Case: Edge/Compact', fontsize=10, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.6))

    # Add comparison arrows
    ax2.text(5, 2, 'Key Differences:', ha='center', fontsize=11, fontweight='bold')
    ax2.text(5, 1.5, '• IKS: Large capacity (512GB), CXL composability, enterprise scale',
            ha='center', fontsize=9)
    ax2.text(5, 1, '• NM-RAG: Compact (32GB), HBM bandwidth, aggressive quantization',
            ha='center', fontsize=9)
    ax2.text(5, 0.5, '• Both: 900 GB/s bandwidth, 64 accelerators, near-memory processing',
            ha='center', fontsize=9, style='italic', color='blue')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/cxl_hbm_architecture_comparison.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Generated: cxl_hbm_architecture_comparison.png")
    plt.close()


def main():
    """Generate all additional figures"""
    print("\n" + "="*60)
    print("Generating Additional Figures for NM-RAG Paper")
    print("="*60 + "\n")

    figure1_memory_bandwidth_bottleneck()
    figure2_rag_pipeline_comparison()
    figure3_attention_pattern_visualization()
    figure4_hardware_comparison_radar()
    figure5_quantization_tradeoff()
    figure6_scalability_projection()
    figure7_cxl_architecture_comparison()

    print("\n" + "="*60)
    print("All additional figures generated successfully!")
    print("="*60 + "\n")
    print("New figures:")
    print("  1. memory_bandwidth_analysis.png - Roofline model & bandwidth utilization")
    print("  2. rag_pipeline_comparison.png - TTFT breakdown for different optimizations")
    print("  3. attention_pattern_visualization.png - Block-diagonal attention in RAG")
    print("  4. hardware_comparison_radar.png - Multi-dimensional approach comparison")
    print("  5. quantization_tradeoff.png - Quality-performance tradeoffs")
    print("  6. scalability_projection.png - Corpus size scaling analysis")
    print("  7. cxl_hbm_architecture_comparison.png - IKS vs NM-RAG architecture")
    print("\n")


if __name__ == "__main__":
    main()
