from django.template import Library
#from wildlifelicensing.apps.main import helpers
#from disturbance import helpers
from django.conf import settings
from disturbance import helpers as disturbance_helpers
from disturbance.components.main.models import SystemMaintenance
from disturbance.components.organisations.models import Organisation
from disturbance.components.organisations.utils import can_admin_org, is_consultant
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

register = Library()
TIME_FORMAT = '%a %d-%b %Y %H:%M:%S' #'Fri 29-Oct 2021 08:30:33'


@register.simple_tag(takes_context=True)
def is_disturbance_admin(context):
    # checks if user is an AdminUser
    request = context['request']
    return disturbance_helpers.is_disturbance_admin(request)

@register.simple_tag(takes_context=True)
def is_apiary_admin(context):
    # checks if user is an AdminUser
    request = context['request']
    return disturbance_helpers.is_apiary_admin(request)

@register.filter
def is_org_admin(org_id, user):
    """ Is an Admin for the given Organisation """
    return can_admin_org(Organisation.objects.get(id=org_id), user)

#@register.filter
#def is_org_consultant(org_id, user):
#    """ Is an Admin for the given Organisation """
#    return is_consultant(Organisation.objects.get(id=org_id), user)

@register.simple_tag(takes_context=True)
def is_internal(context):
    # checks if user is a departmentuser and logged in via single sign-on
    request = context['request']
    return disturbance_helpers.is_internal(request)

@register.simple_tag(takes_context=True)
def is_internal_path(context):
    # checks if user is viewing page via '/internal/' or '/external/' url
    # return 'internal/' in context['url_path']
    request = context['request']
    return '/internal/' in request.path

@register.simple_tag(takes_context=True)
def is_model_backend(context):
    # Return True if user logged in via single sign-on (or False via social_auth i.e. an external user signing in with a login-token)
    request = context['request']
    return disturbance_helpers.is_model_backend(request)


@register.simple_tag()
def system_maintenance_due():
    """ Returns True (actually a time str), if within <timedelta hours> of system maintenance due datetime """
    tz = pytz.timezone(settings.TIME_ZONE)
    now = timezone.now()  # returns UTC time
    qs = SystemMaintenance.objects.filter(start_date__gte=now - timedelta(minutes=1))
    if qs:
        obj = qs.earliest('start_date')
        if now >= obj.start_date - timedelta(hours=settings.SYSTEM_MAINTENANCE_WARNING) and now <= obj.start_date + timedelta(minutes=1):
            # display time in local timezone
            return '{0} - {1} (Duration: {2} mins)'.format(obj.start_date.astimezone(tz=tz).strftime(TIME_FORMAT), obj.end_date.astimezone(tz=tz).strftime(TIME_FORMAT), obj.duration())
    return False


@register.simple_tag()
def system_maintenance_can_start():
    """ Returns True if current datetime is within 1 minute past scheduled start_date """
    now = timezone.now() # returns UTC time
    qs = SystemMaintenance.objects.filter(start_date__gte=now - timedelta(minutes=1))
    if qs:
        obj = qs.earliest('start_date')
        if now >= obj.start_date and now <= obj.start_date + timedelta(minutes=1):
            return True
    return False


@register.simple_tag()
def dept_support_phone2():
    return settings.DEPT_NAME

@register.simple_tag(takes_context=True)
def get_notices_tag(context):
    return disturbance_helpers.get_notices()['notices'] 
