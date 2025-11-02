# Gunicorn Configuration for Raspberry Pi (Optimized for Limited RAM)
import multiprocessing
import os

# Server socket
bind = '0.0.0.0:8000'
backlog = 64  # Reduced from default 2048 for lower memory

# Worker processes - Single worker for low RAM environment
workers = 1
worker_class = 'gthread'
threads = 2  # Optimal for Raspberry Pi - balance between performance and memory
worker_connections = 100  # Reduced from default 1000
max_requests = 1000  # Restart worker after this many requests (prevents memory leaks)
max_requests_jitter = 100
timeout = 120  # Reduced from 600 - most requests should complete faster
graceful_timeout = 60
keepalive = 2

# Use shared memory for worker temp files (faster and saves RAM)
worker_tmp_dir = '/dev/shm'

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'warning'  # Only log warnings and errors
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sμs'

# Process naming
proc_name = 'homework-scraper'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Preload app for better memory efficiency with multiple workers
preload_app = True

# Worker lifecycle
worker_class = 'gthread'  # Better for I/O bound Django apps
worker_tmp_dir = '/dev/shm'  # Use RAM for temp files

def on_starting(server):
    """Called just before the master process is initialized."""
    print("Starting Homework Scraper Backend (Optimized)")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("Reloading Homework Scraper Backend")

def when_ready(server):
    """Called just after the server is started."""
    print(f"Server is ready. Spawning {workers} workers")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    print(f"Worker {worker.pid} interrupted")

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    print(f"Worker {worker.pid} initialized")
