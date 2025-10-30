# Redeploy Frontend to Netlify
# This script will rebuild and redeploy the frontend with the correct API endpoints

Write-Host "🚀 Redeploying Frontend to Netlify" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📍 Root Cause Analysis:" -ForegroundColor Yellow
Write-Host "  - Backend API is CORRECT: /api/tasks/sync ✅" -ForegroundColor Green
Write-Host "  - Local frontend code is CORRECT: uses /api/tasks/sync ✅" -ForegroundColor Green
Write-Host "  - Deployed frontend on Netlify is OUTDATED ❌" -ForegroundColor Red
Write-Host "  - Current error logs show: POST /api/scraper/homework/sync-google-tasks/" -ForegroundColor Red
Write-Host ""

Write-Host "🔧 Solution: Rebuild and redeploy frontend" -ForegroundColor Yellow
Write-Host ""

Set-Location -Path "c:\Users\Dovydukas\Documents\GitHub\automation\homework-scraper\frontend"

Write-Host "1️⃣  Installing dependencies..." -ForegroundColor Cyan
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ npm install failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2️⃣  Building frontend..." -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Build successful!" -ForegroundColor Green
Write-Host ""
Write-Host "📤 Next Steps to Deploy to Netlify:" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: Netlify CLI (Recommended)" -ForegroundColor Cyan
Write-Host "  Run: netlify deploy --prod" -ForegroundColor White
Write-Host "  (If you don't have Netlify CLI: npm install -g netlify-cli)" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2: Git Push (Automatic)" -ForegroundColor Cyan
Write-Host "  cd .." -ForegroundColor White
Write-Host "  git add ." -ForegroundColor White
Write-Host "  git commit -m 'fix: Update API endpoints to /api/tasks/sync'" -ForegroundColor White
Write-Host "  git push" -ForegroundColor White
Write-Host "  (Netlify will auto-deploy if connected to GitHub)" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 3: Netlify Dashboard (Manual)" -ForegroundColor Cyan
Write-Host "  1. Go to https://app.netlify.com" -ForegroundColor White
Write-Host "  2. Find your homework-scraper site" -ForegroundColor White
Write-Host "  3. Click 'Trigger deploy' → 'Deploy site'" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Verify After Deploy:" -ForegroundColor Yellow
Write-Host "  1. Open DevTools Network tab" -ForegroundColor White
Write-Host "  2. Click 'Sync to Google Tasks' button" -ForegroundColor White
Write-Host "  3. Verify it calls: POST /api/tasks/sync (not /api/scraper/homework/sync-google-tasks/)" -ForegroundColor White
Write-Host ""
