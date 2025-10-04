@echo off
echo Setting up MongoDB for modLRN...
echo.

echo Checking if Docker is available...
docker --version >nul 2>&1
if %errorlevel% == 0 (
    echo Docker is available. Starting MongoDB with Docker...
    docker run -d -p 27017:27017 --name mongodb mongo:latest
    if %errorlevel% == 0 (
        echo MongoDB started successfully with Docker!
        echo You can now run the backend server.
        pause
        exit /b 0
    ) else (
        echo Failed to start MongoDB with Docker.
    )
) else (
    echo Docker is not available.
)

echo.
echo Please install MongoDB manually:
echo 1. Download from: https://www.mongodb.com/try/download/community
echo 2. Install with default settings
echo 3. Start the service: net start MongoDB
echo.
echo Or use MongoDB Atlas (cloud):
echo 1. Go to: https://www.mongodb.com/atlas
echo 2. Create free account and cluster
echo 3. Get connection string
echo 4. Set MONGO_URI environment variable
echo.
pause
