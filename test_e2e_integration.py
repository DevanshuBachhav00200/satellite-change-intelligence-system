import os
import sys
import time
import subprocess
import requests

def test_e2e():
    print("==================================================")
    print("Testing End-to-End System Integration")
    print("==================================================")

    python_exe = r"C:\Users\Devanshu\anaconda3\envs\changeformer\python.exe"
    app_dir = os.path.dirname(os.path.abspath(__file__))

    # Launch FastAPI backend process
    print("Starting FastAPI server process on port 8000...")
    proc = subprocess.Popen(
        [python_exe, "backend/main.py"],
        cwd=app_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # Wait up to 15 seconds for backend to start
        started = False
        for i in range(15):
            time.sleep(1)
            try:
                r = requests.get("http://localhost:8000/api/health", timeout=2)
                if r.status_code == 200 and r.json().get("status") == "healthy":
                    started = True
                    print(f"✅ Backend server is online! Response: {r.json()}")
                    break
            except Exception:
                pass

        assert started, "Backend server failed to start within 15 seconds."

        # Test sample analysis endpoint
        print("\nSending POST request to http://localhost:8000/api/analyze-sample...")
        res = requests.post("http://localhost:8000/api/analyze-sample", json={"sample_name": "test_100_10.png"})
        assert res.status_code == 200, f"Analyze sample request failed with code {res.status_code}: {res.text}"

        data = res.json()
        print("\n--- Verified End-to-End Response ---")
        print(f"Changed Pixels:      {data['changed_pixel_count']}")
        print(f"Change Percentage:   {data['change_percentage']:.4f}%")
        print(f"CII Score:           {data['cii_score']:.4f}")
        print(f"Impact Category:     {data['impact_category']}")
        print(f"Prediction Mask PNG: {len(data['prediction_mask'])} chars (Base64)")
        print(f"Visualization PNG:   {len(data['analysis_visualization'])} chars (Base64)")

        # Assert LEVIR test case requirements
        assert data['changed_pixel_count'] == 1933, f"Expected 1933, got {data['changed_pixel_count']}"
        assert abs(data['change_percentage'] - 2.9495) < 0.05
        assert abs(data['cii_score'] - 29.8791) < 0.1
        assert data['impact_category'] == 'Low Impact'

        print("\n==================================================")
        print("END-TO-END INTEGRATION TEST PASSED PERFECTLY!")
        print("==================================================")

    finally:
        print("Shutting down backend server process...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

if __name__ == '__main__':
    test_e2e()
