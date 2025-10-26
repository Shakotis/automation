# Configure Supabase on RPI Backend

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Configure Supabase for RPI Backend" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Please enter your Supabase credentials:" -ForegroundColor Yellow
Write-Host "(Find these at: https://supabase.com/dashboard → Your Project → Settings → API)`n" -ForegroundColor Gray

$supabaseUrl = Read-Host "Supabase URL (e.g., https://xxxxx.supabase.co)"
$supabaseKey = Read-Host "Supabase Anon Key"

if ([string]::IsNullOrWhiteSpace($supabaseUrl) -or [string]::IsNullOrWhiteSpace($supabaseKey)) {
    Write-Host "`n❌ Error: Both URL and Key are required!" -ForegroundColor Red
    exit 1
}

Write-Host "`n📡 Connecting to RPI and updating configuration..." -ForegroundColor Yellow

$SSH_KEY = "C:\Users\Dovydukas\.ssh\rpi_3"
$SSH_CMD = "C:\Windows\System32\OpenSSH\ssh.exe"

# Update .env file on RPI
& $SSH_CMD -i $SSH_KEY dovydukas@172.20.10.7 @"
cd homework-scraper-backend && \
sed -i 's|^SUPABASE_URL=.*|SUPABASE_URL=$supabaseUrl|' .env && \
sed -i 's|^SUPABASE_KEY=.*|SUPABASE_KEY=$supabaseKey|' .env && \
echo '✓ Configuration updated'
"@

Write-Host "`n🔄 Restarting backend service..." -ForegroundColor Yellow
& $SSH_CMD -i $SSH_KEY dovydukas@172.20.10.7 "sudo systemctl restart homework-scraper"

Start-Sleep -Seconds 3

Write-Host "`n🧪 Testing configuration..." -ForegroundColor Yellow
& $SSH_CMD -i $SSH_KEY dovydukas@172.20.10.7 "curl -s http://localhost:8000/api/test/"

Write-Host "`n`n========================================" -ForegroundColor Green
Write-Host "✅ Supabase Configuration Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Your backend is now fully configured and ready to use!" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Set up port forwarding on your router" -ForegroundColor White
Write-Host "2. Configure DNS for api.dovydas.space" -ForegroundColor White
Write-Host "3. Install SSL certificate with certbot" -ForegroundColor White
Write-Host "4. Test integration with frontend at nd.dovydas.space`n" -ForegroundColor White
