#!/usr/bin/env python3
"""
Deploy monitoring files to RPI server
"""
import subprocess
import os

SSH_KEY = os.path.expanduser("~/.ssh/rpi_3")
SERVER = "dovydukas@192.168.0.88"
BACKEND_PATH = "/home/dovydukas/homework-scraper-backend"

def run_ssh_command(command):
    """Run command on remote server"""
    full_cmd = [
        "C:\\Windows\\System32\\OpenSSH\\ssh.exe",
        "-i", SSH_KEY,
        SERVER,
        command
    ]
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    print(f"Command: {command}")
    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result.returncode == 0

def copy_file_content(local_path, remote_path):
    """Copy file content to remote server"""
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Escape single quotes in content
    content = content.replace("'", "'\"'\"'")
    
    # Create the file on remote server
    command = f"cat > {remote_path} << 'EOFPYTHON'\n{content}\nEOFPYTHON"
    return run_ssh_command(command)

# Create monitoring directory
print("Creating monitoring directory...")
run_ssh_command(f"mkdir -p {BACKEND_PATH}/monitoring")

# Copy files
print("\nCopying __init__.py...")
copy_file_content("backend/monitoring/__init__.py", f"{BACKEND_PATH}/monitoring/__init__.py")

print("\nCopying urls.py...")
copy_file_content("backend/monitoring/urls.py", f"{BACKEND_PATH}/monitoring/urls.py")

print("\nCopying views.py...")
copy_file_content("backend/monitoring/views.py", f"{BACKEND_PATH}/monitoring/views.py")

# Update settings.py to add monitoring to INSTALLED_APPS
print("\nUpdating INSTALLED_APPS...")
run_ssh_command(f"""
cd {BACKEND_PATH} && 
if ! grep -q "'monitoring'" homework_scraper/settings.py; then
    sed -i "/INSTALLED_APPS = \\[/a\\    'monitoring'," homework_scraper/settings.py
    echo "Added monitoring to INSTALLED_APPS"
else
    echo "monitoring already in INSTALLED_APPS"
fi
""")

# Update urls.py to include monitoring routes
print("\nUpdating URL configuration...")
run_ssh_command(f"""
cd {BACKEND_PATH} &&
if ! grep -q "monitoring.urls" homework_scraper/urls.py; then
    sed -i "/urlpatterns = \\[/a\\    path('api/monitoring/', include('monitoring.urls'))," homework_scraper/urls.py
    echo "Added monitoring to URLs"
else
    echo "monitoring already in URLs"
fi
""")

# Create log directories
print("\nCreating log directories...")
run_ssh_command("sudo mkdir -p /var/log/homework-scraper")
run_ssh_command("sudo chown -R dovydukas:dovydukas /var/log/homework-scraper")

# Restart Django service
print("\nRestarting Django service...")
run_ssh_command("sudo systemctl restart homework-scraper.service")

print("\n✅ Deployment complete!")
print("\nTest the API:")
print("  curl http://localhost:8000/api/monitoring/")
print("\nView in browser:")
print("  https://dovydas.space/logs")
