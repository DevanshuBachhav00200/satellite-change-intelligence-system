import os
import sys
import csv
import json
import numpy as np

# Ensure analysis package import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.change_impact_assessor import ChangeImpactAssessor, run_levir_test_impact_assessment


def test_change_impact_assessor():
    print("==================================================")
    print("Testing Change Impact Index (CII) Assessment Suite")
    print("==================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'analysis', 'results', 'LEVIR_test_impact_assessment.csv')
    json_path = os.path.join(base_dir, 'analysis', 'results', 'LEVIR_impact_summary.json')
    plots_dir = os.path.join(base_dir, 'analysis', 'results', 'impact_analysis')

    # 1. Test single-mask assessment unit function
    print("\n--- 1. Testing Single-Mask Assessor Unit Function ---")
    assessor = ChangeImpactAssessor()

    # Synthetic mask test
    synth_mask = np.zeros((256, 256), dtype=np.uint8)
    synth_mask[50:150, 50:150] = 255  # 100x100 square change (10,000 px)

    res = assessor.assess_mask(synth_mask)
    print("Single Mask Assessment Output:")
    print(json.dumps(res, indent=2))

    required_keys = ['cii_score', 'impact_category', 'primary_driver', 'factor_contributions', 'sub_scores', 'raw_features']
    for key in required_keys:
        assert key in res, f"Missing key in assessor output: '{key}'"

    assert 0.0 <= res['cii_score'] <= 100.0, f"Invalid CII score: {res['cii_score']}"
    assert res['impact_category'] in ['Zero Impact', 'Low Impact', 'Moderate Impact', 'High Impact']

    # 2. Run Batch Assessment
    print("\n--- 2. Executing Batch CII Assessment ---")
    batch_res = run_levir_test_impact_assessment()

    summary = batch_res['summary']
    print("\n--- 3. Verifying Summary Statistics ---")
    print("CII Statistics:")
    for k, v in summary['cii_statistics'].items():
        print(f"  {k:8s}: {v}")

    print("\nCategory Counts:")
    for cat, count in summary['impact_category_counts'].items():
        pct = (count / summary['total_images']) * 100.0
        print(f"  {cat:15s}: {count:4d} ({pct:.2f}%)")

    assert summary['total_images'] == 2048, f"Expected 2048 images, got {summary['total_images']}"
    assert summary['impact_category_counts']['Zero Impact'] == 1113, f"Expected 1113 Zero Impact images"

    # 4. Verify CSV Output
    print("\n--- 4. Verifying Output CSV ---")
    assert os.path.exists(csv_path), f"Missing CSV: {csv_path}"

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames

    assert len(rows) == 2048, f"Expected 2048 rows in CSV, found {len(rows)}"
    required_headers = [
        'image_name', 'cii_score', 'impact_category', 'primary_driver',
        'extent_contribution_pct', 'concentration_contribution_pct', 'scale_contribution_pct',
        'change_percentage', 'grid_density_max', 'largest_region_area', 'connected_region_count'
    ]
    for h in required_headers:
        assert h in headers, f"Missing header column: '{h}'"

    # 5. Verify Plot Artifacts
    print("\n--- 5. Verifying Plot Artifacts ---")
    expected_plots = [
        "01_cii_distribution.png",
        "02_impact_categories_distribution.png",
        "03_primary_drivers_pie.png",
        "04_impact_dashboard.png"
    ]

    for plot_file in expected_plots:
        plot_p = os.path.join(plots_dir, plot_file)
        assert os.path.exists(plot_p), f"Missing plot artifact: {plot_file}"
        size = os.path.getsize(plot_p)
        assert size > 5000, f"Plot file invalid or empty: {plot_file} ({size} bytes)"
        print(f"  Verified {plot_file} ({size} bytes)")

    print("\n==================================================")
    print("ALL CHANGE IMPACT INDEX (CII) SUITE CHECKS PASSED!")
    print("==================================================")


if __name__ == '__main__':
    test_change_impact_assessor()
