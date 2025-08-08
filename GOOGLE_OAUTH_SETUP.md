# Google OAuth Setup Guide

## Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API and Google OAuth2 API

## Step 2: Configure OAuth Consent Screen
1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill in app information:
   - App name: "Carrigar by Tubematic"
   - User support email: your email
   - Developer contact email: your email
4. Add scopes: `email`, `profile`, `openid`
5. Add test users (your email)

## Step 3: Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - `http://127.0.0.1:8000/accounts/google/callback/`
   - `http://localhost:8000/accounts/google/callback/`
5. Copy Client ID and Client Secret

## Step 4: Update Django Settings
Replace in `mywebsite/settings.py`:
```python
GOOGLE_OAUTH2_CLIENT_ID = 'your-actual-client-id.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET = 'your-actual-client-secret'
```

## Step 5: Test
1. Restart Django server
2. Click "Continue with Google" button
3. Complete Google OAuth flow

## Security Notes
- Never commit real credentials to version control
- Use environment variables in production
- Add `*.pyc` and `__pycache__/` to .gitignore 