"""
Simple ManoDienynas scraper using urllib (no Selenium)
Based on working Python script
"""

import urllib.request
import urllib.parse
import http.cookiejar
from html.parser import HTMLParser
import gzip
from django.utils import timezone
from datetime import datetime
import re


class HomeworkTableParser(HTMLParser):
    """Parser to extract homework data from HTML table"""
    
    def __init__(self):
        super().__init__()
        self.in_target_table = False
        self.in_row = False
        self.in_cell = False
        self.in_p_tag = False  # Track if we're in a <p> tag
        self.current_row = []
        self.current_row_attrs = {}  # Store row attributes
        self.table_data = []
        self.current_text = ""
        self.current_cell_index = 0  # Track which cell we're in (0-indexed)
        self.current_p_text = ""  # Text from <p> tags only
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'table':
            # Check if this is the homework table (classhomework)
            if 'class' in attrs_dict and 'classhomework' in attrs_dict['class']:
                self.in_target_table = True
                print("DEBUG: Found classhomework table")
                
        elif tag == 'tr' and self.in_target_table:
            self.in_row = True
            self.current_row = []
            self.current_cell_index = 0
            # Store row attributes to detect completed tasks (e.g., class="completed" or style with opacity/gray)
            self.current_row_attrs = attrs_dict
            
        elif tag == 'td' and self.in_row:
            self.in_cell = True
            self.current_text = ""
            self.current_p_text = ""
            
        elif tag == 'p' and self.in_cell:
            self.in_p_tag = True
            self.current_p_text = ""
            
    def handle_endtag(self, tag):
        if tag == 'table' and self.in_target_table:
            self.in_target_table = False
            
        elif tag == 'tr' and self.in_row:
            self.in_row = False
            if self.current_row:  # Only add non-empty rows
                # Detect if row is completed based on class or style
                is_completed = self._is_row_completed(self.current_row_attrs)
                self.table_data.append({
                    'cells': self.current_row[:],
                    'completed': is_completed
                })
                print(f"DEBUG: Added row with {len(self.current_row)} cells, completed={is_completed}")
                
        elif tag == 'td' and self.in_cell:
            self.in_cell = False
            # For td[4] (index 3 in 0-based), prefer <p> content if available
            if self.current_cell_index == 3 and self.current_p_text.strip():
                # This is the description cell - use <p> content
                self.current_row.append(self.current_p_text.strip())
                print(f"DEBUG: Cell {self.current_cell_index}: Using <p> content: {self.current_p_text.strip()[:50]}...")
            else:
                # For other cells, use all text
                self.current_row.append(self.current_text.strip())
            self.current_cell_index += 1
            
        elif tag == 'p' and self.in_p_tag:
            self.in_p_tag = False
            
    def handle_data(self, data):
        if self.in_cell:
            self.current_text += data.strip() + " "
            if self.in_p_tag:
                self.current_p_text += data.strip() + " "
            self.current_text += data.strip() + " "
    
    def _is_row_completed(self, attrs):
        """Check if a row represents a completed task"""
        # Check for common completed indicators
        row_class = attrs.get('class', '')
        row_style = attrs.get('style', '')
        
        # Common patterns for completed tasks:
        # - class contains "completed", "done", "finished"
        # - style contains "opacity", "text-decoration: line-through", "color: gray"
        if any(keyword in row_class.lower() for keyword in ['completed', 'done', 'finished', 'inactive']):
            return True
        
        if any(keyword in row_style.lower() for keyword in ['opacity', 'line-through', 'gray', 'grey', '#999', '#ccc']):
            return True
            
        return False
    
    def get_homework_data(self):
        """Process table data into homework format"""
        homework_data = []
        
        for row_data in self.table_data:
            row = row_data['cells']
            is_completed = row_data['completed']
            
            # Table structure (7 columns):
            # 0: Lesson date (Pamokos data)
            # 1: Subject (Pamoka)
            # 2: Teacher (Mokytojas)
            # 3: Description (Namų darbas) - <p> tag content from td[4]
            # 4: Due date (Atlikti iki)
            # 5: Entered date (Įvesta)
            # 6: Attached files (Prikabinti failai)
            
            if len(row) >= 5 and row[3].strip():  # Must have description in row[3]
                homework_data.append({
                    'date': row[0].strip(),
                    'subject': row[1].strip(),
                    'teacher': row[2].strip() if len(row) > 2 else "",
                    'description': row[3].strip(),  # Fixed: was row[2], now row[3]
                    'due_date': row[4].strip() if len(row) > 4 else "",
                    'completed': is_completed
                })
        
        return homework_data


class ManoDienynasSimple:
    """Simple ManoDienynas client using urllib"""
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.base_url = "https://www.manodienynas.lt"
        
        # Set up cookie jar and opener
        self.cookie_jar = http.cookiejar.CookieJar()
        cookie_processor = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        self.opener = urllib.request.build_opener(cookie_processor)
        
        # Set headers
        self.opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('Accept-Language', 'en-US,en;q=0.5'),
            ('Accept-Encoding', 'gzip, deflate'),
            ('Connection', 'keep-alive'),
            ('Upgrade-Insecure-Requests', '1'),
        ]
    
    def login(self):
        """Login to ManoDienynas and check for validation errors
        Returns tuple: (success: bool, response_html: str)
        """
        # First, visit the login page to establish session
        login_page_url = f"{self.base_url}/1/lt/public/public/login"
        print(f"DEBUG: Visiting login page: {login_page_url}")
        
        try:
            # Visit login page first
            login_page_request = urllib.request.Request(login_page_url)
            login_page_response = self.opener.open(login_page_request)
            print(f"DEBUG: Login page status: {login_page_response.getcode()}")
        except Exception as e:
            print(f"⚠️ Warning: Could not visit login page: {e}")
        
        # Now submit login
        login_url = f"{self.base_url}/1/lt/ajax/user/login"
        print(f"DEBUG: Submitting login to: {login_url}")
        
        # Prepare login data
        login_data = {
            'username': self.username,
            'password': self.password
        }
        
        # Encode the data
        data = urllib.parse.urlencode(login_data).encode('utf-8')
        
        try:
            # Create the request
            request = urllib.request.Request(login_url, data=data, method='POST')
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            # Make the login request
            response = self.opener.open(request)
            
            if response.getcode() == 200:
                # Read response content
                raw_data = response.read()
                
                # Check if response is gzipped
                if raw_data.startswith(b'\x1f\x8b'):
                    import gzip
                    response_content = gzip.decompress(raw_data).decode('utf-8')
                else:
                    response_content = raw_data.decode('utf-8')
                
                # Check for login validation errors div
                # If div has content (not style="display: none;"), login failed
                if '<div class="login-validation-errors"' in response_content:
                    # Check if it's visible (has errors)
                    if 'style="display: none;"' not in response_content:
                        print("❌ Login failed - incorrect credentials detected")
                        return False, response_content
                
                print("✅ Successfully logged in to ManoDienynas!")
                return True, response_content
            else:
                print(f"❌ Login failed with status code: {response.getcode()}")
                return False, ""
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            import traceback
            traceback.print_exc()
            return False, ""
    
    def _fetch_page(self, url):
        """Generic method to fetch and decode page content"""
        try:
            request = urllib.request.Request(url)
            response = self.opener.open(request)
            
            if response.getcode() != 200:
                print(f"❌ Failed to fetch page. Status code: {response.getcode()}")
                return None
            
            # Read and decode the response
            raw_data = response.read()
            
            # Check if response is gzipped
            if raw_data.startswith(b'\x1f\x8b'):
                html_content = gzip.decompress(raw_data).decode('utf-8')
            else:
                html_content = raw_data.decode('utf-8')
            
            return html_content
            
        except Exception as e:
            print(f"❌ Error fetching page: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_homework(self):
        """Get homework data"""
        homework_url = f"{self.base_url}/1/lt/page/classhomework/home_work"
        
        print(f"DEBUG: Fetching homework from {homework_url}")
        html_content = self._fetch_page(homework_url)
        
        if not html_content:
            return None
        
        # Save for debugging
        try:
            with open('manodienynas_homework_debug.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("DEBUG: Saved HTML to manodienynas_homework_debug.html")
        except:
            pass
        
        # Parse the HTML to extract homework
        parser = HomeworkTableParser()
        parser.feed(html_content)
        return parser.get_homework_data()
    
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
            (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),  # YYYY-MM-DD (most common)
            (r'(\d{2})\.(\d{2})\.(\d{4})', '%d.%m.%Y'),  # DD.MM.YYYY
            (r'(\d{2})/(\d{2})/(\d{4})', '%d/%m/%Y'),  # DD/MM/YYYY
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


def scrape_manodienynas_homework(user):
    """
    Main function to scrape ManoDienynas homework for a user
    Returns list of homework dictionaries
    """
    from authentication.credential_storage import SecureCredentialStorage
    
    homework_list = []
    
    try:
        # Get credentials
        credential_storage = SecureCredentialStorage()
        credentials = credential_storage.get_user_credentials(user.id, 'manodienynas')
        
        if not credentials:
            print("No ManoDienynas credentials found for user")
            return homework_list
        
        if not credentials.get('is_verified', False):
            print("ManoDienynas credentials not verified")
            return homework_list
        
        username = credentials['username']
        password = credentials['password']
        
        # Create client and login
        client = ManoDienynasSimple(username, password)
        login_success, response_html = client.login()
        if not login_success:
            print("Failed to login to ManoDienynas")
            return homework_list
        
        # Get homework
        homework_data = client.get_homework()
        
        if not homework_data:
            print("No homework data found")
            return homework_list
        
        print(f"DEBUG: Found {len(homework_data)} homework items")
        
        # Convert to format expected by the scraping service
        for hw in homework_data:
            # Parse due date
            due_date = client.parse_date(hw['due_date'])
            if not due_date:
                # Default to 7 days from now
                from datetime import timedelta
                due_date = timezone.now() + timedelta(days=7)
            
            # Use subject as title (e.g., "Matematika", "Lietuvių kalba ir literatūra")
            subject = hw['subject']
            title = subject if subject else "Namų darbas"
            
            # Description is just the task description
            description = hw['description']
            
            # Check if task is completed (greyed out in the table)
            is_completed = hw.get('completed', False)
            
            homework_entry = {
                'title': title[:200],
                'description': description[:1000],
                'due_date': due_date,
                'subject': subject[:100] if subject else "Bendras",
                'url': f"{client.base_url}/1/lt/page/classhomework/home_work",
                'site': 'manodienynas',
                'completed': is_completed
            }
            
            homework_list.append(homework_entry)
            status_icon = "✓" if is_completed else "📝"
            print(f"{status_icon} Added homework: {title} {'(Completed)' if is_completed else ''}")
        
    except Exception as e:
        print(f"Error scraping ManoDienynas: {e}")
        import traceback
        traceback.print_exc()
    
    return homework_list
