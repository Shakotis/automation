import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.utils import timezone
from datetime import datetime
import re
import time
from .models import ScrapedHomework, UserScrapingPreferences

class BaseScraper:
    """Base class for web scrapers"""
    
    def __init__(self, user):
        self.user = user
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_selenium_driver(self):
        """Setup Chrome driver for Selenium"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        return webdriver.Chrome(options=chrome_options)
    
    def parse_date(self, date_str):
        """Parse Lithuanian date string to datetime"""
        if not date_str:
            return None
        
        # Common Lithuanian date patterns
        patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}.\d{2}.\d{4})',  # DD.MM.YYYY
            r'(\d{2}/\d{2}/\d{4})',  # DD/MM/YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    if '-' in match.group(1):
                        return datetime.strptime(match.group(1), '%Y-%m-%d')
                    elif '.' in match.group(1):
                        return datetime.strptime(match.group(1), '%d.%m.%Y')
                    elif '/' in match.group(1):
                        return datetime.strptime(match.group(1), '%d/%m/%Y')
                except ValueError:
                    continue
        
        return None

class ManodienynasScaper(BaseScraper):
    """Scraper for manodienynas.lt"""
    
    def __init__(self, user):
        super().__init__(user)
        self.base_url = 'https://www.manodienynas.lt'
        self.login_url = 'https://www.manodienynas.lt/1/lt/public/public/login'
        self.homework_url = 'https://www.manodienynas.lt/1/lt/page/classhomework/home_work'
        self.exam_dates_url = 'https://www.manodienynas.lt/1/lt/page/control_work/dates_pupil'
        self.driver = None
        self.is_logged_in = False
        
        # Import session manager
        from authentication.session_manager import ScrapingSessionManager
        self.session_manager = ScrapingSessionManager(user.id, 'manodienynas')
    
    def login(self, username, password):
        """Login to Manodienynas using credentials"""
        try:
            if not self.driver:
                self.driver = self.get_selenium_driver()
            
            self.driver.get(self.login_url)
            
            wait = WebDriverWait(self.driver, 15)
            
            # Look for username field
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
                except:
                    continue
            
            if not username_field:
                raise Exception("Username field not found")
            
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
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not password_field:
                raise Exception("Password field not found")
            
            # Enter credentials
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(0.5)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(0.5)
            
            # Find and click submit button
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
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not submit_button:
                raise Exception("Submit button not found")
            
            submit_button.click()
            time.sleep(3)
            
            # Verify login success
            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()
            
            # Check for success indicators
            success_indicators = [
                "dashboard", "dienynas", "pagrindinis", "home", "student", 
                "pupil", "mokinys", "logout", "atsijungti", "prisijungta"
            ]
            
            has_success = any(indicator in page_source or indicator in current_url for indicator in success_indicators)
            
            if has_success and "login" not in current_url:
                self.is_logged_in = True
                # Save session for future use
                self.session_manager.save_session(self.driver)
                return True
            else:
                raise Exception("Login failed - authentication unsuccessful")
                
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def scrape_homework(self):
        """Scrape homework from manodienynas.lt using session management"""
        homework_list = []
        
        try:
            # Get user credentials from the credential storage
            from authentication.credential_storage import SecureCredentialStorage
            credential_storage = SecureCredentialStorage()
            credentials = credential_storage.get_user_credentials(self.user.id, 'manodienynas')
            
            if not credentials:
                print("No Manodienynas credentials found for user")
                return homework_list
            
            if not credentials.get('is_verified', False):
                print("Manodienynas credentials not verified - please verify them first")
                return homework_list
            
            username = credentials['username']
            password = credentials['password']
            
            # Try to get an authenticated driver (with existing session)
            self.driver, session_loaded = self.session_manager.get_authenticated_driver()
            
            if session_loaded:
                print("Using existing authenticated session")
                self.is_logged_in = True
            else:
                print("No valid session found, logging in...")
                # Login to Manodienynas
                if not self.login(username, password):
                    print("Failed to login to Manodienynas")
                    return homework_list
            
            # Navigate to homework section
            try:
                self.driver.get(self.homework_url)
                time.sleep(3)
                
                # Check if we're still authenticated after navigation
                if not self.session_manager.is_session_valid(self.driver):
                    print("Session expired, attempting re-login...")
                    self.session_manager.clear_session()
                    if not self.login(username, password):
                        print("Re-login failed")
                        return homework_list
                    self.driver.get(self.homework_url)
                    time.sleep(3)
                
                # Look for homework content
                homework_elements = []
                
                # Common selectors for homework items in Manodienynas
                homework_selectors = [
                    ".homework-item",
                    ".assignment",
                    ".task",
                    ".work-item",
                    "tr.homework",
                    "tr.assignment",
                    ".homework-row",
                    ".table-row",
                    "tbody tr"
                ]
                
                for selector in homework_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            homework_elements.extend(elements)
                            break
                    except:
                        continue
                
                # If no specific homework elements found, look for table content
                if not homework_elements:
                    content_selectors = [
                        ".content table tr",
                        ".main-content tr",
                        ".homework-table tr",
                        "table tr",
                        ".data-table tr"
                    ]
                    
                    for selector in content_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if len(elements) > 1:  # Skip header row
                                homework_elements.extend(elements[1:])  # Skip first (header) row
                                break
                        except:
                            continue
                
                # Parse homework from found elements
                for element in homework_elements[:10]:  # Limit to first 10 items
                    try:
                        # Extract text content from the element
                        element_text = element.text.strip()
                        
                        if not element_text or len(element_text) < 10:
                            continue
                        
                        # Try to find title in various ways
                        title = ""
                        try:
                            # Look for specific title elements
                            title_selectors = ["td:first-child", ".title", ".subject", "strong", "b"]
                            for sel in title_selectors:
                                try:
                                    title_elem = element.find_element(By.CSS_SELECTOR, sel)
                                    title = title_elem.text.strip()
                                    if title:
                                        break
                                except:
                                    continue
                            
                            # If no specific title found, use first meaningful text
                            if not title:
                                text_parts = element_text.split('\n')
                                title = text_parts[0] if text_parts else "Namų darbai"
                                
                        except:
                            title = "Manodienynas namų darbai"
                        
                        # Look for description
                        description = ""
                        try:
                            desc_selectors = [".description", "td:nth-child(2)", ".content"]
                            for sel in desc_selectors:
                                try:
                                    desc_elem = element.find_element(By.CSS_SELECTOR, sel)
                                    description = desc_elem.text.strip()
                                    if description:
                                        break
                                except:
                                    continue
                            
                            if not description:
                                # Use remaining text as description
                                text_parts = element_text.split('\n')
                                description = '\n'.join(text_parts[1:]) if len(text_parts) > 1 else "Namų darbų aprašymas"
                                
                        except:
                            description = "Detalus aprašymas Manodienynas platformoje"
                        
                        # Look for due date
                        due_date = timezone.now() + timezone.timedelta(days=7)  # Default
                        try:
                            date_selectors = [".due-date", ".deadline", ".date", "td:last-child", ".date-column"]
                            for sel in date_selectors:
                                try:
                                    date_elem = element.find_element(By.CSS_SELECTOR, sel)
                                    date_text = date_elem.text.strip()
                                    parsed_date = self.parse_date(date_text)
                                    if parsed_date:
                                        due_date = parsed_date
                                        break
                                except:
                                    continue
                        except:
                            pass
                        
                        # Look for subject
                        subject = "Manodienynas"
                        try:
                            subject_selectors = [".subject", ".course", ".class", "td:nth-child(1)"]
                            for sel in subject_selectors:
                                try:
                                    subject_elem = element.find_element(By.CSS_SELECTOR, sel)
                                    subject_text = subject_elem.text.strip()
                                    if subject_text and len(subject_text) < 50:  # Reasonable subject length
                                        subject = subject_text
                                        break
                                except:
                                    continue
                        except:
                            pass
                        
                        # Create homework entry
                        homework_entry = {
                            'title': title[:100],  # Limit title length
                            'description': description[:500],  # Limit description length
                            'due_date': due_date,
                            'subject': subject,
                            'url': self.driver.current_url,
                            'site': 'manodienynas'
                        }
                        
                        homework_list.append(homework_entry)
                        
                    except Exception as e:
                        print(f"Error parsing homework element: {e}")
                        continue
                
                # If still no homework found, create a sample entry to indicate successful login
                if not homework_list:
                    homework_list = [{
                        'title': 'Manodienynas prisijungimas sėkmingas',
                        'description': 'Sėkmingai prisijungta prie Manodienynas platformos. Namų darbų nerasta arba jie gali būti kitoje skiltyje.',
                        'due_date': timezone.now() + timezone.timedelta(days=1),
                        'subject': 'Sistema',
                        'url': self.driver.current_url,
                        'site': 'manodienynas'
                    }]
                
            except Exception as e:
                print(f"Error navigating Manodienynas pages: {e}")
                # Still return at least one entry to show login was successful
                homework_list = [{
                    'title': 'Manodienynas prisijungimas patvirtintas',
                    'description': f'Sėkmingai prisijungta prie Manodienynas, bet kilo navigacijos problema: {str(e)}',
                    'due_date': timezone.now() + timezone.timedelta(days=1),
                    'subject': 'Sistema',
                    'url': self.login_url,
                    'site': 'manodienynas'
                }]
            
        except Exception as e:
            print(f"Error scraping manodienynas: {e}")
        finally:
            # Clean up driver (but don't clear session - it's saved)
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
                self.is_logged_in = False
        
        return homework_list

class EdukaScraper(BaseScraper):
    """Scraper for eduka.lt"""
    
    def __init__(self, user):
        super().__init__(user)
        self.base_url = 'https://eduka.lt'
        self.auth_url = 'https://eduka.lt/auth'
        self.groups_url = 'https://eduka.lt/student/my-groups'
        self.assignments_base_url = 'https://eduka.lt/fe/student/my-groups'
        self.driver = None
        self.is_logged_in = False
        
        # Import session manager
        from authentication.session_manager import ScrapingSessionManager
        self.session_manager = ScrapingSessionManager(user.id, 'eduka')
    
    def login(self, username, password):
        """Login to Eduka using credentials"""
        try:
            if not self.driver:
                self.driver = self.get_selenium_driver()
            
            self.driver.get(self.auth_url)
            
            wait = WebDriverWait(self.driver, 15)
            
            # Look for email/username field
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
                except:
                    continue
            
            if not username_field:
                raise Exception("Username/email field not found")
            
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
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not password_field:
                raise Exception("Password field not found")
            
            # Enter credentials
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(0.5)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(0.5)
            
            # Find and click submit button
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
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not submit_button:
                raise Exception("Submit button not found")
            
            submit_button.click()
            time.sleep(3)
            
            # Verify login success
            current_url = self.driver.current_url.lower()
            if "auth" not in current_url or "dashboard" in current_url or "student" in current_url:
                self.is_logged_in = True
                # Save session for future use
                self.session_manager.save_session(self.driver)
                return True
            else:
                raise Exception("Login failed - still on auth page")
                
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def scrape_homework(self):
        """Scrape homework from eduka.lt using session management"""
        homework_list = []
        
        try:
            # Get user credentials from the credential storage
            from authentication.credential_storage import SecureCredentialStorage
            credential_storage = SecureCredentialStorage()
            credentials = credential_storage.get_user_credentials(self.user.id, 'eduka')
            
            if not credentials:
                print("No Eduka credentials found for user")
                return homework_list
            
            if not credentials.get('is_verified', False):
                print("Eduka credentials not verified - please verify them first")
                return homework_list
            
            username = credentials['username']
            password = credentials['password']
            
            # Try to get an authenticated driver (with existing session)
            self.driver, session_loaded = self.session_manager.get_authenticated_driver()
            
            if session_loaded:
                print("Using existing authenticated session")
                self.is_logged_in = True
            else:
                print("No valid session found, logging in...")
                # Login to Eduka
                if not self.login(username, password):
                    print("Failed to login to Eduka")
                    return homework_list
            
            # Navigate to student groups/homework section
            try:
                self.driver.get(self.groups_url)
                time.sleep(3)
                
                # Check if we're still authenticated after navigation
                if not self.session_manager.is_session_valid(self.driver):
                    print("Session expired, attempting re-login...")
                    self.session_manager.clear_session()
                    if not self.login(username, password):
                        print("Re-login failed")
                        return homework_list
                    self.driver.get(self.groups_url)
                    time.sleep(3)
                
                # Look for homework/assignments content
                homework_elements = []
                
                # Common selectors for homework items
                homework_selectors = [
                    ".assignment",
                    ".homework",
                    ".task",
                    ".activity",
                    "[data-testid*='assignment']",
                    "[data-testid*='homework']",
                    ".homework-item",
                    ".assignment-item"
                ]
                
                for selector in homework_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            homework_elements.extend(elements)
                            break
                    except:
                        continue
                
                # If no specific homework elements found, look for general content areas
                if not homework_elements:
                    content_selectors = [
                        ".content",
                        ".main-content", 
                        ".dashboard-content",
                        "[role='main']",
                        ".student-content"
                    ]
                    
                    for selector in content_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            homework_elements.extend(elements)
                        except:
                            continue
                
                # Parse homework from found elements
                for element in homework_elements[:10]:  # Limit to first 10 items
                    try:
                        title_element = element.find_element(By.CSS_SELECTOR, "h1, h2, h3, h4, .title, .assignment-title, .homework-title")
                        title = title_element.text.strip()
                        
                        if not title:
                            continue
                        
                        # Look for description
                        description = ""
                        try:
                            desc_element = element.find_element(By.CSS_SELECTOR, ".description, .assignment-description, p, .content")
                            description = desc_element.text.strip()
                        except:
                            description = "No description available"
                        
                        # Look for due date
                        due_date = timezone.now() + timezone.timedelta(days=7)  # Default
                        try:
                            date_element = element.find_element(By.CSS_SELECTOR, ".due-date, .deadline, .date, time")
                            date_text = date_element.text.strip()
                            parsed_date = self.parse_date(date_text)
                            if parsed_date:
                                due_date = parsed_date
                        except:
                            pass
                        
                        # Look for subject
                        subject = "Eduka"
                        try:
                            subject_element = element.find_element(By.CSS_SELECTOR, ".subject, .course, .class")
                            subject = subject_element.text.strip() or "Eduka"
                        except:
                            pass
                        
                        # Create homework entry
                        homework_entry = {
                            'title': title,
                            'description': description,
                            'due_date': due_date,
                            'subject': subject,
                            'url': self.driver.current_url,
                            'site': 'eduka'
                        }
                        
                        homework_list.append(homework_entry)
                        
                    except Exception as e:
                        print(f"Error parsing homework element: {e}")
                        continue
                
                # If still no homework found, create a sample entry to indicate successful login
                if not homework_list:
                    homework_list = [{
                        'title': 'Eduka Dashboard Access Verified',
                        'description': 'Successfully logged in to Eduka using saved session. No pending homework found or homework section may have a different layout.',
                        'due_date': timezone.now() + timezone.timedelta(days=1),
                        'subject': 'System',
                        'url': self.driver.current_url,
                        'site': 'eduka'
                    }]
                
            except Exception as e:
                print(f"Error navigating Eduka pages: {e}")
                # Still return at least one entry to show login was successful
                homework_list = [{
                    'title': 'Eduka Login Verified',
                    'description': f'Successfully logged in to Eduka, but encountered navigation issue: {str(e)}',
                    'due_date': timezone.now() + timezone.timedelta(days=1),
                    'subject': 'System',
                    'url': self.auth_url,
                    'site': 'eduka'
                }]
            
        except Exception as e:
            print(f"Error scraping eduka: {e}")
        finally:
            # Clean up driver (but don't clear session - it's saved)
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
                self.is_logged_in = False
        
        return homework_list

class HomeworkScrapingService:
    """Main service for coordinating homework scraping"""
    
    def __init__(self, user):
        self.user = user
        self.preferences, _ = UserScrapingPreferences.objects.get_or_create(user=user)
    
    def scrape_all_sites(self):
        """Scrape homework from all enabled sites"""
        all_homework = []
        
        if self.preferences.enable_manodienynas:
            scraper = ManodienynasScaper(self.user)
            homework = scraper.scrape_homework()
            all_homework.extend(homework)
            self.preferences.last_scraped_manodienynas = timezone.now()
        
        if self.preferences.enable_eduka:
            scraper = EdukaScraper(self.user)
            homework = scraper.scrape_homework()
            all_homework.extend(homework)
            self.preferences.last_scraped_eduka = timezone.now()
        
        self.preferences.save()
        
        # Save scraped homework to database
        self.save_homework(all_homework)
        
        return all_homework
    
    def save_homework(self, homework_list):
        """Save scraped homework to database"""
        saved_count = 0
        
        for hw_data in homework_list:
            homework, created = ScrapedHomework.objects.get_or_create(
                user=self.user,
                site=hw_data['site'],
                title=hw_data['title'],
                due_date=hw_data['due_date'],
                defaults={
                    'description': hw_data['description'],
                    'subject': hw_data['subject'],
                    'url': hw_data['url'],
                }
            )
            
            if created:
                saved_count += 1
        
        return saved_count