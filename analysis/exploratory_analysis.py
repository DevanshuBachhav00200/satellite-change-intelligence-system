import os
import sys
import csv
import json
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List

# Ensure analysis package import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ExploratoryAnalyzer:
    """
    Exploratory Data Analysis (EDA) module for ChangeFormer LEVIR-CD test set analysis.
    Reads LEVIR_test_change_analysis.csv and produces statistical metrics and high-quality plots.
    """

    def __init__(
        self,
        csv_path: str = "analysis/results/LEVIR_test_change_analysis.csv",
        output_dir: str = "analysis/results"
    ):
        self.csv_path = os.path.abspath(csv_path)
        self.output_dir = os.path.abspath(output_dir)
        self.plots_dir = os.path.join(self.output_dir, "plots")

    def load_data(self) -> Dict[str, np.ndarray]:
        """
        Reads CSV file and returns numpy arrays for numerical columns.
        """
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Analysis CSV not found at: {self.csv_path}")

        rows = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)

        if not rows:
            raise ValueError(f"CSV file is empty: {self.csv_path}")

        data = {
            'changed_pixel_count': np.array([float(r['changed_pixel_count']) for r in rows]),
            'total_pixel_count': np.array([float(r['total_pixel_count']) for r in rows]),
            'change_percentage': np.array([float(r['change_percentage']) for r in rows]),
            'connected_region_count': np.array([float(r['connected_region_count']) for r in rows]),
            'largest_region_area': np.array([float(r['largest_region_area']) for r in rows]),
            'average_region_area': np.array([float(r['average_region_area']) for r in rows]),
            'grid_density_mean': np.array([float(r['grid_density_mean']) for r in rows]),
            'grid_density_max': np.array([float(r['grid_density_max']) for r in rows]),
        }

        return data

    def compute_statistics(self, data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Computes mean, median, std, min, max, 25th percentile, 75th percentile for all variables.
        """
        stats_dict = {
            'total_samples': len(data['change_percentage'])
        }

        variables = [
            'changed_pixel_count',
            'change_percentage',
            'connected_region_count',
            'largest_region_area',
            'average_region_area',
            'grid_density_mean',
            'grid_density_max'
        ]

        for var in variables:
            arr = data[var]
            stats_dict[var] = {
                'mean': round(float(np.mean(arr)), 6),
                'median': round(float(np.median(arr)), 6),
                'std': round(float(np.std(arr)), 6),
                'min': round(float(np.min(arr)), 6),
                'max': round(float(np.max(arr)), 6),
                'p25': round(float(np.percentile(arr, 25)), 6),
                'p75': round(float(np.percentile(arr, 75)), 6)
            }

        return stats_dict

    def generate_plots(self, data: Dict[str, np.ndarray]):
        """
        Generates publication-quality distribution and scatter plots.
        """
        os.makedirs(self.plots_dir, exist_ok=True)
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

        primary_color = '#1f77b4'
        accent_color = '#d62728'

        # 1. Change Percentage Distribution
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(data['change_percentage'], bins=50, color=primary_color, edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(data['change_percentage']), color=accent_color, linestyle='--', linewidth=2,
                   label=f"Mean: {np.mean(data['change_percentage']):.2f}%")
        ax.axvline(np.median(data['change_percentage']), color='green', linestyle='-', linewidth=2,
                   label=f"Median: {np.median(data['change_percentage']):.2f}%")
        ax.set_title("Distribution of Change Percentage Across Test Split", fontsize=13, fontweight='bold')
        ax.set_xlabel("Change Percentage (%)", fontsize=11)
        ax.set_ylabel("Number of Images", fontsize=11)
        ax.legend(fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "01_change_percentage_distribution.png"), dpi=300)
        plt.close()

        # 2. Connected Region Counts Distribution
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(data['connected_region_count'], bins=40, color='#2ca02c', edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(data['connected_region_count']), color=accent_color, linestyle='--', linewidth=2,
                   label=f"Mean: {np.mean(data['connected_region_count']):.2f}")
        ax.set_title("Distribution of Connected Change Region Counts", fontsize=13, fontweight='bold')
        ax.set_xlabel("Number of Connected Changed Regions", fontsize=11)
        ax.set_ylabel("Number of Images", fontsize=11)
        ax.legend(fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "02_connected_regions_distribution.png"), dpi=300)
        plt.close()

        # 3. Largest Region Area Distribution
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(data['largest_region_area'], bins=50, color='#ff7f0e', edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(data['largest_region_area']), color=accent_color, linestyle='--', linewidth=2,
                   label=f"Mean: {np.mean(data['largest_region_area']):.1f} px")
        ax.set_title("Distribution of Largest Changed-Region Area", fontsize=13, fontweight='bold')
        ax.set_xlabel("Largest Region Area (Pixels)", fontsize=11)
        ax.set_ylabel("Number of Images", fontsize=11)
        ax.legend(fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "03_largest_region_area_distribution.png"), dpi=300)
        plt.close()

        # 4. Scatter Plot: Change Percentage vs Connected Region Count
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(data['change_percentage'], data['connected_region_count'], alpha=0.5, color='#9467bd', edgecolors='none', s=25)
        ax.set_title("Change Percentage vs. Connected Region Count", fontsize=13, fontweight='bold')
        ax.set_xlabel("Change Percentage (%)", fontsize=11)
        ax.set_ylabel("Connected Changed Regions", fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "04_scatter_change_pct_vs_regions.png"), dpi=300)
        plt.close()

        # 5. Scatter Plot: Change Percentage vs Largest Region Area
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(data['change_percentage'], data['largest_region_area'], alpha=0.5, color='#8c564b', edgecolors='none', s=25)
        ax.set_title("Change Percentage vs. Largest Region Area", fontsize=13, fontweight='bold')
        ax.set_xlabel("Change Percentage (%)", fontsize=11)
        ax.set_ylabel("Largest Region Area (Pixels)", fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "05_scatter_change_pct_vs_largest_area.png"), dpi=300)
        plt.close()

        # 6. Grid Density Mean Distribution
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(data['grid_density_mean'], bins=50, color='#17becf', edgecolor='black', alpha=0.7)
        ax.set_title("Distribution of Grid Density Mean (%)", fontsize=13, fontweight='bold')
        ax.set_xlabel("Mean Grid Change Density (%)", fontsize=11)
        ax.set_ylabel("Number of Images", fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "06_grid_density_mean_distribution.png"), dpi=300)
        plt.close()

        # 7. Grid Density Max Distribution
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(data['grid_density_max'], bins=50, color='#bcbd22', edgecolor='black', alpha=0.7)
        ax.set_title("Distribution of Grid Density Max (%)", fontsize=13, fontweight='bold')
        ax.set_xlabel("Max Grid Change Density (%)", fontsize=11)
        ax.set_ylabel("Number of Images", fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "07_grid_density_max_distribution.png"), dpi=300)
        plt.close()

        # 8. Combined Exploratory Dashboard
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))

        axes[0, 0].hist(data['change_percentage'], bins=40, color=primary_color, edgecolor='black', alpha=0.7)
        axes[0, 0].set_title("Change Percentage (%)")

        axes[0, 1].hist(data['connected_region_count'], bins=30, color='#2ca02c', edgecolor='black', alpha=0.7)
        axes[0, 1].set_title("Connected Region Count")

        axes[0, 2].hist(data['largest_region_area'], bins=40, color='#ff7f0e', edgecolor='black', alpha=0.7)
        axes[0, 2].set_title("Largest Region Area (px)")

        axes[1, 0].scatter(data['change_percentage'], data['connected_region_count'], alpha=0.4, color='#9467bd', s=15)
        axes[1, 0].set_title("Change % vs Regions")

        axes[1, 1].scatter(data['change_percentage'], data['largest_region_area'], alpha=0.4, color='#8c564b', s=15)
        axes[1, 1].set_title("Change % vs Largest Area")

        axes[1, 2].hist(data['grid_density_max'], bins=40, color='#bcbd22', edgecolor='black', alpha=0.7)
        axes[1, 2].set_title("Max Grid Density (%)")

        fig.suptitle("Satellite Change Intelligence - LEVIR-CD Exploratory Dashboard", fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "08_exploratory_dashboard.png"), dpi=300)
        plt.close()

        print(f"Generated 8 plots in: {self.plots_dir}")

    def run(self):
        """
        Executes full EDA pipeline.
        """
        print(f"Reading CSV data from: {self.csv_path}")
        data = self.load_data()

        print("Computing statistical metrics...")
        stats_dict = self.compute_statistics(data)

        json_path = os.path.join(self.output_dir, "LEVIR_analysis_statistics.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(stats_dict, f, indent=4)
        print(f"Saved statistics summary to: {json_path}")

        print("Generating plots...")
        self.generate_plots(data)

        print("\nExploratory Data Analysis Complete!")
        return stats_dict


def run_exploratory_analysis():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "analysis", "results", "LEVIR_test_change_analysis.csv")
    output_dir = os.path.join(base_dir, "analysis", "results")

    analyzer = ExploratoryAnalyzer(csv_path=csv_path, output_dir=output_dir)
    return analyzer.run()


if __name__ == '__main__':
    run_exploratory_analysis()
