import re
from telnetlib3 import NEW_ENVIRON
import traceback
import os
import csv
import requests
from requests.auth import HTTPBasicAuth

import json
from dateutil import parser
from deepdiff import DeepDiff

import pytz
from ledger.settings_base import TIME_ZONE, DATABASES
from django.conf import settings
from django.db.models import F, Q
from django.db import transaction, connection
from django.core.exceptions import ValidationError
from rest_framework import viewsets, serializers, status, views
from rest_framework.decorators import action, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from ledger.accounts.models import EmailUser
from datetime import datetime
import time
from reversion.models import Version
from django.core.cache import cache
from rest_framework.exceptions import NotFound

from django.http import HttpResponse, JsonResponse #, Http404
from disturbance.components.main.decorators import basic_exception_handler, timeit, query_debugger, api_exception_handler
from disturbance.components.proposals.utils import (
    save_proponent_data,
    save_assessor_data,
    search_schema,
    gen_shapefile,
)
from disturbance.components.proposals.models import ProposalDocument, searchKeyWords, search_reference, \
    ExportDocument, search_sections, get_search_geojson, private_storage
from disturbance.settings import SITE_STATUS_DRAFT, SITE_STATUS_APPROVED, SITE_STATUS_CURRENT, SITE_STATUS_DENIED, \
    SITE_STATUS_NOT_TO_BE_REISSUED, SITE_STATUS_VACANT, SITE_STATUS_TRANSFERRED, SITE_STATUS_DISCARDED
from disturbance.utils import search_tenure, search_label, get_schema_questions
from disturbance.components.main.utils import (
    check_db_connection,
    handle_validation_error,
    get_template_group,
)

from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from disturbance.components.main.models import ApplicationType, DASMapLayer
from disturbance.components.proposals.models import (
    ProposalType,
    Proposal,
    Referral,
    ProposalRequirement,
    ProposalStandardRequirement,
    AmendmentRequest,
    AmendmentReason,
    AmendmentRequestDocument,
    ProposalTypeSection,
    SectionQuestion,
    MasterlistQuestion,
    CddpQuestionGroup,
    SpatialQueryQuestion,
    SpatialQueryLayer,
    SpatialQueryMetrics,
    ProposalUserAction,
)
from disturbance.components.proposals.serializers import (
    SendReferralSerializer,
    ProposalTypeSerializer,
    ProposalSerializer,
    InternalProposalSerializer,
    SaveProposalSerializer,
    ProposalUserActionSerializer,
    ProposalLogEntrySerializer,
    DTReferralSerializer,
    ReferralSerializer,
    ProposalRequirementSerializer,
    ProposalStandardRequirementSerializer,
    ProposedApprovalSerializer,
    ProposedApprovalSiteTransferSerializer,
    PropedDeclineSerializer,
    AmendmentRequestSerializer,
    SearchReferenceSerializer,
    SearchKeywordSerializer,
    ListProposalSerializer,
    AmendmentRequestDisplaySerializer,
    SaveProposalRegionSerializer,
    ProposalWrapperSerializer,
    ReferralWrapperSerializer,
    ProposalTypeSectionSerializer,
    DTSchemaQuestionSerializer,
    SchemaMasterlistSerializer,
    DTSchemaMasterlistSerializer,
    SchemaQuestionSerializer,
    SelectSchemaMasterlistSerializer,
    DTSchemaProposalTypeSerializer,
    SchemaProposalTypeSerializer,
    SchemaMasterlistOptionSerializer,
    DASMapFilterSerializer,
    SearchGeoJsonSerializer,
    SearchProposalTypeSerializer,
)
#from disturbance.components.proposals.sqs_utils.serializers import (
#    DTSpatialQueryQuestionSerializer,
#    SpatialQueryLayerSerializer,
#    DTSpatialQueryMetricsSerializer,
#    DTSpatialQueryMetricsDetailsSerializer,
#    DTSpatialQueryLayersUsedSerializer,
#    CddpQuestionGroupSerializer,
#)
from disturbance.components.approvals.models import Approval
from disturbance.components.approvals.serializers import ApprovalLogEntrySerializer
from disturbance.components.compliances.models import Compliance
from disturbance.components.main.serializers import DASMapLayerSqsSerializer

from disturbance.helpers import is_authorised_to_modify, is_customer, is_internal, is_authorised_to_modify_draft
from django.core.files.base import ContentFile
from rest_framework.pagination import PageNumberPagination
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer
from disturbance.components.main.process_document import (
        process_generic_document, 
        )


import logging
logger = logging.getLogger(__name__)


class GetProposalType(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        _type = ProposalType.objects.first()
        if _type:
            serializer = ProposalTypeSerializer(_type)
            return Response(serializer.data)
        else:
            return Response({'error': 'There is currently no proposal type.'}, status=status.HTTP_404_NOT_FOUND)

class GetEmptyList(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        return Response([])

#class DatatablesFilterBackend(BaseFilterBackend):
#
#       def filter_queryset(self, request, queryset, view):
#               queryset = super(DatatablesFilterBackend, self).filter_queryset(request, queryset, view)
#               return queryset

class ProposalFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """

    def filter_queryset(self, request, queryset, view):
        search_text = request.GET.get('search[value]', '')
        total_count = queryset.count()
        def get_choice(status, choices=Proposal.PROCESSING_STATUS_CHOICES):
            for i in choices:
                if i[1]==status:
                    return i[0]
            return None

        # on the internal dashboard, the Region filter is multi-select - have to use the custom filter below
        regions = request.GET.get('regions')
        if regions:
            if queryset.model is Proposal:
                queryset = queryset.filter(region__name__iregex=regions.replace(',', '|'))
            elif queryset.model is Referral or queryset.model is Compliance:
                queryset = queryset.filter(proposal__region__name__iregex=regions.replace(',', '|'))

        districts = request.GET.get('districts')
        if districts:
            if queryset.model is Proposal:
                queryset = queryset.filter(district__name__iregex=districts.replace(',', '|'))

            #elif queryset.model is Approval:
            #    queryset = queryset.filter(region__iregex=regions.replace(',', '|'))

        # since in proposal_datatables.vue, the 'region' data field is declared 'searchable=false'
        #global_search = request.GET.get('search[value]')
        #if global_search:
        #    queryset = queryset.filter(region__name__iregex=global_search)


        # on the internal dashboard, the Referral 'Status' filter - have to use the custom filter below
#        processing_status = request.GET.get('processing_status')
#        processing_status = get_choice(processing_status, Proposal.PROCESSING_STATUS_CHOICES)
#        if processing_status:
#            if queryset.model is Referral:
#                #processing_status_id = [i for i in Proposal.PROCESSING_STATUS_CHOICES if i[1]==processing_status][0][0]
#                queryset = queryset.filter(processing_status=processing_status)
        application_type = request.GET.get('application_type')
        if application_type and not application_type.lower() =='all':
            if queryset.model is Referral or queryset.model is Compliance:
                queryset = queryset.filter(proposal__application_type__name=application_type)
            else:
                queryset = queryset.filter(application_type__name=application_type)
        proposal_activity = request.GET.get('proposal_activity')
        if proposal_activity and not proposal_activity.lower() == 'all':
            if queryset.model is Referral or queryset.model is Compliance:
                queryset = queryset.filter(proposal__activity=proposal_activity)
            else:
                queryset = queryset.filter(activity=proposal_activity)
        proposal_status = request.GET.get('proposal_status')
        if proposal_status and not proposal_status.lower() == 'all':
            #processing_status = get_choice(proposal_status, Proposal.PROCESSING_STATUS_CHOICES)
            #queryset = queryset.filter(processing_status=processing_status)
            if queryset.model is Referral or queryset.model is Compliance:
                queryset = queryset.filter(proposal__processing_status=proposal_status)
            else:
                queryset = queryset.filter(processing_status=proposal_status)
        submitter = request.GET.get('submitter')
        if submitter and not submitter.lower() == 'all':
            if queryset.model is Referral or queryset.model is Compliance:
                queryset = queryset.filter(proposal__submitter__email=submitter)
            else:
                queryset = queryset.filter(submitter__email=submitter)
        applicant = request.GET.get('applicant')
        if applicant and not applicant.lower() == 'all':
            if queryset.model is Referral or queryset.model is Compliance:
                queryset = queryset.filter(proposal__applicant_id=applicant)
            else:
                queryset = queryset.filter(applicant_id=applicant)
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        if queryset.model is Proposal:
            if date_from:
                queryset = queryset.filter(lodgement_date__gte=date_from)

            if date_to:
                queryset = queryset.filter(lodgement_date__lte=date_to)
        elif queryset.model is Approval: #TODO check if this is ever used
            if date_from:
                queryset = queryset.filter(expiry_date__gte=date_from)

            if date_to:
                queryset = queryset.filter(expiry_date__lte=date_to)
        elif queryset.model is Compliance: #TODO check if this is ever used
            if date_from:
                queryset = queryset.filter(due_date__gte=date_from)

            if date_to:
                queryset = queryset.filter(due_date__lte=date_to)

            if request.GET.get('processing_status'):
                queryset = queryset.filter(processing_status__icontains=request.GET.get('processing_status'))

            if request.GET.get('customer_status'):
                queryset = queryset.filter(customer_status__icontains=request.GET.get('customer_status'))

        elif queryset.model is Referral:
            if date_from:
                queryset = queryset.filter(proposal__lodgement_date__gte=date_from)

            if date_to:
                queryset = queryset.filter(proposal__lodgement_date__lte=date_to)

        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        sort_by = request.GET.get('sort_by')
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            #for num, item in enumerate(ordering):
             #   if item == 'status__name':
              #      ordering[num] = 'status'
               # elif item == '-status__name':
                #    ordering[num] = '-status'
            queryset = queryset.order_by(*ordering)
        
        try:
            queryset = super(ProposalFilterBackend, self).filter_queryset(request, queryset, view)
        except Exception as e:
            print(e)
        if(sort_by and sort_by!=''):
            if queryset.model is Proposal:
                queryset = queryset.order_by(sort_by)
        setattr(view, '_datatables_total_count', total_count)
        return queryset


class ProposalPaginatedViewSet(viewsets.ModelViewSet):
    #filter_backends = (DatatablesFilterBackend,)
    filter_backends = (ProposalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    #renderer_classes = (ProposalRenderer,)
    queryset = Proposal.objects.none()
    serializer_class = ListProposalSerializer
    search_fields = ['lodgement_number',]
    #serializer_class = DTProposalSerializer
    page_size = 10

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request): #user.is_authenticated():
            #return Proposal.objects.all().order_by('-id')
            return Proposal.objects.exclude(processing_status='hidden')
            #TODO will need to exclude apiary proposals
            # return Proposal.objects.exclude(processing_status='hidden').filter(~Q(application_type__name__in=apiary_proposal_types))
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.disturbance_organisations.all()]
            #return  Proposal.objects.filter( Q(applicant_id__in = user_orgs) | Q(submitter = user) )
            #return Proposal.objects.filter( Q(applicant_id__in = user_orgs) | Q(submitter = user) | Q(proxy_applicant = user)).order_by('-id')
            qs = Proposal.objects.exclude(processing_status='hidden').filter(Q(applicant_id__in=user_orgs) | Q(submitter=user) | Q(proxy_applicant=user))
            return qs
            #queryset =  Proposal.objects.filter(region__isnull=False).filter( Q(applicant_id__in = user_orgs) | Q(submitter = user) )
        return Proposal.objects.none()
    
    def get_external_queryset(self):
        user = self.request.user
        if is_internal(self.request): #user.is_authenticated():
            #return Proposal.objects.all().order_by('-id')
            #return Proposal.objects.exclude(processing_status='hidden')
            user_orgs = [org.id for org in user.disturbance_organisations.all()]
            qs = Proposal.objects.exclude(processing_status='hidden').filter(Q(applicant_id__in=user_orgs) | Q(submitter=user) | Q(proxy_applicant=user))
            return qs
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.disturbance_organisations.all()]
            #return  Proposal.objects.filter( Q(applicant_id__in = user_orgs) | Q(submitter = user) )
            #return Proposal.objects.filter( Q(applicant_id__in = user_orgs) | Q(submitter = user) | Q(proxy_applicant = user)).order_by('-id')
            qs = Proposal.objects.exclude(processing_status='hidden').filter(Q(applicant_id__in=user_orgs) | Q(submitter=user) | Q(proxy_applicant=user))
            return qs
            #queryset =  Proposal.objects.filter(region__isnull=False).filter( Q(applicant_id__in = user_orgs) | Q(submitter = user) )
        return Proposal.objects.none()

    @action(methods=['GET',], detail=False)
    def proposals_internal(self, request, *args, **kwargs):
        """
        Used by the internal dashboard

        http://localhost:8499/api/proposal_paginated/proposal_paginated_internal/?format=datatables&draw=1&length=2
        """
        template_group  =  get_template_group(request)
        if template_group == 'das':
            apiary_proposal_types=['Apiary','Site Transfer','Temporary Use']
            qs = self.get_queryset().exclude(
                        application_type__name__in=apiary_proposal_types
                    )
        qs = self.filter_queryset(qs)

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
        applicant_id = request.GET.get('org_id')
        if applicant_id:
            qs = qs.filter(applicant_id=applicant_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ListProposalSerializer(result_page, context={
            'request':request,
            'template_group': 'DAS'
            }, many=True)
        #serializer = DTProposalSerializer(result_page, context={'request':request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    @action(methods=['GET',], detail=False)
    def referrals_internal(self, request, *args, **kwargs):
        """
        Used by the internal dashboard

        http://localhost:8499/api/proposal_paginated/referrals_internal/?format=datatables&draw=1&length=2
        """
        #self.serializer_class = ReferralSerializer
        template_group = get_template_group(request)
        if template_group == 'das':
            qs = Referral.objects.filter(referral=request.user) if is_internal(self.request) else Referral.objects.none()
        #for r in qs_r:
         #   referral_id_list.append(r.id)
        #qs = self.filter_queryset(self.request, qs, self)
        # Add Apiary Referrals
        #qs_ra = Referral.objects.filter(apiary_referral__referral_group__members=request.user)
        #qs = qs_r.union(qs_ra) if qs_r else qs_ra
        #for ar in qs_ra:
         #   if ar.id not in referral_id_list:
          #      referral_id_list.append(ar.id)
        #qs = Referral.objects.filter(id__in=referral_id_list)
        qs = self.filter_queryset(qs)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = DTReferralSerializer(result_page, context={
            'request':request,
            'template_group': 'DAS'
            }, many=True)
        return self.paginator.get_paginated_response(serializer.data)


    @action(methods=['GET',], detail=False)
    def proposals_external(self, request, *args, **kwargs):
        """
        Used by the external dashboard

        http://localhost:8499/api/proposal_paginated/proposal_paginated_external/?format=datatables&draw=1&length=2
        """
        template_group = get_template_group(request)
        if template_group == 'das':
            apiary_proposal_types=['Apiary','Site Transfer','Temporary Use']
            # qs = self.get_queryset().exclude(application_type__name__in=apiary_proposal_types
            #                                  ).exclude(processing_status=Proposal.PROCESSING_STATUS_DISCARDED)
            qs = self.get_external_queryset().exclude(application_type__name__in=apiary_proposal_types
                                             ).exclude(processing_status=Proposal.PROCESSING_STATUS_DISCARDED)
        qs = self.filter_queryset(qs)

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
        applicant_id = request.GET.get('org_id')
        if applicant_id:
            qs = qs.filter(applicant_id=applicant_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ListProposalSerializer(result_page, context={
            'request':request,
            'template_group': 'DAS'
            }, many=True)
        #serializer = DTProposalSerializer(result_page, context={'request':request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    @action(methods=['GET', ], detail=False)
    def spatial_query_layers_used_datatable_list(self, request, *args, **kwargs):
        """ http://localhost:8003/api/proposal_paginated/spatial_query_layers_used_datatable_list/?format=datatables&draw=1&length=10 """
        self.serializer_class = DTSpatialQueryLayersUsedSerializer 
        queryset = self.get_queryset().filter(layer_data__isnull=False, processing_status=Proposal.PROCESSING_STATUS_APPROVED)

        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        # self.paginator.page_size = 0
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTSpatialQueryLayersUsedSerializer(
            result_page, context={'request': request}, many=True
        )
        data = serializer.data

        response = self.paginator.get_paginated_response(data)
        return response
    

class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.none()
    serializer_class = ProposalSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Proposal.objects.filter(
                Q(region__isnull=False)
            )
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.disturbance_organisations.all()]
            queryset = Proposal.objects.filter(region__isnull=False).filter(
                Q(applicant_id__in=user_orgs) |
                Q(submitter=user)
            ).exclude(processing_status='')
            return queryset

        #logger.warn("User is neither customer nor internal user: {} <{}>".format(user.get_full_name(), user.email))
        return Proposal.objects.none()

    #TODO: review this - is this needed?
    def get_object(self):
        check_db_connection()
        try:
            obj = super(ProposalViewSet, self).get_object()
        except Exception as e:
            # because current queryset excludes migrated licences
            #obj = get_object_or_404(Proposal, id=self.kwargs['id'])
            obj_id = self.kwargs['id'] if 'id' in self.kwargs else self.kwargs['pk']
            obj = get_object_or_404(Proposal, id=obj_id)
            if self.request.user != obj.submitter:
                raise #if we do not raise here it will return a record regardless of auth
        return obj

    def get_serializer_class(self):
        try:
            # application_type = self.get_object().application_type.name
            # if application_type in (ApplicationType.APIARY, ApplicationType.SITE_TRANSFER, ApplicationType.TEMPORARY_USE):
            #     return ProposalApiaryTypeSerializer
            # else:
            #     return ProposalSerializer
            return ProposalSerializer
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def internal_serializer_class(self):
        try:
            #application_type = Proposal.objects.get(id=self.kwargs.get('pk')).application_type.name
            application_type = self.get_object().application_type.name
            return InternalProposalSerializer
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST', ], detail=False)
    @api_exception_handler
    def create_shapefile(self, request, *args, **kwargs):
        ''' requests.get('http://localhost:8003/api/proposal/create_shapefile.json')
        '''
        geojson = request.data.get('geojson', False)
        filter_kwargs = request.data.get('filter_kwargs', {})
        filename = gen_shapefile(request.user, self.get_queryset(), filter_kwargs, geojson)
        file_url = reverse('file-download', kwargs={'filename':filename})
        return Response(data={'message': f'File created {filename}'}, status=status.HTTP_200_OK)
                
    @action(methods=['POST',], detail=True)
    def get_revision(self, request, *args, **kwargs):
        """
        Use the Proposal model method to get a particular Proposal revision.
        """
        try:
            instance = self.get_object()
            version_number = request.data.get("version_number")
            revision = instance.get_revision_flat(version_number)
            
            return Response(revision)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def get_revision_diffs(self, request, *args, **kwargs):
        """
        Use the Proposal model method to get the differences between the lastest revision and
        the revision specified.
        """
        try:
            instance = self.get_object()
            newer_version = int(request.GET.get("newer_version"))
            older_version = int(request.GET.get("older_version"))
            diffs = instance.get_revision_diff(newer_version, older_version)

            return Response(diffs)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET'], detail=True)
    def version_differences(self, request, *args, **kwargs):
        """ Returns a json response containing the differences between two 
            versions.
        
        """
        try:
            newer_version = int(request.GET.get("newer_version"))
            older_version = int(request.GET.get("older_version"))
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        instance = self.get_object()
        differences = instance.get_version_differences(newer_version, older_version)

        return Response(differences)

    @action(methods=['GET'], detail=True)
    def version_differences_comment_data(self, request, *args, **kwargs):
        """ Returns a json response containing the differences between two 
            versions.
        
        """
        try:
            newer_version = int(request.GET.get("newer_version"))
            older_version = int(request.GET.get("older_version"))
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        instance = self.get_object()
        differences = instance.get_version_differences_comment_and_assessor_data('comment_data', newer_version, older_version)

        return JsonResponse(differences, safe=False)

    @action(methods=['GET'], detail=True)
    def version_differences_assessor_data(self, request, *args, **kwargs):
        """ Returns a json response containing the differences between two 
            versions.
        
        """
        try:
            newer_version = int(request.GET.get("newer_version"))
            older_version = int(request.GET.get("older_version"))
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        instance = self.get_object()
        differences = instance.get_version_differences_comment_and_assessor_data('assessor_data', newer_version, older_version)

        return JsonResponse(differences, safe=False)

    @action(methods=['GET'], detail=True)
    def version_differences_documents(self, request, *args, **kwargs):
        """ Returns a json response containing the differences between two 
            versions.
        
        """
        try:
            newer_version = int(request.GET.get("newer_version"))
            older_version = int(request.GET.get("older_version"))
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        instance = self.get_object()
        differences_only = request.GET.get('differences_only')
        differences = instance.get_document_differences(newer_version, older_version, differences_only)

        return JsonResponse(differences, safe=False)

    @action(methods=['POST'], detail=True)
    @renderer_classes((JSONRenderer,))
    def process_deed_poll_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            returned_data = process_generic_document(request, instance, document_type=DeedPollDocument.DOC_TYPE_NAME)
            if returned_data:
                return Response(returned_data)
            else:
                return Response()

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=False)
    def filter_list(self, request, *args, **kwargs):
        """ Used by the internal/external dashboard filters """
        template_group = get_template_group(request)
        region_qs = []
        activity_qs = []
        application_type_qs = []
        applicant_qs = []

        if template_group == 'das':
            apiary_proposal_types=['Apiary','Site Transfer','Temporary Use']
            qs = self.get_queryset().exclude(
                        application_type__name__in=apiary_proposal_types
                    )
            qs = self.get_queryset()
            region_qs =  qs.filter(region__isnull=False).values_list('region__name', flat=True).distinct()
            district_qs =  qs.filter(district__isnull=False).values_list('district__name', flat=True).distinct()
            submitter_qs = qs.filter(submitter__isnull=False).distinct(
                            'submitter__email').values_list('submitter__first_name','submitter__last_name','submitter__email')
            applicant_qs = qs.filter(applicant__isnull=False).distinct(
                        'applicant_id').values_list('applicant_id','applicant__organisation__name',)


        activity_qs =  qs.filter(activity__isnull=False).values_list('activity', flat=True).distinct()
        submitters = [dict(email=i[2], search_term='{} {} ({})'.format(i[0], i[1], i[2])) for i in submitter_qs]
        application_type_qs =  qs.filter(application_type__isnull=False).values_list('application_type__name', flat=True).distinct()
        applicants = [dict(id=i[0], search_term='{}'.format(i[1])) for i in applicant_qs]
        data = dict(
            regions=region_qs,
            districts=district_qs,
            activities=activity_qs,
            submitters=submitters,
            application_types=application_type_qs,
            applicants=applicants,
            approval_status_choices = [i[1] for i in Approval.STATUS_CHOICES],
        )
        return Response(data)

    @action(methods=['POST'], detail=True)
    @renderer_classes((JSONRenderer,))
    def process_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            action = request.POST.get('action')
            section = request.POST.get('input_name')

            if action == 'list' and 'input_name' in request.POST:
                pass

            elif action == 'delete' and 'document_id' in request.POST:
                document_id = request.POST.get('document_id')
                document = instance.documents.get(id=document_id)

                if document._file and os.path.isfile(document._file.path) and document.can_delete:
                    os.remove(document._file.path)

                document.delete()
                instance.save(version_comment='Approval File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history
                #instance.current_proposal.save(version_comment='File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == 'hide' and 'document_id' in request.POST:
                document_id = request.POST.get('document_id')
                document = instance.documents.get(id=document_id)

                document.hidden=True
                document.save()
                instance.save(version_comment='File hidden: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == 'save' and 'input_name' in request.POST and 'filename' in request.POST:
                proposal_id = request.POST.get('proposal_id')
                filename = request.POST.get('filename')
                _file = request.POST.get('_file')
                if not _file:
                    _file = request.FILES.get('_file')

                document = instance.documents.get_or_create(input_name=section, name=filename)[0]
                path = private_storage.save('proposals/{}/documents/{}'.format(proposal_id, filename), ContentFile(_file.read()))

                document._file = path
                document.save()
                instance.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history
                #instance.current_proposal.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history

            proposal_lodgement_date = request.POST.get('proposal_lodgement_date')
            # Only go through the overhead of finding older proposal documents when viewing a version other than current
            if proposal_lodgement_date:
                if(parser.parse(str(instance.lodgement_date))!=parser.parse(proposal_lodgement_date)):
                    # For viewing older versions of a proposal we need to build a list of documents that were not hidden at that time
                    documents = instance.documents.filter(input_name=section, uploaded_date__lte=proposal_lodgement_date).order_by('input_name', 'uploaded_date')
                    older_version_documents = []
                    for document in documents:
                        older_document_version = Version.objects.get_for_object(document)\
                        .select_related('revision').filter(revision__date_created__lte=proposal_lodgement_date).order_by('-revision__date_created').first()
                        if not older_document_version:
                            continue
                        older_document = ProposalDocument(**older_document_version.field_dict)
                        if not older_document.hidden:
                            older_document = ProposalDocument(**older_document_version.field_dict)
                            older_version_documents.append(older_document)

                    return  Response( [dict(input_name=d.input_name, name=d.name,file=d._file.url, id=d.id, can_delete=d.can_delete, can_hide=d.can_hide) for d in older_version_documents if d._file] )
                else:
                    return  Response( [dict(input_name=d.input_name, name=d.name,file=d._file.url, id=d.id, can_delete=d.can_delete, can_hide=d.can_hide) for d in instance.documents.filter(input_name=section, hidden=False) if d._file] )
            else:
                return  Response( [dict(input_name=d.input_name, name=d.name,file=d._file.url, id=d.id, can_delete=d.can_delete, can_hide=d.can_hide) for d in instance.documents.filter(input_name=section, hidden=False) if d._file] )

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST'], detail=True)
    @renderer_classes((JSONRenderer,))
    def process_map_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            action = request.POST.get('action')
            section = request.POST.get('input_name')
            if action == 'list' and 'input_name' in request.POST:
                pass

            elif action == 'delete' and 'document_id' in request.POST:
                document_id = request.POST.get('document_id')
                document = instance.map_documents.get(id=document_id)

                if document._file and os.path.isfile(document._file.path) and document.can_delete:
                    os.remove(document._file.path)

                document.delete()
                instance.save(version_comment='Map File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history
                #instance.current_proposal.save(version_comment='File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == 'hide' and 'document_id' in request.POST:
                document_id = request.POST.get('document_id')
                document = instance.map_documents.get(id=document_id)

                document.hidden=True
                document.save()
                instance.save(version_comment='Map File hidden: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == 'save' and 'input_name' in request.POST and 'filename' in request.POST:
                proposal_id = request.POST.get('proposal_id')
                filename = request.POST.get('filename').replace(' ', '_')
                _file = request.POST.get('_file')
                if not _file:
                    _file = request.FILES.get('_file')
                _file._name = filename

                #Check if the file with same extension already exists so not to allow multiple shapefiles with same extension.
                fname, fext=os.path.splitext(filename)
                doc_qs=instance.map_documents.filter(name__endswith=fext, hidden=False)
                if doc_qs:
                    raise serializers.ValidationError('Document with extension {} already exists.'.format(fext))
                else:
                    document = instance.map_documents.get_or_create(input_name=section, name=filename)[0]
                    path = private_storage.save('proposals/{}/documents/map_docs/{}'.format(proposal_id, filename), ContentFile(_file.read()))

                    document._file = path
                    document.save()
                    instance.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history
                    #instance.current_proposal.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history

            return  Response( [dict(input_name=d.input_name, name=d.name,file=d._file.url, id=d.id, can_delete=d.can_delete, can_hide=d.can_hide) for d in instance.map_documents.filter(input_name=section, hidden=False) if d._file] )

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

#    def list(self, request, *args, **kwargs):
#        #queryset = self.get_queryset()
#        #serializer = DTProposalSerializer(queryset, many=True)
#        #serializer = DTProposalSerializer(self.get_queryset(), many=True)
#        serializer = ListProposalSerializer(self.get_queryset(), context={'request':request}, many=True)
#        return Response(serializer.data)

    @action(methods=['GET',], detail=False)
    def list_paginated(self, request, *args, **kwargs):
        """
        https://stackoverflow.com/questions/29128225/django-rest-framework-3-1-breaks-pagination-paginationserializer
        """
        proposals = self.get_queryset()
        paginator = PageNumberPagination()
        #paginator = LimitOffsetPagination()
        paginator.page_size = 5
        result_page = paginator.paginate_queryset(proposals, request)
        serializer = ListProposalSerializer(result_page, context={'request':request}, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(methods=['GET',], detail=True)
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ProposalUserActionSerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = ProposalLogEntrySerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST',], detail=True)
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                request_data = request.data.copy()
                request_data['proposal'] = u'{}'.format(instance.id)
                request_data['staff'] = u'{}'.format(request.user.id)
                serializer = ProposalLogEntrySerializer(data=request_data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES.getlist("files"):
                    document = comms.documents.create(
                            name = str(f),
                            _file = f
                            )
                #for f in request.FILES:
                #    document = comms.documents.create()
                #    document.name = str(request.FILES[f])
                #    document._file = request.FILES[f]
                #    document.save()
                # End Save Documents

                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def requirements(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            #qs = instance.requirements.all()
            qs = instance.requirements.all().exclude(is_deleted=True).order_by('order')
            serializer = ProposalRequirementSerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def apiary_site_transfer_originating_approval_requirements(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            #qs = instance.requirements.all()
            #qs = instance.requirements.all().exclude(is_deleted=True)
            approval = Approval.objects.get(id=instance.proposal_apiary.originating_approval_id)
            qs = instance.apiary_requirements(approval).exclude(is_deleted=True)
            #qs = instance.apiary_site_transfer_originatingrequirements(approval_id).exclude(is_deleted=True)
            serializer = ProposalRequirementSerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def apiary_site_transfer_target_approval_requirements(self, request, *args, **kwargs):
        # for new licences, sitetransfer_approval is None
        try:
            instance = self.get_object()
            if instance.proposal_apiary.target_approval_id:
                approval = Approval.objects.get(id=instance.proposal_apiary.target_approval_id)
                qs = instance.apiary_requirements(approval).exclude(is_deleted=True)
            else:
                qs = instance.apiary_requirements().exclude(is_deleted=True)

            serializer = ProposalRequirementSerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @action(methods=['GET',], detail=True)
    def amendment_request(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.amendment_requests
            qs = qs.filter(status = 'requested')
            serializer = AmendmentRequestDisplaySerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=False)
    def user_list(self, request, *args, **kwargs):
        qs = self.get_queryset().exclude(processing_status=Proposal.PROCESSING_STATUS_DISCARDED)
        #serializer = DTProposalSerializer(qs, many=True)
        serializer = ListProposalSerializer(qs,context={'request':request}, many=True)
        return Response(serializer.data)

    @action(methods=['GET',], detail=False)
    def user_list_paginated(self, request, *args, **kwargs):
        """
        Placing Paginator class here (instead of settings.py) allows specific method for desired behaviour),
        otherwise all serializers will use the default pagination class

        https://stackoverflow.com/questions/29128225/django-rest-framework-3-1-breaks-pagination-paginationserializer
        """
        proposals = self.get_queryset().exclude(processing_status=Proposal.PROCESSING_STATUS_DISCARDED)
        paginator = DatatablesPageNumberPagination()
        paginator.page_size = proposals.count()
        result_page = paginator.paginate_queryset(proposals, request)
        serializer = ListProposalSerializer(result_page, context={'request':request}, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(methods=['GET',], detail=False)
    def list_paginated(self, request, *args, **kwargs):
        """
        Placing Paginator class here (instead of settings.py) allows specific method for desired behaviour),
        otherwise all serializers will use the default pagination class

        https://stackoverflow.com/questions/29128225/django-rest-framework-3-1-breaks-pagination-paginationserializer
        """
        proposals = self.get_queryset()
        paginator = DatatablesPageNumberPagination()
        paginator.page_size = proposals.count()
        result_page = paginator.paginate_queryset(proposals, request)
        serializer = ListProposalSerializer(result_page, context={'request':request}, many=True)
        return paginator.get_paginated_response(serializer.data)

   

    @action(methods=['GET',], detail=True)
    def internal_proposal(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.internal_view_log(request)
        #serializer = InternalProposalSerializer(instance,context={'request':request})
        serializer_class = self.internal_serializer_class()
        serializer = serializer_class(instance,context={'request': request})
        return Response(serializer.data)

    @action(methods=['GET',], detail=True)
    def internal_revision_proposal(self, request, *args, **kwargs):
        
        instance = self.get_object()

        version_number = int(request.query_params.get("revision_number"))
        revision = instance.get_revision(version_number)
        
        # Populate a new Proposal object with the version data
        instance = Proposal(**revision)

        serializer_class = self.internal_serializer_class()
        serializer = serializer_class(instance,context={'request':request})

        return Response(serializer.data)

    @action(methods=['GET',], detail=True)
    def internal_proposal_wrapper(self, request, *args, **kwargs):
        instance = self.get_object()
        #instance.internal_view_log(request)
        #serializer = InternalProposalSerializer(instance,context={'request':request})
        serializer_class = ProposalWrapperSerializer #self.internal_serializer_class()
        #serializer = serializer_class(instance,context={'request':request})
        serializer = serializer_class(instance)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    @renderer_classes((JSONRenderer,))
    def submit(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # if instance.apiary_group_application_type:
            #     save_proponent_data(instance, request, self)
            # else:
            #     instance.submit(request, self)
            #     instance.tenure = search_tenure(instance)
            instance.submit(request, self)
            instance.tenure = search_tenure(instance)

            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
            #return redirect(reverse('external'))
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['post'], detail=True)
    @renderer_classes((JSONRenderer,))
    def validate_map_files(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # if instance.apiary_group_application_type:
            #     pass
            # else:
            #     instance.validate_map_files(request)
            instance.validate_map_files(request)
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
            #return redirect(reverse('external'))
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
        
    @action(methods=['GET',], detail=True)
    def assign_request_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.assign_officer(request,request.user)
            #serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST',], detail=True)
    def assign_to(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_id = request.data.get('assessor_id',None)
            user = None
            if not user_id:
                raise serializers.ValidationError('An assessor id is required')
            try:
                user = EmailUser.objects.get(id=user_id)
            except EmailUser.DoesNotExist:
                raise serializers.ValidationError('A user with the id passed in does not exist')
            instance.assign_officer(request,user)
            #serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def unassign(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.unassign(request)
            #serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST',], detail=True)
    def switch_status(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            status = request.data.get('status')
            approver_comment = request.data.get('approver_comment')
            if not status:
                raise serializers.ValidationError('Status is required')
            else:
                if not status in ['with_assessor','with_assessor_requirements','with_approver']:
                    raise serializers.ValidationError('The status provided is not allowed')
            instance.move_to_status(request,status, approver_comment)
            #serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST',], detail=True)
    def reissue_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            status = request.data.get('status')
            if not status:
                raise serializers.ValidationError('Status is required')
            else:
                if not status in ['with_approver']:
                    raise serializers.ValidationError('The status provided is not allowed')
            instance.reissue_approval(request,status)
            #serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def renew_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance = instance.renew_approval(request)
            # if instance.apiary_group_application_type:
            #     serializer_class = self.internal_serializer_class()
            #     serializer = serializer_class(instance,context={'request':request})
            # else:
            #     serializer = SaveProposalSerializer(instance,context={'request':request})
            serializer = SaveProposalSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            if hasattr(e, 'message'):
                raise serializers.ValidationError(e.message)
            else:
                raise

    @action(methods=['GET',], detail=True)
    def amend_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance = instance.amend_approval(request)
            serializer = SaveProposalSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            if hasattr(e, 'message'):
                raise serializers.ValidationError(e.message)
            else:
                raise

    @action(methods=['POST',], detail=True)
    def proposed_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # if instance.application_type.name == ApplicationType.SITE_TRANSFER:
            #     #serializer = ProposedApprovalSiteTransferSerializer(data=request.data)
            #     serializer = ProposedApprovalSerializer(data=request.data)
            #     serializer.is_valid(raise_exception=True)
            # else:
            #     serializer = ProposedApprovalSerializer(data=request.data)
            #     serializer.is_valid(raise_exception=True)
            serializer = ProposedApprovalSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.proposed_approval(request,serializer.validated_data)
            #serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST',], detail=True)
    def approval_level_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance = instance.assing_approval_level_document(request)
            #serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST',], detail=True)
    def approval_level_comment(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance = instance.save_approval_level_comment(request)
            #serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST',], detail=True)
    @basic_exception_handler
    def final_approval_temp_use(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.final_approval_temp_use(request,)
        return Response({})

    @action(methods=['POST',], detail=True)
    @basic_exception_handler
    def final_decline_temp_use(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.final_decline_temp_use(request,)
        return Response({})

    @action(methods=['POST',], detail=True)
    def final_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ProposedApprovalSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.final_approval(request,serializer.validated_data)
            #serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST',], detail=True)
    def proposed_decline(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = PropedDeclineSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.proposed_decline(request,serializer.validated_data)
            #serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST',], detail=True)
    def final_decline(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = PropedDeclineSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.final_decline(request,serializer.validated_data)
            #serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['post'], detail=True)
    def assesor_send_referral(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = SendReferralSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            #text=serializer.validated_data['text']
            #instance.send_referral(request,serializer.validated_data['email'])
            instance.send_referral(request,serializer.validated_data['email'], serializer.validated_data['text'])
            #serializer = InternalProposalSerializer(instance,context={'request':request})
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['post'], detail=True)
    @basic_exception_handler
    def remove_apiary_site(self, request, *args, **kwargs):
        proposal_obj = self.get_object()
        apiary_site_id = request.data.get('apiary_site_id')

        apiary_site = ApiarySite.objects.get(id=apiary_site_id)
        apiary_site_on_proposal = ApiarySiteOnProposal.objects.get(apiary_site=apiary_site, proposal_apiary=proposal_obj.proposal_apiary)
        apiary_site_on_proposal.delete()

        return Response({'removed': 'success'})
 
    @action(methods=['post'], detail=True)
    @renderer_classes((JSONRenderer,))
    def draft(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            # Ensure the current user is a member of the organisation that created the draft application.
            is_authorised_to_modify_draft(request, instance)

            save_proponent_data(instance, request, self)
            return redirect(reverse('external'))
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['post'], detail=True)
    @renderer_classes((JSONRenderer,))
    def update_region_section(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            region = request.data.get('region')
            district = request.data.get('district')
            activity = request.data.get('activity')
            sub_activity1 = request.data.get('sub_activity1')
            sub_activity2 = request.data.get('sub_activity2')
            management_area = request.data.get('category')
            approval_level = request.data.get('approval_level')
            data={
                'region': region,
                'district': district,
                'activity': activity,
                'sub_activity_level1': sub_activity1,
                'sub_activity_level2': sub_activity2,
                'management_area': management_area,
                'approval_level': approval_level,
            }
            serializer = SaveProposalRegionSerializer(instance,data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = self.get_serializer(instance, context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
        raise serializers.ValidationError(str(e))

    @action(methods=['post'], detail=True)
    @renderer_classes((JSONRenderer,))
    def assessor_save(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            save_assessor_data(instance,request,self)
            return redirect(reverse('external'))
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                http_status = status.HTTP_200_OK
                if request.data.get('application'):
                    application_type = ApplicationType.objects.get(id=request.data.get('application'))

                # When there is a parameter named 'application_type_str', we may need to update application_type
                application_type_str = request.data.get('application_type_str', None)
                #if application_type_str == 'disturbance':
                #    application_type = ApplicationType.objects.get(name=ApplicationType.DISTURBANCE)
                #if application_type_str == 'powerline_maintenance':
                #    application_type = ApplicationType.objects.get(name=ApplicationType.POWERLINE_MAINTENANCE)

                #region = request.data.get('region') if request.data.get('region') else 1
                region = request.data.get('region')
                district = request.data.get('district')
                activity = request.data.get('activity')
                sub_activity1 = request.data.get('sub_activity1')
                sub_activity2 = request.data.get('sub_activity2')
                category = request.data.get('category')
                approval_level = request.data.get('approval_level')

                # Get most recent versions of the Proposal Types
                qs_proposal_type = ProposalType.objects.all().order_by('name', '-version').distinct('name')
                proposal_type = qs_proposal_type.get(name=application_type.name)
                applicant = None
                proxy_applicant = None
                if request.data.get('behalf_of') == 'individual':
                    # Validate User for Individual applications
                    request_user = EmailUser.objects.get(id=request.user.id)
                    if not request_user.residential_address:
                        raise ValidationError('null_applicant_address')
                    # Assign request.user as applicant
                    proxy_applicant = request.user.id
                else:
                    applicant = request.data.get('behalf_of')

                data = {
                    #'schema': qs_proposal_type.order_by('-version').first().schema,
                    'schema': proposal_type.schema,
                    'submitter': request.user.id,
                    'applicant': applicant,
                    'proxy_applicant': proxy_applicant,
                    'application_type': application_type.id,
                    'region': region,
                    'district': district,
                    'activity': activity,
                    'approval_level': approval_level,
                    'sub_activity_level1':sub_activity1,
                    'sub_activity_level2':sub_activity2,
                    'management_area':category,
                    'data': [
                    ],
                }
                serializer = SaveProposalSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                proposal_obj = serializer.save()

                # TODO any APIARY specific settings go here - eg renewal, amendment

                # if proposal_obj.apiary_group_application_type:
                #     proposal_obj.activity = proposal_obj.application_type.name
                #     proposal_obj.save()
                # details_data = {
                #     'proposal_id': proposal_obj.id
                # }
                # if application_type.name == ApplicationType.APIARY:
                #     serializer = SaveProposalApiarySerializer(data=details_data)
                #     serializer.is_valid(raise_exception=True)
                #     proposal_apiary = serializer.save()
                #     for question in ApiaryChecklistQuestion.objects.filter(
                #             checklist_type='apiary',
                #             checklist_role='applicant'
                #             ):
                #         new_answer = ApiaryChecklistAnswer.objects.create(proposal = proposal_apiary,
                #                                                                    question = question)
                #     # Find relevant approval
                #     approval = proposal_apiary.retrieve_approval
                #     if approval:
                #         # Copy requirements from approval.current_proposal
                #         #req = approval.current_proposal.apiary_requirements(approval).exclude(is_deleted=True)
                #         req = approval.proposalrequirement_set.exclude(is_deleted=True)
                #         from copy import deepcopy
                #         if req:
                #             for r in req:
                #                 old_r = deepcopy(r)
                #                 r.proposal = proposal_apiary.proposal
                #                 r.apiary_approval = None
                #                 r.copied_from=old_r
                #                 r.id = None
                #                 r.save()
                #         # Set previous_application to maintain proposal history
                #         proposal_apiary.proposal.previous_application = approval.current_proposal
                #         proposal_apiary.proposal.save()
                #         #proposal_apiary.proposal.proposal_type = 'amendment'
                #         #proposal_apiary.proposal.save()

                # elif application_type.name == ApplicationType.SITE_TRANSFER:
                #     approval_id = request.data.get('originating_approval_id')
                #     approval = Approval.objects.get(id=approval_id)
                #     details_data['originating_approval_id'] = approval_id
                #     serializer = CreateProposalApiarySiteTransferSerializer(data=details_data)
                #     serializer.is_valid(raise_exception=True)
                #     proposal_apiary = serializer.save()
                #     # Set proposal applicant
                #     if approval.applicant:
                #         proposal_obj.applicant = approval.applicant
                #     else:
                #         proposal_obj.proxy_applicant = approval.proxy_applicant
                #     proposal_obj.save()
                #     # Set up checklist questions
                #     for question in ApiaryChecklistQuestion.objects.filter(
                #             checklist_type='site_transfer',
                #             checklist_role='applicant'
                #             ):
                #         new_answer = ApiaryChecklistAnswer.objects.create(proposal=proposal_apiary, question=question)
                #     # Save approval apiary sites to site transfer proposal
                #     # for apiary_site in approval.apiary_sites.all():
                #     for relation in approval.get_relations():
                #         SiteTransferApiarySite.objects.create(proposal_apiary=proposal_apiary, apiary_site_on_approval=relation)

                # elif application_type.name == ApplicationType.TEMPORARY_USE:
                #     approval_id = request.data.get('approval_id')
                #     approval = Approval.objects.get(id=approval_id)

                #     details_data['loaning_approval_id'] = approval_id
                #     serializer = ProposalApiaryTemporaryUseSerializer(data=details_data)
                #     serializer.is_valid(raise_exception=True)
                #     new_temp_use = serializer.save()

                #     # Save TemporaryUseApiarySite
                #     for relation in approval.get_relations():
                #         data_to_save = {
                #             'proposal_apiary_temporary_use_id': new_temp_use.id,
                #             'apiary_site_on_approval_id': relation.id,
                #         }
                #         serializer = TemporaryUseApiarySiteSerializer(data=data_to_save)
                #         serializer.is_valid(raise_exception=True)
                #         serializer.save()

                # #elif application_type.name == ApplicationType.SITE_TRANSFER:
                # #    serializer = ProposalApiarySiteTransferSerializer(data=details_data)
                # #    serializer.is_valid(raise_exception=True)
                # #    serializer.save()
                # else:
                #     pass

                serializer = SaveProposalSerializer(proposal_obj)
                return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    # def retrieve(self, request, *args, **kwargs):
    #     pass

    def update(self, request, *args, **kwargs):
        """
        This function might not be used anymore
        The function 'draft()' is used rather than this update()
        """
        try:
            http_status = status.HTTP_200_OK
            application_type = ApplicationType.objects.get(id=request.data.get('application'))

            # When there is a parameter named 'application_type_str', we may need to update application_type
            application_type_str = request.data.get('application_type_str', None)

            instance = self.get_object()
            serializer = SaveProposalSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def destroy(self, request, *args, **kwargs):
        try:
            http_status = status.HTTP_200_OK
            instance = self.get_object()
            serializer = SaveProposalSerializer(instance, {
                'processing_status': Proposal.PROCESSING_STATUS_DISCARDED,
                'previous_application': None
            }, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            if hasattr(instance, 'proposal_apiary') and instance.proposal_apiary and instance.proposal_apiary.apiary_sites.count():
                for apiary_site in instance.proposal_apiary.apiary_sites.all():
                    if apiary_site.can_be_deleted_from_the_system:
                        # Apiary sites can be actually deleted from the system
                        apiary_site.delete()
                    else:
                        # This apiary site was submitted at least once
                        # Therefore we have to keep the record of this apiary site
                        apiary_site.latest_proposal_link.site_status = SITE_STATUS_DISCARDED
                        apiary_site.latest_proposal_link.save()
            return Response(serializer.data,status=http_status)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class ReferralViewSet(viewsets.ModelViewSet):
    #queryset = Referral.objects.all()
    queryset = Referral.objects.none()
    serializer_class = ReferralSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and is_internal(self.request):
            #queryset =  Referral.objects.filter(referral=user)
            queryset =  Referral.objects.all()
            return queryset
        return Referral.objects.none()

    def get_serializer_class(self):
        try:
            #referral_id = self.kwargs.get('referral_id')
            #if referral_id:
             #   referral = Referral.objects.get(id=referral_id)
            referral = self.get_object()
            apiary_referral_attribute_exists = getattr(referral, 'apiary_referral', None)
            if apiary_referral_attribute_exists:
                return FullApiaryReferralSerializer
            else:
                return ReferralSerializer
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=False)
    def filter_list(self, request, *args, **kwargs):
        """ Used by the external dashboard filters """
        template_group = get_template_group(request)
        region_qs = []
        application_type_qs = []
        activity_qs = []
        if template_group == 'das':
            qs =  self.get_queryset().filter(referral=request.user)
            region_qs =  qs.filter(proposal__region__isnull=False).values_list('proposal__region__name', flat=True).distinct()
            #district_qs =  qs.filter(proposal__district__isnull=False).values_list('proposal__district__name', flat=True).distinct()
            activity_qs =  qs.filter(proposal__activity__isnull=False).order_by('proposal__activity').distinct('proposal__activity').values_list('proposal__activity', flat=True).distinct()
            submitter_qs = qs.filter(proposal__submitter__isnull=False).order_by('proposal__submitter').distinct('proposal__submitter').values_list(
                    'proposal__submitter__first_name','proposal__submitter__last_name','proposal__submitter__email')

        #submitter_qs = qs.filter(proposal__submitter__isnull=False).order_by('proposal__submitter').distinct('proposal__submitter').values_list('proposal__submitter__first_name','proposal__submitter__last_name','proposal__submitter__email')
        submitters = [dict(email=i[2], search_term='{} {} ({})'.format(i[0], i[1], i[2])) for i in submitter_qs]
        processing_status_qs =  qs.filter(proposal__processing_status__isnull=False).order_by('proposal__processing_status').distinct('proposal__processing_status').values_list('proposal__processing_status', flat=True)
        processing_status = [dict(value=i, name='{}'.format(' '.join(i.split('_')).capitalize())) for i in processing_status_qs]
        data = dict(
            regions=region_qs,
            #districts=district_qs,
            application_types=application_type_qs,
            activities=activity_qs,
            submitters=submitters,
            processing_status_choices=processing_status,
        )
        return Response(data)

    @action(methods=['GET',], detail=True)
    def referral_wrapper(self, request, *args, **kwargs):
        instance = self.get_object()
        #instance.internal_view_log(request)
        #serializer = InternalProposalSerializer(instance,context={'request':request})
        serializer_class = ReferralWrapperSerializer #self.internal_serializer_class()
        #serializer = serializer_class(instance,context={'request':request})
        serializer = serializer_class(instance)
        return Response(serializer.data)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request':request})
        #serializer = self.get_serializer_class(request)
        return Response(serializer.data)

    @action(methods=['GET',], detail=False)
    def user_list(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(referral=request.user)
        serializer = DTReferralSerializer(qs, many=True)
        #serializer = DTReferralSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(methods=['GET',], detail=False)
    def datatable_list(self, request, *args, **kwargs):
        proposal = request.GET.get('proposal',None)
        qs = self.get_queryset().all()
        if proposal:
            qs = qs.filter(proposal_id=int(proposal))
        serializer = DTReferralSerializer(qs, many=True)
        return Response(serializer.data)

    @action(methods=['GET',], detail=True)
    def referral_list(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = self.get_queryset().all()
        qs=qs.filter(sent_by=instance.referral, proposal=instance.proposal)
        serializer = DTReferralSerializer(qs, many=True)
        #serializer = ProposalReferralSerializer(qs, many=True)

        return Response(serializer.data)

    @action(methods=['GET', 'POST'], detail=True)
    def complete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            referral_comment = request.data.get('referral_comment')
            instance.complete(request, referral_comment)
            serializer = self.get_serializer(instance, context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def remind(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.remind(request)
            serializer = InternalProposalSerializer(instance.proposal,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def recall(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.recall(request)
            serializer = InternalProposalSerializer(instance.proposal,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def resend(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.resend(request)
            serializer = InternalProposalSerializer(instance.proposal,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['post'], detail=True)
    def send_referral(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = SendReferralSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.send_referral(request,serializer.validated_data['email'],serializer.validated_data['text'])
            serializer = self.get_serializer(instance, context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))



class ProposalRequirementViewSet(viewsets.ModelViewSet):
    #queryset = ProposalRequirement.objects.all()
    queryset = ProposalRequirement.objects.none()
    serializer_class = ProposalRequirementSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return ProposalRequirement.objects.exclude(is_deleted=True)
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.disturbance_organisations.all()]
            qs = ProposalRequirement.objects.exclude(is_deleted=True).filter(Q(proposal_id__applicant_id__in=user_orgs)|Q(proposal_id__submitter_id=user.id))
            return qs
        return ProposalRequirement.objects.none()

    @action(methods=['GET',], detail=True)
    def move_up(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.up()
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def move_down(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.down()
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def discard(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class ProposalStandardRequirementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProposalStandardRequirement.objects.none()
    serializer_class = ProposalStandardRequirementSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return ProposalStandardRequirement.objects.all()
        return ProposalStandardRequirement.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(text__icontains=search)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET',], detail=False)
    def disturbance_standard_requirements(self, request, *args, **kwargs):
        # Only Disturbance standard requirements
        queryset = self.get_queryset().filter(system='disturbance')
        #queryset = self.get_queryset()
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(text__icontains=search)
        # Only Disturbance standard requirements
        queryset = queryset.filter(system='disturbance')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET',], detail=False)
    def apiary_standard_requirements(self, request, *args, **kwargs):
        # Only Apiary standard requirements
        queryset = self.get_queryset().filter(system='apiary')
        #queryset = self.get_queryset()
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(text__icontains=search)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AmendmentRequestViewSet(viewsets.ModelViewSet):
    queryset = AmendmentRequest.objects.none()
    serializer_class = AmendmentRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return AmendmentRequest.objects.all()
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.disturbance_organisations.all()]
            qs = AmendmentRequest.objects.filter(Q(proposal_id__applicant_id__in=user_orgs)|Q(proposal_id__submitter_id=user.id))
            return qs
        return AmendmentRequest.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            # reason_id=request.data.get('reason')
            # data = {
            #     #'schema': qs_proposal_type.order_by('-version').first().schema,
            #     'text': request.data.get('text'),
            #     'proposal': request.data.get('proposal'),
            #     'reason': AmendmentReason.objects.get(id=reason_id) if reason_id else None,
            # }
            #serializer = self.get_serializer(data= request.data)
            serializer = self.get_serializer(data= json.loads(request.data.get('data')))
            #serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception = True)
            instance = serializer.save()
            instance.add_documents(request)
            instance.generate_amendment(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST',], detail=True)
    @renderer_classes((JSONRenderer,))
    def delete_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            AmendmentRequestDocument.objects.get(id=request.data.get('id')).delete()
            return Response([dict(id=i.id, name=i.name,_file=i._file.url) for i in instance.requirement_documents.all()])
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class AmendmentRequestReasonChoicesView(views.APIView):

    renderer_classes = [JSONRenderer,]
    def get(self,request, format=None):
        choices_list = []
        #choices = AmendmentRequest.REASON_CHOICES
        choices=AmendmentReason.objects.all()
        if choices:
            for c in choices:
                #choices_list.append({'key': c[0],'value': c[1]})
                choices_list.append({'key': c.id,'value': c.reason})
        return Response(choices_list)


class SearchKeywordsView(views.APIView):
    renderer_classes = [JSONRenderer,]
    def post(self,request, format=None):
        qs = []
        searchWords = request.data.get('searchKeywords')
        searchProposal = request.data.get('searchProposal')
        searchApproval = request.data.get('searchApproval')
        searchCompliance = request.data.get('searchCompliance')
        if searchWords:
            qs= searchKeyWords(searchWords, searchProposal, searchApproval, searchCompliance)
        #queryset = list(set(qs))
        serializer = SearchKeywordSerializer(qs, many=True)
        return Response(serializer.data)


class SearchReferenceView(views.APIView):
    renderer_classes = [JSONRenderer,]
    def post(self,request, format=None):
        try:
            qs = []
            reference_number = request.data.get('reference_number')
            if reference_number:
                qs= search_reference(reference_number)
            #queryset = list(set(qs))
            serializer = SearchReferenceSerializer(qs)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class ProposalTypeSectionViewSet(viewsets.ReadOnlyModelViewSet):
    latest_proposal_types=[p.id for p in ProposalType.objects.all() if p.latest ]
    queryset = ProposalTypeSection.objects.filter(proposal_type_id__in=latest_proposal_types).order_by('id')
    #queryset = ProposalTypeSection.objects.all().order_by('id')
    serializer_class = ProposalTypeSectionSerializer

class SearchProposalTypeViewSet(viewsets.ReadOnlyModelViewSet):
    #Only select Proposal Types which has Sections linked to them
    proposal_type_ids= ProposalTypeSection.objects.all().values_list('proposal_type_id', flat=True).distinct()
    queryset = ProposalType.objects.filter(id__in=proposal_type_ids)
    serializer_class = SearchProposalTypeSerializer

class SearchSectionsView(views.APIView):
    renderer_classes = [JSONRenderer,]
    def post(self,request, format=None):
        qs = []
        proposal_type_id= request.data.get('proposal_type_id')
        region= request.data.get('region')
        district= request.data.get('district')
        activity= request.data.get('activity')
        section_label= request.data.get('section_label')
        question_id= request.data.get('question_id')
        option_label= request.data.get('option_label')
        is_internal= request.data.get('is_internal')
        qs= search_sections(proposal_type_id, section_label,question_id,option_label,is_internal, region,district,activity)
        #queryset = list(set(qs))
        serializer = SearchKeywordSerializer(qs, many=True)
        return Response(serializer.data)

class GetSearchGeoJsonView(views.APIView):
    renderer_classes = [JSONRenderer,]
    def post(self,request, format=None):
        proposal_lodgement_numbers= request.data.get('proposal_lodgement_numbers')
        
        search_geojson= get_search_geojson(proposal_lodgement_numbers, request)
        #queryset = list(set(qs))
        serializer = SearchGeoJsonSerializer({'search_geojson':search_geojson})
        return Response(serializer.data)

#Schema api's
class SchemaMasterlistFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """
    def filter_queryset(self, request, queryset, view):
        # Get built-in DRF datatables queryset first to join with search text,
        # then apply additional filters.
        # super_queryset = super(
        #     SchemaMasterlistFilterBackend, self
        # ).filter_queryset(request, queryset, view).distinct()

        search_text = request.GET.get('search[value]')

        if queryset.model is MasterlistQuestion:

            if search_text:
                search_text = search_text.lower()
                search_text_masterlist_ids = MasterlistQuestion.objects.values(
                    'id'
                ).filter(question__icontains=search_text)

                queryset = queryset.filter(
                    id__in=search_text_masterlist_ids
                ).distinct()

        total_count = queryset.count()
        # override queryset ordering, required because the ordering is usually
        # handled in the super call, but is then clobbered by the custom
        # queryset joining above also needed to disable ordering for all fields
        # for which data is not an Application model field, as property
        # functions will not work with order_by.
        getter = request.query_params.get
        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        total_count = queryset.count()

        setattr(view, '_datatables_total_count', total_count)
        return queryset


class SchemaMasterlistPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (SchemaMasterlistFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    #renderer_classes = (JSONRenderer,BrowsableAPIRenderer,SchemaMasterlistRenderer,) #if we need the custom renderer classes we should set it like this
    #renderer_classes = (SchemaMasterlistRenderer,)
    queryset = MasterlistQuestion.objects.none()
    serializer_class = DTSchemaMasterlistSerializer
    page_size = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return MasterlistQuestion.objects.all()
        return MasterlistQuestion.objects.none()

    @action(methods=['GET', ], detail=False)
    def schema_masterlist_datatable_list(self, request, *args, **kwargs):
        self.serializer_class = DTSchemaMasterlistSerializer
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTSchemaMasterlistSerializer(
            result_page, context={'request': request}, many=True
        )
        response = self.paginator.get_paginated_response(serializer.data)

        return response


class SchemaMasterlistViewSet(viewsets.ModelViewSet):
    queryset = MasterlistQuestion.objects.none()
    serializer_class = SchemaMasterlistSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return MasterlistQuestion.objects.all()
        return MasterlistQuestion.objects.none()

    @action(methods=['GET', ], detail=True)
    def get_masterlist_selects(self, request, *args, **kwargs):
        '''
        Get independant Select lists associated with Schema Masterlist.
        '''
        try:

            excl_choices = [
                # None
            ]

            answer_types = [
                {
                    'value': a[0], 'label': a[1]
                } for a in MasterlistQuestion.ANSWER_TYPE_CHOICES
                if a[0] not in excl_choices
            ]

            return Response(
                {
                    'all_answer_types': answer_types,
                },
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('get_masterlist_selects()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

    @action(methods=['GET', ], detail=True)
    def get_masterlist_options(self, request, *args, **kwargs):
        '''
        Get associated QuestionOption for Schema Masterlist type.
        '''
        try:

            masterlist_id = request.query_params.get('masterlist_id', 0)
            masterlist = MasterlistQuestion.objects.filter(
                licence_purpose_id=int(masterlist_id)
            )[0]

            option_list = masterlist.get_property_cache_options()
            options = [
                {'label': o.label, 'value': ''} for o in option_list
            ]

            return Response(
                {'masterlist_options': options},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('get_masterlist_selects()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

    @action(methods=['DELETE', ], detail=True)
    def delete_masterlist(self, request, *args, **kwargs):
        '''
        Delete Masterlist record.
        '''
        try:
            instance = self.get_object()

            with transaction.atomic():

                instance.delete()

            return Response(
                {'masterlist_id': instance.id},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('save_masterlist()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

    @action(methods=['POST', ], detail=True)
    def save_masterlist(self, request, *args, **kwargs):
        '''
        Save Masterlist record.
        '''
        try:
            instance = self.get_object()

            with transaction.atomic():

                options = request.data.get('options', None)
                instance.set_property_cache_options(options)

                headers = request.data.get('headers', None)
                instance.set_property_cache_headers(headers)

                expanders = request.data.get('expanders', None)
                instance.set_property_cache_expanders(expanders)

                serializer = SchemaMasterlistSerializer(
                    instance, data=request.data
                )
                serializer.get_options(instance)
                serializer.is_valid(raise_exception=True)
                serializer.save()

            return Response(
                {'masterlist_id': instance.id},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('save_masterlist()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

class SchemaQuestionFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """
    def filter_queryset(self, request, queryset, view):
        # Get built-in DRF datatables queryset first to join with search text,
        # then apply additional filters.
        # super_queryset = super(
        #     SchemaQuestionFilterBackend, self
        # ).filter_queryset(request, queryset, view).distinct()

        search_text = request.GET.get('search[value]')
        proposal_type = request.GET.get('proposal_type_id')
        section = request.GET.get('section_id')
        group = request.GET.get('group_id')

        if queryset.model is SectionQuestion:

            if search_text:
                search_text = search_text.lower()
                search_text_question_ids = SectionQuestion.objects.values(
                    'id'
                ).filter(
                    question__question__icontains=search_text
                )

                queryset = queryset.filter(
                    id__in=search_text_question_ids
                ).distinct()

            proposal_type = proposal_type.lower() if proposal_type else 'all'
            if proposal_type != 'all':
                proposal_type_ids = SectionQuestion.objects.values(
                    'id'
                ).filter(
                    section__proposal_type_id=int(proposal_type)
                )
                queryset = queryset.filter(id__in=proposal_type_ids)

            section = section.lower() if section else 'all'
            if section != 'all':
                section_ids = SectionQuestion.objects.values(
                    'id'
                ).filter(
                    section_id=int(section)
                )
                queryset = queryset.filter(id__in=section_ids)

            group = group.lower() if group else 'all'
            if group != 'all':
                group_ids = SectionQuestion.objects.values(
                    'id'
                ).filter(
                    section_group_id=int(group)
                )
                queryset = queryset.filter(id__in=group_ids)

        total_count = queryset.count()
        # override queryset ordering, required because the ordering is usually
        # handled in the super call, but is then clobbered by the custom
        # queryset joining above also needed to disable ordering for all fields
        # for which data is not an Application model field, as property
        # functions will not work with order_by.
        getter = request.query_params.get
        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        total_count = queryset.count()

        setattr(view, '_datatables_total_count', total_count)
        return queryset


class SchemaQuestionPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (SchemaQuestionFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    #renderer_classes = (SchemaQuestionRenderer,)
    queryset = SectionQuestion.objects.none()
    serializer_class = DTSchemaQuestionSerializer
    page_size = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return SectionQuestion.objects.all()
        return SectionQuestion.objects.none()

    @action(methods=['GET', ], detail=False)
    def schema_question_datatable_list(self, request, *args, **kwargs):
        self.serializer_class = DTSchemaQuestionSerializer
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        # self.paginator.page_size = 0
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTSchemaQuestionSerializer(
            result_page, context={'request': request}, many=True
        )
        response = self.paginator.get_paginated_response(serializer.data)

        return response


class SchemaQuestionViewSet(viewsets.ModelViewSet):
    queryset = SectionQuestion.objects.none()
    serializer_class = SchemaQuestionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return SectionQuestion.objects.all()
        return SectionQuestion.objects.none()

    @action(methods=['GET', ], detail=True)
    def get_question_parents(self, request, *args, **kwargs):
        '''
        Get all Parent Question associated with Schema Questions in Section.
        '''
        try:
            section_id = request.query_params.get('section_id', 0)
            # opt_list = MasterlistQuestion.ANSWER_TYPE_OPTIONS
            opt_list = MasterlistQuestion.ANSWER_TYPE_OPTIONS_NEW
            all_questions = SectionQuestion.objects.filter(
                section_id=int(section_id),
            )
            questions = [
                q for q in all_questions if q.question.answer_type in opt_list
            ]

            parents = [
                {
                    'label': q.question.question,
                    'value': q.question.id,
                    #'group': q.section_group_id,
                } for q in questions
            ]

            # section_groups = SectionGroup.objects.filter(
            #     section_id=int(section_id)
            # )

            # groups = [
            #     {
            #         'label': g.group_label, 'value': g.id
            #     } for g in section_groups
            # ]

            return Response(
                {
                    'question_parents': parents,
                    #'question_groups': groups,
                },
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('get_question_parents()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

    @action(methods=['GET', ], detail=True)
    def get_question_sections(self, request, *args, **kwargs):
        '''
        Get all Sections associated with Schema Questions with Licence Purpose.
        '''
        try:
            proposal_type_id = request.query_params.get('proposal_type_id', 0)
            sections = ProposalTypeSection.objects.filter(
                proposal_type_id=int(proposal_type_id)
            )
            names = [
                {
                    'label': s.section_label, 'value': s.id
                } for s in sections
            ]

            # section_groups = SectionGroup.objects.filter(
            #     section__licence_purpose=int(purpose_id)
            # )

            # groups = [
            #     {
            #         'label': g.group_label, 'value': g.id
            #     } for g in section_groups
            # ]

            return Response(
                {
                    'question_sections': names,
                    #'question_groups': groups,
                },
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('get_question_sections()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

    @action(methods=['GET', ], detail=True)
    def get_question_order(self, request, *args, **kwargs):
        '''
        Get order number for Schema Question using Schema Group.
        '''
        try:
            group_id = request.query_params.get('group_id', 0)
            questions = SectionQuestion.objects.filter(
                section_group=int(group_id)
            )
            next_order = len(questions) + 1 if questions else 0

            return Response(
                {'question_order': str(next_order)},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('get_question_order()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

    @action(methods=['GET', ], detail=True)
    def get_question_selects(self, request, *args, **kwargs):
        '''
        Get independant Select lists associated with Schema Questions.
        '''
        try:

            qs = MasterlistQuestion.objects.all()
            #masterlist = SelectSchemaMasterlistSerializer(qs, many=True).data
            masterlist = SchemaMasterlistSerializer(qs, many=True).data

            qs = ProposalType.objects.filter().exclude(sections=None)
            proposal_types = [
                {
                    'label': p.name_with_version,
                    'value': p.id
                } for p in qs
            ]

            qs = ProposalTypeSection.objects.all()
            sections = [
                {
                    'label': s.section_label, 'value': s.id
                } for s in qs
            ]

            # qs = SectionGroup.objects.all()
            # groups = [
            #     {
            #         'label': s.group_label, 'value': s.id
            #     } for s in qs
            # ]

            return Response(
                {
                    'all_masterlist': masterlist,
                    'all_proposal_types': proposal_types,
                    'all_section': sections,
                    #'all_group': groups,
                },
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('get_question_selects()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

    @action(methods=['DELETE', ], detail=True)
    def delete_question(self, request, *args, **kwargs):
        '''
        Delete Section Question record.
        '''
        try:
            instance = self.get_object()

            with transaction.atomic():

                instance.delete()

            return Response(
                {'masterlist_id': instance.id},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('delete_question()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

    @action(methods=['POST', ], detail=True)
    def save_question(self, request, *args, **kwargs):
        '''
        Save Section Question record.
        '''
        try:
            instance = self.get_object()

            with transaction.atomic():

                # process options.
                options = request.data.get('options', None)
                instance.set_property_cache_options(options)

                serializer = SchemaQuestionSerializer(
                    instance, data=request.data
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

            return Response(
                {'question_id': instance.id},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('save_question()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

class SchemaProposalTypeFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """
    def filter_queryset(self, request, queryset, view):
        # Get built-in DRF datatables queryset first to join with search text,
        # then apply additional filters.
        search_text = request.GET.get('search[value]')
        proposal_type = request.GET.get('proposal_type_id')

        if queryset.model is ProposalTypeSection:

            if search_text:
                search_text = search_text.lower()
                search_text_proposal_type_ids = ProposalTypeSection.objects.values(
                    'id'
                ).filter(section_label__icontains=search_text)

                queryset = queryset.filter(
                    id__in=search_text_proposal_type_ids
                ).distinct()

            proposal_type = proposal_type.lower() if proposal_type else 'all'
            if proposal_type != 'all':
                proposal_type_ids = ProposalTypeSection.objects.values(
                    'id'
                ).filter(
                    proposal_type_id=int(proposal_type)
                )
                queryset = queryset.filter(id__in=proposal_type_ids)

        total_count = queryset.count()
        # override queryset ordering, required because the ordering is usually
        # handled in the super call, but is then clobbered by the custom
        # queryset joining above also needed to disable ordering for all fields
        # for which data is not an Application model field, as property
        # functions will not work with order_by.
        getter = request.query_params.get
        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        total_count = queryset.count()

        setattr(view, '_datatables_total_count', total_count)
        return queryset


#class SchemaProposalTypeRenderer(DatatablesRenderer):
#    def render(self, data, accepted_media_type=None, renderer_context=None):
#        if 'view' in renderer_context and \
#                hasattr(renderer_context['view'], '_datatables_total_count'):
#            data['recordsTotal'] = \
#                renderer_context['view']._datatables_total_count
#        return super(SchemaProposalTypeRenderer, self).render(
#            data, accepted_media_type, renderer_context)


class SchemaProposalTypePaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (SchemaProposalTypeFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    #renderer_classes = (SchemaProposalTypeRenderer,)
    queryset = ProposalTypeSection.objects.none()
    serializer_class = DTSchemaProposalTypeSerializer
    page_size = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return ProposalTypeSection.objects.all()
        return ProposalTypeSection.objects.none()

    @action(methods=['GET', ], detail=False)
    def schema_proposal_type_datatable_list(self, request, *args, **kwargs):
        self.serializer_class = DTSchemaProposalTypeSerializer
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        # self.paginator.page_size = 0
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTSchemaProposalTypeSerializer(
            result_page, context={'request': request}, many=True
        )
        response = self.paginator.get_paginated_response(serializer.data)

        return response


class SchemaProposalTypeViewSet(viewsets.ModelViewSet):
    queryset = ProposalTypeSection.objects.none()
    serializer_class = SchemaProposalTypeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return ProposalTypeSection.objects.all()
        return ProposalTypeSection.objects.none()

    @action(methods=['GET', ], detail=True)
    def get_proposal_type_selects(self, request, *args, **kwargs):
        '''
        Get independant Select lists associated with Schema Section ProposalType.
        '''
        try:

            sections = ProposalType.objects.all()
            proposal_types = [
                {
                    'label': s.name_with_version,
                    'value': s.id,
                } for s in sections
            ]

            return Response(
                {'all_proposal_type': proposal_types},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('get_proposal_type_selects()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

    @action(methods=['GET', ], detail=True)
    def get_proposal_type_sections(self, request, *args, **kwargs):
        '''
        Get all Schema Sections associated with Licence ProposalType.
        '''
        try:
            proposal_type_id = request.query_params.get('proposal_type_id', 0)
            sections = ProposalTypeSection.objects.filter(
                proposal_type_id=int(proposal_type_id)
            )
            names = [
                {
                    'label': s.section_label, 'value': s.id
                } for s in sections
            ]

            return Response(
                {'proposal_type_sections': names},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('get_proposal_type_sections()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

    @action(methods=['DELETE', ], detail=True)
    def delete_proposal_type(self, request, *args, **kwargs):
        '''
        Delete Licence ProposalType Section record.
        '''
        try:
            instance = self.get_object()

            with transaction.atomic():

                instance.delete()

            return Response(
                {'proposal_type_id': instance.id},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('delete_proposal_type()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))

    @action(methods=['POST', ], detail=True)
    def save_proposal_type(self, request, *args, **kwargs):
        '''
        Save Licence ProposalType Section record.
        '''
        try:
            instance = self.get_object()

            with transaction.atomic():

                serializer = SchemaProposalTypeSerializer(
                    instance, data=request.data
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

            return Response(serializer.data)

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('save_proposal_type()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception(e)
            raise serializers.ValidationError(str(e))


class DASMapFilterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = DASMapFilterSerializer
    permission_classes = []

    def get_queryset(self):
        user = self.request.user
        apiary_proposal_types=['Apiary','Site Transfer','Temporary Use']
        if is_internal(self.request):
            return Proposal.objects.filter(
                Q(region__isnull=False) | 
                Q(application_type__name__in=apiary_proposal_types)).exclude(shapefile_json__isnull=True)
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.disturbance_organisations.all()]
            queryset = Proposal.objects.filter(region__isnull=False).filter(
                Q(applicant_id__in=user_orgs) |
                Q(submitter=user)
            ).exclude(processing_status='')
            queryset= queryset.exclude(shapefile_json__isnull=True)
            return queryset

        logger.warning("User is neither customer nor internal user: {} <{}>".format(user.get_full_name(), user.email))
        return Proposal.objects.none()


    def list(self, request, *args, **kwargs):
        #Turning off the caching for now. Can be added if dashboard performance is poor.
        # cache_key = settings.CACHE_KEY_MAP_PROPOSALS
        # queryset = cache.get(cache_key)
        # if queryset is None:
        #     queryset = self.get_queryset()
        #     cache.set(cache_key, queryset, settings.CACHE_TIMEOUT_2_HOURS)
        # logger.debug(f"{cache_key}:{queryset}")
        queryset = self.get_queryset()
        search_text = request.GET.get('search[value]', '')
        total_count = queryset.count()
        def get_choice(status, choices=Proposal.PROCESSING_STATUS_CHOICES):
            for i in choices:
                if i[1]==status:
                    return i[0]
            return None

        # on the internal dashboard, the Region filter is multi-select - have to use the custom filter below
        regions = request.GET.get('regions')
        if regions:
            if queryset.model is Proposal:
                queryset = queryset.filter(region__name__iregex=regions.replace(',', '|'))
            elif queryset.model is Referral or queryset.model is Compliance:
                queryset = queryset.filter(proposal__region__name__iregex=regions.replace(',', '|'))
            #elif queryset.model is Approval:
            #    queryset = queryset.filter(region__iregex=regions.replace(',', '|'))

        
        application_type = request.GET.get('application_type')
        if application_type and not application_type.lower() =='all':
            if queryset.model is Referral or queryset.model is Compliance:
                queryset = queryset.filter(proposal__application_type__name=application_type)
            else:
                queryset = queryset.filter(application_type__name=application_type)
        proposal_activity = request.GET.get('proposal_activity')
        if proposal_activity and not proposal_activity.lower() == 'all':
            if queryset.model is Referral or queryset.model is Compliance:
                queryset = queryset.filter(proposal__activity=proposal_activity)
            else:
                queryset = queryset.filter(activity=proposal_activity)
        proposal_status = request.GET.get('proposal_status')
        if proposal_status and not proposal_status.lower() == 'all':
            #processing_status = get_choice(proposal_status, Proposal.PROCESSING_STATUS_CHOICES)
            #queryset = queryset.filter(processing_status=processing_status)
            if queryset.model is Referral or queryset.model is Compliance:
                queryset = queryset.filter(proposal__processing_status=proposal_status)
            else:
                queryset = queryset.filter(processing_status=proposal_status)
        
        submitter = request.GET.get('submitter')
        if submitter and not submitter.lower() == 'all':
            if queryset.model is Referral or queryset.model is Compliance:
                queryset = queryset.filter(proposal__submitter__email=submitter)
            else:
                queryset = queryset.filter(submitter__email=submitter)
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        if queryset.model is Proposal:
            if date_from:
                queryset = queryset.filter(lodgement_date__gte=date_from)

            if date_to:
                queryset = queryset.filter(lodgement_date__lte=date_to)
        
        serializer = DASMapFilterSerializer(queryset,context={'request':request}, many=True)
        return Response(serializer.data)

    @action(methods=['GET',], detail=False)
    def filter_list(self, request, *args, **kwargs):
        """ Used by the internal/external dashboard filters """
        template_group = get_template_group(request)
        region_qs = []
        activity_qs = []
        application_type_qs = []
        applicant_qs = []
        apiary_proposal_types=['Apiary','Site Transfer','Temporary Use']
        if template_group == 'das':
            qs = self.get_queryset().exclude(
                application_type__name__in=apiary_proposal_types)
            region_qs =  qs.filter(region__isnull=False).values_list('region_id', 'region__name').distinct()
            submitter_qs = qs.filter(submitter__isnull=False).distinct(
                            'submitter__email').values_list('submitter__first_name','submitter__last_name','submitter__email')
            applicant_qs = qs.filter(applicant__isnull=False).distinct(
                        'applicant_id').values_list('applicant_id','applicant__organisation__name',)

        application_type_qs =  qs.filter(application_type__isnull=False).values_list('application_type__name', flat=True).distinct()
        activity_qs =  qs.filter(activity__isnull=False).values_list('activity', flat=True).distinct()
        submitters = [dict(email=i[2], search_term='{} {} ({})'.format(i[0], i[1], i[2])) for i in submitter_qs]
        applicants = [dict(id=i[0], search_term='{}'.format(i[1])) for i in applicant_qs]
        regions = [dict(id=i[0], search_term='{}'.format(i[1])) for i in region_qs]
        data = dict(
            regions=regions,
            #districts=district_qs,
            activities=activity_qs,
            submitters=submitters,
            applicants=applicants,
            application_types=application_type_qs,
            processing_status_choices = [i[1] for i in Proposal.PROCESSING_STATUS_CHOICES],
            ##processing_status_id_choices = [i[0] for i in Proposal.PROCESSING_STATUS_CHOICES],
            ##customer_status_choices = [i[1] for i in Proposal.CUSTOMER_STATUS_CHOICES],
            approval_status_choices = [i[1] for i in Approval.STATUS_CHOICES],
        )
        return Response(data)
