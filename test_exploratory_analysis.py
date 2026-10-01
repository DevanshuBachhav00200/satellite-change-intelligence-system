import os
import sys
import json

# Ensure analysis package import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.exploratory_analysis import run_exploratory_analysis


def test_exploratory_analysis():
    print("==================================================")
    print("Testing Exploratory Data Analysis & Visualization")
    print("==================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    stats_json_path = os.path.join(base_dir, 'analysis', 'results', 'LEVIR_analysis_statistics.json')
    plots_dir = os.path.join(base_dir, 'analysis', 'results', 'plots')

    # Execute EDA module
    stats = run_exploratory_analysis()

    # 1. Verify JSON file existence and contents
    print("\n--- Verifying Statistics JSON Artifact ---")
    assert os.path.exists(stats_json_path), f"Missing statistics file: {stats_json_path}"
    with open(stats_json_path, 'r', encoding='utf-8') as f:
        loaded_stats = json.load(f)

    assert loaded_stats['total_samples'] == 2048, f"Expected 2048 samples, got {loaded_stats['total_samples']}"

    required_vars = [
        'changed_pixel_count',
        'change_percentage',
        'connected_region_count',
        'largest_region_area',
        'average_region_area',
        'grid_density_mean',
        'grid_density_max'
    ]

    required_metric_keys = ['mean', 'median', 'std', 'min', 'max', 'p25', 'p75']

    for var in required_vars:
        assert var in loaded_stats, f"Missing variable in JSON statistics: '{var}'"
        for key in required_metric_keys:
            assert key in loaded_stats[var], f"Missing metric key '{key}' in variable '{var}'"

    print("Statistics JSON Contents (Change Percentage):")
    print(json.dumps(loaded_stats['change_percentage'], indent=2))

    # 2. Verify Plots Generation
    print("\n--- Verifying Generated Plots ---")
    expected_plots = [
        "01_change_percentage_distribution.png",
        "02_connected_regions_distribution.png",
        "03_largest_region_area_distribution.png",
        "04_scatter_change_pct_vs_regions.png",
        "05_scatter_change_pct_vs_largest_area.png",
        "06_grid_density_mean_distribution.png",
        "07_grid_density_max_distribution.png",
        "08_exploratory_dashboard.png"
    ]

    for plot_name in expected_plots:
        plot_path = os.path.join(plots_dir, plot_name)
        assert os.path.exists(plot_path), f"Missing expected plot file: {plot_name}"
        file_size = os.path.getsize(plot_path)
        assert file_size > 5000, f"Plot file {plot_name} is invalid or empty (size: {file_size} bytes)"
        print(f"  Verified {plot_name} ({file_size} bytes)")

    print("\n==================================================")
    print("ALL EXPLORATORY ANALYSIS CHECKS PASSED!")
    print("==================================================")


if __name__ == '__main__':
    test_exploratory_analysis()
