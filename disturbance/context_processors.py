from confy import env
from django.conf import settings
from disturbance.settings import (
    TEMPLATE_GROUP,
    TEMPLATE_HEADER_LOGO,
    TEMPLATE_TITLE,
)
#from ledger.payments.helpers import is_payment_admin
from disturbance.settings import KB_SERVER_URL
import logging


logger = logging.getLogger(__name__)

def apiary_url(request):
    # logger.debug(f'DOMAIN_DETECTED: {settings.DOMAIN_DETECTED}')

    # if settings.DOMAIN_DETECTED == 'apiary':
    #     PUBLIC_URL = 'https://apiary.dbca.wa.gov.au/'
    #     displayed_system_name = settings.APIARY_SYSTEM_NAME
    #     support_email = settings.APIARY_SUPPORT_EMAIL
    # else:
    #     PUBLIC_URL = 'https://das.dbca.wa.gov.au'
    #     displayed_system_name = settings.SYSTEM_NAME
    #     support_email = settings.SUPPORT_EMAIL

    PUBLIC_URL = 'https://das.dbca.wa.gov.au'
    displayed_system_name = settings.SYSTEM_NAME
    support_email = settings.SUPPORT_EMAIL

    is_payment_officer = False #is_payment_admin(request.user)

    return {
        "template_group": TEMPLATE_GROUP,
        "template_header_logo": TEMPLATE_HEADER_LOGO,
        "template_title": TEMPLATE_TITLE,
        'DOMAIN_DETECTED': settings.DOMAIN_DETECTED,
        'DJANGO_SETTINGS': settings,
        'DEBUG': settings.DEBUG,
        'TEMPLATE_GROUP': settings.DOMAIN_DETECTED,
        'SYSTEM_NAME': settings.SYSTEM_NAME,
        'PUBLIC_URL': PUBLIC_URL,
        'APPLICATION_GROUP': settings.DOMAIN_DETECTED,
        'DISPLAYED_SYSTEM_NAME': displayed_system_name,
        'SUPPORT_EMAIL': support_email,
        'is_payment_admin': is_payment_officer,
        'build_tag': settings.BUILD_TAG,
        'KB_SERVER_URL': KB_SERVER_URL,
        'SQS_APIURL': settings.SQS_APIURL,
        'SHOW_DAS_MAP': settings.SHOW_DAS_MAP,
        'MAX_LAYERS_PER_SQQ': settings.MAX_LAYERS_PER_SQQ,
        "vue3_entry_script": settings.VUE3_ENTRY_SCRIPT,
    }