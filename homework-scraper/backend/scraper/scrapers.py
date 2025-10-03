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
        # Temporarily disable headless mode for debugging
        # chrome_options.add_argument('--headless')  # COMMENTED OUT FOR DEBUGGING
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Hide automation
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        return webdriver.Chrome(options=chrome_options)
    
    def parse_date(self, date_str):
        """Parse Lithuanian date string to datetime"""
        if not date_str:
            return None
        
        # Clean up the date string
        date_str = date_str.strip()
        
        # Lithuanian month names mapping
        lithuanian_months = {
            'sausio': '01', 'sausis': '01',
            'vasario': '02', 'vasaris': '02',
            'kovo': '03', 'kovas': '03',
            'balandžio': '04', 'balandis': '04',
            'gegužės': '05', 'gegužė': '05',
            'birželio': '06', 'birželis': '06',
            'liepos': '07', 'liepа': '07',
            'rugpjūčio': '08', 'rugpjūtis': '08',
            'rugsėjo': '09', 'rugsėjis': '09',
            'spalio': '10', 'spalis': '10',
            'lapkričio': '11', 'lapkritis': '11',
            'gruodžio': '12', 'gruodis': '12'
        }
        
        # Try to replace Lithuanian month names with numbers
        date_str_lower = date_str.lower()
        for lt_month, month_num in lithuanian_months.items():
            if lt_month in date_str_lower:
                date_str = date_str_lower.replace(lt_month, month_num)
                break
        
        # Common date patterns
        patterns = [
            (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),  # YYYY-MM-DD (most common in Manodienynas)
            (r'(\d{2})\.(\d{2})\.(\d{4})', '%d.%m.%Y'),  # DD.MM.YYYY
            (r'(\d{2})/(\d{2})/(\d{4})', '%d/%m/%Y'),  # DD/MM/YYYY
            (r'(\d{4})\.(\d{2})\.(\d{2})', '%Y.%m.%d'),  # YYYY.MM.DD
            (r'(\d{2})\s+(\d{2})\s+(\d{4})', '%d %m %Y'),  # DD MM YYYY with spaces
        ]
        
        for pattern, date_format in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    date_obj = datetime.strptime(match.group(0), date_format)
                    # Make timezone aware
                    return timezone.make_aware(date_obj)
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
            
            print(f"DEBUG: Navigating to login page: {self.login_url}")
            self.driver.get(self.login_url)
            time.sleep(5)  # Increased wait time
            
            wait = WebDriverWait(self.driver, 20)  # Increased timeout
            
            # Save screenshot before login
            try:
                self.driver.save_screenshot(f"debug_manodienynas_login_page_{self.user.id}.png")
                print(f"DEBUG: Login page screenshot saved")
            except:
                pass
            
            # Use specific XPath selectors for Manodienynas
            # XPath: //*[@id="dl_username"] for username
            # XPath: //*[@id="dl_password"] for password
            # XPath: //*[@id="login_submit"] for submit button
            
            print(f"DEBUG: Looking for username field with XPath: //*[@id='dl_username']")
            username_field = None
            try:
                username_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dl_username"]')))
                # Try to make it visible and clickable
                self.driver.execute_script("arguments[0].scrollIntoView(true);", username_field)
                time.sleep(1)
                username_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="dl_username"]')))
                print(f"DEBUG: Found username field with XPath")
            except Exception as e:
                print(f"DEBUG: Failed to find username field: {str(e)}")
                raise Exception("Username field not found with XPath //*[@id='dl_username']")
            
            print(f"DEBUG: Looking for password field with XPath: //*[@id='dl_password']")
            password_field = None
            try:
                password_field = self.driver.find_element(By.XPATH, '//*[@id="dl_password"]')
                print(f"DEBUG: Found password field with XPath")
            except Exception as e:
                print(f"DEBUG: Failed to find password field: {str(e)}")
                raise Exception("Password field not found with XPath //*[@id='dl_password']")
            
            # Enter credentials
            print(f"DEBUG: Entering username: {username}")
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            print(f"DEBUG: Entering password")
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Save screenshot before submitting
            try:
                self.driver.save_screenshot(f"debug_manodienynas_before_submit_{self.user.id}.png")
                print(f"DEBUG: Before submit screenshot saved")
            except:
                pass
            
            # Find and click submit button using XPath: //*[@id="login_submit"]
            print(f"DEBUG: Looking for submit button with XPath: //*[@id='login_submit']")
            submit_button = None
            try:
                submit_button = self.driver.find_element(By.XPATH, '//*[@id="login_submit"]')
                # Scroll into view and make clickable
                self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(1)
                print(f"DEBUG: Found submit button with XPath")
            except Exception as e:
                print(f"DEBUG: Failed to find submit button: {str(e)}")
                raise Exception("Submit button not found with XPath //*[@id='login_submit']")
            
            if not submit_button:
                raise Exception("Submit button not found")
            
            print(f"DEBUG: Clicking submit button")
            try:
                # Try normal click first
                submit_button.click()
            except:
                # If normal click fails, try JavaScript click
                print(f"DEBUG: Normal click failed, trying JavaScript click")
                self.driver.execute_script("arguments[0].click();", submit_button)
            
            time.sleep(5)  # Increased wait time
            
            # Save screenshot after submit
            try:
                self.driver.save_screenshot(f"debug_manodienynas_after_submit_{self.user.id}.png")
                print(f"DEBUG: After submit screenshot saved")
            except:
                pass
            
            # Verify login success
            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()
            
            print(f"DEBUG: After login - URL: {current_url}")
            print(f"DEBUG: After login - Page title: {self.driver.title}")
            
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
                print(f"DEBUG: Login successful!")
                return True
            else:
                print(f"DEBUG: Login failed - still on login page or no success indicators")
                raise Exception("Login failed - authentication unsuccessful")
                
        except Exception as e:
            print(f"Login failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def scrape_homework(self):
        """Scrape homework from manodienynas.lt using simple urllib approach"""
        # Import and use the simple scraper
        from .manodienynas_simple import scrape_manodienynas_homework
        
        print("\n" + "="*60)
        print("SCRAPING MANODIENYNAS (urllib method)")
        print("="*60)
        
        homework_list = scrape_manodienynas_homework(self.user)
        
        print(f"✓ Scraped {len(homework_list)} items from ManoDienynas")
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
            
            print(f"DEBUG: Navigating to Eduka auth page: {self.auth_url}")
            self.driver.get(self.auth_url)
            time.sleep(5)
            
            wait = WebDriverWait(self.driver, 20)
            
            # Save screenshot before login
            try:
                self.driver.save_screenshot(f"debug_eduka_login_page_{self.user.id}.png")
                print(f"DEBUG: Eduka login page screenshot saved")
            except:
                pass
            
            # Use specific XPath selectors for Eduka
            # XPath: //*[@id="username"] for username
            # XPath: //*[@id="password"] for password
            # XPath: /html/body/app-root/div/app-classroom/app-auth/app-auth-card/div/div/div/app-auth-login/div/div[2]/div/app-auth-login-form/div[2]/button for submit
            
            print(f"DEBUG: Looking for username field with XPath: //*[@id='username']")
            username_field = None
            try:
                username_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", username_field)
                time.sleep(1)
                username_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="username"]')))
                print(f"DEBUG: Found username field with XPath")
            except Exception as e:
                print(f"DEBUG: Failed to find username field: {str(e)}")
                raise Exception("Username field not found with XPath //*[@id='username']")
            
            print(f"DEBUG: Looking for password field with XPath: //*[@id='password']")
            password_field = None
            try:
                password_field = self.driver.find_element(By.XPATH, '//*[@id="password"]')
                print(f"DEBUG: Found password field with XPath")
            except Exception as e:
                print(f"DEBUG: Failed to find password field: {str(e)}")
                raise Exception("Password field not found with XPath //*[@id='password']")
            
            # Enter credentials
            print(f"DEBUG: Entering username: {username}")
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            print(f"DEBUG: Entering password")
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Save screenshot before submitting
            try:
                self.driver.save_screenshot(f"debug_eduka_before_submit_{self.user.id}.png")
                print(f"DEBUG: Before submit screenshot saved")
            except:
                pass
            
            # Find and click submit button using XPath
            print(f"DEBUG: Looking for submit button with XPath")
            submit_button = None
            try:
                # Try the specific XPath first
                submit_button = self.driver.find_element(By.XPATH, '/html/body/app-root/div/app-classroom/app-auth/app-auth-card/div/div/div/app-auth-login/div/div[2]/div/app-auth-login-form/div[2]/button')
                print(f"DEBUG: Found submit button with specific XPath")
            except Exception as e1:
                print(f"DEBUG: Specific XPath failed, trying generic button selector: {str(e1)}")
                try:
                    # Fallback: Look for any button in the login form
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, 'app-auth-login-form button[type="submit"]')
                    print(f"DEBUG: Found submit button with CSS selector")
                except Exception as e2:
                    print(f"DEBUG: CSS selector failed: {str(e2)}")
                    # Last fallback: any button containing login-related text
                    try:
                        submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Prisijungti') or contains(text(), 'Login') or contains(text(), 'Sign in')]")
                        print(f"DEBUG: Found submit button by text content")
                    except Exception as e3:
                        print(f"DEBUG: Text-based search failed: {str(e3)}")
                        raise Exception("Submit button not found")
            
            if submit_button:
                # Scroll into view and make clickable
                self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(1)
                print(f"DEBUG: Clicking submit button")
                try:
                    submit_button.click()
                except:
                    # Try JavaScript click if normal click fails
                    print(f"DEBUG: Normal click failed, trying JavaScript click")
                    self.driver.execute_script("arguments[0].click();", submit_button)
            else:
                raise Exception("Submit button not found")
            
            time.sleep(5)
            
            # Save screenshot after submit
            try:
                self.driver.save_screenshot(f"debug_eduka_after_submit_{self.user.id}.png")
                print(f"DEBUG: After submit screenshot saved")
            except:
                pass
            
            # Verify login success
            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()
            
            print(f"DEBUG: After login - URL: {current_url}")
            print(f"DEBUG: After login - Page title: {self.driver.title}")
            
            # Check for success indicators
            success_indicators = [
                "student", "my-groups", "dashboard", "mokinys", "logout", 
                "atsijungti", "prisijungta", "classroom"
            ]
            
            has_success = any(indicator in page_source or indicator in current_url for indicator in success_indicators)
            
            if has_success and "auth" not in current_url:
                self.is_logged_in = True
                # Save session for future use
                self.session_manager.save_session(self.driver)
                print(f"DEBUG: Eduka login successful!")
                return True
            else:
                print(f"DEBUG: Eduka login failed - still on auth page or no success indicators")
                raise Exception("Login failed - authentication unsuccessful")
                
        except Exception as e:
            print(f"Login failed: {e}")
            import traceback
            traceback.print_exc()
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
                print(f"Navigating to groups page: {self.groups_url}")
                self.driver.get(self.groups_url)
                time.sleep(3)
                
                # Save screenshot for debugging
                try:
                    screenshot_path = f"debug_eduka_groups_{self.user.id}.png"
                    self.driver.save_screenshot(screenshot_path)
                    print(f"Groups page screenshot saved to: {screenshot_path}")
                except Exception as screenshot_error:
                    print(f"Could not save screenshot: {screenshot_error}")
                
                # Print page info for debugging
                print(f"Page title: {self.driver.title}")
                print(f"Current URL: {self.driver.current_url}")
                
                # Check if we're still authenticated after navigation
                if not self.session_manager.is_session_valid(self.driver):
                    print("Session expired, attempting re-login...")
                    self.session_manager.clear_session()
                    if not self.login(username, password):
                        print("Re-login failed")
                        return homework_list
                    self.driver.get(self.groups_url)
                    time.sleep(3)
                
                # Look for group links to navigate to
                # Based on HTML: <a href="/fe/student/my-groups/7145079/recipient-assignment">
                group_links = []
                try:
                    # Find all links to group assignment pages
                    link_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/my-groups/'][href*='/recipient-assignment']")
                    if link_elements:
                        group_links = [link.get_attribute('href') for link in link_elements if link.get_attribute('href')]
                        print(f"Found {len(group_links)} group assignment links")
                    else:
                        print("No group assignment links found")
                except Exception as e:
                    print(f"Error finding group links: {e}")
                
                # Visit each group and scrape assignments
                for group_idx, group_url in enumerate(group_links[:5]):  # Limit to 5 groups
                    try:
                        print(f"\n--- Visiting group {group_idx + 1}: {group_url} ---")
                        self.driver.get(group_url)
                        time.sleep(3)
                        
                        # Save screenshot
                        try:
                            screenshot_path = f"debug_eduka_group_{group_idx}_{self.user.id}.png"
                            self.driver.save_screenshot(screenshot_path)
                            print(f"Group {group_idx + 1} screenshot saved to: {screenshot_path}")
                        except:
                            pass
                        
                        # Now look for assignments on this page
                        self._extract_assignments_from_page(homework_list, group_url)
                        
                    except Exception as group_error:
                        print(f"Error processing group {group_idx + 1}: {group_error}")
                        continue
                
            except Exception as e:
                print(f"Error navigating Eduka pages: {e}")
                import traceback
                print(traceback.format_exc())
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
    
    def _extract_assignments_from_page(self, homework_list, page_url):
        """Extract assignments from current Eduka page"""
        # Look for homework/assignments content
        # Based on the HTML structure: <div class="assignment-list__item">
        # Structure contains:
        # - .assignment__description-title: Title (e.g., "Trigonometrinių lygčių sprendimas")
        # - .assignment__description-tasks-count: Task count (e.g., "15 užd.")
        # - .assignment-list__deadline-label: Deadline (e.g., "Neribotas" or date)
        # - .assignment-list__status-label: Status (e.g., "Nepradėta")
        
        homework_elements = []
        
        # Look for assignment list items with specific class
        try:
            assignment_items = self.driver.find_elements(By.CSS_SELECTOR, ".assignment-list__item")
            if assignment_items:
                homework_elements = assignment_items
                print(f"Found {len(assignment_items)} assignment items with class 'assignment-list__item'")
            else:
                # Fallback: Look for assignment divs
                assignment_divs = self.driver.find_elements(By.CSS_SELECTOR, ".assignment")
                if assignment_divs:
                    homework_elements = assignment_divs
                    print(f"Found {len(assignment_divs)} assignment divs")
                else:
                    # Last fallback: Look for any content with assignment in class
                    any_assignments = self.driver.find_elements(By.CSS_SELECTOR, "[class*='assignment']")
                    homework_elements = any_assignments
                    print(f"Found {len(any_assignments)} elements with 'assignment' in class")
        except Exception as e:
            print(f"Error finding assignment elements: {e}")
            import traceback
            print(traceback.format_exc())
            return
        
        # Parse homework from found elements
        print(f"Processing {len(homework_elements)} assignment elements on {page_url}")
        for idx, element in enumerate(homework_elements[:20]):  # Limit to first 20 items
            try:
                # Extract title from .assignment__description-title
                title = ""
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, ".assignment__description-title")
                    title = title_elem.text.strip()
                except:
                    # Fallback: try other title selectors
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, "h1, h2, h3, h4, .title, .assignment-title")
                        title = title_elem.text.strip()
                    except:
                        pass
                
                if not title:
                    print(f"Element {idx}: No title found, skipping")
                    continue
                
                print(f"Element {idx}: Title='{title}'")
                
                # Extract task count from .assignment__description-tasks-count
                task_count = ""
                try:
                    task_count_elem = element.find_element(By.CSS_SELECTOR, ".assignment__description-tasks-count")
                    task_count = task_count_elem.text.strip()
                    print(f"Element {idx}: Task count='{task_count}'")
                except:
                    pass
                
                # Extract deadline from .assignment-list__deadline-label
                due_date_text = ""
                try:
                    deadline_elem = element.find_element(By.CSS_SELECTOR, ".assignment-list__deadline-label")
                    due_date_text = deadline_elem.text.strip()
                    print(f"Element {idx}: Deadline='{due_date_text}'")
                except:
                    # Fallback: try other deadline selectors
                    try:
                        deadline_elem = element.find_element(By.CSS_SELECTOR, ".due-date, .deadline, .date")
                        due_date_text = deadline_elem.text.strip()
                    except:
                        pass
                
                # Extract status from .assignment-list__status-label
                status = ""
                is_completed = False
                try:
                    status_elem = element.find_element(By.CSS_SELECTOR, ".assignment-list__status-label")
                    status = status_elem.text.strip()
                    print(f"Element {idx}: Status='{status}'")
                    # Check if status indicates completion
                    if status and any(word in status.lower() for word in ['baig', 'atlik', 'complete', 'done', 'finished']):
                        is_completed = True
                        print(f"Element {idx}: Assignment is completed, skipping")
                        continue  # Skip completed assignments
                except:
                    pass
                
                # Parse due date
                due_date = None
                # Only create a due date if it's NOT "Neribotas" (unlimited)
                if due_date_text and due_date_text.lower() not in ['neribotas', 'unlimited', 'no deadline', '-', 'none']:
                    due_date = self.parse_date(due_date_text)
                    if due_date:
                        print(f"Element {idx}: Parsed due date: {due_date}")
                    else:
                        print(f"Element {idx}: Could not parse due date '{due_date_text}'")
                else:
                    print(f"Element {idx}: No deadline (unlimited) - will not set due date")
                
                # If no due date was set, leave it as None (don't default to 30 days)
                
                # Build description - ONLY include task count (Užduočių skaičius)
                description = ""
                if task_count:
                    description = f"Užduočių skaičius: {task_count}"
                else:
                    description = "Užduotis iš Eduka platformos"
                
                # Do NOT add status or deadline to description
                # Do NOT add additional element text
                
                # Try to extract subject from page context (group card or page title)
                subject = "Eduka"
                try:
                    # Look for group-card__description-line elements (usually contains subject name)
                    # Structure: Line 0: Teacher, Line 1: Subject, Line 2: School
                    group_desc_lines = self.driver.find_elements(By.CSS_SELECTOR, ".group-card__description-line")
                    if len(group_desc_lines) >= 2:
                        subject_text = group_desc_lines[1].text.strip()
                        if subject_text and len(subject_text) < 100 and len(subject_text) > 2:
                            subject = subject_text
                            print(f"Element {idx}: Extracted subject from group card: '{subject}'")
                    else:
                        # Fallback: try other subject selectors
                        subject_elems = self.driver.find_elements(By.CSS_SELECTOR, ".group-name, .course-name, h1, h2")
                        if subject_elems and len(subject_elems) > 0:
                            subject_text = subject_elems[0].text.strip()
                            if subject_text and len(subject_text) < 100 and len(subject_text) > 2:
                                subject = subject_text
                                print(f"Element {idx}: Extracted subject from fallback: '{subject}'")
                except Exception as subj_error:
                    print(f"Element {idx}: Could not extract subject: {subj_error}")
                    pass
                
                # Create homework entry
                homework_entry = {
                    'title': title[:200],
                    'description': description[:1000],
                    'due_date': due_date,
                    'subject': subject[:100],
                    'url': page_url,  # Use the group page URL
                    'site': 'eduka'
                }
                
                homework_list.append(homework_entry)
                print(f"Element {idx}: ✓ Added homework - {title}")
                
            except Exception as e:
                print(f"Element {idx}: ✗ Error parsing assignment element: {e}")
                import traceback
                print(traceback.format_exc())
                continue

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