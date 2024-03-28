from __future__ import unicode_literals
import os
from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.gis.db.models import MultiPolygonField
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from ledger.accounts.models import EmailUser, Document, RevisionedMixin
from django.contrib.postgres.fields.jsonb import JSONField
from django.utils import timezone
from django.core.cache import cache

from disturbance.components.main.utils import overwrite_regions_polygons, overwrite_districts_polygons


class MapLayer(models.Model):
    display_name = models.CharField(max_length=100, blank=True, null=True)
    layer_name = models.CharField(max_length=200, blank=True, null=True)
    option_for_internal = models.BooleanField(default=True)
    option_for_external = models.BooleanField(default=True)
    display_all_columns = models.BooleanField(default=False)

    class Meta:
        app_label = 'disturbance'
        verbose_name = 'apiary map layer'

    def __str__(self):
        return '{0}, {1}'.format(self.display_name, self.layer_name)

    @property
    def column_names(self):
        column_names = []
        for column in self.columns.all():
            column_names.append(column.name)
        return ','.join(column_names)


class MapColumn(models.Model):
    map_layer = models.ForeignKey(MapLayer, null=True, blank=True, related_name='columns')
    name = models.CharField(max_length=100, blank=True, null=True)
    option_for_internal = models.BooleanField(default=True)
    option_for_external = models.BooleanField(default=True)

    class Meta:
        app_label = 'disturbance'
        verbose_name = 'apiary map column'

    def __str__(self):
        return '{0}, {1}'.format(self.map_layer, self.name)

class DASMapLayer(models.Model):
    display_name = models.CharField(max_length=100)
    layer_name = models.CharField(max_length=200)
    layer_url = models.CharField(max_length=256, blank=True, null=True)
    cache_expiry = models.IntegerField(default=300)
    option_for_internal = models.BooleanField(default=True)
    option_for_external = models.BooleanField(default=True)
    display_all_columns = models.BooleanField(default=False)

    class Meta:
        app_label = 'disturbance'
        verbose_name = 'Disturbance map layer'

    def __str__(self):
        return '{0}, {1}'.format(self.display_name, self.layer_name)

    def save(self, *args, **kwargs):
        if not self.layer_url:
            self.layer_url = settings.KB_LAYER_URL.replace('{{layer_name}}', self.layer_name)

        cache.delete('utils_cache.get_proxy_cache()')
        self.full_clean()
        super(DASMapLayer, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Region(models.Model):
    name = models.CharField(max_length=200, unique=True)
    forest_region = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        app_label = 'disturbance'

    def __str__(self):
        return self.name


class ArchivedDistrictManager(models.Manager):
    def get_queryset(self):
        #return super().get_queryset().all()
        return super().get_queryset().exclude(archive_date__lte=date.today())

@python_2_unicode_compatible
class District(models.Model):
    region = models.ForeignKey(Region, related_name='districts')
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=3)
    archive_date = models.DateField(null=True, blank=True)

    objects = ArchivedDistrictManager()

    class Meta:
        ordering = ['name']
        app_label = 'disturbance'

    def __str__(self):
        return self.name


class DistrictDbca(models.Model):
    wkb_geometry = MultiPolygonField(srid=4326, blank=True, null=True)
    district_name = models.CharField(max_length=200, blank=True, null=True)
    office = models.CharField(max_length=200, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['object_id', ]
        app_label = 'disturbance'
        verbose_name_plural = "Apiary DBCA Districts"


class RegionDbca(models.Model):
    wkb_geometry = MultiPolygonField(srid=4326, blank=True, null=True)
    region_name = models.CharField(max_length=200, blank=True, null=True)
    office = models.CharField(max_length=200, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['object_id', ]
        app_label = 'disturbance'
        verbose_name_plural = "Apiary DBCA Regions"


class CategoryDbca(models.Model):
    '''
    This model is used for defining the categories
    '''
    wkb_geometry = MultiPolygonField(srid=4326, blank=True, null=True)
    category_name = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        app_label = 'disturbance'


class WaCoast(models.Model):
    '''
    This model is used for validating if the apiary site is in the valid area
    '''
    wkb_geometry = MultiPolygonField(srid=4326, blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True)
    source = models.CharField(max_length=50, blank=True, null=True)
    smoothed = models.BooleanField(default=False)

    class Meta:
        app_label = 'disturbance'


@python_2_unicode_compatible
class ApplicationType(models.Model):
    DISTURBANCE = 'Disturbance'
    DISTURBANCE_UAT = 'Disturbance Training'
    DISTURBANCE_DEMO = 'Disturbance Demo'
    POWERLINE_MAINTENANCE = 'Powerline Maintenance'
    APIARY = 'Apiary'
    TEMPORARY_USE = 'Temporary Use'
    SITE_TRANSFER = 'Site Transfer'
    FIRE = 'Prescribed Burning'

    APPLICATION_TYPES = (
        (DISTURBANCE, 'Disturbance'),
        (DISTURBANCE_UAT, 'Disturbance Training'),
        (DISTURBANCE_DEMO, 'Disturbance Demo'),
        (POWERLINE_MAINTENANCE, 'Powerline Maintenance'),
        (APIARY, 'Apiary'),
        (TEMPORARY_USE, 'Temporary Use'),
        (SITE_TRANSFER, 'Site Transfer'),
        (FIRE, 'Prescribed Burning'),
    )

    APIARY_APPLICATION_TYPES = (APIARY, TEMPORARY_USE, SITE_TRANSFER,)

    DOMAIN_USED_CHOICES = (
        ('das', 'DAS'),
        ('apiary', 'Apiary'),
    )

    # name = models.CharField(max_length=64, unique=True)
    name = models.CharField(
        verbose_name='Application Type name',
        max_length=64,
        choices=APPLICATION_TYPES,
    )
    order = models.PositiveSmallIntegerField(default=0)
    visible = models.BooleanField(default=True)
    application_fee = models.DecimalField(max_digits=6, decimal_places=2)
    oracle_code_application = models.CharField(max_length=50)
    is_gst_exempt = models.BooleanField(default=True)
    domain_used = models.CharField(max_length=40, choices=DOMAIN_USED_CHOICES, default=DOMAIN_USED_CHOICES[0][0])
    searchable = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        app_label = 'disturbance'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ActivityMatrix(models.Model):
    # name = models.CharField(verbose_name='Activity matrix name', max_length=24, choices=application_type_choicelist(), default='Disturbance')
    name = models.CharField(verbose_name='Activity matrix name', max_length=24,
                            choices=[('Disturbance', u'Disturbance')], default='Disturbance')
    description = models.CharField(max_length=256, blank=True, null=True)
    schema = JSONField()
    replaced_by = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    version = models.SmallIntegerField(default=1, blank=False, null=False)
    ordered = models.BooleanField('Activities Ordered Alphabetically', default=False)

    class Meta:
        app_label = 'disturbance'
        unique_together = ('name', 'version')
        verbose_name_plural = "Approval matrix"

    def __str__(self):
        return '{} - v{}'.format(self.name, self.version)


@python_2_unicode_compatible
class Tenure(models.Model):
    name = models.CharField(max_length=255, unique=True)
    order = models.PositiveSmallIntegerField(default=0)
    application_type = models.ForeignKey(ApplicationType, related_name='tenure_app_types')

    class Meta:
        ordering = ['order', 'name']
        app_label = 'disturbance'

    def __str__(self):
        return '{}: {}'.format(self.name, self.application_type)


@python_2_unicode_compatible
class UserAction(models.Model):
    who = models.ForeignKey(EmailUser, null=False, blank=False)
    when = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    what = models.TextField(blank=False)

    def __str__(self):
        return "{what} ({who} at {when})".format(
            what=self.what,
            who=self.who,
            when=self.when
        )

    class Meta:
        abstract = True
        app_label = 'disturbance'


class CommunicationsLogEntry(models.Model):
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('mail', 'Mail'),
        ('person', 'In Person'),
        ('referral_complete', 'Referral Completed'),
    ]
    DEFAULT_TYPE = TYPE_CHOICES[0][0]

    # to = models.CharField(max_length=200, blank=True, verbose_name="To")
    to = models.TextField(blank=True, verbose_name="To")
    fromm = models.CharField(max_length=200, blank=True, verbose_name="From")
    # cc = models.CharField(max_length=200, blank=True, verbose_name="cc")
    cc = models.TextField(blank=True, verbose_name="cc")

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=DEFAULT_TYPE)
    reference = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200, blank=True, verbose_name="Subject / Description")
    text = models.TextField(blank=True)

    customer = models.ForeignKey(EmailUser, null=True, related_name='+')
    staff = models.ForeignKey(EmailUser, null=True, related_name='+')

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        app_label = 'disturbance'


@python_2_unicode_compatible
class Document(models.Model):
    name = models.CharField(max_length=255, blank=True,
                            verbose_name='name', help_text='')
    description = models.TextField(blank=True,
                                   verbose_name='description', help_text='')
    uploaded_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'disturbance'
        abstract = True

    @property
    def path(self):
        # return self.file.path
        return self._file.path

    @property
    def filename(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename


@python_2_unicode_compatible
class SystemMaintenance(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def duration(self):
        """ Duration of system maintenance (in mins) """
        return int((self.end_date - self.start_date).total_seconds() / 60.) if self.end_date and self.start_date else ''
        # return (datetime.now(tz=tz) - self.start_date).total_seconds()/60.

    duration.short_description = 'Duration (mins)'

    class Meta:
        app_label = 'disturbance'
        verbose_name_plural = "System maintenance"

    def __str__(self):
        return 'System Maintenance: {} ({}) - starting {}, ending {}'.format(self.name, self.description,
                                                                             self.start_date, self.end_date)


@python_2_unicode_compatible
class ApiaryGlobalSettings(models.Model):
    KEY_ORACLE_CODE_APIARY_SITE_ANNUAL_RENTAL_FEE = 'oracle_code_apiary_site_annural_rental_fee'  # ApplicationType object has an attribute 'oracle_code_application' to store oracle account code
                                                                                                  # However for the annual rental fee, there are not proposals, which means no ApplicationType objects related.
                                                                                                  # Therefore we store oracle account code for the annual site fee here.
    KEY_APIARY_SITES_LIST_TOKEN = 'apiary_sites_list_token'
    KEY_APIARY_LICENCE_TEMPLATE_FILE = 'apiary_licence_template_file'
    KEY_PRINT_DEED_POLL_URL = 'print_deed_poll_url'
    KEY_DBCA_DISTRICTS_FILE = 'dbca_districts_file'
    KEY_DBCA_REGIONS_FILE = 'dbca_regions_file'

    keys = (
        (KEY_ORACLE_CODE_APIARY_SITE_ANNUAL_RENTAL_FEE, 'Oracle code for the apiary site annual site fee'),
        (KEY_APIARY_SITES_LIST_TOKEN, 'Token to import the apiary sites list'),
        (KEY_APIARY_LICENCE_TEMPLATE_FILE, 'Apiary licence template file'),
        (KEY_PRINT_DEED_POLL_URL, 'URL of the deed poll'),
        (KEY_DBCA_DISTRICTS_FILE, 'DBCA districts geojson file'),
        (KEY_DBCA_REGIONS_FILE, 'DBCA regions geojson file'),
    )

    default_values = (
        (KEY_ORACLE_CODE_APIARY_SITE_ANNUAL_RENTAL_FEE, 'T1 EXEMPT'),
        (KEY_APIARY_SITES_LIST_TOKEN, 'abc123'),
        (KEY_APIARY_LICENCE_TEMPLATE_FILE, ''),
        (KEY_DBCA_DISTRICTS_FILE, ''),
        (KEY_DBCA_REGIONS_FILE, ''),
        (KEY_PRINT_DEED_POLL_URL, 'https://parks.dpaw.wa.gov.au/sites/default/files/downloads/know/DBCA%20apiary%20deed%20poll.pdf')
    )
    key = models.CharField(max_length=255, choices=keys, blank=False, null=False, unique=True)
    value = models.CharField(max_length=255)
    _file = models.FileField(upload_to='apiary_licence_template', null=True, blank=True)

    class Meta:
        app_label = 'disturbance'
        verbose_name_plural = "Apiary Global Settings"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(ApiaryGlobalSettings, self).save(force_insert, force_update, using, update_fields)

        if self._file:
            # When regions/districts file has been updated, update polygons for it.
            if self.key == ApiaryGlobalSettings.KEY_DBCA_REGIONS_FILE:
                overwrite_regions_polygons(self._file.path)
            elif self.key == ApiaryGlobalSettings.KEY_DBCA_DISTRICTS_FILE:
                overwrite_districts_polygons(self._file.path)

    def __str__(self):
        return self.key


@python_2_unicode_compatible
class GlobalSettings(models.Model):
    KEY_ASSESSMENT_REMINDER_DAYS = 'assessment_reminder_days'
    DAS_SHAREPOINT_PAGE = 'das_sharepoint_page'
    PROPOSAL_ASSESS_HELP_PAGE ='proposal_assess_help_page'
    COMPLIANCE_ASSESS_HELP_PAGE='compliance_assess_help_page'
    REFERRAL_ASSESS_HELP_PAGE='referral_assess_help_page'
    PROPOSAL_APPROVER_HELP_PAGE ='proposal_approver_help_page'
    SHAPEFILE_INFO='shapefile_info'
    PROPOSAL_TYPE_HELP='proposal_type_help_url'
    REGION_HELP='region_help_url'
    DISTRICT_HELP='district_help_url'
    ACTIVITY_TYPE_HELP='activity_type_help_url'
    SUB_ACTIVITY_1_HELP='sub_activity_1_help_url'
    SUB_ACTIVITY_2_HELP='sub_activity_2_help_url'
    CATEGORY_HELP='category_help_url'
    MAX_NO_POLYGONS='max_no_polygon'

    keys = (
        (KEY_ASSESSMENT_REMINDER_DAYS, 'Assessment reminder days'),
        (DAS_SHAREPOINT_PAGE, 'DAS Sharepoint page'),
        (PROPOSAL_ASSESS_HELP_PAGE, 'DAS Proposal assess help page'),
        (COMPLIANCE_ASSESS_HELP_PAGE, 'DAS compliance assess help page'),
        (REFERRAL_ASSESS_HELP_PAGE, 'DAS referral assess help page'),
        (PROPOSAL_APPROVER_HELP_PAGE, 'DAS Proposal approver help page'),
        (SHAPEFILE_INFO, 'Shapefile further information'),
        (PROPOSAL_TYPE_HELP, 'Proposal Type help url'),
        (REGION_HELP, 'Region help url'),
        (DISTRICT_HELP, 'District help url'),
        (ACTIVITY_TYPE_HELP, 'Activity type help url'),
        (SUB_ACTIVITY_1_HELP, 'Sub activity 1 help url'),
        (SUB_ACTIVITY_2_HELP, 'Sub activity 2 help url'),
        (CATEGORY_HELP, 'Category help url'),
        (MAX_NO_POLYGONS, 'Maximum number of polygons allowed in the Shapefile'),
        
    )
    default_values = (
    )
    key = models.CharField(max_length=255, choices=keys, blank=False, null=False, unique=True)
    value = models.CharField(max_length=255)

    class Meta:
        app_label = 'disturbance'
        verbose_name_plural = "Global Settings"

    def __str__(self):
        return self.key


class TemporaryDocumentCollection(models.Model):
    # input_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        app_label = 'disturbance'


# temp document obj for generic file upload component
class TemporaryDocument(Document):
    temp_document_collection = models.ForeignKey(
        TemporaryDocumentCollection,
        related_name='documents')
    _file = models.FileField(max_length=255)

    # input_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        app_label = 'disturbance'


class ActiveTaskMonitorManager(models.Manager):
    ''' filter queued tasks and omit old (stale) queued tasks '''
    def get_queryset(self):
        earliest_date = (datetime.now() - timedelta(days=7)).replace(tzinfo=timezone.utc)
        return super().get_queryset().filter(status=TaskMonitor.STATUS_CREATED, created__gte=earliest_date)


#class TaskMonitor(RevisionedMixin):
class TaskMonitor(models.Model):
    STATUS_FAILED = 'failed'
    STATUS_CREATED = 'created'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_ERROR = 'error'
    STATUS_MAX_QUEUE_TIME = 'max_queue_time'
    STATUS_MAX_RETRIES_REACHED = 'max_retries'
    STATUS_CHOICES = (
        (STATUS_FAILED,    'Failed'),
        (STATUS_CREATED,   'Created'),
        (STATUS_RUNNING,   'Running'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_ERROR,     'Error'),
        (STATUS_MAX_QUEUE_TIME, 'Max_Queue_Time_Reached'),
        (STATUS_MAX_RETRIES_REACHED, 'Max_Retries_Reached'),
    )

    task_id = models.PositiveIntegerField()
    status  = models.CharField('Task Status', choices=STATUS_CHOICES, default=STATUS_CREATED, max_length=32)
    retries = models.PositiveSmallIntegerField(default=0)
    proposal = models.ForeignKey('Proposal')
    info = models.TextField(blank=True, null=True)
    requester = models.ForeignKey(EmailUser, blank=False, null=False, related_name='+')
    created = models.DateTimeField(default=timezone.now, editable=False)
    
    objects = models.Manager()
    queued_jobs = ActiveTaskMonitorManager()

    class Meta:
        app_label = 'disturbance'
        verbose_name_plural = "Task Monitor"

    def __str__(self):
        return f'Task {self.task_id}, Proposal: {self.proposal}'



import reversion
reversion.register(ApiaryGlobalSettings)
reversion.register(TaskMonitor)

