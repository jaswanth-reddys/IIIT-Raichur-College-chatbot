# Project Upgrade Process: Local to Live Host

This document outlines the steps to deploy the project to a live hosting service.

## 1. Prerequisites
- A GitHub repository containing the current project.
- Accounts on [Render](https://render.com/) (for Backend) and [Vercel](https://vercel.com/) (for Frontend).

## 2. Backend Deployment (FastAPI)

We will use **Render** for the backend.

### Steps:
1. **Prepare for Render**: Ensure `requirements.txt` is updated in the `backend/` folder.
2. **Create Web Service**:
   - Connect your GitHub repository.
   - Select the `backend/` directory as the root.
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Environment Variables**:
   - Add `GOOGLE_API_KEY` with your AIzaSy... key.
   - Set `PYTHON_VERSION` to `3.9` or higher.
4. **Deploy**: Render will automatically build and deploy the service.
5. **Copy URL**: Note the backend URL (e.g., `https://your-backend.onrender.com`).

## 3. Frontend Deployment (Next.js)

We will use **Vercel** for the frontend.

### Steps:
1. **Import Project**:
   - Connect your GitHub repository.
   - Select the `frontend/` directory as the root.
   - Vercel will automatically detect the **Next.js** framework.
2. **Environment Variables**:
   - Add `NEXT_PUBLIC_API_URL` and set its value to your **Backend URL** from the previous step.
3. **Deploy**: Vercel will trigger a build.
4. **Visit Site**: Your frontend will be live at a `.vercel.app` domain.

## 4. Final Verification
1. Ensure the frontend successfully makes requests to the backend.
2. Verify that the Google Generative AI features work in the live environment.
3. Check for CORS issues; ensure the backend's `main.py` allows your Vercel domain if CORS is enabled.
