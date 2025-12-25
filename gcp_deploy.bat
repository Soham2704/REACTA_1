@echo off
echo ========================================================
echo   Google Cloud Run Deployment Helper (Remote Build)
echo ========================================================
echo.
echo NOTE: This script assumes you have:
echo 1. Installed Google Cloud SDK (gcloud CLI)
echo 2. Authenticated (gcloud auth login)
echo 3. Selected your project (gcloud config set project [YOUR_PROJECT_ID])
echo 4. Enabled Cloud Run, Cloud Build, and Artifact Registry APIs
echo.

echo Available GCP Projects:
gcloud projects list
echo.
set /p PROJECT_ID=Enter your GCP Project ID: 
set APP_NAME=veritas-compliance-system
set REGION=us-central1

echo.
echo 1. Submitting Build to Google Cloud Build...
echo (This uploads your code and builds the container on Google's servers)
echo (This may take a few minutes)
gcloud builds submit --tag gcr.io/%PROJECT_ID%/%APP_NAME% --project %PROJECT_ID% .

echo.
echo 2. Deploying to Cloud Run...
gcloud run deploy %APP_NAME% ^
    --image gcr.io/%PROJECT_ID%/%APP_NAME% ^
    --project %PROJECT_ID% ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --port 8080 ^
    --memory 4Gi ^
    --cpu 2 ^
    --timeout 300

echo.
echo Deployment Complete! Check the URL above.
pause
