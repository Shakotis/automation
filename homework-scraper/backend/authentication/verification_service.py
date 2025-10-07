# Playwright for browser automation (replaces Selenium)
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import requests

from .credential_storage import SecureCredentialStorage
import logging
import time

logger = logging.getLogger(__name__)

class CredentialVerificationService:
    """Service to verify user credentials by attempting login to target sites"""
    
    def __init__(self):
        self.credential_storage = SecureCredentialStorage()
    
    def _setup_browser_context(self, playwright, headless=True):
        """Setup Playwright browser context with appropriate options"""
        browser = playwright.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        return browser, context
    
    def verify_blackboard_credentials(self, username, password, url=None):
        """Verify Blackboard credentials using Playwright"""
        try:
            with sync_playwright() as p:
                browser, context = self._setup_browser_context(p)
                page = context.new_page()
                
                try:
                    # Default Blackboard URL if not provided
                    if not url:
                        url = "https://blackboard.com"
                    
                    page.goto(url, timeout=30000)
                    
                    # Look for common Blackboard login selectors
                    username_selectors = [
                        "input[name='user_id']",
                        "input[name='username']",
                        "#user_id",
                        "#username"
                    ]
                    
                    password_selectors = [
                        "input[name='password']",
                        "#password"
                    ]
                    
                    username_field = None
                    password_field = None
                    
                    for selector in username_selectors:
                        try:
                            username_field = page.wait_for_selector(selector, timeout=5000)
                            if username_field:
                                break
                        except PlaywrightTimeoutError:
                            continue
                    
                    for selector in password_selectors:
                        try:
                            password_field = page.query_selector(selector)
                            if password_field:
                                break
                        except:
                            continue
                    
                    if not username_field or not password_field:
                        return False, "Could not find login form"
                    
                    # Enter credentials
                    username_field.fill(username)
                    password_field.fill(password)
                    
                    # Submit form
                    submit_selectors = [
                        "input[type='submit']",
                        "button[type='submit']",
                        "#entry-login"
                    ]
                    
                    for selector in submit_selectors:
                        try:
                            submit_button = page.query_selector(selector)
                            if submit_button:
                                submit_button.click()
                                break
                        except:
                            continue
                    
                    # Wait for page to load
                    page.wait_for_timeout(3000)
                    
                    # Check for success/error indicators
                    page_content = page.content().lower()
                    
                    success_indicators = ["dashboard", "course", "home", "welcome"]
                    error_indicators = ["invalid", "incorrect", "error", "failed", "denied"]
                    
                    has_error = any(error in page_content for error in error_indicators)
                    has_success = any(success in page_content for success in success_indicators)
                    
                    if has_error and not has_success:
                        return False, "Invalid credentials"
                    elif has_success:
                        return True, "Login successful"
                    else:
                        return False, "Unable to determine login status"
                        
                finally:
                    browser.close()
                    
        except Exception as e:
            logger.error(f"Error verifying Blackboard credentials: {str(e)}")
            return False, f"Verification failed: {str(e)}"
    
    def verify_canvas_credentials(self, username, password, url=None):
        """Verify Canvas credentials using Playwright"""
        try:
            with sync_playwright() as p:
                browser, context = self._setup_browser_context(p)
                page = context.new_page()
                
                try:
                    if not url:
                        url = "https://canvas.instructure.com"
                    
                    page.goto(url, timeout=30000)
                    
                    # Canvas login selectors
                    try:
                        username_field = page.wait_for_selector("#pseudonym_session_unique_id", timeout=10000)
                        password_field = page.query_selector("#pseudonym_session_password")
                        
                        if not username_field or not password_field:
                            return False, "Login form not found"
                        
                        username_field.fill(username)
                        password_field.fill(password)
                        
                        submit_button = page.query_selector("button[type='submit']")
                        if submit_button:
                            submit_button.click()
                        
                        page.wait_for_timeout(3000)
                        
                        # Check URL for success indicators
                        current_url = page.url.lower()
                        if "dashboard" in current_url or "courses" in current_url:
                            return True, "Login successful"
                        elif "login" in current_url:
                            return False, "Invalid credentials"
                        else:
                            return False, "Unable to determine login status"
                            
                    except PlaywrightTimeoutError:
                        return False, "Login form not found"
                    
                finally:
                    browser.close()
                    
        except Exception as e:
            logger.error(f"Error verifying Canvas credentials: {str(e)}")
            return False, f"Verification failed: {str(e)}"
    
    def verify_moodle_credentials(self, username, password, url=None):
        """Verify Moodle credentials using Playwright"""
        try:
            with sync_playwright() as p:
                browser, context = self._setup_browser_context(p)
                page = context.new_page()
                
                try:
                    if not url:
                        return False, "Moodle URL is required"
                    
                    page.goto(url, timeout=30000)
                    
                    # Moodle login selectors
                    try:
                        username_field = page.wait_for_selector("#username", timeout=10000)
                        password_field = page.query_selector("#password")
                        
                        if not username_field or not password_field:
                            return False, "Login form not found"
                        
                        username_field.fill(username)
                        password_field.fill(password)
                        
                        submit_button = page.query_selector("#loginbtn")
                        if submit_button:
                            submit_button.click()
                        
                        page.wait_for_timeout(3000)
                        
                        # Check for success/error indicators
                        page_content = page.content().lower()
                        
                        if "dashboard" in page_content or "my courses" in page_content:
                            return True, "Login successful"
                        elif "invalid login" in page_content or "error" in page_content:
                            return False, "Invalid credentials"
                        else:
                            return False, "Unable to determine login status"
                            
                    except PlaywrightTimeoutError:
                        return False, "Login form not found"
                    
                finally:
                    browser.close()
                    
        except Exception as e:
            logger.error(f"Error verifying Moodle credentials: {str(e)}")
            return False, f"Verification failed: {str(e)}"
    
    def verify_credentials(self, user_id: int, site: str, custom_url: str = None):
        """Verify credentials for a specific site"""
        try:
            # Get credentials from storage
            credentials = self.credential_storage.get_user_credentials(user_id, site)
            
            if not credentials:
                return False, "Credentials not found"
            
            username = credentials['username']
            password = credentials['password']
            additional_data = credentials.get('additional_data', {})
            
            # Use custom URL if provided, otherwise from additional_data
            url = custom_url or additional_data.get('url')
            
            # Route to appropriate verification method
            if site == 'blackboard':
                success, message = self.verify_blackboard_credentials(username, password, url)
            elif site == 'canvas':
                success, message = self.verify_canvas_credentials(username, password, url)
            elif site == 'moodle':
                success, message = self.verify_moodle_credentials(username, password, url)
            elif site == 'manodienynas':
                success, message = self.verify_manodienynas_credentials(username, password, url)
            elif site == 'eduka':
                success, message = self.verify_eduka_credentials(username, password, url)
            elif site == 'google_classroom':
                # Google Classroom uses OAuth, so this would be different
                success, message = False, "Google Classroom uses OAuth authentication"
            elif site == 'microsoft_teams':
                success, message = False, "Microsoft Teams verification not implemented yet"
            elif site == 'schoology':
                success, message = False, "Schoology verification not implemented yet"
            else:
                success, message = False, f"Verification not supported for {site}"
            
            # Update verification status
            self.credential_storage.update_credential_verification(user_id, site, success)
            
            return success, message
            
        except Exception as e:
            logger.error(f"Error verifying credentials for user {user_id} on site {site}: {str(e)}")
            return False, f"Verification error: {str(e)}"
    
    def verify_manodienynas_credentials(self, username, password, url=None):
        """Verify Manodienynas.lt credentials using fast requests-based login"""
        try:
            if not username or not password:
                return False, "Username and password are required"
            
            logger.info(f"Verifying Manodienynas credentials using requests method...")
            
            # Use the same fast requests-based login from production scraper
            import requests
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # First, visit the login page to establish session
            login_url = url or 'https://www.manodienynas.lt/1/lt/public/public/login'
            response = session.get(login_url)
            
            if response.status_code != 200:
                return False, f"Failed to reach login page (status {response.status_code})"
            
            # Submit login to AJAX endpoint (same as production scraper)
            ajax_login_url = 'https://www.manodienynas.lt/1/lt/ajax/user/login'
            login_data = {
                'username': username,
                'password': password,
            }
            
            login_response = session.post(ajax_login_url, data=login_data)
            
            if login_response.status_code != 200:
                return False, f"Login request failed (status {login_response.status_code})"
            
            # Check response for success/failure
            try:
                response_data = login_response.json()
                
                # Check if login was successful (no error message)
                if response_data.get('success') == False or response_data.get('error'):
                    error_msg = response_data.get('message', 'Invalid credentials')
                    return False, f"Login failed: {error_msg}"
                
                # If we got here, login was successful
                logger.info("Manodienynas credentials verified successfully")
                return True, "Credentials verified successfully"
                
            except ValueError:
                # Response wasn't JSON, check if we got redirected or got HTML
                response_text = login_response.text.lower()
                
                # Check for error indicators in response
                if 'error' in response_text or 'invalid' in response_text:
                    return False, "Invalid username or password"
                
                # If no errors, assume success
                return True, "Credentials verified successfully"
            
        except requests.RequestException as e:
            logger.error(f"Network error during Manodienynas verification: {str(e)}")
            return False, f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Error verifying Manodienynas credentials: {str(e)}")
            return False, f"Verification failed: {str(e)}"
    
    def verify_eduka_credentials(self, username, password, url=None):
        """Verify Eduka.lt credentials using Playwright (same as production scraper)"""
        try:
            if not username or not password:
                return False, "Username and password are required"
            
            logger.info(f"Verifying Eduka credentials using Playwright...")
            
            # Use the production Playwright scraper for verification
            # This ensures 100% consistency with scraping
            from scraper.eduka_playwright import EdukaPlaywrightScraper
            
            # Create a temporary user object just for verification
            class TempUser:
                def __init__(self, username, password):
                    self.username = username
                    self.password = password
                    
                def get_eduka_credentials(self):
                    return {
                        'username': username,
                        'password': password
                    }
            
            temp_user = TempUser(username, password)
            
            try:
                # Use the production scraper with context manager
                with EdukaPlaywrightScraper(temp_user) as scraper:
                    # Just try to login (don't scrape)
                    success = scraper.login(username, password)
                    
                    if success:
                        logger.info("Eduka credentials verified successfully")
                        return True, "Credentials verified successfully"
                    else:
                        logger.warning("Eduka login failed - invalid credentials")
                        return False, "Invalid username or password"
                        
            except Exception as e:
                logger.error(f"Error during Eduka verification: {str(e)}")
                return False, f"Verification failed: {str(e)}"
            
        except ImportError:
            logger.error("Playwright scraper not available")
            return False, "Eduka verification requires Playwright. Run: pip install playwright && playwright install chromium"
        except Exception as e:
            logger.error(f"Error verifying Eduka credentials: {str(e)}")
            return False, f"Verification failed: {str(e)}"