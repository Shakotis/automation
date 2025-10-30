# Supabase RLS Performance Fix - Complete Guide

## 🎯 Overview

This guide helps you fix the Supabase database linter warnings for your `profiles` table. The issues are:

1. **Auth RLS InitPlan** - `auth.uid()` being re-evaluated for each row (performance issue)
2. **Multiple Permissive Policies** - Duplicate policies causing unnecessary overhead

## 📋 The Problems

### Issue 1: Auth RLS InitPlan
Your policies use `auth.uid()` directly, which PostgreSQL re-evaluates for EVERY row:
```sql
-- ❌ BAD: Evaluated per row
USING (id = auth.uid())
```

### Issue 2: Multiple Permissive Policies
You have duplicate policies for the same role and action:
- 2 SELECT policies for `anon`, `authenticated`, `authenticator`, `dashboard_user`
- 2 UPDATE policies for `anon`, `authenticated`, `authenticator`, `dashboard_user`
- 2 INSERT policies for `authenticated`

## ✅ The Solution

### 1. Wrap auth.uid() with SELECT
```sql
-- ✅ GOOD: Evaluated once per query
USING (id = (SELECT auth.uid()))
```

### 2. Consolidate Policies
Instead of having multiple policies per action, create ONE optimized policy per action:

- **SELECT**: `allow_public_select` - Everyone can view profiles
- **INSERT**: `allow_authenticated_insert_own` - Authenticated users can create their own profile
- **UPDATE**: `allow_authenticated_update_own` - Users can update only their own profile

## 🚀 How to Apply the Fix

### Option 1: Supabase Dashboard (Recommended)

1. **Open Supabase Dashboard**
   - Go to https://app.supabase.com
   - Select your project

2. **Open SQL Editor**
   - Click "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Copy and Paste**
   - Open `supabase-fix-rls-performance.sql`
   - Copy the entire contents
   - Paste into the SQL Editor

4. **Execute**
   - Click "Run" or press `Ctrl+Enter`
   - Wait for confirmation message

5. **Verify**
   - Run the verification queries at the bottom of the script
   - You should see exactly 3 policies

### Option 2: Supabase CLI

If you have Supabase CLI installed:

```powershell
# Apply the fix
supabase db execute --file supabase-fix-rls-performance.sql

# Or using pipeline
Get-Content supabase-fix-rls-performance.sql | supabase db execute

# Verify
supabase db execute -c "SELECT policyname, cmd, roles FROM pg_policies WHERE tablename = 'profiles';"
```

### Option 3: PowerShell Script

```powershell
# Run the helper script
.\apply-rls-fix.ps1
```

This script will guide you through the process and offer to use Supabase CLI if available.

## 🔍 Verification

After applying the fix, verify the changes:

### Check Policies
```sql
SELECT 
    policyname,
    cmd,
    roles,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'profiles'
ORDER BY cmd, policyname;
```

**Expected Result:** You should see exactly 3 policies:
- `allow_public_select` (SELECT, USING: true)
- `allow_authenticated_insert_own` (INSERT, WITH CHECK: id = (SELECT auth.uid()))
- `allow_authenticated_update_own` (UPDATE, USING & WITH CHECK: id = (SELECT auth.uid()))

### Check RLS Status
```sql
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename = 'profiles';
```

**Expected Result:** `rowsecurity` should be `true`

### Test Functionality

After applying the fix, test that your application still works:

1. **Sign Up** - Create a new account
2. **View Profile** - Check if you can see your profile
3. **Update Profile** - Modify your profile information
4. **View Others** - Check if you can view other users' profiles (if applicable)

## 📊 Performance Impact

### Before
- `auth.uid()` called **N times** (where N = number of rows)
- **Multiple policies** evaluated per query
- **Slower queries** at scale

### After
- `auth.uid()` called **once per query**
- **Single policy** per action
- **Faster queries**, especially with many profiles

## 🎉 Expected Outcomes

After applying this fix:

1. ✅ All "Auth RLS InitPlan" warnings will disappear
2. ✅ All "Multiple Permissive Policies" warnings will disappear
3. ✅ Query performance will improve, especially at scale
4. ✅ Your application will continue to work exactly the same

## 🔧 Troubleshooting

### Error: "policy already exists"
This means the old policies weren't dropped. Try:
```sql
-- List all policies
SELECT policyname FROM pg_policies WHERE tablename = 'profiles';

-- Drop them manually
DROP POLICY IF EXISTS "<policy_name>" ON public.profiles;
```

### Error: "permission denied"
Make sure you're using a user with appropriate permissions (service role key or database admin).

### Policies not showing up
Check if RLS is enabled:
```sql
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
```

### Application not working after fix
The policies should maintain the same behavior. If something broke, check:
1. Are you using `anon` vs `authenticated` correctly?
2. Is the `id` column in profiles matching the user ID?
3. Check browser console and network logs for specific errors

## 📝 What Changed

### Removed Policies
- ❌ "Public profiles are viewable by everyone."
- ❌ "Users can view their own profile"
- ❌ "Users can update their own profile"
- ❌ "Users can update own profile."
- ❌ "Users can insert their own profile."
- ❌ "Enable insert for authenticated users only"

### Added Policies
- ✅ `allow_public_select` - Consolidated SELECT
- ✅ `allow_authenticated_insert_own` - Consolidated INSERT with optimized auth check
- ✅ `allow_authenticated_update_own` - Consolidated UPDATE with optimized auth check

## 📚 References

- [Supabase RLS Performance Guide](https://supabase.com/docs/guides/database/postgres/row-level-security#call-functions-with-select)
- [Database Linter Documentation](https://supabase.com/docs/guides/database/database-linter)
- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

## 🤝 Need Help?

If you encounter any issues:

1. Check the Supabase Dashboard logs
2. Review the verification queries output
3. Test with curl or Postman to isolate issues
4. Check your environment variables (`.env` file)

---

**Last Updated:** October 29, 2025  
**Status:** Ready to apply  
**Impact:** Low risk, high benefit
