from django.core.management.base import BaseCommand
from cryptography.fernet import Fernet


class Command(BaseCommand):
    help = 'Generate a new Fernet encryption key for credential storage'

    def handle(self, *args, **options):
        key = Fernet.generate_key()
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('Generated Fernet Encryption Key'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'\n{key.decode()}\n')
        self.stdout.write(self.style.WARNING('\nIMPORTANT: Save this key securely!'))
        self.stdout.write(self.style.WARNING('Add it to your environment variables as ENCRYPTION_KEY'))
        self.stdout.write(self.style.WARNING('\nFor Render.com:'))
        self.stdout.write(self.style.WARNING('1. Go to your service → Environment'))
        self.stdout.write(self.style.WARNING('2. Add environment variable: ENCRYPTION_KEY'))
        self.stdout.write(self.style.WARNING(f'3. Value: {key.decode()}'))
        self.stdout.write(self.style.WARNING('4. Save changes'))
        self.stdout.write(self.style.SUCCESS('\n' + '='*70 + '\n'))
