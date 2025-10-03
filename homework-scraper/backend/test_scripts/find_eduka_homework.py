#!/usr/bin/env python
"""Quick test to find Eduka homework"""
import django
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from scraper.eduka_playwright import EdukaPlaywrightScraper

# Get user
user = User.objects.get(email='dovydasjusevicius@gmail.com')

print("="*60)
print("FINDING EDUKA HOMEWORK")
print("="*60)

# Scrape with Playwright
with EdukaPlaywrightScraper(user) as scraper:
    homework = scraper.scrape_homework()

print(f"\n✓ Found {len(homework)} homework items:")
for hw in homework:
    print(f"\n📝 {hw['title']}")
    print(f"   Subject: {hw['subject']}")
    print(f"   Due: {hw['due_date']}")
    print(f"   Description: {hw['description'][:100]}...")
