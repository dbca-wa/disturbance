import csv
import logging
from datetime import datetime
from io import (
    BytesIO,
)

from django.conf import settings
from django.core.management.base import BaseCommand

from disturbance.components.approvals.models import Proposal
from disturbance.components.emails.email import TemplateEmailBase

logger = logging.getLogger(__name__)


class LayersUsedEmail(TemplateEmailBase):
    subject = "DAS - Layers Used CSV"


class Command(BaseCommand):
    help = "Run the Disturbance Layers User script"

    def handle(self, *args, **options):
        self.stdout.write(f"Running command {__name__}")

        try:
            # Use BytesIO and encode to utf-8 for robust email attachment handling
            csvfile = BytesIO()
            # Wrap with TextIOWrapper so csv.writer can write strings to BytesIO
            import codecs

            wrapper = codecs.getwriter("utf-8")(csvfile)
            csvwriter = csv.writer(wrapper)

            csvwriter.writerow(
                (
                    "Proposal Number",
                    "Proposal Submitter",
                    "Status",
                    "Proposal Section",
                    "Layer Name",
                    "Layer Version",
                    "Layer Modified Date",
                    "SQS Timestamp",
                )
            )

            proposals = Proposal.objects.filter(
                layer_data__isnull=False,
                processing_status=Proposal.PROCESSING_STATUS_APPROVED,
            )

            row_count = 0
            for p in proposals:
                for data in p.layer_data:
                    csvwriter.writerow(
                        (
                            p.lodgement_number,
                            p.submitter,
                            p.processing_status,
                            data.get("name"),
                            data.get("layer_name"),
                            data.get("layer_version"),
                            data.get("layer_modified_date"),
                            data.get("sqs_timestamp"),
                        )
                    )
                    row_count += 1

            context = {
                "description": (
                    "CSV file for Layers used in proposal applications, where:\n"
                    "\t1. Proposal polygon/layer(s) exist (DAS Phase 2),\n"
                    "\t2. Approved proposals"
                )
            }
            filename = f"layers_used_{datetime.now().strftime('%Y%m%dT%H%M')}.csv"

            # Get value from BytesIO
            attachments = [(filename, csvfile.getvalue(), "text/csv")]

            email_obj = LayersUsedEmail()
            email_obj.send(
                to_addresses=[settings.NOTIFICATION_EMAIL],
                from_address=settings.EMAIL_FROM,
                context=context,
                attachments=attachments,
            )

            self.stdout.write(
                f"Command {__name__} completed successfully ({row_count} rows processed)."
            )

        except Exception as e:
            logger.exception(f"An error occurred while running {__name__}: {e}")
            raise
