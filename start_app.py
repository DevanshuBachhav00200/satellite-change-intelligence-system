import os
import sys
import subprocess
import time

def main():
    print("==================================================")
    print("Launching Satellite Change Intelligence System")
    print("==================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = r"C:\Users\Devanshu\anaconda3\envs\changeformer\python.exe"

    print("\n1. Starting FastAPI Backend Server (http://localhost:8000)...")
    backend_proc = subprocess.Popen(
        [python_exe, "backend/main.py"],
        cwd=base_dir
    )

    print("\n2. Starting React Vite Frontend Server (http://localhost:5173)...")
    frontend_proc = subprocess.Popen(
        "npx vite",
        cwd=os.path.join(base_dir, "frontend"),
        shell=True
    )

    print("\n==================================================")
    print("🚀 App is running!")
    print("  Backend API:  http://localhost:8000")
    print("  API Docs:     http://localhost:8000/docs")
    print("  Frontend UI:  http://localhost:5173")
    print("==================================================")
    print("Press Ctrl+C to stop both servers.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Shutdown complete.")

if __name__ == '__main__':
    main()
