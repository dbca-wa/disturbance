from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from pathlib import Path
from disturbance.components.approvals.models import Approval
from ledger.accounts.models import EmailUser
import datetime

import itertools
import subprocess

import logging
logger = logging.getLogger(__name__)

LOGFILE = 'logs/cron_tasks.log'

class Command(BaseCommand):
    help = 'Run the Disturbance Cron tasks'

    def handle(self, *args, **options):
        stdout_redirect = ' | tee -a {}'.format(LOGFILE)
        subprocess.call('cat /dev/null > {}'.format(LOGFILE), shell=True)  # empty the log file

        logger.info('Running command {}'.format(__name__))
        subprocess.call('python manage_ds.py update_compliance_status' + stdout_redirect, shell=True) 
        subprocess.call('python manage_ds.py send_compliance_reminder' + stdout_redirect, shell=True) 
        subprocess.call('python manage_ds.py update_approval_status' + stdout_redirect, shell=True) 
        subprocess.call('python manage_ds.py expire_approvals' + stdout_redirect, shell=True) 
        subprocess.call('python manage_ds.py approval_renewal_notices' + stdout_redirect, shell=True) 
        subprocess.call('python manage_ds.py send_assessment_reminder' + stdout_redirect, shell=True)
        subprocess.call('python manage_ds.py weekly_assessment_reminder' + stdout_redirect, shell=True)
        subprocess.call('python manage_ds.py send_annual_rental_fee_invoice' + stdout_redirect, shell=True)
        subprocess.call('python manage_ds.py save_apiary_sites' + stdout_redirect, shell=True)

        # TaskMonitor jobs
        subprocess.call('python manage_ds.py delete_old_tasks' + stdout_redirect, shell=True) 
        subprocess.call('python manage_ds.py update_queued_tasks' + stdout_redirect, shell=True) 

        logger.info('Command {} completed'.format(__name__))
        self.send_email()

    def send_email(self):
        log_txt = Path(LOGFILE).read_text()
        #subject = '{} - Cronjob'.format(settings.SYSTEM_NAME_SHORT)
        subject = 'DAS-Apiary - Cronjob'.format(settings.SYSTEM_NAME_SHORT)
        body = ''
        to = settings.CRON_NOTIFICATION_EMAIL if isinstance(settings.NOTIFICATION_EMAIL, list) else [settings.CRON_NOTIFICATION_EMAIL]
        send_mail(subject, body, settings.EMAIL_FROM, to, fail_silently=False, html_message=log_txt)
