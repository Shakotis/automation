"""
Production-ready Selenium configuration and session management
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from threading import Lock
from datetime import datetime, timedelta
from typing import Dict, Optional
import os


class ProductionSeleniumConfig:
    """Production-optimized Selenium configuration"""
    
    @staticmethod
    def get_chrome_options(headless: bool = True) -> Options:
        """
        Get production-ready Chrome options
        
        Args:
            headless: Whether to run in headless mode (default: True for production)
        """
        chrome_options = Options()
        
        # Headless mode (CRITICAL for production)
        if headless or os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true':
            chrome_options.add_argument('--headless=new')
        
        # Security & stability
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # Performance optimizations
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # Don't load images
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument('--disable-software-rasterizer')
        
        # Window size
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Anti-detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Reduce logging noise
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        return chrome_options
    
    @staticmethod
    def create_driver(headless: bool = True) -> webdriver.Chrome:
        """
        Create a production-ready Chrome WebDriver
        
        Args:
            headless: Whether to run in headless mode
            
        Returns:
            Configured Chrome WebDriver instance
        """
        options = ProductionSeleniumConfig.get_chrome_options(headless)
        driver = webdriver.Chrome(options=options)
        
        # Set timeouts
        driver.set_page_load_timeout(30)  # 30 seconds max for page load
        driver.set_script_timeout(30)  # 30 seconds max for scripts
        driver.implicitly_wait(10)  # 10 seconds default wait for elements
        
        return driver


class SeleniumSessionPool:
    """
    Thread-safe session pool for managing Selenium WebDriver instances
    
    Benefits:
    - Reuses browser sessions (faster than creating new ones)
    - Limits concurrent sessions (prevents memory exhaustion)
    - Automatically cleans up expired sessions
    - Thread-safe for concurrent access
    """
    
    def __init__(self, max_sessions: int = 5, session_timeout: int = 600):
        """
        Initialize the session pool
        
        Args:
            max_sessions: Maximum number of concurrent sessions
            session_timeout: Session timeout in seconds (default: 10 minutes)
        """
        self.sessions: Dict[str, dict] = {}
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self.pool_lock = Lock()
        print(f"Selenium pool initialized: max_sessions={max_sessions}, timeout={session_timeout}s")
    
    def get_session(self, user_id: str, headless: bool = True) -> webdriver.Chrome:
        """
        Get or create a Selenium session for a user
        
        Args:
            user_id: Unique identifier for the user
            headless: Whether to run in headless mode
            
        Returns:
            Chrome WebDriver instance
        """
        with self.pool_lock:
            # Clean up expired sessions first
            self._cleanup_expired()
            
            # Check if user already has an active session
            if user_id in self.sessions:
                session = self.sessions[user_id]
                cutoff_time = datetime.now() - timedelta(seconds=self.session_timeout)
                
                if session['last_used'] > cutoff_time:
                    # Session is still valid, update last used time
                    session['last_used'] = datetime.now()
                    print(f"Reusing existing Selenium session for user {user_id}")
                    return session['driver']
                else:
                    # Session expired, close it
                    print(f"Session expired for user {user_id}, creating new one")
                    self._close_session(user_id)
            
            # Need to create a new session
            # First check if we're at capacity
            if len(self.sessions) >= self.max_sessions:
                # Close the oldest session
                oldest_user = min(
                    self.sessions.items(),
                    key=lambda x: x[1]['last_used']
                )[0]
                print(f"Pool at capacity, closing oldest session for user {oldest_user}")
                self._close_session(oldest_user)
            
            # Create new driver
            print(f"Creating new Selenium session for user {user_id}")
            driver = ProductionSeleniumConfig.create_driver(headless=headless)
            
            self.sessions[user_id] = {
                'driver': driver,
                'last_used': datetime.now(),
                'created_at': datetime.now()
            }
            
            print(f"Active sessions: {len(self.sessions)}/{self.max_sessions}")
            return driver
    
    def release_session(self, user_id: str):
        """
        Mark session as available (updates last used time)
        
        Args:
            user_id: User identifier
        """
        with self.pool_lock:
            if user_id in self.sessions:
                self.sessions[user_id]['last_used'] = datetime.now()
                print(f"Session released for user {user_id}")
    
    def close_session(self, user_id: str):
        """
        Explicitly close a user's session
        
        Args:
            user_id: User identifier
        """
        with self.pool_lock:
            self._close_session(user_id)
    
    def _close_session(self, user_id: str):
        """Internal method to close a session (not thread-safe, must be called with lock)"""
        if user_id in self.sessions:
            try:
                self.sessions[user_id]['driver'].quit()
                print(f"Closed Selenium session for user {user_id}")
            except Exception as e:
                print(f"Error closing session for user {user_id}: {e}")
            finally:
                del self.sessions[user_id]
    
    def _cleanup_expired(self):
        """Remove expired sessions (not thread-safe, must be called with lock)"""
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=self.session_timeout)
        
        expired_users = [
            user_id for user_id, session in self.sessions.items()
            if session['last_used'] < cutoff_time
        ]
        
        for user_id in expired_users:
            print(f"Cleaning up expired session for user {user_id}")
            self._close_session(user_id)
    
    def close_all(self):
        """Close all sessions (useful for shutdown)"""
        with self.pool_lock:
            print(f"Closing all {len(self.sessions)} Selenium sessions")
            for user_id in list(self.sessions.keys()):
                self._close_session(user_id)
    
    def get_stats(self) -> dict:
        """Get pool statistics"""
        with self.pool_lock:
            return {
                'active_sessions': len(self.sessions),
                'max_sessions': self.max_sessions,
                'session_timeout': self.session_timeout,
                'users': list(self.sessions.keys())
            }


# Global singleton instance
# This will be shared across all requests
_selenium_pool: Optional[SeleniumSessionPool] = None


def get_selenium_pool(max_sessions: int = 5, session_timeout: int = 600) -> SeleniumSessionPool:
    """
    Get the global Selenium session pool (singleton pattern)
    
    Args:
        max_sessions: Maximum concurrent sessions (only used on first call)
        session_timeout: Session timeout in seconds (only used on first call)
        
    Returns:
        SeleniumSessionPool instance
    """
    global _selenium_pool
    if _selenium_pool is None:
        _selenium_pool = SeleniumSessionPool(
            max_sessions=max_sessions,
            session_timeout=session_timeout
        )
    return _selenium_pool


# Convenience function for scraping with automatic cleanup
def scrape_with_selenium(user_id: str, scraping_func, *args, **kwargs):
    """
    Execute a scraping function with automatic session management
    
    Args:
        user_id: User identifier
        scraping_func: Function that takes (driver, *args, **kwargs) and returns results
        *args, **kwargs: Arguments to pass to scraping_func
        
    Returns:
        Results from scraping_func
        
    Example:
        def my_scraper(driver, url):
            driver.get(url)
            return driver.page_source
        
        result = scrape_with_selenium('user123', my_scraper, 'https://example.com')
    """
    pool = get_selenium_pool()
    driver = None
    
    try:
        # Get session from pool
        driver = pool.get_session(user_id)
        
        # Execute scraping function
        result = scraping_func(driver, *args, **kwargs)
        
        # Mark session as available
        pool.release_session(user_id)
        
        return result
        
    except Exception as e:
        print(f"Scraping error for user {user_id}: {e}")
        # On error, close the session (it might be in bad state)
        if driver:
            pool.close_session(user_id)
        raise


# Usage example
if __name__ == "__main__":
    # Example 1: Direct usage
    pool = get_selenium_pool(max_sessions=3, session_timeout=300)
    
    try:
        driver = pool.get_session('user123')
        driver.get('https://www.google.com')
        print(f"Page title: {driver.title}")
        pool.release_session('user123')
    finally:
        pool.close_all()
    
    # Example 2: Using convenience function
    def scrape_google(driver):
        driver.get('https://www.google.com')
        return driver.title
    
    title = scrape_with_selenium('user456', scrape_google)
    print(f"Title: {title}")
