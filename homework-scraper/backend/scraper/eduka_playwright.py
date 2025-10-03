"""
Eduka scraper using Playwright (headless browser)
Playwright is faster and more reliable than Selenium for modern SPAs like Angular
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from datetime import timedelta
from django.utils import timezone
import re
import time


class EdukaPlaywrightScraper:
    """
    Scraper for Eduka.lt using Playwright headless browser
    
    Why Playwright?
    - Faster than Selenium (better protocol)
    - Built-in headless mode (no visible browser)
    - Better for Angular SPAs (proper wait mechanisms)
    - Lower memory usage
    - Cleaner API
    """
    
    def __init__(self, user):
        self.user = user
        self.base_url = 'https://eduka.lt'
        self.auth_url = 'https://eduka.lt/auth'
        self.groups_url = 'https://eduka.lt/student/my-groups'
        self.browser = None
        self.context = None
        self.page = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        self.cleanup()
    
    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            print("DEBUG: ✓ Playwright browser cleaned up")
        except Exception as e:
            print(f"DEBUG: Warning during cleanup: {e}")
    
    def login(self, username, password):
        """
        Login to Eduka using Playwright headless browser
        """
        playwright = None
        try:
            print(f"DEBUG: Starting Playwright headless browser...")
            playwright = sync_playwright().start()
            
            # Launch browser in headless mode (no visible window)
            self.browser = playwright.chromium.launch(
                headless=True,  # Headless mode
                args=[
                    '--disable-blink-features=AutomationControlled',  # Avoid detection
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )
            
            print(f"DEBUG: Creating browser context...")
            # Create browser context (isolated session)
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Create new page
            self.page = self.context.new_page()
            
            print(f"DEBUG: Navigating to Eduka auth page...")
            self.page.goto(self.auth_url, timeout=30000, wait_until='domcontentloaded')
            
            print(f"DEBUG: Waiting for login form...")
            # Wait for login form to appear (Angular needs time to render)
            self.page.wait_for_selector('#username', timeout=10000)
            
            print(f"DEBUG: Filling username: {username}")
            self.page.fill('#username', username)
            
            print(f"DEBUG: Filling password...")
            self.page.fill('#password', password)
            
            # Take screenshot before submitting
            try:
                self.page.screenshot(path=f"debug_eduka_playwright_before_submit.png")
                print(f"DEBUG: Saved screenshot before submit")
            except:
                pass
            
            print(f"DEBUG: Clicking submit button...")
            # Try multiple selectors for the submit button
            submit_selectors = [
                'button:has-text("Prisijungti")',
                'button[type="submit"]',
                'button.btn-primary',
                'input[type="submit"]',
                '.submit-button',
                'form button'
            ]
            
            clicked = False
            for selector in submit_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        print(f"DEBUG: Found submit button with selector: {selector}")
                        # Click without waiting for navigation (sometimes Angular doesn't trigger navigation event)
                        self.page.click(selector, timeout=5000)
                        clicked = True
                        break
                except Exception as e:
                    print(f"DEBUG: Selector {selector} failed: {e}")
                    continue
            
            if not clicked:
                # Fallback: Try pressing Enter on the password field
                print(f"DEBUG: Trying Enter key on password field...")
                self.page.press('#password', 'Enter')
            
            # Wait for page to change (Angular SPAs may not trigger navigation event)
            print(f"DEBUG: Waiting for page to load after login...")
            time.sleep(5)  # Give Angular time to process login and redirect
            
            # Take screenshot to see what happened
            try:
                self.page.screenshot(path=f"debug_eduka_playwright_after_login.png")
                print(f"DEBUG: Saved screenshot after login")
            except:
                pass
            
            print(f"DEBUG: After login - URL: {self.page.url}")
            print(f"DEBUG: After login - Page title: {self.page.title()}")
            
            # Check if we're logged in by checking URL or page content
            if 'my-groups' in self.page.url or 'student' in self.page.url:
                print(f"DEBUG: ✓ Playwright login successful!")
                # Already on groups page, no need to navigate again
                return True
            elif self.page.url != self.auth_url:
                # URL changed but not to expected page - might still be logged in
                print(f"DEBUG: ⚠ URL changed to: {self.page.url}")
                print(f"DEBUG: Checking if logged in by navigating to groups page...")
                self.page.goto(self.groups_url, timeout=30000)
                time.sleep(2)
                if 'my-groups' in self.page.url or 'auth' not in self.page.url:
                    print(f"DEBUG: ✓ Login successful (verified by accessing groups page)!")
                    return True
            
            print(f"DEBUG: ✗ Login may have failed - unexpected URL: {self.page.url}")
            return False
        
        except PlaywrightTimeoutError as e:
            print(f"DEBUG: ✗ Timeout during login: {e}")
            return False
        except Exception as e:
            print(f"DEBUG: ✗ Login failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def parse_date(self, date_str):
        """Parse Lithuanian date format to datetime"""
        try:
            from datetime import datetime
            import locale
            
            # Lithuanian month names
            lt_months = {
                'sausio': 1, 'vasario': 2, 'kovo': 3, 'balandžio': 4,
                'gegužės': 5, 'birželio': 6, 'liepos': 7, 'rugpjūčio': 8,
                'rugsėjo': 9, 'spalio': 10, 'lapkričio': 11, 'gruodžio': 12
            }
            
            # Clean the string
            date_str = date_str.strip().lower()
            
            # Try to parse format like "spalio 15" or "2025-10-15"
            if '-' in date_str:
                # ISO format
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                # Lithuanian format: "spalio 15"
                parts = date_str.split()
                if len(parts) >= 2:
                    month_name = parts[0]
                    day = int(parts[1])
                    month = lt_months.get(month_name, 1)
                    year = timezone.now().year
                    dt = datetime(year, month, day)
                else:
                    return None
            
            # Make timezone aware
            return timezone.make_aware(dt)
        except:
            return None
    
    def scrape_homework(self):
        """Scrape homework from Eduka using Playwright"""
        homework_list = []
        
        try:
            # Get user credentials
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
            
            # Login
            if not self.login(username, password):
                print("Failed to login to Eduka")
                return homework_list
            
            # Check if we're already on the groups page after login
            if 'my-groups' not in self.page.url:
                print(f"DEBUG: Navigating to groups page...")
                self.page.goto(self.groups_url, timeout=30000, wait_until='domcontentloaded')
            else:
                print(f"DEBUG: Already on groups page after login")
            
            # Wait for Angular to render the content
            time.sleep(3)
            
            print(f"DEBUG: Getting page HTML...")
            # Get the fully rendered HTML
            html = self.page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Save HTML for debugging
            with open(f"debug_eduka_playwright_{self.user.id}.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            print(f"DEBUG: Saved HTML to debug file")
            
            # Find group assignment links
            group_links = []
            for link in soup.find_all('a', href=re.compile(r'/my-groups/\d+/recipient-assignment')):
                href = link.get('href')
                if href:
                    full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    group_links.append(full_url)
            
            print(f"DEBUG: Found {len(group_links)} group links")
            
            # Visit each group and extract assignments
            for group_idx, group_url in enumerate(group_links[:5]):  # Limit to 5 groups
                try:
                    print(f"\nDEBUG: Visiting group {group_idx + 1}: {group_url}")
                    
                    # Navigate to group page (use domcontentloaded instead of networkidle for Angular)
                    self.page.goto(group_url, timeout=30000, wait_until='domcontentloaded')
                    time.sleep(3)  # Wait for Angular to render
                    
                    # Get rendered HTML
                    group_html = self.page.content()
                    soup = BeautifulSoup(group_html, 'html.parser')
                    
                    # Save HTML for debugging
                    with open(f"debug_eduka_playwright_group_{group_idx}_{self.user.id}.html", "w", encoding="utf-8") as f:
                        f.write(soup.prettify())
                    print(f"DEBUG: Saved group HTML")
                    
                    # Extract group/subject name
                    group_name = "Eduka"
                    try:
                        group_desc_lines = soup.find_all(class_='group-card__description-line')
                        if len(group_desc_lines) >= 2:
                            group_name = group_desc_lines[1].get_text(strip=True)
                            print(f"DEBUG: Group name: {group_name}")
                    except:
                        pass
                    
                    # Find assignment items
                    assignment_items = soup.find_all(class_='assignment-list__item')
                    print(f"DEBUG: Found {len(assignment_items)} assignment items")
                    
                    for assign_idx, assignment_item in enumerate(assignment_items[:10]):  # Limit per group
                        try:
                            # Extract title
                            title = ""
                            title_elem = assignment_item.find(class_='assignment__description-title')
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                            
                            if not title:
                                print(f"Group {group_idx + 1}, Assignment {assign_idx}: No title found, skipping")
                                continue
                            
                            print(f"Group {group_idx + 1}, Assignment {assign_idx}: Title='{title}'")
                            
                            # Extract task count
                            task_count = ""
                            task_count_elem = assignment_item.find(class_='assignment__description-tasks-count')
                            if task_count_elem:
                                task_count = task_count_elem.get_text(strip=True)
                                print(f"Group {group_idx + 1}, Assignment {assign_idx}: Task count='{task_count}'")
                            
                            # Extract deadline
                            due_date_text = ""
                            deadline_elem = assignment_item.find(class_='assignment-list__deadline-label')
                            if deadline_elem:
                                due_date_text = deadline_elem.get_text(strip=True)
                                print(f"Group {group_idx + 1}, Assignment {assign_idx}: Deadline='{due_date_text}'")
                            
                            # Parse due date
                            due_date = None
                            if due_date_text and due_date_text.lower() not in ['neribotas', 'unlimited', '']:
                                try:
                                    due_date = self.parse_date(due_date_text)
                                    if due_date:
                                        print(f"Group {group_idx + 1}, Assignment {assign_idx}: Parsed due date: {due_date}")
                                except:
                                    print(f"Group {group_idx + 1}, Assignment {assign_idx}: Could not parse date: {due_date_text}")
                            
                            if not due_date:
                                print(f"Group {group_idx + 1}, Assignment {assign_idx}: No deadline (unlimited)")
                            
                            # Create homework object
                            description = f"Užduočių skaičius: {task_count}" if task_count else title
                            
                            homework_list.append({
                                'title': title,
                                'subject': group_name,
                                'due_date': due_date,
                                'description': description,
                                'source': 'eduka'
                            })
                            print(f"Group {group_idx + 1}, Assignment {assign_idx}: ✓ Added homework - {title}")
                            
                        except Exception as e:
                            print(f"Group {group_idx + 1}, Assignment {assign_idx}: Error: {e}")
                            continue
                
                except Exception as e:
                    print(f"Group {group_idx + 1}: Error: {e}")
                    continue
        
        except Exception as e:
            print(f"Error scraping homework: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Always cleanup, even if there was an error
            self.cleanup()
        
        return homework_list
