"""
Generate block diagrams for NM-RAG paper
Creates system architecture diagrams for the Proposed Solution section
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
import numpy as np

# Set publication quality
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10

def create_system_overview():
    """Create high-level system architecture diagram"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Title
    ax.text(5, 5.7, 'NM-RAG System Architecture',
            ha='center', va='top', fontsize=14, fontweight='bold')

    # Host CPU
    host = FancyBboxPatch((0.5, 4.0), 1.5, 1.2,
                          boxstyle="round,pad=0.1",
                          edgecolor='black', facecolor='lightblue', linewidth=2)
    ax.add_patch(host)
    ax.text(1.25, 4.6, 'Host CPU', ha='center', va='center', fontweight='bold')
    ax.text(1.25, 4.3, 'Query\nEmbedding', ha='center', va='center', fontsize=8)

    # CXL Interface
    cxl = FancyBboxPatch((2.5, 4.2), 1.2, 0.8,
                         boxstyle="round,pad=0.05",
                         edgecolor='darkgreen', facecolor='lightgreen', linewidth=2)
    ax.add_patch(cxl)
    ax.text(3.1, 4.6, 'CXL 3.0', ha='center', va='center', fontweight='bold')
    ax.text(3.1, 4.35, 'Interface', ha='center', va='center', fontsize=8)

    # Arrow: Host -> CXL
    arrow1 = FancyArrowPatch((2.0, 4.6), (2.5, 4.6),
                            arrowstyle='->', mutation_scale=20,
                            linewidth=2, color='black')
    ax.add_patch(arrow1)

    # NM-RAG Accelerator Box
    accelerator = Rectangle((4.2, 0.5), 5.3, 5.0,
                           edgecolor='darkred', facecolor='none',
                           linewidth=3, linestyle='--')
    ax.add_patch(accelerator)
    ax.text(6.8, 5.3, 'NM-RAG Accelerator',
            ha='center', va='center', fontsize=12, fontweight='bold', color='darkred')

    # Arrow: CXL -> Accelerator
    arrow2 = FancyArrowPatch((3.7, 4.6), (4.2, 4.6),
                            arrowstyle='->', mutation_scale=20,
                            linewidth=2, color='black')
    ax.add_patch(arrow2)

    # Control Unit
    control = FancyBboxPatch((4.5, 4.2), 1.3, 0.8,
                            boxstyle="round,pad=0.05",
                            edgecolor='black', facecolor='wheat', linewidth=2)
    ax.add_patch(control)
    ax.text(5.15, 4.6, 'Control Unit', ha='center', va='center', fontweight='bold', fontsize=9)
    ax.text(5.15, 4.35, 'Query Broadcast', ha='center', va='center', fontsize=7)

    # Near-Memory Processing Units (NMPU Array)
    nmpu_start_y = 2.3
    nmpu_height = 1.5
    nmpu_width = 4.8

    nmpu_box = FancyBboxPatch((4.5, nmpu_start_y), nmpu_width, nmpu_height,
                             boxstyle="round,pad=0.1",
                             edgecolor='darkblue', facecolor='lightcyan', linewidth=2)
    ax.add_patch(nmpu_box)
    ax.text(6.9, nmpu_start_y + nmpu_height - 0.15, '64 Near-Memory Processing Units (NMPUs)',
            ha='center', va='center', fontweight='bold', fontsize=9)

    # Individual NMPUs (show 4 representative units)
    nmpu_positions = [4.7, 5.8, 6.9, 8.0]
    for i, x_pos in enumerate(nmpu_positions):
        nmpu = FancyBboxPatch((x_pos, nmpu_start_y + 0.2), 0.9, 1.0,
                             boxstyle="round,pad=0.05",
                             edgecolor='blue', facecolor='aliceblue', linewidth=1.5)
        ax.add_patch(nmpu)
        ax.text(x_pos + 0.45, nmpu_start_y + 0.95, f'NMPU{i}',
                ha='center', va='center', fontsize=7, fontweight='bold')
        ax.text(x_pos + 0.45, nmpu_start_y + 0.70, 'Vector',
                ha='center', va='center', fontsize=6)
        ax.text(x_pos + 0.45, nmpu_start_y + 0.55, 'Engine',
                ha='center', va='center', fontsize=6)
        ax.text(x_pos + 0.45, nmpu_start_y + 0.35, '64KB',
                ha='center', va='center', fontsize=6)
        ax.text(x_pos + 0.45, nmpu_start_y + 0.20, 'Buffer',
                ha='center', va='center', fontsize=6)

        if i < len(nmpu_positions) - 1:
            ax.text(x_pos + 0.95, nmpu_start_y + 0.7, '...',
                   ha='center', va='center', fontsize=10, fontweight='bold')

    # Arrows: Control -> NMPUs
    for x_pos in nmpu_positions:
        arrow = FancyArrowPatch((5.15, 4.2), (x_pos + 0.45, nmpu_start_y + nmpu_height),
                               arrowstyle='->', mutation_scale=15,
                               linewidth=1, color='gray', alpha=0.6)
        ax.add_patch(arrow)

    # HBM3 Memory Banks
    hbm_start_y = 0.7
    hbm_height = 1.2

    hbm_box = FancyBboxPatch((4.5, hbm_start_y), nmpu_width, hbm_height,
                            boxstyle="round,pad=0.1",
                            edgecolor='darkgreen', facecolor='lightgreen', linewidth=2)
    ax.add_patch(hbm_box)
    ax.text(6.9, hbm_start_y + hbm_height - 0.15, 'HBM3 Memory (32GB, 900 GB/s)',
            ha='center', va='center', fontweight='bold', fontsize=9)

    # Memory banks
    bank_positions = [4.7, 5.8, 6.9, 8.0]
    for i, x_pos in enumerate(bank_positions):
        bank = Rectangle((x_pos, hbm_start_y + 0.15), 0.9, 0.8,
                        edgecolor='darkgreen', facecolor='honeydew', linewidth=1.5)
        ax.add_patch(bank)
        ax.text(x_pos + 0.45, hbm_start_y + 0.7, f'Bank {i}',
                ha='center', va='center', fontsize=7, fontweight='bold')
        ax.text(x_pos + 0.45, hbm_start_y + 0.45, '14 GB/s',
                ha='center', va='center', fontsize=6)
        ax.text(x_pos + 0.45, hbm_start_y + 0.25, 'Documents',
                ha='center', va='center', fontsize=6)

        if i < len(bank_positions) - 1:
            ax.text(x_pos + 0.95, hbm_start_y + 0.55, '...',
                   ha='center', va='center', fontsize=10, fontweight='bold')

    # Bidirectional arrows: NMPUs <-> Memory Banks
    for i, x_pos in enumerate(nmpu_positions):
        arrow_down = FancyArrowPatch((x_pos + 0.45, nmpu_start_y + 0.2),
                                    (x_pos + 0.45, hbm_start_y + hbm_height),
                                    arrowstyle='<->', mutation_scale=15,
                                    linewidth=2, color='blue')
        ax.add_patch(arrow_down)

    # Top-K Selection Unit
    topk = FancyBboxPatch((6.2, 4.2), 1.3, 0.8,
                         boxstyle="round,pad=0.05",
                         edgecolor='black', facecolor='lightyellow', linewidth=2)
    ax.add_patch(topk)
    ax.text(6.85, 4.6, 'Top-K', ha='center', va='center', fontweight='bold', fontsize=9)
    ax.text(6.85, 4.35, 'Selection', ha='center', va='center', fontsize=7)

    # Arrows: NMPUs -> Top-K
    for x_pos in nmpu_positions:
        arrow = FancyArrowPatch((x_pos + 0.45, nmpu_start_y + nmpu_height),
                               (6.85, 4.2),
                               arrowstyle='->', mutation_scale=15,
                               linewidth=1, color='gray', alpha=0.6)
        ax.add_patch(arrow)

    # Arrow: Top-K -> Output
    arrow_out = FancyArrowPatch((7.5, 4.6), (8.5, 4.6),
                               arrowstyle='->', mutation_scale=20,
                               linewidth=2, color='black')
    ax.add_patch(arrow_out)
    ax.text(8.0, 4.9, 'Top-100\nResults', ha='center', va='center', fontsize=7)

    plt.tight_layout()
    plt.savefig('results/figures/system_overview.png', bbox_inches='tight', dpi=300)
    print("[OK] Generated: system_overview.png")
    plt.close()


def create_nmpu_detail():
    """Create detailed NMPU architecture diagram"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Title
    ax.text(5, 7.7, 'Near-Memory Processing Unit (NMPU) Architecture',
            ha='center', va='top', fontsize=14, fontweight='bold')

    # Main NMPU boundary
    nmpu_box = Rectangle((0.5, 0.5), 9, 6.8,
                         edgecolor='darkblue', facecolor='none',
                         linewidth=3, linestyle='--')
    ax.add_patch(nmpu_box)

    # Memory Controller
    mem_ctrl = FancyBboxPatch((1, 5.5), 2.5, 1.2,
                              boxstyle="round,pad=0.1",
                              edgecolor='darkgreen', facecolor='lightgreen', linewidth=2)
    ax.add_patch(mem_ctrl)
    ax.text(2.25, 6.5, 'Memory Controller', ha='center', va='center', fontweight='bold')
    ax.text(2.25, 6.1, 'HBM Bank Access', ha='center', va='center', fontsize=8)
    ax.text(2.25, 5.8, '14 GB/s bandwidth', ha='center', va='center', fontsize=7, style='italic')

    # Local Buffer (64KB)
    buffer = FancyBboxPatch((4.5, 5.5), 2.5, 1.2,
                           boxstyle="round,pad=0.1",
                           edgecolor='purple', facecolor='lavender', linewidth=2)
    ax.add_patch(buffer)
    ax.text(5.75, 6.5, 'Local Buffer', ha='center', va='center', fontweight='bold')
    ax.text(5.75, 6.1, '64 KB Scratchpad', ha='center', va='center', fontsize=8)
    ax.text(5.75, 5.8, 'Query + Intermediates', ha='center', va='center', fontsize=7, style='italic')

    # Arrow: Mem Controller -> Buffer
    arrow1 = FancyArrowPatch((3.5, 6.1), (4.5, 6.1),
                            arrowstyle='->', mutation_scale=20,
                            linewidth=2, color='black')
    ax.add_patch(arrow1)
    ax.text(4.0, 6.4, 'Load', ha='center', va='bottom', fontsize=7)

    # Vector Engine
    vector_engine = FancyBboxPatch((1, 3.0), 6, 2.0,
                                   boxstyle="round,pad=0.15",
                                   edgecolor='darkred', facecolor='mistyrose', linewidth=2)
    ax.add_patch(vector_engine)
    ax.text(4.0, 4.7, 'Vector Engine (256-bit SIMD)',
            ha='center', va='center', fontweight='bold', fontsize=11)

    # SIMD lanes
    lane_y = 3.4
    lane_width = 1.2
    lane_height = 0.9
    lane_positions = [1.3, 2.7, 4.1, 5.5]

    for i, x_pos in enumerate(lane_positions):
        lane = FancyBboxPatch((x_pos, lane_y), lane_width, lane_height,
                             boxstyle="round,pad=0.05",
                             edgecolor='red', facecolor='white', linewidth=1.5)
        ax.add_patch(lane)
        ax.text(x_pos + lane_width/2, lane_y + 0.65, f'Lane {i}',
                ha='center', va='center', fontsize=8, fontweight='bold')
        ax.text(x_pos + lane_width/2, lane_y + 0.35, '8x INT8',
                ha='center', va='center', fontsize=7)
        ax.text(x_pos + lane_width/2, lane_y + 0.15, 'MAC Units',
                ha='center', va='center', fontsize=7)

    ax.text(4.0, 3.2, '32 elements/cycle (4 lanes × 8 elements)',
            ha='center', va='center', fontsize=7, style='italic')

    # Arrow: Buffer -> Vector Engine
    arrow2 = FancyArrowPatch((5.75, 5.5), (4.5, 5.0),
                            arrowstyle='->', mutation_scale=20,
                            linewidth=2, color='black')
    ax.add_patch(arrow2)

    # Accumulator
    accumulator = FancyBboxPatch((7.5, 3.5), 1.8, 1.0,
                                boxstyle="round,pad=0.08",
                                edgecolor='orange', facecolor='lightyellow', linewidth=2)
    ax.add_patch(accumulator)
    ax.text(8.4, 4.2, 'Accumulator', ha='center', va='center', fontweight='bold', fontsize=9)
    ax.text(8.4, 3.8, '32-bit\nAdder Tree', ha='center', va='center', fontsize=7)

    # Arrow: Vector Engine -> Accumulator
    arrow3 = FancyArrowPatch((7.0, 4.0), (7.5, 4.0),
                            arrowstyle='->', mutation_scale=20,
                            linewidth=2, color='black')
    ax.add_patch(arrow3)

    # Top-K Tracker
    topk = FancyBboxPatch((7.5, 1.8), 1.8, 1.2,
                         boxstyle="round,pad=0.08",
                         edgecolor='blue', facecolor='lightblue', linewidth=2)
    ax.add_patch(topk)
    ax.text(8.4, 2.7, 'Local Top-K', ha='center', va='center', fontweight='bold', fontsize=9)
    ax.text(8.4, 2.35, 'Priority Queue', ha='center', va='center', fontsize=7)
    ax.text(8.4, 2.05, '(K=100)', ha='center', va='center', fontsize=7, style='italic')

    # Arrow: Accumulator -> Top-K
    arrow4 = FancyArrowPatch((8.4, 3.5), (8.4, 3.0),
                            arrowstyle='->', mutation_scale=20,
                            linewidth=2, color='black')
    ax.add_patch(arrow4)
    ax.text(8.8, 3.25, 'Score', ha='left', va='center', fontsize=7)

    # Control Logic
    control = FancyBboxPatch((1, 1.3), 2.5, 1.2,
                            boxstyle="round,pad=0.08",
                            edgecolor='black', facecolor='wheat', linewidth=2)
    ax.add_patch(control)
    ax.text(2.25, 2.2, 'Control Logic', ha='center', va='center', fontweight='bold', fontsize=9)
    ax.text(2.25, 1.8, 'Pipeline Control', ha='center', va='center', fontsize=7)
    ax.text(2.25, 1.5, 'FSM', ha='center', va='center', fontsize=7)

    # Control arrows (dashed)
    for component_y in [6.1, 4.0, 2.4]:
        arrow = FancyArrowPatch((3.5, 1.9), (1.0 if component_y == 6.1 else 4.0, component_y),
                               arrowstyle='->', mutation_scale=15,
                               linewidth=1, color='gray', linestyle='--', alpha=0.5)
        ax.add_patch(arrow)

    # Output to Global Top-K
    output_box = FancyBboxPatch((7.5, 0.5), 1.8, 0.6,
                               boxstyle="round,pad=0.05",
                               edgecolor='darkblue', facecolor='lightcyan', linewidth=1.5)
    ax.add_patch(output_box)
    ax.text(8.4, 0.8, 'To Global Top-K', ha='center', va='center', fontsize=8, fontweight='bold')

    # Arrow: Local Top-K -> Output
    arrow5 = FancyArrowPatch((8.4, 1.8), (8.4, 1.1),
                            arrowstyle='->', mutation_scale=20,
                            linewidth=2, color='black')
    ax.add_patch(arrow5)

    # Annotations
    ax.text(5, 0.2, 'Processing: 128D × 8-bit quantized embeddings | 4 cycles per dot product',
            ha='center', va='center', fontsize=8, style='italic',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()
    plt.savefig('results/figures/nmpu_detail.png', bbox_inches='tight', dpi=300)
    print("[OK] Generated: nmpu_detail.png")
    plt.close()


def create_pipeline_diagram():
    """Create query processing pipeline diagram"""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # Title
    ax.text(5.5, 4.8, 'Query Processing Pipeline',
            ha='center', va='top', fontsize=14, fontweight='bold')

    stages = [
        ('Query\nEmbedding', 'Host CPU', 0.5, 'lightblue'),
        ('PCA\nQuantization', '384D→128D', 2.5, 'lightgreen'),
        ('Query\nBroadcast', 'To 64 NMPUs', 4.5, 'wheat'),
        ('Parallel\nSimilarity', '100K docs', 6.5, 'mistyrose'),
        ('Top-K\nMerge', 'K=100', 8.5, 'lightyellow'),
        ('Result\nReturn', 'Doc IDs', 10.0, 'lightcyan')
    ]

    y_center = 2.5
    box_width = 1.5
    box_height = 1.2

    for i, (title, subtitle, x_pos, color) in enumerate(stages):
        # Stage box
        stage_box = FancyBboxPatch((x_pos, y_center - box_height/2),
                                   box_width, box_height,
                                   boxstyle="round,pad=0.1",
                                   edgecolor='black', facecolor=color, linewidth=2)
        ax.add_patch(stage_box)

        # Title
        ax.text(x_pos + box_width/2, y_center + 0.3, title,
                ha='center', va='center', fontweight='bold', fontsize=9)

        # Subtitle
        ax.text(x_pos + box_width/2, y_center - 0.2, subtitle,
                ha='center', va='center', fontsize=7, style='italic')

        # Stage number
        ax.text(x_pos + box_width/2, y_center - box_height/2 - 0.3, f'Stage {i+1}',
                ha='center', va='top', fontsize=7, color='gray')

        # Arrow to next stage
        if i < len(stages) - 1:
            arrow = FancyArrowPatch((x_pos + box_width, y_center),
                                   (stages[i+1][2], y_center),
                                   arrowstyle='->', mutation_scale=20,
                                   linewidth=2, color='black')
            ax.add_patch(arrow)

    # Timing annotations
    timings = ['~10μs', '~5μs', '~2μs', '~450μs', '~10μs', '~1μs']
    for i, (stage, timing) in enumerate(zip(stages, timings)):
        x_pos = stage[2]
        ax.text(x_pos + box_width/2, y_center + box_height/2 + 0.3, timing,
                ha='center', va='bottom', fontsize=7, color='darkred', fontweight='bold')

    # Total latency
    ax.text(5.5, 0.5, 'Total End-to-End Latency: ~480μs (0.48ms)',
            ha='center', va='center', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5, edgecolor='darkred', linewidth=2))

    plt.tight_layout()
    plt.savefig('results/figures/pipeline_diagram.png', bbox_inches='tight', dpi=300)
    print("[OK] Generated: pipeline_diagram.png")
    plt.close()


if __name__ == '__main__':
    print("Generating block diagrams for NM-RAG paper...")
    print()

    create_system_overview()
    create_nmpu_detail()
    create_pipeline_diagram()

    print()
    print("=" * 60)
    print("All diagrams generated successfully!")
    print("=" * 60)
    print()
    print("Files created in results/figures/:")
    print("  - system_overview.png    : High-level system architecture")
    print("  - nmpu_detail.png        : Detailed NMPU microarchitecture")
    print("  - pipeline_diagram.png   : Query processing pipeline")
    print()
    print("These diagrams are ready to include in your IEEE paper.")
