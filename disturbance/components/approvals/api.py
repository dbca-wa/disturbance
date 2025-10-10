import traceback
import os
import datetime
import base64
import geojson
from six.moves.urllib.parse import urlparse
from wsgiref.util import FileWrapper
from django.db.models import Q, Min
from django.db import transaction
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import action, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser, Address
from ledger.address.models import Country
from datetime import datetime, timedelta, date
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from disturbance.components.approvals.models import (
    Approval, ApprovalUserAction, ApprovalDocument,
)
from disturbance.components.approvals.serializers import (
    ApprovalSerializer,
    DTApprovalSerializer,
    ApprovalCancellationSerializer,
    ApprovalSuspensionSerializer,
    ApprovalSurrenderSerializer,
    ApprovalUserActionSerializer,
    ApprovalLogEntrySerializer,
    ApprovalWrapperSerializer,
    ApprovalDocumentHistorySerializer,
)
from disturbance.components.main.decorators import basic_exception_handler
from disturbance.components.proposals.models import Proposal
from disturbance.helpers import is_customer, is_internal
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer
from disturbance.components.main.utils import get_template_group, handle_validation_error


class ApprovalFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        def get_choice(status, choices=Approval.STATUS_CHOICES):
            for i in choices:
                if i[1]==status:
                    return i[0]
            return None

        # on the internal dashboard, the Region filter is multi-select - have to use the custom filter below
        region = request.GET.get('region')
        if region and not region.lower() == 'all':
            queryset = queryset.filter(current_proposal__region__name=region)
        proposal_activity = request.GET.get('proposal_activity')
        if proposal_activity and not proposal_activity.lower() == 'all':
            queryset = queryset.filter(current_proposal__activity=proposal_activity)
        approval_status = request.GET.get('approval_status')
        if approval_status and not approval_status.lower() == 'all':
            queryset = queryset.filter(status=get_choice(approval_status))

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
        start_date_from = request.GET.get('start_date_from')
        start_date_to = request.GET.get('start_date_to')
        if start_date_from:
            queryset = queryset.filter(start_date__gte=start_date_from)
        if start_date_to:
            queryset = queryset.filter(start_date__lte=start_date_to)
        
        expiry_date_from = request.GET.get('expiry_date_from')
        expiry_date_to = request.GET.get('expiry_date_to')
        if expiry_date_from:
            queryset = queryset.filter(expiry_date__gte=expiry_date_from)
        if expiry_date_to:
            queryset = queryset.filter(expiry_date__lte=expiry_date_to)

        # getter = request.query_params.get
        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            #for num, item in enumerate(ordering):
             #   if item == 'status__name':
              #      ordering[num] = 'status'
               # elif item == '-status__name':
                #    ordering[num] = '-status'
            queryset = queryset.order_by(*ordering)

        try:
            queryset = super(ApprovalFilterBackend, self).filter_queryset(request, queryset, view)
        except Exception as e:
            print(e)
        setattr(view, '_datatables_total_count', total_count)
        return queryset


#class ApprovalRenderer(DatatablesRenderer):
#    def render(self, data, accepted_media_type=None, renderer_context=None):
#        if 'view' in renderer_context and hasattr(renderer_context['view'], '_datatables_total_count'):
#            data['recordsTotal'] = renderer_context['view']._datatables_total_count
#            #data.pop('recordsTotal')
#            #data.pop('recordsFiltered')
#        return super(ApprovalRenderer, self).render(data, accepted_media_type, renderer_context)


class ApprovalPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ApprovalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    #renderer_classes = (ApprovalRenderer,)
    page_size = 10
    queryset = Approval.objects.none()
    serializer_class = ApprovalSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return Approval.objects.all().exclude(status='hidden')
        elif is_customer(self.request):
            user_orgs = [org.id for org in self.request.user.disturbance_organisations.all()]
            queryset =  Approval.objects.filter(Q(applicant_id__in = user_orgs)|Q(proxy_applicant_id=self.request.user.id)).exclude(status='hidden')
            #queryset =  Approval.objects.filter(applicant_id__in = user_orgs)
            return queryset
        return Approval.objects.none()

    def get_external_queryset(self):
        if is_internal(self.request):
            user_orgs = [org.id for org in self.request.user.disturbance_organisations.all()]
            queryset =  Approval.objects.filter(Q(applicant_id__in = user_orgs)|Q(proxy_applicant_id=self.request.user.id)).exclude(status='hidden')
            return queryset
            #return Approval.objects.all().exclude(status='hidden')
        elif is_customer(self.request):
            user_orgs = [org.id for org in self.request.user.disturbance_organisations.all()]
            queryset =  Approval.objects.filter(Q(applicant_id__in = user_orgs)|Q(proxy_applicant_id=self.request.user.id)).exclude(status='hidden')
            #queryset =  Approval.objects.filter(applicant_id__in = user_orgs)
            return queryset
        return Approval.objects.none()
#    def list(self, request, *args, **kwargs):
#        response = super(ProposalPaginatedViewSet, self).list(request, args, kwargs)
#
#        # Add extra data to response.data
#        #response.data['regions'] = self.get_queryset().filter(region__isnull=False).values_list('region__name', flat=True).distinct()
#        return response

    #@list_route(methods=['GET',])
    #def approvals_external(self, request, *args, **kwargs):
    #    """
    #    Paginated serializer for datatables - used by the internal and external dashboard (filtered by the get_queryset method)

    #    To test:
    #        http://localhost:8000/api/approval_paginated/approvals_external/?format=datatables&draw=1&length=2
    #    """

    #    #qs = self.queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
    #    #qs = ProposalFilterBackend().filter_queryset(self.request, qs, self)

    #    ids = self.get_queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number').values_list('id', flat=True)
    #    qs = Approval.objects.filter(id__in=ids)
    #    qs = self.filter_queryset(qs)

    #    # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
    #    applicant_id = request.GET.get('org_id')
    #    if applicant_id:
    #        qs = qs.filter(applicant_id=applicant_id)

    #    self.paginator.page_size = qs.count()
    #    result_page = self.paginator.paginate_queryset(qs, request)
    #    serializer = ApprovalSerializer(result_page, context={'request':request}, many=True)
    #    return self.paginator.get_paginated_response(serializer.data)

    @action(methods=['GET',], detail=False)
    def approvals_external(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the internal and external dashboard (filtered by the get_queryset method)

        To test:
            http://localhost:8000/api/approval_paginated/approvals_external/?format=datatables&draw=1&length=2
        """

        ids = self.get_queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number').values_list('id', flat=True)
        template_group = get_template_group(request)
        if template_group == 'das':
            # TODO as apiary_approval field is removed from migrations, changed the qurery
            # qs = self.get_queryset().exclude(apiary_approval=True).filter(id__in=ids)
            apiary_proposal_types=['Apiary','Site Transfer','Temporary Use']
            qs = self.get_external_queryset().exclude(current_proposal__application_type__name__in=apiary_proposal_types).filter(id__in=ids)
        qs = self.filter_queryset(qs)

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
        applicant_id = request.GET.get('org_id')
        if applicant_id:
            qs = qs.filter(applicant__id=applicant_id)
        submitter_id = request.GET.get('submitter_id', None)
        if submitter_id:
            qs = qs.filter(submitter_id=submitter_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = DTApprovalSerializer(result_page, context={
            'request':request,
            'template_group': template_group
            }, many=True)
        return self.paginator.get_paginated_response(serializer.data)
    
    @action(methods=['GET',], detail=False)
    def approvals_internal(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the internal and external dashboard (filtered by the get_queryset method)
        To test:
            http://localhost:8000/api/approval_paginated/approvals_external/?format=datatables&draw=1&length=2
        """

        ids = self.get_queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number').values_list('id', flat=True)
        apiary_proposal_types=['Apiary','Site Transfer','Temporary Use']
        template_group = get_template_group(request)
        qs = self.get_queryset().exclude(
                current_proposal__application_type__name__in=apiary_proposal_types
                ).filter(id__in=ids)

        qs = self.filter_queryset(qs)

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
        applicant_id = request.GET.get('org_id')
        if applicant_id:
            qs = qs.filter(applicant__id=applicant_id)
        submitter_id = request.GET.get('submitter_id', None)
        if submitter_id:
            qs = qs.filter(submitter_id=submitter_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = DTApprovalSerializer(result_page, context={
            'request':request,
            'template_group': template_group
            }, many=True)
        return self.paginator.get_paginated_response(serializer.data)


class ApprovalViewSet(viewsets.ModelViewSet):
    #queryset = Approval.objects.all()
    queryset = Approval.objects.none()
    serializer_class = ApprovalSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return Approval.objects.all()
        elif is_customer(self.request):
            user_orgs = [org.id for org in self.request.user.disturbance_organisations.all()]
            #queryset =  Approval.objects.filter(applicant_id__in = user_orgs)
            queryset =  Approval.objects.filter(Q(applicant_id__in = user_orgs)|Q(proxy_applicant_id=self.request.user.id))
            return queryset
        return Approval.objects.none()

    #TODO: review this - seems like a workaround at the moment
    def get_serializer_class(self):
        try:
            approval = self.get_object()
            return ApprovalSerializer
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def list(self, request, *args, **kwargs):
        #queryset = self.get_queryset()
        queryset = self.get_queryset().order_by('-lodgement_number', '-issue_date').distinct('lodgement_number')
        # Filter by org
        org_id = request.GET.get('org_id',None)
        if org_id:
            queryset = queryset.filter(applicant_id=org_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET',], detail=False)
    def filter_list(self, request, *args, **kwargs):
        """ Used by the external dashboard filters """
        region_qs =  self.get_queryset().filter(current_proposal__region__isnull=False).values_list('current_proposal__region__name', flat=True).distinct()
        activity_qs =  self.get_queryset().filter(current_proposal__activity__isnull=False).values_list('current_proposal__activity', flat=True).distinct()
        data = dict(
            regions=region_qs,
            activities=activity_qs,
            approval_status_choices = [i[1] for i in Approval.STATUS_CHOICES],
        )
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        approval = self.get_object()
        serializer = self.get_serializer(approval, context={'request': request})
        return Response(serializer.data)

    @action(methods=['GET',], detail=True)
    def approval_wrapper(self, request, *args, **kwargs):
        instance = self.get_object()
        #instance.internal_view_log(request)
        #serializer = InternalProposalSerializer(instance,context={'request':request})
        serializer_class = ApprovalWrapperSerializer #self.internal_serializer_class()
        #serializer = serializer_class(instance,context={'request':request})
        serializer = serializer_class(instance)
        return Response(serializer.data)

    @action(methods=['POST',], detail=True)
    @basic_exception_handler
    def approval_cancellation(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ApprovalCancellationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.approval_cancellation(request,serializer.validated_data)
        serializer = ApprovalSerializer(instance,context={'request':request})
        return Response(serializer.data)

    @action(methods=['POST',], detail=True)
    def approval_suspension(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ApprovalSuspensionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.approval_suspension(request,serializer.validated_data)
            serializer = ApprovalSerializer(instance,context={'request':request})
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
    def approval_reinstate(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.reinstate_approval(request)
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
    def approval_surrender(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ApprovalSurrenderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.approval_surrender(request,serializer.validated_data)
            serializer = ApprovalSerializer(instance,context={'request':request})
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
    def approval_pdf_view_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.pdf_view_log(request)
            serializer = ApprovalSerializer(instance,context={'request':request})
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
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ApprovalUserActionSerializer(qs,many=True)
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
            serializer = ApprovalLogEntrySerializer(qs,many=True)
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
                request_data['approval'] = u'{}'.format(instance.id)
                request_data['staff'] = u'{}'.format(request.user.id)
                serializer = ApprovalLogEntrySerializer(data=request_data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES.getlist("files"):
                    document = comms.documents.create(
                            name = str(f),
                            _file = f
                            )
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

    @action(methods=['GET',], detail=False)
    def sti_search(self, request, *args, **kwargs):
        """ Used by the internal users to filter for sti name in ptoposal titlei (for use by external systems) """
        name = request.GET.get('name')
        data = Approval.objects.filter(current_proposal__title__icontains=name).values_list('licence_document___file', flat=True)
        return Response(list(data))

    @action(methods=['GET',], detail=False)
    def sti_unmatched(self, request, *args, **kwargs):
        """ Used by the internal users to filter for sti name in ptoposal titlei (for use by external systems) """

        name = request.GET.get('name')
        data = Approval.objects.filter(current_proposal__title__icontains=name).values_list('licence_document___file', flat=True)


        #qs = User.objects.all()
        #for search_term in ['x', 'y', 'z']:
        #    qs = qs.filter(first_name__contains=search_term)

        return Response(list(data))

    @action(methods=['GET',], detail=True)
    def requirements(self, request, *args, **kwargs):
        try:
            approval = self.get_object()
            requirements = []
            #for requirement in approval.current_proposal.requirements.all():
            #    requirements.append(ApiaryProposalRequirementSerializer(requirement).data)
            return Response(requirements)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET', ], detail=False)
    def approval_history(self, request, *args, **kwargs):
        try:
            qs = None
            approval_history_id = request.query_params['approval_history_id']
            return_list = []
            if approval_history_id:
                instance = Approval.objects.get(id=approval_history_id)
                qs=ApprovalDocument.objects.filter(approval__lodgement_number=instance.lodgement_number, name__icontains='approval')
                qs=qs.order_by("-uploaded_date")
                for item in qs:
                    se = ApprovalDocumentHistorySerializer(item)
                    return_list.append(se.data)
            return Response(return_list)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
        

class ApprovalDocumentPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ApprovalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    #renderer_classes = (ApprovalRenderer,)
    page_size = 10
    queryset = ApprovalDocument.objects.none()
    serializer_class = ApprovalDocumentHistorySerializer

    def get_queryset(self):
        
        return ApprovalDocument.objects.all()
    
    @action(methods=['GET',], detail=True)
    def approvals_document_external(self, request, pk=None):
        
        qs = self.get_queryset()
        # allow approval id to be passed either as URL pk or as query param approval_id
        approval_id = pk or request.GET.get('approval_id', None)
        if approval_id:
            try:
                instance = Approval.objects.get(id=approval_id)
                qs = qs.filter(approval__lodgement_number=instance.lodgement_number, name__icontains='approval')
            except Approval.DoesNotExist:
                qs = qs.none()

        qs = qs.order_by("-uploaded_date")

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ApprovalDocumentHistorySerializer(result_page, context={
            'request': request,
        }, many=True)
        return self.paginator.get_paginated_response(serializer.data)
    

