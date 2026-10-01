# 🚀 Satellite Change Intelligence System — Production Deployment Guide

This document outlines the deployment configuration, environment setup, containerization, and build procedures for the **Satellite Change Intelligence System** (ChangeFormerV6 + Change Impact Index).

---

## 📋 Table of Contents
1. [Deployment Prerequisites](#1-deployment-prerequisites)
2. [Environment Variables](#2-environment-variables)
3. [Model Checkpoint Handling](#3-model-checkpoint-handling)
4. [Local Backend Setup](#4-local-backend-setup)
5. [Local Frontend Setup](#5-local-frontend-setup)
6. [Docker Build & Deployment](#6-docker-build--deployment)
7. [Frontend Production Build & Vercel](#7-frontend-production-build--vercel)
8. [Backend & Frontend Communication & CORS](#8-backend--frontend-communication--cors)
9. [Files Excluded from Git](#9-files-excluded-from-git)

---

## 1. Deployment Prerequisites

- **Backend**: Python 3.9+ or Docker engine.
- **Frontend**: Node.js 18+ and `npm`.
- **Model Weights**: `best_ckpt.pt` (**469.85 MB**) placed under `checkpoints/ChangeFormer_LEVIR/` or hosted at an accessible HTTP URL.

---

## 2. Environment Variables

### Backend Configuration (`.env`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | Port for FastAPI server binding. |
| `MODEL_CHECKPOINT_PATH` | `checkpoints/ChangeFormer_LEVIR/best_ckpt.pt` | Path to PyTorch model checkpoint. |
| `MODEL_DOWNLOAD_URL` | *(empty)* | Optional HTTP URL for automated streaming download of checkpoint if missing on startup. |
| `ALLOWED_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Comma-separated list of origins allowed by CORS middleware. |

### Frontend Configuration (`frontend/.env.production`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `VITE_API_URL` | `/api` | Base URL endpoint for backend REST API calls. |

---

## 3. Model Checkpoint Handling

The trained ChangeFormer model weight file `best_ckpt.pt` is **469.85 MB**, which exceeds standard Git file size limits.

- **Option A (Local / Volume Mount)**: Place `best_ckpt.pt` directly in `./checkpoints/ChangeFormer_LEVIR/best_ckpt.pt`.
- **Option B (Automated Download)**: Set `MODEL_DOWNLOAD_URL="https://your-storage.com/best_ckpt.pt"`. On server startup, if the file is missing, the backend will automatically perform a streaming download to disk.
- **Diagnostics**: If the checkpoint is missing and no URL is defined, `/api/health` returns `status: "unhealthy"` with diagnostic details without crashing the HTTP server.

---

## 4. Local Backend Setup

1. Create and activate a Python environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. Install production dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run FastAPI backend server:
   ```bash
   python backend/main.py
   ```
   *Backend starts at `http://localhost:8000` (API Docs: `http://localhost:8000/docs`).*

---

## 5. Local Frontend Setup

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   npm install
   ```
2. Start Vite development server:
   ```bash
   npm run dev
   ```
   *Frontend starts at `http://localhost:5173`.*

---

## 6. Docker Build & Deployment

### Building Backend Docker Image
```bash
docker build -t satellite-change-intelligence-backend .
```

### Running Backend Docker Container
Mount your local checkpoint directory:
```bash
docker run -d \
  -p 8000:8000 \
  -e PORT=8000 \
  -e ALLOWED_ORIGINS="http://localhost:5173" \
  -v $(pwd)/checkpoints:/app/checkpoints \
  --name sci-backend \
  satellite-change-intelligence-backend
```

### Running with Docker Compose
```bash
docker-compose up -d
```

---

## 7. Frontend Production Build & Vercel

### Building Production Bundle
```bash
cd frontend
npm run build
```
*(Outputs optimized static bundle to `frontend/dist/`)*

### Vercel Deployment
1. Import `frontend/` repository into Vercel.
2. Set Environment Variable in Vercel settings:
   - `VITE_API_URL` = `https://your-backend-api-domain.com/api`
3. Deploy! Single Page Application routes are handled via `frontend/vercel.json`.

---

## 8. Backend & Frontend Communication & CORS

- In local development, `frontend/vite.config.js` proxies `/api` requests to `http://localhost:8000`.
- In production, CORS is controlled by the backend's `ALLOWED_ORIGINS` environment variable. Ensure `ALLOWED_ORIGINS` includes your production frontend domain (e.g. `https://your-app.vercel.app`).

---

## 9. Files Excluded from Git

The following large files and temporary build artifacts are explicitly excluded in `.gitignore`:
- `LEVIR-CD256/` (benchmark dataset, ~250 MB)
- `checkpoints/ChangeFormer_LEVIR/best_ckpt.pt` (469.85 MB binary checkpoint)
- `.venv/` (Python virtual environment)
- `frontend/node_modules/` & `frontend/dist/`
