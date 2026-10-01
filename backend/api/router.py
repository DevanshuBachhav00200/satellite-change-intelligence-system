import os
import sys
import io
import base64
import numpy as np
import cv2
import requests
from PIL import Image
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

import matplotlib
matplotlib.use('Agg')

# Add project root directory to path so analysis modules can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from analysis.change_intelligence_pipeline import SatelliteChangeIntelligencePipeline
from analysis.change_analyzer import analyze_change_mask, visualize_change_analysis

router = APIRouter()

# Global pipeline reference (initialized lazily or on startup)
pipeline_instance: Optional[SatelliteChangeIntelligencePipeline] = None


def get_checkpoint_path() -> str:
    """Returns absolute path to trained model checkpoint from environment or default location."""
    env_path = os.environ.get("MODEL_CHECKPOINT_PATH")
    if env_path:
        return os.path.abspath(env_path)
    return os.path.join(PROJECT_ROOT, "checkpoints", "ChangeFormer_LEVIR", "best_ckpt.pt")


def download_checkpoint_if_configured(ckpt_path: str):
    """
    Downloads model checkpoint from MODEL_DOWNLOAD_URL using streaming I/O if the file is missing locally.
    """
    if os.path.exists(ckpt_path):
        return

    download_url = os.environ.get("MODEL_DOWNLOAD_URL", "").strip()
    if not download_url:
        raise FileNotFoundError(
            f"Model checkpoint file not found at '{ckpt_path}'. "
            "Please provide 'best_ckpt.pt' in the checkpoints folder or set the 'MODEL_DOWNLOAD_URL' environment variable for automated streaming download."
        )

    print(f"[INFO] Checkpoint missing at '{ckpt_path}'. Downloading from MODEL_DOWNLOAD_URL...")
    os.makedirs(os.path.dirname(os.path.abspath(ckpt_path)), exist_ok=True)
    temp_path = ckpt_path + ".tmp"

    try:
        with requests.get(download_url, stream=True, timeout=120) as response:
            response.raise_for_status()
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        os.replace(temp_path, ckpt_path)
        print(f"[OK] Successfully downloaded model checkpoint to '{ckpt_path}'.")
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise RuntimeError(f"Failed to download model checkpoint from '{download_url}': {str(e)}")


def get_pipeline() -> SatelliteChangeIntelligencePipeline:
    """Instantiates and returns the cached ChangeFormer pipeline."""
    global pipeline_instance
    if pipeline_instance is None:
        ckpt_path = get_checkpoint_path()
        download_checkpoint_if_configured(ckpt_path)
        pipeline_instance = SatelliteChangeIntelligencePipeline(checkpoint_path=ckpt_path)
    return pipeline_instance


def array_to_base64_png(img_arr: np.ndarray, is_rgb: bool = False) -> str:
    """Converts numpy image array to base64 data URI PNG string."""
    if is_rgb:
        bgr_arr = cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR)
    else:
        bgr_arr = img_arr
    
    success, buffer = cv2.imencode('.png', bgr_arr)
    if not success:
        raise ValueError("Failed to encode image to PNG format")
    
    b64_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"


def validate_image_bytes(image_bytes: bytes, filename: str = "image") -> np.ndarray:
    """Validates uploaded image bytes and converts to 3-channel RGB numpy array."""
    try:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img_np = np.array(pil_img)
        if img_np.ndim != 3 or img_np.shape[2] != 3:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image dimensions for {filename}. Expected 3-channel RGB image, got shape {img_np.shape}"
            )
        return img_np
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Failed to decode image '{filename}': {str(e)}")


@router.get("/health")
async def health_check():
    """Returns backend status, model loading state, hardware device, and checkpoint status."""
    ckpt_path = get_checkpoint_path()
    checkpoint_exists = os.path.exists(ckpt_path)

    try:
        pipe = get_pipeline()
        device_str = str(pipe.device)
        return {
            "status": "healthy",
            "model_loaded": True,
            "architecture": pipe.net_G_name,
            "device": device_str,
            "cuda_available": device_str.startswith("cuda"),
            "checkpoint_exists": True
        }
    except Exception as e:
        return {
            "status": "degraded" if checkpoint_exists else "unhealthy",
            "model_loaded": False,
            "error": str(e),
            "checkpoint_exists": checkpoint_exists
        }


@router.get("/samples")
async def get_levir_samples():
    """Returns available LEVIR-CD sample image pair names."""
    sample_dir = os.path.join(PROJECT_ROOT, "LEVIR-CD256", "A")
    if not os.path.exists(sample_dir):
        return {"samples": []}
    
    samples = sorted([f for f in os.listdir(sample_dir) if f.endswith(".png")])
    return {"samples": samples}


@router.post("/analyze")
async def analyze_images(
    image_a: UploadFile = File(...),
    image_b: UploadFile = File(...)
):
    """
    Accepts bi-temporal image pair uploads, runs ChangeFormer inference and spatial CII assessment.
    Returns structured analysis metrics and Base64-encoded prediction mask & visualization.
    """
    bytes_a = await image_a.read()
    bytes_b = await image_b.read()

    img_a_np = validate_image_bytes(bytes_a, image_a.filename or "Image A")
    img_b_np = validate_image_bytes(bytes_b, image_b.filename or "Image B")

    return run_pipeline_analysis(img_a_np, img_b_np)


class SampleAnalysisRequest(BaseModel):
    sample_name: str = "test_100_10.png"


@router.post("/analyze-sample")
async def analyze_sample(req: SampleAnalysisRequest):
    """
    Runs analysis directly on a LEVIR-CD test set sample pair.
    """
    path_a = os.path.join(PROJECT_ROOT, "LEVIR-CD256", "A", req.sample_name)
    path_b = os.path.join(PROJECT_ROOT, "LEVIR-CD256", "B", req.sample_name)

    if not os.path.exists(path_a) or not os.path.exists(path_b):
        raise HTTPException(
            status_code=404,
            detail=f"Sample pair '{req.sample_name}' not found in LEVIR-CD256 dataset directory."
        )

    pil_a = Image.open(path_a).convert('RGB')
    pil_b = Image.open(path_b).convert('RGB')

    img_a_np = np.array(pil_a)
    img_b_np = np.array(pil_b)

    result = run_pipeline_analysis(img_a_np, img_b_np)
    # Include previews for sample loading in UI
    result["image_a_preview"] = array_to_base64_png(img_a_np, is_rgb=True)
    result["image_b_preview"] = array_to_base64_png(img_b_np, is_rgb=True)
    result["sample_name"] = req.sample_name
    return result


def run_pipeline_analysis(img_a_np: np.ndarray, img_b_np: np.ndarray) -> Dict[str, Any]:
    """Helper function to execute pipeline and format complete response."""
    pipe = get_pipeline()
    
    try:
        res = pipe.process_pair(img_a_np, img_b_np)
        
        pred_mask = res['prediction_mask']
        
        # Generate side-by-side visualization
        full_analysis = analyze_change_mask(pred_mask, grid_size=(4, 4))
        vis_fig_arr = visualize_change_analysis(pred_mask, full_analysis, draw_centroids=True, draw_grid=True)
        
        # Convert images to Base64 PNGs
        mask_b64 = array_to_base64_png(pred_mask, is_rgb=False)
        vis_b64 = array_to_base64_png(vis_fig_arr, is_rgb=True)

        return {
            "changed_pixel_count": int(res['changed_pixel_count']),
            "total_pixel_count": int(res['total_pixel_count']),
            "change_percentage": float(res['change_percentage']),
            "connected_region_count": int(res['connected_region_count']),
            "largest_region_area": float(res['largest_region_area']),
            "average_region_area": float(res['average_region_area']),
            "grid_density_statistics": {
                "max": float(res['grid_density_statistics']['max']),
                "grid": res['grid_density_statistics']['grid']
            },
            "cii_score": float(res['cii_score']),
            "impact_category": str(res['impact_category']),
            "primary_driver": str(res['primary_driver']),
            "factor_contributions": {
                "extent_pct": float(res['factor_contributions']['extent_pct']),
                "concentration_pct": float(res['factor_contributions']['concentration_pct']),
                "scale_pct": float(res['factor_contributions']['scale_pct'])
            },
            "prediction_mask": mask_b64,
            "analysis_visualization": vis_b64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")
