import logging

from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import serializers
from rest_framework.exceptions import APIException, NotAuthenticated, PermissionDenied
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

class ReferralNotAuthorized(PermissionDenied):
    default_detail = 'You are not authorised to work on this referral'
    default_code = 'referral_not_authorized'

class ProposalNotAuthorized(PermissionDenied):
    default_detail = 'You are not authorised to work on this proposal'
    default_code = 'proposal_not_authorized'

class ReferralCanNotSend(PermissionDenied):
    default_detail = 'You can only send referrals sent from an assessor'
    default_code = 'referral_level_send_unauthorized'

class ProposalReferralCannotBeSent(PermissionDenied):
    default_detail = 'Referrals can only be sent if it is in the right processing status'
    default_code = 'proposal_referral_cannot_be_sent'

class ProposalNotComplete(APIException):
    status_code = 400
    default_detail = 'The proposal is not complete'
    default_code = 'proposal_incoplete'

class ProposalMissingFields(APIException):
    status_code = 400
    default_detail = 'The proposal has missing required fields'
    default_code = 'proposal_missing_fields'

class InternalServerError(APIException):
    status_code = 500
    default_detail = "A server error occurred."
    default_code = "internal_server_error"

def custom_exception_handler(exc, context):
    """Custom django rest framework exception handler
    That makes sure all the exception responses are in json format since many django
    exceptions are in html format
    """

    # Django rest framework errors are already in json format
    if isinstance(
        exc, (serializers.ValidationError, Http404, NotAuthenticated, PermissionDenied)
    ):
        pass

    # handle django validation errors
    elif isinstance(exc, ValidationError):
        if hasattr(exc, "error_dict"):
            exc = serializers.ValidationError(repr(exc.error_dict))
        elif hasattr(exc, "message"):
            exc = serializers.ValidationError(exc.message)
        else:
            exc = serializers.ValidationError(str(exc))

    else:
        # Handle all other exceptions
        logger.exception(str(exc))
        exc = InternalServerError(str(exc))

    return exception_handler(exc, context)
