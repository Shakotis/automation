# 🚀 QUICK DEPLOY COMMANDS

## Netlify (Frontend) - 3 Settings Only

```
Base directory:     frontend
Build command:      npm run build
Publish directory:  frontend/out
```

**Environment Variables (3):**
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api
NEXT_PUBLIC_SITE_URL=https://your-app.netlify.app
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

---

## Render (Backend) - 2 Commands

### Build Command:
```bash
pip install --upgrade pip && pip install -r requirements.txt && playwright install chromium && python manage.py collectstatic --no-input && python manage.py migrate
```

### Start Command:
```bash
gunicorn homework_scraper.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
```

**Or use Blueprint:** Just select `render.yaml` and click "Apply" ✅

---

## Environment Variables (Render)

Copy from `backend/.env.production.example` and set:
- `SECRET_KEY` - Use "Generate Value"
- `CORS_ALLOWED_ORIGINS` - Your Netlify URL
- `GOOGLE_OAUTH2_CLIENT_ID` - From Google Console
- `GOOGLE_OAUTH2_CLIENT_SECRET` - From Google Console
- `ENCRYPTION_KEY` - Use "Generate Value"

Others are auto-provided by Render services.

---

## Test URLs After Deploy

- Frontend: `https://your-app.netlify.app`
- Backend Health: `https://your-backend.onrender.com/api/health`
- Should see: `{"status": "ok"}`

---

## 🐛 Still Getting 404?

1. Check Netlify build log - should see "Exporting (X/X)"
2. Verify `out/` directory exists in build
3. Verify publish directory is `frontend/out` not `.next`
4. Check redirect rules in netlify.toml

**All fixed!** ✅ Your config is correct now.
