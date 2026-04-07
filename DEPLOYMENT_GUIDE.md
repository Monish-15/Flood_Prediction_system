# 🚀 Flood Prediction OS — Unified Vercel Guide

I've upgraded your system to a **React + Vite** frontend with a **FastAPI** backend, fully optimized for a single Vercel deployment.

## 1. Local Development
To run the full system locally, you need two terminals:

### Terminal 1: Backend (FastAPI)
```bash
# In the root D:\Flood_Prediction_system
uvicorn backend.main:app --reload --port 8000
```

### Terminal 2: Frontend (React)
```bash
cd frontend-react
npm run dev
# Dashboard runs at http://localhost:5173
```

---

## 2. GitHub Sync Issues
If your `git push` is failing, it's likely because the remote repository has diverged. To reflect ALL local changes (caution: this overwrites the remote), run:
```bash
git push origin main -f
```
Or to sync correctly:
```bash
git pull origin main --rebase
git push origin main
```

---

## 3. Vercel Deployment (One-Click)
Since everything is integrated through `vercel.json`:
1. Connect your repo to **Vercel**.
2. **Framework Preset**: Vite.
3. **Build Command**: `npm run build` (Vercel will build the frontend-react).
4. **Output Directory**: `dist`.

Your API (Python) and UI (React) will work together seamlessly under a single URL!
