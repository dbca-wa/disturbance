import traceback
import os
import csv
import requests
from requests.auth import HTTPBasicAuth

import json
from dateutil import parser
from deepdiff import DeepDiff
import inspect

import pytz
from ledger.settings_base import TIME_ZONE, DATABASES
from django.conf import settings
from django.db.models import F, Q
from django.db import transaction, connection
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from rest_framework import viewsets, serializers, status, views
from rest_framework.decorators import detail_route, list_route, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from ledger.accounts.models import EmailUser
from datetime import datetime
import time
from reversion.models import Version
from django.core.cache import cache

from django.http import HttpResponse, JsonResponse #, Http404
from disturbance.components.proposals.email import (
    send_proposal_prefill_request_sent_email_notification,
    send_proposal_refresh_request_sent_email_notification,
    send_proposal_test_sqq_request_sent_email_notification,
)
from disturbance.components.approvals.email import (
    send_contact_licence_holder_email,
    send_on_site_notification_email,
)
#from disturbance.components.approvals.serializers_apiary import (
#    ApiarySiteOnApprovalGeometrySerializer,
#    ApiarySiteOnApprovalMinimalGeometrySerializer,
#    ApiarySiteOnApprovalMinGeometrySerializer,
#)
from disturbance.utils import search_label, get_schema_questions
from disturbance.components.main.decorators import basic_exception_handler, timeit, query_debugger, api_exception_handler

from django.shortcuts import redirect, get_object_or_404
from disturbance.components.main.models import ApplicationType, DASMapLayer, TaskMonitor, RequestTypeEnum
from disturbance.components.proposals.models import (
    Proposal,
    ProposalUserAction,
    MasterlistQuestion,
    CddpQuestionGroup,
    SpatialQueryQuestion,
    SpatialQueryLayer,
    SpatialQueryMetrics,
)
from disturbance.components.main.serializers import DASMapLayerSqsSerializer
from disturbance.components.proposals.serializers import (
    ProposalSerializer,
    SchemaMasterlistOptionSerializer,
)
from disturbance.components.proposals.sqs_utils.serializers import (
    DTSpatialQueryQuestionSerializer,
    SpatialQueryLayerSerializer,
    DTSpatialQueryMetricsSerializer,
    DTSpatialQueryMetricsDetailsSerializer,
    DTSpatialQueryLayersUsedSerializer,
    CddpQuestionGroupSerializer,
)
from disturbance.helpers import is_authorised_to_modify, is_customer, is_internal, log_request
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer

from disturbance.components.main.utils import (
    check_db_connection,
)
import logging
logger = logging.getLogger(__name__)


def get_sqs_url(url_name, user='', func=''):
    return f'{settings.SQS_APIURL}{url_name}' if f'{settings.SQS_APIURL}'.endswith('/') else f'{settings.SQS_APIURL}/{url_name}'


class ProposalSqsViewSet(viewsets.ModelViewSet):
 
    queryset = Proposal.objects.none()
    serializer_class = ProposalSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Proposal.objects.filter(
                Q(region__isnull=False) |
                Q(application_type__name__in=[ApplicationType.APIARY, ApplicationType.SITE_TRANSFER, ApplicationType.TEMPORARY_USE])
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
            obj = super(ProposalSqsViewSet, self).get_object()
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
            application_type = self.get_object().application_type.name
            if application_type in (ApplicationType.APIARY, ApplicationType.SITE_TRANSFER, ApplicationType.TEMPORARY_USE):
                return ProposalApiaryTypeSerializer
            else:
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
            if application_type in (ApplicationType.APIARY, ApplicationType.SITE_TRANSFER, ApplicationType.TEMPORARY_USE):
                return ApiaryInternalProposalSerializer
                #return InternalProposalSerializer
            else:
                return InternalProposalSerializer
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @list_route(methods=['GET', ])
    @api_exception_handler
    def layers_used(self, request, *args, **kwargs):
        if not is_internal(self.request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        response = cache.get(f'layers_used')

        if response:
            logger.info('Export Layers Used: Retrieved from cache.')
        else:

            qs = Proposal.objects.filter(layer_data__isnull=False)
            paginator = Paginator(qs, settings.QS_PAGINATOR_SIZE) # chunks 

            rows = []
            rows.append(('Proposal Number', 'Proposal Submitter', 'Proposal Section', 'Layer Name', 'Layer Version', 'Layer Modified Date', 'SQS Timestamp'))
            #for p_id in p_ids:
            for page_num in paginator.page_range:
                for proposal in paginator.page(page_num).object_list:
                    for data in proposal.layer_data:
                        rows.append((proposal.lodgement_number, proposal.submitter, data['name'], data['layer_name'], data['layer_version'], data['layer_modified_date'], data['sqs_timestamp']))

            filename = f'layers_used_{datetime.now().strftime("%Y%m%dT%H%M")}.csv'
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename={filename}'
            response['filename'] = filename 
            writer = csv.writer(response)
            for row in rows:
                writer.writerow(row)

            cache.set(f'layers_used', response, settings.LAYERS_USED_CACHE_TIMEOUT)

        return response


    @list_route(methods=['GET', ])
    @api_exception_handler
    def __layers_used(self, request, *args, **kwargs):
        if not is_internal(self.request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        response = cache.get(f'layers_used')

        if response:
            logger.info('Export Layers Used: Retrieved from cache.')
        else:
            rows = []
            rows.append(('Proposal Number', 'Proposal Submitter', 'Proposal Section', 'Layer Name', 'Layer Version', 'Layer Modified Date', 'SQS Timestamp'))
            p_ids = Proposal.objects.filter(layer_data__isnull=False).values_list('id', flat=True)
            for p_id in p_ids:
                proposal = Proposal.objects.get(id=p_id)
                for data in proposal.layer_data:
                    rows.append((proposal.lodgement_number, proposal.submitter, data['name'], data['layer_name'], data['layer_version'], data['layer_modified_date'], data['sqs_timestamp']))

            filename = f'layers_used_{datetime.now().strftime("%Y%m%dT%H%M")}.csv'
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename={filename}'
            response['filename'] = filename 
            writer = csv.writer(response)
            for row in rows:
                writer.writerow(row)

            cache.set(f'layers_used', response, settings.LAYERS_USED_CACHE_TIMEOUT)

        return response

#    @detail_route(methods=['POST',])
#    @api_exception_handler
#    def sqs_data(self, request, *args, **kwargs):
#        '''
#        Creates data payload for SQS Server API Endpoint. Request to SQS sends:
#            1. proposal.schema, proposal.data, proposal.id
#            2. CDDP masterlist questions
#            3. User Polygon (Shapefile/GeoJSON)
#            4. System short code - 'DAS'
#        ''' 
#        lodgement_number = request.data.get('lodgement_number')
#        current_ts = request.data.get('current_ts') # format required '%Y-%m-%dT%H:%M:%S'
#        proposal = Proposal.objects.get(lodgement_number=lodgement_number)
#
#        geojson=proposal.shapefile_json
#
#        #masterlist_question_qs = SpatialQueryQuestion.current_questions.all() # exclude expired questions from SQS Query
#        masterlist_question_qs = SpatialQueryQuestion.objects.all() # exclude expired questions from SQS Query
#        if not masterlist_question_qs.exists():
#            return Response(
#                {'errors': 'There are no CDDP questions in Request. Check if CDDP questions exist and are not expired'},
#                status=status.HTTP_400_BAD_REQUEST
#            )
#
#        serializer = DTSpatialQueryQuestionSerializer(masterlist_question_qs, context={'data': request.data, 'filter_expired': True}, many=True)
#        rendered = JSONRenderer().render(serializer.data).decode('utf-8')
#        masterlist_questions = json.loads(rendered)
#
#        # ONLY include masterlist_questions that are present in proposal.schema to send to SQS
#        schema_questions = get_schema_questions(proposal.schema) 
#        questions = [i['masterlist_question']['question'] for i in masterlist_questions if i['masterlist_question']['question'] in schema_questions]
#        unique_questions = list(set(questions))
#
#        # group by question
#        question_group_list = [{'question_group': i, 'questions': []} for i in unique_questions]
#        for question_dict in question_group_list:
#            for sqq_record in masterlist_questions:
#                #logger.info(sqq_record['layer']['layer_name'])
#                #if question_dict['question_group'] in sqq_record.values():
#                if question_dict['question_group'] in sqq_record['masterlist_question'].values() and len(sqq_record['layers'])>0:
#                    question_dict['questions'].append(sqq_record)
#
#        if len(question_dict['questions']) == 0:
#            return Response(
#                data={'errors': f'Questions do not appear to have any associated GIS layers: {unique_questions}'},
#                status=status.HTTP_400_BAD_REQUEST
#            )
#
#
#        data = dict(
#            proposal=dict(
#                id=proposal.id,
#                current_ts=current_ts,
#                schema=proposal.schema,
#                data=proposal.data,
#
#            ),
#            requester = request.user.email,
#            request_type=RequestTypeEnum.FULL,
#            system=settings.SYSTEM_NAME_SHORT,
#            masterlist_questions = question_group_list,
#            geojson = geojson,
#        )
#
#        #url = f'{settings.SQS_APIURL}das/spatial_query/' if f'{settings.SQS_APIURL}'.endswith('/') else f'{settings.SQS_APIURL}/das/spatial_query/'
#        url = get_sqs_url('das/spatial_query/')
#        log_request(f'{request.user} - {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} - {url}')
#        resp = requests.post(url=url, data={'data': json.dumps(data)}, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
#        if resp.status_code != 200:
#            logger.error(f'SpatialQuery API call error: {resp.content}')
#            try:
#                return Response(resp.json(), status=resp.status_code)
#            except:
#                return Response({'errors': resp.content}, status=resp.status_code)
#
#        return Response(resp.json())

    @detail_route(methods=['POST',])
    @api_exception_handler
    def sqs_data_single(self, request, *args, **kwargs):
        '''
        Used by 'Test' button for questions on CDDP Question Tab

        Creates data payload for SQS Server API Endpoint - specifically for a single masterlist question or group of questions. Request to SQS sends:
            1. proposal.schema, proposal.data, proposal.id
            2. CDDP single masterlist question (or group of masterlist questions, eg all questions for a given radio button/checkbox/select/multiselect)
            3. User Polygon (Shapefile/GeoJSON)
            4. System short code - 'DAS'

        To test (from DAS shell): 
            requests.get('http://localhost:8003/api/proposal/1528/sqs_data_single.json').json()
        ''' 

        group_mlqs = request.data.get('group_mlqs', True) # group questions for given widget (radionbutton, checkbox, select, multiselect)
        mlq_id = request.data.get('masterlist_question_id')
        lodgement_number = request.data.get('lodgement_number')
        proposal = Proposal.objects.get(lodgement_number=lodgement_number)
        layer_id = request.data.get('layer_id')

        geojson=proposal.shapefile_json

        # get all masterlist questions
        #masterlist_question_qs_all = SpatialQueryQuestion.current_questions.all()
        masterlist_question_qs_all = SpatialQueryQuestion.objects.all()
        if not masterlist_question_qs_all.exists():
            return JsonResponse(
                data={'errors': 'There are no SpatialQuery questions in Request. Check if questions exist and/or are layers are not expired'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer_all = DTSpatialQueryQuestionSerializer(masterlist_question_qs_all, context={'data': request.data, 'filter_expired': True}, many=True)
        rendered_all = JSONRenderer().render(serializer_all.data).decode('utf-8')
        masterlist_questions_all = json.loads(rendered_all)

        # serialize specific masterlist question
        masterlist_question_qs = SpatialQueryQuestion.objects.filter(id=mlq_id)

        ''' Start Checks '''
        mlq = masterlist_question_qs[0]

        # search_label searches the p.schema for a given question section and 
        # returns the entire question section, including nested questions for that given question
        schema, _found = search_label(proposal.schema, mlq.question.question)
        if _found is not True or all(not d for d in schema):
            # schema is empty
            return JsonResponse(data={'errors': f'SpatialQuery Question not found in proposal schema <br/> {lodgement_number}'}, status=status.HTTP_400_BAD_REQUEST)

        ''' End Checks '''

        if group_mlqs:
            request_type = RequestTypeEnum.TEST_GROUP
            question_group_list = [{'question_group': masterlist_question_qs[0].question.question, 'questions': []}]
            for question_dict in question_group_list:
                for sqq_record in masterlist_questions_all:
                    #print(j['layer_name'])
                    #if question_dict['question_group'] in sqq_record.values():
                    if question_dict['question_group'] in sqq_record['masterlist_question'].values() and len(sqq_record['layers'])>0:
                        ''' question belongs to question_group AND has associated GIS layers to allow SQS query '''
                        question_dict['questions'].append(sqq_record)

            if len(question_dict['questions']) == 0:
                question = masterlist_question_qs[0].question.question
                return Response(
                    data={'errors': f'Question does not have any associated GIS layers: \'{question}\'.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            request_type = RequestTypeEnum.TEST_SINGLE
            serializer = DTSpatialQueryQuestionSerializer(masterlist_question_qs, context={'data': request.data, 'filter_expired': True}, many=True)
            rendered = JSONRenderer().render(serializer.data).decode('utf-8')
            masterlist_question_json = json.loads(rendered)

            # remove/filter questions where there are no layers (or expired layers)
            #masterlist_question_json[0]['layers'][idx]['id']
            for mlq in masterlist_question_json:
                for layer in mlq['layers']:
                    if layer['id'] == layer_id:
                        mlq['layers'] = [layer]

            if len(masterlist_question_json) == 0:
                question = masterlist_question_qs[0].question.question
                return Response(
                    data={'errors': f'Question does not have any associated GIS layers: \'{question}\'.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            question_group_list = [dict(question_group=masterlist_question_json[0]['masterlist_question']['question'], questions=masterlist_question_json)]

        data = dict(
            proposal=dict(
                id=proposal.id,
                #schema=proposal.schema,
                schema=schema,
                data=proposal.data,
            ),
            requester = request.user.email,
            #request_type=RequestTypeEnum.PARTIAL if group_mlqs else RequestTypeEnum.SINGLE,
            request_type=request_type,
            system=settings.SYSTEM_NAME_SHORT,
            masterlist_questions = question_group_list,
            geojson = geojson,
        )

#        #url = f'{settings.SQS_APIURL}das/spatial_query/' if f'{settings.SQS_APIURL}'.endswith('/') else f'{settings.SQS_APIURL}/das/spatial_query/'
#        url = get_sqs_url('das/spatial_query/')
#        log_request(f'{request.user} - {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} - {url}')
#        resp = requests.post(url=url, data={'data': json.dumps(data)}, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
#        if resp.status_code != 200:
#            logger.error(f'SpatialQuery API call error: {resp.content}')
#            try:
#                return Response(resp.json(), status=resp.status_code)
#            except:
#                return Response({'errors': resp.content}, status=resp.status_code)
#
#        return Response(resp.json())

        url = get_sqs_url('das/task_queue')
        log_request(f'{request.user} - {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} - {url}')
        resp = requests.post(url=url, data={'data': json.dumps(data)}, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
        if resp.status_code != 200:
            logger.error(f'SpatialQuery API call error: {resp.content}')
            try:
                return Response(resp.json(), status=resp.status_code)
            except:
                return Response({'errors': resp.content}, status=resp.status_code)
         
        #sqs_resp=(resp.json())
        resp_data = resp.json()
        if 'errors' in resp_data:
            logger.error(f'Error: {resp_data["errors"]}')
            raise serializers.ValidationError(f'Error: {resp_data["errors"]}')

        sqs_task_id = resp_data['data']['task_id']
        task, created = TaskMonitor.objects.get_or_create(
                task_id=sqs_task_id,
                defaults={
                    'proposal': proposal,
                    'requester': request.user,
                    'request_type': request_type,
                }
            )

#        if not created and task.requester.email != request.user.email:
#            # another user may attempt to Prefill, whilst job is still queued
#            logger.info(f'Task ID {task.id}, Proposal {proposal.lodgement_number} requester updated. Prev {task.requester.email}, New {request.user.email}')
#            task.requester = request.user
        #serializer = self.get_serializer(proposal)
        #resp_data['proposal']=serializer.data

        send_proposal_test_sqq_request_sent_email_notification(proposal, request.user, task.id)
        #action = ProposalUserAction.ACTION_SEND_TEST_SQQ_REQUEST_TO.format(proposal.lodgement_number, task.id, sqs_task_id, resp_data['position'])
        action = ProposalUserAction.ACTION_SEND_TEST_SQQ_REQUEST_TO.format(proposal.lodgement_number, task.id, sqs_task_id, 0)
        ProposalUserAction.log_action(proposal, action, request.user)

        #return Response(resp_data, status=resp.status_code)
        return Response(resp_data, status=resp.status_code)


#    def filter_expired_questions(self, spatial_query_question_list):
#        '''  remove/filter questions where there are no layers (or expired layers) '''
#        filtered_question_list = [mlq for mlq in spatial_query_question_list if len(mlq['layers'])>0]
#        if len(filtered_question_list) == 0:
#            mlq = masterlist_question_qs[0]
#            question = spatial_query_question_list[0]['masterlist_question']['question']
#            return Response(
#                data={'errors': f'Question does not have any associated GIS layers: \'{question}\'.'},
#                status=status.HTTP_400_BAD_REQUEST
#            )

    @detail_route(methods=['POST',])
    @api_exception_handler
    def refresh(self, request, *args, **kwargs):
        
        mlq_label = request.data.get('label')
        schema_name= request.data.get('name')
        # proposal_id = request.data.get('proposal_id')
        # proposal = Proposal.objects.get(id=proposal_id)
        proposal = self.get_object()

        #clear_data_option='clear_all'
        clear_data_option = request.data.get('option') if 'option' in request.data else 'refresh_single'
        from disturbance.utils import remove_prefilled_data
        if(clear_data_option=='clear_sqs'):
            proposal=remove_prefilled_data(proposal)
            request_type = RequestTypeEnum.REFRESH_PARTIAL
        elif(clear_data_option=='refresh_single'):
            #proposal.data=None
            request_type = RequestTypeEnum.REFRESH_SINGLE

#        # returns only the subset schema required for the refresh question. But,
#        # then only a subset p.data will be populated by SQS. Sending all allows prefill of p.data with existing values for all other q's.
#        schema, _found = search_label(proposal.schema, mlq_label) 
#        if _found is not True or all(not d for d in schema):
#            # schema is empty
#            return JsonResponse(data={'errors': f'CDDP Question not found in proposal schema <br/> {proposal.lodgement_number}'}, status=status.HTTP_400_BAD_REQUEST)
        schema = proposal.schema

        geojson=proposal.shapefile_json
        # serialize masterlist question
        masterlist_question_qs = SpatialQueryQuestion.objects.filter(question__question=mlq_label)
        #masterlist_question_qs = SpatialQueryQuestion.current_layers.filter(question__question=mlq_label)
        if not masterlist_question_qs.exists():
            return JsonResponse(
                data={'errors': f'CDDP question does not exist. First create the question in the CDDP Question section: {mlq_label}'},
                status=status.HTTP_400_BAD_REQUEST
            )
#        elif masterlist_question_qs[0].expiry and masterlist_question_qs[0].expiry < datetime.now().date():
#            mlq = masterlist_question_qs[0]
#            return Response(
#                date={'errors': 'CDDP question is expired {mlq.question}: {mlq.expired}.'},
#                status=status.HTTP_400_BAD_REQUEST
#            )

        serializer = DTSpatialQueryQuestionSerializer(masterlist_question_qs, context={'data': request.data, 'filter_expired': True}, many=True)
        rendered = JSONRenderer().render(serializer.data).decode('utf-8')
        masterlist_question_json = json.loads(rendered)

        #masterlist_question_json = self.filter_expired_questions(masterlist_question_json)
        # remove/filter questions where there are no layers (or expired layers)
        masterlist_question_json = [mlq for mlq in masterlist_question_json if len(mlq['layers'])>0]
        if len(masterlist_question_json) == 0:
            question = masterlist_question_qs[0].question.question
            #question = masterlist_question_json[0]['masterlist_question']['question']
            return Response(
                data={'errors': f'Question does not have any associated GIS layers: \'{question}\'.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        masterlist_question = [dict(question_group=masterlist_question_json[0]['masterlist_question']['question'], questions=masterlist_question_json)]


        data = dict(
            proposal=dict(
                id=proposal.id,
                #schema=proposal.schema,
                schema=schema,
                data=proposal.data,

            ),
            requester = request.user.email,
            request_type=request_type,
            system=settings.SYSTEM_NAME_SHORT,
            masterlist_questions = masterlist_question,
            geojson = geojson,
        )

        # send query to SQS - need to first retrieve csrf token and cookie from SQS 
        # resp = requests.get(f'{settings.SQS_APIURL}/csrf_token/', auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
        # meta = resp.cookies.get_dict()
        # csrftoken = meta['csrftoken'] if 'csrftoken' in meta else None
        # sessionid = meta['sessionid'] if 'sessionid' in meta else None
        # cookies = cookies={'csrftoken': csrftoken, 'sessionid': sessionid}
        # headers={'X-CSRFToken' : csrftoken}

        #url = f'{settings.SQS_APIURL}spatial_query/' if f'{settings.SQS_APIURL}'.endswith('/') else f'{settings.SQS_APIURL}/spatial_query/'
        #url = get_sqs_url('das/spatial_query/')
        url = get_sqs_url('das/task_queue')
        log_request(f'{request.user} - {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} - {url}')
        resp = requests.post(url=url, data={'data': json.dumps(data)}, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
        if resp.status_code != 200:
            logger.error(f'SpatialQuery API call error: {resp.content}')
            try:
                return Response(resp.json(), status=resp.status_code)
            except:
                return Response({'errors': resp.content}, status=resp.status_code)
              
        #sqs_resp=(resp.json())
        resp_data = resp.json()
        if 'errors' in resp_data:
            logger.error(f'Error: {resp_data["errors"]}')
            raise serializers.ValidationError(f'Error: {resp_data["errors"]}')

        sqs_task_id = resp_data['data']['task_id']
        task, created = TaskMonitor.objects.get_or_create(
                task_id=sqs_task_id,
                defaults={
                    'proposal': proposal,
                    'requester': request.user,
                    'request_type': request_type,
                }
            )

#        if not created and task.requester.email != request.user.email:
#            # another user may attempt to Prefill, whilst job is still queued
#            logger.info(f'Task ID {task.id}, Proposal {proposal.lodgement_number} requester updated. Prev {task.requester.email}, New {request.user.email}')
#            task.requester = request.user
        serializer = self.get_serializer(proposal)
        resp_data['proposal']=serializer.data

        send_proposal_refresh_request_sent_email_notification(proposal, request.user)
        action = ProposalUserAction.ACTION_SEND_REFRESH_REQUEST_TO.format(proposal.lodgement_number, task.id, sqs_task_id, resp_data['position'])
        ProposalUserAction.log_action(proposal, action, request.user)

        return Response(resp_data, status=resp.status_code)


    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def prefill_proposal(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not instance.shapefile_json:
                raise serializers.ValidationError(str('Please upload a valid shapefile'))                   

            if instance.apiary_group_application_type:
                return
            else:
                if instance.shapefile_json:
                    start_time = time.time()

                    proposal = instance
                    # current_ts = request.data.get('current_ts') # format required '%Y-%m-%dT%H:%M:%S'
                    if proposal.prefill_timestamp:
                        current_ts= proposal.prefill_timestamp.strftime('%Y-%m-%dT%H:%M:%S')
                    else:
                        current_ts = proposal.prefill_timestamp
                    geojson=proposal.shapefile_json
                    #clear_data_option='clear_all'
                    clear_data_option=request.data.get('option') if 'option' in request.data else 'clear_all'
                    from disturbance.utils import remove_prefilled_data
                    if(clear_data_option=='clear_sqs'):
                        proposal=remove_prefilled_data(proposal)
                        request_type = RequestTypeEnum.PARTIAL
                    elif(clear_data_option=='clear_all'):
                        proposal.data=None
                        request_type = RequestTypeEnum.FULL
                    proposal.save(version_comment=f'Proposal data cleared for Prefill')
                
                    #masterlist_question_qs = SpatialQueryQuestion.objects.filter()
                    #masterlist_question_qs = SpatialQueryQuestion.current_questions.all() # exclude expired questions from SQS Query
                    #masterlist_question_qs = SpatialQueryQuestion.objects.filter(question__question__icontains='2.0 What is the land tenur') # checkbox
                    #masterlist_question_qs = SpatialQueryQuestion.objects.filter(question__question__icontains='1.4.2 Are these planned dates') # radio
                    #masterlist_question_qs = SpatialQueryQuestion.objects.filter(question__question__icontains='1.2b Select widget question?') # select
                    #masterlist_question_qs = SpatialQueryQuestion.objects.filter(question__question__icontains='1.2 In which') # multi-select
                    #masterlist_question_qs = SpatialQueryQuestion.objects.filter(question__question__icontains='1.1 Proposal purpose and description') # text-area
                    #masterlist_question_qs = SpatialQueryQuestion.objects.filter(question__question__icontains='1.0 Proposal title') # text

                    masterlist_question_qs = SpatialQueryQuestion.objects.all() # exclude expired questions from SQS Query

                    serializer = DTSpatialQueryQuestionSerializer(masterlist_question_qs, context={'data': request.data, 'filter_expired': True}, many=True)
                    rendered = JSONRenderer().render(serializer.data).decode('utf-8')
                    masterlist_questions = json.loads(rendered)

                    # ONLY include masterlist_questions that are present in proposal.schema to send to SQS
                    schema_questions = get_schema_questions(proposal.schema) 
                    questions = [i['masterlist_question']['question'] for i in masterlist_questions if i['masterlist_question']['question'] in schema_questions]
                    #questions = [i['question'] for i in masterlist_questions if i['question'] in schema_questions and '1.2 In which' in i['question']]
                    unique_questions = list(set(questions))

                    # group by question
                    question_group_list = [{'question_group': i, 'questions': []} for i in unique_questions]
                    for question_dict in question_group_list:
                        for sqq_record in masterlist_questions:
                            #print(j['layer_name'])
                            if question_dict['question_group'] in sqq_record['masterlist_question'].values():
                                question_dict['questions'].append(sqq_record)

                    data = dict(
                        proposal=dict(
                            id=proposal.id,
                            current_ts=current_ts,
                            schema=proposal.schema,
                            data=proposal.data,
                        ),
                        requester = request.user.email,
                        request_type=request_type,
                        system=settings.SYSTEM_NAME_SHORT,
                        masterlist_questions = question_group_list,
                        geojson = geojson,
                    )


                    #url = get_sqs_url('das/spatial_query/')
                    url = get_sqs_url('das/task_queue')
                    #url = get_sqs_url('das_queue/')
                    log_request(f'{request.user} - {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} - {url}')
                    resp = requests.post(url=url, data={'data': json.dumps(data)}, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
                    resp_data = resp.json()
                    if 'errors' in resp_data:
                        logger.error(f'Error: {resp_data["errors"]}')
                        raise serializers.ValidationError(f'Error: {resp_data["errors"]}')                   
                    
                    sqs_task_id = resp_data['data']['task_id']
                    task, created = TaskMonitor.objects.get_or_create(
                            task_id=sqs_task_id, 
                            defaults={
                                'proposal': proposal,
                                'requester': request.user,
                                'request_type': request_type,
                            }
                        )
                    if not created and task.requester.email != request.user.email:
                        # another user may attempt to Prefill, whilst job is still queued
                        logger.info(f'Task ID {task.id}, Proposal {proposal.lodgement_number} requester updated. Prev {task.requester.email}, New {request.user.email}')
                        task.requester = request.user
                    serializer = self.get_serializer(proposal)
                    resp_data['proposal']=serializer.data

                    send_proposal_prefill_request_sent_email_notification(proposal, request.user)
                    action = ProposalUserAction.ACTION_SEND_PREFILL_REQUEST_TO.format(proposal.lodgement_number, task.id, sqs_task_id, resp_data['position'])
                    ProposalUserAction.log_action(proposal, action, request.user)

                    return Response(resp_data, status=resp.status_code)
                else:
                    raise serializers.ValidationError(str('Please upload a valid shapefile'))                   

        except Exception as e:
            logger.error(f'{traceback.print_exc()}')
            raise serializers.ValidationError(str(e))


class SpatialQueryMetricsFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """
    def filter_queryset(self, request, queryset, view):
        # Get built-in DRF datatables queryset first to join with search text,
        # then apply additional filters.
        search_text = request.GET.get('search[value]')
        if queryset.model is SpatialQueryMetrics:
            if search_text:
                search_text = search_text.lower()
                search_text_masterlist_ids = SpatialQueryMetrics.objects.values('id').filter(
                    Q(id=search_text) | Q(proposal__lodgement_number__icontains=search_text)
                )

                queryset = queryset.filter(
                    id__in=search_text_masterlist_ids
                ).distinct()
        getter = request.query_params.get
        fields = self.get_fields(getter)
        ordering = self.get_ordering(getter, fields)
        if len(ordering):
            queryset = queryset.order_by(*ordering)
        total_count = queryset.count()

        setattr(view, '_datatables_total_count', total_count)
        return queryset


class SpatialQueryQuestionFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """
    def filter_queryset(self, request, queryset, view):
        # Get built-in DRF datatables queryset first to join with search text,
        # then apply additional filters.
        search_text = request.GET.get('search[value]')
        if queryset.model is SpatialQueryQuestion:
            if search_text:
                search_text = search_text.lower()
                search_text_masterlist_ids = SpatialQueryQuestion.objects.values(
                    'id'
                ).filter(question__question__icontains=search_text)

                queryset = queryset.filter(
                    id__in=search_text_masterlist_ids
                ).distinct()
        
        getter = request.query_params.get
        fields = self.get_fields(getter)
        ordering = self.get_ordering(getter, fields)
        if len(ordering):
            queryset = queryset.order_by(*ordering)
        total_count = queryset.count()

        setattr(view, '_datatables_total_count', total_count)
        return queryset

#class SpatialQueryLayerFilterBackend(DatatablesFilterBackend):
#    """
#    Custom filters
#    """
#    def filter_queryset(self, request, queryset, view):
#        # Get built-in DRF datatables queryset first to join with search text,
#        # then apply additional filters.
#        search_text = request.GET.get('search[value]')
#        if queryset.model is SpatialQueryLayer:
#            if search_text:
#                search_text = search_text.lower()
#                search_text_masterlist_ids = SpatialQueryQuestion.objects.values(
#                    'id'
#                ).filter(question__question__icontains=search_text)
#
#                queryset = queryset.filter(
#                    id__in=search_text_masterlist_ids
#                ).distinct()
#        
#        getter = request.query_params.get
#        fields = self.get_fields(getter)
#        ordering = self.get_ordering(getter, fields)
#        if len(ordering):
#            queryset = queryset.order_by(*ordering)
#        total_count = queryset.count()
#
#        setattr(view, '_datatables_total_count', total_count)
#        return queryset


class SpatialQueryRenderer(DatatablesRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if 'view' in renderer_context and \
                hasattr(renderer_context['view'], '_datatables_total_count'):
            data['recordsTotal'] = \
                renderer_context['view']._datatables_total_count
        return super(SpatialQueryRenderer, self).render(
            data, accepted_media_type, renderer_context)


class SpatialQueryQuestionPaginatedViewSet(viewsets.ModelViewSet):
    """ For the dashboard table - http://localhost:8000/internal/schema 'Spatial Query Questions' tab """
    filter_backends = (SpatialQueryQuestionFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (SpatialQueryRenderer,)
    queryset = SpatialQueryQuestion.objects.none()
    serializer_class = DTSpatialQueryQuestionSerializer
    page_size = 10

    def get_queryset(self):
        # user = self.request.user
        return SpatialQueryQuestion.objects.all()

    @list_route(methods=['GET', ])
    def spatial_query_question_datatable_list(self, request, *args, **kwargs):
        """ http://localhost:8003/api/spatial_query_paginated/spatial_query_question_datatable_list/?format=datatables&draw=1&length=10 """
        self.serializer_class = DTSpatialQueryQuestionSerializer
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        # self.paginator.page_size = 0
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTSpatialQueryQuestionSerializer(
            result_page, context={'data': request.data, 'request': request}, many=True
        )
        data = serializer.data

#        qs_das_map_layers = DASMapLayer.objects.all()
#        das_map_layers = DASMapLayerSqsSerializer(qs_das_map_layers, context={'request': request}, many=True).data
#
#        base_api_url = reverse_lazy('api-root', request=request)
#        base_api_url = base_api_url.split('?format')[0]
#        available_sqs_layers = requests.get(base_api_url + 'spatial_query/get_sqs_layers.json', headers={}).json()
#
#        for idx, das_layer in enumerate(das_map_layers):
#            #print(idx, das_layer['layer_name'])
#            #is_available_in_sqs = any(das_layer['layer_name'] in sqs_layer['name'] for sqs_layer in available_sqs_layers)
#            available_in_sqs = [sqs_layer for sqs_layer in available_sqs_layers if sqs_layer['name'] == das_layer['layer_name']]
#            if (len(available_in_sqs) > 0):
#               das_map_layers[idx]['available_in_sqs'] = True
#               das_map_layers[idx]['active_in_sqs'] = available_in_sqs[0]['active']
#            else:
#               das_map_layers[idx]['available_in_sqs'] = False
#               das_map_layers[idx]['active_in_sqs'] = False
#
#        #data['das_map_layers'] = das_map_layers
#        data.append({'abc':das_map_layers})

        response = self.paginator.get_paginated_response(data)

        return response

    @list_route(methods=['GET', ])
    def spatial_query_layer_datatable_list(self, request, *args, **kwargs):
        """ http://localhost:8003/api/spatial_query_paginated/spatial_query_layer_datatable_list/?format=datatables&draw=1&length=10&sqq_id=225 """

        sqq_id = request.GET.get('sqq_id')
        queryset = SpatialQueryLayer.objects.filter(spatial_query_question_id=sqq_id)
        self.paginator.page_size = queryset.count()
        # self.paginator.page_size = 0
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = SpatialQueryLayerSerializer(
            result_page, context={'data': request.data, 'request': request}, many=True
        )
        data = serializer.data

        response = self.paginator.get_paginated_response(data)
        return response



#class SpatialQueryQuestionPaginatedViewSet(viewsets.ModelViewSet):
#    """ For the dashboard table - http://localhost:8000/internal/schema 'Spatial Query Questions' tab """
#    filter_backends = (DatatablesFilterBackend,)
#    #filter_backends = (SpatialQueryLayerFilterBackend,)
#    pagination_class = DatatablesPageNumberPagination
#    renderer_classes = (SpatialQueryRenderer,)
#    queryset = SpatialQueryLayer.objects.none()
#    serializer_class = SpatialQueryLayerSerializer
#    page_size = 10
#
#    def get_queryset(self):
#        # user = self.request.user
#        return SpatialQueryLayer.objects.all()
#
#    @list_route(methods=['GET', ])
#    def spatial_query_layer_datatable_list(self, request, *args, **kwargs):
#        """ http://localhost:8003/api/spatial_query_paginated/spatial_query_layer_datatable_list/?format=datatables&draw=1&length=10 """
#        self.serializer_class = SpatialQueryLayerSerializer
#        queryset = self.get_queryset()
#
#        queryset = self.filter_queryset(queryset)
#        self.paginator.page_size = queryset.count()
#        # self.paginator.page_size = 0
#        result_page = self.paginator.paginate_queryset(queryset, request)
#        serializer = SpatialQueryLayerSerializer(
#            result_page, context={'data': request.data, 'request': request}, many=True
#        )
#        data = serializer.data
#
#        response = self.paginator.get_paginated_response(data)
#        return response


class SpatialQueryMetricsPaginatedViewSet(viewsets.ModelViewSet):
    """ For the dashboard table - http://localhost:8000/internal/schema 'Spatial Query Metrics' tab """
    filter_backends = (SpatialQueryMetricsFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (SpatialQueryRenderer,)
    queryset = SpatialQueryMetrics.objects.none()
    serializer_class = DTSpatialQueryMetricsSerializer
    page_size = 10

    def get_queryset(self):
        # user = self.request.user
        return SpatialQueryMetrics.objects.all()

    @list_route(methods=['GET', ])
    def spatial_query_metrics_datatable_list(self, request, *args, **kwargs):
        """ http://localhost:8003/api/spatial_query_metrics_paginated/spatial_query_metrics_datatable_list/?format=datatables&draw=1&length=10 """
        self.serializer_class = DTSpatialQueryMetricsSerializer
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        # self.paginator.page_size = 0
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTSpatialQueryMetricsSerializer(
            result_page, context={'request': request}, many=True
        )
        data = serializer.data

        response = self.paginator.get_paginated_response(data)
        return response

    @list_route(methods=['GET', ])
    def spatial_query_metrics_details_datatable_list(self, request, *args, **kwargs):
        """ http://localhost:8003/api/spatial_query_metrics_paginated/spatial_query_metrics_datatable_list/?format=datatables&draw=1&length=10 """
        self.serializer_class = DTSpatialQueryMetricsDetailsSerializer
        #queryset = self.get_queryset().filter(id=9)
        #queryset = queryset.values('proposal__metrics')
        queryset = self.get_queryset().values('proposal__metrics')

        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        # self.paginator.page_size = 0
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTSpatialQueryMetricsDetailsSerializer(
            result_page, context={'request': request}, many=True
        )
        data = serializer.data

        response = self.paginator.get_paginated_response(data)
        return response


class SpatialQueryMetricsDetailsPaginatedViewSet(viewsets.ModelViewSet):
    """ For the dashboard table - http://localhost:8000/internal/schema 'Spatial Query Metrics' tab """
    #filter_backends = (SpatialQueryMetricsFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (SpatialQueryRenderer,)
    queryset = SpatialQueryMetrics.objects.none()
    serializer_class = DTSpatialQueryMetricsDetailsSerializer
    page_size = 10

    def get_queryset(self):
        # user = self.request.user
        return SpatialQueryMetrics.objects.all()

    @list_route(methods=['GET', ])
    def spatial_query_metrics_datatable_list(self, request, *args, **kwargs):
        """ http://localhost:8003/api/spatial_query_metrics_paginated/spatial_query_metrics_datatable_list/?format=datatables&draw=1&length=10 """
        self.serializer_class = DTSpatialQueryMetricsDetailsSerializer
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        # self.paginator.page_size = 0
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTSpatialQueryMetricsSerializer(
            result_page, context={'request': request}, many=True
        )
        data = serializer.data

        response = self.paginator.get_paginated_response(data)
        return response


class SpatialQueryQuestionViewSet(viewsets.ModelViewSet):
    """ For the 'New Question' and 'Edit' in 'Spatial Query Questions' tab  http://localhost:8000/api/spatial_query/1.json """
    queryset = SpatialQueryQuestion.objects.all()
    serializer_class = DTSpatialQueryQuestionSerializer

#    @list_route(methods=['GET', ])
#    @api_exception_handler
#    def grouped_by_question(self, request, *args, **kwargs):
#        """ http://localhost:8001/api/spatial_query/grouped_by_question.json 
#  
#            Group spatial query questions by layer_name
#        """
#        queryset = self.get_queryset()
#        #queryset = queryset.filter(id__in=[48,49,50,51,52]) # radiobutton
#        #queryset = queryset.filter(id__in=[45,46,47,55])       # checkbox
#        #queryset = queryset.filter(id__in=[43])             # select
#        #queryset = queryset.filter(id__in=[44])             # multi-select
#        queryset = queryset.filter(id__in=[53,54])           # text, text_area
#        serializer = self.get_serializer(queryset, many=True)
#
#        rendered = JSONRenderer().render(serializer.data).decode('utf-8')
#        sqq_json = json.loads(rendered)
#
#        questions = [i['question'] for i in sqq_json]
#        unique_questions = list(set(questions))
#        question_group_list = [{'question_group': i, 'questions': []} for i in unique_questions]
#        for question_dict in question_group_list:
#            for sqq_record in sqq_json:
#                #print(j['layer_name'])
#                if question_dict['question_group'] in sqq_record.values():
#                    question_dict['questions'].append(sqq_record)
#
#        return Response(question_group_list)

    @list_route(methods=['GET', ])
    @api_exception_handler
    def get_sqs_layers(self, request, *args, **kwargs):
        '''
        EXTERNAL SQS API CALL

        Get current available layers on SQS Server.
        To test (from DAS shell): 
            requests.get('http://localhost:8002/api/v1/layers.json')

        To test via DAS redirect:
            requests.get('http://localhost:8003/api/spatial_query/get_sqs_layers/')
        ''' 
        #url = f'{settings.SQS_APIURL}layers/' if f'{settings.SQS_APIURL}'.endswith('/') else f'{settings.SQS_APIURL}/layers/'

        # check and get from cache to avoid rapid repeated API Calls to SQS
        if 'clear_cache' in request.GET:
            cache.delete('sqs_layers')

        data = cache.get('sqs_layers')
        if not data:
            url = get_sqs_url('layers/')
            log_request(f'{request.user} - {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} - {url}')
            resp = requests.get(url=url, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
            #resp = retrieve_sqs_layers(url)
            if resp.status_code != 200:
                logger.error(f'SpatialQuery API call error: {resp.content}')
                try:
                    return Response(resp.json(), status=resp.status_code)
                except:
                    return Response({'errors': resp.content}, status=resp.status_code)

            data = resp.json()
            cache.set('sqs_layers', json.dumps(data), settings.SQS_LAYERS_CACHE_TIMEOUT)
        else:
            data = json.loads(data)

        return Response(data)

    @list_route(methods=['GET', ])
    def get_spatialquery_selects(self, request, *args, **kwargs):
        '''
        INTERNAL DAS API CALLS

        Get independant Select lists associated with SpatialQuery Questions.
        eg. http://localhost:8000/api/spatial_query/get_spatialquery_selects.json
        '''
        try:

            excl_operator_choices = []
            excl_how_choices = []

            operators = [
                {
                    'value': a[0], 'label': a[1]
                } for a in SpatialQueryLayer.OPERATOR_CHOICES
                if a[0] not in excl_operator_choices
            ]

            how = [
                {
                    'value': a[0], 'label': a[1]
                } for a in SpatialQueryLayer.HOW_CHOICES
                if a[0] not in excl_how_choices
            ]

            qs_mlq = MasterlistQuestion.objects.all()
            masterlist = SchemaMasterlistOptionSerializer(qs_mlq, many=True).data
            #masterlist = SchemaMasterlistSerializer(qs, many=True).data

            qs_cddp = CddpQuestionGroup.objects.all()
            cddp_groups = CddpQuestionGroupSerializer(qs_cddp, context={'request': request}, many=True).data

            qs_das_map_layers = DASMapLayer.objects.all()
            das_map_layers = DASMapLayerSqsSerializer(qs_das_map_layers, context={'request': request}, many=True).data

#            # this is a call to retrieve response from the local API endpoint (which sends onward request to SQS API Endpoint)
#            base_api_url = reverse_lazy('api-root', request=request)
#            available_sqs_layers = requests.get(base_api_url + 'spatial_query/get_sqs_layers.json', headers={}).json()
#
#            for idx, das_layer in enumerate(das_map_layers):
#                #print(idx, das_layer['layer_name'])
#                #is_available_in_sqs = any(das_layer['layer_name'] in sqs_layer['name'] for sqs_layer in available_sqs_layers)
#                available_in_sqs = [sqs_layer for sqs_layer in available_sqs_layers if sqs_layer['name'] == das_layer['layer_name']]
#                if (len(available_in_sqs) > 0):
#                   das_map_layers[idx]['available_in_sqs'] = True
#                   das_map_layers[idx]['active_in_sqs'] = available_in_sqs[0]['active']
#                else:
#                   das_map_layers[idx]['available_in_sqs'] = False
#                   das_map_layers[idx]['active_in_sqs'] = False
#
#            expired_cddp_questions = SpatialQueryQuestion.objects.filter(
#                expiry__lt=datetime.now().date()
#                ).annotate(layer_name=F('layer__layer_name')).values('id', 'expiry', 'question', 'layer_name')

            return Response(
                {
                    'permissions': {'is_admin': request.user.is_superuser},
                    'operators': operators,
                    'how': how,
                    'cddp_groups': cddp_groups,
                    'das_map_layers': das_map_layers,
                    'all_masterlist': masterlist,
#                    'expired_cddp_questions': expired_cddp_questions,
                },
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('get_spatialquery_selects()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.error(str(e))
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    @api_exception_handler
    def check_cddp_question(self, request, *args, **kwargs):
        '''
        INTERNAL DAS API CALLS

        Checks if CDDP Qution exists in proposal.schema
        To test (from DAS shell): 
            requests.post('http://localhost:8003/api/spatial_query/59/check_cddp_question/?proposal_id=P001528')
        ''' 

        p_lodgement_number = request.GET.get('proposal_id')
        proposal = Proposal.objects.get(lodgement_number=p_lodgement_number)

        instance = self.get_object()
        data = self.get_serializer(instance).data
        question = data['question']
        answer = data['answer_mlq']

        res = search_schema(proposal.id, question)
        if not res:
            return JsonResponse(data={'errors': f'CDDP Question not found in proposal schema {p_lodgement_number}'}, status=status.HTTP_400_BAD_REQUEST)

#        if res:
#            if 'text' not in res['type'] and not answer:
#                # the widget type is neither ['text', textbox], 
#                # therefore answer_mlq is required (for select, multi-select, checkbox, radiobutton)
#                return JsonResponse(data={'errors': f'CDDP Question: An answer is required for widget type: {res["type"]}.'}, status=status.HTTP_400_BAD_REQUEST)
#        else:
#            return JsonResponse(data={'errors': f'CDDP Question not found in proposal schema {p_lodgement_number}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


    @detail_route(methods=['GET',])
    @api_exception_handler
    def check_sqs_layer(self, request, *args, **kwargs):
        '''
        EXTERNAL SQS API CALL

        Checks if layer exists on SQS Server
        To test (from DAS shell): 
            requests.get('http://localhost:8003/api/spatial_query/59/check_sqs_layer.json')

            This will direct query to SQS Server
        ''' 

        layer_name = kwargs['pk']

        # check and get from cache to avoid rapid repeated API Calls to SQS
        cache_key = f'sqs_layer_{layer_name}'
        if 'clear_cache' in request.GET:
            cache.delete(cache_key)

        data = cache.get(cache_key)
        if not data:
            url = get_sqs_url(f'layers/check_layer')
            log_request(f'{request.user} - {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} - {url}')
            resp = requests.get(url=url, params={'layer_name':layer_name}, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
            if resp.status_code != 200:
                logger.error(f'SpatialQuery API call error: {resp.content}')
                try:
                    return Response(resp.json(), status=resp.status_code)
                except:
                    return Response({'errors': resp.content}, status=resp.status_code)

            data = resp.json()
            cache.set(cache_key, json.dumps(data), settings.SQS_LAYER_EXISTS_CACHE_TIMEOUT)
        else:
            data = json.loads(data)

        return Response(data)

    @detail_route(methods=['GET',])
    @api_exception_handler
    def get_sqs_attrs(self, request, *args, **kwargs):
        '''
        EXTERNAL SQS API CALL

        Get Layer Attributes from SQS
        To test (from DAS shell): 
            http://localhost:8002/api/v1/layers/get_attributes/?layer_name=CPT_LOCAL_GOVT_AREAS&use_cache=False
            requests.get('http://localhost:8003/api/spatial_query/CPT_LOCAL_GOVT_AREAS/get_sqs_attrs.json')

            This will direct query to SQS Server
        ''' 

        layer_name = kwargs.get('pk')
        attrs_only = request.GET.get('attrs_only')
        attr_name = request.GET.get('attr_name')

        params={'layer_name':layer_name}

        # check and get from cache to avoid rapid repeated API Calls to SQS
        cache_key = f'sqs_layer_attr_{layer_name}'
        if 'clear_cache' in request.GET:
            cache.delete(cache_key)

        data = cache.get(cache_key)
        if not data:
            url = get_sqs_url(f'layers/get_attributes')
            log_request(f'{request.user} - {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} - {url}')
            resp = requests.get(url=url, params=params, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
            #resp = requests.get(url=url, params={'layer_name':layer_name}, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
            data = resp.json()
            if resp.status_code != 200:
                logger.error(f'SpatialQuery API call error: {resp.content}')
                try:
                    return Response(resp.json(), status=resp.status_code)
                except:
                    return Response({'errors': resp.content}, status=resp.status_code)

            data = resp.json()
            cache.set(cache_key, json.dumps(data), settings.SQS_LAYER_EXISTS_CACHE_TIMEOUT)
        else:
            data = json.loads(data)

        if attrs_only:
            data = [i['attribute'] for i in data]
        else:
            data = [i['values'] for i in data if i['attribute']==attr_name] 

        if not request.GET:
            # add additional info for debugging on frontend
            layer_url = get_sqs_url(f'layers/{layer_name}/geojson')
            log_request(f'{request.user} - {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} - {url}')
            data.update({'layer_url': layer_url}) if isinstance(data, dict) else data.append({'layer_url': layer_url})

        return Response(data)

    @detail_route(methods=['GET',])
    @api_exception_handler
    def get_sqs_layer_geojson(self, request, *args, **kwargs):
        '''
        EXTERNAL SQS API CALL

        Get Layer GeoJSON from SQS - By default returns a truncated number of features
        To test (from DAS shell): 
            http://localhost:8002/api/v1/layers/geojson
            requests.get('http://localhost:8003/api/spatial_query/CPT_LOCAL_GOVT_AREAS/geojson.json')

            This will direct query to SQS Server
        ''' 

        layer_name = kwargs.get('pk')

        # check and get from cache to avoid rapid repeated API Calls to SQS
        cache_key = f'sqs_layer_geojson_{layer_name}'
        if 'clear_cache' in request.GET:
            cache.delete(cache_key)

        data = cache.get(cache_key)
        if not data:
            url = get_sqs_url(f'layers/{layer_name}/geojson')
            log_request(f'{request.user} - {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} - {url}')
            resp = requests.get(url=url, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
            if resp.status_code != 200:
                logger.error(f'SpatialQuery API call error: {resp.content}')
                try:
                    return Response(resp.json(), status=resp.status_code)
                except:
                    return Response({'errors': resp.content}, status=resp.status_code)

            data = resp.json()
            cache.set(cache_key, json.dumps(data), settings.SQS_LAYER_EXISTS_CACHE_TIMEOUT)
        else:
            data = json.loads(data)

        return Response(data)

    @detail_route(methods=['POST',])
    @api_exception_handler
    def create_or_update_sqs_layer(self, request, *args, **kwargs):
        '''
        Creates/Updates layer on SQS Server from Geoserver

        To test (from DAS shell): 
            import requests
            from requests.auth import HTTPBasicAuth
            import json

            data = {'layer_details': json.dumps({'layer_name': 'CPT_DBCA_REGIONS', 'layer_url': ' https://kaartdijin-boodja.dbca.wa.gov.au/api/catalogue/entries/CPT_DBCA_REGIONS/layer/'})}
            url='http://localhost:8002/api/v1/add_layer'
            resp = requests.post(url=url, data=data, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False, timeout=settings.REQUEST_TIMEOUT)
        ''' 
        #data = json.dumps({'layer_details': request.data.get('layer'), 'system': settings.SYSTEM_NAME_SHORT})
        layer_name = request.data.get('layer').get('layer_name')
        layer_url = request.data.get('layer').get('layer_url')
        data = {'layer_name': layer_name, 'layer_url': layer_url, 'system': settings.SYSTEM_NAME_SHORT}
        url = get_sqs_url(f'add_layer/')
        log_request(f'{request.user} - {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} - {url}')
        resp = requests.post(url=url, data=data, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False, timeout=settings.REQUEST_TIMEOUT)
        if resp.status_code != 200:
            logger.error(f'SpatialQuery API call error: {resp.content}')
            try:
                return Response(resp.json(), status=resp.status_code)
            except:
                return Response({'errors': resp.content}, status=resp.status_code)

        cache.delete('sqs_layers')

        return Response(resp.json())

#    import geopandas as gpd
#    import matplotlib as mpl
#    import matplotlib.pyplot as plt, mpld3
#    mpl.use('TkAgg')
#
#    @detail_route(methods=['GET',])
#    @api_exception_handler
#    def view_layer_polygon_overlay(self, request, *args, **kwargs):
#        '''
#        EXTERNAL SQS API CALL
#
#        Get Layer GeoJSON from SQS
#        To test (from DAS shell): 
#            http://localhost:8002/api/v1/layers/geojson
#            requests.get('http://localhost:8003/api/spatial_query/CPT_LOCAL_GOVT_AREAS/geojson.json')
#
#            This will direct query to SQS Server
#        ''' 
#
#
#        sqq_id = kwargs.get('pk')
#
#        sqq = SpatialQueryQuestion.objects.get(id=sqq_id)
#        column_name = sqq.column_name
#        layer_name = sqq.layer_name
#
#        # check and get from cache to avoid rapid repeated API Calls to SQS
#        cache_key = f'sqs_layer_geojson_{layer_name}'
#        if 'clear_cache' in request.GET:
#            cache.delete(cache_key)
#
#        layer_geojson = cache.get(cache_key)
#        if not layer_geojson:
#            url = get_sqs_url(f'layers/{layer_name}/geojson')
#            resp = requests.get(url=url, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
#            if resp.status_code != 200:
#                logger.error(f'SpatialQuery API call error: {resp.content}')
#                try:
#                    return Response(resp.json(), status=resp.status_code)
#                except:
#                    return Response({'errors': resp.content}, status=resp.status_code)
#
#            layer_geojson = resp.json()
#            cache.set(cache_key, json.dumps(layer_geojson), settings.SQS_LAYER_EXISTS_CACHE_TIMEOUT)
#        else:
#            layer_geojson = json.loads(layer_geojson)
#
#        p_lodgement_number = request.GET.get('proposal_id')
#        proposal = Proposal.objects.get(lodgement_number=p_lodgement_number)
#        polygon_geojson = proposal.shapefile_json
#
#
#        mpl.use('WebAgg') # opens a browser window with the plot and is fully interactive
#        layer_gdf = gpd.GeoDataFrame.from_features(layer_geojson)
#        polygon_gdf = gpd.GeoDataFrame.from_features(polygon_geojson)
#        #mpoly = gpd.read_file(json.dumps(geojson))
#
#        #layer_gdf = layer_gdf.to_crs(CRS_CART)
#        #polygon_gdf = polygon_gdf.to_crs(CRS_CART)
#        layer_gdf.crs = settings.CRS
#        polygon_gdf.crs = settings.CRS
#
#        fig, ax = plt.subplots(figsize=(10,10))
#
#        layer_gdf.boundary.plot(ax=ax, color='black', alpha=0.5)
#        polygon_gdf.plot(ax=ax, color='darkgreen', alpha=.5)
#
#        layer_gdf['coords'] = layer_gdf['geometry'].apply(lambda x: x.representative_point().coords[:])
#        layer_gdf['coords'] = [coords[0] for coords in layer_gdf['coords']]
#
#        for idx, row in layer_gdf.iterrows():
#           plt.annotate(text=row[column_name], xy=row['coords'], horizontalalignment='center', color='blue')
#
#        g = mpld3.fig_to_html(fig)
#        return HttpResponse(g)
#
#        #plt.show()
#        #return Response(polygon_geojson)

    @detail_route(methods=['DELETE', ])
    def delete_spatialquery(self, request, *args, **kwargs):
        '''
        Delete spatialquery record.
        '''
        try:
            instance = self.get_object()

            with transaction.atomic():

                instance.delete()

            return Response(
                {'spatialquery_id': instance.id},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('delete_spatialquery()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception()
            raise serializers.ValidationError(str(e))

    @basic_exception_handler
    def create(self, request, *args, **kwargs):

        fields = {'question_id': request.data['question_id']}
        if request.data.get('answer_mlq_id'):
            fields.update({'answer_mlq_id': request.data.get('answer_mlq_id')})

        sqq = SpatialQueryQuestion.objects.filter(**fields)
        if sqq.exists():
            return JsonResponse(
                data={'errors': 'This SpatialQuery Question/Answer already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            serializer = DTSpatialQueryQuestionSerializer(data=request.data, context={'data': request.data})
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(serializer.data)

    @detail_route(methods=['POST', ])
    def save_spatialquery(self, request, *args, **kwargs):
        '''
        Save spatialquery record.
        '''
        try:
            instance = self.get_object()

            with transaction.atomic():
                serializer = DTSpatialQueryQuestionSerializer(
                    instance, data=request.data, context={'data': request.data}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

            return Response(
                {'spatialquery_id': instance.id},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            if 'non_field_errors' in ve.get_codes() and 'unique' in ve.get_codes()['non_field_errors']:
                if any('question' in s for s in ve.detail['non_field_errors']):
                    raise serializers.ValidationError('CDDP Question and Answer already exist. Must be a unique set')
            log = '{0} {1}'.format('save_spatialquery()')
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception()
            raise serializers.ValidationError(str(e))

#    @detail_route(methods=['POST', ])
#    def _save_spatialquery(self, request, *args, **kwargs):
#        '''
#        Save spatialquery record.
#        '''
#        try:
#            instance = self.get_object()
#
#            # check attrs and values exist in layer
#            layer_name = request.data['layer']['layer_name']
#            url = get_sqs_url(f'layers/get_attributes')
#            resp = requests.get(url=url, params={'layer_name':layer_name}, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
#            if resp.status_code != 200:
#                logger.error(f'SpatialQuery API call error (get_attributes): {resp.content}')
#                return Response({'errors': resp.content}, status=resp.status_code)
#
#            data = resp.json()
#            layer_attrs = [d['attribute'] for d in data]
#            #attr_values = [d['values'] for d in data if 'LGA_TYPE' in  d['attribute']]
#            #layer_attrs = []
#            #for d in data:
#            #    layer_attrs.append(d['attribute'])
#            #    if 'LGA_TYPE' in d['attribute']:
#            #        attr_values = d['values']
#
#            sqq_column_name = request.data.get('column_name').strip()
#            sqq_answer = request.data.get('answer').strip()
#            sqq_assessor_info = request.data.get('assessor_info').strip()
#
#            proponent_items = request.data.get('proponent_items')
#            proponent_attrs_unavailable = [i['answer'] for i in proponent_items if 'answer' in i and i['answer'] not in layer_attrs]
#
#            assessor_items = request.data.get('assessor_items')
#            assessor_attrs_unavailable = [i['info'] for i in assessor_items if 'info' in i and i['info'] not in layer_attrs]
#
#
#            if sqq_column_name not in layer_attrs:
#                # check column_name in exists layer_attrs
#                return JsonResponse(
#                    data={'errors': f'Column name \'{sqq_column_name}\' not available in Layer {layer_name}.<br><br>Attributes available are<br>{layer_attrs}'},
#                    status=status.HTTP_400_BAD_REQUEST
#                )
#
#            #if sqq_answer and (not sqq_answer.startswith('::') or sqq_answer.split('::')[1] not in layer_attrs):
#            if proponent_attrs_unavailable:
#                # check answer (label) in exists layer_attrs
#                return JsonResponse(
#                    data={'errors': f'Answer(s) (Proponent section) \'{proponent_attrs_unavailable}\' not available in Layer {layer_name}.<br><br>Attributes available are<br>{layer_attrs}'},
#                    status=status.HTTP_400_BAD_REQUEST
#                )
#
#            #if sqq_assessor_info and (not sqq_assessor_info.startswith('::') or sqq_assessor_info.split('::')[1] not in layer_attrs):
#            if assessor_attrs_unavailable:
#                # check assessor_info (label) exists in layer_attrs
#                return JsonResponse(
#                    data={'errors': f'Info for assessor (Assessor section) \'{assessor_attrs_unavailable}\' not available in Layer {layer_name}.<br><br>Attributes available are<br>{layer_attrs}'},
#                    status=status.HTTP_400_BAD_REQUEST
#                )
#
#            with transaction.atomic():
#
#                serializer = DTSpatialQueryQuestionSerializer(
#                    instance, data=request.data, context={'data': request.data}
#                )
#                serializer.is_valid(raise_exception=True)
#                serializer.save()
#
#            return Response(
#                {'spatialquery_id': instance.id},
#                status=status.HTTP_200_OK
#            )
#
#        except serializers.ValidationError as ve:
#            if 'non_field_errors' in ve.get_codes() and 'unique' in ve.get_codes()['non_field_errors']:
#                if any('question' in s for s in ve.detail['non_field_errors']):
#                    raise serializers.ValidationError('CDDP Question and Answer already exist. Must be a unique set')
#            log = '{0} {1}'.format('save_spatialquery()')
#            logger.exception(log)
#            raise
#
#        except ValidationError as e:
#            if hasattr(e, 'error_dict'):
#                raise serializers.ValidationError(repr(e.error_dict))
#            else:
#                raise serializers.ValidationError(repr(e[0]))
#
#        except Exception as e:
#            logger.exception()
#            raise serializers.ValidationError(str(e))

class SpatialQueryLayerViewSet(viewsets.ModelViewSet):
    """ For the 'New Layer' and 'Edit' in 'Spatial Query Questions' tab  http://localhost:8000/api/spatial_query/1.json """
    queryset = SpatialQueryLayer.objects.all()
    serializer_class = SpatialQueryLayerSerializer

    @detail_route(methods=['DELETE', ])
    def delete_spatialquerylayer(self, request, *args, **kwargs):
        '''
        Delete spatialquerylayer record.
        '''
        try:
            instance = self.get_object()

            with transaction.atomic():
                instance.delete()

            # get masterlist_question_json, and return to caller js func - allows datatable in nested js modal to be refreshed
            #sqq_id = request.data['spatial_query_question_id']
            #masterlist_question = SpatialQueryQuestion.objects.get(id=sqq_id)
            #serializer = DTSpatialQueryQuestionSerializer(instance, context={}, many=False)
#            serializer = SpatialQueryLayerSerializer(instance, context={}, many=False)
#            rendered = JSONRenderer().render(serializer.data).decode('utf-8')
#            layers_json = json.loads(rendered)

            sqq_id = instance.spatial_query_question_id
            masterlist_question = SpatialQueryQuestion.objects.get(id=sqq_id)
            serializer = DTSpatialQueryQuestionSerializer(masterlist_question, context={}, many=False)
            rendered = JSONRenderer().render(serializer.data).decode('utf-8')
            masterlist_question_json = json.loads(rendered)


            return Response(
                {'spatialquery_id': instance.id, 'data': masterlist_question_json},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            log = '{0} {1}'.format('delete_spatialquery()', ve)
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception()
            raise serializers.ValidationError(str(e))


    @basic_exception_handler
    def create(self, request, *args, **kwargs):
#        fields = {'question_id': request.data['question_id']}
#        if request.data.get('answer_mlq_id'):
#            fields.update({'answer_mlq_id': request.data.get('answer_mlq_id')})

#        sqq = SpatialQueryQuestion.objects.filter(**fields)
#        if sqq.exists():
#            return JsonResponse(
#                data={'errors': 'This SpatialQuery Question/Answer already exists.'},
#                status=status.HTTP_400_BAD_REQUEST
#            )
        
        with transaction.atomic():
            serializer = SpatialQueryLayerSerializer(data=request.data, context={'data': request.data})
            serializer.is_valid(raise_exception=True)
            serializer.save()

        sqq_id = request.data['spatial_query_question_id']
        masterlist_question = SpatialQueryQuestion.objects.get(id=sqq_id)
        serializer = DTSpatialQueryQuestionSerializer(masterlist_question, context={}, many=False)
        rendered = JSONRenderer().render(serializer.data).decode('utf-8')
        masterlist_question_json = json.loads(rendered)

        return Response(
            {'spatialquerylayer_id': serializer.data['id'], 'data': masterlist_question_json},
            status=status.HTTP_200_OK
        )

        #return Response(serializer.data)

    @detail_route(methods=['POST', ])
    def save_spatialquerylayer(self, request, *args, **kwargs):
        '''
        Save spatialquery record.
        '''
        try:
            instance = self.get_object()

            # check attrs and values exist in layer
            layer_name = request.data['layer']['layer_name']
            url = get_sqs_url(f'layers/get_attributes')
            log_request(f'{request.user} - {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} - {url}')
            resp = requests.get(url=url, params={'layer_name':layer_name}, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
            if resp.status_code != 200:
                logger.error(f'SpatialQuery API call error (get_attributes): {resp.content}')
                return Response({'errors': resp.content}, status=resp.status_code)

            data = resp.json()
            layer_attrs = [d['attribute'] for d in data]
            #attr_values = [d['values'] for d in data if 'LGA_TYPE' in  d['attribute']]
            #layer_attrs = []
            #for d in data:
            #    layer_attrs.append(d['attribute'])
            #    if 'LGA_TYPE' in d['attribute']:
            #        attr_values = d['values']

            sqq_column_name = request.data.get('column_name').strip()
            sqq_answer = request.data.get('answer').strip()
            sqq_assessor_info = request.data.get('assessor_info').strip()

            proponent_items = request.data.get('proponent_items')
            proponent_attrs_unavailable = [i['answer'] for i in proponent_items if 'answer' in i and i['answer'].strip() and i['answer'] not in layer_attrs]

            assessor_items = request.data.get('assessor_items')
            assessor_attrs_unavailable = [i['info'] for i in assessor_items if 'info' in i and i['info'].strip() and i['info'] not in layer_attrs]


            if sqq_column_name not in layer_attrs:
                # check column_name in exists layer_attrs
                return JsonResponse(
                    data={'errors': f'Column name \'{sqq_column_name}\' not available in Layer {layer_name}.<br><br>Attributes available are<br>{layer_attrs}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            #if sqq_answer and (not sqq_answer.startswith('::') or sqq_answer.split('::')[1] not in layer_attrs):
            if proponent_attrs_unavailable:
                # check answer (label) in exists layer_attrs
                return JsonResponse(
                    data={'errors': f'Answer(s) (Proponent section) \'{proponent_attrs_unavailable}\' not available in Layer {layer_name}.<br><br>Attributes available are<br>{layer_attrs}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            #if sqq_assessor_info and (not sqq_assessor_info.startswith('::') or sqq_assessor_info.split('::')[1] not in layer_attrs):
            if assessor_attrs_unavailable:
                # check assessor_info (label) exists in layer_attrs
                return JsonResponse(
                    data={'errors': f'Info for assessor (Assessor section) \'{assessor_attrs_unavailable}\' not available in Layer {layer_name}.<br><br>Attributes available are<br>{layer_attrs}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():

                #serializer = DTSpatialQueryQuestionSerializer(
                serializer = SpatialQueryLayerSerializer(
                    instance, data=request.data, context={'data': request.data}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

            # get masterlist_question_json, and return to caller js func - allows datatable in nested js modal to be refreshed
            sqq_id = request.data['spatial_query_question_id']
            masterlist_question = SpatialQueryQuestion.objects.get(id=sqq_id)
            serializer = DTSpatialQueryQuestionSerializer(masterlist_question, context={}, many=False)
            rendered = JSONRenderer().render(serializer.data).decode('utf-8')
            masterlist_question_json = json.loads(rendered)

            return Response(
                    #{'spatialquery_id': instance.id, 'layers': masterlist_question_json['layers']},
                    {'spatialquery_id': instance.id, 'data': masterlist_question_json},
                status=status.HTTP_200_OK
            )

        except serializers.ValidationError as ve:
            if 'non_field_errors' in ve.get_codes() and 'unique' in ve.get_codes()['non_field_errors']:
                if any('question' in s for s in ve.detail['non_field_errors']):
                    raise serializers.ValidationError('CDDP Question and Answer already exist. Must be a unique set')
            log = '{0} {1}'.format('save_spatialquery()')
            logger.exception(log)
            raise

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0]))

        except Exception as e:
            logger.exception()
            raise serializers.ValidationError(str(e))


