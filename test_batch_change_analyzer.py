import os
import sys
import csv
import json

# Ensure analysis package path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.batch_change_analyzer import run_levir_test_batch_analysis


def test_batch_change_analyzer():
    print("==================================================")
    print("Testing LEVIR-CD Batch Change Analysis System")
    print("==================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    list_path = os.path.join(base_dir, 'LEVIR-CD256', 'list', 'test.txt')
    mask_dir = os.path.join(base_dir, 'LEVIR-CD256', 'label')
    csv_path = os.path.join(base_dir, 'analysis', 'results', 'LEVIR_test_change_analysis.csv')
    json_path = os.path.join(base_dir, 'analysis', 'results', 'LEVIR_test_change_summary.json')

    # 1. Verify input list file
    assert os.path.exists(list_path), f"List file missing: {list_path}"
    with open(list_path, 'r', encoding='utf-8') as f:
        test_images = [line.strip() for line in f if line.strip()]

    print(f"1. Verified list file. Total test images listed: {len(test_images)}")
    assert len(test_images) == 2048, f"Expected exactly 2048 test images, got {len(test_images)}"

    # 2. Verify all masks exist before batch run
    missing_masks = [img for img in test_images if not os.path.exists(os.path.join(mask_dir, img))]
    print(f"2. Verified mask existence. Missing masks count: {len(missing_masks)}")
    assert len(missing_masks) == 0, f"Found {len(missing_masks)} missing masks: {missing_masks[:5]}"

    # 3. Execute batch analysis
    print("\nExecuting batch change analysis...")
    run_results = run_levir_test_batch_analysis()

    # 4. Verify CSV Output File
    print("\n--- Verifying CSV Artifact ---")
    assert os.path.exists(csv_path), f"CSV output missing: {csv_path}"

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames

    print(f"4.1 CSV Row Count: {len(rows)}")
    assert len(rows) == 2048, f"CSV must contain exactly 2048 rows, found {len(rows)}"

    print(f"4.2 CSV Headers: {headers}")
    required_columns = [
        'image_name',
        'changed_pixel_count',
        'total_pixel_count',
        'change_percentage',
        'connected_region_count',
        'largest_region_area',
        'average_region_area',
        'grid_density_mean',
        'grid_density_max'
    ]
    for col in required_columns:
        assert col in headers, f"Missing required CSV header column: '{col}'"

    # 5. Verify image uniqueness and order matching
    csv_image_names = [r['image_name'] for r in rows]
    print(f"5.1 Checking uniqueness of image names...")
    assert len(set(csv_image_names)) == 2048, "Duplicate image names detected in CSV output!"

    print(f"5.2 Checking exact alignment with test.txt...")
    assert csv_image_names == test_images, "CSV rows do not preserve exact order of LEVIR-CD256/list/test.txt!"

    # 6. Verify metric bounds
    print(f"6. Checking value ranges for change percentage...")
    for idx, row in enumerate(rows):
        pct = float(row['change_percentage'])
        assert 0.0 <= pct <= 100.0, f"Invalid change percentage {pct} at row {idx} ({row['image_name']})"
        changed = int(row['changed_pixel_count'])
        total = int(row['total_pixel_count'])
        assert 0 <= changed <= total, f"Invalid pixel count {changed}/{total} at row {idx}"

    # 7. Verify JSON Summary File
    print("\n--- Verifying JSON Summary Artifact ---")
    assert os.path.exists(json_path), f"JSON summary file missing: {json_path}"

    with open(json_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    print("JSON Summary Contents:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    required_json_keys = [
        'total_images_processed',
        'mean_change_percentage',
        'median_change_percentage',
        'min_change_percentage',
        'max_change_percentage',
        'mean_connected_region_count',
        'median_connected_region_count',
        'mean_largest_region_area'
    ]
    for key in required_json_keys:
        assert key in summary, f"Missing required summary key: '{key}'"

    assert summary['total_images_processed'] == 2048
    assert 0.0 <= summary['min_change_percentage'] <= summary['max_change_percentage'] <= 100.0

    print("\n==================================================")
    print("ALL BATCH ANALYSIS VERIFICATION CHECKS PASSED!")
    print("==================================================")


if __name__ == '__main__':
    test_batch_change_analyzer()
