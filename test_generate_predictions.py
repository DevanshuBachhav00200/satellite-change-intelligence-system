import os
import cv2
import numpy as np


def test_prediction_generation():
    print("==================================================")
    print("Verifying Generated ChangeFormer Prediction Masks")
    print("==================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    list_path = os.path.join(base_dir, 'LEVIR-CD256', 'list', 'test.txt')
    pred_dir = os.path.join(base_dir, 'LEVIR-CD256', 'predict_ChangeFormer')

    assert os.path.exists(list_path), f"Missing list file: {list_path}"
    with open(list_path, 'r', encoding='utf-8') as f:
        expected_images = [line.strip() for line in f if line.strip()]

    print(f"1. Total images in test.txt: {len(expected_images)}")
    assert len(expected_images) == 2048

    assert os.path.exists(pred_dir), f"Missing prediction directory: {pred_dir}"
    generated_files = [f for f in os.listdir(pred_dir) if f.endswith('.png')]

    print(f"2. Total PNG files in predict_ChangeFormer: {len(generated_files)}")
    assert len(generated_files) == 2048, f"Expected 2048 PNGs, found {len(generated_files)}"

    # Check for missing or unexpected files
    missing_files = [f for f in expected_images if f not in generated_files]
    unexpected_files = [f for f in generated_files if f not in expected_images]

    print(f"3. Missing files count: {len(missing_files)}")
    print(f"4. Unexpected files count: {len(unexpected_files)}")
    assert len(missing_files) == 0, f"Missing files: {missing_files[:5]}"
    assert len(unexpected_files) == 0, f"Unexpected files: {unexpected_files[:5]}"

    # Verify sample mask properties
    sample_file = os.path.join(pred_dir, expected_images[0])
    img = cv2.imread(sample_file, cv2.IMREAD_GRAYSCALE)

    print(f"5. Sample mask filename: {expected_images[0]}")
    print(f"   Shape: {img.shape}")
    print(f"   Unique pixel values: {np.unique(img)}")

    assert img.shape == (256, 256), f"Expected shape (256, 256), got {img.shape}"

    unique_vals = list(np.unique(img))
    for val in unique_vals:
        assert val in [0, 255], f"Unexpected pixel value {val} in prediction mask!"

    print("\n==================================================")
    print("ALL PREDICTION VERIFICATION CHECKS PASSED!")
    print("==================================================")


if __name__ == '__main__':
    test_prediction_generation()
