import os
import sys
import cv2
import numpy as np

# Ensure analysis package import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.change_intelligence_pipeline import run_change_intelligence_pipeline


def test_satellite_change_intelligence_pipeline():
    print("==================================================")
    print("Testing Integrated Satellite Change Intelligence Pipeline")
    print("==================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_a_path = os.path.join(base_dir, "LEVIR-CD256", "A", "test_100_10.png")
    img_b_path = os.path.join(base_dir, "LEVIR-CD256", "B", "test_100_10.png")
    batch_pred_path = os.path.join(base_dir, "LEVIR-CD256", "predict_ChangeFormer", "test_100_10.png")

    out_dir = os.path.join(base_dir, "LEVIR-CD256", "predict_ChangeFormer_pipeline_test")
    save_mask_path = os.path.join(out_dir, "test_100_10_mask.png")
    save_vis_path = os.path.join(out_dir, "test_100_10_vis.png")

    assert os.path.exists(img_a_path), f"Missing Image A: {img_a_path}"
    assert os.path.exists(img_b_path), f"Missing Image B: {img_b_path}"

    print(f"Running pipeline on test pair:")
    print(f"  Image A: {img_a_path}")
    print(f"  Image B: {img_b_path}")

    # 1. Run Pipeline
    result = run_change_intelligence_pipeline(
        img_a=img_a_path,
        img_b=img_b_path,
        save_mask_path=save_mask_path,
        save_vis_path=save_vis_path
    )

    print("\n--- Pipeline Execution Output ---")
    required_fields = [
        'prediction_mask',
        'changed_pixel_count',
        'total_pixel_count',
        'change_percentage',
        'connected_region_count',
        'largest_region_area',
        'average_region_area',
        'grid_density_statistics',
        'cii_score',
        'impact_category',
        'primary_driver',
        'factor_contributions'
    ]

    for field in required_fields:
        assert field in result, f"Missing required output field: '{field}'"

    print(f"1. Changed Pixel Count:      {result['changed_pixel_count']}")
    print(f"2. Total Pixel Count:        {result['total_pixel_count']}")
    print(f"3. Change Percentage:        {result['change_percentage']:.4f}%")
    print(f"4. Connected Region Count:   {result['connected_region_count']}")
    print(f"5. Largest Region Area:      {result['largest_region_area']} px")
    print(f"6. Average Region Area:      {result['average_region_area']:.2f} px")
    print(f"7. Grid Density Max:         {result['grid_density_statistics']['max']:.2f}%")
    print(f"8. Change Impact Index (CII): {result['cii_score']:.4f}")
    print(f"9. Impact Category:          {result['impact_category']}")
    print(f"10. Primary Driver:          {result['primary_driver']}")
    print(f"11. Factor Contributions:    {result['factor_contributions']}")

    # 2. Verify CII Bounds
    print("\n--- Verifying Field Assertions ---")
    assert 0.0 <= result['cii_score'] <= 100.0, f"Invalid CII score: {result['cii_score']}"
    assert result['impact_category'] in ['Zero Impact', 'Low Impact', 'Moderate Impact', 'High Impact']

    # 3. Verify Prediction Mask Properties
    pred_mask = result['prediction_mask']
    print(f"12. Prediction Mask Shape:  {pred_mask.shape}")
    print(f"    Unique Pixel Values:   {np.unique(pred_mask)}")

    assert pred_mask.shape == (256, 256), f"Expected shape (256, 256), got {pred_mask.shape}"
    unique_vals = list(np.unique(pred_mask))
    for val in unique_vals:
        assert val in [0, 255], f"Unexpected pixel value in mask: {val}"

    # 4. Verify Saved Artifacts
    print("\n--- Verifying Saved Artifacts ---")
    assert os.path.exists(save_mask_path), f"Saved mask missing: {save_mask_path}"
    assert os.path.exists(save_vis_path), f"Saved vis missing: {save_vis_path}"
    print(f"  Mask Saved Successfully: {save_mask_path} ({os.path.getsize(save_mask_path)} bytes)")
    print(f"  Vis Saved Successfully:  {save_vis_path} ({os.path.getsize(save_vis_path)} bytes)")

    # 5. Consistency Comparison against Batch Prediction
    print("\n--- Comparing Standalone Prediction with Batch Prediction ---")
    if os.path.exists(batch_pred_path):
        batch_mask = cv2.imread(batch_pred_path, cv2.IMREAD_GRAYSCALE)
        is_identical = np.array_equal(pred_mask, batch_mask)
        diff_pixels = int(np.sum(pred_mask != batch_mask))
        print(f"  Batch Prediction Mask Path: {batch_pred_path}")
        print(f"  Are Standalone and Batch Predictions Identical? {is_identical} (Differences: {diff_pixels} pixels)")
        assert is_identical, f"Standalone prediction differs from batch prediction by {diff_pixels} pixels!"
    else:
        print("  Batch prediction path not found; skipping comparison.")

    print("\n==================================================")
    print("ALL CHANGE INTELLIGENCE PIPELINE CHECKS PASSED!")
    print("==================================================")


if __name__ == '__main__':
    test_satellite_change_intelligence_pipeline()
