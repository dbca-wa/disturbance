
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
from disturbance.components.compliances.models import (
   Compliance,
   ComplianceAmendmentRequest,
   ComplianceAmendmentReason
)
#from disturbance.components.proposals.models import (
 #       Proposal
  #      )
from disturbance.components.compliances.serializers import (
    DTComplianceSerializer,
    ComplianceSerializer,
    SaveComplianceSerializer,
    ComplianceActionSerializer,
    ComplianceCommsSerializer,
    ComplianceAmendmentRequestSerializer,
    CompAmendmentRequestDisplaySerializer
)
from disturbance.components.main.utils import get_template_group,handle_validation_error
from disturbance.helpers import is_customer, is_internal
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from disturbance.components.proposals.api import ProposalFilterBackend #, ProposalRenderer
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer


class ComplianceFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        #def get_choice(status, choices=Approval.STATUS_CHOICES):
        #    for i in choices:
        #        if i[1]==status:
        #            return i[0]
        #    return None

        def get_processing_choice(status, choices=Compliance.PROCESSING_STATUS_CHOICES):
            for i in choices:
                if i[1]==status:
                    return i[0]
            return None
        def get_customer_choice(status, choices=Compliance.CUSTOMER_STATUS_CHOICES):
            for i in choices:
                if i[1]==status:
                    return i[0]
            return None
        regions = request.GET.get('regions')
        if regions:
            queryset = queryset.filter(proposal__region__name__iregex=regions.replace(',', '|'))
        proposal_activity = request.GET.get('proposal_activity')
        if proposal_activity and not proposal_activity.lower() == 'all':
            queryset = queryset.filter(proposal__activity=proposal_activity)
        compliance_status = request.GET.get('compliance_status')
        if compliance_status and not compliance_status.lower() == 'all':
            is_external = request.GET.get('is_external')
            if is_external == 'true':
                queryset = queryset.filter(customer_status=get_customer_choice(compliance_status))
            else:
                queryset = queryset.filter(processing_status=get_processing_choice(compliance_status))

        start_date_from = request.GET.get('start_date_from')
        start_date_to = request.GET.get('start_date_to')
        if start_date_from:
            queryset = queryset.filter(approval__start_date__gte=start_date_from)
        if start_date_to:
            queryset = queryset.filter(approval__start_date__lte=start_date_to)

        due_date_from = request.GET.get('due_date_from')
        due_date_to = request.GET.get('due_date_to')
        if due_date_from:
            queryset = queryset.filter(due_date__gte=due_date_from)
        if due_date_to:
            queryset = queryset.filter(due_date__lte=due_date_to)

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
            queryset = super(ComplianceFilterBackend, self).filter_queryset(request, queryset, view)
        except Exception as e:
            print(e)
        setattr(view, '_datatables_total_count', total_count)
        return queryset


class CompliancePaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ComplianceFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    #renderer_classes = (ComplianceRenderer,)
    page_size = 10
    queryset = Compliance.objects.none()
    serializer_class = DTComplianceSerializer

    def get_queryset(self):
        if is_internal(self.request):
            #return Compliance.objects.all()
            return Compliance.objects.all().exclude(processing_status='discarded')
        elif is_customer(self.request):
            user_orgs = [org.id for org in self.request.user.disturbance_organisations.all()]
            compliance_id_list = []
            for das_compliance in Compliance.objects.filter( 
                    Q(proposal__applicant_id__in = user_orgs) | Q(proposal__submitter = self.request.user
                        ) ).exclude(processing_status='discarded'):
                        compliance_id_list.append(das_compliance.id)
            # Return all records
            queryset =  Compliance.objects.filter(id__in=compliance_id_list)
            return queryset
        return Compliance.objects.none()
    
    def get_external_queryset(self):
        if is_internal(self.request):
            #return Compliance.objects.all()
            #return Compliance.objects.all().exclude(processing_status='discarded')
            user_orgs = [org.id for org in self.request.user.disturbance_organisations.all()]
            compliance_id_list = []
            
            # DAS logic
            for das_compliance in Compliance.objects.filter( 
                    Q(proposal__applicant_id__in = user_orgs) | Q(proposal__submitter = self.request.user
                        ) ).exclude(processing_status='discarded'):
                        compliance_id_list.append(das_compliance.id)
            # Return all records
            queryset =  Compliance.objects.filter(id__in=compliance_id_list)
            return queryset
        elif is_customer(self.request):
            user_orgs = [org.id for org in self.request.user.disturbance_organisations.all()]
            compliance_id_list = []
            # DAS logic
            for das_compliance in Compliance.objects.filter( 
                    Q(proposal__applicant_id__in = user_orgs) | Q(proposal__submitter = self.request.user
                        ) ).exclude(processing_status='discarded'):
                        compliance_id_list.append(das_compliance.id)
            # Return all records
            queryset =  Compliance.objects.filter(id__in=compliance_id_list)
            return queryset
        return Compliance.objects.none()



    @action(methods=['GET',], detail=False)
    def compliances_external(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the external dashboard

        To test:
            http://localhost:8000/api/compliance_paginated/compliances_external/?format=datatables&draw=1&length=2
        """
        template_group  =  get_template_group(request)
        if template_group == 'das':
            apiary_proposal_types=['Apiary','Site Transfer','Temporary Use']
            # qs = self.get_queryset().exclude(proposal__application_type__name__in=apiary_proposal_types)
            qs = self.get_external_queryset().exclude(proposal__application_type__name__in=apiary_proposal_types)
        qs = self.filter_queryset(qs)

        applicant_id = request.GET.get('org_id')
        if applicant_id:
            qs = qs.filter(proposal__applicant_id=applicant_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = DTComplianceSerializer(result_page, context={'request':request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)


class ComplianceViewSet(viewsets.ModelViewSet):
    serializer_class = ComplianceSerializer
    #queryset = Compliance.objects.all()
    queryset = Compliance.objects.none()

    def get_queryset(self):
        if is_internal(self.request):
            #return Compliance.objects.all()
            return Compliance.objects.all().exclude(processing_status='discarded')
        elif is_customer(self.request):
            user_orgs = [org.id for org in self.request.user.disturbance_organisations.all()]
            compliance_id_list = []
            for das_compliance in Compliance.objects.filter( 
                    Q(proposal__applicant_id__in = user_orgs) | Q(proposal__submitter = self.request.user
                        ) ).exclude(processing_status='discarded'):
                        compliance_id_list.append(das_compliance.id)
            # Return all records
            queryset =  Compliance.objects.filter(id__in=compliance_id_list)
            return queryset
        return Compliance.objects.none()

    #def get_queryset(self):
    #    if is_internal(self.request):
    #        return Compliance.objects.all().exclude(processing_status='discarded')
    #    elif is_customer(self.request):
    #        user_orgs = [org.id for org in self.request.user.disturbance_organisations.all()]
    #        queryset =  Compliance.objects.filter( Q(proposal__applicant_id__in = user_orgs) | Q(proposal__submitter = self.request.user) ).exclude(processing_status='discarded')
    #        return queryset
    #    return Compliance.objects.none()

    #TODO: review this - seems like a workaround at the moment
    def get_serializer_class(self):
        try:
            compliance = self.get_object()
            return ComplianceSerializer
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
        
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Filter by org
        org_id = request.GET.get('org_id',None)
        if org_id:
            queryset = queryset.filter(proposal__applicant_id=org_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET',], detail=False)
    def filter_list(self, request, *args, **kwargs):
        """ Used by the external dashboard filters """
        region_qs =  self.get_queryset().filter(proposal__region__isnull=False).values_list('proposal__region__name', flat=True).distinct()
        activity_qs =  self.get_queryset().filter(proposal__activity__isnull=False).values_list('proposal__activity', flat=True).distinct()
        data = dict(
            regions=region_qs,
            activities=activity_qs,
        )
        return Response(data)


#    @list_route(methods=['GET',])
#    def compliances_paginated(self, request, *args, **kwargs):
#        """
#        Used by the external dashboard
#
#        http://localhost:8499/api/compliances/compliances_external/paginated/?format=datatables&draw=1&length=2
#        """
#
#        qs = self.get_queryset().exclude(processing_status='future')
#        qs = ProposalFilterBackend().filter_queryset(request, qs, self)
#
#        paginator = DatatablesPageNumberPagination()
#        paginator.page_size = qs.count()
#        result_page = paginator.paginate_queryset(qs, request)
#        serializer = ComplianceSerializer(result_page, context={'request':request}, many=True)
#        return paginator.get_paginated_response(serializer.data)

#    @list_route(methods=['GET',])
#    def user_list(self, request, *args, **kwargs):
#        #Remove filter to include 'Apporved Proposals in external dashboard .exclude(processing_status=Proposal.PROCESSING_STATUS_CHOICES[13][0])
#        queryset = self.get_queryset().exclude(processing_status='future')
#        serializer = ComplianceSerializer(queryset, many=True)
#        return Response(serializer.data)
#
#    @list_route(methods=['GET'])
#    def user_list_paginated(self, request, *args, **kwargs):
#        """
#        Placing Paginator class here (instead of settings.py) allows specific method for desired behaviour),
#        otherwise all serializers will use the default pagination class
#
#        https://stackoverflow.com/questions/29128225/django-rest-framework-3-1-breaks-pagination-paginationserializer
#        """
#        queryset = self.get_queryset().exclude(processing_status='future')
#        paginator = DatatablesPageNumberPagination()
#        paginator.page_size = queryset.count()
#        result_page = paginator.paginate_queryset(queryset, request)
#        #serializer = ListProposalSerializer(result_page, context={'request':request}, many=True)
#        serializer = self.get_serializer(result_page, context={'request':request}, many=True)
#        return paginator.get_paginated_response(serializer.data)

    @action(methods=['POST',], detail=True)
    @renderer_classes((JSONRenderer,))
    def submit(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()

                data = {
                'text': request.data.get('detail')
                }
                serializer = SaveComplianceSerializer(instance, data=data)
                serializer.is_valid(raise_exception=True)

                # Must ensure processing_status is "future" or "due" to prevent modification of
                # data that has previously been approved or is with assessor.
                if instance.processing_status not in [instance.PROCESSING_STATUS_CHOICES[0][0],
                                                      instance.PROCESSING_STATUS_CHOICES[1][0]]:
                    raise serializers.ValidationError("Compliance Request is not in the correct processing status: ",
                                                       instance.processing_status)
                instance = serializer.save()
                instance.submit(request)
                serializer = self.get_serializer(instance)
                # Save the files
                '''for f in request.FILES:
                    document = instance.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents'''
                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['GET',], detail=True)
    def assign_request_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.assign_to(request.user,request)
            serializer = ComplianceSerializer(instance)
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
    def delete_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            doc=request.data.get('document')
            instance.delete_document(request, doc)
            serializer = ComplianceSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(methods=['POST',], detail=True)
    def assign_to(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_id = request.data.get('user_id',None)
            user = None
            if not user_id:
                raise serializers.ValidationError('A user id is required')
            try:
                user = EmailUser.objects.get(id=user_id)
            except EmailUser.DoesNotExist:
                raise serializers.ValidationError('A user with the id passed in does not exist')
            instance.assign_to(user,request)
            serializer = ComplianceSerializer(instance)
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
            serializer = (instance)
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
    def accept(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.accept(request)
            serializer = ComplianceSerializer(instance)
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
            serializer = CompAmendmentRequestDisplaySerializer(qs,many=True)
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
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ComplianceActionSerializer(qs,many=True)
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
            serializer = ComplianceCommsSerializer(qs,many=True)
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
                request_data['compliance'] = u'{}'.format(instance.id)
                request_data['staff'] = u'{}'.format(request.user.id)
                serializer = ComplianceCommsSerializer(data=request_data)
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


class ComplianceAmendmentRequestViewSet(viewsets.ModelViewSet):
    queryset = ComplianceAmendmentRequest.objects.none()
    serializer_class = ComplianceAmendmentRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return ComplianceAmendmentRequest.objects.all()
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.disturbance_organisations.all()]
            qs = ComplianceAmendmentRequest.objects.filter(Q(compliance_id__proposal_id__applicant_id__in=user_orgs)|Q(compliance_id__proposal_id__submitter_id=user.id))
            return qs
        return ComplianceAmendmentRequest.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data= request.data)
            serializer.is_valid(raise_exception = True)
            instance = serializer.save()
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




class ComplianceAmendmentReasonChoicesView(views.APIView):

    renderer_classes = [JSONRenderer,]
    def get(self,request, format=None):
        choices_list = []
        #choices = ComplianceAmendmentRequest.REASON_CHOICES
        choices=ComplianceAmendmentReason.objects.all()
        if choices:
            for c in choices:
                choices_list.append({'key': c.id,'value': c.reason})
        return Response(choices_list)

