# Credential Encryption Setup

## Overview

The homework scraper stores user credentials (school login information) securely using encryption. This requires an `ENCRYPTION_KEY` environment variable to be set.

## Generating an Encryption Key

### Method 1: Using Django Management Command

```bash
cd backend
python manage.py generate_encryption_key
```

This will output a key like: `xScR7Q9v8j2kL4mN6pP1qR3sT5uV7wX9yA0bC2dE4fG=`

### Method 2: Using Python Directly

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Method 3: Using Python REPL

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

## Setting Up the Key

### For Local Development

Add to `backend/.env`:
```bash
ENCRYPTION_KEY=your_generated_key_here
```

### For Render.com Production

1. Go to your Render.com dashboard
2. Select your backend service (homework-scraper-backend)
3. Go to "Environment" tab
4. Click "Add Environment Variable"
5. Key: `ENCRYPTION_KEY`
6. Value: Paste your generated key
7. Click "Save Changes"

The service will automatically redeploy with the new key.

## Important Notes

⚠️ **CRITICAL**: Once you set an encryption key and store credentials, you MUST keep using the same key. If you change the key, all existing encrypted credentials will become unreadable.

⚠️ **Security**: Keep your encryption key secret. Don't commit it to version control.

⚠️ **Backup**: Save your encryption key in a secure password manager or secrets vault.

## Key Format

The encryption key must be:
- 32 bytes (256 bits) of random data
- Base64-encoded
- Results in a 44-character string
- Example: `xScR7Q9v8j2kL4mN6pP1qR3sT5uV7wX9yA0bC2dE4fG=`

## Troubleshooting

### Error: "Invalid ENCRYPTION_KEY format"

The key in your environment is not a valid Fernet key. Generate a new one using the methods above.

### Error: "Failed to retrieve credentials" (500)

This usually means:
1. `ENCRYPTION_KEY` is not set in the environment
2. The key format is invalid
3. Credentials were encrypted with a different key

**Solution**: Set a valid encryption key using the steps above.

### Warning: "Cannot write to .env file (production environment)"

This is normal in production. The system will use environment variables instead of a file.

## How It Works

1. User credentials (username/password) are encrypted using Fernet (symmetric encryption)
2. Encrypted data is stored in the database
3. When needed, credentials are decrypted using the same key
4. The key itself is never stored in the database - only in environment variables

## Security Best Practices

✅ Use a unique encryption key for each environment (dev, staging, prod)
✅ Rotate keys periodically (requires re-encrypting all credentials)
✅ Use environment variables, never hardcode keys
✅ Restrict access to production environment variables
✅ Keep backups of your encryption key in a secure vault
