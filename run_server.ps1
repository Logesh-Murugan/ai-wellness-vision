Write-Host "🚀 Starting AI Wellness Vision Backend Server..." -ForegroundColor Green
Write-Host ""
Write-Host "📡 Server will start on http://localhost:8000" -ForegroundColor Cyan
Write-Host "📖 API docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🔍 Health check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Gray
Write-Host ""

try {
    python main_api_server.py
}
catch {
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")