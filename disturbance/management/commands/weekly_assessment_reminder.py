from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from django.conf import settings
from disturbance.components.proposals.models import Proposal
from disturbance.components.main.models import GlobalSettings
from disturbance.components.proposals.email import send_assessment_reminder_email_notification
from ledger.accounts.models import EmailUser
import datetime

import itertools

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send weekly notification emails for proposals which has not been assessed yet and assessment reminder has sent.'

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email=settings.CRON_EMAIL)
        except:
            user = EmailUser.objects.create(email=settings.CRON_EMAIL, password = '')

        errors = []
        updates = []
        today = timezone.localtime(timezone.now()).date()
        logger.info('Running command {}'.format(__name__))
        
        #Send weekly reminder after ther first reminder if the Proposal is still pending for assessement    
        weekly_reminder_conditions = {
            'processing_status': 'with_assessor',
            'assessment_reminder_sent': True,
            'assigned_officer__isnull': True,
        }
        assessment_days_record= GlobalSettings.objects.filter(key='assessment_reminder_days')
        if assessment_days_record:
            assessment_days_record=assessment_days_record[0]
            assessment_reminder_days=assessment_days_record.value
            assessment_reminder_days=int(assessment_reminder_days)
        else:
            assessment_reminder_days= settings.ASSESSMENT_REMINDER_DAYS
        apiary_proposal_types=['Apiary','Site Transfer','Temporary Use']
        qs=Proposal.objects.filter(**weekly_reminder_conditions).exclude(application_type__name__in=apiary_proposal_types)
        for proposal in qs:
            compare_date=None
            if proposal.lodgement_date:
                if proposal.weekly_reminder_sent_date:
                    compare_date=proposal.weekly_reminder_sent_date + timedelta(days=7)
                    if compare_date < today:
                        try:
                            send_assessment_reminder_email_notification(proposal)
                            proposal.weekly_reminder_sent_date=today
                            proposal.save()
                            logger.info('sending weekly reminder Proposal {}'.format(proposal.lodgement_number))
                            updates.append(proposal.lodgement_number)
                        except Exception as e:
                            err_msg = 'Error sending weekly reminder Proposal {}'.format(proposal.lodgement_number)
                            logger.error('{}\n{}'.format(err_msg, str(e)))
                            errors.append(err_msg)

                else: 
                    compare_date=proposal.lodgement_date.date() + timedelta(days=assessment_reminder_days)+ timedelta(days=7)
                    if compare_date < today:
                        try:
                            send_assessment_reminder_email_notification(proposal)
                            proposal.weekly_reminder_sent_date=today
                            proposal.save()
                            updates.append(proposal.lodgement_number)
                        except Exception as e:
                            err_msg = 'Error sending weekly reminder Proposal {}'.format(proposal.lodgement_number)
                            logger.error('{}\n{}'.format(err_msg, str(e)))
                            errors.append(err_msg)

        cmd_name = __name__.split('.')[-1].replace('_', ' ').upper()
        err_str = '<strong style="color: red;">Errors: {}</strong>'.format(len(errors)) if len(errors)>0 else '<strong style="color: green;">Errors: 0</strong>'
        msg = '<p>{} completed. {}. IDs updated: {}.</p>'.format(cmd_name, err_str, updates)
        logger.info(msg)
        print(msg) # will redirect to cron_tasks.log file, by the parent script
