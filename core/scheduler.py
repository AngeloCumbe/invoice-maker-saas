# core/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
import logging

from .models import Invoice

logger = logging.getLogger(__name__)


@util.close_old_connections
def update_overdue_invoices():
    """
    Job function to update overdue invoices.
    Runs automatically every hour.
    """
    try:
        now = timezone.now()
        
        # Find all 'sent' invoices that are past due date
        overdue_invoices = Invoice.objects.filter(
            status='sent',
            due_date__lt=now
        )
        
        updated_count = 0
        for invoice in overdue_invoices:
            invoice.status = 'overdue'
            invoice.save(update_fields=['status', 'last_modified_timestamp'])
            updated_count += 1
            logger.info(f'Updated invoice {invoice.invoice_number} to overdue')
        
        if updated_count > 0:
            logger.info(f'Successfully updated {updated_count} invoice(s) to overdue')
        else:
            logger.info('No invoices to update')
            
    except Exception as e:
        logger.error(f'Error updating overdue invoices: {str(e)}')


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    Delete old job executions (older than 7 days by default).
    This keeps the database clean.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def start_scheduler():
    """
    Start the APScheduler to run background jobs.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Update overdue invoices every hour
    scheduler.add_job(
        update_overdue_invoices,
        trigger=CronTrigger(minute="0"),  # Run at the top of every hour
        id="update_overdue_invoices",
        max_instances=1,
        replace_existing=True,
        name="Update overdue invoices"
    )
    logger.info("Added job 'update_overdue_invoices'.")

    # Clean up old job executions every week
    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(
            day_of_week="mon", hour="00", minute="00"
        ),  # Every Monday at midnight
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
        name="Delete old job executions"
    )
    logger.info("Added weekly job: 'delete_old_job_executions'.")

    try:
        logger.info("Starting scheduler...")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully!")