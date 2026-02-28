# AI Wellness Vision - PostgreSQL Docker Setup
# This script starts PostgreSQL in Docker for the AI Wellness Vision app

Write-Host "🎯 AI Wellness Vision - Starting PostgreSQL with Docker" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Check if Docker is running
Write-Host "🐳 Checking Docker..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    Write-Host "📋 Steps:" -ForegroundColor Yellow
    Write-Host "1. Open Docker Desktop from Start menu" -ForegroundColor White
    Write-Host "2. Wait for Docker to start completely" -ForegroundColor White
    Write-Host "3. Run this script again" -ForegroundColor White
    exit 1
}

# Stop existing container if running
Write-Host "🛑 Stopping existing PostgreSQL container..." -ForegroundColor Yellow
docker stop ai-wellness-postgres 2>$null
docker rm ai-wellness-postgres 2>$null

# Start PostgreSQL container
Write-Host "🚀 Starting PostgreSQL container..." -ForegroundColor Yellow
docker run -d `
    --name ai-wellness-postgres `
    -e POSTGRES_DB=ai_wellness_vision `
    -e POSTGRES_USER=wellness_user `
    -e POSTGRES_PASSWORD=wellness_pass123 `
    -p 5432:5432 `
    postgres:15

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostgreSQL container started successfully!" -ForegroundColor Green
    Write-Host "" -ForegroundColor White
    Write-Host "📊 Database Details:" -ForegroundColor Cyan
    Write-Host "Host: localhost" -ForegroundColor White
    Write-Host "Port: 5432" -ForegroundColor White
    Write-Host "Database: ai_wellness_vision" -ForegroundColor White
    Write-Host "Username: wellness_user" -ForegroundColor White
    Write-Host "Password: wellness_pass123" -ForegroundColor White
    Write-Host "" -ForegroundColor White
    
    # Wait for PostgreSQL to be ready
    Write-Host "⏳ Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Test connection
    Write-Host "🔍 Testing PostgreSQL connection..." -ForegroundColor Yellow
    $env:PGPASSWORD = "wellness_pass123"
    docker exec ai-wellness-postgres psql -h localhost -U wellness_user -d ai_wellness_vision -c "SELECT version();" 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL is ready and accepting connections!" -ForegroundColor Green
        Write-Host "" -ForegroundColor White
        Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
        Write-Host "1. Run: python working_postgres_server.py" -ForegroundColor White
        Write-Host "2. In another terminal, run: cd flutter_app && flutter run" -ForegroundColor White
    } else {
        Write-Host "⚠️ PostgreSQL started but connection test failed. It might need more time." -ForegroundColor Yellow
        Write-Host "Wait 30 seconds and try running the backend server." -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Failed to start PostgreSQL container" -ForegroundColor Red
    Write-Host "Please check Docker Desktop is running and try again." -ForegroundColor Yellow
}

Write-Host "" -ForegroundColor White
Write-Host "📋 Useful Commands:" -ForegroundColor Cyan
Write-Host "Stop PostgreSQL: docker stop ai-wellness-postgres" -ForegroundColor White
Write-Host "View logs: docker logs ai-wellness-postgres" -ForegroundColor White
Write-Host "Check status: docker ps" -ForegroundColor White