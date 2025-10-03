"""
Script to analyze Eduka network traffic and reverse-engineer API calls
This will help us scrape Eduka without Selenium by using the same API endpoints
"""
import os
import sys
import django
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.credential_storage import SecureCredentialStorage

def analyze_eduka_api():
    """Analyze Eduka network traffic to find API endpoints"""
    
    print("\n" + "="*80)
    print("EDUKA API ANALYZER")
    print("="*80)
    print("\nThis script will:")
    print("  1. Login to Eduka using Selenium")
    print("  2. Capture all network requests")
    print("  3. Identify API endpoints used")
    print("  4. Show you how to replicate without Selenium")
    
    # Get user credentials
    user = User.objects.get(email='dovydasjusevicius@gmail.com')
    credential_storage = SecureCredentialStorage()
    credentials = credential_storage.get_user_credentials(user.id, 'eduka')
    
    if not credentials:
        print("\n❌ No Eduka credentials found")
        return
    
    username = credentials['username']
    password = credentials['password']
    
    print(f"\n✓ Found credentials for: {username}")
    
    # Enable network logging in Chrome
    capabilities = DesiredCapabilities.CHROME
    capabilities['goog:loggingPrefs'] = {'performance': 'ALL', 'browser': 'ALL'}
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    print("\n" + "-"*80)
    print("Starting Chrome with network logging...")
    print("-"*80)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to auth page
        auth_url = 'https://eduka.lt/auth'
        print(f"\n📍 Navigating to: {auth_url}")
        driver.get(auth_url)
        time.sleep(5)
        
        # Login
        print(f"\n🔐 Logging in as: {username}")
        wait = WebDriverWait(driver, 20)
        
        username_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
        password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        time.sleep(1)
        
        # Find and click submit - try multiple selectors
        print("🔍 Looking for submit button...")
        submit_button = None
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, 'app-auth-login-form button[type="submit"]')
            print("   Found with CSS: app-auth-login-form button[type='submit']")
        except:
            try:
                submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Prisijungti') or contains(text(), 'Login')]")
                print("   Found with XPath (text-based)")
            except:
                print("   ❌ Could not find submit button")
                driver.save_screenshot("eduka_login_debug.png")
                print("   Saved screenshot to eduka_login_debug.png")
                raise Exception("Submit button not found")
        
        if submit_button:
            submit_button.click()
        
        print("⏳ Waiting for login to complete...")
        time.sleep(5)
        
        # Navigate to groups page
        groups_url = 'https://eduka.lt/student/my-groups'
        print(f"\n📍 Navigating to: {groups_url}")
        driver.get(groups_url)
        time.sleep(5)
        
        # Get first group link
        group_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/my-groups/"][href*="/recipient-assignment"]')
        if group_links:
            group_url = group_links[0].get_attribute('href')
            print(f"\n📍 Navigating to group: {group_url}")
            driver.get(group_url)
            time.sleep(5)
        
        # Analyze network logs
        print("\n" + "="*80)
        print("ANALYZING NETWORK TRAFFIC")
        print("="*80)
        
        logs = driver.get_log('performance')
        
        api_calls = []
        auth_calls = []
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])
                message = log['message']
                method = message.get('method')
                
                if method == 'Network.requestWillBeSent':
                    request = message['params']['request']
                    url = request['url']
                    req_method = request['method']
                    headers = request.get('headers', {})
                    
                    # Filter for API calls
                    if 'eduka.lt' in url and any(keyword in url for keyword in ['api', 'auth', 'student', 'group', 'assignment']):
                        if req_method in ['POST', 'GET', 'PUT']:
                            api_calls.append({
                                'method': req_method,
                                'url': url,
                                'headers': headers,
                            })
                    
                    # Capture authentication calls
                    if 'auth' in url.lower() or 'login' in url.lower():
                        auth_calls.append({
                            'method': req_method,
                            'url': url,
                            'headers': headers,
                            'hasData': 'hasPostData' in request,
                        })
                
                elif method == 'Network.responseReceived':
                    response = message['params']['response']
                    url = response['url']
                    status = response['status']
                    headers = response.get('headers', {})
                    
                    # Check for authentication responses
                    if 'auth' in url.lower() and status == 200:
                        # Check if response has a token
                        if 'set-cookie' in str(headers).lower() or 'authorization' in str(headers).lower():
                            print(f"\n🔑 Found auth response:")
                            print(f"   URL: {url}")
                            print(f"   Status: {status}")
                            if 'set-cookie' in headers:
                                print(f"   Cookies: {headers.get('set-cookie', 'N/A')}")
                            if 'authorization' in headers:
                                print(f"   Auth: {headers.get('authorization', 'N/A')}")
                            
            except Exception as e:
                continue
        
        # Print authentication calls
        print("\n" + "-"*80)
        print("AUTHENTICATION CALLS FOUND:")
        print("-"*80)
        if auth_calls:
            for i, call in enumerate(auth_calls, 1):
                print(f"\n{i}. {call['method']} {call['url']}")
                if 'authorization' in call['headers']:
                    print(f"   Authorization: {call['headers']['authorization']}")
                if 'content-type' in call['headers']:
                    print(f"   Content-Type: {call['headers']['content-type']}")
        else:
            print("No authentication calls found")
        
        # Print API calls
        print("\n" + "-"*80)
        print("API CALLS FOUND:")
        print("-"*80)
        if api_calls:
            # Deduplicate URLs
            unique_urls = {}
            for call in api_calls:
                key = f"{call['method']} {call['url']}"
                if key not in unique_urls:
                    unique_urls[key] = call
            
            for i, call in enumerate(unique_urls.values(), 1):
                print(f"\n{i}. {call['method']} {call['url']}")
                if 'authorization' in call['headers']:
                    print(f"   Authorization: Present (Bearer token?)")
                if 'content-type' in call['headers']:
                    print(f"   Content-Type: {call['headers']['content-type']}")
        else:
            print("No API calls found")
        
        # Check cookies
        print("\n" + "-"*80)
        print("COOKIES:")
        print("-"*80)
        cookies = driver.get_cookies()
        for cookie in cookies:
            print(f"  {cookie['name']}: {cookie['value'][:50]}..." if len(cookie['value']) > 50 else f"  {cookie['name']}: {cookie['value']}")
        
        # Check for window state
        print("\n" + "-"*80)
        print("CHECKING FOR INITIAL STATE IN WINDOW:")
        print("-"*80)
        try:
            initial_state = driver.execute_script("return window.__INITIAL_STATE__ || window.__STATE__ || window.INITIAL_STATE || null")
            if initial_state:
                print("✓ Found initial state in window object!")
                print(f"  Keys: {list(initial_state.keys()) if isinstance(initial_state, dict) else 'Not a dict'}")
            else:
                print("❌ No initial state found in window object")
        except Exception as e:
            print(f"❌ Error checking window state: {e}")
        
        # Check local storage
        print("\n" + "-"*80)
        print("LOCAL STORAGE:")
        print("-"*80)
        try:
            local_storage = driver.execute_script("""
                var items = {};
                for (var i = 0; i < localStorage.length; i++) {
                    var key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
            """)
            if local_storage:
                for key, value in local_storage.items():
                    print(f"  {key}: {value[:100]}..." if len(str(value)) > 100 else f"  {key}: {value}")
            else:
                print("  (empty)")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Summary and recommendations
        print("\n" + "="*80)
        print("RECOMMENDATIONS FOR REQUESTS-BASED SCRAPER:")
        print("="*80)
        
        if auth_calls:
            print("\n1. AUTHENTICATION:")
            print("   Use the identified auth endpoint(s) above")
            print("   Method: POST with username/password")
            print("   Capture cookies or tokens from response")
        
        if api_calls:
            print("\n2. DATA FETCHING:")
            print("   Use the API endpoints identified above")
            print("   Include authentication cookies/tokens in headers")
        
        print("\n3. NEXT STEPS:")
        print("   a) Test the auth endpoint with requests.post()")
        print("   b) Extract and store session cookies/tokens")
        print("   c) Use those tokens to call data API endpoints")
        print("   d) Parse JSON responses instead of HTML")
        
    finally:
        print("\n" + "-"*80)
        print("Cleaning up...")
        print("-"*80)
        driver.quit()
        print("✓ Browser closed")
        print("\n" + "="*80)

if __name__ == '__main__':
    analyze_eduka_api()
