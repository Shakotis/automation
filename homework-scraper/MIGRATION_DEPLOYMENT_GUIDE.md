# Render Migration Deployment Guide

Since you don't have shell access, follow these steps to run migrations:

## Step 1: Commit and Push Changes
1. In VS Code, open the Source Control panel (Ctrl+Shift+G)
2. Stage the `render.yaml` file
3. Commit with message: "Add migration worker service"
4. Push to main branch

## Step 2: Deploy Migration Worker
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Blueprint"
3. Connect your GitHub repo: `Shakotis/automation`
4. Select branch: `main`
5. In the service selection, you'll see the new "homework-scraper-migrations" worker
6. Click "Create Blueprint"

## Step 3: Configure Environment Variables
In the new migration worker service:
1. Go to Environment
2. Add these variables (copy from your main backend service):
   - `DATABASE_URL` (your Supabase session pooler URL)
   - `SECRET_KEY` (your Django secret key)

## Step 4: Deploy and Run Migrations
1. Click "Manual Deploy" → "Deploy latest commit"
2. Wait for deployment to complete
3. Check the logs - you should see "✓ Migrations completed!"
4. Once migrations are done, you can delete this worker service

## Step 5: Test Your Application
After migrations complete:
1. Visit https://nd.dovydas.space
2. Try logging in - CORS errors should be resolved
3. Check that settings page loads without 500 errors

## Troubleshooting
- If deployment fails, check the logs for specific errors
- Make sure DATABASE_URL uses port 6543 (session pooler)
- Verify all environment variables are set correctly