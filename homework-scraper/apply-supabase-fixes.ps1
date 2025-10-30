# ========================================
# Apply Complete Supabase Fixes
# ========================================
# Applies all security and performance fixes to Supabase
# Handles: RLS, Functions, and provides Auth configuration guidance

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('all', 'rls', 'security', 'functions')]
    [string]$FixType = 'all',
    
    [string]$SupabaseUrl = $env:SUPABASE_URL,
    [string]$SupabaseKey = $env:SUPABASE_SERVICE_KEY
)

# Color output helpers
function Write-Success { param([string]$Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Info { param([string]$Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }
function Write-Warning { param([string]$Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Failure { param([string]$Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Step { param([string]$Message) Write-Host "`n═══ $Message ═══" -ForegroundColor Magenta }

# Banner
Clear-Host
Write-Host @"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     Supabase Complete Fix Application Tool              ║
║     Resolves: RLS Performance + Security Issues         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host ""

# Load environment variables
if (Test-Path ".env") {
    Write-Info "Loading environment variables from .env..."
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
    Write-Success "Environment loaded"
}

# Determine which SQL file to use
$sqlFile = switch ($FixType) {
    'all'      { "supabase-fix-all-warnings.sql" }
    'rls'      { "supabase-fix-rls-performance.sql" }
    'security' { "supabase-fix-security-issues.sql" }
    'functions' { "supabase-fix-security-issues.sql" }
}

Write-Host ""
Write-Info "Fix Type: $FixType"
Write-Info "SQL File: $sqlFile"
Write-Host ""

# Check if file exists
if (-not (Test-Path $sqlFile)) {
    Write-Failure "SQL file not found: $sqlFile"
    exit 1
}

# Display what will be fixed
Write-Step "Issues to be Fixed"
Write-Host ""

switch ($FixType) {
    'all' {
        Write-Host "Performance Issues:" -ForegroundColor Yellow
        Write-Host "  • Auth RLS InitPlan (4 warnings)"
        Write-Host "  • Multiple Permissive Policies (9 warnings)"
        Write-Host ""
        Write-Host "Security Issues:" -ForegroundColor Yellow
        Write-Host "  • Function Search Path Mutable (2 warnings)"
        Write-Host ""
        Write-Host "Total Automated Fixes: 15 warnings" -ForegroundColor Green
    }
    'rls' {
        Write-Host "Performance Issues:" -ForegroundColor Yellow
        Write-Host "  • Auth RLS InitPlan (4 warnings)"
        Write-Host "  • Multiple Permissive Policies (9 warnings)"
        Write-Host ""
        Write-Host "Total Automated Fixes: 13 warnings" -ForegroundColor Green
    }
    'security' {
        Write-Host "Security Issues:" -ForegroundColor Yellow
        Write-Host "  • Function Search Path Mutable (2 warnings)"
        Write-Host ""
        Write-Host "Total Automated Fixes: 2 warnings" -ForegroundColor Green
    }
}

Write-Host ""

# Check for Supabase CLI
Write-Step "Checking for Supabase CLI"
Write-Host ""

$supabaseCli = Get-Command "supabase" -ErrorAction SilentlyContinue

if ($supabaseCli) {
    Write-Success "Supabase CLI detected at: $($supabaseCli.Source)"
    Write-Host ""
    
    # Ask user if they want to apply now
    $response = Read-Host "Do you want to apply fixes using Supabase CLI now? (y/n)"
    
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Step "Applying Fixes"
        Write-Host ""
        Write-Info "Executing SQL script..."
        Write-Host ""
        
        try {
            # Execute the SQL file
            $output = Get-Content $sqlFile -Raw | supabase db execute 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "SQL script executed successfully!"
                Write-Host ""
                
                # Show what was fixed
                Write-Step "Verification"
                Write-Host ""
                Write-Info "Checking RLS policies..."
                
                $policiesQuery = @"
SELECT 
    policyname,
    cmd,
    roles
FROM pg_policies 
WHERE tablename = 'profiles'
ORDER BY cmd, policyname;
"@
                
                $policiesOutput = supabase db execute -c $policiesQuery 2>&1
                Write-Host $policiesOutput
                Write-Host ""
                
                Write-Info "Checking function security..."
                
                $functionsQuery = @"
SELECT 
    p.proname as function_name,
    pg_catalog.array_to_string(p.proconfig, ', ') as settings
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public' 
AND p.proname IN ('handle_new_user', 'is_admin');
"@
                
                $functionsOutput = supabase db execute -c $functionsQuery 2>&1
                Write-Host $functionsOutput
                Write-Host ""
                
                Write-Success "All automated fixes applied successfully!"
                
            } else {
                Write-Failure "Failed to execute SQL script"
                Write-Host $output
                exit 1
            }
        } catch {
            Write-Failure "Error executing SQL: $_"
            exit 1
        }
    } else {
        Write-Warning "Skipping automatic application"
    }
} else {
    Write-Warning "Supabase CLI not found"
    Write-Host ""
    Write-Info "Install Supabase CLI with:"
    Write-Host "  npm install -g supabase" -ForegroundColor Yellow
    Write-Host ""
}

# Manual steps guidance
if ($FixType -eq 'all' -or $FixType -eq 'security') {
    Write-Step "Manual Configuration Required"
    Write-Host ""
    Write-Warning "The following settings must be configured in Supabase Dashboard:"
    Write-Host ""
    
    Write-Host "1. LEAKED PASSWORD PROTECTION" -ForegroundColor Yellow
    Write-Host "   URL: https://app.supabase.com/project/YOUR_PROJECT/auth/policies"
    Write-Host "   • Navigate to Authentication → Policies"
    Write-Host "   • Find 'Password Strength' section"
    Write-Host "   • Enable 'Check against HaveIBeenPwned.org'"
    Write-Host "   • Click Save"
    Write-Host ""
    
    Write-Host "2. MULTI-FACTOR AUTHENTICATION (MFA)" -ForegroundColor Yellow
    Write-Host "   URL: https://app.supabase.com/project/YOUR_PROJECT/auth/mfa"
    Write-Host "   • Navigate to Authentication → Multi-Factor Auth"
    Write-Host "   • Enable at least one method:"
    Write-Host "     ✓ TOTP (Recommended) - Google Authenticator, Authy"
    Write-Host "     ✓ WebAuthn - Hardware keys, Touch ID, Face ID"
    Write-Host "     ✓ Phone/SMS - Requires SMS provider setup"
    Write-Host "   • Click Save"
    Write-Host ""
    
    Write-Info "After configuring, implement MFA in your frontend:"
    Write-Host "  See: https://supabase.com/docs/guides/auth/auth-mfa"
    Write-Host ""
}

# Alternative: Manual application
if (-not $supabaseCli -or ($response -ne "y" -and $response -ne "Y")) {
    Write-Step "Manual Application Instructions"
    Write-Host ""
    Write-Info "Apply fixes manually via Supabase Dashboard:"
    Write-Host ""
    Write-Host "1. Go to: https://app.supabase.com" -ForegroundColor White
    Write-Host "2. Select your project" -ForegroundColor White
    Write-Host "3. Navigate to: SQL Editor" -ForegroundColor White
    Write-Host "4. Click: New Query" -ForegroundColor White
    Write-Host "5. Copy contents of: $sqlFile" -ForegroundColor Yellow
    Write-Host "6. Paste into SQL Editor" -ForegroundColor White
    Write-Host "7. Click: Run (or press Ctrl+Enter)" -ForegroundColor White
    Write-Host ""
}

# Documentation
Write-Step "Documentation"
Write-Host ""
Write-Info "For detailed information, see:"
Write-Host "  • docs/COMPLETE_SECURITY_FIX_GUIDE.md" -ForegroundColor Yellow
Write-Host "  • docs/RLS_PERFORMANCE_FIX_GUIDE.md" -ForegroundColor Yellow
Write-Host ""

# Summary
Write-Step "Summary"
Write-Host ""

if ($supabaseCli -and ($response -eq "y" -or $response -eq "Y")) {
    Write-Success "Automated fixes applied successfully!"
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Configure Auth settings in Dashboard (see above)"
    Write-Host "  2. Run database linter to verify (should show 0 warnings)"
    Write-Host "  3. Test your application thoroughly"
    Write-Host "  4. Monitor query performance"
} else {
    Write-Info "Ready to apply fixes"
    Write-Host ""
    Write-Host "Choose your method:" -ForegroundColor Cyan
    Write-Host "  A. Install Supabase CLI and run this script again"
    Write-Host "  B. Apply manually via Supabase Dashboard (see above)"
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
