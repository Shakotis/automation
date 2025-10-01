"""
Session management for authenticated scraping sessions
"""
import pickle
import os
import time
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging

logger = logging.getLogger(__name__)

class ScrapingSessionManager:
    """Manage authenticated Selenium sessions for scraping"""
    
    def __init__(self, user_id, site):
        self.user_id = user_id
        self.site = site
        self.session_dir = os.path.join(settings.BASE_DIR, 'sessions')
        self.session_file = os.path.join(self.session_dir, f'session_{user_id}_{site}.pkl')
        os.makedirs(self.session_dir, exist_ok=True)
    
    def save_session(self, driver):
        """Save the current session cookies and state"""
        try:
            session_data = {
                'cookies': driver.get_cookies(),
                'current_url': driver.current_url,
                'timestamp': time.time(),
                'user_agent': driver.execute_script("return navigator.userAgent;")
            }
            
            with open(self.session_file, 'wb') as f:
                pickle.dump(session_data, f)
            
            logger.info(f"Session saved for user {self.user_id} on {self.site}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False
    
    def load_session(self, driver):
        """Load a saved session into the driver"""
        try:
            if not os.path.exists(self.session_file):
                return False
            
            with open(self.session_file, 'rb') as f:
                session_data = pickle.load(f)
            
            # Check if session is not too old (24 hours)
            if time.time() - session_data['timestamp'] > 24 * 3600:
                self.clear_session()
                return False
            
            # Navigate to a base page first (required for setting cookies)
            base_urls = {
                'eduka': 'https://eduka.lt',
                'manodienynas': 'https://www.manodienynas.lt'
            }
            
            base_url = base_urls.get(self.site, 'https://eduka.lt')
            driver.get(base_url)
            
            # Restore cookies
            for cookie in session_data['cookies']:
                try:
                    driver.add_cookie(cookie)
                except Exception as cookie_error:
                    logger.warning(f"Failed to add cookie: {cookie_error}")
            
            # Navigate back to the saved URL
            if session_data['current_url']:
                driver.get(session_data['current_url'])
            
            logger.info(f"Session loaded for user {self.user_id} on {self.site}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            self.clear_session()
            return False
    
    def clear_session(self):
        """Clear the saved session"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            logger.info(f"Session cleared for user {self.user_id} on {self.site}")
        except Exception as e:
            logger.warning(f"Failed to clear session: {e}")
    
    def is_session_valid(self, driver):
        """Check if the current session is still valid"""
        try:
            # Check if we're still logged in by looking for common auth indicators
            current_url = driver.current_url.lower()
            page_source = driver.page_source.lower()
            
            # If we're back on the auth page, session is invalid
            if 'auth' in current_url or 'login' in current_url:
                return False
            
            # Look for indicators of being logged in
            auth_indicators = [
                'logout',
                'profile',
                'dashboard',
                'student',
                'prisijungta',  # Lithuanian
                'atsijungti'    # Lithuanian for logout
            ]
            
            return any(indicator in page_source for indicator in auth_indicators)
            
        except Exception as e:
            logger.error(f"Failed to check session validity: {e}")
            return False
    
    def get_authenticated_driver(self, force_new=False):
        """Get a driver with an authenticated session"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        if not force_new and self.load_session(driver):
            # Check if session is still valid
            if self.is_session_valid(driver):
                return driver, True  # Session loaded successfully
            else:
                self.clear_session()
        
        return driver, False  # New session needed
    
    @staticmethod
    def clear_all_sessions(user_id):
        """Clear all sessions for a user"""
        try:
            session_dir = os.path.join(settings.BASE_DIR, 'sessions')
            if os.path.exists(session_dir):
                for filename in os.listdir(session_dir):
                    if filename.startswith(f'session_{user_id}_'):
                        os.remove(os.path.join(session_dir, filename))
            logger.info(f"All sessions cleared for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to clear all sessions for user {user_id}: {e}")