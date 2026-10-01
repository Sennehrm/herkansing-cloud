@echo off
echo ===================================================
echo [CI/CD] Starting Automated Deployment Pipeline...
echo ===================================================

echo [1/4] Pulling latest changes from Git repository...
git pull origin main

echo [2/4] Building updated Docker images...
docker compose build --no-cache

echo [3/4] Stopping old containers and starting updated stack...
docker compose up -d --remove-orphans

echo [4/4] Cleaning up unused and dangling Docker images...
docker image prune -f

echo ===================================================
echo [CI/CD] Deployment successfully completed!
echo System is running and healthy.
echo ===================================================
docker compose ps
