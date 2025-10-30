# ========================================
# Deploy Backend 404 Fix to Server
# ========================================
# This script uploads the missing backend files and restarts services

param(
    [string]$ServerIP = "192.168.0.88",
    [string]$Username = "dovydukas",
    [string]$SSHKey = "$env:USERPROFILE\.ssh\rpi_3",
    [string]$LocalBackendPath = ".\backend",
    [string]$RemoteBackendPath = "/home/dovydukas/homework-scraper/backend"
)

Write-Host @"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     Deploy Backend 404 Fix                              ║
║     Uploads missing tasks URLs and views                ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host ""

# Check if WinSCP or pscp is available
$scpTool = $null
if (Get-Command "pscp" -ErrorAction SilentlyContinue) {
    $scpTool = "pscp"
    Write-Host "✓ Found PuTTY SCP (pscp)" -ForegroundColor Green
} elseif (Get-Command "scp" -ErrorAction SilentlyContinue) {
    $scpTool = "scp"
    Write-Host "✓ Found OpenSSH SCP" -ForegroundColor Green
} else {
    Write-Host "✗ No SCP tool found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install one of:" -ForegroundColor Yellow
    Write-Host "  • PuTTY (includes pscp): https://www.putty.org/" -ForegroundColor White
    Write-Host "  • OpenSSH Client (Windows 10+): Settings → Apps → Optional Features → OpenSSH Client" -ForegroundColor White
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "MANUAL UPLOAD INSTRUCTIONS" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Open WinSCP or FileZilla" -ForegroundColor Yellow
    Write-Host "2. Connect to: $ServerIP" -ForegroundColor White
    Write-Host "3. Navigate to: $RemoteBackendPath/tasks/" -ForegroundColor White
    Write-Host "4. Upload these files from $LocalBackendPath\tasks\:" -ForegroundColor White
    Write-Host "   • urls.py" -ForegroundColor Green
    Write-Host "   • views.py" -ForegroundColor Green
    Write-Host ""
    Write-Host "5. SSH into server and run:" -ForegroundColor Yellow
    Write-Host @"
   cd $RemoteBackendPath
   sudo systemctl restart homework-scraper.service
   sudo systemctl status homework-scraper.service
"@ -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "FILES TO UPLOAD" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$filesToUpload = @(
    @{Local="$LocalBackendPath\tasks\urls.py"; Remote="$RemoteBackendPath/tasks/urls.py"}
    @{Local="$LocalBackendPath\tasks\views.py"; Remote="$RemoteBackendPath/tasks/views.py"}
)

foreach ($file in $filesToUpload) {
    if (Test-Path $file.Local) {
        Write-Host "✓ Found: $($file.Local)" -ForegroundColor Green
    } else {
        Write-Host "✗ Missing: $($file.Local)" -ForegroundColor Red
    }
}

Write-Host ""
$confirm = Read-Host "Do you want to proceed with upload? (y/n)"

if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Cancelled by user." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "UPLOADING FILES" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Upload files
foreach ($file in $filesToUpload) {
    if (-not (Test-Path $file.Local)) {
        Write-Host "⚠ Skipping $($file.Local) - file not found" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "Uploading: $($file.Local) → $($file.Remote)" -ForegroundColor Cyan
    
    try {
        if ($scpTool -eq "pscp") {
            # PuTTY SCP
            & pscp -i $SSHKey $file.Local "${Username}@${ServerIP}:$($file.Remote)"
        } else {
            # OpenSSH SCP
            & scp -i $SSHKey $file.Local "${Username}@${ServerIP}:$($file.Remote)"
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Uploaded successfully" -ForegroundColor Green
        } else {
            Write-Host "✗ Upload failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Error: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "RESTARTING SERVICES" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Write-Host "NOTE: You need to SSH into the server and run these commands:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Verify files uploaded:" -ForegroundColor Cyan
Write-Host @"
   ls -la $RemoteBackendPath/tasks/urls.py
   ls -la $RemoteBackendPath/tasks/views.py
"@ -ForegroundColor White

Write-Host ""
Write-Host "2. Restart Django service:" -ForegroundColor Cyan
Write-Host @"
   sudo systemctl restart homework-scraper.service
   sudo systemctl status homework-scraper.service
"@ -ForegroundColor White

Write-Host ""
Write-Host "3. Check logs for errors:" -ForegroundColor Cyan
Write-Host @"
   sudo journalctl -u homework-scraper.service -f
"@ -ForegroundColor White

Write-Host ""
Write-Host "4. Test the endpoint:" -ForegroundColor Cyan
Write-Host @"
   curl -X POST http://localhost:8000/api/tasks/sync \
     -H "Content-Type: application/json" \
     -d '{}'
"@ -ForegroundColor White

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "NEXT STEPS" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. SSH into your server (use PuTTY or other SSH client)" -ForegroundColor Yellow
Write-Host "2. Run the commands above to restart services" -ForegroundColor Yellow
Write-Host "3. Test your frontend application" -ForegroundColor Yellow
Write-Host "4. Check browser console for any remaining errors" -ForegroundColor Yellow
Write-Host ""

Write-Host "If you still see 404 errors:" -ForegroundColor Yellow
Write-Host "  • Check Django logs: sudo journalctl -u homework-scraper.service -f" -ForegroundColor White
Write-Host "  • Verify URL patterns: Check homework_scraper/urls.py includes tasks.urls" -ForegroundColor White
Write-Host "  • Clear browser cache and retry" -ForegroundColor White
Write-Host ""

Write-Host "Files created locally:" -ForegroundColor Cyan
Write-Host "  • backend/tasks/urls.py" -ForegroundColor Green
Write-Host "  • backend/tasks/views.py" -ForegroundColor Green
Write-Host ""

Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  • debug-404-error.ps1 - Diagnostic tool" -ForegroundColor Green
Write-Host "  • BACKEND_ROUTING_FIX.md - Detailed guide" -ForegroundColor Green
Write-Host ""
