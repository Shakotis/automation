# Build script for Render.com
#!/usr/bin/env bash
set -o errexit  # Exit on error

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Installing Playwright browsers..."
# Install browsers to default location (~/.cache/ms-playwright)
# Skip system dependency validation as Render provides them
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true playwright install chromium

echo "Verifying browser installation..."
BROWSER_PATH="$HOME/.cache/ms-playwright"
if [ -d "$BROWSER_PATH" ]; then
    echo "✓ Browsers installed successfully at $BROWSER_PATH"
    ls -la "$BROWSER_PATH/" | head -20
else
    echo "⚠ Warning: Browser directory not found at $BROWSER_PATH"
fi

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Checking database connection..."
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set!"
    echo "Waiting for database service to be provisioned..."
    exit 1
fi

# Check if DATABASE_URL contains placeholder text
if echo "$DATABASE_URL" | grep -q "user:password@host:port"; then
    echo "ERROR: DATABASE_URL contains placeholder text!"
    echo "The database service is not yet linked properly."
    echo "Please wait for the database to finish provisioning."
    echo "Current DATABASE_URL: $DATABASE_URL"
    exit 1
fi

echo "Running database migrations..."
python manage.py migrate

echo "Build complete!"
