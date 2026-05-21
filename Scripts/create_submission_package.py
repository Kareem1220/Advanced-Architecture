"""
Create submission package for Overleaf
Packages all necessary files for IEEE paper compilation
"""

import os
import zipfile
from pathlib import Path

def create_submission_zip():
    """Create a ZIP file ready for Overleaf upload"""

    # Files to include
    files_to_include = [
        'NM_RAG_Paper.tex',
        # Original figures
        'results/figures/system_overview.png',
        'results/figures/nmpu_detail.png',
        'results/figures/pipeline_diagram.png',
        'results/figures/speedup_comparison.png',
        'results/figures/latency_vs_quality.png',
        'results/figures/latency_comparison.png',
        'results/figures/energy_comparison.png',
        'results/figures/recall_comparison.png',
        'results/figures/results_table.tex',
        # New figures from enhancement
        'results/figures/attention_pattern_visualization.png',
        'results/figures/rag_pipeline_comparison.png',
        'results/figures/cxl_hbm_architecture_comparison.png',
        'results/figures/memory_bandwidth_analysis.png',
        'results/figures/hardware_comparison_radar.png',
        'results/figures/quantization_tradeoff.png',
        'results/figures/scalability_projection.png',
    ]

    # Output ZIP file
    output_zip = 'NM_RAG_Overleaf_Submission.zip'

    print("=" * 60)
    print("Creating Overleaf Submission Package")
    print("=" * 60)
    print()

    # Create ZIP
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_include:
            if os.path.exists(file_path):
                # Preserve directory structure
                zipf.write(file_path, arcname=file_path)
                print(f"[OK] Added: {file_path}")
            else:
                print(f"[WARNING] Not found: {file_path}")

    print()
    print("=" * 60)
    print("Package created successfully!")
    print("=" * 60)
    print()
    print(f"Output file: {output_zip}")
    print(f"Size: {os.path.getsize(output_zip) / 1024:.1f} KB")
    print()
    print("Next steps:")
    print("1. Go to https://www.overleaf.com")
    print("2. Create new project -> Upload Project")
    print(f"3. Upload: {output_zip}")
    print("4. Wait for automatic compilation")
    print("5. Download PDF")
    print()
    print("=" * 60)

if __name__ == '__main__':
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    create_submission_zip()
