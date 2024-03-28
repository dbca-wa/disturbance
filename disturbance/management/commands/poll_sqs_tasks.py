from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from ledger.accounts.models import EmailUser
from disturbance.components.proposals.api import get_sqs_url
from disturbance.components.main.models import TaskMonitor
from disturbance.components.proposals.models import Proposal
from disturbance.components.proposals.email import (
    send_proposal_prefill_completed_email_notification,
    send_proposal_prefill_error_email_notification,
    )


from datetime import datetime
import pytz
import itertools
import requests
from requests.auth import HTTPBasicAuth

import logging
logger = logging.getLogger(__name__)


class PollSqsTasksException(Exception):
    #pass
    def __init__(self, value):
        self.value = value
 
    def __str__(self):
        return(repr(self.value))


class Command(BaseCommand):
    help = 'Polls the SQS application to check for completed proposal tasks.'

    def handle(self, *args, **options):
        '''
        1. Loop through all CREATED tasks in TaskMonitor (queued_jobs), get task_ids for status=CREATED
        2. retrieve sqs_tasks from SQS for given task_ids (tasks/get_tasks/?task_ids={task_ids_str})
        3. for each sqs_task (from SQS), retrieve the sqs_task request_log from SQS, this has the status of the task on SQS
        4. if sqs_task status=COMPLETED, update Proposal obj. Also update status in TaskMonitor
        '''

        def get_sqs_task(task_id):
            for sqs_task in sqs_tasks:
                if sqs_task['id'] == task_id:
                    return sqs_task
            return None

        def update_retries(msg):
            task.retries = task.retries + 1
            if task.retries == settings.SQS_POLLING_MAX_RETRIES:
                task.status = TaskMonitor.STATUS_MAX_RETRIES_REACHED
                task.info = f'Retry {task.retries}: {msg}.'
                send_proposal_prefill_error_email_notification(task.proposal, task.id)
            task.save()

        msg = None
        try:
            task_ids = list(TaskMonitor.queued_jobs.all().values_list('task_id', flat=True))
            
            if len(task_ids) > 0:
                task_ids_str = ','.join(map(str, task_ids))
                url = get_sqs_url(f'tasks/get_tasks/?task_ids={task_ids_str}')
                resp_tasks = requests.get(url=url, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS))

                if resp_tasks.status_code != 200:
                    raise Exception(f'API Call: error getting tasks from SQS: {resp_tasks.status_code}, url: {url}')

                sqs_tasks = resp_tasks.json()
                for task_id in task_ids:
                    task = TaskMonitor.queued_jobs.get(task_id=task_id)
                    sqs_task = get_sqs_task(task_id)
                    if sqs_task:
                        if sqs_task['status'] == TaskMonitor.STATUS_COMPLETED:
                            if sqs_task['request_log'] is None:
                                msg = f'Unable to process task_id {task_id}. Request Log is not available'
                                logger.warn(msg)
                                update_retries(msg)
                            else:
                                proposal = self.update_proposal(sqs_task)
                                if proposal:
                                    task.status = TaskMonitor.STATUS_COMPLETED
                                    task.save()
                                    user = send_proposal_prefill_completed_email_notification(proposal)
                                else:
                                    msg = f'Unable to update proposal, task_id {task_id}'
                                    update_retries(msg)

                        elif sqs_task['status'] in [TaskMonitor.STATUS_CREATED, TaskMonitor.STATUS_RUNNING]:
                            msg = f'task_id {task_id} - current status \'{sqs_task["status"]}\' on SQS'
                            logger.info(msg)

                        elif sqs_task['status'] != TaskMonitor.STATUS_CREATED:
                            # this task on SQS may have status ERROR/FAILED - update local TaskMonitor with the same
                            task.status = sqs_task['status']
                            task.save()
                            send_proposal_prefill_error_email_notification(task.proposal, task.id)

                        else:
                            msg = f'Unable to process task_id {task_id}'
                            logger.warn(msg)
                            update_retries(msg)

                    else:
                        msg = f'task_id {task_id} not found in SQS API request'
                        logger.warn(msg)
                        update_retries(msg)

        except Exception as e: 
            msg = f'{e}'
            logger.error(msg)
            update_retries(msg)


    def update_proposal(self, payload):
        ''' Payload is the response from SQS API call, containing results from the shapefile/layer intersection 
        '''
        try:
            required_payload_keys = ['app_id', 'request_log']
            if not all(key in payload.keys() for key in required_payload_keys):
                raise Exception(f'Missing keys in payload from API call to SQS: {payload.keys()}')

            res = payload['request_log']
            required_response_keys = ['data', 'layer_data', 'add_info_assessor', 'when']
            if not all(key in res.keys() for key in required_response_keys):
                raise Exception(f'Missing keys in payload from API call to SQS: {res.keys()}')

            proposal = Proposal.objects.get(id=payload['app_id'])
            if res['data']:
                proposal.data=res['data']
            if res['layer_data']:
                proposal.layer_data=res['layer_data']
            if res['add_info_assessor']:
                proposal.history_add_info_assessor = proposal.get_history_add_info_assessor()
                #print(proposal.history_add_info_assessor)
                proposal.add_info_assessor= res['add_info_assessor']
            if res['when']:
                when = datetime.strptime(res['when'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=pytz.utc)
                proposal.prefill_timestamp=when

            proposal.save(version_comment='Prefill Proposal')
            proposal.log_metrics(when, res, proposal.id)
            return proposal
        except PollSqsTasksException as e: 
            raise PollSqsTasksException(e)

        return None


