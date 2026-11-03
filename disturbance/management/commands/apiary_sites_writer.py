import logging
from datetime import datetime
from io import BytesIO

import xlsxwriter
from django.conf import settings
from django.core.management.base import BaseCommand

from disturbance.components.approvals.models import ApiarySiteOnApproval
from disturbance.components.emails.email import TemplateEmailBase

logger = logging.getLogger(__name__)


class ApiarySitesEmail(TemplateEmailBase):
    # Subject can be dynamic, but we can set a default or override it in handle()
    subject = "Apiary Sites List"


class Command(BaseCommand):
    help = (
        "Write Apiary Sites to Excel file and email the file as an attachment "
        '(defaults to settings.APIARY_SUPPORT_EMAIL), python manage_ds.py apiary_sites_writer --org_name "Western Honey"'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--org_name", type=str, help="Organisation Name", required=False
        )

    def handle(self, *args, **options):
        self.stdout.write(f"Running command {__name__}")

        try:
            organisation_name = options["org_name"]
            date_str = datetime.now().date().strftime("%Y%m%d")
            output = BytesIO()
            col = 0

            if organisation_name:
                qs = ApiarySiteOnApproval.objects.filter(
                    approval__current_proposal__applicant__organisation__name__icontains=organisation_name
                )
            else:
                qs = ApiarySiteOnApproval.objects.all()

            with xlsxwriter.Workbook(output, {"in_memory": True}) as wb:
                sheet = wb.add_worksheet()

                line = [
                    "Applicant",
                    "Site ID",
                    "Lon/Lat",
                    "Site Status",
                    "Zone",
                    "Licensed Site",
                ]
                sheet.write_row(0, col, line)

                row_count = 0
                for row, asoa in enumerate(
                    qs.order_by("approval__current_proposal__applicant"), 1
                ):
                    # Using safe access or string formatting where appropriate
                    line = [
                        f"{asoa.approval.relevant_applicant_name}",
                        f"{asoa.apiary_site_id}",
                        f"{asoa.wkb_geometry.coords}" if asoa.wkb_geometry else "",
                        f"{asoa.site_status}",
                        f"{asoa.site_category.name}" if asoa.site_category else "",
                        f"{asoa.licensed_site}",
                    ]
                    sheet.write_row(row, col, line)
                    row_count += 1

            # Prepare context for TemplateEmailBase templates
            context = {
                "description": "Please find attached Excel WB with list of Apiary Sites."
            }

            filename = f"apiary_sites_{date_str}.xlsx"

            # Note: xlsxwriter produces OpenXML format (.xlsx),
            # so application/vnd.openxmlformats-officedocument.spreadsheetml.sheet is more accurate than .vnd.ms-excel
            attachments = [
                (
                    filename,
                    output.getvalue(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            ]

            # Instantiate and configure the email class dynamically
            email_obj = ApiarySitesEmail()
            email_obj.subject = f"Apiary Sites List - {date_str}"

            to_addresses = settings.APIARY_SUPPORT_EMAIL
            if not isinstance(to_addresses, list):
                to_addresses = [to_addresses]

            # Send the email using TemplateEmailBase
            email_obj.send(
                to_addresses=to_addresses,
                from_address=getattr(settings, "EMAIL_FROM", "no-reply@dbca.wa.gov.au"),
                context=context,
                attachments=attachments,
                headers=None,
            )

            self.stdout.write(
                f"Command {__name__} completed successfully ({row_count} records exported)."
            )

        except Exception as e:
            logger.exception(f"An error occurred while running {__name__}: {e}")
            raise
