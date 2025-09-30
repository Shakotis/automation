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
    
    def scrape_homework(self):
        """Scrape homework from manodienynas.lt"""
        homework_list = []
        
        try:
            # For demo purposes, return realistic mock data
            # In production, this would use Selenium to scrape actual homework
            homework_list = [
                {
                    'title': 'Matematikos namų darbai - Algebros uždaviniai',
                    'description': 'Spręsti uždavinius 15-20 iš vadovėlio. Ypatingas dėmesys skirtinas kvadratinėms lygtims.',
                    'due_date': timezone.now() + timezone.timedelta(days=2),
                    'subject': 'Matematika',
                    'url': f'{self.base_url}/homework/123',
                    'site': 'manodienynas'
                },
                {
                    'title': 'Fizikos laboratorinis darbas',
                    'description': 'Atlikti laboratorinius darbus Nr. 5 ir 6. Parengti ataskaitas.',
                    'due_date': timezone.now() + timezone.timedelta(days=5),
                    'subject': 'Fizika',
                    'url': f'{self.base_url}/homework/456',
                    'site': 'manodienynas'
                },
                {
                    'title': 'Istorijos referatas',
                    'description': 'Parašyti referatą apie Lietuvos nepriklausomybės atkūrimą. 5-7 puslapiai.',
                    'due_date': timezone.now() + timezone.timedelta(days=7),
                    'subject': 'Istorija',
                    'url': f'{self.base_url}/homework/789',
                    'site': 'manodienynas'
                }
            ]
            
        except Exception as e:
            print(f"Error scraping manodienynas: {e}")
        
        return homework_list

class EdukaScraper(BaseScraper):
    """Scraper for eduka.lt"""
    
    def __init__(self, user):
        super().__init__(user)
        self.base_url = 'https://eduka.lt'
    
    def scrape_homework(self):
        """Scrape homework from eduka.lt"""
        homework_list = []
        
        try:
            # For demo purposes, return realistic mock data
            # In production, this would scrape actual homework from Eduka
            homework_list = [
                {
                    'title': 'Lietuvių kalbos rašinys',
                    'description': 'Parašyti kūrybos darbą tema "Vasaros prisiminimai". 2-3 puslapiai.',
                    'due_date': timezone.now() + timezone.timedelta(days=3),
                    'subject': 'Lietuvių kalba',
                    'url': f'{self.base_url}/homework/eduka_001',
                    'site': 'eduka'
                },
                {
                    'title': 'Chemijos laboratorinis darbas',
                    'description': 'Atlikti cheminės reakcijos tyrimą ir užpildyti ataskaitą.',
                    'due_date': timezone.now() + timezone.timedelta(days=4),
                    'subject': 'Chemija',
                    'url': f'{self.base_url}/homework/eduka_002',
                    'site': 'eduka'
                },
                {
                    'title': 'Anglų kalbos teksto analizė',
                    'description': 'Perskaityti tekstą ir atsakyti į klausimus. Puslapiai 45-50.',
                    'due_date': timezone.now() + timezone.timedelta(days=6),
                    'subject': 'Anglų kalba',
                    'url': f'{self.base_url}/homework/eduka_003',
                    'site': 'eduka'
                }
            ]
            
        except Exception as e:
            print(f"Error scraping eduka: {e}")
        
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