"""
Manodienynas Exam/Test Scraper
Scrapes exam dates from https://www.manodienynas.lt/1/lt/page/control_work/dates_pupil
"""

import urllib.request
import urllib.parse
import http.cookiejar
from html.parser import HTMLParser
import gzip
import brotli
from django.utils import timezone
from datetime import datetime
import re


class ExamTableParser(HTMLParser):
    """Parser to extract exam data from cWorksListTable"""
    
    def __init__(self):
        super().__init__()
        self.in_target_table = False
        self.in_tbody = False  # Not required
        self.in_row = False
        self.in_cell = False
        self.current_row = []
        self.table_data = []
        self.current_text = ""
        self.cell_index = 0
        self.is_header_row = False  # Track if we're in <th> row
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'table':
            # Check if this is the exam table (cWorksListTable)
            if 'id' in attrs_dict and attrs_dict['id'] == 'cWorksListTable':
                self.in_target_table = True
                print("DEBUG: Found cWorksListTable")
        
        elif tag == 'tbody' and self.in_target_table:
            self.in_tbody = True
            
        elif tag == 'tr' and self.in_target_table:  # Don't require tbody
            self.in_row = True
            self.current_row = []
            self.cell_index = 0
            self.is_header_row = False
            
        elif tag == 'th' and self.in_row:
            # This is a header row, mark it
            self.is_header_row = True
            self.in_cell = True
            self.current_text = ""
            self.cell_index += 1
            
        elif tag == 'td' and self.in_row:
            self.in_cell = True
            self.current_text = ""
            self.cell_index += 1
            
    def handle_endtag(self, tag):
        if tag == 'table' and self.in_target_table:
            self.in_target_table = False
            print(f"DEBUG: Finished parsing table, found {len(self.table_data)} rows")
            
        elif tag == 'tbody' and self.in_tbody:
            self.in_tbody = False
            
        elif tag == 'tr' and self.in_row:
            self.in_row = False
            # Skip header rows (those with <th> tags)
            if self.current_row and not self.is_header_row:
                if len(self.current_row) >= 5:  # Valid exam row
                    self.table_data.append(self.current_row[:])
                    print(f"DEBUG: Added exam row with {len(self.current_row)} cells: {self.current_row}")
                else:
                    print(f"DEBUG: Skipped row with {len(self.current_row)} cells (need >= 5)")
            elif self.is_header_row:
                print(f"DEBUG: Skipped header row")
                
        elif tag in ('td', 'th') and self.in_cell:
            self.in_cell = False
            self.current_row.append(self.current_text.strip())
            
    def handle_data(self, data):
        if self.in_cell:
            self.current_text += data.strip() + " "
    
    def get_exam_data(self):
        """Process table data into exam format"""
        exam_data = []
        
        for row in self.table_data:
            if len(row) >= 6:  # Need at least 6 columns
                # Table structure (6 columns):
                # row[0] = Eil. Nr. (Number) - td[1] in XPath
                # row[1] = Data (Date) - td[2] in XPath
                # row[2] = Atsiskaitomojo darbo tipas (Exam type) - td[3]
                # row[3] = Grupė (Subject/Group) - td[4] in XPath
                # row[4] = Atsiskaitomojo darbo tema (Exam name) - td[5] in XPath
                # row[5] = Įvesta (Entered date) - td[6]
                
                exam_date_str = row[1].strip() if len(row) > 1 else ""  # td[2] = Date
                subject = row[3].strip() if len(row) > 3 else ""         # td[4] = Subject
                exam_name = row[4].strip() if len(row) > 4 else ""       # td[5] = Exam name
                
                if exam_date_str and subject and exam_name:
                    exam_data.append({
                        'exam_date': exam_date_str,
                        'subject': subject,
                        'exam_name': exam_name
                    })
                    print(f"DEBUG: Parsed exam - Date: {exam_date_str}, Subject: {subject}, Name: {exam_name}")
        
        return exam_data


class ManoDienynasExamClient:
    """Client for ManoDienynas exam extraction"""
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.base_url = "https://www.manodienynas.lt"
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar),
            urllib.request.HTTPSHandler()
        )
        urllib.request.install_opener(self.opener)
        
    def login(self):
        """Login to ManoDienynas"""
        print("DEBUG: Starting login...")
        
        # Step 1: Visit login page to establish session
        login_page_url = f"{self.base_url}/1/lt/public/public/login"
        request = urllib.request.Request(
            login_page_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9,lt;q=0.8',
            }
        )
        
        try:
            with self.opener.open(request) as response:
                print(f"DEBUG: Login page status: {response.status}")
        except Exception as e:
            print(f"DEBUG: Error getting login page: {str(e)}")
            # Continue anyway - session might still work
        
        # Step 2: Submit login form to AJAX endpoint
        login_url = f"{self.base_url}/1/lt/ajax/user/login"
        login_data = {
            'username': self.username,
            'password': self.password
        }
        
        data = urllib.parse.urlencode(login_data).encode('utf-8')
        request = urllib.request.Request(
            login_url,
            data=data,
            method='POST',
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        )
        
        try:
            with self.opener.open(request) as response:
                response_data = response.read()
                
                print(f"DEBUG: Response length: {len(response_data)}")
                print(f"DEBUG: Content-Encoding: {response.headers.get('Content-Encoding')}")
                
                # Handle compression
                content_encoding = response.headers.get('Content-Encoding', '')
                if content_encoding == 'br' or response_data.startswith(b'\x1b'):
                    print("DEBUG: Data is brotli compressed, decompressing...")
                    response_data = brotli.decompress(response_data)
                elif response_data.startswith(b'\x1f\x8b'):
                    print("DEBUG: Data is gzipped, decompressing...")
                    response_data = gzip.decompress(response_data)
                
                html = response_data.decode('utf-8')
                
                # Check for login errors
                if '<div class="login-validation-errors"' in html:
                    if 'style="display: none;"' not in html:
                        print("DEBUG: Login failed - incorrect credentials")
                        return False
                
                print("DEBUG: Login successful!")
                return True
                    
        except Exception as e:
            print(f"DEBUG: Login error: {str(e)}")
            raise
    
    def get_exam_dates_page(self):
        """Get the exam dates page HTML"""
        url = f"{self.base_url}/1/lt/page/control_work/dates_pupil"
        
        request = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9,lt;q=0.8',
            }
        )
        
        try:
            with self.opener.open(request) as response:
                response_data = response.read()
                
                # Handle compression
                content_encoding = response.headers.get('Content-Encoding', '')
                if content_encoding == 'br' or response_data.startswith(b'\x1b'):
                    response_data = brotli.decompress(response_data)
                elif response_data.startswith(b'\x1f\x8b'):
                    response_data = gzip.decompress(response_data)
                
                html = response_data.decode('utf-8')
                print(f"DEBUG: Got exam dates page, length: {len(html)}")
                
                # Save HTML for debugging
                with open('manodienynas_exams_debug.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print("DEBUG: Saved HTML to manodienynas_exams_debug.html")
                
                return html
                
        except Exception as e:
            print(f"DEBUG: Error getting exam dates page: {str(e)}")
            raise


def parse_lithuanian_date(date_str):
    """Parse Lithuanian date format (e.g., '2025-10-15' or '2025.10.15')"""
    try:
        # Try different date formats
        for fmt in ['%Y-%m-%d', '%Y.%m.%d', '%d-%m-%Y', '%d.%m.%Y']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If all fails, try to extract year-month-day
        match = re.search(r'(\d{4})[.-](\d{1,2})[.-](\d{1,2})', date_str)
        if match:
            year, month, day = match.groups()
            return datetime(int(year), int(month), int(day))
        
        print(f"WARNING: Could not parse date: {date_str}")
        return None
    except Exception as e:
        print(f"ERROR: Date parsing error: {str(e)}")
        return None


def scrape_manodienynas_exams(user):
    """
    Scrape exam dates from ManoDienynas for a user
    Returns list of exam dictionaries
    """
    from authentication.credential_storage import SecureCredentialStorage
    from .models import ScrapedExam
    
    print(f"\n=== Starting ManoDienynas Exam Scraping for {user.username} ===")
    
    # Get credentials
    storage = SecureCredentialStorage()
    credentials = storage.get_user_credentials(user.id, 'manodienynas')
    if not credentials:
        print("ERROR: No ManoDienynas credentials found")
        return []
    
    username = credentials.get('username')
    password = credentials.get('password')
    
    if not username or not password:
        print("ERROR: Missing username or password")
        return []
    
    print(f"DEBUG: Got credentials for user: {username}")
    
    # Create client and login
    client = ManoDienynasExamClient(username, password)
    
    if not client.login():
        print("ERROR: Login failed")
        return []
    
    # Get exam dates page
    html = client.get_exam_dates_page()
    
    # Parse exam table
    parser = ExamTableParser()
    parser.feed(html)
    exam_data = parser.get_exam_data()
    
    print(f"\nDEBUG: Found {len(exam_data)} exams")
    
    # Process and save exams
    saved_exams = []
    
    for exam in exam_data:
        try:
            # Parse date
            exam_date = parse_lithuanian_date(exam['exam_date'])
            if not exam_date:
                print(f"WARNING: Skipping exam with invalid date: {exam['exam_date']}")
                continue
            
            # Make timezone aware
            exam_date = timezone.make_aware(exam_date)
            
            # Create or update exam record
            exam_obj, created = ScrapedExam.objects.update_or_create(
                user=user,
                site='manodienynas',
                exam_name=exam['exam_name'][:500],
                exam_date=exam_date,
                defaults={
                    'subject': exam['subject'][:200],
                    'url': f"{client.base_url}/1/lt/page/control_work/dates_pupil",
                }
            )
            
            action = "Created" if created else "Updated"
            print(f"{action}: {exam['exam_name']} - {exam['subject']} on {exam_date.strftime('%Y-%m-%d')}")
            
            saved_exams.append(exam_obj)
            
        except Exception as e:
            print(f"ERROR: Failed to save exam {exam.get('exam_name', 'Unknown')}: {str(e)}")
            continue
    
    print(f"\n=== Exam Scraping Complete: {len(saved_exams)} exams saved ===\n")
    
    return saved_exams
