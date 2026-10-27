from confy import env
from django.urls import reverse
from django.shortcuts import redirect

import re
import datetime
import logging
import psutil
import os

from django.http import HttpResponseRedirect
from django.utils import timezone

from django.conf import settings
#from disturbance.components.das_payments.models import ApplicationFee
from reversion.middleware  import RevisionMiddleware
from reversion.views import _request_creates_revision


logger = logging.getLogger(__name__)


class RevisionOverrideMiddleware(RevisionMiddleware):

    """
        Wraps the entire request in a revision.

        override venv/lib/python2.7/site-packages/reversion/middleware.py
    """

    # exclude ledger payments/checkout from revision - hack to overcome basket (lagging status) issue/conflict with reversion
    def request_creates_revision(self, request):
        return _request_creates_revision(request) and 'checkout' not in request.get_full_path()


class DomainDetectMiddleware(object):
    def __init__(self, next_layer=None):
        """
        We allow next_layer to be None because old-style middlewares
        won't accept any argument.
        """
        self.get_response = next_layer

    def process_request(self, request):
        """
        Handle old-style request processing here, as usual.
        Any request goes through this function
        """
        # Do something with request
        # Probably return None
        # Or return an HttpResponse in some cases
        settings.DOMAIN_DETECTED = 'das'
        settings.SYSTEM_NAME = env('SYSTEM_NAME', 'Disturbance Approval System')
        settings.SYSTEM_NAME_SHORT = 'DAS'
        settings.BASE_EMAIL_TEXT = 'disturbance/emails/base_email.txt'
        settings.BASE_EMAIL_HTML = 'disturbance/emails/base_email.html'

        http_host = request.META.get('HTTP_HOST', None)

        logger.debug(f'http_host: {http_host}')

        return None

    def process_response(self, request, response):
        """
        Handle old-style response processing here, as usual.
        """
        # Do something with response, possibly using request.

        return response

    def __call__(self, request):
        """
        Handle new-style middleware here.
        """
        response = self.process_request(request)
        if response is None:
            # If process_request returned None, we must call the next middleware or
            # the view. Note that here, we are sure that self.get_response is not
            # None because this method is executed only in new-style middlewares.
            response = self.get_response(request)
        response = self.process_response(request, response)
        return response


class CacheControlMiddleware(object):
    def process_response(self, request, response):
        if request.path[:5] == '/api/' or request.path == '/':
            response['Cache-Control'] = 'private, no-store'
        elif request.path[:8] == '/static/':
            response['Cache-Control'] = 'public, max-age=86400'
        else:
            response['Cache-Control'] = 'private, no-store'
        return response


class MemoryTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        
        response = self.get_response(request)
        
        mem_after = process.memory_info().rss
        mem_diff = (mem_after - mem_before) / (1024 * 1024) # in MB
        
        logger.info(f"Memory used by {request.path}: {mem_diff:.2f} MB")
        return response
