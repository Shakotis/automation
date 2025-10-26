# Test Public API Access Script
# Run this after setting up port forwarding

$publicIP = "84.15.189.151"
$localIP = "192.168.0.88"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing Backend API Access" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test Local Access
Write-Host "[1/3] Testing Local Network Access..." -ForegroundColor Yellow
try {
    $localResponse = Invoke-WebRequest -Uri "http://$localIP/api/" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Local Access: SUCCESS (Status: $($localResponse.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Local Access: FAILED" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host ""

# Test Public Access
Write-Host "[2/3] Testing Public IP Access..." -ForegroundColor Yellow
try {
    $publicResponse = Invoke-WebRequest -Uri "http://$publicIP/api/" -TimeoutSec 10 -UseBasicParsing
    Write-Host "✅ Public Access: SUCCESS (Status: $($publicResponse.StatusCode))" -ForegroundColor Green
    Write-Host "`nAPI Response:" -ForegroundColor Cyan
    $publicResponse.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10 | Write-Host -ForegroundColor White
} catch {
    Write-Host "❌ Public Access: FAILED" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
    Write-Host "`n⚠️  This means port forwarding is not configured yet!" -ForegroundColor Yellow
    Write-Host "   Go to your router settings and forward:" -ForegroundColor White
    Write-Host "   External Port 80 → Internal $localIP:80`n" -ForegroundColor Gray
}

Write-Host ""

# Test API endpoint
Write-Host "[3/3] Testing API Endpoints (Local)..." -ForegroundColor Yellow
$endpoints = @(
    "/api/",
    "/api/test/",
    "/api/health"
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri "http://$localIP$endpoint" -TimeoutSec 5 -UseBasicParsing
        Write-Host "  ✅ $endpoint - OK" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $endpoint - Failed" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test Complete" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "📝 Summary:" -ForegroundColor Yellow
Write-Host "  Local IP:  http://$localIP/api/" -ForegroundColor White
Write-Host "  Public IP: http://$publicIP/api/" -ForegroundColor White
Write-Host "`nIf public access failed, configure port forwarding on your router." -ForegroundColor Gray
