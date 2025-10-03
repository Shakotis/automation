"""
Test script to verify that the credential verification API works
"""
import requests
import json

# Test the API endpoints
BASE_URL = "http://127.0.0.1:8000/api"

def test_api_endpoints():
    """Test API endpoints without authentication (just to check they're reachable)"""
    print("🔧 Testing API Endpoints")
    print("=" * 50)
    
    # Test endpoints that should return 401 (unauthorized) but not fail to connect
    endpoints_to_test = [
        "/auth/credentials/",
        "/auth/verify-credentials/",
        "/auth/sites/",
        "/auth/user/",
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            print(f"✅ {endpoint} - Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
            elif response.status_code == 401:
                print(f"   ✓ Requires authentication (expected)")
            else:
                print(f"   Response: {response.text[:100]}...")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ {endpoint} - Connection failed: {e}")
        except requests.exceptions.Timeout:
            print(f"⏱️ {endpoint} - Request timed out")
        except Exception as e:
            print(f"⚠️ {endpoint} - Error: {e}")
    
    print("\n🧪 Testing Frontend Connection")
    print("=" * 50)
    
    # Test if frontend can connect to backend
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        print(f"✅ Frontend (http://localhost:3000) - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Frontend not reachable - make sure Next.js is running")
    except Exception as e:
        print(f"⚠️ Frontend error: {e}")

def test_verification_logic():
    """Test the verification service logic separately"""
    print("\n🔍 Testing Verification Logic")
    print("=" * 50)
    
    # Test the verification service directly
    import sys
    import os
    import django
    from pathlib import Path
    
    # Add the backend directory to Python path
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework_scraper.settings')
    django.setup()
    
    from authentication.verification_service import CredentialVerificationService
    
    verification_service = CredentialVerificationService()
    
    # Test with invalid credentials (should fail gracefully)
    print("Testing with invalid credentials...")
    
    try:
        success, message = verification_service.verify_eduka_credentials(
            "test_user", "test_password", "https://eduka.lt/auth"
        )
        print(f"Eduka test result: {success}, message: {message}")
    except Exception as e:
        print(f"Eduka test error: {e}")
    
    try:
        success, message = verification_service.verify_manodienynas_credentials(
            "test_user", "test_password"
        )
        print(f"Manodienynas test result: {success}, message: {message}")
    except Exception as e:
        print(f"Manodienynas test error: {e}")

if __name__ == "__main__":
    print("🚀 Homework Scraper API & Verification Test")
    print("=" * 60)
    
    test_api_endpoints()
    
    try:
        test_verification_logic()
    except Exception as e:
        print(f"\n⚠️ Verification test failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("\n📋 Next steps:")
    print("1. Make sure both servers are running:")
    print("   - Backend: http://127.0.0.1:8000/")
    print("   - Frontend: http://localhost:3000/")
    print("2. Test the actual verification in the web interface")
    print("3. Use real credentials for actual verification")
    print("\n💡 Tips:")
    print("- The 'Failed to fetch' error should be resolved with CORS settings")
    print("- The 'element not interactable' error should be fixed with improved Selenium logic")
    print("- Make sure Chrome/ChromeDriver is properly installed for verification")