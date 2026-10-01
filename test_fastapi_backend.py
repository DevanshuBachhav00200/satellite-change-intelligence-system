import os
import sys
import requests
import json
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from backend.main import app

def test_fastapi_backend():
    print("==================================================")
    print("Testing FastAPI Backend API Endpoints & Verification")
    print("==================================================")

    client = TestClient(app)

    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    health_data = res_health.json()
    print(f"1. Health Check Response: {health_data}")
    assert health_data['status'] == 'healthy'
    assert health_data['model_loaded'] is True

    # 2. Sample analysis test (LEVIR test_100_10.png)
    print("\n2. Testing /api/analyze-sample with 'test_100_10.png'...")
    t0 = time.time()
    res_sample = client.post("/api/analyze-sample", json={"sample_name": "test_100_10.png"})
    t1 = time.time()
    assert res_sample.status_code == 200, f"Sample analysis failed: {res_sample.text}"
    data = res_sample.json()

    print(f"Inference & Analysis completed in {t1 - t0:.2f} seconds.")
    print("\n--- Field Verification ---")
    print(f"Changed Pixels:         {data['changed_pixel_count']}")
    print(f"Total Pixels:           {data['total_pixel_count']}")
    print(f"Change Percentage:      {data['change_percentage']:.4f}%")
    print(f"Connected Regions:      {data['connected_region_count']}")
    print(f"Largest Region Area:    {data['largest_region_area']:.2f}")
    print(f"Average Region Area:    {data['average_region_area']:.2f}")
    print(f"Grid Density Max:       {data['grid_density_statistics']['max']:.4f}%")
    print(f"CII Score:              {data['cii_score']:.4f}")
    print(f"Impact Category:        {data['impact_category']}")
    print(f"Primary Driver:         {data['primary_driver']}")
    print(f"Factor Contributions:   {data['factor_contributions']}")

    # Verification of exact LEVIR test metrics
    assert data['changed_pixel_count'] == 1933, f"Expected 1933, got {data['changed_pixel_count']}"
    assert abs(data['change_percentage'] - 2.9495) < 0.05, f"Expected ~2.9495%, got {data['change_percentage']}"
    assert abs(data['cii_score'] - 29.8791) < 0.1, f"Expected ~29.8791, got {data['cii_score']}"
    assert data['impact_category'] == 'Low Impact', f"Expected Low Impact, got {data['impact_category']}"

    # Verify base64 images present
    assert data['prediction_mask'].startswith("data:image/png;base64,"), "Prediction mask Base64 missing!"
    assert data['analysis_visualization'].startswith("data:image/png;base64,"), "Analysis visualization Base64 missing!"

    print("\n==================================================")
    print("ALL FASTAPI BACKEND VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == '__main__':
    test_fastapi_backend()
