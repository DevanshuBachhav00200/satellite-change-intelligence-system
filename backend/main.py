import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure parent directory is in Python path for package imports
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.api.router import router as api_router, get_pipeline

app = FastAPI(
    title="Satellite Change Intelligence API",
    description="Backend API for ChangeFormer-V6 Satellite Change Detection & Explainable Change Impact Index (CII) Assessment",
    version="1.0.0"
)

# Parse CORS allowed origins from environment variable
raw_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,*")
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    print("==================================================")
    print("Starting Satellite Change Intelligence Backend API")
    print("==================================================")
    try:
        pipeline = get_pipeline()
        print(f"[OK] ChangeFormer Pipeline initialized on device: {pipeline.device}")
    except Exception as e:
        print(f"[WARN] Pipeline initialization deferred or warning: {str(e)}")


@app.get("/")
async def root():
    return {
        "title": "Satellite Change Intelligence System API",
        "status": "online",
        "docs": "/docs"
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)
