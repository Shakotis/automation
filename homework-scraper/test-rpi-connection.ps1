# Quick test of RPI connection and environment
$SSH_KEY = "C:\Users\Dovydukas\.ssh\rpi_3"
$SSH_CMD = "C:\Windows\System32\OpenSSH\ssh.exe"

Write-Host "Testing RPI Connection..." -ForegroundColor Cyan

& $SSH_CMD -i $SSH_KEY dovydukas@172.20.10.7 @"
echo "=== System Info ===" && \
uname -a && \
echo -e "\n=== Python Version ===" && \
python3 --version && \
echo -e "\n=== Disk Space ===" && \
df -h / && \
echo -e "\n=== Memory ===" && \
free -h && \
echo -e "\n=== Network ===" && \
ip addr show | grep "inet " && \
echo -e "\n=== Services ===" && \
sudo systemctl is-active redis-server 2>/dev/null || echo "Redis not installed" && \
sudo systemctl is-active nginx 2>/dev/null || echo "Nginx not installed"
"@
