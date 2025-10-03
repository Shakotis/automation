"""
Simplified Eduka API analyzer - uses the working Selenium scraper to capture session info
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from scraper.scrapers import EdukaScraper
import requests

def analyze_eduka_session():
    """Use the working Selenium scraper to get session info"""
    
    print("\n" + "="*80)
    print("EDUKA SESSION ANALYZER")
    print("="*80)
    
    # Get user
    user = User.objects.get(email='dovydasjusevicius@gmail.com')
    
    print("\nStep 1: Login with Selenium (working method)")
    print("-"*80)
    
    # Use the working Selenium scraper
    scraper = EdukaScraper(user)
    
    # Get authenticated driver
    driver, session_loaded = scraper.session_manager.get_authenticated_driver()
    
    if not session_loaded:
        print("No existing session, logging in...")
        from authentication.credential_storage import SecureCredentialStorage
        credential_storage = SecureCredentialStorage()
        credentials = credential_storage.get_user_credentials(user.id, 'eduka')
        
        if credentials:
            scraper.driver = driver
            scraper.login(credentials['username'], credentials['password'])
    else:
        print("✓ Loaded existing session")
        scraper.driver = driver
    
    # Navigate to a page
    print("\nStep 2: Navigate to groups page")
    print("-"*80)
    scraper.driver.get('https://eduka.lt/student/my-groups')
    import time
    time.sleep(3)
    
    # Get cookies
    print("\nStep 3: Extract session cookies")
    print("-"*80)
    cookies = scraper.driver.get_cookies()
    cookie_dict = {}
    for cookie in cookies:
        cookie_dict[cookie['name']] = cookie['value']
        print(f"  {cookie['name']}: {cookie['value'][:50]}..." if len(cookie['value']) > 50 else f"  {cookie['name']}: {cookie['value']}")
    
    # Test if we can use these cookies with requests
    print("\nStep 4: Test cookies with requests library")
    print("-"*80)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    
    # Set cookies
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', 'eduka.lt'))
    
    # Try to access groups page with requests
    try:
        response = session.get('https://eduka.lt/student/my-groups')
        print(f"  Status: {response.status_code}")
        print(f"  URL: {response.url}")
        print(f"  Content length: {len(response.content)} bytes")
        
        # Check if we're logged in
        if 'my-groups' in response.url and response.status_code == 200:
            print("  ✓ Successfully accessed page with cookies!")
            
            # Try to access an API endpoint
            print("\nStep 5: Try to access API endpoints")
            print("-"*80)
            
            # Common API patterns for Angular apps
            api_endpoints = [
                'https://eduka.lt/api/student/groups',
                'https://eduka.lt/api/groups',
                'https://eduka.lt/api/student/my-groups',
                'https://eduka.lt/fe/api/student/groups',
                'https://eduka.lt/fe/api/groups',
            ]
            
            for endpoint in api_endpoints:
                try:
                    api_response = session.get(endpoint)
                    print(f"\n  {endpoint}")
                    print(f"    Status: {api_response.status_code}")
                    if api_response.status_code == 200:
                        print(f"    ✓ SUCCESS! Content length: {len(api_response.content)}")
                        print(f"    Content preview: {api_response.text[:200]}...")
                        
                        # Save full response
                        with open(f"eduka_api_response_{endpoint.split('/')[-1]}.json", "w", encoding="utf-8") as f:
                            f.write(api_response.text)
                        print(f"    Saved to: eduka_api_response_{endpoint.split('/')[-1]}.json")
                except Exception as e:
                    print(f"    Error: {e}")
        else:
            print("  ❌ Could not access page - cookies might not be valid")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Close driver
    scraper.driver.quit()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\nNext steps:")
    print("  1. Check if any API endpoints returned 200")
    print("  2. Examine the saved JSON files")
    print("  3. Implement requests-based scraper using those endpoints")
    print("\n" + "="*80)

if __name__ == '__main__':
    analyze_eduka_session()
