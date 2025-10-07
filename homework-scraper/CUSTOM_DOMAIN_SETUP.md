# Custom Domain Setup Guide

## Your Domains
- **Frontend**: `nd.dovydas.space`
- **Backend API**: `api.dovydas.space`

---

## 🔧 Setup Steps

### Step 1: Configure Backend Domain on Render (api.dovydas.space)

1. **Go to Render Dashboard**
   - Navigate to your `homework-scraper-backend` service
   - Click on "Settings"

2. **Add Custom Domain**
   - Scroll to "Custom Domain" section
   - Click "Add Custom Domain"
   - Enter: `api.dovydas.space`
   - Click "Save"

3. **Update DNS Records**
   Render will show you the DNS records to add. In your DNS provider (where dovydas.space is hosted):
   
   **Option A: CNAME (Recommended)**
   ```
   Type: CNAME
   Name: api
   Value: homework-scraper-backend.onrender.com
   TTL: 3600 (or automatic)
   ```

   **Option B: A Record**
   ```
   Type: A
   Name: api
   Value: [IP address provided by Render]
   TTL: 3600
   ```

4. **Wait for DNS Propagation**
   - Usually takes 5-30 minutes
   - Render will automatically provision SSL certificate
   - Status will change from "Pending" to "Live"

5. **Update Environment Variables on Render**
   - Go to Environment tab
   - Update `ALLOWED_HOSTS`:
     ```
     .onrender.com,api.dovydas.space
     ```
   - Update `CSRF_TRUSTED_ORIGINS`:
     ```
     https://nd.dovydas.space,https://api.dovydas.space
     ```
   - Click "Save Changes" (triggers redeploy)

---

### Step 2: Configure Frontend Domain on Netlify (nd.dovydas.space)

1. **Go to Netlify Dashboard**
   - Navigate to your site
   - Click on "Domain settings"

2. **Add Custom Domain**
   - Click "Add custom domain"
   - Enter: `nd.dovydas.space`
   - Click "Verify"
   - If you own the domain, click "Add domain"

3. **Update DNS Records**
   In your DNS provider (where dovydas.space is hosted):
   
   **Option A: CNAME (Recommended if not apex domain)**
   ```
   Type: CNAME
   Name: nd
   Value: [your-site-name].netlify.app
   TTL: 3600
   ```

   **Option B: Netlify DNS (if using Netlify nameservers)**
   - Follow Netlify's instructions to update nameservers
   - Netlify will manage all DNS records

4. **Enable HTTPS**
   - Netlify automatically provisions SSL certificate
   - This may take a few minutes
   - Check that "HTTPS" shows as active

5. **Update Environment Variables on Netlify**
   - Go to Site settings → Environment variables
   - Update or add:
     ```
     NEXT_PUBLIC_API_URL=https://api.dovydas.space/api
     NEXT_PUBLIC_SITE_URL=https://nd.dovydas.space
     ```
   - Click "Save"
   - Trigger a new deployment: Deploys → Trigger deploy → Deploy site

---

### Step 3: Update Google OAuth Settings

1. **Go to Google Cloud Console**
   - Navigate to: https://console.cloud.google.com
   - Select your project
   - Go to "APIs & Services" → "Credentials"

2. **Update OAuth 2.0 Client**
   - Click on your OAuth client ID
   - Under "Authorized JavaScript origins", add:
     ```
     https://nd.dovydas.space
     ```
   - Under "Authorized redirect URIs", add:
     ```
     https://nd.dovydas.space/auth/callback
     https://nd.dovydas.space/api/auth/callback/google
     ```
   - Click "Save"

---

### Step 4: Update Frontend Configuration

If you have a config file in your frontend, update the API URL:

**File**: `frontend/config/api.ts` or similar
```typescript
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.dovydas.space/api';
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://nd.dovydas.space';
```

---

## ✅ Verification Checklist

### Backend (api.dovydas.space)
- [ ] Custom domain shows as "Live" in Render
- [ ] SSL certificate is active (🔒 shows in browser)
- [ ] Health check works: `https://api.dovydas.space/api/health`
- [ ] Returns: `{"status": "ok"}`
- [ ] No CORS errors in browser console

### Frontend (nd.dovydas.space)
- [ ] Domain shows as "Active" in Netlify
- [ ] SSL certificate is active (🔒 shows in browser)
- [ ] Site loads: `https://nd.dovydas.space`
- [ ] No 404 errors
- [ ] Assets load correctly (check Network tab)

### Integration
- [ ] Google login button appears
- [ ] Can click "Sign in with Google"
- [ ] OAuth redirect works (no errors)
- [ ] After login, can access dashboard
- [ ] API calls reach backend (check Network tab)
- [ ] No CORS errors in console

### DNS Propagation
Check DNS is working:
```powershell
# Check backend DNS
nslookup api.dovydas.space

# Check frontend DNS
nslookup nd.dovydas.space

# Alternative: use online tools
# https://dnschecker.org
```

---

## 🐛 Troubleshooting

### DNS Not Resolving
**Problem**: Domain doesn't load, shows DNS error

**Solutions**:
1. Wait longer (DNS can take up to 48 hours, usually 5-30 min)
2. Check DNS records are correct in your DNS provider
3. Use `nslookup` or online DNS checker to verify
4. Clear your DNS cache:
   ```powershell
   ipconfig /flushdns
   ```

### SSL Certificate Pending
**Problem**: Domain shows "Not Secure" or SSL pending

**Solutions**:
1. Wait for automatic provisioning (5-15 minutes)
2. For Render: Check domain is verified
3. For Netlify: Check "Domain settings" → HTTPS section
4. Try manual renewal in platform settings

### CORS Errors
**Problem**: Browser console shows CORS errors

**Solutions**:
1. Verify `CORS_ALLOWED_ORIGINS` includes `https://nd.dovydas.space`
2. Check no trailing slashes in CORS settings
3. Ensure backend redeploy after changing env vars
4. Check browser console for exact error message
5. Verify API URL in frontend matches `api.dovydas.space`

### Google OAuth Fails
**Problem**: Redirect errors or "400: redirect_uri_mismatch"

**Solutions**:
1. Add all redirect URIs in Google Console (see Step 3)
2. Check URIs match exactly (no trailing slashes)
3. Wait 5 minutes after updating Google Console
4. Clear browser cache and cookies
5. Try incognito/private browsing

### 404 on Frontend Routes
**Problem**: Direct navigation to routes shows 404

**Solutions**:
1. Check `netlify.toml` has redirect rules
2. Verify `output: 'export'` in `next.config.js`
3. Check build created `out` directory
4. Redeploy frontend after configuration changes

---

## 📋 Environment Variables Summary

### Render (Backend)
```bash
# Already in render.yaml, but verify in dashboard:
ALLOWED_HOSTS=.onrender.com,api.dovydas.space
CORS_ALLOWED_ORIGINS=https://nd.dovydas.space,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://nd.dovydas.space,https://api.dovydas.space
```

### Netlify (Frontend)
```bash
NEXT_PUBLIC_API_URL=https://api.dovydas.space/api
NEXT_PUBLIC_SITE_URL=https://nd.dovydas.space
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
```

---

## 🚀 Deployment After Domain Setup

1. **Commit configuration changes**:
   ```powershell
   git add .
   git commit -m "Configure custom domains: nd.dovydas.space and api.dovydas.space"
   git push origin main
   ```

2. **Verify auto-deployment**:
   - Render: Auto-deploys from Git push
   - Netlify: Auto-deploys from Git push

3. **Manual redeploy if needed**:
   - Render: Dashboard → Manual Deploy → Deploy latest commit
   - Netlify: Deploys → Trigger deploy → Deploy site

---

## 🎯 Quick Test Commands

```powershell
# Test backend health
curl https://api.dovydas.space/api/health

# Test frontend loads
curl -I https://nd.dovydas.space

# Check DNS resolution
nslookup api.dovydas.space
nslookup nd.dovydas.space

# Test CORS (from browser console at nd.dovydas.space)
fetch('https://api.dovydas.space/api/health')
  .then(r => r.json())
  .then(console.log)
```

---

## 📝 DNS Records Summary

Add these records in your DNS provider for `dovydas.space`:

| Type  | Name | Value                                    | TTL  |
|-------|------|------------------------------------------|------|
| CNAME | api  | homework-scraper-backend.onrender.com    | 3600 |
| CNAME | nd   | [your-site-name].netlify.app             | 3600 |

*Replace `[your-site-name]` with your actual Netlify site name*

---

## ✨ All Set!

Once DNS propagates and SSL certificates are active:
- Frontend: https://nd.dovydas.space
- Backend API: https://api.dovydas.space/api
- Health Check: https://api.dovydas.space/api/health

Your homework scraper will be live on your custom domains! 🎉
