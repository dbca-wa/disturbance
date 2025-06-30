from __future__ import unicode_literals
import os
from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.gis.db.models import MultiPolygonField
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
# from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from ledger.accounts.models import EmailUser, Document, RevisionedMixin
from django.db.models import JSONField
from django.utils import timezone
from django.core.cache import cache
from django.utils.html import strip_tags

class MapLayer(models.Model):
    display_name = models.CharField(max_length=100, blank=True, null=True)
    layer_name = models.CharField(max_length=200, blank=True, null=True)
    option_for_internal = models.BooleanField(default=True)
    option_for_external = models.BooleanField(default=True)
    display_all_columns = models.BooleanField(default=False)

    class Meta:
        app_label = 'disturbance'
        verbose_name = 'map layer'

    def __str__(self):
        return '{0}, {1}'.format(self.display_name, self.layer_name)

    @property
    def column_names(self):
        column_names = []
        for column in self.columns.all():
            column_names.append(column.name)
        return ','.join(column_names)


class MapColumn(models.Model):
    map_layer = models.ForeignKey(MapLayer, null=True, blank=True, related_name='columns', on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, blank=True, null=True)
    option_for_internal = models.BooleanField(default=True)
    option_for_external = models.BooleanField(default=True)

    class Meta:
        app_label = 'disturbance'
        verbose_name = 'map column'

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

class District(models.Model):
    region = models.ForeignKey(Region, related_name='districts', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=3)
    archive_date = models.DateField(null=True, blank=True)

    objects = ArchivedDistrictManager()

    class Meta:
        ordering = ['name']
        app_label = 'disturbance'

    def __str__(self):
        return self.name


class ApplicationType(models.Model):
    DISTURBANCE = 'Disturbance'
    DISTURBANCE_UAT = 'Disturbance Training'
    DISTURBANCE_DEMO = 'Disturbance Demo'
    DISTURBANCE_ECOLOGICAL = 'Ecological Thinning'
    POWERLINE_MAINTENANCE = 'Powerline Maintenance'
    FIRE = 'Prescribed Burning'

    APPLICATION_TYPES = (
        (DISTURBANCE, 'Disturbance'),
        (DISTURBANCE_UAT, 'Disturbance Training'),
        (DISTURBANCE_DEMO, 'Disturbance Demo'),
        (DISTURBANCE_ECOLOGICAL, 'Ecological Thinning'),
        (POWERLINE_MAINTENANCE, 'Powerline Maintenance'),
        (FIRE, 'Prescribed Burning'),
    )

    DOMAIN_USED_CHOICES = (
        ('das', 'DAS'),
        ('dummy', 'DUMMY'),
    )

    # name = models.CharField(max_length=64, unique=True)
    name = models.CharField(
        verbose_name='Application Type name',
        max_length=64,
        choices=APPLICATION_TYPES,
    )
    order = models.PositiveSmallIntegerField(default=0)
    visible = models.BooleanField(default=True)
    domain_used = models.CharField(max_length=40, choices=DOMAIN_USED_CHOICES, default=DOMAIN_USED_CHOICES[0][0])
    searchable = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        app_label = 'disturbance'

    def __str__(self):
        return self.name


class ActivityMatrix(models.Model):
    # name = models.CharField(verbose_name='Activity matrix name', max_length=24, choices=application_type_choicelist(), default='Disturbance')
    name = models.CharField(verbose_name='Activity matrix name', max_length=24,
                            choices=[('Disturbance', u'Disturbance'), ('Ecological Thinning', u'Ecological Thinning') ], default='Disturbance')
    description = models.CharField(max_length=256, blank=True, null=True)
    schema = JSONField()
    replaced_by = models.ForeignKey('self', on_delete=models.CASCADE , blank=True, null=True)
    version = models.SmallIntegerField(default=1, blank=False, null=False)
    ordered = models.BooleanField('Activities Ordered Alphabetically', default=False)

    class Meta:
        app_label = 'disturbance'
        unique_together = ('name', 'version')
        verbose_name_plural = "Approval matrix"

    def __str__(self):
        return '{} - v{}'.format(self.name, self.version)
    
    @property
    def latest(self):
        if self.name:
            last_record=ActivityMatrix.objects.filter(name=self.name).order_by('-version')[0]
            if last_record==self:
                return True
            else:
                False
        return False


class Tenure(models.Model):
    name = models.CharField(max_length=255, unique=True)
    order = models.PositiveSmallIntegerField(default=0)
    application_type = models.ForeignKey(ApplicationType, related_name='tenure_app_types', null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['order', 'name']
        app_label = 'disturbance'

    def __str__(self):
        return '{}: {}'.format(self.name, self.application_type)


class UserAction(models.Model):
    who = models.ForeignKey(EmailUser, null=False, blank=False, on_delete=models.CASCADE)
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

    customer = models.ForeignKey(EmailUser, null=True, related_name='+', on_delete=models.SET_NULL)
    staff = models.ForeignKey(EmailUser, null=True, related_name='+', on_delete=models.SET_NULL)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        app_label = 'disturbance'


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


from ckeditor.fields import RichTextField

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
    help_text_required=models.BooleanField(default=False)
    help_text=RichTextField(null=True, blank=True)

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
        related_name='documents', on_delete=models.CASCADE)
    _file = models.FileField(max_length=255)

    # input_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        app_label = 'disturbance'


class ActiveTaskMonitorManager(models.Manager):
    ''' filter queued tasks and omit old (stale) queued tasks '''
    def get_queryset(self):
        earliest_date = (datetime.now() - timedelta(days=7)).replace(tzinfo=timezone.utc)
        return super().get_queryset().filter(status=TaskMonitor.STATUS_CREATED, created__gte=earliest_date)


class RequestTypeEnum():
    FULL = 'FULL'
    PARTIAL = 'PARTIAL'
    SINGLE = 'SINGLE'
    REFRESH_PARTIAL = 'REFRESH_PARTIAL'
    REFRESH_SINGLE = 'REFRESH_SINGLE'
    TEST_GROUP = 'TEST_GROUP'
    TEST_SINGLE = 'TEST_SINGLE'
    REQUEST_TYPE_CHOICES = (
        (FULL, 'FULL'),
        (PARTIAL, 'PARTIAL'),
        (SINGLE, 'SINGLE'),
        (REFRESH_PARTIAL, 'REFRESH_PARTIAL'),
        (REFRESH_SINGLE, 'REFRESH_SINGLE'),
        (TEST_GROUP, 'TEST_GROUP'),
        (TEST_SINGLE, 'TEST_SINGLE'),
    )
 

#class TaskMonitor(RevisionedMixin):
class TaskMonitor(models.Model):
    STATUS_FAILED = 'failed'
    STATUS_CREATED = 'created'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_ERROR = 'error'
    STATUS_MAX_QUEUE_TIME = 'max_queue_time'
    STATUS_MAX_RUNNING_TIME = 'max_running_time'
    STATUS_MAX_RETRIES_REACHED = 'max_retries'
    STATUS_CHOICES = (
        (STATUS_FAILED,    'Failed'),
        (STATUS_CREATED,   'Created'),
        (STATUS_RUNNING,   'Running'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_ERROR,     'Error'),
        (STATUS_MAX_QUEUE_TIME, 'Max_Queue_Time_Reached'),
        (STATUS_MAX_RUNNING_TIME, 'Max_Running_Time_Reached'),
        (STATUS_MAX_RETRIES_REACHED, 'Max_Retries_Reached'),
    )

    task_id = models.PositiveIntegerField()
    status  = models.CharField('Task Status', choices=STATUS_CHOICES, default=STATUS_CREATED, max_length=32)
    retries = models.PositiveSmallIntegerField(default=0)
    proposal = models.ForeignKey('Proposal', on_delete=models.CASCADE)
    info = models.TextField(blank=True, null=True)
    requester = models.ForeignKey(EmailUser, blank=False, null=False, related_name='+', on_delete=models.DO_NOTHING)
    created = models.DateTimeField(default=timezone.now, editable=False)
    request_type = models.CharField(max_length=40, choices=RequestTypeEnum.REQUEST_TYPE_CHOICES)
    
    objects = models.Manager()
    queued_jobs = ActiveTaskMonitorManager()

    class Meta:
        app_label = 'disturbance'
        verbose_name_plural = "Task Monitor"

    def __str__(self):
        return f'Task {self.task_id}, Proposal: {self.proposal}'

class JobQueue(models.Model):
    STATUS = (
       (0, 'Pending'),
       (1, 'Running'),
       (2, 'Completed'),
       (3, 'Failed'),
    )

    job_cmd = models.CharField(max_length=1000, null=True, blank=True)
    system_id = models.CharField(max_length=4, null=True, blank=True)
    status = models.SmallIntegerField(choices=STATUS, default=0) 
    parameters_json = models.JSONField(null=True, blank=True)
    processed_dt = models.DateTimeField(default=None,null=True, blank=True )
    user = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_cmd 

    class Meta:
        app_label = 'disturbance' 


class Notice(models.Model):

    NOTICE_TYPE_CHOICES = (
        (0, 'Red Warning'),
        (1, 'Orange Warning'),
        (2, 'Blue Warning') ,
        (3, 'Green Warning')   
        )

    notice_type = models.IntegerField(choices=NOTICE_TYPE_CHOICES,default=0)
    message = models.TextField(null=True, blank=True, default='')
    order = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'disturbance'

    def __str__(self):
           return '{}'.format(strip_tags(self.message).replace('&nbsp;', ' '))
    
    def save(self, *args, **kwargs):
        cache.delete('helpers.get_notices()')
        self.full_clean()
        super(Notice, self).save(*args, **kwargs)

import reversion
reversion.register(TaskMonitor)

