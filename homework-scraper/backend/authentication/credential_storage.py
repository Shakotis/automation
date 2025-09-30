from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.contrib.auth.models import User
import base64
import json
import os
import logging

logger = logging.getLogger(__name__)

class SecureCredentialStorage:
    """
    Secure credential storage service using local encryption
    Free alternative to Google Secret Manager API
    """
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self):
        """Get or create encryption key from environment or generate new one"""
        if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY:
            # Use key from settings
            return settings.ENCRYPTION_KEY.encode()
        
        # Generate new key and save to .env file
        key = Fernet.generate_key()
        
        # Try to save to .env file
        try:
            env_path = os.path.join(settings.BASE_DIR.parent, '.env')
            
            # Read existing .env
            env_content = ""
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_content = f.read()
            
            # Add or update ENCRYPTION_KEY
            if 'ENCRYPTION_KEY=' in env_content:
                lines = env_content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('ENCRYPTION_KEY='):
                        lines[i] = f'ENCRYPTION_KEY={key.decode()}'
                        break
                env_content = '\n'.join(lines)
            else:
                env_content += f'\nENCRYPTION_KEY={key.decode()}\n'
            
            # Write back to .env
            with open(env_path, 'w') as f:
                f.write(env_content)
                
            logger.info("Generated and saved new encryption key")
            
        except Exception as e:
            logger.warning(f"Could not save encryption key to .env: {str(e)}")
        
        return key
    
    def _get_user_key(self, user_id: int, site: str):
        """Generate a unique key for user-site combination"""
        return f"user_{user_id}_site_{site}"
    
    def encrypt_credentials(self, data: dict) -> str:
        """Encrypt credential data"""
        try:
            json_data = json.dumps(data)
            encrypted_data = self.fernet.encrypt(json_data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Error encrypting credentials: {str(e)}")
            raise
    
    def decrypt_credentials(self, encrypted_data: str) -> dict:
        """Decrypt credential data"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Error decrypting credentials: {str(e)}")
            raise
    
    def store_user_credentials(self, user_id: int, site: str, username: str, password: str, additional_data: dict = None):
        """Store user credentials for a specific site"""
        try:
            from .models import UserCredential
            
            credential_data = {
                'username': username,
                'password': password,
                'site': site,
                'additional_data': additional_data or {}
            }
            
            encrypted_data = self.encrypt_credentials(credential_data)
            
            # Store in database
            credential, created = UserCredential.objects.update_or_create(
                user_id=user_id,
                site=site,
                defaults={
                    'encrypted_data': encrypted_data,
                    'is_verified': False
                }
            )
            
            logger.info(f"Stored credentials for user {user_id} on site {site}")
            return credential
            
        except Exception as e:
            logger.error(f"Error storing credentials: {str(e)}")
            raise
    
    def get_user_credentials(self, user_id: int, site: str) -> dict:
        """Get user credentials for a specific site"""
        try:
            from .models import UserCredential
            
            credential = UserCredential.objects.get(user_id=user_id, site=site)
            decrypted_data = self.decrypt_credentials(credential.encrypted_data)
            
            return {
                'username': decrypted_data['username'],
                'password': decrypted_data['password'],
                'additional_data': decrypted_data.get('additional_data', {}),
                'is_verified': credential.is_verified,
                'last_verified': credential.last_verified
            }
            
        except Exception as e:
            logger.error(f"Error getting credentials for user {user_id} on site {site}: {str(e)}")
            return None
    
    def get_all_user_credentials(self, user_id: int) -> dict:
        """Get all credentials for a user"""
        try:
            from .models import UserCredential
            
            credentials = UserCredential.objects.filter(user_id=user_id)
            result = {}
            
            for credential in credentials:
                try:
                    decrypted_data = self.decrypt_credentials(credential.encrypted_data)
                    result[credential.site] = {
                        'username': decrypted_data['username'],
                        'password': decrypted_data['password'],
                        'additional_data': decrypted_data.get('additional_data', {}),
                        'is_verified': credential.is_verified,
                        'last_verified': credential.last_verified
                    }
                except Exception as e:
                    logger.error(f"Error decrypting credentials for {credential.site}: {str(e)}")
                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting all credentials for user {user_id}: {str(e)}")
            return {}
    
    def update_credential_verification(self, user_id: int, site: str, is_verified: bool):
        """Update verification status of credentials"""
        try:
            from .models import UserCredential
            from django.utils import timezone
            
            credential = UserCredential.objects.get(user_id=user_id, site=site)
            credential.is_verified = is_verified
            if is_verified:
                credential.last_verified = timezone.now()
            credential.save()
            
            logger.info(f"Updated verification status for user {user_id} on site {site}: {is_verified}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating verification status: {str(e)}")
            return False
    
    def delete_user_credentials(self, user_id: int, site: str):
        """Delete user credentials for a specific site"""
        try:
            from .models import UserCredential
            
            UserCredential.objects.filter(user_id=user_id, site=site).delete()
            logger.info(f"Deleted credentials for user {user_id} on site {site}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting credentials: {str(e)}")
            return False