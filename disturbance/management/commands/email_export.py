from django.core.management.base import BaseCommand
import json

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--model", type=str)
        parser.add_argument("--filters", required=False, type=str)

    def email_export_data_async(self,**options):
        if "model" in options:
            print(options["model"])
            if "filters" in options:
                print(options["filters"])
                print(json.loads(options["filters"]))

    def handle(self, *args, **options):
        self.email_export_data_async(**options)
