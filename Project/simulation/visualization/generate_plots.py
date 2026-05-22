"""
Visualization Generator
Creates plots and tables for the paper
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12


class PlotGenerator:
    """Generate all plots for the paper"""

    def __init__(self, results_dir='../results', output_dir='../results/figures'):
        self.results_dir = results_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Load results
        self.load_results()

    def load_results(self):
        """Load experiment results"""
        json_path = os.path.join(self.results_dir, 'detailed_results.json')

        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                self.results = json.load(f)
            print(f"Loaded results from {json_path}")
        else:
            print(f"Results file not found: {json_path}")
            print("Please run experiments first: python experiments/run_all_experiments.py")
            self.results = None

    def plot_latency_comparison(self):
        """Bar chart comparing latency across methods"""
        if not self.results:
            return

        perf = self.results['performance']

        methods = list(perf.keys())
        latencies = [perf[m]['latency_ms'] for m in methods]

        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
        bars = ax.bar(methods, latencies, color=colors[:len(methods)], alpha=0.8, edgecolor='black')

        ax.set_ylabel('Latency (ms)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Method', fontsize=14, fontweight='bold')
        ax.set_title('Retrieval Latency Comparison', fontsize=16, fontweight='bold')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax.set_ylim(0, max(latencies) * 1.15)
        plt.tight_layout()

        save_path = os.path.join(self.output_dir, 'latency_comparison.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()

    def plot_energy_comparison(self):
        """Bar chart comparing energy consumption"""
        if not self.results:
            return

        perf = self.results['performance']

        methods = list(perf.keys())
        energy = [perf[m]['energy_joules'] for m in methods]

        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
        bars = ax.bar(methods, energy, color=colors[:len(methods)], alpha=0.8, edgecolor='black')

        ax.set_ylabel('Energy (Joules/query)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Method', fontsize=14, fontweight='bold')
        ax.set_title('Energy Consumption Comparison', fontsize=16, fontweight='bold')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax.set_ylim(0, max(energy) * 1.15)
        plt.tight_layout()

        save_path = os.path.join(self.output_dir, 'energy_comparison.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()

    def plot_recall_comparison(self):
        """Bar chart comparing Recall@100"""
        if not self.results:
            return

        quality = self.results['quality']

        methods = list(quality.keys())
        recalls = [quality[m].get('Recall@100', 0) * 100 for m in methods]

        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
        bars = ax.bar(methods, recalls, color=colors[:len(methods)], alpha=0.8, edgecolor='black')

        ax.set_ylabel('Recall@100 (%)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Method', fontsize=14, fontweight='bold')
        ax.set_title('Retrieval Quality Comparison (Recall@100)', fontsize=16, fontweight='bold')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax.set_ylim(0, 105)
        ax.axhline(y=95, color='red', linestyle='--', alpha=0.5, label='95% threshold')
        ax.legend()

        plt.tight_layout()

        save_path = os.path.join(self.output_dir, 'recall_comparison.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()

    def plot_latency_vs_quality(self):
        """Scatter plot: Latency vs Quality trade-off"""
        if not self.results:
            return

        perf = self.results['performance']
        quality = self.results['quality']

        methods = list(perf.keys())
        latencies = [perf[m]['latency_ms'] for m in methods]
        recalls = [quality[m].get('Recall@100', 0) * 100 for m in methods]

        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71']

        for i, method in enumerate(methods):
            ax.scatter(latencies[i], recalls[i], s=300, color=colors[i],
                       alpha=0.7, edgecolors='black', linewidth=2, label=method)

            # Add method labels
            ax.annotate(method, (latencies[i], recalls[i]),
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=11, fontweight='bold')

        ax.set_xlabel('Latency (ms)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Recall@100 (%)', fontsize=14, fontweight='bold')
        ax.set_title('Latency vs Quality Trade-off', fontsize=16, fontweight='bold')

        ax.set_xscale('log')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='lower left')

        plt.tight_layout()

        save_path = os.path.join(self.output_dir, 'latency_vs_quality.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()

    def plot_speedup_chart(self):
        """Bar chart showing speedup over CPU baseline"""
        if not self.results:
            return

        perf = self.results['performance']

        methods = list(perf.keys())
        latencies = [perf[m]['latency_ms'] for m in methods]

        # Calculate speedup relative to CPU
        cpu_latency = latencies[0]  # Assuming first is CPU
        speedups = [cpu_latency / lat for lat in latencies]

        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
        bars = ax.bar(methods, speedups, color=colors[:len(methods)], alpha=0.8, edgecolor='black')

        ax.set_ylabel('Speedup vs CPU', fontsize=14, fontweight='bold')
        ax.set_xlabel('Method', fontsize=14, fontweight='bold')
        ax.set_title('Performance Speedup Relative to CPU Baseline', fontsize=16, fontweight='bold')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.1f}x',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax.axhline(y=1, color='red', linestyle='--', alpha=0.5, label='Baseline (1x)')
        ax.set_ylim(0, max(speedups) * 1.15)
        ax.legend()

        plt.tight_layout()

        save_path = os.path.join(self.output_dir, 'speedup_comparison.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()

    def generate_latex_table(self):
        """Generate LaTeX table for paper"""
        if not self.results:
            return

        perf = self.results['performance']
        quality = self.results['quality']

        latex = "\\begin{table}[H]\n"
        latex += "    \\centering\n"
        latex += "    \\caption{Performance Comparison of RAG Acceleration Methods}\n"
        latex += "    \\label{tab:results}\n"
        latex += "    \\begin{tabular}{|l|c|c|c|c|}\n"
        latex += "        \\hline\n"
        latex += "        \\textbf{Method} & \\textbf{Latency (ms)} & \\textbf{Energy (J)} & "
        latex += "\\textbf{Recall@100} & \\textbf{MRR} \\\\\n"
        latex += "        \\hline\n"

        for method in perf.keys():
            lat = perf[method]['latency_ms']
            energy = perf[method]['energy_joules']
            recall = quality[method].get('Recall@100', 0) * 100
            mrr = quality[method].get('MRR', 0)

            latex += f"        {method} & {lat:.2f} & {energy:.2f} & {recall:.1f}\\% & {mrr:.4f} \\\\\n"
            latex += "        \\hline\n"

        latex += "    \\end{tabular}\n"
        latex += "\\end{table}\n"

        # Save to file
        latex_path = os.path.join(self.output_dir, 'results_table.tex')
        with open(latex_path, 'w') as f:
            f.write(latex)

        print(f"Saved LaTeX table to: {latex_path}")
        print("\nLaTeX Table:")
        print(latex)

    def generate_all_plots(self):
        """Generate all plots and tables"""
        print("\n" + "=" * 60)
        print("GENERATING ALL VISUALIZATIONS")
        print("=" * 60 + "\n")

        self.plot_latency_comparison()
        self.plot_energy_comparison()
        self.plot_recall_comparison()
        self.plot_latency_vs_quality()
        self.plot_speedup_chart()
        self.generate_latex_table()

        print("\n" + "=" * 60)
        print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
        print(f"Output directory: {self.output_dir}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    generator = PlotGenerator()
    generator.generate_all_plots()
