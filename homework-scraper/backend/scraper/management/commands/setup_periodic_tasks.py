"""
Management command to set up periodic tasks in the database.
This is useful for server deployment with django-celery-beat.
"""
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


class Command(BaseCommand):
    help = 'Set up periodic tasks for automatic homework scraping'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up periodic tasks...'))

        # Define the schedule times
        schedules = [
            {'hour': '9', 'minute': '0', 'name': 'scrape-homework-09am'},
            {'hour': '11', 'minute': '0', 'name': 'scrape-homework-11am'},
            {'hour': '13', 'minute': '0', 'name': 'scrape-homework-01pm'},
            {'hour': '14', 'minute': '0', 'name': 'scrape-homework-02pm'},
            {'hour': '15', 'minute': '0', 'name': 'scrape-homework-03pm'},
            {'hour': '16', 'minute': '0', 'name': 'scrape-homework-04pm'},
        ]

        created_count = 0
        updated_count = 0

        for schedule_info in schedules:
            # Create or get the crontab schedule
            schedule, created = CrontabSchedule.objects.get_or_create(
                minute=schedule_info['minute'],
                hour=schedule_info['hour'],
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
                timezone='Europe/Vilnius'
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Created schedule: {schedule_info["hour"]}:{schedule_info["minute"]}'
                    )
                )

            # Create or update the periodic task
            task, task_created = PeriodicTask.objects.get_or_create(
                name=schedule_info['name'],
                defaults={
                    'task': 'scraper.tasks.scrape_all_homework',
                    'crontab': schedule,
                    'enabled': True,
                    'description': f'Automatic homework scraping at {schedule_info["hour"]}:{schedule_info["minute"]}',
                }
            )

            if task_created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Created task: {schedule_info["name"]}'
                    )
                )
            else:
                # Update existing task
                task.task = 'scraper.tasks.scrape_all_homework'
                task.crontab = schedule
                task.enabled = True
                task.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'  ↻ Updated task: {schedule_info["name"]}'
                    )
                )

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(
            self.style.SUCCESS(
                f'Setup complete! Created: {created_count}, Updated: {updated_count}'
            )
        )
        self.stdout.write(self.style.SUCCESS('\nSchedule Overview:'))
        self.stdout.write('  Morning (9am-1pm): Every 2 hours')
        self.stdout.write('    • 9:00 AM')
        self.stdout.write('    • 11:00 AM')
        self.stdout.write('    • 1:00 PM')
        self.stdout.write('  Afternoon (1pm-4pm): Every hour')
        self.stdout.write('    • 1:00 PM')
        self.stdout.write('    • 2:00 PM')
        self.stdout.write('    • 3:00 PM')
        self.stdout.write('    • 4:00 PM')
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(
            self.style.WARNING(
                '\nNote: Make sure Celery Beat is running with:'
            )
        )
        self.stdout.write('  celery -A homework_scraper beat --loglevel=info')
        self.stdout.write('\n')
