from typing import Optional
import os
import sys
import io
import torch
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import streamlit as st

# Ensure analysis package import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.change_intelligence_pipeline import SatelliteChangeIntelligencePipeline
from analysis.change_analyzer import analyze_change_mask, visualize_change_analysis


# Page configuration
st.set_page_config(
    page_title="Satellite Change Intelligence System",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Academic/Research Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        font-weight: 400;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0.3rem 0;
    }
    .badge-low {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .badge-moderate {
        background-color: #FEF08A;
        color: #713F12;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .badge-high {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .badge-zero {
        background-color: #F3F4F6;
        color: #374151;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_pipeline():
    """
    Caches the model pipeline instantiation across user sessions.
    """
    ckpt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "checkpoints", "ChangeFormer_LEVIR", "best_ckpt.pt")
    gpu_id = "0" if torch.cuda.is_available() else "-1"
    return SatelliteChangeIntelligencePipeline(checkpoint_path=ckpt_path, gpu_ids=gpu_id)


def render_sidebar():
    st.sidebar.image("https://img.icons8.com/isometric/96/satellite.png", width=64)
    st.sidebar.title("Satellite Intelligence")
    st.sidebar.markdown("**Temporal Change Detection & Impact Analysis**")
    st.sidebar.markdown("---")

    st.sidebar.subheader("System Architecture")
    st.sidebar.markdown("""
    - **Model Architecture**: ChangeFormerV6 (Transformer)
    - **Pretrained Checkpoint**: `ChangeFormer_LEVIR`
    - **Dataset Benchmark**: LEVIR-CD256
    - **Hardware Engine**: PyTorch (CUDA GPU Accelerated)
    """)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Change Impact Index (CII)")
    st.sidebar.markdown("""
    An explainable image-based index $S \in [0, 100]$:
    $$\\text{CII} = 100 \\times (0.40 \\cdot f_{\\text{extent}} + 0.35 \\cdot f_{\\text{conc}} + 0.25 \\cdot f_{\\text{scale}})$$

    **Categories**:
    - **Zero Impact**: $\\text{CII} = 0.0$
    - **Low Impact**: $0.0 < \\text{CII} \\le 30.0$
    - **Moderate Impact**: $30.0 < \\text{CII} \\le 55.0$
    - **High Impact**: $\\text{CII} > 55.0$
    """)


def validate_and_convert_image(uploaded_file) -> Optional[np.ndarray]:
    """
    Validates uploaded file / path to ensure it is a valid 3-channel RGB image.
    """
    try:
        if isinstance(uploaded_file, str):
            pil_img = Image.open(uploaded_file).convert('RGB')
        else:
            pil_img = Image.open(uploaded_file).convert('RGB')
        arr = np.array(pil_img)
        if arr.ndim != 3 or arr.shape[2] != 3:
            st.error(f"Image must be 3-channel RGB format, got shape {arr.shape}")
            return None
        return arr
    except Exception as e:
        st.error(f"Failed to load image: {str(e)}")
        return None


def main():
    render_sidebar()

    st.markdown('<div class="main-header">Satellite Change Intelligence System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Bitemporal Change Detection & Explainable Change Impact Assessment (ChangeFormer-V6)</div>', unsafe_allow_html=True)

    pipeline = load_pipeline()

    # Input Mode Selection
    input_mode = st.radio("Choose Input Source:", ["Use LEVIR-CD Sample Test Pair", "Upload Custom Image Pair"], horizontal=True)

    img_a_arr = None
    img_b_arr = None
    sample_name = "test_100_10.png"

    if input_mode == "Use LEVIR-CD Sample Test Pair":
        sample_dir_a = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LEVIR-CD256", "A")
        available_samples = [f for f in os.listdir(sample_dir_a) if f.endswith('.png')] if os.path.exists(sample_dir_a) else ["test_100_10.png"]
        selected_sample = st.selectbox("Select LEVIR-CD Test Pair:", available_samples, index=available_samples.index("test_100_10.png") if "test_100_10.png" in available_samples else 0)
        
        path_a = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LEVIR-CD256", "A", selected_sample)
        path_b = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LEVIR-CD256", "B", selected_sample)
        
        img_a_arr = validate_and_convert_image(path_a)
        img_b_arr = validate_and_convert_image(path_b)
        sample_name = selected_sample

    else:
        col_up1, col_up2 = st.columns(2)
        with col_up1:
            up_a = st.file_uploader("Upload Image A (T1 / Before)", type=["png", "jpg", "jpeg", "tif"])
            if up_a is not None:
                img_a_arr = validate_and_convert_image(up_a)
        with col_up2:
            up_b = st.file_uploader("Upload Image B (T2 / After)", type=["png", "jpg", "jpeg", "tif"])
            if up_b is not None:
                img_b_arr = validate_and_convert_image(up_b)

    # Display Bitemporal Inputs
    if img_a_arr is not None and img_b_arr is not None:
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.image(img_a_arr, caption="Image A (T1 / Before)", use_column_width=True)
        with col_img2:
            st.image(img_b_arr, caption="Image B (T2 / After)", use_column_width=True)

        # Analyze Button
        if st.button("🚀 Analyze Change Intelligence", type="primary", use_container_width=True):
            with st.spinner("Running ChangeFormer inference & spatial analysis..."):
                try:
                    result = pipeline.process_pair(img_a_arr, img_b_arr)

                    st.markdown("---")
                    st.subheader("📊 Change Intelligence Analysis Results")

                    # Primary Metrics Banner
                    c1, c2, c3, c4 = st.columns(4)

                    cat = result['impact_category']
                    badge_class = "badge-zero"
                    if cat == "Low Impact": badge_class = "badge-low"
                    elif cat == "Moderate Impact": badge_class = "badge-moderate"
                    elif cat == "High Impact": badge_class = "badge-high"

                    with c1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">Change Impact Index</div>
                            <div class="metric-value">{result['cii_score']:.2f} / 100</div>
                            <span class="{badge_class}">{cat}</span>
                        </div>
                        """, unsafe_allow_html=True)

                    with c2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">Change Percentage</div>
                            <div class="metric-value">{result['change_percentage']:.4f}%</div>
                            <div style="font-size: 0.8rem; color: #64748B;">{result['changed_pixel_count']:,} / {result['total_pixel_count']:,} px</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with c3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">Connected Regions</div>
                            <div class="metric-value">{result['connected_region_count']}</div>
                            <div style="font-size: 0.8rem; color: #64748B;">Largest: {result['largest_region_area']:.0f} px</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with c4:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">Primary Driver</div>
                            <div class="metric-value" style="font-size: 1.1rem; margin-top: 0.6rem;">{result['primary_driver']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Visualizations & Masks
                    col_vis1, col_vis2 = st.columns(2)

                    pred_mask = result['prediction_mask']

                    with col_vis1:
                        st.subheader("Predicted Change Mask")
                        st.image(pred_mask, caption="ChangeFormer Binary Prediction (0=Background, 255=Change)", use_column_width=True)

                        # Download Prediction Mask
                        is_success, buffer = cv2.imencode(".png", pred_mask)
                        if is_success:
                            st.download_button(
                                label="📥 Download Binary Prediction Mask (.png)",
                                data=buffer.tobytes(),
                                file_name=f"predict_{sample_name}",
                                mime="image/png"
                            )

                    with col_vis2:
                        st.subheader("Annotated Change Analysis")
                        # Generate side-by-side annotated visualization image
                        vis_analysis = {
                            'change_percentage': result['change_percentage'],
                            'num_connected_regions': result['connected_region_count'],
                            'largest_region_area': result['largest_region_area'],
                            'avg_region_area': result['average_region_area'],
                            'bounding_boxes': [],  # Re-computed inside pipeline or visualization
                            'centroids': [],
                            'spatial_density_grid': np.array(result['grid_density_statistics']['grid'])
                        }
                        
                        # Re-run single mask analysis for visualization bounding boxes
                        full_analysis = analyze_change_mask(pred_mask, grid_size=(4, 4))
                        vis_fig_arr = visualize_change_analysis(pred_mask, full_analysis, draw_centroids=True, draw_grid=True)
                        st.image(vis_fig_arr, caption="Annotated Regions (Green), Centroids (Red/Blue), & Density Grid", use_column_width=True)

                        # Download Visualization Figure
                        vis_pil = Image.fromarray(vis_fig_arr)
                        buf_vis = io.BytesIO()
                        vis_pil.save(buf_vis, format="PNG")
                        st.download_button(
                            label="📥 Download Annotated Analysis Visualization (.png)",
                            data=buf_vis.getvalue(),
                            file_name=f"vis_analysis_{sample_name}",
                            mime="image/png"
                        )

                    # Detailed Explanations
                    st.markdown("---")
                    st.subheader("🔍 Factor Contribution Breakdown & Spatial Density")

                    col_exp1, col_exp2 = st.columns(2)
                    with col_exp1:
                        st.markdown("**CII Factor Contributions:**")
                        contribs = result['factor_contributions']
                        st.progress(contribs['extent_pct'] / 100.0, text=f"Extent (Overall Coverage): {contribs['extent_pct']:.2f}%")
                        st.progress(contribs['concentration_pct'] / 100.0, text=f"Concentration (Cluster Severity): {contribs['concentration_pct']:.2f}%")
                        st.progress(contribs['scale_pct'] / 100.0, text=f"Scale (Structural Footprint): {contribs['scale_pct']:.2f}%")

                    with col_exp2:
                        st.markdown("**Grid Density Distribution (4x4 Spatial Cell %):**")
                        grid_matrix = np.array(result['grid_density_statistics']['grid'])
                        st.dataframe(grid_matrix.round(2), use_container_width=True)

                except Exception as e:
                    st.error(f"An error occurred during pipeline execution: {str(e)}")
                    st.exception(e)
    else:
        st.info("Please select or upload both Image A and Image B to begin analysis.")


if __name__ == '__main__':
    main()
