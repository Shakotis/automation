from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .credential_storage import SecureCredentialStorage
import logging
import time

logger = logging.getLogger(__name__)

class CredentialVerificationService:
    """Service to verify user credentials by attempting login to target sites"""
    
    def __init__(self):
        self.credential_storage = SecureCredentialStorage()
    
    def _setup_driver(self, headless=True):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        return webdriver.Chrome(options=chrome_options)
    
    def verify_blackboard_credentials(self, username, password, url=None):
        """Verify Blackboard credentials"""
        driver = None
        try:
            driver = self._setup_driver()
            
            # Default Blackboard URL if not provided
            if not url:
                url = "https://blackboard.com"
            
            driver.get(url)
            
            # Wait for login form
            wait = WebDriverWait(driver, 10)
            
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
                    username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            for selector in password_selectors:
                try:
                    password_field = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not username_field or not password_field:
                return False, "Could not find login form"
            
            # Enter credentials
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit form
            submit_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "#entry-login"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                    submit_button.click()
                    break
                except NoSuchElementException:
                    continue
            
            # Wait for page to load and check for success indicators
            time.sleep(3)
            
            # Check for common success indicators
            success_indicators = [
                "dashboard",
                "course",
                "home",
                "welcome"
            ]
            
            page_source = driver.page_source.lower()
            
            # Check for error indicators
            error_indicators = [
                "invalid",
                "incorrect",
                "error",
                "failed",
                "denied"
            ]
            
            has_error = any(error in page_source for error in error_indicators)
            has_success = any(success in page_source for success in success_indicators)
            
            if has_error and not has_success:
                return False, "Invalid credentials"
            elif has_success:
                return True, "Login successful"
            else:
                return False, "Unable to determine login status"
                
        except Exception as e:
            logger.error(f"Error verifying Blackboard credentials: {str(e)}")
            return False, f"Verification failed: {str(e)}"
        finally:
            if driver:
                driver.quit()
    
    def verify_canvas_credentials(self, username, password, url=None):
        """Verify Canvas credentials"""
        driver = None
        try:
            driver = self._setup_driver()
            
            if not url:
                url = "https://canvas.instructure.com"
            
            driver.get(url)
            
            wait = WebDriverWait(driver, 10)
            
            # Canvas login selectors
            try:
                username_field = wait.until(EC.presence_of_element_located((By.ID, "pseudonym_session_unique_id")))
                password_field = driver.find_element(By.ID, "pseudonym_session_password")
                
                username_field.clear()
                username_field.send_keys(username)
                password_field.clear()
                password_field.send_keys(password)
                
                submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_button.click()
                
                time.sleep(3)
                
                # Check for Canvas-specific success indicators
                if "dashboard" in driver.current_url.lower() or "courses" in driver.current_url.lower():
                    return True, "Login successful"
                elif "login" in driver.current_url.lower():
                    return False, "Invalid credentials"
                else:
                    return False, "Unable to determine login status"
                    
            except TimeoutException:
                return False, "Login form not found"
                
        except Exception as e:
            logger.error(f"Error verifying Canvas credentials: {str(e)}")
            return False, f"Verification failed: {str(e)}"
        finally:
            if driver:
                driver.quit()
    
    def verify_moodle_credentials(self, username, password, url=None):
        """Verify Moodle credentials"""
        driver = None
        try:
            driver = self._setup_driver()
            
            if not url:
                return False, "Moodle URL is required"
            
            driver.get(url)
            
            wait = WebDriverWait(driver, 10)
            
            # Moodle login selectors
            try:
                username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
                password_field = driver.find_element(By.ID, "password")
                
                username_field.clear()
                username_field.send_keys(username)
                password_field.clear()
                password_field.send_keys(password)
                
                submit_button = driver.find_element(By.ID, "loginbtn")
                submit_button.click()
                
                time.sleep(3)
                
                # Check for Moodle-specific indicators
                page_source = driver.page_source.lower()
                
                if "dashboard" in page_source or "my courses" in page_source:
                    return True, "Login successful"
                elif "invalid login" in page_source or "error" in page_source:
                    return False, "Invalid credentials"
                else:
                    return False, "Unable to determine login status"
                    
            except TimeoutException:
                return False, "Login form not found"
                
        except Exception as e:
            logger.error(f"Error verifying Moodle credentials: {str(e)}")
            return False, f"Verification failed: {str(e)}"
        finally:
            if driver:
                driver.quit()
    
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
        """Verify Manodienynas.lt credentials by attempting actual login"""
        driver = None
        try:
            if not username or not password:
                return False, "Username and password are required"
            
            driver = self._setup_driver()
            
            # Use the provided URL or default to Manodienynas login page
            login_url = url or "https://www.manodienynas.lt/1/lt/public/public/login"
            driver.get(login_url)
            
            wait = WebDriverWait(driver, 15)
            
            # Wait for login form to appear
            try:
                # Look for username field (Manodienynas typically uses username, not email)
                username_selectors = [
                    "input[name='username']",
                    "input[name='user']",
                    "input[name='login']",
                    "#username",
                    "#user",
                    "#login",
                    ".username-input",
                    ".user-input"
                ]
                
                username_field = None
                for selector in username_selectors:
                    try:
                        username_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        break
                    except TimeoutException:
                        continue
                
                if not username_field:
                    return False, "Username field not found on login page"
                
                # Look for password field
                password_selectors = [
                    "input[type='password']",
                    "input[name='password']",
                    "#password",
                    ".password-input"
                ]
                
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if not password_field:
                    return False, "Password field not found on login page"
                
                # Clear and enter credentials
                username_field.clear()
                username_field.send_keys(username)
                time.sleep(0.5)  # Small delay between inputs
                
                password_field.clear()
                password_field.send_keys(password)
                time.sleep(0.5)
                
                # Look for submit button
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button.login-button",
                    "button.submit-button",
                    ".login-form button",
                    "form button",
                    "[value='Prisijungti']",  # Lithuanian for "Login"
                    "[value='LOGIN']"
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if not submit_button:
                    return False, "Submit button not found"
                
                # Click submit and wait for response
                submit_button.click()
                
                # Wait for page to load and check result
                time.sleep(3)
                
                current_url = driver.current_url.lower()
                page_source = driver.page_source.lower()
                
                # Check for successful login indicators
                success_indicators = [
                    "dashboard",
                    "dienynas",     # Lithuanian for "diary"
                    "pagrindinis",  # Lithuanian for "main"
                    "home",
                    "student",
                    "pupil",
                    "mokinys",      # Lithuanian for "student"
                    "logout",
                    "atsijungti",   # Lithuanian for "logout"
                    "prisijungta",  # Lithuanian for "logged in"
                    "sveiki",       # Lithuanian for "welcome"
                ]
                
                # Check for error indicators
                error_indicators = [
                    "invalid",
                    "incorrect",
                    "error",
                    "failed",
                    "denied",
                    "neteisingas",  # Lithuanian for "incorrect"
                    "klaida",       # Lithuanian for "error"
                    "nepavyko",     # Lithuanian for "failed"
                    "neteisingai",  # Lithuanian for "incorrectly"
                    "login",        # If still on login page
                    "prisijungimas" # Lithuanian for "login"
                ]
                
                # Check URL for success patterns
                url_success_patterns = [
                    "dashboard",
                    "home",
                    "main",
                    "dienynas",
                    "student",
                    "pupil"
                ]
                
                has_url_success = any(pattern in current_url for pattern in url_success_patterns)
                has_content_success = any(indicator in page_source for indicator in success_indicators)
                has_error = any(error in page_source for error in error_indicators)
                
                # If URL changed away from login and has success indicators
                if has_url_success or (not "login" in current_url and has_content_success):
                    return True, "Login successful - credentials verified"
                elif has_error or "login" in current_url:
                    return False, "Invalid credentials - login failed"
                else:
                    # Additional check: look for specific elements that indicate successful login
                    try:
                        # Look for elements that typically appear after login
                        post_login_elements = [
                            "[data-testid='user-menu']",
                            ".user-menu",
                            ".logout",
                            ".atsijungti",
                            ".profile",
                            "nav",
                            ".navigation",
                            ".menu",
                            ".header-user"
                        ]
                        
                        for element_selector in post_login_elements:
                            try:
                                driver.find_element(By.CSS_SELECTOR, element_selector)
                                return True, "Login successful - user interface detected"
                            except NoSuchElementException:
                                continue
                        
                        return False, "Unable to determine login status - please check credentials"
                        
                    except Exception:
                        return False, "Unable to verify login status"
                
            except TimeoutException:
                return False, "Login form not found or page took too long to load"
                
        except Exception as e:
            logger.error(f"Error verifying Manodienynas credentials: {str(e)}")
            return False, f"Verification failed: {str(e)}"
        finally:
            if driver:
                driver.quit()
    
    def verify_eduka_credentials(self, username, password, url=None):
        """Verify Eduka.lt credentials by attempting actual login"""
        driver = None
        try:
            if not username or not password:
                return False, "Username and password are required"
            
            driver = self._setup_driver()
            
            # Use the provided URL or default to Eduka auth page
            auth_url = url or "https://eduka.lt/auth"
            driver.get(auth_url)
            
            wait = WebDriverWait(driver, 15)
            
            # Wait for login form to appear
            try:
                # Look for email/username field (Eduka might use email)
                username_selectors = [
                    "input[type='email']",
                    "input[name='email']", 
                    "input[name='username']",
                    "#email",
                    "#username",
                    ".email-input",
                    ".username-input"
                ]
                
                username_field = None
                for selector in username_selectors:
                    try:
                        username_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        break
                    except TimeoutException:
                        continue
                
                if not username_field:
                    return False, "Username/email field not found on login page"
                
                # Look for password field
                password_selectors = [
                    "input[type='password']",
                    "input[name='password']",
                    "#password",
                    ".password-input"
                ]
                
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if not password_field:
                    return False, "Password field not found on login page"
                
                # Clear and enter credentials
                username_field.clear()
                username_field.send_keys(username)
                time.sleep(0.5)  # Small delay between inputs
                
                password_field.clear()
                password_field.send_keys(password)
                time.sleep(0.5)
                
                # Look for submit button
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button.login-button",
                    "button.submit-button",
                    ".login-form button",
                    "form button"
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if not submit_button:
                    return False, "Submit button not found"
                
                # Click submit and wait for response
                submit_button.click()
                
                # Wait for page to load and check result
                time.sleep(3)
                
                current_url = driver.current_url.lower()
                page_source = driver.page_source.lower()
                
                # Check for successful login indicators
                success_indicators = [
                    "dashboard",
                    "student",
                    "my-groups",
                    "profile",
                    "logout",
                    "prisijungta",  # Lithuanian for "logged in"
                    "pagrindinis",  # Lithuanian for "main"
                ]
                
                # Check for error indicators
                error_indicators = [
                    "invalid",
                    "incorrect",
                    "error",
                    "failed",
                    "denied",
                    "neteisingas",  # Lithuanian for "incorrect"
                    "klaida",       # Lithuanian for "error"
                    "nepavyko",     # Lithuanian for "failed"
                ]
                
                # Check URL for success patterns
                url_success_patterns = [
                    "dashboard",
                    "student",
                    "home",
                    "main",
                    "groups"
                ]
                
                has_url_success = any(pattern in current_url for pattern in url_success_patterns)
                has_content_success = any(indicator in page_source for indicator in success_indicators)
                has_error = any(error in page_source for error in error_indicators)
                
                # If URL changed away from auth and has success indicators
                if has_url_success or (not "auth" in current_url and has_content_success):
                    return True, "Login successful - credentials verified"
                elif has_error or "auth" in current_url:
                    return False, "Invalid credentials - login failed"
                else:
                    # Additional check: look for specific elements that indicate successful login
                    try:
                        # Look for elements that typically appear after login
                        post_login_elements = [
                            "[data-testid='user-menu']",
                            ".user-menu",
                            ".logout",
                            ".profile",
                            "nav",
                            ".navigation"
                        ]
                        
                        for element_selector in post_login_elements:
                            try:
                                driver.find_element(By.CSS_SELECTOR, element_selector)
                                return True, "Login successful - user interface detected"
                            except NoSuchElementException:
                                continue
                        
                        return False, "Unable to determine login status - please check credentials"
                        
                    except Exception:
                        return False, "Unable to verify login status"
                
            except TimeoutException:
                return False, "Login form not found or page took too long to load"
                
        except Exception as e:
            logger.error(f"Error verifying Eduka credentials: {str(e)}")
            return False, f"Verification failed: {str(e)}"
        finally:
            if driver:
                driver.quit()