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
            # Use Selenium for dynamic content
            driver = self.get_selenium_driver()
            
            # Navigate to homework section (this would need login credentials)
            # For demo purposes, we'll scrape publicly available content
            driver.get(self.base_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for homework-related content
            # This is a simplified example - real implementation would need proper selectors
            homework_elements = driver.find_elements(By.CLASS_NAME, "homework-item")
            
            for element in homework_elements:
                try:
                    title = element.find_element(By.CLASS_NAME, "title").text
                    description = element.find_element(By.CLASS_NAME, "description").text
                    due_date_str = element.find_element(By.CLASS_NAME, "due-date").text
                    subject = element.find_element(By.CLASS_NAME, "subject").text
                    
                    due_date = self.parse_date(due_date_str)
                    
                    homework_data = {
                        'title': title,
                        'description': description,
                        'due_date': due_date,
                        'subject': subject,
                        'url': driver.current_url,
                        'site': 'manodienynas'
                    }
                    homework_list.append(homework_data)
                    
                except Exception as e:
                    print(f"Error parsing homework item: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            print(f"Error scraping manodienynas.lt: {e}")
        
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
            # Use requests for simpler content if possible
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for homework-related content
            # This is a simplified example - real implementation would need proper selectors
            homework_elements = soup.find_all('div', class_='homework-item')
            
            for element in homework_elements:
                try:
                    title_elem = element.find('h3', class_='title')
                    desc_elem = element.find('div', class_='description')
                    date_elem = element.find('span', class_='due-date')
                    subject_elem = element.find('span', class_='subject')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        description = desc_elem.get_text(strip=True) if desc_elem else ''
                        due_date_str = date_elem.get_text(strip=True) if date_elem else ''
                        subject = subject_elem.get_text(strip=True) if subject_elem else ''
                        
                        due_date = self.parse_date(due_date_str)
                        
                        homework_data = {
                            'title': title,
                            'description': description,
                            'due_date': due_date,
                            'subject': subject,
                            'url': self.base_url,
                            'site': 'eduka'
                        }
                        homework_list.append(homework_data)
                        
                except Exception as e:
                    print(f"Error parsing homework item: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping eduka.lt: {e}")
        
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