# AI NinjaCoach Backend Deployment on Render

This guide explains how to deploy the AI NinjaCoach backend on Render.

## Prerequisites

1. A [Render](https://render.com) account
2. The AI NinjaCoach repository on GitHub

## Deployment Steps

### Option 1: Deploy via Render Dashboard (Recommended)

1. **Sign up or log in to Render**:
   - Go to [https://render.com](https://render.com)
   - Sign up or log in with your GitHub account

2. **Create a new Web Service**:
   - Click on "New +" in the top right corner
   - Select "Web Service"

3. **Connect your repository**:
   - Connect your GitHub account if not already connected
   - Select the AI NinjaCoach repository

4. **Configure the service**:
   - Name: `ain-backend-api` (or your preferred name)
   - Environment: `Python`
   - Region: Choose the region closest to your users
   - Branch: `main` (or your deployment branch)
   - Root Directory: Leave empty
   - Build Command: `pip install -r render-requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Set environment variables**:
   - Click on "Advanced" to expand additional settings
   - Add the following environment variables:
     - `PYTHON_VERSION`: `3.10.0`
     - Add any API keys required for your agents (e.g., `GOOGLE_API_KEY` if using Google Generative AI)

6. **Create Web Service**:
   - Click "Create Web Service"
   - Render will start deploying your application

7. **Verify deployment**:
   - Once deployment is complete, click on the URL provided by Render
   - Append `/docs` to the URL to access the FastAPI documentation
   - Verify the health check endpoint at `/health`

### Option 2: Deploy via render.yaml

1. **Push the repository to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push
   ```

2. **Deploy using the Blueprint**:
   - Go to [https://render.com/deploy](https://render.com/deploy)
   - Enter your repository URL
   - Click "Deploy"

3. **Verify deployment**:
   - Once deployment is complete, click on the URL provided by Render
   - Append `/docs` to the URL to access the FastAPI documentation
   - Verify the health check endpoint at `/health`

## Connecting Frontend to Backend

After deploying the backend on Render, you'll need to update the frontend's `BACKEND_URL` environment variable in Streamlit Cloud:

1. Go to your Streamlit Cloud dashboard
2. Select your app
3. Go to "Settings" > "Secrets"
4. Add a new secret:
   - Key: `BACKEND_URL`
   - Value: Your Render backend URL (e.g., `https://ain-backend-api.onrender.com`)

## Troubleshooting

If you encounter any issues during deployment:

1. **Check the logs** in the Render dashboard
2. Verify that all required environment variables are set
3. Make sure the health check endpoint is responding correctly
4. Check if there are any dependency issues in the build logs

## Monitoring

Render provides built-in monitoring for your deployed services:

1. Go to your Web Service in the Render dashboard
2. Click on "Logs" to view application logs
3. Click on "Metrics" to view performance metrics

For more information, refer to the [Render documentation](https://render.com/docs).
