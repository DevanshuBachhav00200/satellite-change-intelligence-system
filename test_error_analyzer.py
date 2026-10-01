import os
import sys
import csv
import json

# Ensure analysis package import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.error_analyzer import run_levir_test_error_analysis


def test_error_analyzer():
    print("==================================================")
    print("Testing LEVIR-CD Independent Error Analysis Suite")
    print("==================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'analysis', 'results', 'LEVIR_test_error_analysis.csv')
    json_path = os.path.join(base_dir, 'analysis', 'results', 'LEVIR_error_analysis_summary.json')
    plots_dir = os.path.join(base_dir, 'analysis', 'results', 'error_analysis')

    # Execute Error Analysis Suite
    results = run_levir_test_error_analysis()

    # 1. Verify Image Counts
    print("\n--- Verifying Image Counts ---")
    summary = results['summary']
    processed = summary['total_images_processed']
    missing_gt = summary['missing_gt_masks']
    missing_pred = summary['missing_pred_masks']

    print(f"Processed Images: {processed}")
    print(f"Missing GT Masks:   {missing_gt}")
    print(f"Missing Pred Masks: {missing_pred}")

    assert processed == 2048, f"Expected 2048 images, got {processed}"
    assert missing_gt == 0, f"Found {missing_gt} missing GT masks"
    assert missing_pred == 0, f"Found {missing_pred} missing Pred masks"

    # 2. Verify CSV Output
    print("\n--- Verifying Error Analysis CSV Artifact ---")
    assert os.path.exists(csv_path), f"CSV missing: {csv_path}"

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames

    assert len(rows) == 2048, f"Expected 2048 rows in CSV, found {len(rows)}"

    required_headers = [
        'image_name', 'tp', 'tn', 'fp', 'fn',
        'accuracy', 'precision', 'recall', 'f1',
        'iou', 'fpr', 'fnr', 'gt_change_pct', 'pred_change_pct'
    ]
    for header in required_headers:
        assert header in headers, f"Missing header in CSV: '{header}'"

    # Check value bounds
    for r in rows:
        acc = float(r['accuracy'])
        prec = float(r['precision'])
        rec = float(r['recall'])
        f1 = float(r['f1'])
        iou = float(r['iou'])
        assert 0.0 <= acc <= 1.0, f"Invalid accuracy {acc}"
        assert 0.0 <= prec <= 1.0, f"Invalid precision {prec}"
        assert 0.0 <= rec <= 1.0, f"Invalid recall {rec}"
        assert 0.0 <= f1 <= 1.0, f"Invalid F1 {f1}"
        assert 0.0 <= iou <= 1.0, f"Invalid IoU {iou}"

    # 3. Verify JSON Summary Artifact
    print("\n--- Verifying JSON Summary Artifact ---")
    assert os.path.exists(json_path), f"JSON summary missing: {json_path}"

    with open(json_path, 'r', encoding='utf-8') as f:
        loaded_summary = json.load(f)

    assert 'overall_metrics' in loaded_summary
    assert 'top_fp_rate_images' in loaded_summary
    assert 'top_fn_rate_images' in loaded_summary
    assert 'lowest_iou_images' in loaded_summary

    print("Overall Performance Metrics:")
    for metric_name, vals in loaded_summary['overall_metrics'].items():
        print(f"  {metric_name.upper():10s}: Mean={vals['mean']:.4f}, Median={vals['median']:.4f}, Std={vals['std']:.4f}")

    print("\nTop Error Cases (Sample):")
    print(f"  Lowest IoU Sample: {loaded_summary['lowest_iou_images'][0]}")
    print(f"  Top FP Rate Sample: {loaded_summary['top_fp_rate_images'][0]}")
    print(f"  Top FN Rate Sample: {loaded_summary['top_fn_rate_images'][0]}")

    # 4. Verify Generated Error Plots
    print("\n--- Verifying Error Analysis Plots ---")
    expected_plots = [
        "01_change_iou_distribution.png",
        "02_false_positive_rate_distribution.png",
        "03_false_negative_rate_distribution.png",
        "04_gt_change_pct_vs_iou.png",
        "05_gt_change_pct_vs_f1.png",
        "06_top_error_cases_visualization.png"
    ]

    for plot_file in expected_plots:
        plot_path = os.path.join(plots_dir, plot_file)
        assert os.path.exists(plot_path), f"Missing plot: {plot_file}"
        size = os.path.getsize(plot_path)
        assert size > 5000, f"Plot file empty or invalid: {plot_file} ({size} bytes)"
        print(f"  Verified {plot_file} ({size} bytes)")

    print("\n==================================================")
    print("ALL ERROR ANALYSIS VERIFICATION CHECKS PASSED!")
    print("==================================================")


if __name__ == '__main__':
    test_error_analyzer()
