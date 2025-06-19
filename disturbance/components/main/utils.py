from datetime import datetime
import os
import requests
import json
import pytz
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import Distance
from django.core.cache import cache
from django.db import connection, transaction
from django.db.models.query_utils import Q
from rest_framework import serializers
from ledger.accounts.models import EmailUser

from rest_framework.renderers import JSONRenderer
#from disturbance.components.proposals.serializers import SpatialQueryQuestionSerializer

from disturbance.components.main.decorators import timeit
from disturbance.settings import SITE_STATUS_DRAFT, SITE_STATUS_APPROVED, SITE_STATUS_TRANSFERRED, RESTRICTED_RADIUS, \
    SITE_STATUS_PENDING, SITE_STATUS_DISCARDED, SITE_STATUS_VACANT, SITE_STATUS_DENIED, SITE_STATUS_CURRENT, \
    SITE_STATUS_NOT_TO_BE_REISSUED, SITE_STATUS_SUSPENDED

# from disturbance.components.proposals.models import Proposal
# from disturbance.components.approvals.models import Approval
# from disturbance.components.compliances.models import Compliance
from disturbance.settings import MAX_NUM_ROWS_MODEL_EXPORT
from django.db.models import Case, Value, When, CharField, Count, F
from django.db.models.functions import Concat, Cast
import csv
import xlsxwriter
import datetime
import uuid
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Subquery, OuterRef

# from disturbance.components.proposals.models import Proposal

import logging
logger = logging.getLogger(__name__)


#def retrieve_department_users():
#    try:
#        res = requests.get('{}/api/users?minimal'.format(settings.CMS_URL), auth=(settings.LEDGER_USER,settings.LEDGER_PASS), verify=False)
#        res.raise_for_status()
#        cache.set('department_users',json.loads(res.content).get('objects'),10800)
#    except:
#        raise
#
#
#def get_department_user(email):
#    try:
#        res = requests.get('{}/api/users?email={}'.format(settings.CMS_URL,email), auth=(settings.LEDGER_USER,settings.LEDGER_PASS), verify=False)
#        res.raise_for_status()
#        data = json.loads(res.content).get('objects')
#        if len(data) > 0:
#            return data[0]
#        else:
#            return None
#    except:
#        raise
#


def retrieve_department_users():
    try:
        res = requests.get('{}/api/users?minimal'.format(settings.CMS_URL), auth=(settings.LEDGER_USER,settings.LEDGER_PASS), verify=False)
        res.raise_for_status()
        cache.set('department_users',json.loads(res.content).get('objects'),10800)
    except:
        raise


def get_department_user(email):
    if (EmailUser.objects.filter(email__iexact=email.strip()) and 
            EmailUser.objects.get(email__iexact=email.strip()).is_staff):
        return True
    return False


def to_local_tz(_date):
    local_tz = pytz.timezone(settings.TIME_ZONE)
    return _date.astimezone(local_tz)


def check_db_connection():
    """  check connection to DB exists, connect if no connection exists """
    try:
        if not connection.is_usable():
            connection.connect()
    except Exception as e:
        connection.connect()


def convert_utc_time_to_local(utc_time_str_with_z):
    """
    This function converts datetime str like '', which is in UTC, to python datetime in local
    """
    if utc_time_str_with_z:
        # Serialized moment obj is supposed to be sent. Which is UTC timezone.
        date_utc = datetime.strptime(utc_time_str_with_z, '%Y-%m-%dT%H:%M:%S.%fZ')
        # Add timezone (UTC)
        date_utc = date_utc.replace(tzinfo=pytz.UTC)
        # Convert the timezone to TIME_ZONE
        date_perth = date_utc.astimezone(pytz.timezone(settings.TIME_ZONE))
        return date_perth
    else:
        return utc_time_str_with_z


def get_template_group(request):
    return 'das'


def _get_params(layer_name, coords):
    return {
        'SERVICE': 'WMS',
        'VERSION': '1.1.1',
        'REQUEST': 'GetFeatureInfo',
        'FORMAT': 'image/png',
        'TRANSPARENT': True,
        'QUERY_LAYERS': layer_name,
        'STYLES': '',
        'LAYERS': layer_name,
        'INFO_FORMAT': 'application/json',
        'FEATURE_COUNT': 1,  # Features should not be overwrapped
        'X': 50,
        'Y': 50,
        'SRS': 'EPSG:4283',
        'WIDTH': 101,
        'HEIGHT': 101,
        'BBOX': str(coords[0] - 0.0001) + ',' + str(coords[1] - 0.0001) + ',' + str(coords[0] + 0.0001) + ',' + str( coords[1] + 0.0001),
    }

def get_feature_in_wa_coastline_original(wkb_geometry):
    return get_feature_in_wa_coastline(wkb_geometry, False)


@timeit
def get_feature_in_wa_coastline_smoothed(wkb_geometry):
    return get_feature_in_wa_coastline(wkb_geometry, True)


def get_feature_in_wa_coastline(wkb_geometry, smoothed):
    from disturbance.components.main.models import WaCoast

    try:
        features = WaCoast.objects.filter(wkb_geometry__contains=wkb_geometry, smoothed=smoothed)
        if features:
            return features[0]
        else:
            return None
    except:
        return None


def get_feature_in_wa_coastline_kmi(wkb_geometry):
    try:
        URL = 'https://kmi.dpaw.wa.gov.au/geoserver/public/wms'
        coords = wkb_geometry.get_coords()
        PARAMS = _get_params('public:wa_coast_pub', coords)
        res = requests.get(url=URL, params=PARAMS)
        geo_json = res.json()
        feature = None
        if len(geo_json['features']) > 0:
            feature = geo_json['features'][0]
        return feature
    except:
        return None


def get_tenure(wkb_geometry):
    try:
        URL = 'https://kmi.dpaw.wa.gov.au/geoserver/public/wms'
        coords = wkb_geometry.get_coords()
        PARAMS = _get_params('public:dpaw_lands_and_waters', coords)
        res = requests.get(url=URL, params=PARAMS)
        geo_json = res.json()
        tenure_name = ''
        if len(geo_json['features']) > 0:
            tenure_name = geo_json['features'][0]['properties']['tenure']
        return tenure_name
    except:
        return ''


def get_region_district(wkb_geometry):
    from disturbance.components.main.models import RegionDbca
    from disturbance.components.main.models import DistrictDbca

    try:
        regions = RegionDbca.objects.filter(wkb_geometry__contains=wkb_geometry, enabled=True)
        districts = DistrictDbca.objects.filter(wkb_geometry__contains=wkb_geometry, enabled=True)
        text_arr = []
        if regions:
            text_arr.append(regions.first().region_name)
        if districts:
            text_arr.append(districts.first().district_name)

        ret_text = '/'.join(text_arr)
        return ret_text
    except:
        return ''


def handle_validation_error(e):
    # if hasattr(e, 'error_dict'):
    #     raise serializers.ValidationError(repr(e.error_dict))
    # else:
    #     raise serializers.ValidationError(repr(e[0].encode('utf-8')))
    if hasattr(e, 'error_dict'):
        raise serializers.ValidationError(repr(e.error_dict))
    else:
        if hasattr(e, 'message'):
            raise serializers.ValidationError(e.message)
        else:
            raise


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def custom_strftime(format_str, t):
    return t.strftime(format_str).replace('{S}', str(t.day) + suffix(t.day))

def getProposalExport(filters, num):
    from disturbance.components.proposals.models import Proposal
    qs = Proposal.objects.order_by("-lodgement_date").exclude(processing_status='hidden')
    if filters:
        #type
        if "type" in filters and filters["type"] and not filters["type"].lower() == 'all':
            qs = qs.filter(application_type=filters["type"])
        #lodged_on_from
        if "lodged_on_from" in filters and filters["lodged_on_from"]:
            qs = qs.filter(lodgement_date__gte=filters["lodged_on_from"])
        #lodged_on_to
        if "lodged_on_to" in filters and filters["lodged_on_to"]:
            qs = qs.filter(lodgement_date__lte=filters["lodged_on_to"])
        #category
        # if "category" in filters and filters["category"] and not filters["category"].lower() == 'all':
        #     qs = qs.filter(proposal_type__code=filters["category"])
        #status
        if "status" in filters and filters["status"] and not filters["status"].lower() == 'all':
            qs = qs.filter(processing_status=filters["status"])

    return qs[:num]
    
def getApprovalExport(filters, num):
    from disturbance.components.approvals.models import Approval
    qs = Approval.objects.all().exclude(status='hidden')
    ids = qs.order_by('lodgement_number', '-issue_date').distinct('lodgement_number').values_list('id', flat=True)
    qs = qs.filter(id__in=ids)
    
    # for obj in qs:
    #     if hasattr(obj.proxy_applicant, 'get_full_name') and obj.proxy_applicant.get_full_name():
    #         name = obj.proxy_applicant.get_full_name()
    #     elif hasattr(obj.applicant, 'name'):
    #         name = obj.applicant.name
    #     else:
    #         name = str(obj.applicant)

    if filters:
        #type
        # if "type" in filters and filters["type"] and not filters["type"].lower() == 'all':
        #     if filters["type"].lower() == 'ml':
        #         qs = qs.filter(lodgement_number__startswith="MOL")
        #expiry_from
        if "expiry_from" in filters and filters["expiry_from"]:
            qs = qs.filter(expiry_date__gte=filters["expiry_from"])
        #issued_to
        if "expiry_to" in filters and filters["expiry_to"]:
            qs = qs.filter(expiry_date__lte=filters["expiry_to"])
        #status
        if "status" in filters and filters["status"] and not filters["status"].lower() == 'all':
            qs = qs.filter(status=filters["status"])

    return qs[:num]
    
def getComplianceExport(filters, num):
    from disturbance.components.compliances.models import Compliance
    qs = Compliance.objects.order_by("-lodgement_date")

    if filters:
        #lodged_on_from
        if "lodged_on_from" in filters and filters["lodged_on_from"]:
            qs = qs.filter(lodgement_date__gte=filters["lodged_on_from"])
        #lodged_on_to
        if "lodged_on_to" in filters and filters["lodged_on_to"]:
            qs = qs.filter(lodgement_date__lte=filters["lodged_on_to"])
        #status
        if "status" in filters and filters["status"] and not filters["status"].lower() == 'all':
            qs = qs.filter(processing_status=filters["status"])

    return qs[:num]


def exportModelData(model, filters, num_records):

    if not num_records:
        num_records = MAX_NUM_ROWS_MODEL_EXPORT
    else:
        num_records = min(num_records, MAX_NUM_ROWS_MODEL_EXPORT)

    if model == "proposal":
        return getProposalExport(filters, num_records)
    elif model == "approval": #exclude waiting list
        return getApprovalExport(filters, num_records)
    elif model == "compliance":
        return getComplianceExport(filters, num_records)
    else:
        return

def csvExportData(model, header, columns):
    
    csv_file = str(settings.BASE_DIR)+'/tmp/{}_{}_{}.csv'.format(model,uuid.uuid4(),int(datetime.datetime.now().timestamp()*100000))
    with open(csv_file, 'w', newline='') as new_file:
        writer = csv.writer(new_file)
        writer.writerow(header)
        for i in columns:
            writer.writerow(i)
    return csv_file

def excelExportData(model, header, columns):
    excel_file = str(settings.BASE_DIR)+'/tmp/{}_{}_{}.xlsx'.format(model,uuid.uuid4(),int(datetime.datetime.now().timestamp()*100000))
    workbook = xlsxwriter.Workbook(excel_file) 
    worksheet = workbook.add_worksheet("{} Report".format(model.capitalize()))
    format = workbook.add_format()

    col = 0 
    row = 0

    col_lens = [0]*len(header)

    for i in header:
        worksheet.write(row, col, str(i), format)
        col_lens[col] = len(str(i))+2
        worksheet.set_column(col, col, col_lens[col])
        col += 1
    col = 0 
    row += 1
    for i in columns:
        for j in i:
            worksheet.write(row, col, str(j), format)
            if len(str(j)) > col_lens[col]:
                col_lens[col] = len(str(j))+2
                worksheet.set_column(col, col, col_lens[col])
            col += 1
        col = 0
        row += 1

    workbook.close() 

    return excel_file

def getProposalExportFields(data):
    header = ["Lodgement Number", "Proposal Type", "Region", "District", "Activity", "Title", "Submitter", "Proponent", "Lodged On", "Approval", "Status"]

    columns = list(data.annotate(
        submitter_name=Concat(
            'submitter__first_name',
            Value(" "),
            'submitter__last_name'
            ),
        ).values_list(
        "lodgement_number",
        "application_type__name",
        "region__name",
        "district__name",
        "activity",
        "title",
        "submitter_name",
        "applicant__organisation__name",
        "lodgement_date",
        "approval__lodgement_number",
        "processing_status",
        )
    )
    
    return header, columns

def getApprovalExportFields(data):
    from disturbance.components.proposals.models import Proposal
    # header = ["Lodgement Number", "Region" , "Activity", "Title", "Holder", "Associated Proposals", "Status", "Start Date", "Expiry Date"]
    header = ["Lodgement Number", "Region" , "Activity", "Title",  "Associated Proposals", "Status", "Start Date", "Expiry Date"]
    columns = list(data
    # .annotate(
    #     associated_proposals=Subquery(Proposal.objects.filter(approval__lodgement_number=OuterRef("lodgement_number")).values_list('lodgement_number', flat=True))
    # )
    .annotate(
        associated_proposals=Subquery(
            Proposal.objects.filter(approval__lodgement_number=OuterRef("lodgement_number"))
            .order_by()
            .annotate(proposals=ArrayAgg('lodgement_number'))
            .values('proposals')[:1],
            )
    )
    .values_list(
        "lodgement_number",
        "current_proposal__region__name",
        "current_proposal__activity",
        "current_proposal__title",
        "associated_proposals",
        "status",
        "start_date",
        "expiry_date",
        )
    )
    
    return header, columns

def getComplianceExportFields(data):
    header = ["Lodgement Number", "Type", "Approval Number", "Holder", "Status", "Due Date"]

    columns = list(data.annotate(type=
        Case(
            When(
                approval__lodgement_number__startswith='MOL',
                then=Value("Mooring Site Licence")
            ),
            When(
                approval__lodgement_number__startswith='AAP',
                then=Value("Annual Admission Permit")
            ),
            When(
                approval__lodgement_number__startswith='AUP',
                then=Value("Authorised User Permit")
            ),
            default=Value(''),
            output_field=CharField(),     
        )
    ).annotate(
        holder=Concat(
            'proposal__proposal_applicant__first_name',
            Value(" "),
            'proposal__proposal_applicant__last_name'
            ),
    ).values_list(
        "lodgement_number",
        "type",
        "approval__lodgement_number",
        "holder",
        "processing_status",
        "due_date",
        )
    )

    return header, columns

def formatExportData(model, data, format):

    if model == "proposal":
        header, columns = getProposalExportFields(data)
    elif model == "approval": 
        header, columns = getApprovalExportFields(data)
    elif model == "compliance":
        header, columns = getComplianceExportFields(data)
    
    if os.path.isdir(str(settings.BASE_DIR)+'/tmp/') is False:
        os.makedirs(str(settings.BASE_DIR)+'/tmp/')

    if format == "excel":
        file_name = excelExportData(model, header, columns)
        file_buffer = None
        with open(file_name, 'rb') as f:
            file_buffer = f.read()    
        return ('Disturbance - {} Report.xlsx'.format(model.capitalize()), file_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        file_name =  csvExportData(model, header, columns)
        file_buffer = None
        with open(file_name, 'rb') as f:
            file_buffer = f.read()    
        return ('Disturbance - {} Report.csv'.format(model.capitalize()), file_buffer, 'application/csv')

