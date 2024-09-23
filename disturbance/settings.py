from django.core.exceptions import ImproperlyConfigured

import os, hashlib
import confy
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
confy.read_environment_file(BASE_DIR+"/.env")
os.environ.setdefault("BASE_DIR", BASE_DIR)

from ledger.settings_base import *


ROOT_URLCONF = 'disturbance.urls'
SITE_ID = 1
DEPT_DOMAINS = env('DEPT_DOMAINS', ['dpaw.wa.gov.au', 'dbca.wa.gov.au'])
SUPERVISOR_STOP_CMD = env('SUPERVISOR_STOP_CMD')
SYSTEM_MAINTENANCE_WARNING = env('SYSTEM_MAINTENANCE_WARNING', 24) # hours
DISABLE_EMAIL = env('DISABLE_EMAIL', False)
MEDIA_APP_DIR = env('MEDIA_APP_DIR', 'das')
MEDIA_APIARY_DIR = env('MEDIA_APIARY_DIR', 'apiary')
SPATIAL_DATA_DIR = env('SPATIAL_DATA_DIR', 'spatial_data')
ANNUAL_RENTAL_FEE_GST_EXEMPT = True
FILE_UPLOAD_MAX_MEMORY_SIZE = env('FILE_UPLOAD_MAX_MEMORY_SIZE', 15728640)
APIARY_MIGRATED_LICENCES_APPROVER = env('APIARY_MIGRATED_LICENCES_APPROVER', 'jacinta.overman@dbca.wa.gov.au')
SHOW_ROOT_API = env('SHOW_ROOT_API', False)

SQS_POLLING_MAX_RETRIES = env('SQS_POLLING_MAX_RETRIES', 3)

SQS_APIKEY = env('SQS_APIKEY', '')
SQS_BASEURL = env('SQS_APIURL', '')
#SQS_APIURL = SQS_BASEURL + SQS_APIKEY if SQS_BASEURL.endswith('/') else SQS_BASEURL + os.sep + SQS_APIKEY # adds the APIKEY TOKEN
#SQS_APIURL = SQS_BASEURL if SQS_BASEURL.endswith('/') else SQS_BASEURL + os.sep
SQS_APIURL = SQS_BASEURL

LEDGER_USER = env('LEDGER_USER', '')
LEDGER_PASS = env('LEDGER_PASS', '')

SQS_USER = env('SQS_USER', LEDGER_USER)
SQS_PASS = env('SQS_PASS', LEDGER_PASS)

KMI_USER = env('KMI_USER', LEDGER_USER)
KMI_PASSWORD = env('KMI_PASSWORD', LEDGER_PASS)

KB_USER = env('KB_USER', LEDGER_USER)
KB_PASSWORD = env('KB_PASSWORD', LEDGER_PASS)

KMI_SERVER_URL = env('KMI_SERVER_URL', 'https://kmi.dbca.wa.gov.au')
KMI_API_SERVER_URL = env('KMI_API_SERVER_URL', 'https://kmi-api.dbca.wa.gov.au/')
# KB_SERVER_URL = env('KB_SERVER_URL', 'https://gis-kaartdijin-boodja-geoserver-api-dev.dbca.wa.gov.au/')
KB_SERVER_URL = env('KB_SERVER_URL', 'https://kaartdijin-boodja-geoserver-api.dbca.wa.gov.au/')
KB_API_URL=env("KMI_URL", 'https://kaartdijin-boodja.dbca.wa.gov.au/')

KB_LAYER_URL = env('KB_LAYER_URL', 'https://kaartdijin-boodja.dbca.wa.gov.au/api/catalogue/entries/{{layer_name}}/layer/')
SHOW_DAS_MAP = env('SHOW_DAS_MAP', True)
SHOW_ROOT_API = env('SHOW_ROOT_API', False)
MAX_LAYERS_PER_SQQ = env('MAX_LAYERS_PER_SQQ', 15)

INSTALLED_APPS += [
    'reversion_compare',
    'bootstrap3',
    'disturbance',
    'disturbance.components.main',
    'disturbance.components.organisations',
    'disturbance.components.users',
    'disturbance.components.proposals',
    'disturbance.components.approvals',
    'disturbance.components.compliances',
    'disturbance.components.das_payments',
    'disturbance.components.history',
    'taggit',
    'rest_framework',
    'rest_framework_datatables',
    'rest_framework_gis',
    'reset_migrations',
    'ckeditor',
    # 'corsheaders',
    'smart_selects',
    'crispy_forms',
    'appmonitor_client',
]

ADD_REVERSION_ADMIN=True

# maximum number of days allowed for a booking
WSGI_APPLICATION = 'disturbance.wsgi.application'

'''REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'disturbance.perms.OfficerPermission',
    ),
}'''

#REST_FRAMEWORK = {
#    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
#    #'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#        'PAGE_SIZE': 5
#}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    #'DEFAULT_FILTER_BACKENDS': (
    #    'rest_framework_datatables.filters.DatatablesFilterBackend',
    #),
    #'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    #'PAGE_SIZE': 20,
    #'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}

USE_DJANGO_JQUERY= True
# JQUERY_URL = True

#CRISPY_TEMPLATE_PACK = 'uni_form'
CRISPY_TEMPLATE_PACK = 'bootstrap3'

MIDDLEWARE_CLASSES += [
    'disturbance.middleware.BookingTimerMiddleware',
    'disturbance.middleware.FirstTimeNagScreenMiddleware',
    'disturbance.middleware.RevisionOverrideMiddleware',
    'disturbance.middleware.DomainDetectMiddleware',
    'disturbance.middleware.CacheControlMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # 'corsheaders.middleware.CorsMiddleware',
]
# CORS_ORIGIN_ALLOW_ALL = True

TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'disturbance', 'templates'))
TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'disturbance','components','organisations', 'templates'))
TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'disturbance','components','emails', 'templates'))
TEMPLATES[0]['OPTIONS']['context_processors'].append('disturbance.context_processors.apiary_url')
del BOOTSTRAP3['css_url']
#BOOTSTRAP3 = {
#    'jquery_url': '//static.dpaw.wa.gov.au/static/libs/jquery/2.2.1/jquery.min.js',
#    'base_url': '//static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/',
#    'css_url': None,
#    'theme_url': None,
#    'javascript_url': None,
#    'javascript_in_head': False,
#    'include_jquery': False,
#    'required_css_class': 'required-form-field',
#    'set_placeholder': False,
#}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'disturbance', 'cache'),
        "OPTIONS": {"MAX_ENTRIES": 10000},
    }
}
SQS_LAYERS_CACHE_TIMEOUT = env('SQS_LAYERS_CACHE_TIMEOUT', 60*5) # 5 mins
SQS_LAYER_EXISTS_CACHE_TIMEOUT = env('SQS_LAYER_EXISTS_CACHE_TIMEOUT', 60*5) # 5 mins
SQS_RESPONSE_CACHE_TIMEOUT = env('SQS_RESPONSE_CACHE_TIMEOUT', 60*60) # 60 mins
LAYERS_USED_CACHE_TIMEOUT = env('LAYERS_USED_CACHE_TIMEOUT', 60*15) # 15 mins
REQUEST_TIMEOUT = env('REQUEST_TIMEOUT', 60*5) # 5mins

STATIC_ROOT=os.path.join(BASE_DIR, 'staticfiles_ds')
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'disturbance', 'static')))
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'disturbance', 'static', 'disturbance_vue', 'static')))
DEV_STATIC = env('DEV_STATIC',False)
DEV_STATIC_URL = env('DEV_STATIC_URL')
if DEV_STATIC and not DEV_STATIC_URL:
    raise ImproperlyConfigured('If running in DEV_STATIC, DEV_STATIC_URL has to be set')
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Department details
SYSTEM_NAME = env('SYSTEM_NAME', 'Disturbance Approval System')
APIARY_SYSTEM_NAME = env('APIARY_SYSTEM_NAME', 'Apiary System')
SYSTEM_NAME_SHORT = env('SYSTEM_NAME_SHORT', 'DAS')
SITE_PREFIX = env('SITE_PREFIX')
SITE_PREFIX_APIARY = env('SITE_PREFIX_APIARY')
SITE_DOMAIN = env('SITE_DOMAIN')
SUPPORT_EMAIL = env('SUPPORT_EMAIL', SYSTEM_NAME_SHORT.lower() + '@' + SITE_DOMAIN).lower()
APIARY_SUPPORT_EMAIL = env('APIARY_SUPPORT_EMAIL', SUPPORT_EMAIL).lower()
DEP_URL = env('DEP_URL','www.' + SITE_DOMAIN)
DEP_PHONE = env('DEP_PHONE','(08) 9219 9000')
DEP_PHONE_SUPPORT = env('DEP_PHONE_SUPPORT','(08) 9219 9000')
DEP_FAX = env('DEP_FAX','(08) 9423 8242')
DEP_POSTAL = env('DEP_POSTAL','Locked Bag 104, Bentley Delivery Centre, Western Australia 6983')
DEP_NAME = env('DEP_NAME','Department of Biodiversity, Conservation and Attractions')
DEP_NAME_SHORT = env('DEP_NAME_SHORT','DBCA')
SITE_URL = env('SITE_URL', 'https://' + '.'.join([SITE_PREFIX, SITE_DOMAIN]).strip('.'))
PUBLIC_URL=env('PUBLIC_URL', SITE_URL)
EMAIL_FROM = env('EMAIL_FROM', 'no-reply@' + SITE_DOMAIN).lower()
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'no-reply@' + SITE_DOMAIN).lower()
ADMIN_GROUP = env('ADMIN_GROUP', 'Disturbance Admin')
APIARY_ADMIN_GROUP = 'Apiary Admin'
DAS_APIARY_ADMIN_GROUP = 'DAS-Apiary Admin'
APIARY_PAYMENTS_OFFICERS_GROUP = 'Apiary Payments Officers'
APPROVED_DAS_EXTERNAL_USERS_GROUP = env('APPROVED_DAS_EXTERNAL_USERS_GROUP', 'Disturbance Approved External Users')
APPROVED_APIARY_EXTERNAL_USERS_GROUP = env('APPROVED_APIARY_EXTERNAL_USERS_GROUP', 'Apiary Approved External Users')
CRON_EMAIL = env('CRON_EMAIL', 'cron@' + SITE_DOMAIN).lower()
TENURE_SECTION = env('TENURE_SECTION', None)
ASSESSMENT_REMINDER_DAYS = env('ASSESSMENT_REMINDER_DAYS', 15)
MAX_QUEUE_TIME = env('MAX_QUEUE_TIME', 7) # Days
MAX_TASK_HISTORY = env('MAX_TASK_HISTORY', 60) # Days
LOG_REQUEST_STATS = env('LOG_REQUEST_STATS', False)
QS_PAGINATOR_SIZE = env('QS_PAGINATOR_SIZE', 400)

CLEAR_AFTER_DAYS_FILE_EXPORT = env('CLEAR_AFTER_DAYS_FILE_EXPORT', 7) # Days
GEO_EXPORT_FOLDER = env('GEO_EXPORT_FOLDER', 'geo_exports') # Days
if not os.path.exists('private-media' + os.sep + GEO_EXPORT_FOLDER):
    os.makedirs('private-media' + os.sep + GEO_EXPORT_FOLDER)

CRS = env('CRS', 'epsg:4326')
CRS_CARTESIAN = env('CRS_CARTESIAN', 'epsg:3043')
OGR2OGR = env('OGR2OGR', '/usr/bin/ogr2ogr')
#GEOM_PRECISION = env('GEOM_PRECISION', 5)

OSCAR_BASKET_COOKIE_OPEN = 'das_basket'
PAYMENT_SYSTEM_ID = env('PAYMENT_SYSTEM_ID', 'S517')
PS_PAYMENT_SYSTEM_ID = PAYMENT_SYSTEM_ID
PAYMENT_SYSTEM_PREFIX = env('PAYMENT_SYSTEM_PREFIX', PAYMENT_SYSTEM_ID.replace('S','0')) # '0517'
os.environ['LEDGER_PRODUCT_CUSTOM_FIELDS'] = "('ledger_description','quantity','price_incl_tax','price_excl_tax','oracle_code')"
APIARY_URL = env('APIARY_URL', [])
CRON_NOTIFICATION_EMAIL = env('CRON_NOTIFICATION_EMAIL', NOTIFICATION_EMAIL).lower()
VERSION_NO="1.0.1"

BASE_URL='https://' + SITE_PREFIX + '.' + SITE_DOMAIN

CRON_CLASSES = [
    'appmonitor_client.cron.CronJobAppMonitorClient',
]


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        #'width': 300,
        'width': '100%',
    },
    'awesome_ckeditor': {
        'toolbar': 'Basic',
    },
}

BUILD_TAG = env('BUILD_TAG', hashlib.md5(os.urandom(32)).hexdigest())  # URL of the Dev app.js served by webpack & express
DEV_APP_BUILD_URL = env('DEV_APP_BUILD_URL')  # URL of the Dev app.js served by webpack & express
GEOCODING_ADDRESS_SEARCH_TOKEN = env('GEOCODING_ADDRESS_SEARCH_TOKEN', 'ACCESS_TOKEN_NOT_FOUND')
RESTRICTED_RADIUS = 3000  # unit: [m]
DBCA_ABN = '38 052 249 024'
if env('CONSOLE_EMAIL_BACKEND', False):
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


SITE_STATUS_DRAFT = 'draft'
SITE_STATUS_PENDING = 'pending'
SITE_STATUS_APPROVED = 'approved'  # This status 'approved' is assigned to the ApiarySiteOnProposal object once it's approved.  'current' is assigned to the ApiarySiteOnApproval object after that.
SITE_STATUS_DENIED = 'denied'
SITE_STATUS_CURRENT = 'current'
SITE_STATUS_NOT_TO_BE_REISSUED = 'not_to_be_reissued'
SITE_STATUS_SUSPENDED = 'suspended'
SITE_STATUS_TRANSFERRED = 'transferred'  # This status 'transferred' is assigned to the old relationship (ApiarySiteOnApproval object)
SITE_STATUS_VACANT = 'vacant'
SITE_STATUS_DISCARDED = 'discarded'

BASE_EMAIL_TEXT = ''
BASE_EMAIL_HTML = ''

# This is either 'das'/'apiary'
# default: 'das'
# This value is determined at the middleware, DomainDetectMiddleware by where the request comes from
DOMAIN_DETECTED = 'das'
HTTP_HOST_FOR_TEST = 'localhost:8071'

# Additional logging for commercialoperator
LOGGING['loggers']['disturbance'] = {
            'handlers': ['file'],
            'level': 'INFO'
        }

# Add a handler
LOGGING['handlers']['file_apiary'] = {
    'level': 'INFO',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': os.path.join(BASE_DIR, 'logs', 'apiary.log'),
    'formatter': 'verbose',
    'maxBytes': 5242880
}

# Add a handler
LOGGING['handlers']['request_stats'] = {
    'level': 'INFO',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': os.path.join(BASE_DIR, 'logs', 'requests.log'),
    'formatter': 'verbose',
    'maxBytes': 5242880
}


# define logger
LOGGING['loggers']['apiary'] = {
    'handlers': ['file_apiary'],
    'level': 'INFO'
}
LOGGING['loggers']['request_stats'] = {
    'handlers': ['request_stats'],
    'level': 'INFO'
}

# Add a debug level logger for development
#if DEBUG:
#    LOGGING = {
#        'version': 1,
#        'disable_existing_loggers': True,
#        'handlers': {
#            'console': {
#                'class': 'logging.StreamHandler',
#            },
#        },
#        'loggers': {
#            'disturbance': {
#                'handlers': ['console'],
#                'level': 'DEBUG',
#                'propagate': False,
#            },
#        },
#    }    

#APPLICATION_TYPES_SQL='''
#        SELECT name, name FROM disturbance_applicationtypechoice
#        WHERE archive_date IS NULL OR archive_date > now()
#    '''

#from django.db import connection
#def run_select_sql(sql):
#    try:
#        with connection.cursor() as cursor:
#            cursor.execute(sql)
#            row = cursor.fetchall()
#        return row
#    except:
#        return []

