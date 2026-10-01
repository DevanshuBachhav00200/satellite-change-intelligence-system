import os
import sys
import csv
import json
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from typing import Dict, Any, List, Optional, Tuple

# Ensure analysis package import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.change_analyzer import analyze_change_mask


class ChangeImpactAssessor:
    """
    Explainable Change Impact Index (CII) Assessment Module.
    Calculates an image-based index S in [0, 100] based on detected change extent,
    spatial concentration, and structural scale from ChangeFormer prediction masks.
    """

    # Empirical design reference values from LEVIR-CD distribution
    C_REF: float = 25.0       # Reference change percentage (%)
    A_REF: float = 4096.0     # Reference largest region area (px, 64x64 footprint)
    SQRT_A_REF: float = 64.0  # sqrt(4096)

    # Weights for non-redundant feature dimensions
    W_EXTENT: float = 0.40
    W_CONCENTRATION: float = 0.35
    W_SCALE: float = 0.25

    # Data-driven category thresholds (derived from non-zero tertiles)
    THRESH_LOW_MODERATE: float = 30.0
    THRESH_MODERATE_HIGH: float = 55.0

    def __init__(self, min_region_area: int = 1):
        self.min_region_area = min_region_area

    def compute_cii_from_features(
        self,
        change_percentage: float,
        grid_density_max: float,
        largest_region_area: float,
        connected_region_count: int,
        average_region_area: float
    ) -> Dict[str, Any]:
        """
        Computes the Change Impact Index (CII), impact category, primary driver,
        and factor contributions from extracted features.
        """
        # 1. Feature Sub-scores
        f_extent = min(1.0, max(0.0, change_percentage / self.C_REF))
        f_conc = min(1.0, max(0.0, grid_density_max / 100.0))
        f_scale = min(1.0, max(0.0, np.sqrt(largest_region_area) / self.SQRT_A_REF))

        # 2. Weighted Composite Index (0 to 100)
        c_extent = self.W_EXTENT * f_extent
        c_conc = self.W_CONCENTRATION * f_conc
        c_scale = self.W_SCALE * f_scale

        cii_score = float(100.0 * (c_extent + c_conc + c_scale))

        # 3. Category Categorization
        if cii_score == 0.0:
            category = "Zero Impact"
        elif cii_score <= self.THRESH_LOW_MODERATE:
            category = "Low Impact"
        elif cii_score <= self.THRESH_MODERATE_HIGH:
            category = "Moderate Impact"
        else:
            category = "High Impact"

        # 4. Factor Contributions (%)
        total_c = c_extent + c_conc + c_scale
        if total_c > 0:
            pct_extent = (c_extent / total_c) * 100.0
            pct_conc = (c_conc / total_c) * 100.0
            pct_scale = (c_scale / total_c) * 100.0
        else:
            pct_extent, pct_conc, pct_scale = 0.0, 0.0, 0.0

        # 5. Primary Driver Identification
        if cii_score == 0.0:
            primary_driver = "None (No Change Detected)"
        else:
            drivers = [
                ('Extent (Coverage)', pct_extent),
                ('Concentration (Local Cluster)', pct_conc),
                ('Structural Scale (Object Footprint)', pct_scale)
            ]
            primary_driver = max(drivers, key=lambda x: x[1])[0]

        return {
            'cii_score': round(cii_score, 4),
            'impact_category': category,
            'primary_driver': primary_driver,
            'factor_contributions': {
                'extent_pct': round(pct_extent, 2),
                'concentration_pct': round(pct_conc, 2),
                'scale_pct': round(pct_scale, 2)
            },
            'sub_scores': {
                'f_extent': round(float(f_extent), 4),
                'f_concentration': round(float(f_conc), 4),
                'f_scale': round(float(f_scale), 4)
            },
            'raw_features': {
                'change_percentage': round(float(change_percentage), 4),
                'grid_density_max': round(float(grid_density_max), 4),
                'largest_region_area': round(float(largest_region_area), 2),
                'connected_region_count': int(connected_region_count),
                'average_region_area': round(float(average_region_area), 2)
            }
        }

    def assess_mask(self, mask: np.ndarray) -> Dict[str, Any]:
        """
        Extracts features from binary prediction mask and computes CII assessment.
        """
        analysis = analyze_change_mask(mask, grid_size=(4, 4), min_region_area=self.min_region_area)
        grid_max = float(np.max(analysis['spatial_density_grid']))

        return self.compute_cii_from_features(
            change_percentage=analysis['change_percentage'],
            grid_density_max=grid_max,
            largest_region_area=analysis['largest_region_area'],
            connected_region_count=analysis['num_connected_regions'],
            average_region_area=analysis['avg_region_area']
        )


class BatchImpactPipeline:
    """
    Batch processing pipeline for CII calculation across all test split images.
    """

    def __init__(
        self,
        analysis_csv_path: str = "analysis/results/LEVIR_test_change_analysis.csv",
        output_dir: str = "analysis/results"
    ):
        self.analysis_csv_path = os.path.abspath(analysis_csv_path)
        self.output_dir = os.path.abspath(output_dir)
        self.plots_dir = os.path.join(self.output_dir, "impact_analysis")

    def run_batch(self) -> Dict[str, Any]:
        """
        Runs batch CII assessment on CSV dataset.
        """
        if not os.path.exists(self.analysis_csv_path):
            raise FileNotFoundError(f"Missing analysis CSV: {self.analysis_csv_path}")

        assessor = ChangeImpactAssessor()
        rows = []

        with open(self.analysis_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                img_name = r['image_name']
                change_pct = float(r['change_percentage'])
                grid_max = float(r['grid_density_max'])
                largest_area = float(r['largest_region_area'])
                region_cnt = int(r['connected_region_count'])
                avg_area = float(r['average_region_area'])

                res = assessor.compute_cii_from_features(
                    change_percentage=change_pct,
                    grid_density_max=grid_max,
                    largest_region_area=largest_area,
                    connected_region_count=region_cnt,
                    average_region_area=avg_area
                )

                row = {
                    'image_name': img_name,
                    'cii_score': res['cii_score'],
                    'impact_category': res['impact_category'],
                    'primary_driver': res['primary_driver'],
                    'extent_contribution_pct': res['factor_contributions']['extent_pct'],
                    'concentration_contribution_pct': res['factor_contributions']['concentration_pct'],
                    'scale_contribution_pct': res['factor_contributions']['scale_pct'],
                    'change_percentage': change_pct,
                    'grid_density_max': grid_max,
                    'largest_region_area': largest_area,
                    'connected_region_count': region_cnt
                }
                rows.append(row)

        # Output CSV
        os.makedirs(self.output_dir, exist_ok=True)
        csv_path = os.path.join(self.output_dir, "LEVIR_test_impact_assessment.csv")
        headers = list(rows[0].keys())

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        # Summary Statistics
        scores = np.array([r['cii_score'] for r in rows])
        categories = [r['impact_category'] for r in rows]
        drivers = [r['primary_driver'] for r in rows]

        category_counts = {
            'Zero Impact': categories.count('Zero Impact'),
            'Low Impact': categories.count('Low Impact'),
            'Moderate Impact': categories.count('Moderate Impact'),
            'High Impact': categories.count('High Impact')
        }

        driver_counts = {d: drivers.count(d) for d in set(drivers)}

        summary = {
            'total_images': len(rows),
            'cii_statistics': {
                'mean': round(float(np.mean(scores)), 4),
                'median': round(float(np.median(scores)), 4),
                'std': round(float(np.std(scores)), 4),
                'min': round(float(np.min(scores)), 4),
                'max': round(float(np.max(scores)), 4),
                'p25': round(float(np.percentile(scores, 25)), 4),
                'p75': round(float(np.percentile(scores, 75)), 4),
                'p90': round(float(np.percentile(scores, 90)), 4),
                'p95': round(float(np.percentile(scores, 95)), 4)
            },
            'impact_category_counts': category_counts,
            'primary_driver_counts': driver_counts
        }

        json_path = os.path.join(self.output_dir, "LEVIR_impact_summary.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4)

        # Plots
        self.generate_plots(scores, category_counts, driver_counts, rows)

        return {
            'rows': rows,
            'summary': summary,
            'csv_path': csv_path,
            'json_path': json_path,
            'plots_dir': self.plots_dir
        }

    def generate_plots(self, scores: np.ndarray, category_counts: Dict[str, int], driver_counts: Dict[str, int], rows: List[Dict[str, Any]]):
        """
        Generates plots saved under analysis/results/impact_analysis/.
        """
        os.makedirs(self.plots_dir, exist_ok=True)
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

        # 1. Distribution of CII Score
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(scores, bins=50, color='#1f77b4', edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(scores), color='red', linestyle='--', linewidth=2, label=f"Mean CII: {np.mean(scores):.2f}")
        ax.set_title("Distribution of Change Impact Index (CII) across LEVIR-CD Test Set", fontsize=13, fontweight='bold')
        ax.set_xlabel("Change Impact Index (CII Score: 0 - 100)", fontsize=11)
        ax.set_ylabel("Number of Images", fontsize=11)
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "01_cii_distribution.png"), dpi=300)
        plt.close()

        # 2. Impact Categories Breakdown
        fig, ax = plt.subplots(figsize=(8, 5))
        cats = list(category_counts.keys())
        counts = list(category_counts.values())
        colors = ['#7f7f7f', '#2ca02c', '#ff7f0e', '#d62728']

        bars = ax.bar(cats, counts, color=colors, edgecolor='black', alpha=0.85)
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 15, f"{yval} ({yval/len(scores)*100:.1f}%)", ha='center', va='bottom', fontweight='bold')

        ax.set_title("Empirical Distribution of Change Impact Categories", fontsize=13, fontweight='bold')
        ax.set_ylabel("Number of Images", fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "02_impact_categories_distribution.png"), dpi=300)
        plt.close()

        # 3. Primary Drivers Breakdown
        fig, ax = plt.subplots(figsize=(8, 5))
        drivers = list(driver_counts.keys())
        d_counts = list(driver_counts.values())

        ax.pie(d_counts, labels=drivers, autopct='%1.1f%%', startangle=140, colors=['#8c564b', '#e377c2', '#17becf', '#7f7f7f'])
        ax.set_title("Primary Contributing Drivers of Change Impact", fontsize=13, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "03_primary_drivers_pie.png"), dpi=300)
        plt.close()

        # 4. Multi-panel Dashboard
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        axes[0, 0].hist(scores, bins=40, color='#1f77b4', edgecolor='black', alpha=0.7)
        axes[0, 0].set_title("CII Score Distribution")

        axes[0, 1].bar(cats, counts, color=colors, edgecolor='black', alpha=0.85)
        axes[0, 1].set_title("Impact Category Breakdown")

        change_pcts = [r['change_percentage'] for r in rows]
        axes[1, 0].scatter(change_pcts, scores, alpha=0.5, color='#9467bd', s=20)
        axes[1, 0].set_title("Change % vs. CII Score")
        axes[1, 0].set_xlabel("Change Percentage (%)")
        axes[1, 0].set_ylabel("CII Score")

        grid_maxs = [r['grid_density_max'] for r in rows]
        axes[1, 1].scatter(grid_maxs, scores, alpha=0.5, color='#8c564b', s=20)
        axes[1, 1].set_title("Max Grid Density % vs. CII Score")
        axes[1, 1].set_xlabel("Max Grid Density (%)")
        axes[1, 1].set_ylabel("CII Score")

        fig.suptitle("Satellite Change Intelligence - Change Impact Index (CII) Dashboard", fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "04_impact_dashboard.png"), dpi=300)
        plt.close()


def run_levir_test_impact_assessment():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "analysis", "results", "LEVIR_test_change_analysis.csv")
    output_dir = os.path.join(base_dir, "analysis", "results")

    pipeline = BatchImpactPipeline(analysis_csv_path=csv_path, output_dir=output_dir)
    return pipeline.run_batch()


if __name__ == '__main__':
    run_levir_test_impact_assessment()
