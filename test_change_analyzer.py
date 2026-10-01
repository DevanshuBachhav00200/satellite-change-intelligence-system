import os
import sys
import numpy as np
from PIL import Image

# Ensure analysis package can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.change_analyzer import analyze_change_mask, visualize_change_analysis


def test_analysis_module():
    print("==================================================")
    print("Testing Satellite Change Intelligence Analysis Module")
    print("==================================================")

    # 1. Select sample prediction mask from repository
    sample_mask_path = os.path.join(
        os.path.dirname(__file__),
        'samples_LEVIR',
        'predict_CD_ChangeFormerV6',
        'test_102_0512_0000.png'
    )

    print(f"Loading sample prediction mask from:\n  {sample_mask_path}")
    assert os.path.exists(sample_mask_path), f"Test image file not found at {sample_mask_path}"

    mask_img = Image.open(sample_mask_path)
    mask = np.array(mask_img)

    print(f"Mask loaded successfully. Shape: {mask.shape}, Dtype: {mask.dtype}, Min: {mask.min()}, Max: {mask.max()}")

    # 2. Run Change Analyzer
    grid_size = (4, 4)
    results = analyze_change_mask(mask, grid_size=grid_size)

    # 3. Assertions and Verifications
    print("\n--- Verifying Metrics ---")

    # Metric 1: Total changed pixel count
    total_changed = results['total_changed_pixels']
    print(f"1. Total Changed Pixels: {total_changed}")
    assert isinstance(total_changed, int) and total_changed >= 0

    # Metric 2: Total image pixel count
    total_pixels = results['total_image_pixels']
    print(f"2. Total Image Pixels: {total_pixels}")
    assert total_pixels == mask.shape[0] * mask.shape[1]

    # Metric 3: Change percentage
    change_pct = results['change_percentage']
    print(f"3. Change Percentage: {change_pct:.4f}%")
    assert 0.0 <= change_pct <= 100.0

    # Metric 4: Number of connected changed regions
    num_regions = results['num_connected_regions']
    print(f"4. Number of Connected Regions: {num_regions}")
    assert num_regions >= 0

    # Metric 5: Area of each connected region
    region_areas = results['region_areas']
    print(f"5. Connected Region Areas (first 5): {region_areas[:5]}")
    assert len(region_areas) == num_regions

    # Metric 6: Largest changed region
    largest_area = results['largest_region_area']
    print(f"6. Largest Region Area: {largest_area} pixels")
    if num_regions > 0:
        assert largest_area == max(region_areas)
    else:
        assert largest_area == 0

    # Metric 7: Bounding boxes
    bboxes = results['bounding_boxes']
    print(f"7. Bounding Boxes (first 5 x,y,w,h): {bboxes[:5]}")
    assert len(bboxes) == num_regions
    for x, y, w, h in bboxes:
        assert x >= 0 and y >= 0 and w > 0 and h > 0

    # Metric 8: Centroids
    centroids = results['centroids']
    print(f"8. Centroids (first 5 cx,cy): {[(round(cx, 1), round(cy, 1)) for cx, cy in centroids[:5]]}")
    assert len(centroids) == num_regions
    for cx, cy in centroids:
        assert 0 <= cx <= mask.shape[1] and 0 <= cy <= mask.shape[0]

    # Metric 9: Average changed-region area
    avg_area = results['avg_region_area']
    print(f"9. Average Region Area: {avg_area:.2f} pixels")
    if num_regions > 0:
        assert abs(avg_area - (sum(region_areas) / num_regions)) < 1e-4

    # Metric 10: Spatial density grid
    density_grid = results['spatial_density_grid']
    print(f"10. Spatial Density Grid ({grid_size[0]}x{grid_size[1]}):\n{np.round(density_grid, 2)}")
    assert density_grid.shape == grid_size
    assert np.all(density_grid >= 0.0) and np.all(density_grid <= 100.0)

    # 4. Visualization & Save Test
    output_vis_path = os.path.join(
        os.path.dirname(__file__),
        'samples_LEVIR',
        'predict_CD_ChangeFormerV6',
        'test_102_analysis_vis.png'
    )
    print(f"\nGenerating and saving visualization to:\n  {output_vis_path}")

    vis_img = visualize_change_analysis(
        mask=mask,
        analysis_results=results,
        save_path=output_vis_path,
        draw_centroids=True,
        draw_grid=True
    )

    assert os.path.exists(output_vis_path), f"Failed to save visualization at {output_vis_path}"
    print(f"Visualization saved successfully ({os.path.getsize(output_vis_path)} bytes).")

    print("\n==================================================")
    print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == '__main__':
    test_analysis_module()
