"""
Simple scraper using requests instead of Selenium
Much faster and more reliable
"""
import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from datetime import datetime, timedelta
import re
from .models import ScrapedHomework, UserScrapingPreferences

class BaseScraper:
    """Base class for web scrapers using requests"""
    
    def __init__(self, user):
        self.user = user
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
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

class ManodienynasScraperSimple(BaseScraper):
    """Simple scraper for manodienynas.lt using requests"""
    
    def __init__(self, user):
        super().__init__(user)
        self.base_url = 'https://www.manodienynas.lt'
        self.login_url = 'https://www.manodienynas.lt/1/lt/public/public/login'
        self.homework_url = 'https://www.manodienynas.lt/1/lt/page/classhomework/home_work'
    
    def login(self, username, password):
        """Login to Manodienynas using AJAX endpoint"""
        try:
            print(f"DEBUG: Attempting login to {self.login_url}")
            
            # First, visit the login page to establish session
            print(f"DEBUG: Visiting login page first...")
            response = self.session.get(self.login_url)
            print(f"DEBUG: Login page status: {response.status_code}")
            
            # Now submit login to AJAX endpoint
            ajax_login_url = 'https://www.manodienynas.lt/1/lt/ajax/user/login'
            print(f"DEBUG: Submitting login to AJAX endpoint: {ajax_login_url}")
            
            # Prepare login data
            login_data = {
                'username': username,
                'password': password,
            }
            
            # Submit login to AJAX endpoint
            response = self.session.post(ajax_login_url, data=login_data)
            print(f"DEBUG: Login response status: {response.status_code}")
            
            # Check response content
            response_text = response.text
            
            # Check for login validation errors
            if '<div class="login-validation-errors"' in response_text:
                # Check if it's visible (has errors)
                if 'style="display: none;"' not in response_text:
                    print(f"DEBUG: Login failed - validation errors found")
                    return False
            
            # If we got a 200 response and no visible errors, login succeeded
            if response.status_code == 200:
                print(f"DEBUG: Login successful!")
                return True
            else:
                print(f"DEBUG: Login failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Login failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def scrape_homework(self):
        """Scrape homework from Manodienynas"""
        homework_list = []
        
        try:
            # Get user credentials
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
            
            # Login
            if not self.login(username, password):
                print("Failed to login to Manodienynas")
                return homework_list
            
            # Get homework page
            print(f"DEBUG: Fetching homework from {self.homework_url}")
            response = self.session.get(self.homework_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save HTML for debugging
            with open(f"debug_manodienynas_{self.user.id}.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            print(f"DEBUG: Saved HTML to debug_manodienynas_{self.user.id}.html")
            
            # Look for the homework table with class "classhomework_table"
            homework_table = soup.find('table', class_='classhomework_table')
            if not homework_table:
                print(f"DEBUG: No homework table found with class 'classhomework_table'")
                # Try alternative approach - find any table
                homework_table = soup.find('table')
                if not homework_table:
                    print(f"DEBUG: No table found at all in the page")
                    return homework_list
                else:
                    print(f"DEBUG: Found alternative table")
            else:
                print(f"DEBUG: Found homework table with class 'classhomework_table'")
            
            # Find homework rows - these have class 'simple_info_block' or 'simple_info_block stripe'
            # Skip header rows (with <th>) and ad rows (with class containing 'adnet')
            tbody = homework_table.find('tbody')
            if not tbody:
                tbody = homework_table
            
            all_rows = tbody.find_all('tr')
            print(f"DEBUG: Found {len(all_rows)} total rows in table")
            
            homework_rows = []
            for row in all_rows:
                # Skip header rows (containing <th> elements)
                if row.find('th'):
                    print(f"DEBUG: Skipping header row")
                    continue
                
                # Skip ad rows (containing class with 'adnet')
                row_class = row.get('class', [])
                row_class_str = ' '.join(row_class) if isinstance(row_class, list) else str(row_class)
                if 'adnet' in row_class_str.lower():
                    print(f"DEBUG: Skipping ad row")
                    continue
                
                # Check if row has class 'simple_info_block'
                if 'simple_info_block' in row_class_str:
                    homework_rows.append(row)
                else:
                    # Also include rows with enough td cells (at least 5)
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        homework_rows.append(row)
                        print(f"DEBUG: Including row with {len(cells)} cells (no simple_info_block class)")
            
            print(f"DEBUG: Found {len(homework_rows)} valid homework rows")
            
            for idx, row in enumerate(homework_rows):
                try:
                    cells = row.find_all('td')
                    
                    if len(cells) < 5:
                        print(f"Row {idx}: Not enough cells ({len(cells)}), skipping")
                        continue
                    
                    # Extract lesson date (column 0)
                    # Structure: Month name (text), day in .month_day div, weekday (text)
                    lesson_date_cell = cells[0]
                    month_day_div = lesson_date_cell.find('div', class_='month_day')
                    if month_day_div:
                        day = month_day_div.get_text(strip=True)
                        # Get all text and extract month (usually first line)
                        cell_text = lesson_date_cell.get_text('\n', strip=True).split('\n')
                        month = cell_text[0] if len(cell_text) > 0 else ""
                        weekday = cell_text[2] if len(cell_text) > 2 else ""
                        lesson_date = f"{month} {day}, {weekday}"
                    else:
                        lesson_date = lesson_date_cell.get_text(strip=True)
                    
                    # Extract subject (column 1) - has class "mark_subject"
                    subject_cell = cells[1]
                    subject = subject_cell.get_text(strip=True)
                    
                    # Extract teacher (column 2)
                    teacher = cells[2].get_text(strip=True)
                    
                    # Extract homework description (column 3) - has class "chDescription"
                    # Description is in a <p> tag within the cell
                    desc_cell = cells[3]
                    desc_p = desc_cell.find('p')
                    if desc_p:
                        description = desc_p.get_text(strip=True)
                    else:
                        description = desc_cell.get_text(strip=True)
                    
                    # Extract due date (column 4) - format: YYYY-MM-DD
                    due_date_text = cells[4].get_text(strip=True)
                    
                    # Skip if no description
                    if not description or len(description) < 3:
                        print(f"Row {idx}: No description ('{description}'), skipping")
                        continue
                    
                    print(f"Row {idx}: Subject='{subject}', Teacher='{teacher}', Description='{description[:50]}...', DueDate='{due_date_text}', LessonDate='{lesson_date}'")
                    
                    # Parse due date
                    due_date = self.parse_date(due_date_text)
                    if not due_date:
                        print(f"Row {idx}: Failed to parse due date '{due_date_text}', using default")
                        due_date = timezone.now() + timedelta(days=7)
                    else:
                        print(f"Row {idx}: Parsed due date: {due_date}")
                    
                    # Create title - match Selenium format (subject name repeated)
                    title = f"{subject} {subject}" if subject else "Namų darbas"
                    
                    # Build full description with metadata
                    full_description = description
                    if teacher:
                        full_description = f"Mokytojas: {teacher}\n\n{full_description}"
                    if lesson_date:
                        full_description = f"Pamokos data: {lesson_date}\n{full_description}"
                    
                    # Create homework entry
                    homework_entry = {
                        'title': title[:200],
                        'description': full_description[:1000],
                        'due_date': due_date,
                        'subject': subject[:100] if subject else "Bendras",
                        'url': self.homework_url,
                        'site': 'manodienynas'
                    }
                    
                    homework_list.append(homework_entry)
                    print(f"Row {idx}: ✓ Added homework - {title}")
                    
                except Exception as e:
                    print(f"Row {idx}: ✗ Error parsing row: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
        except Exception as e:
            print(f"Error scraping manodienynas: {e}")
            import traceback
            traceback.print_exc()
        
        return homework_list

class EdukaScraperSimple(BaseScraper):
    """
    Simple scraper for eduka.lt using Playwright headless browser
    
    Note: Eduka is an Angular SPA that requires JavaScript execution.
    We use Playwright instead of Selenium for better performance.
    """
    
    def __init__(self, user):
        super().__init__(user)
        self.base_url = 'https://eduka.lt'
        self.auth_url = 'https://eduka.lt/auth'
        self.groups_url = 'https://eduka.lt/student/my-groups'
    
    def scrape_homework(self):
        """Scrape homework from Eduka using Playwright"""
        try:
            # Use Playwright scraper
            from .eduka_playwright import EdukaPlaywrightScraper
            
            print(f"DEBUG: Using Playwright headless browser for Eduka...")
            
            # Use context manager to ensure cleanup
            with EdukaPlaywrightScraper(self.user) as scraper:
                homework_list = scraper.scrape_homework()
            
            print(f"DEBUG: ✓ Playwright scraping complete")
            return homework_list
            
        except Exception as e:
            print(f"Error scraping Eduka with Playwright: {e}")
            import traceback
            traceback.print_exc()
            return []


class HomeworkScraperSimple:
    """Combined scraper that uses all simple (requests-based) scrapers"""
    
    def __init__(self, user):
        self.user = user


class HomeworkScrapingService:
    """Main service for coordinating homework scraping"""
    
    def __init__(self, user):
        self.user = user
        from scraper.models import UserScrapingPreferences
        self.preferences, _ = UserScrapingPreferences.objects.get_or_create(user=user)
    
    def scrape_all_sites(self):
        """Scrape homework from all enabled sites"""
        all_homework = []
        
        if self.preferences.enable_manodienynas:
            print("\n" + "="*60)
            print("SCRAPING MANODIENYNAS")
            print("="*60)
            scraper = ManodienynasScraperSimple(self.user)
            homework = scraper.scrape_homework()
            all_homework.extend(homework)
            self.preferences.last_scraped_manodienynas = timezone.now()
            print(f"✓ Scraped {len(homework)} items from Manodienynas")
        
        if self.preferences.enable_eduka:
            print("\n" + "="*60)
            print("SCRAPING EDUKA")
            print("="*60)
            scraper = EdukaScraperSimple(self.user)
            homework = scraper.scrape_homework()
            all_homework.extend(homework)
            self.preferences.last_scraped_eduka = timezone.now()
            print(f"✓ Scraped {len(homework)} items from Eduka")
        
        self.preferences.save()
        
        # Save scraped homework to database
        saved_count = self.save_homework(all_homework)
        print(f"\n✓ Saved {saved_count} new homework items to database")
        
        return all_homework
    
    def save_homework(self, homework_list):
        """Save scraped homework to database"""
        from scraper.models import ScrapedHomework
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
