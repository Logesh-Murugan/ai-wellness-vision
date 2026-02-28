@echo off
echo AI Wellness Vision - Starting PostgreSQL with Docker
echo ============================================================

echo Checking Docker...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    echo Steps:
    echo 1. Open Docker Desktop from Start menu
    echo 2. Wait for Docker to start completely
    echo 3. Run this script again
    pause
    exit /b 1
)

echo Docker is running!

echo Stopping existing PostgreSQL container...
docker stop ai-wellness-postgres >nul 2>&1
docker rm ai-wellness-postgres >nul 2>&1

echo Starting PostgreSQL container...
docker run -d --name ai-wellness-postgres -e POSTGRES_DB=ai_wellness_vision -e POSTGRES_USER=wellness_user -e POSTGRES_PASSWORD=wellness_pass123 -p 5432:5432 postgres:15

if %errorlevel% equ 0 (
    echo PostgreSQL container started successfully!
    echo.
    echo Database Details:
    echo Host: localhost
    echo Port: 5432
    echo Database: ai_wellness_vision
    echo Username: wellness_user
    echo Password: wellness_pass123
    echo.
    echo Waiting for PostgreSQL to be ready...
    timeout /t 15 /nobreak >nul
    echo.
    echo PostgreSQL is ready!
    echo.
    echo Next Steps:
    echo 1. Run: python setup_database.py
    echo 2. Run: python working_postgres_server.py
    echo 3. In another terminal: cd flutter_app && flutter run
) else (
    echo ERROR: Failed to start PostgreSQL container
    echo Please check Docker Desktop is running and try again.
)

echo.
echo Useful Commands:
echo Stop PostgreSQL: docker stop ai-wellness-postgres
echo View logs: docker logs ai-wellness-postgres
echo Check status: docker ps

pause