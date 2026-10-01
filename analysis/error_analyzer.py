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


class ErrorAnalyzer:
    """
    Independent Error Analysis Module for ChangeFormer Binary Change Detection.
    Calculates pixel-level confusion matrices, error rates, and classification metrics
    for all images in a dataset split.
    """

    def __init__(
        self,
        list_file: str = "LEVIR-CD256/list/test.txt",
        gt_dir: str = "LEVIR-CD256/label",
        pred_dir: str = "LEVIR-CD256/predict_ChangeFormer",
        img_a_dir: str = "LEVIR-CD256/A",
        img_b_dir: str = "LEVIR-CD256/B",
        output_dir: str = "analysis/results"
    ):
        self.list_file = os.path.abspath(list_file)
        self.gt_dir = os.path.abspath(gt_dir)
        self.pred_dir = os.path.abspath(pred_dir)
        self.img_a_dir = os.path.abspath(img_a_dir)
        self.img_b_dir = os.path.abspath(img_b_dir)
        self.output_dir = os.path.abspath(output_dir)
        self.plots_dir = os.path.join(self.output_dir, "error_analysis")

    def load_test_image_list(self) -> List[str]:
        """
        Loads the list of test image names.
        """
        if not os.path.exists(self.list_file):
            raise FileNotFoundError(f"List file not found: {self.list_file}")

        with open(self.list_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        return lines

    def compute_image_error_metrics(
        self,
        gt_mask: np.ndarray,
        pred_mask: np.ndarray
    ) -> Dict[str, float]:
        """
        Normalizes GT and Prediction masks to binary {0, 1} and computes confusion matrix & metrics.
        """
        # 1. Normalization to binary uint8 {0, 1}
        if gt_mask.ndim > 2:
            gt_mask = gt_mask[:, :, 0]
        if pred_mask.ndim > 2:
            pred_mask = pred_mask[:, :, 0]

        gt_bin = (gt_mask > 0).astype(np.uint8)
        pred_bin = (pred_mask > 0).astype(np.uint8)

        total_pixels = float(gt_bin.size)

        # 2. Confusion matrix pixel counts
        tp = float(np.sum((pred_bin == 1) & (gt_bin == 1)))
        tn = float(np.sum((pred_bin == 0) & (gt_bin == 0)))
        fp = float(np.sum((pred_bin == 1) & (gt_bin == 0)))
        fn = float(np.sum((pred_bin == 0) & (gt_bin == 1)))

        # 3. Derived classification metrics
        accuracy = (tp + tn) / total_pixels if total_pixels > 0 else 1.0

        # Precision: TP / (TP + FP)
        if (tp + fp) > 0:
            precision = tp / (tp + fp)
        else:
            precision = 1.0 if (tp + fn) == 0 else 0.0

        # Recall: TP / (TP + FN)
        if (tp + fn) > 0:
            recall = tp / (tp + fn)
        else:
            recall = 1.0 if (tp + fp) == 0 else 0.0

        # F1 Score
        if (precision + recall) > 0:
            f1 = (2.0 * precision * recall) / (precision + recall)
        else:
            f1 = 1.0 if (tp + fp + fn) == 0 else 0.0

        # Change IoU: TP / (TP + FP + FN)
        union = tp + fp + fn
        if union > 0:
            iou = tp / union
        else:
            iou = 1.0  # Perfect match when both GT and Pred have 0 change pixels

        # False Positive Rate: FP / (FP + TN)
        negatives = fp + tn
        fpr = (fp / negatives) if negatives > 0 else 0.0

        # False Negative Rate: FN / (TP + FN)
        positives = tp + fn
        fnr = (fn / positives) if positives > 0 else 0.0

        gt_change_pct = (positives / total_pixels) * 100.0 if total_pixels > 0 else 0.0
        pred_change_pct = ((tp + fp) / total_pixels) * 100.0 if total_pixels > 0 else 0.0

        return {
            'tp': int(tp),
            'tn': int(tn),
            'fp': int(fp),
            'fn': int(fn),
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            'iou': float(iou),
            'fpr': float(fpr),
            'fnr': float(fnr),
            'gt_change_pct': float(gt_change_pct),
            'pred_change_pct': float(pred_change_pct)
        }

    def run_analysis(self) -> Dict[str, Any]:
        """
        Executes error analysis across all images in the list file.
        """
        pass


class ErrorAnalysisPipeline(ErrorAnalyzer):

    def run_analysis(self) -> Dict[str, Any]:
        """
        Executes error analysis across all images.
        """
        image_list = self.load_test_image_list()
        total_images = len(image_list)

        print(f"Executing Error Analysis across {total_images} images...")
        print(f"  GT Dir:   {self.gt_dir}")
        print(f"  Pred Dir: {self.pred_dir}")

        missing_gt = 0
        missing_pred = 0
        rows = []

        for idx, img_name in enumerate(image_list):
            gt_path = os.path.join(self.gt_dir, img_name)
            pred_path = os.path.join(self.pred_dir, img_name)

            if not os.path.exists(gt_path):
                missing_gt += 1
                raise FileNotFoundError(f"Missing Ground Truth mask: {gt_path}")
            if not os.path.exists(pred_path):
                missing_pred += 1
                raise FileNotFoundError(f"Missing Prediction mask: {pred_path}")

            gt_arr = np.array(Image.open(gt_path))
            pred_arr = np.array(Image.open(pred_path))

            metrics = self.compute_image_error_metrics(gt_arr, pred_arr)

            row = {'image_name': img_name}
            row.update(metrics)
            rows.append(row)

            if (idx + 1) % 500 == 0 or (idx + 1) == total_images:
                print(f"  Processed {idx + 1}/{total_images} error metrics...")

        # Save CSV
        os.makedirs(self.output_dir, exist_ok=True)
        csv_path = os.path.join(self.output_dir, "LEVIR_test_error_analysis.csv")
        headers = list(rows[0].keys())

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        # Top Error Cases Extraction
        # 1. Top False Positive Rate (FPR) cases
        top_fp_cases = sorted(rows, key=lambda x: x['fpr'], reverse=True)[:10]

        # 2. Top False Negative Rate (FNR) cases (where GT change > 0)
        gt_has_change = [r for r in rows if r['gt_change_pct'] > 0]
        top_fn_cases = sorted(gt_has_change, key=lambda x: x['fnr'], reverse=True)[:10]

        # 3. Lowest Change IoU cases (where GT change > 0)
        lowest_iou_cases = sorted(gt_has_change, key=lambda x: x['iou'])[:10]

        # Aggregate Summary Statistics
        def calc_stats(metric_name: str) -> Dict[str, float]:
            vals = np.array([r[metric_name] for r in rows])
            return {
                'mean': float(np.mean(vals)),
                'median': float(np.median(vals)),
                'std': float(np.std(vals)),
                'min': float(np.min(vals)),
                'max': float(np.max(vals))
            }

        summary = {
            'total_images_processed': total_images,
            'missing_gt_masks': missing_gt,
            'missing_pred_masks': missing_pred,
            'overall_metrics': {
                'accuracy': calc_stats('accuracy'),
                'precision': calc_stats('precision'),
                'recall': calc_stats('recall'),
                'f1': calc_stats('f1'),
                'iou': calc_stats('iou'),
                'fpr': calc_stats('fpr'),
                'fnr': calc_stats('fnr')
            },
            'top_fp_rate_images': [{'image_name': r['image_name'], 'fpr': r['fpr'], 'fp': r['fp']} for r in top_fp_cases],
            'top_fn_rate_images': [{'image_name': r['image_name'], 'fnr': r['fnr'], 'fn': r['fn']} for r in top_fn_cases],
            'lowest_iou_images': [{'image_name': r['image_name'], 'iou': r['iou'], 'gt_pct': r['gt_change_pct']} for r in lowest_iou_cases]
        }

        json_path = os.path.join(self.output_dir, "LEVIR_error_analysis_summary.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4)

        # Generate Plot Visualizations
        self.generate_error_plots(rows, lowest_iou_cases, top_fp_cases, top_fn_cases)

        return {
            'rows': rows,
            'summary': summary,
            'csv_path': csv_path,
            'json_path': json_path,
            'plots_dir': self.plots_dir
        }

    def generate_error_plots(
        self,
        rows: List[Dict[str, Any]],
        lowest_iou_cases: List[Dict[str, Any]],
        top_fp_cases: List[Dict[str, Any]],
        top_fn_cases: List[Dict[str, Any]]
    ):
        """
        Generates required distribution, scatter, and error overlay visualization plots.
        """
        os.makedirs(self.plots_dir, exist_ok=True)
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

        ious = np.array([r['iou'] for r in rows])
        fprs = np.array([r['fpr'] for r in rows])
        fnrs = np.array([r['fnr'] for r in rows])
        gt_pcts = np.array([r['gt_change_pct'] for r in rows])
        f1s = np.array([r['f1'] for r in rows])

        # 1. Distribution of per-image Change IoU
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(ious, bins=50, color='#1f77b4', edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(ious), color='red', linestyle='--', label=f"Mean IoU: {np.mean(ious):.4f}")
        ax.set_title("Distribution of Per-Image Change-Class IoU", fontsize=13, fontweight='bold')
        ax.set_xlabel("Intersection over Union (IoU)", fontsize=11)
        ax.set_ylabel("Number of Images", fontsize=11)
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "01_change_iou_distribution.png"), dpi=300)
        plt.close()

        # 2. Distribution of False-Positive Rate
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(fprs, bins=50, color='#d62728', edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(fprs), color='black', linestyle='--', label=f"Mean FPR: {np.mean(fprs):.4f}")
        ax.set_title("Distribution of False-Positive Rate (FPR)", fontsize=13, fontweight='bold')
        ax.set_xlabel("False-Positive Rate", fontsize=11)
        ax.set_ylabel("Number of Images", fontsize=11)
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "02_false_positive_rate_distribution.png"), dpi=300)
        plt.close()

        # 3. Distribution of False-Negative Rate
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(fnrs, bins=50, color='#ff7f0e', edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(fnrs), color='black', linestyle='--', label=f"Mean FNR: {np.mean(fnrs):.4f}")
        ax.set_title("Distribution of False-Negative Rate (FNR)", fontsize=13, fontweight='bold')
        ax.set_xlabel("False-Negative Rate", fontsize=11)
        ax.set_ylabel("Number of Images", fontsize=11)
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "03_false_negative_rate_distribution.png"), dpi=300)
        plt.close()

        # 4. GT Change Percentage vs. IoU
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(gt_pcts, ious, alpha=0.5, color='#2ca02c', s=20)
        ax.set_title("Ground-Truth Change % vs. Change IoU", fontsize=13, fontweight='bold')
        ax.set_xlabel("Ground-Truth Change Percentage (%)", fontsize=11)
        ax.set_ylabel("Change IoU", fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "04_gt_change_pct_vs_iou.png"), dpi=300)
        plt.close()

        # 5. GT Change Percentage vs. F1
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(gt_pcts, f1s, alpha=0.5, color='#9467bd', s=20)
        ax.set_title("Ground-Truth Change % vs. F1 Score", fontsize=13, fontweight='bold')
        ax.set_xlabel("Ground-Truth Change Percentage (%)", fontsize=11)
        ax.set_ylabel("F1 Score", fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "05_gt_change_pct_vs_f1.png"), dpi=300)
        plt.close()

        # 6. Top Error Cases Visualization Grid (3 sample cases: lowest IoU, highest FP, highest FN)
        self._visualize_top_error_grid(lowest_iou_cases, top_fp_cases, top_fn_cases)

    def _visualize_top_error_grid(
        self,
        lowest_iou_cases: List[Dict[str, Any]],
        top_fp_cases: List[Dict[str, Any]],
        top_fn_cases: List[Dict[str, Any]]
    ):
        """
        Renders side-by-side error grid visualization: Image A | Image B | Ground Truth | Prediction | Error Overlay (TP=Green, FP=Red, FN=Blue).
        """
        sample_cases = []
        if lowest_iou_cases:
            sample_cases.append(('Lowest IoU Case', lowest_iou_cases[0]['image_name']))
        if top_fp_cases:
            sample_cases.append(('Highest False-Positive Case', top_fp_cases[0]['image_name']))
        if top_fn_cases:
            sample_cases.append(('Highest False-Negative Case', top_fn_cases[0]['image_name']))

        if not sample_cases:
            return

        fig, axes = plt.subplots(len(sample_cases), 5, figsize=(20, 4 * len(sample_cases)))
        if len(sample_cases) == 1:
            axes = np.expand_dims(axes, axis=0)

        for row_idx, (title, img_name) in enumerate(sample_cases):
            a_path = os.path.join(self.img_a_dir, img_name)
            b_path = os.path.join(self.img_b_dir, img_name)
            gt_path = os.path.join(self.gt_dir, img_name)
            pred_path = os.path.join(self.pred_dir, img_name)

            img_a = cv2.imread(a_path) if os.path.exists(a_path) else np.zeros((256, 256, 3), dtype=np.uint8)
            img_b = cv2.imread(b_path) if os.path.exists(b_path) else np.zeros((256, 256, 3), dtype=np.uint8)
            gt = cv2.imread(gt_path, cv2.IMREAD_GRAYSCALE) if os.path.exists(gt_path) else np.zeros((256, 256), dtype=np.uint8)
            pred = cv2.imread(pred_path, cv2.IMREAD_GRAYSCALE) if os.path.exists(pred_path) else np.zeros((256, 256), dtype=np.uint8)

            img_a_rgb = cv2.cvtColor(img_a, cv2.COLOR_BGR2RGB)
            img_b_rgb = cv2.cvtColor(img_b, cv2.COLOR_BGR2RGB)

            gt_bin = (gt > 0).astype(np.uint8)
            pred_bin = (pred > 0).astype(np.uint8)

            # Error overlay: TP = Green (0,255,0), FP = Red (255,0,0), FN = Blue (0,0,255)
            overlay = np.zeros((256, 256, 3), dtype=np.uint8)
            tp_mask = (pred_bin == 1) & (gt_bin == 1)
            fp_mask = (pred_bin == 1) & (gt_bin == 0)
            fn_mask = (pred_bin == 0) & (gt_bin == 1)

            overlay[tp_mask] = [0, 255, 0]   # Green = TP
            overlay[fp_mask] = [255, 0, 0]   # Red = FP
            overlay[fn_mask] = [0, 100, 255] # Blue = FN

            axes[row_idx, 0].imshow(img_a_rgb)
            axes[row_idx, 0].set_title(f"{title}\nImage A ({img_name})")
            axes[row_idx, 0].axis('off')

            axes[row_idx, 1].imshow(img_b_rgb)
            axes[row_idx, 1].set_title(f"Image B")
            axes[row_idx, 1].axis('off')

            axes[row_idx, 2].imshow(gt_bin * 255, cmap='gray')
            axes[row_idx, 2].set_title(f"Ground Truth")
            axes[row_idx, 2].axis('off')

            axes[row_idx, 3].imshow(pred_bin * 255, cmap='gray')
            axes[row_idx, 3].set_title(f"Prediction Mask")
            axes[row_idx, 3].axis('off')

            axes[row_idx, 4].imshow(overlay)
            axes[row_idx, 4].set_title(f"Error Map\n(Green:TP, Red:FP, Blue:FN)")
            axes[row_idx, 4].axis('off')

        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "06_top_error_cases_visualization.png"), dpi=300)
        plt.close()


def run_levir_test_error_analysis():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    list_file = os.path.join(base_dir, "LEVIR-CD256", "list", "test.txt")
    gt_dir = os.path.join(base_dir, "LEVIR-CD256", "label")
    pred_dir = os.path.join(base_dir, "LEVIR-CD256", "predict_ChangeFormer")
    img_a_dir = os.path.join(base_dir, "LEVIR-CD256", "A")
    img_b_dir = os.path.join(base_dir, "LEVIR-CD256", "B")
    output_dir = os.path.join(base_dir, "analysis", "results")

    analyzer = ErrorAnalysisPipeline(
        list_file=list_file,
        gt_dir=gt_dir,
        pred_dir=pred_dir,
        img_a_dir=img_a_dir,
        img_b_dir=img_b_dir,
        output_dir=output_dir
    )

    return analyzer.run_analysis()


if __name__ == '__main__':
    run_levir_test_error_analysis()
