import os
import sys
import numpy as np
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.change_intelligence_pipeline import run_change_intelligence_pipeline


def test_app_dashboard_backend():
    print("==================================================")
    print("Testing Streamlit App Dashboard Backend Execution")
    print("==================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_a_path = os.path.join(base_dir, "LEVIR-CD256", "A", "test_100_10.png")
    img_b_path = os.path.join(base_dir, "LEVIR-CD256", "B", "test_100_10.png")

    assert os.path.exists(img_a_path), f"Missing Image A: {img_a_path}"
    assert os.path.exists(img_b_path), f"Missing Image B: {img_b_path}"

    print(f"Running pipeline with test pair:\n  Image A: {img_a_path}\n  Image B: {img_b_path}")

    res = run_change_intelligence_pipeline(img_a_path, img_b_path)

    print("\n--- Output Verification ---")
    print(f"1. Change Percentage:        {res['change_percentage']:.4f}%")
    print(f"2. Change Impact Index (CII): {res['cii_score']:.4f}")
    print(f"3. Impact Category:          {res['impact_category']}")
    print(f"4. Changed Pixel Count:      {res['changed_pixel_count']}")

    # Expected values verification from requirement #19
    assert abs(res['change_percentage'] - 2.9495) < 0.05, f"Expected ~2.9495%, got {res['change_percentage']}"
    assert abs(res['cii_score'] - 29.8791) < 0.1, f"Expected ~29.8791, got {res['cii_score']}"
    assert res['impact_category'] == 'Low Impact', f"Expected Low Impact, got {res['impact_category']}"
    assert res['changed_pixel_count'] == 1933, f"Expected 1933 changed pixels, got {res['changed_pixel_count']}"

    print("\n==================================================")
    print("ALL APP DASHBOARD BACKEND CHECKS PASSED!")
    print("==================================================")


if __name__ == '__main__':
    test_app_dashboard_backend()
