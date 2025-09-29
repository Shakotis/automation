from supabase import create_client, Client
from django.conf import settings
from django.contrib.auth.models import User
from scraper.models import ScrapedHomework, UserScrapingPreferences
from authentication.models import GoogleOAuth
import json
from datetime import datetime

class SupabaseService:
    """Service for Supabase integration"""
    
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.supabase: Client = create_client(self.url, self.key)
    
    def sync_user_data(self, user):
        """Sync user data to Supabase"""
        try:
            # Sync user profile
            user_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
            
            self.supabase.table('users').upsert(user_data).execute()
            
            # Sync user preferences
            try:
                preferences = UserScrapingPreferences.objects.get(user=user)
                preferences_data = {
                    'user_id': user.id,
                    'enable_manodienynas': preferences.enable_manodienynas,
                    'enable_eduka': preferences.enable_eduka,
                    'auto_sync_to_google_tasks': preferences.auto_sync_to_google_tasks,
                    'scraping_frequency_hours': preferences.scraping_frequency_hours,
                    'last_scraped_manodienynas': preferences.last_scraped_manodienynas.isoformat() if preferences.last_scraped_manodienynas else None,
                    'last_scraped_eduka': preferences.last_scraped_eduka.isoformat() if preferences.last_scraped_eduka else None,
                }
                
                self.supabase.table('user_preferences').upsert(preferences_data).execute()
            except UserScrapingPreferences.DoesNotExist:
                pass
            
            return True
            
        except Exception as e:
            print(f"Error syncing user data to Supabase: {e}")
            return False
    
    def sync_homework_data(self, user):
        """Sync homework data to Supabase"""
        try:
            homework_qs = ScrapedHomework.objects.filter(user=user)
            
            homework_data = []
            for hw in homework_qs:
                homework_data.append({
                    'id': hw.id,
                    'user_id': user.id,
                    'site': hw.site,
                    'title': hw.title,
                    'description': hw.description,
                    'due_date': hw.due_date.isoformat() if hw.due_date else None,
                    'subject': hw.subject,
                    'url': hw.url,
                    'scraped_at': hw.scraped_at.isoformat(),
                    'synced_to_google_tasks': hw.synced_to_google_tasks,
                    'google_task_id': hw.google_task_id,
                })
            
            if homework_data:
                self.supabase.table('scraped_homework').upsert(homework_data).execute()
            
            return True
            
        except Exception as e:
            print(f"Error syncing homework data to Supabase: {e}")
            return False
    
    def backup_oauth_tokens(self, user):
        """Backup OAuth tokens to Supabase (encrypted)"""
        try:
            oauth = GoogleOAuth.objects.get(user=user)
            
            # Note: In production, tokens should be encrypted before storing
            oauth_data = {
                'user_id': user.id,
                'token_expiry': oauth.token_expiry.isoformat(),
                'created_at': oauth.created_at.isoformat(),
                'updated_at': oauth.updated_at.isoformat(),
                # Don't store actual tokens in this example for security
                'has_tokens': True,
            }
            
            self.supabase.table('oauth_tokens').upsert(oauth_data).execute()
            return True
            
        except GoogleOAuth.DoesNotExist:
            return False
        except Exception as e:
            print(f"Error backing up OAuth tokens: {e}")
            return False
    
    def get_user_analytics(self, user):
        """Get user analytics from Supabase"""
        try:
            # Get homework count by site
            homework_stats = self.supabase.table('scraped_homework').select('site').eq('user_id', user.id).execute()
            
            site_counts = {}
            for item in homework_stats.data:
                site = item['site']
                site_counts[site] = site_counts.get(site, 0) + 1
            
            # Get sync statistics
            sync_stats = self.supabase.table('scraped_homework').select('synced_to_google_tasks').eq('user_id', user.id).execute()
            
            synced_count = sum(1 for item in sync_stats.data if item['synced_to_google_tasks'])
            total_count = len(sync_stats.data)
            
            return {
                'site_counts': site_counts,
                'sync_stats': {
                    'synced': synced_count,
                    'total': total_count,
                    'percentage': (synced_count / total_count * 100) if total_count > 0 else 0
                }
            }
            
        except Exception as e:
            print(f"Error getting user analytics: {e}")
            return {}
    
    def create_tables(self):
        """Create necessary tables in Supabase (run once during setup)"""
        # This would typically be done through Supabase dashboard or SQL scripts
        # Here's the SQL structure you would need:
        
        sql_scripts = {
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    first_name VARCHAR(150),
                    last_name VARCHAR(150),
                    date_joined TIMESTAMP WITH TIME ZONE,
                    last_login TIMESTAMP WITH TIME ZONE
                );
            """,
            'user_preferences': """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER PRIMARY KEY REFERENCES users(id),
                    enable_manodienynas BOOLEAN DEFAULT TRUE,
                    enable_eduka BOOLEAN DEFAULT TRUE,
                    auto_sync_to_google_tasks BOOLEAN DEFAULT TRUE,
                    scraping_frequency_hours INTEGER DEFAULT 6,
                    last_scraped_manodienynas TIMESTAMP WITH TIME ZONE,
                    last_scraped_eduka TIMESTAMP WITH TIME ZONE
                );
            """,
            'scraped_homework': """
                CREATE TABLE IF NOT EXISTS scraped_homework (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    site VARCHAR(20) NOT NULL,
                    title VARCHAR(500) NOT NULL,
                    description TEXT,
                    due_date TIMESTAMP WITH TIME ZONE,
                    subject VARCHAR(200),
                    url VARCHAR(1000),
                    scraped_at TIMESTAMP WITH TIME ZONE,
                    synced_to_google_tasks BOOLEAN DEFAULT FALSE,
                    google_task_id VARCHAR(200),
                    UNIQUE(user_id, site, title, due_date)
                );
            """,
            'oauth_tokens': """
                CREATE TABLE IF NOT EXISTS oauth_tokens (
                    user_id INTEGER PRIMARY KEY REFERENCES users(id),
                    token_expiry TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE,
                    updated_at TIMESTAMP WITH TIME ZONE,
                    has_tokens BOOLEAN DEFAULT FALSE
                );
            """
        }
        
        return sql_scripts