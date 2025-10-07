"""
Celery tasks for automated homework scraping.
"""
from celery import shared_task
from django.contrib.auth.models import User
from scraper.scrapers_simple import HomeworkScrapingService
from tasks.services import GoogleTasksService
import logging

logger = logging.getLogger(__name__)


@shared_task(name='scraper.tasks.scrape_all_homework')
def scrape_all_homework():
    """
    Scrape homework for all users and sync to Google Tasks.
    This task is scheduled to run automatically:
    - Every 2 hours from 9am to 1pm (9am, 11am, 1pm)
    - Every hour from 1pm to 4pm (1pm, 2pm, 3pm, 4pm)
    """
    logger.info("Starting automated homework scraping for all users")
    
    users = User.objects.all()
    total_scraped = 0
    total_synced = 0
    total_errors = 0
    
    for user in users:
        try:
            logger.info(f"Processing user: {user.email}")
            
            # Scrape homework
            scraping_service = HomeworkScrapingService(user)
            homework_list = scraping_service.scrape_all_sites()
            scraped_count = len(homework_list)
            total_scraped += scraped_count
            
            logger.info(f"  Scraped {scraped_count} homework items for {user.email}")
            
            # Sync to Google Tasks (if user has OAuth connected)
            try:
                if hasattr(user, 'googleoauth') and user.googleoauth:
                    tasks_service = GoogleTasksService(user)
                    sync_result = tasks_service.sync_homework_to_tasks()
                    synced_count = sync_result.get('synced_count', 0)
                    total_synced += synced_count
                    
                    logger.info(f"  Synced {synced_count} items to Google Tasks for {user.email}")
                    
                    if sync_result.get('errors'):
                        for error in sync_result['errors']:
                            logger.warning(f"  Sync error for {user.email}: {error}")
                else:
                    logger.info(f"  User {user.email} does not have Google OAuth connected, skipping sync")
                    
            except Exception as e:
                logger.error(f"  Sync failed for {user.email}: {str(e)}")
                total_errors += 1
                
        except Exception as e:
            logger.error(f"Error processing {user.email}: {str(e)}")
            total_errors += 1
    
    # Log summary
    logger.info(
        f"Automated scraping completed. "
        f"Total scraped: {total_scraped}, "
        f"Total synced: {total_synced}, "
        f"Errors: {total_errors}"
    )
    
    return {
        'total_scraped': total_scraped,
        'total_synced': total_synced,
        'total_errors': total_errors,
    }


@shared_task(name='scraper.tasks.scrape_user_homework')
def scrape_user_homework(user_id):
    """
    Scrape homework for a specific user.
    
    Args:
        user_id: The ID of the user to scrape homework for
    """
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"Starting homework scraping for user: {user.email}")
        
        # Scrape homework
        scraping_service = HomeworkScrapingService(user)
        homework_list = scraping_service.scrape_all_sites()
        scraped_count = len(homework_list)
        
        logger.info(f"Scraped {scraped_count} homework items for {user.email}")
        
        # Sync to Google Tasks (if user has OAuth connected)
        synced_count = 0
        if hasattr(user, 'googleoauth') and user.googleoauth:
            try:
                tasks_service = GoogleTasksService(user)
                sync_result = tasks_service.sync_homework_to_tasks()
                synced_count = sync_result.get('synced_count', 0)
                logger.info(f"Synced {synced_count} items to Google Tasks for {user.email}")
            except Exception as e:
                logger.error(f"Sync failed for {user.email}: {str(e)}")
        
        return {
            'user_id': user_id,
            'scraped_count': scraped_count,
            'synced_count': synced_count,
        }
        
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error scraping homework for user {user_id}: {str(e)}")
        raise
