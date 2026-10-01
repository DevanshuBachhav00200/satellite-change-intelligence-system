import os
import sys
import argparse
import torch
import numpy as np
import cv2
from PIL import Image
from typing import Dict, Any, Union, Optional
from torchvision import transforms
import torchvision.transforms.functional as TF

# Ensure analysis package import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.networks import define_G
from misc.imutils import save_image
from analysis.change_analyzer import analyze_change_mask, visualize_change_analysis
from analysis.change_impact_assessor import ChangeImpactAssessor


class SatelliteChangeIntelligencePipeline:
    """
    Integrated Satellite Change Intelligence Pipeline.
    Accepts bi-temporal satellite image pair (Image A, Image B), runs ChangeFormer model inference,
    extracts spatial change features, and computes the explainable Change Impact Index (CII).
    """

    def __init__(
        self,
        checkpoint_path: str = "checkpoints/ChangeFormer_LEVIR/best_ckpt.pt",
        net_G: str = "ChangeFormerV6",
        img_size: int = 256,
        embed_dim: int = 256,
        n_class: int = 2,
        gpu_ids: str = "0"
    ):
        self.checkpoint_path = os.path.abspath(checkpoint_path)
        self.net_G_name = net_G
        self.img_size = img_size
        self.embed_dim = embed_dim
        self.n_class = n_class
        self.gpu_ids = gpu_ids

        # Set device
        if torch.cuda.is_available() and gpu_ids != "-1":
            str_ids = gpu_ids.split(',')
            device_id = int(str_ids[0]) if str_ids[0] != '' else 0
            self.device = torch.device(f"cuda:{device_id}")
        else:
            self.device = torch.device("cpu")

        # Load ChangeFormer model
        self.model = self._load_model()
        self.assessor = ChangeImpactAssessor()

    def _load_model(self) -> torch.nn.Module:
        """
        Instantiates ChangeFormer network architecture and loads weights from checkpoint.
        """
        if not os.path.exists(self.checkpoint_path):
            raise FileNotFoundError(f"Checkpoint file not found: {self.checkpoint_path}")

        # Construct args matching ChangeFormer model definition
        args = argparse.Namespace()
        args.net_G = self.net_G_name
        args.img_size = self.img_size
        args.embed_dim = self.embed_dim
        args.n_class = self.n_class
        args.gpu_ids = [0] if self.device.type == 'cuda' else []

        net_G = define_G(args=args, gpu_ids=args.gpu_ids)

        checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        if 'model_G_state_dict' in checkpoint:
            net_G.load_state_dict(checkpoint['model_G_state_dict'])
        else:
            net_G.load_state_dict(checkpoint)

        net_G.to(self.device)
        net_G.eval()
        return net_G

    def preprocess_image(self, img_input: Union[str, np.ndarray, Image.Image]) -> torch.Tensor:
        """
        Preprocesses an input image (filepath, numpy array, or PIL Image)
        to match exact ChangeFormer evaluation transforms:
        Resize to (256, 256) -> ToTensor [0, 1] -> Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]).
        """
        if isinstance(img_input, str):
            if not os.path.exists(img_input):
                raise FileNotFoundError(f"Input image file not found: {img_input}")
            pil_img = Image.open(img_input).convert('RGB')
        elif isinstance(img_input, np.ndarray):
            if img_input.ndim == 2:
                img_input = cv2.cvtColor(img_input, cv2.COLOR_GRAY2RGB)
            elif img_input.shape[2] == 4:
                img_input = cv2.cvtColor(img_input, cv2.COLOR_RGBA2RGB)
            pil_img = Image.fromarray(img_input.astype(np.uint8))
        elif isinstance(img_input, Image.Image):
            pil_img = img_input.convert('RGB')
        else:
            raise TypeError(f"Unsupported image input type: {type(img_input)}")

        # Resize if necessary
        if pil_img.size != (self.img_size, self.img_size):
            pil_img = pil_img.resize((self.img_size, self.img_size), Image.BICUBIC)

        tensor_img = TF.to_tensor(pil_img)
        tensor_img = TF.normalize(tensor_img, mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        tensor_img = tensor_img.unsqueeze(0).to(self.device)

        return tensor_img

    def process_pair(
        self,
        img_a: Union[str, np.ndarray, Image.Image],
        img_b: Union[str, np.ndarray, Image.Image],
        save_mask_path: Optional[str] = None,
        save_vis_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs complete satellite change intelligence pipeline on an image pair.

        Returns:
            Dict[str, Any]: Structured dictionary with all 12 required fields.
        """
        # 1. Preprocess Image A and Image B
        t_a = self.preprocess_image(img_a)
        t_b = self.preprocess_image(img_b)

        # 2. ChangeFormer GPU Inference
        with torch.no_grad():
            logits = self.model(t_a, t_b)[-1]
            pred_tensor = torch.argmax(logits, dim=1, keepdim=True) * 255
            pred_np = pred_tensor.squeeze().cpu().numpy().astype(np.uint8)

        # 3. Spatial Change Analysis
        change_analysis = analyze_change_mask(pred_np, grid_size=(4, 4))
        grid_max = float(np.max(change_analysis['spatial_density_grid']))

        # 4. Explainable Change Impact Assessment (CII)
        impact_res = self.assessor.compute_cii_from_features(
            change_percentage=change_analysis['change_percentage'],
            grid_density_max=grid_max,
            largest_region_area=change_analysis['largest_region_area'],
            connected_region_count=change_analysis['num_connected_regions'],
            average_region_area=change_analysis['avg_region_area']
        )

        # 5. Assemble Structured Output Dictionary
        result = {
            'prediction_mask': pred_np,
            'changed_pixel_count': change_analysis['total_changed_pixels'],
            'total_pixel_count': change_analysis['total_image_pixels'],
            'change_percentage': change_analysis['change_percentage'],
            'connected_region_count': change_analysis['num_connected_regions'],
            'largest_region_area': float(change_analysis['largest_region_area']),
            'average_region_area': float(change_analysis['avg_region_area']),
            'grid_density_statistics': {
                'max': grid_max,
                'grid': change_analysis['spatial_density_grid'].tolist()
            },
            'cii_score': impact_res['cii_score'],
            'impact_category': impact_res['impact_category'],
            'primary_driver': impact_res['primary_driver'],
            'factor_contributions': impact_res['factor_contributions']
        }

        # 6. Save Artifacts if Requested
        if save_mask_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_mask_path)), exist_ok=True)
            save_image(pred_np, save_mask_path)
            result['saved_mask_path'] = os.path.abspath(save_mask_path)

        if save_vis_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_vis_path)), exist_ok=True)
            visualize_change_analysis(
                mask=pred_np,
                analysis_results=change_analysis,
                save_path=save_vis_path,
                draw_centroids=True,
                draw_grid=True
            )
            result['saved_vis_path'] = os.path.abspath(save_vis_path)

        return result


def run_change_intelligence_pipeline(
    img_a: Union[str, np.ndarray, Image.Image],
    img_b: Union[str, np.ndarray, Image.Image],
    checkpoint_path: str = "checkpoints/ChangeFormer_LEVIR/best_ckpt.pt",
    save_mask_path: Optional[str] = None,
    save_vis_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to run Satellite Change Intelligence Pipeline on an image pair.
    """
    pipeline = SatelliteChangeIntelligencePipeline(checkpoint_path=checkpoint_path)
    return pipeline.process_pair(
        img_a=img_a,
        img_b=img_b,
        save_mask_path=save_mask_path,
        save_vis_path=save_vis_path
    )


if __name__ == '__main__':
    img_a_sample = "LEVIR-CD256/A/test_100_10.png"
    img_b_sample = "LEVIR-CD256/B/test_100_10.png"
    if os.path.exists(img_a_sample) and os.path.exists(img_b_sample):
        res = run_change_intelligence_pipeline(img_a_sample, img_b_sample)
        print("Pipeline Execution Output:")
        for k, v in res.items():
            if k != 'prediction_mask':
                print(f"  {k}: {v}")
