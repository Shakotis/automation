# Fixing Supabase Security Issues

## Issues to Fix

1. ⚠️ **Function Search Path Mutable** (2 issues)
   - `public.handle_new_user`
   - `public.is_admin`

2. 🔐 **Leaked Password Protection Disabled**

3. 🔑 **Insufficient MFA Options**

---

## Fix 1 & 2: Function Search Path Issues

### Problem
Functions without explicit `search_path` are vulnerable to SQL injection and privilege escalation attacks.

### Solution

**Run in Supabase SQL Editor:**

```sql
-- Fix handle_new_user function
DROP FUNCTION IF EXISTS public.handle_new_user CASCADE;

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public  -- This fixes the issue
AS $$
BEGIN
  INSERT INTO public.users (id, email, created_at)
  VALUES (NEW.id, NEW.email, NEW.created_at)
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

-- Fix is_admin function
DROP FUNCTION IF EXISTS public.is_admin CASCADE;

CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public  -- This fixes the issue
AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.admin_users WHERE id = auth.uid()
  );
END;
$$;
```

**Key Change:** Adding `SET search_path = public` to each function prevents the security vulnerability.

---

## Fix 3: Enable Leaked Password Protection

### Problem
Users can set passwords that have been exposed in data breaches.

### Solution

**Via Supabase Dashboard:**

1. Go to: **Authentication** → **Settings**
2. Scroll to: **Security and Protection**
3. Find: **"Leaked Password Protection"**
4. Toggle: **Enable**
5. Click: **Save**

**Via Supabase CLI** (if you have it installed):
```bash
supabase auth update --enable-leaked-password-protection
```

**What it does:**
- Checks passwords against the [HaveIBeenPwned](https://haveibeenpwned.com/) database
- Prevents users from using compromised passwords
- Happens during signup and password change

---

## Fix 4: Enable Multi-Factor Authentication (MFA)

### Problem
Only one MFA method is available. More options improve security.

### Solution

**Via Supabase Dashboard:**

1. Go to: **Authentication** → **Settings**
2. Scroll to: **Multi-Factor Authentication**
3. Enable these options:
   - ✅ **TOTP (Time-based One-Time Password)** - Apps like Google Authenticator, Authy
   - ✅ **Phone (SMS)** - If you have Twilio configured
   - ✅ **Email** - If email OTP is desired

4. Click: **Save**

**Recommended MFA Settings:**
- **Enable TOTP** (most secure, works offline)
- **Set MFA level:** "Optional" or "Required"
- **Grace period:** 7 days (allows users time to set up)

**For your application:**

If you want to enforce MFA for certain users:

```typescript
// In your frontend (Next.js)
import { supabase } from '@/lib/supabase'

// Enroll user in MFA (TOTP)
const { data, error } = await supabase.auth.mfa.enroll({
  factorType: 'totp',
})

// User scans QR code and enters verification code
const { data: verifyData, error: verifyError } = await supabase.auth.mfa.verify({
  factorId: data.id,
  code: userEnteredCode,
})
```

---

## Quick Steps Summary

### 1. SQL Fixes (2 minutes)
1. Open Supabase Dashboard → **SQL Editor**
2. Copy and paste the SQL from `supabase-security-fixes.sql`
3. Click **Run**
4. Verify: Should see "Success" message

### 2. Dashboard Settings (3 minutes)
1. Go to **Authentication** → **Settings**
2. Enable **Leaked Password Protection** ✅
3. Enable **MFA options** (TOTP at minimum) ✅
4. Click **Save**

### 3. Verification
Run this query to verify the functions are fixed:

```sql
SELECT 
    proname as function_name,
    prosecdef as is_security_definer,
    proconfig as configuration
FROM pg_proc 
WHERE proname IN ('handle_new_user', 'is_admin')
AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');
```

Expected result: `configuration` column should show `{search_path=public}`

---

## Additional Security Recommendations

### 1. Enable RLS on All User Tables
```sql
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
```

### 2. Set Strong Password Requirements
In **Authentication** → **Settings**:
- Minimum length: 12 characters
- Require uppercase, lowercase, numbers, symbols

### 3. Enable Email Confirmations
- Require email confirmation for signups
- Enable email change confirmation

### 4. Set Session Timeout
- JWT expiry: 3600 seconds (1 hour)
- Refresh token rotation: Enabled

### 5. Monitor Auth Events
Set up webhooks to track:
- Failed login attempts
- Password resets
- MFA enrollments

---

## Testing

After applying fixes:

1. **Test handle_new_user:**
   - Create a new user via your signup flow
   - Verify user appears in `public.users` table

2. **Test is_admin:**
   ```sql
   SELECT public.is_admin(); -- Should return true/false
   ```

3. **Test Leaked Password Protection:**
   - Try signing up with password: `password123`
   - Should be rejected as compromised

4. **Test MFA:**
   - Enable MFA on a test account
   - Verify 6-digit code works

---

## Files Created

- `supabase-security-fixes.sql` - Run this in Supabase SQL Editor
- `docs/SUPABASE_SECURITY_FIXES.md` - This guide

---

## Questions?

- **"Will this break existing users?"** - No, these are additive security improvements
- **"Do I need to recreate triggers?"** - Yes, if you use triggers with these functions
- **"Is MFA mandatory?"** - No, you can set it as optional (recommended for UX)
- **"What about SMS costs?"** - SMS MFA requires Twilio (costs apply), but TOTP is free

---

## Priority

1. 🔴 **HIGH:** Fix function search paths (prevents SQL injection)
2. 🟡 **MEDIUM:** Enable leaked password protection (improves user security)
3. 🟢 **LOW:** Add more MFA options (convenience/optional security)

Start with the SQL fixes, then enable the dashboard settings.
