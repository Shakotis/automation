import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from scraper.scrapers_simple import ManodienynasScraperSimple

user = User.objects.get(email='dovydasjusevicius@gmail.com')
scraper = ManodienynasScraperSimple(user)
hw = scraper.scrape_homework()

print(f'\nFound {len(hw)} items:')
for i, item in enumerate(hw):
    print(f'{i+1}. Title: {item["title"]}')
    print(f'   Subject: {item["subject"]}')
