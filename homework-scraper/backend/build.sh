# Build script for Render.com
#!/usr/bin/env bash
set -o errexit  # Exit on error

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Installing Playwright browsers..."
# Install browsers to a persistent location in the project directory
# This ensures browsers are available at runtime
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.playwright-browsers
mkdir -p "$PLAYWRIGHT_BROWSERS_PATH"

# Install chromium with system dependency validation skipped
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true playwright install chromium

echo "Verifying browser installation..."
if [ -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    echo "✓ Browsers installed successfully at $PLAYWRIGHT_BROWSERS_PATH"
    ls -la "$PLAYWRIGHT_BROWSERS_PATH/" | head -20
    
    # Find the chromium executable
    CHROMIUM_EXEC=$(find "$PLAYWRIGHT_BROWSERS_PATH" -name "chrome" -o -name "chromium" | head -1)
    if [ -n "$CHROMIUM_EXEC" ]; then
        echo "✓ Chromium executable found at: $CHROMIUM_EXEC"
    else
        echo "⚠ Warning: Chromium executable not found in $PLAYWRIGHT_BROWSERS_PATH"
    fi
else
    echo "⚠ Warning: Browser directory not found at $PLAYWRIGHT_BROWSERS_PATH"
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
