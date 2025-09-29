from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from scraper.scrapers import HomeworkScrapingService
from tasks.services import GoogleTasksService

class Command(BaseCommand):
    help = 'Scrape homework for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Scrape homework for specific user ID only',
        )
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Also sync to Google Tasks after scraping',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        sync_tasks = options.get('sync')

        if user_id:
            try:
                users = [User.objects.get(id=user_id)]
                self.stdout.write(f"Scraping homework for user ID {user_id}")
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"User with ID {user_id} does not exist")
                )
                return
        else:
            users = User.objects.all()
            self.stdout.write(f"Scraping homework for {users.count()} users")

        total_scraped = 0
        total_synced = 0

        for user in users:
            try:
                self.stdout.write(f"Processing user: {user.email}")
                
                # Scrape homework
                scraping_service = HomeworkScrapingService(user)
                homework_list = scraping_service.scrape_all_sites()
                scraped_count = len(homework_list)
                total_scraped += scraped_count
                
                self.stdout.write(f"  Scraped {scraped_count} homework items")

                # Sync to Google Tasks if requested
                if sync_tasks:
                    try:
                        tasks_service = GoogleTasksService(user)
                        sync_result = tasks_service.sync_homework_to_tasks()
                        synced_count = sync_result['synced_count']
                        total_synced += synced_count
                        
                        self.stdout.write(f"  Synced {synced_count} items to Google Tasks")
                        
                        if sync_result['errors']:
                            for error in sync_result['errors']:
                                self.stdout.write(
                                    self.style.WARNING(f"  Sync error: {error}")
                                )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"  Sync failed for {user.email}: {e}")
                        )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing {user.email}: {e}")
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted! Total scraped: {total_scraped}, Total synced: {total_synced}"
            )
        )