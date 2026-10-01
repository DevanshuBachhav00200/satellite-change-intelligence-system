import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Tuple, Optional


class ChangeAnalyzer:
    """
    Independent post-processing analysis layer for ChangeFormer binary prediction masks.
    Operates on 2D numpy array binary masks (values: 0=no change, 1 or 255=change).
    """

    def __init__(self, min_region_area: int = 1):
        """
        Args:
            min_region_area (int): Minimum pixel area threshold to consider a connected component a valid changed region.
                                   Helps filter out isolated noise pixels if desired. Default is 1 (no filtering).
        """
        self.min_region_area = min_region_area

    def process(self, mask: np.ndarray, grid_size: Tuple[int, int] = (4, 4)) -> Dict[str, Any]:
        """
        Executes full post-processing metric analysis on a binary change mask.

        Args:
            mask (np.ndarray): 2D binary numpy array representing change prediction mask (values 0 and 1/255).
            grid_size (Tuple[int, int]): Dimensions (rows, cols) for spatial density grid evaluation.

        Returns:
            Dict[str, Any]: Dictionary containing all 10 metric results.
        """
        binary_mask = self._preprocess_mask(mask)
        height, width = binary_mask.shape

        # 1. Total changed pixel count
        total_changed_pixels = int(np.sum(binary_mask == 1))

        # 2. Total image pixel count
        total_image_pixels = int(height * width)

        # 3. Change percentage
        change_percentage = float((total_changed_pixels / total_image_pixels) * 100.0) if total_image_pixels > 0 else 0.0

        # Connected components analysis using OpenCV
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary_mask.astype(np.uint8), connectivity=8
        )

        region_areas: List[int] = []
        bounding_boxes: List[Tuple[int, int, int, int]] = []
        region_centroids: List[Tuple[float, float]] = []

        # Index 0 corresponds to background label, iterate through connected foreground regions
        for i in range(1, num_labels):
            area = int(stats[i, cv2.CC_STAT_AREA])
            if area >= self.min_region_area:
                x = int(stats[i, cv2.CC_STAT_LEFT])
                y = int(stats[i, cv2.CC_STAT_TOP])
                w = int(stats[i, cv2.CC_STAT_WIDTH])
                h = int(stats[i, cv2.CC_STAT_HEIGHT])
                cx = float(centroids[i][0])
                cy = float(centroids[i][1])

                region_areas.append(area)
                bounding_boxes.append((x, y, w, h))
                region_centroids.append((cx, cy))

        # 4. Number of connected changed regions
        num_connected_regions = len(region_areas)

        # 5. Area of each connected region (already in region_areas)

        # 6. Largest changed region (in pixels)
        largest_region_area = max(region_areas) if num_connected_regions > 0 else 0

        # 7. Bounding boxes (already in bounding_boxes)
        # 8. Centroids (already in region_centroids)

        # 9. Average changed-region area
        avg_region_area = float(np.mean(region_areas)) if num_connected_regions > 0 else 0.0

        # 10. Spatial density / grid-based distribution of change
        spatial_density_grid = self._calculate_spatial_density(binary_mask, grid_size)

        return {
            'total_changed_pixels': total_changed_pixels,
            'total_image_pixels': total_image_pixels,
            'change_percentage': change_percentage,
            'num_connected_regions': num_connected_regions,
            'region_areas': region_areas,
            'largest_region_area': largest_region_area,
            'bounding_boxes': bounding_boxes,
            'centroids': region_centroids,
            'avg_region_area': avg_region_area,
            'spatial_density_grid': spatial_density_grid,
            'mask_shape': (height, width)
        }

    def _preprocess_mask(self, mask: np.ndarray) -> np.ndarray:
        """
        Ensures input mask is a 2D uint8 numpy array with values standard 0 (no change) and 1 (change).
        """
        if mask.ndim > 2:
            mask = mask.squeeze()
        if mask.ndim != 2:
            raise ValueError(f"Input mask must be a 2D array, got shape {mask.shape}")

        binary_mask = (mask > 0).astype(np.uint8)
        return binary_mask

    def _calculate_spatial_density(self, binary_mask: np.ndarray, grid_size: Tuple[int, int]) -> np.ndarray:
        """
        Calculates percentage of change within each cell of an N x M grid overlaid on the mask.

        Args:
            binary_mask (np.ndarray): 2D binary numpy array (0/1).
            grid_size (Tuple[int, int]): (rows, cols) grid dimensions.

        Returns:
            np.ndarray: 2D array of shape grid_size containing change percentage for each grid cell.
        """
        height, width = binary_mask.shape
        grid_rows, grid_cols = grid_size
        density_grid = np.zeros(grid_size, dtype=np.float64)

        row_edges = np.linspace(0, height, grid_rows + 1, dtype=int)
        col_edges = np.linspace(0, width, grid_cols + 1, dtype=int)

        for r in range(grid_rows):
            for c in range(grid_cols):
                r_start, r_end = row_edges[r], row_edges[r + 1]
                c_start, c_end = col_edges[c], col_edges[c + 1]

                cell = binary_mask[r_start:r_end, c_start:c_end]
                cell_total = cell.size
                if cell_total > 0:
                    density_grid[r, c] = (np.sum(cell == 1) / cell_total) * 100.0

        return density_grid


def analyze_change_mask(mask: np.ndarray, grid_size: Tuple[int, int] = (4, 4), min_region_area: int = 1) -> Dict[str, Any]:
    """
    Functional wrapper to analyze a binary change mask.

    Args:
        mask (np.ndarray): Binary prediction mask.
        grid_size (Tuple[int, int]): Grid size for spatial density.
        min_region_area (int): Minimum region size filter.

    Returns:
        Dict[str, Any]: Extracted metrics dictionary.
    """
    analyzer = ChangeAnalyzer(min_region_area=min_region_area)
    return analyzer.process(mask, grid_size=grid_size)


def visualize_change_analysis(
    mask: np.ndarray,
    analysis_results: Dict[str, Any],
    save_path: Optional[str] = None,
    draw_centroids: bool = True,
    draw_grid: bool = True
) -> np.ndarray:
    """
    Generates side-by-side visualization of:
    1. Original Binary Change Mask
    2. Detected Change Regions with Bounding Boxes and Centroids
    3. Spatial Density Heatmap

    Args:
        mask (np.ndarray): Original 2D binary mask array.
        analysis_results (Dict[str, Any]): Results from ChangeAnalyzer.
        save_path (Optional[str]): Path to save output plot.
        draw_centroids (bool): Whether to plot centroid markers.
        draw_grid (bool): Whether to overlay spatial grid on regions.

    Returns:
        np.ndarray: Rendered RGB image array of the visualization.
    """
    binary_mask = (mask > 0).astype(np.uint8) * 255
    h, w = binary_mask.shape

    # Create 3-channel BGR visualization image for annotation
    annotated = cv2.cvtColor(binary_mask, cv2.COLOR_GRAY2BGR)

    bounding_boxes = analysis_results.get('bounding_boxes', [])
    centroids = analysis_results.get('centroids', [])

    # Draw bounding boxes and centroids
    for idx, (x, y, bw, bh) in enumerate(bounding_boxes):
        # Draw bounding box (lime green)
        cv2.rectangle(annotated, (x, y), (x + bw, y + bh), (0, 255, 0), 2)

        if draw_centroids and idx < len(centroids):
            cx, cy = centroids[idx]
            # Draw centroid marker (red circle with dot)
            cv2.circle(annotated, (int(cx), int(cy)), 3, (0, 0, 255), -1)
            cv2.circle(annotated, (int(cx), int(cy)), 5, (255, 0, 0), 1)

    # Optional grid overlay
    if draw_grid and 'spatial_density_grid' in analysis_results:
        grid_rows, grid_cols = analysis_results['spatial_density_grid'].shape
        row_step = h / grid_rows
        col_step = w / grid_cols
        for r in range(1, grid_rows):
            cv2.line(annotated, (0, int(r * row_step)), (w, int(r * row_step)), (255, 255, 0), 1, cv2.LINE_AA)
        for c in range(1, grid_cols):
            cv2.line(annotated, (int(c * col_step), 0), (int(c * col_step), h), (255, 255, 0), 1, cv2.LINE_AA)

    # Plot using Matplotlib
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Subplot 1: Original Mask
    axes[0].imshow(binary_mask, cmap='gray')
    axes[0].set_title(f"Original Binary Mask\n(Change: {analysis_results['change_percentage']:.2f}%)")
    axes[0].axis('off')

    # Subplot 2: Detected Regions & Annotations
    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
    axes[1].imshow(annotated_rgb)
    axes[1].set_title(f"Annotated Regions & Centroids\n({analysis_results['num_connected_regions']} Regions Detected)")
    axes[1].axis('off')

    # Subplot 3: Spatial Density Heatmap
    density_grid = analysis_results['spatial_density_grid']
    im = axes[2].imshow(density_grid, cmap='magma', interpolation='nearest')
    axes[2].set_title("Spatial Density Grid (%)")
    fig.colorbar(im, ax=axes[2], fraction=0.046, pad=0.04)

    # Annotate cell values on heatmap
    rows, cols = density_grid.shape
    for r in range(rows):
        for c in range(cols):
            axes[2].text(c, r, f"{density_grid[r, c]:.1f}%",
                         ha="center", va="center", color="white" if density_grid[r, c] < 50 else "black",
                         fontsize=9, fontweight='bold')

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    fig.canvas.draw()
    # Convert canvas to numpy array
    buf = fig.canvas.buffer_rgba()
    vis_arr = np.asarray(buf)[:, :, :3]
    plt.close(fig)

    return vis_arr
