from supabase import create_client, Client
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    """Service for Supabase user management and synchronization"""
    
    def __init__(self):
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("Supabase URL and KEY must be configured in settings")
        
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_KEY
        )
    
    def sync_user_to_supabase(self, user: User):
        """Sync Django user to Supabase"""
        try:
            user_data = {
                'django_user_id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'is_active': user.is_active,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'updated_at': datetime.now().isoformat()
            }
            
            # Check if user already exists in Supabase
            existing_user = self.supabase.table('users').select('*').eq('django_user_id', user.id).execute()
            
            if existing_user.data:
                # Update existing user
                result = self.supabase.table('users').update(user_data).eq('django_user_id', user.id).execute()
                logger.info(f"Updated user {user.email} in Supabase")
            else:
                # Insert new user
                user_data['created_at'] = datetime.now().isoformat()
                result = self.supabase.table('users').insert(user_data).execute()
                logger.info(f"Created user {user.email} in Supabase")
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error syncing user {user.email} to Supabase: {str(e)}")
            raise
    
    def get_user_profile(self, user_id: int):
        """Get user profile from Supabase"""
        try:
            result = self.supabase.table('users').select('*').eq('django_user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user profile from Supabase: {str(e)}")
            return None
    
    def update_user_preferences(self, user_id: int, preferences: dict):
        """Update user preferences in Supabase"""
        try:
            update_data = {
                'preferences': preferences,
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('users').update(update_data).eq('django_user_id', user_id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error updating user preferences in Supabase: {str(e)}")
            raise
    
    def save_user_site_selections(self, user_id: int, selected_sites: list):
        """Save user's selected sites for scraping"""
        try:
            # Delete existing selections
            self.supabase.table('user_site_selections').delete().eq('user_id', user_id).execute()
            
            # Insert new selections
            for site in selected_sites:
                selection_data = {
                    'user_id': user_id,
                    'site_name': site,
                    'created_at': datetime.now().isoformat(),
                    'is_active': True
                }
                self.supabase.table('user_site_selections').insert(selection_data).execute()
            
            logger.info(f"Saved site selections for user {user_id}: {selected_sites}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving site selections for user {user_id}: {str(e)}")
            raise
    
    def get_user_site_selections(self, user_id: int):
        """Get user's selected sites"""
        try:
            result = self.supabase.table('user_site_selections').select('*').eq('user_id', user_id).eq('is_active', True).execute()
            return [item['site_name'] for item in result.data]
        except Exception as e:
            logger.error(f"Error getting site selections for user {user_id}: {str(e)}")
            return []
    
    def create_supabase_tables(self):
        """Create necessary tables in Supabase (run this once during setup)"""
        # Note: This should be run manually in Supabase SQL editor
        sql_commands = """
        -- Create users table
        CREATE TABLE IF NOT EXISTS users (
            id BIGSERIAL PRIMARY KEY,
            django_user_id INTEGER UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            first_name VARCHAR(150),
            last_name VARCHAR(150),
            username VARCHAR(150),
            is_active BOOLEAN DEFAULT true,
            preferences JSONB DEFAULT '{}',
            date_joined TIMESTAMP WITH TIME ZONE,
            last_login TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create user_site_selections table
        CREATE TABLE IF NOT EXISTS user_site_selections (
            id BIGSERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(django_user_id) ON DELETE CASCADE,
            site_name VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_users_django_id ON users(django_user_id);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_site_selections_user ON user_site_selections(user_id);
        """
        
        return sql_commands