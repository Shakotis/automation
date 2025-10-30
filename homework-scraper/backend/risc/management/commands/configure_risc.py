import json
import time
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from django.core.management.base import BaseCommand
from django.conf import settings
from risc.models import RISCConfiguration
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Configure RISC stream with Google'

    def add_arguments(self, parser):
        parser.add_argument(
            '--service-account',
            type=str,
            help='Path to service account JSON file',
            required=True
        )
        parser.add_argument(
            '--receiver-url',
            type=str,
            help='HTTPS URL for RISC event receiver endpoint',
            required=True
        )
        parser.add_argument(
            '--verify-only',
            action='store_true',
            help='Only send verification event, do not configure stream'
        )
        parser.add_argument(
            '--disable',
            action='store_true',
            help='Disable the RISC stream'
        )

    def get_access_token(self, service_account_file):
        """Generate access token from service account"""
        try:
            # Try with cloud-platform scope which has broader access
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Refresh to get access token
            credentials.refresh(Request())
            
            if not credentials.token:
                self.stdout.write(self.style.ERROR("No access token received"))
                self.stdout.write(self.style.WARNING("Trying alternative method with RISC scope..."))
                
                # Try with RISC-specific scope
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_file,
                    scopes=['https://www.googleapis.com/auth/risc']
                )
                credentials.refresh(Request())
            
            return credentials.token
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to get access token: {e}"))
            self.stdout.write(self.style.WARNING("\nPlease ensure:"))
            self.stdout.write("1. RISC API is enabled in Google Cloud Console")
            self.stdout.write("2. Service account has 'RISC Configuration Admin' role")
            self.stdout.write("3. Service account has 'Service Account Token Creator' role")
            raise

    def configure_stream(self, access_token, receiver_url, enable=True, verify_only=False):
        """Configure RISC stream via Google API"""
        
        # Get current configuration
        config = RISCConfiguration.objects.filter(is_active=True).first()
        if not config:
            self.stdout.write(self.style.ERROR("No RISC configuration found in database"))
            return False
        
        if verify_only:
            # Send verification event
            self.stdout.write("Sending verification event...")
            return self.send_verification(access_token, receiver_url)
        
        # Prepare stream configuration
        stream_config = {
            "delivery": {
                "delivery_method": "https://schemas.openid.net/secevent/risc/delivery-method/push",
                "url": receiver_url
            },
            "events_requested": config.get_subscribed_events()
        }
        
        if not enable:
            stream_config["status"] = "disabled"
        else:
            stream_config["status"] = "enabled"
        
        # Update stream configuration
        url = "https://risc.googleapis.com/v1beta/stream:update"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        self.stdout.write(f"Configuring RISC stream...")
        self.stdout.write(f"Receiver URL: {receiver_url}")
        self.stdout.write(f"Status: {'enabled' if enable else 'disabled'}")
        self.stdout.write(f"Subscribed events: {len(config.get_subscribed_events())}")
        
        try:
            response = requests.post(url, headers=headers, json=stream_config)
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("Stream configured successfully!"))
                
                # Update database
                config.stream_enabled = enable
                config.receiver_endpoint = receiver_url
                config.save()
                
                return True
            else:
                self.stdout.write(self.style.ERROR(f"Failed to configure stream: {response.status_code}"))
                self.stdout.write(self.style.ERROR(f"Response: {response.text}"))
                
                # Handle common errors
                if response.status_code == 400:
                    self.stdout.write(self.style.WARNING("Bad request - check receiver URL and event types"))
                elif response.status_code == 401:
                    self.stdout.write(self.style.WARNING("Unauthorized - check service account credentials"))
                elif response.status_code == 403:
                    self.stdout.write(self.style.WARNING("Forbidden - ensure service account has RISC Configuration Admin role"))
                elif response.status_code == 404:
                    self.stdout.write(self.style.WARNING("Not found - verify RISC API is enabled"))
                
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error configuring stream: {e}"))
            return False

    def send_verification(self, access_token, receiver_url):
        """Send verification event to test receiver endpoint"""
        
        url = "https://risc.googleapis.com/v1beta/stream:verify"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Generate unique state for verification
        state = f"verify_{int(time.time())}"
        
        data = {
            "state": state
        }
        
        self.stdout.write(f"Sending verification to: {receiver_url}")
        self.stdout.write(f"Verification state: {state}")
        
        try:
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("Verification event sent!"))
                self.stdout.write("Check your receiver endpoint logs to confirm receipt")
                return True
            else:
                self.stdout.write(self.style.ERROR(f"Failed to send verification: {response.status_code}"))
                self.stdout.write(self.style.ERROR(f"Response: {response.text}"))
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error sending verification: {e}"))
            return False

    def handle(self, *args, **options):
        service_account_file = options['service_account']
        receiver_url = options['receiver_url']
        verify_only = options['verify_only']
        disable = options['disable']
        
        try:
            # Validate receiver URL
            if not receiver_url.startswith('https://'):
                self.stdout.write(self.style.ERROR("Receiver URL must use HTTPS"))
                return
            
            self.stdout.write("Getting access token...")
            access_token = self.get_access_token(service_account_file)
            
            if verify_only:
                success = self.send_verification(access_token, receiver_url)
            else:
                success = self.configure_stream(access_token, receiver_url, enable=not disable, verify_only=verify_only)
            
            if success:
                self.stdout.write(self.style.SUCCESS("\nRISC configuration completed!"))
            else:
                self.stdout.write(self.style.ERROR("\nRISC configuration failed"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Command failed: {e}"))
            import traceback
            self.stdout.write(traceback.format_exc())
