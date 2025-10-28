# Deploy Monitoring Feature to RPI Server
# Run this from your Windows machine

$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying Server Monitoring Feature to RPI..." -ForegroundColor Cyan
Write-Host ""

# Configuration
$SSH_KEY = "$env:USERPROFILE\.ssh\rpi_3"
$SSH_USER = "dovydukas"
$SSH_HOST = "192.168.0.88"
$REMOTE_PATH = "/home/dovydukas/homework-scraper"

# Check if SSH key exists
if (-not (Test-Path $SSH_KEY)) {
    Write-Host "❌ SSH key not found: $SSH_KEY" -ForegroundColor Red
    exit 1
}

Write-Host "✓ SSH key found" -ForegroundColor Green

# Test SSH connection
Write-Host ""
Write-Host "🔐 Testing SSH connection..." -ForegroundColor Yellow
try {
    $testConnection = ssh -i $SSH_KEY -o ConnectTimeout=5 "${SSH_USER}@${SSH_HOST}" "echo 'Connection successful'"
    if ($testConnection -eq "Connection successful") {
        Write-Host "✓ SSH connection successful" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ SSH connection failed" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# Upload deployment script
Write-Host ""
Write-Host "📤 Uploading deployment script..." -ForegroundColor Yellow
try {
    scp -i $SSH_KEY ".\deploy-monitoring.sh" "${SSH_USER}@${SSH_HOST}:${REMOTE_PATH}/"
    Write-Host "✓ Deployment script uploaded" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to upload deployment script" -ForegroundColor Red
    exit 1
}

# Make script executable and run it
Write-Host ""
Write-Host "🚀 Running deployment on server..." -ForegroundColor Yellow
Write-Host ""

$deployCommand = @"
cd $REMOTE_PATH && 
chmod +x deploy-monitoring.sh && 
./deploy-monitoring.sh
"@

ssh -i $SSH_KEY "${SSH_USER}@${SSH_HOST}" $deployCommand

Write-Host ""
Write-Host "✅ Deployment process complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Push your frontend changes to GitHub" -ForegroundColor White
Write-Host "2. Netlify will automatically deploy the frontend" -ForegroundColor White
Write-Host "3. Visit: https://dovydas.space/logs" -ForegroundColor White
Write-Host "4. Make sure you're logged in with Google" -ForegroundColor White
Write-Host ""
Write-Host "🔍 To check logs on server:" -ForegroundColor Cyan
Write-Host "   ssh -i $SSH_KEY ${SSH_USER}@${SSH_HOST}" -ForegroundColor White
Write-Host "   journalctl -u homework-scraper.service -f" -ForegroundColor White
Write-Host ""

# Ask if user wants to open SSH connection
$openSSH = Read-Host "Do you want to open an SSH connection now? (y/n)"
if ($openSSH -eq 'y' -or $openSSH -eq 'Y') {
    Write-Host ""
    Write-Host "🔌 Opening SSH connection..." -ForegroundColor Cyan
    ssh -i $SSH_KEY "${SSH_USER}@${SSH_HOST}"
}
