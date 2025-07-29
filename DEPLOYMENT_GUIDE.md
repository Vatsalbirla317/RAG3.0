# CodeMatrix Deployment Guide
## Deploy to Vercel (Frontend) + Render (Backend) - Free Tier

This guide will walk you through deploying your CodeMatrix application using **Vercel** for the React frontend and **Render** for the Python/FastAPI backend. Both platforms offer generous free tiers that don't require credit card information.

---

## 1. Introduction & Strategy

**Why this approach?**
- **Vercel**: Perfect for React/Vite applications with automatic deployments, global CDN, and excellent performance
- **Render**: Great for Python/FastAPI backends with automatic scaling and easy environment variable management
- **Communication**: Frontend will make API calls to the backend using CORS configuration
- **Cost**: Both platforms offer free tiers sufficient for student projects

**Architecture:**
```
User → Vercel (Frontend) → Render (Backend) → AI APIs
```

---

## 2. Step 1: Prepare the Backend for Production

### Why Gunicorn?
FastAPI's built-in server is great for development but not suitable for production. Gunicorn with Uvicorn workers provides better performance and stability.

### 2.1 Add Gunicorn to Requirements

Add this line to `codematrix_backend/requirements.txt`:
```txt
gunicorn
```

### 2.2 Create Build Script for Render

Create a file called `build.sh` in the `codematrix_backend/` directory:

```bash
#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
```

**Important:** After creating this file, make it executable:
```bash
chmod +x codematrix_backend/build.sh
```

---

## 3. Step 2: Prepare the Frontend for Production

### 3.1 Update API Base URL

You need to update the API base URL in your frontend to point to your future Render backend.

Edit `codematrix_frontend/src/services/api.ts` and update the `API_BASE_URL`:

```typescript
// Replace this line:
const API_BASE_URL = 'http://localhost:8000';

// With this (we'll update this URL later with your actual Render URL):
const API_BASE_URL = 'https://your-backend-name.onrender.com';
```

**Note:** We'll update this URL again in Step 5 with your actual Render URL.

---

## 4. Step 3: Deploy the Frontend to Vercel

### 4.1 Sign Up for Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up" and choose "Continue with GitHub"
3. Authorize Vercel to access your GitHub account

### 4.2 Create New Project
1. Click "New Project" in your Vercel dashboard
2. Import your GitHub repository: `Vatsalbirla317/RAG3.0`
3. **Important Configuration:**
   - **Framework Preset**: Vite
   - **Root Directory**: `codematrix_frontend`
   - **Build Command**: `npm run build` (should auto-detect)
   - **Output Directory**: `dist` (should auto-detect)
4. Click "Deploy"

### 4.3 Get Your Vercel URL
Once deployment is complete, copy your Vercel URL (e.g., `https://rag3-0.vercel.app`)

---

## 5. Step 4: Deploy the Backend to Render

### 5.1 Sign Up for Render
1. Go to [render.com](https://render.com)
2. Click "Get Started" and choose "Continue with GitHub"
3. Authorize Render to access your GitHub account

### 5.2 Create New Web Service
1. Click "New +" and select "Web Service"
2. Connect your GitHub repository: `Vatsalbirla317/RAG3.0`

### 5.3 Configure the Service
Fill in these settings:

- **Name**: `codematrix-backend` (or any name you prefer)
- **Root Directory**: `codematrix_backend`
- **Environment**: `Python 3`
- **Build Command**: `bash build.sh`
- **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
- **Plan**: `Free`

### 5.4 Deploy
Click "Create Web Service" and wait for deployment to complete.

### 5.5 Get Your Render URL
Once deployment is complete, copy your Render URL (e.g., `https://codematrix-backend.onrender.com`)

---

## 6. Step 5: The Final Handshake (Connecting Everything)

This step connects your frontend and backend so they can communicate properly.

### 6.1 Update Frontend API URL

1. Go back to `codematrix_frontend/src/services/api.ts`
2. Replace the placeholder URL with your actual Render URL:

```typescript
const API_BASE_URL = 'https://your-actual-render-url.onrender.com';
```

3. Commit and push the changes:
```bash
git add .
git commit -m "Update API base URL for production"
git push origin main
```

### 6.2 Update Backend CORS

1. Edit `codematrix_backend/main.py`
2. Find the CORS configuration and add your Vercel URL:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Keep for local development
        "https://your-actual-vercel-url.vercel.app"  # Add your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. Commit and push the changes:
```bash
git add .
git commit -m "Update CORS for production frontend"
git push origin main
```

### 6.3 Add Environment Variables to Render

1. Go to your Render dashboard
2. Click on your backend service
3. Go to the "Environment" tab
4. Add these environment variables:
   - **Key**: `GOOGLE_API_KEY`, **Value**: `your_google_api_key`
   - **Key**: `GROQ_API_KEY`, **Value**: `your_groq_api_key`
5. Click "Save Changes"

**Note:** Render will automatically redeploy your service when you add environment variables.

---

## 7. Conclusion

🎉 **Congratulations! Your CodeMatrix application is now deployed!**

### What You've Achieved:
- ✅ **Frontend**: Deployed on Vercel with global CDN
- ✅ **Backend**: Deployed on Render with automatic scaling
- ✅ **Communication**: Frontend and backend properly connected
- ✅ **Environment Variables**: Securely configured
- ✅ **Zero Cost**: Using free tiers only

### Your Live Application:
- **Frontend URL**: `https://your-vercel-url.vercel.app`
- **Backend URL**: `https://your-render-url.onrender.com`

### Next Steps:
1. **Test your application** by visiting the frontend URL
2. **Monitor deployments** in both Vercel and Render dashboards
3. **Set up custom domain** (optional, requires domain purchase)
4. **Configure automatic deployments** (already enabled by default)

### Troubleshooting:
- If you see CORS errors, double-check the URLs in your CORS configuration
- If API calls fail, verify your environment variables are set correctly
- Check the deployment logs in both Vercel and Render dashboards

Your CodeMatrix application is now live and ready to use! 🚀
