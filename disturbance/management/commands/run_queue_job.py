from django.core.management.base import BaseCommand
from disturbance.components.main.models import JobQueue
from django.core import management
from datetime import datetime
from disturbance.settings import NUMBER_OF_QUEUE_JOBS
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        #get n number of jobs at top of queue
        job_queue = JobQueue.objects.filter(status=0)[:NUMBER_OF_QUEUE_JOBS]

        for jq in job_queue:
            #set to running
            jq.status = 1
            jq.save()
            #run job (catch errors)
            try:
                parameters = json.dumps(jq.parameters_json)           
            except Exception as e:
                jq.status = 3
                jq.save()
                print(e)
                continue

            #set to complete or error
            try:     
                management.call_command(jq.job_cmd, parameters, jq.user)
                print("Job Completed {}".format(str(jq.id)))                
                jq.processed_dt = datetime.now()
                jq.status = 2
                jq.save()
            except Exception as e:                
                print("run_queue_job error",e)
                jq.status = 3
                jq.save()
