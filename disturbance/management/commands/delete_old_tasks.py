from django.core.management.base import BaseCommand
from django.conf import settings

from datetime import datetime, timedelta
from django.utils import timezone

from disturbance.components.main.models import TaskMonitor

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = f'Clears old tasks to prevent unnecessary growth of TaskMonitor table (> {settings.MAX_TASK_HISTORY} days)'

    def handle(self, *args, **options):

        task_ids = []
        errors = []
        earliest_date = (datetime.now() - timedelta(days=settings.MAX_TASK_HISTORY)).replace(tzinfo=timezone.utc)
        logger.info('Running command {}'.format(__name__))

        try:
            # delete all tasks created earlier than 'earliest date'
            old_tasks_qs = TaskMonitor.objects.filter(status=TaskMonitor.STATUS_CREATED, created__lte=earliest_date)
            task_ids = list(old_tasks_qs.values_list('id', flat=True))
            old_tasks_qs.delete()

            logger.info(f'Old tasks deleted {task_ids}')
        except Exception as e:
            err_msg = f'Error deleting old tasks {e}'
            logger.error(err_msg)
            errors.append(err_msg)

        cmd_name = __name__.split('.')[-1].replace('_', ' ').upper()
        err_str = '<strong style="color: red;">Errors: {}</strong>'.format(len(errors)) if len(errors)>0 else '<strong style="color: green;">Errors: 0</strong>'
        msg = '<p>{} completed. {}. Deleted IDs: {}</p>'.format(cmd_name, err_str, task_ids)
        logger.info(msg)
        print(msg) # will redirect to cron_tasks.log file, by the parent script

