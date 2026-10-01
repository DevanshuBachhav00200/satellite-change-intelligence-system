import os
import sys
import csv
import json
import numpy as np
from PIL import Image
from typing import Dict, Any, List, Optional

# Ensure analysis package import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.change_analyzer import analyze_change_mask


class BatchChangeAnalyzer:
    """
    Batch post-processing change analysis system for ChangeFormer prediction masks.
    Processes all images listed in a dataset split index (e.g., LEVIR-CD256/list/test.txt)
    and extracts per-image metrics and aggregate summary statistics.
    """

    def __init__(
        self,
        list_file: str = "LEVIR-CD256/list/test.txt",
        mask_dir: str = "LEVIR-CD256/label",
        output_dir: str = "analysis/results"
    ):
        self.list_file = os.path.abspath(list_file)
        self.mask_dir = os.path.abspath(mask_dir)
        self.output_dir = os.path.abspath(output_dir)

    def load_test_image_list(self) -> List[str]:
        """
        Reads image list file and returns ordered list of image filenames.
        """
        if not os.path.exists(self.list_file):
            raise FileNotFoundError(f"List file not found at: {self.list_file}")

        with open(self.list_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        return lines

    def run_batch(self, grid_size: tuple = (4, 4)) -> Dict[str, Any]:
        """
        Runs change analyzer across all test split prediction masks.

        Returns:
            Dict[str, Any]: Combined results containing 'rows' list and 'summary' dictionary.
        """
        image_list = self.load_test_image_list()
        total_images = len(image_list)

        print(f"Starting batch change analysis for {total_images} images...")
        print(f"  List File: {self.list_file}")
        print(f"  Mask Directory: {self.mask_dir}")

        rows = []
        change_percentages = []
        connected_region_counts = []
        largest_region_areas = []

        for idx, img_name in enumerate(image_list):
            mask_path = os.path.join(self.mask_dir, img_name)

            if not os.path.exists(mask_path):
                raise FileNotFoundError(f"Missing prediction mask for entry '{img_name}' at path: {mask_path}")

            # Load mask image
            mask_img = Image.open(mask_path)
            mask_arr = np.array(mask_img)

            # Analyze mask using single-mask analyzer
            res = analyze_change_mask(mask_arr, grid_size=grid_size)

            change_pct = res['change_percentage']
            region_cnt = res['num_connected_regions']
            largest_area = res['largest_region_area']
            avg_area = res['avg_region_area']
            grid_density = res['spatial_density_grid']

            grid_mean = float(np.mean(grid_density))
            grid_max = float(np.max(grid_density))

            row = {
                'image_name': img_name,
                'changed_pixel_count': res['total_changed_pixels'],
                'total_pixel_count': res['total_image_pixels'],
                'change_percentage': round(change_pct, 6),
                'connected_region_count': region_cnt,
                'largest_region_area': largest_area,
                'average_region_area': round(avg_area, 4),
                'grid_density_mean': round(grid_mean, 6),
                'grid_density_max': round(grid_max, 6)
            }

            rows.append(row)
            change_percentages.append(change_pct)
            connected_region_counts.append(region_cnt)
            largest_region_areas.append(largest_area)

            if (idx + 1) % 500 == 0 or (idx + 1) == total_images:
                print(f"  Processed {idx + 1}/{total_images} masks...")

        # Calculate summary statistics across all images
        summary = {
            'total_images_processed': total_images,
            'mean_change_percentage': round(float(np.mean(change_percentages)), 6),
            'median_change_percentage': round(float(np.median(change_percentages)), 6),
            'min_change_percentage': round(float(np.min(change_percentages)), 6),
            'max_change_percentage': round(float(np.max(change_percentages)), 6),
            'mean_connected_region_count': round(float(np.mean(connected_region_counts)), 4),
            'median_connected_region_count': round(float(np.median(connected_region_counts)), 4),
            'mean_largest_region_area': round(float(np.mean(largest_region_areas)), 4)
        }

        # Save CSV and JSON outputs
        os.makedirs(self.output_dir, exist_ok=True)
        csv_path = os.path.join(self.output_dir, 'LEVIR_test_change_analysis.csv')
        json_path = os.path.join(self.output_dir, 'LEVIR_test_change_summary.json')

        self.save_csv(rows, csv_path)
        self.save_json(summary, json_path)

        print(f"\nBatch processing complete!")
        print(f"  CSV Saved:  {csv_path}")
        print(f"  JSON Saved: {json_path}")

        return {'rows': rows, 'summary': summary, 'csv_path': csv_path, 'json_path': json_path}

    def save_csv(self, rows: List[Dict[str, Any]], csv_path: str):
        """
        Saves structured rows list to CSV file.
        """
        if not rows:
            return

        headers = list(rows[0].keys())
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    def save_json(self, summary: Dict[str, Any], json_path: str):
        """
        Saves summary dictionary to JSON file.
        """
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4)


def run_levir_test_batch_analysis():
    """
    Main entry point for running LEVIR-CD test set batch analysis.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    list_file = os.path.join(base_dir, "LEVIR-CD256", "list", "test.txt")
    mask_dir = os.path.join(base_dir, "LEVIR-CD256", "label")
    output_dir = os.path.join(base_dir, "analysis", "results")

    analyzer = BatchChangeAnalyzer(
        list_file=list_file,
        mask_dir=mask_dir,
        output_dir=output_dir
    )
    return analyzer.run_batch()


if __name__ == '__main__':
    run_levir_test_batch_analysis()
