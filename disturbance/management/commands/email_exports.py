import json
import logging

from django.core.management.base import BaseCommand

from disturbance import settings
from disturbance.components.emails.emails import TemplateEmailBase
from disturbance.components.main.utils import exportModelData, formatExportData
from disturbance.helpers import is_internal
from ledger.accounts.models import EmailUser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("parameters", type=str)
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):
        if "parameters" in options and "user_id" in options:
            user_id = options["user_id"]
            params = json.loads(options["parameters"])
            try:
                user = EmailUser.objects.get(id=user_id)
            except EmailUser.DoesNotExist:
                print("Provided user id not valid")
                logger.Error("Provided user id not valid")
                return
            if is_internal:
                if not (params.get("model")):
                    print("No model provided for export")
                    logger.Error("No model provided for export")
                    return
                model = params["model"]
                if not (params.get("format")):
                    format = "csv"
                else:
                    format = params["format"]
                if not (params.get("num_records")):
                    num_records = settings.MAX_NUM_ROWS_MODEL_EXPORT
                else:
                    num_records = params["num_records"]
                if not (params.get("filters")):
                    filters = {}
                else:
                    filters = json.loads(params["filters"])

                # get records
                export_data = exportModelData(model, filters, num_records)
                file = formatExportData(model, export_data, format)
                attachments = []
                attachments.append(file)
                # email to user
                email = TemplateEmailBase(
                    subject=f"Attached: Disturbance - {model.capitalize()} Report",
                    html_template="disturbance/emails_2/report_attached.html",
                    txt_template="disturbance/emails_2/report_attached.txt",
                )
                to_address = user.email
                context = {"recipient": user, "model": model.capitalize()}
                # Send email
                email.send(to_address, attachments=attachments, context=context)

            else:
                print("User not authorised to receive exports")
                logger.Error("User not authorised to receive exports")
                return
