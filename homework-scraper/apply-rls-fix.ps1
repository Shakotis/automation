# ========================================
# Apply Supabase RLS Performance Fix
# ========================================
# This script applies the optimized RLS policies to your Supabase database
# and verifies the changes were successful

param(
    [string]$SupabaseUrl = $env:SUPABASE_URL,
    [string]$SupabaseKey = $env:SUPABASE_SERVICE_KEY
)

# Color output helpers
function Write-Success { param([string]$Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Info { param([string]$Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }
function Write-Warning { param([string]$Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Failure { param([string]$Message) Write-Host "✗ $Message" -ForegroundColor Red }

Write-Info "Starting Supabase RLS Performance Fix Application..."
Write-Host ""

# Check if .env file exists and load it
if (Test-Path ".env") {
    Write-Info "Loading environment variables from .env file..."
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.+)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
            if (-not $SupabaseUrl -and $key -eq "SUPABASE_URL") {
                $SupabaseUrl = $value
            }
            if (-not $SupabaseKey -and $key -eq "SUPABASE_SERVICE_KEY") {
                $SupabaseKey = $value
            }
        }
    }
    Write-Success "Environment variables loaded"
} else {
    Write-Warning ".env file not found"
}

# Validate required parameters
if (-not $SupabaseUrl) {
    Write-Failure "SUPABASE_URL is required. Set it in .env or pass as parameter."
    exit 1
}

if (-not $SupabaseKey) {
    Write-Failure "SUPABASE_SERVICE_KEY is required. Set it in .env or pass as parameter."
    exit 1
}

# Read the SQL file
$sqlFile = "supabase-fix-rls-performance.sql"
if (-not (Test-Path $sqlFile)) {
    Write-Failure "SQL file not found: $sqlFile"
    exit 1
}

Write-Info "Reading SQL script: $sqlFile"
$sqlContent = Get-Content $sqlFile -Raw

# Extract the API endpoint
$apiUrl = "$SupabaseUrl/rest/v1/rpc/exec_sql"

# Note: Supabase doesn't have a direct SQL execution endpoint via REST API
# The recommended way is to use the Supabase Dashboard or CLI
Write-Host ""
Write-Info "===================================="
Write-Info "MANUAL APPLICATION REQUIRED"
Write-Info "===================================="
Write-Host ""
Write-Warning "Supabase doesn't support direct SQL execution via REST API for security reasons."
Write-Host ""
Write-Info "Please follow these steps:"
Write-Host ""
Write-Host "1. Go to your Supabase Dashboard: https://app.supabase.com"
Write-Host "2. Select your project"
Write-Host "3. Navigate to: SQL Editor (in left sidebar)"
Write-Host "4. Click 'New Query'"
Write-Host "5. Copy and paste the contents of: $sqlFile"
Write-Host "6. Click 'Run' or press Ctrl+Enter"
Write-Host ""
Write-Info "The script will:"
Write-Host "  • Drop all existing duplicate policies"
Write-Host "  • Create 3 optimized policies (SELECT, INSERT, UPDATE)"
Write-Host "  • Resolve all performance warnings"
Write-Host ""
Write-Info "After running the script, verify with:"
Write-Host "  SELECT * FROM pg_policies WHERE tablename = 'profiles';"
Write-Host ""

# Alternative: Use Supabase CLI if installed
Write-Host ""
Write-Info "===================================="
Write-Info "ALTERNATIVE: Use Supabase CLI"
Write-Info "===================================="
Write-Host ""
Write-Host "If you have Supabase CLI installed, you can run:"
Write-Host ""
Write-Host "  supabase db execute --file $sqlFile"
Write-Host ""
Write-Host "Or:"
Write-Host ""
Write-Host "  Get-Content $sqlFile | supabase db execute"
Write-Host ""

# Check if Supabase CLI is installed
if (Get-Command "supabase" -ErrorAction SilentlyContinue) {
    Write-Success "Supabase CLI detected!"
    Write-Host ""
    $response = Read-Host "Do you want to apply the fix using Supabase CLI now? (y/n)"
    
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Info "Applying fix via Supabase CLI..."
        try {
            $output = Get-Content $sqlFile | supabase db execute 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "SQL script executed successfully!"
                Write-Host ""
                Write-Info "Verifying policies..."
                $verifyOutput = supabase db execute -c "SELECT policyname, cmd, roles FROM pg_policies WHERE tablename = 'profiles' ORDER BY cmd, policyname;" 2>&1
                Write-Host $verifyOutput
            } else {
                Write-Failure "Failed to execute SQL script"
                Write-Host $output
            }
        } catch {
            Write-Failure "Error executing SQL: $_"
        }
    }
} else {
    Write-Info "Supabase CLI not found. Install it with:"
    Write-Host "  npm install -g supabase"
    Write-Host ""
}

Write-Host ""
Write-Info "Script execution completed."
Write-Host ""
