import re
from datetime import datetime
import time

import pytz
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.contrib.gis.geos import Point, GEOSGeometry
from django.db.models import Q
from django.urls import reverse
from django.core.paginator import Paginator
from ledger.accounts.models import EmailUser, Document
from rest_framework import serializers

from disturbance.components.main.decorators import timeit, traceback_exception_handler
from disturbance.components.proposals.models import ProposalDocument, ProposalUserAction, ApiarySite, SiteCategory, \
    ProposalApiaryTemporaryUse, TemporaryUseApiarySite, ApiarySiteOnProposal, Proposal
from disturbance.components.proposals.serializers import SaveProposalSerializer

from disturbance.components.approvals.models import Approval
from disturbance.components.proposals.models import (
    SiteTransferApiarySite,
    ApiaryChecklistQuestion,
    ApiaryChecklistAnswer,
    QuestionOption,
    MasterlistQuestion,
    ProposalTypeSection,
    SectionQuestion,
    HelpPage,
    ApplicationType,
    ExportDocument,
)
from disturbance.components.proposals.serializers_apiary import (
    ProposalApiarySerializer,
    ProposalApiaryTemporaryUseSerializer,
    ApiarySiteSerializer, TemporaryUseApiarySiteSerializer,
    ApiarySiteOnProposalDraftGeometrySaveSerializer
)
from disturbance.components.proposals.email import send_submit_email_notification, send_external_submit_email_notification
from disturbance.components.organisations.models import Organisation
#from disturbance.components.main.utils import sqs_query

import traceback
import os
import json
import pandas as pd
import geopandas as gpd

from disturbance.settings import RESTRICTED_RADIUS, TIME_ZONE
from disturbance.utils import convert_moment_str_to_python_datetime_obj, search_keys

import logging
logger = logging.getLogger(__name__)

richtext = u''
richtext_assessor=u''

def create_data_from_form(schema, post_data, file_data, post_data_index=None,special_fields=[],assessor_data=False):
    data = {}
    special_fields_list = []
    assessor_data_list = []
    comment_data_list = {}
    add_info_applicant_list={}
    special_fields_search = SpecialFieldsSearch(special_fields)
    add_info_applicant_search=AddInfoApplicantDataSearch()
    refresh_timestamp_search= RefreshTimestampSearch()
    add_info_assessor_search=AddInfoAssessorDataSearch()
    if assessor_data:
        assessor_fields_search = AssessorDataSearch()
        comment_fields_search = CommentDataSearch()
    try:
        for item in schema:
            data.update(_create_data_from_item(item, post_data, file_data, 0, ''))
            #_create_data_from_item(item, post_data, file_data, 0, '')
            special_fields_search.extract_special_fields(item, post_data, file_data, 0, '')
            add_info_applicant_search.extract_special_fields(item, post_data, file_data, 0, '')
            refresh_timestamp_search.extract_special_fields(item, post_data, file_data, 0, '')
            add_info_assessor_search.extract_special_fields(item, post_data, file_data, 0, '')
            if assessor_data:
                assessor_fields_search.extract_special_fields(item, post_data, file_data, 0, '')
                comment_fields_search.extract_special_fields(item, post_data, file_data, 0, '')
        special_fields_list = special_fields_search.special_fields
        add_info_applicant_list = add_info_applicant_search.comment_data
        refresh_timestamp_list = refresh_timestamp_search.comment_data
        print('refresh', refresh_timestamp_list)
        add_info_assessor_list = add_info_assessor_search.comment_data
        if assessor_data:
            assessor_data_list = assessor_fields_search.assessor_data
            comment_data_list = comment_fields_search.comment_data
    except:
        traceback.print_exc()
    if assessor_data:
        return [data],special_fields_list,assessor_data_list,comment_data_list, add_info_assessor_list

    return [data],special_fields_list, add_info_applicant_list, refresh_timestamp_list


def _extend_item_name(name, suffix, repetition):
    return '{}{}-{}'.format(name, suffix, repetition)

def _create_data_from_item(item, post_data, file_data, repetition, suffix):
    item_data = {}

    if 'name' in item:
        extended_item_name = item['name']
    else:
        raise Exception('Missing name in item %s' % item['label'])

    if 'children' not in item:
        if item['type'] in ['checkbox' 'declaration']:
            #item_data[item['name']] = post_data[item['name']]
            item_data[item['name']] = extended_item_name in post_data
        elif item['type'] == 'file':
            if extended_item_name in file_data:
                item_data[item['name']] = str(file_data.get(extended_item_name))
                # TODO save the file here
            elif extended_item_name + '-existing' in post_data and len(post_data[extended_item_name + '-existing']) > 0:
                item_data[item['name']] = post_data.get(extended_item_name + '-existing')
            else:
                item_data[item['name']] = ''
        else:
            if extended_item_name in post_data:
                if item['type'] == 'multi-select':
                    item_data[item['name']] = post_data.getlist(extended_item_name)
                else:
                    item_data[item['name']] = post_data.get(extended_item_name)
    else:
        if 'repetition' in item:
            item_data = generate_item_data(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
        else:
            item_data = generate_item_data(extended_item_name, item, item_data, post_data, file_data,1,suffix)


    if 'conditions' in item:
        for condition in list(item['conditions'].keys()):
            for child in item['conditions'][condition]:
                item_data.update(_create_data_from_item(child, post_data, file_data, repetition, suffix))

    return item_data

def generate_item_data(item_name,item,item_data,post_data,file_data,repetition,suffix):
    item_data_list = []
    for rep in range(0, repetition):
        child_data = {}
        for child_item in item.get('children'):
            child_data.update(_create_data_from_item(child_item, post_data, file_data, 0,
                                                     '{}-{}'.format(suffix, rep)))
        item_data_list.append(child_data)

        item_data[item['name']] = item_data_list
    return item_data

class AssessorDataSearch(object):

    def __init__(self,lookup_field='canBeEditedByAssessor'):
        self.lookup_field = lookup_field
        self.assessor_data = []

    def extract_assessor_data(self,item,post_data):
        values = []
        res = {
            'name': item,
            'assessor': '',
            'referrals':[]
        }
        for k in post_data:
            if re.match(item,k):
                values.append({k:post_data[k]})
        if values:
            for v in values:
                for k,v in v.items():
                    parts = k.split('{}-'.format(item))
                    if len(parts) > 1:
                        # split parts to see if referall
                        ref_parts = parts[1].split('Referral-')
                        if len(ref_parts) > 1:
                            # Referrals
                            if ref_parts[0]=='': #To avoid saving the comment-field here
                                res['referrals'].append({
                                    'value':v,
                                    'email':ref_parts[1],
                                    'full_name': EmailUser.objects.get(email=ref_parts[1].lower()).get_full_name()
                                })
                        elif k.split('-')[-1].lower() == 'assessor':
                            # Assessor
                            res['assessor'] = v

        return res

    def extract_special_fields(self,item, post_data, file_data, repetition, suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            if 'conditions' in item:
                for condition in list(item['conditions'].keys()):
                    for child in item['conditions'][condition]:
                        item_data.update(self.extract_special_fields(child, post_data, file_data, repetition, suffix))

            if item.get(self.lookup_field):
                self.assessor_data.append(self.extract_assessor_data(extended_item_name,post_data))

        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
            else:
                item_data = self.generate_item_data_special_field(extended_item_name, item, item_data, post_data, file_data,1,suffix)

            if 'conditions' in item:
                for condition in list(item['conditions'].keys()):
                    for child in item['conditions'][condition]:
                        item_data.update(self.extract_special_fields(child, post_data, file_data, repetition, suffix))

        return item_data

    def generate_item_data_special_field(self,item_name,item,item_data,post_data,file_data,repetition,suffix):
        item_data_list = []
        for rep in range(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(child_item, post_data, file_data, 0,
                                                         '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data

class CommentDataSearch(object):

    def __init__(self,lookup_field='canBeEditedByAssessor'):
        self.lookup_field = lookup_field
        #self.comment_data = {}
        self.comment_data = []

    def extract_comment_data_original(self,item,post_data):
        res = {}
        values = []
        for k in post_data:
            if re.match(item,k):
                values.append({k:post_data[k]})
        if values:
            for v in values:
                for k,v in v.items():
                    parts = k.split('{}'.format(item))
                    if len(parts) > 1:
                        ref_parts = parts[1].split('-comment-field')
                        if len(ref_parts) > 1:
                            if len(ref_parts)==2 and ref_parts[0]=='' and ref_parts[1]=='':
                                print(v)
                                #if('{}'.format(item)=="Section0-1"):
                                #print(item,v, parts, ref_parts)
                            res = {'{}'.format(item):v}
        return res

    def extract_comment_data_existing(self,item,post_data):
        res = {}
        values = []
        for k in post_data:
            if re.match(item,k):
                values.append({k:post_data[k]})
        if values:
            for v in values:
                for k,v in v.items():
                    parts = k.split('{}'.format(item))
                    if len(parts) > 1:
                        ref_parts = parts[1].split('-comment-field')
                        if len(ref_parts) > 1:
                            if len(ref_parts)==2 and ref_parts[0]=='' and ref_parts[1]=='':
                                res = {'{}'.format(item):v}
        return res

    def extract_comment_data(self,item,post_data):
        values = []
        res = {
            'name': item,
            'assessor': '',
            'referrals':[]
        }
        for k in post_data:
            if re.match(item,k):
                values.append({k:post_data[k]})
        if values:
            for v in values:
                for k,v in v.items():
                    parts = k.split('{}-comment-field'.format(item))
                    if len(parts) > 1:
                        # split parts to see if referall
                        ref_parts = parts[1].split('Referral-')
                        if len(ref_parts) > 1:
                            # Referrals
                            res['referrals'].append({
                                'value':v,
                                'email':ref_parts[1],
                                'full_name': EmailUser.objects.get(email=ref_parts[1].lower()).get_full_name()
                            })
                        elif k.split('-')[-1].lower() == 'assessor':
                            # Assessor
                            res['assessor'] = v

        return res

    def extract_special_fields(self,item, post_data, file_data, repetition, suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            #print(item, extended_item_name)
            #self.comment_data.update(self.extract_comment_data(extended_item_name,post_data))
            self.comment_data.append(self.extract_comment_data(extended_item_name,post_data))

        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
            else:
                item_data = self.generate_item_data_special_field(extended_item_name, item, item_data, post_data, file_data,1,suffix)


        if 'conditions' in item:
            for condition in list(item['conditions'].keys()):
                for child in item['conditions'][condition]:
                    item_data.update(self.extract_special_fields(child, post_data, file_data, repetition, suffix))

        return item_data

    def generate_item_data_special_field(self,item_name,item,item_data,post_data,file_data,repetition,suffix):
        item_data_list = []
        for rep in range(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(child_item, post_data, file_data, 0,
                                                         '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data

class SpecialFieldsSearch(object):

    def __init__(self,lookable_fields):
        self.lookable_fields = lookable_fields
        self.special_fields = {}

    def extract_special_fields(self,item, post_data, file_data, repetition, suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            for f in self.lookable_fields:
                if item['type'] in ['checkbox' 'declaration']:
                    val = None
                    val = item.get(f,None)
                    if val:
                        item_data[f] = extended_item_name in post_data
                        self.special_fields.update(item_data)
                else:
                    if extended_item_name in post_data:
                        val = None
                        val = item.get(f,None)
                        if val:
                            if item['type'] == 'multi-select':
                                item_data[f] = ','.join(post_data.getlist(extended_item_name))
                            else:
                                item_data[f] = post_data.get(extended_item_name)
                            self.special_fields.update(item_data)
        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
            else:
                item_data = self.generate_item_data_special_field(extended_item_name, item, item_data, post_data, file_data,1,suffix)


        if 'conditions' in item:
            for condition in list(item['conditions'].keys()):
                for child in item['conditions'][condition]:
                    item_data.update(self.extract_special_fields(child, post_data, file_data, repetition, suffix))

        return item_data

    def generate_item_data_special_field(self,item_name,item,item_data,post_data,file_data,repetition,suffix):
        item_data_list = []
        for rep in range(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(child_item, post_data, file_data, 0,
                                                         '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data


class AddInfoApplicantDataSearch(object):

    def __init__(self,lookup_field='canBeEditedByAssessor'):
        self.lookup_field = lookup_field
        self.comment_data = {}
        #self.comment_data = []

    

    def extract_add_info_applicant_data(self,item,post_data):
        res = {}
        values = []
        for k in post_data:
            if re.match(item,k):
                values.append({k:post_data[k]})
        if values:
            for v in values:
                for k,v in v.items():
                    parts = k.split('{}'.format(item))
                    if len(parts) > 1:
                        ref_parts = parts[1].split('-add-info-applicant')
                        if len(ref_parts) > 1:
                            if len(ref_parts)==2 and ref_parts[0]=='' and ref_parts[1]=='':
                                res = {'{}'.format(item):v}
        return res

    
    def extract_special_fields(self,item, post_data, file_data, repetition, suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            #print(item, extended_item_name)
            #self.comment_data.update(self.extract_comment_data(extended_item_name,post_data))
            self.comment_data.update(self.extract_add_info_applicant_data(extended_item_name,post_data))

        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
            else:
                item_data = self.generate_item_data_special_field(extended_item_name, item, item_data, post_data, file_data,1,suffix)


        if 'conditions' in item:
            for condition in list(item['conditions'].keys()):
                for child in item['conditions'][condition]:
                    item_data.update(self.extract_special_fields(child, post_data, file_data, repetition, suffix))

        return item_data

    def generate_item_data_special_field(self,item_name,item,item_data,post_data,file_data,repetition,suffix):
        item_data_list = []
        for rep in range(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(child_item, post_data, file_data, 0,
                                                         '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data


class AddInfoAssessorDataSearch(object):

    def __init__(self,lookup_field='canBeEditedByAssessor'):
        self.lookup_field = lookup_field
        self.comment_data = {}
        #self.comment_data = []

    

    def extract_add_info_assessor_data(self,item,post_data):
        res = {}
        values = []
        for k in post_data:
            if re.match(item,k):
                values.append({k:post_data[k]})
        if values:
            for v in values:
                for k,v in v.items():
                    parts = k.split('{}'.format(item))
                    if len(parts) > 1:
                        ref_parts = parts[1].split('-add-info-Assessor')
                        if len(ref_parts) > 1:
                            if len(ref_parts)==2 and ref_parts[0]=='' and ref_parts[1]=='':
                                res = {'{}'.format(item):v}
        return res

    
    def extract_special_fields(self,item, post_data, file_data, repetition, suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            #print(item, extended_item_name)
            #self.comment_data.update(self.extract_comment_data(extended_item_name,post_data))
            self.comment_data.update(self.extract_add_info_assessor_data(extended_item_name,post_data))

        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
            else:
                item_data = self.generate_item_data_special_field(extended_item_name, item, item_data, post_data, file_data,1,suffix)


        if 'conditions' in item:
            for condition in list(item['conditions'].keys()):
                for child in item['conditions'][condition]:
                    item_data.update(self.extract_special_fields(child, post_data, file_data, repetition, suffix))

        return item_data

    def generate_item_data_special_field(self,item_name,item,item_data,post_data,file_data,repetition,suffix):
        item_data_list = []
        for rep in range(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(child_item, post_data, file_data, 0,
                                                         '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data

class RefreshTimestampSearch(object):

    def __init__(self,lookup_field='canBeEditedByAssessor'):
        self.lookup_field = lookup_field
        self.comment_data = {}
        #self.comment_data = []

    

    def extract_refresh_timestamp_data(self,item,post_data):
        res = {}
        values = []
        for k in post_data:
            if re.match(item,k):
                values.append({k:post_data[k]})
        if values:
            for v in values:
                for k,v in v.items():
                    parts = k.split('{}'.format(item))
                    if len(parts) > 1:
                        ref_parts = parts[1].split('-refresh-timestamp')
                        if len(ref_parts) > 1:
                            if len(ref_parts)==2 and ref_parts[0]=='' and ref_parts[1]=='':
                                res = {'{}'.format(item):v}
        return res

    
    def extract_special_fields(self,item, post_data, file_data, repetition, suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            #print(item, extended_item_name)
            #self.comment_data.update(self.extract_comment_data(extended_item_name,post_data))
            self.comment_data.update(self.extract_refresh_timestamp_data(extended_item_name,post_data))

        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
            else:
                item_data = self.generate_item_data_special_field(extended_item_name, item, item_data, post_data, file_data,1,suffix)


        if 'conditions' in item:
            for condition in list(item['conditions'].keys()):
                for child in item['conditions'][condition]:
                    item_data.update(self.extract_special_fields(child, post_data, file_data, repetition, suffix))

        return item_data

    def generate_item_data_special_field(self,item_name,item,item_data,post_data,file_data,repetition,suffix):
        item_data_list = []
        for rep in range(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(child_item, post_data, file_data, 0,
                                                         '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data

# -------------------------------------------------------------------------------------------------------------
# APIARY Section starts here
# -------------------------------------------------------------------------------------------------------------

def save_proponent_data(instance, request, viewset):
    if instance.application_type.name == 'Site Transfer':
    #if instance.application_type.name == ApplicationType.SITE_TRANSFER:
        save_proponent_data_apiary_site_transfer(instance, request, viewset)
        instance.log_user_action(ProposalUserAction.APIARY_ACTION_SAVE_APPLICATION.format(instance.lodgement_number), request)
    elif instance.apiary_group_application_type:
        save_proponent_data_apiary(instance, request, viewset)
        instance.log_user_action(ProposalUserAction.APIARY_ACTION_SAVE_APPLICATION.format(instance.lodgement_number), request)
    else:
        save_proponent_data_disturbance(instance,request,viewset)

def save_proponent_data_apiary_site_transfer(proposal_obj, request, viewset):
    with transaction.atomic():
        try:
            data = {
            }

            try:
                schema = request.data.get('schema')
            except:
                schema = request.POST.get('schema')

            sc = json.loads(schema) if schema else {}

            proposal_apiary_data = sc.get('proposal_apiary', None)
            if proposal_apiary_data:
                save_checklist_answers('applicant', proposal_apiary_data.get('applicant_checklist_answers'))

            transferee_email_text = request.data.get('transferee_email_text')
            if transferee_email_text:
                proposal_obj.proposal_apiary.transferee_email_text = transferee_email_text
                proposal_obj.proposal_apiary.save()
            selected_licence_holder_str = request.data.get('selected_licence_holder')
            selected_licence_holder = json.loads(selected_licence_holder_str) if selected_licence_holder_str else ''
            if selected_licence_holder:
                # for each path, ensure we remove any previously user selected licence holder data (target_approval, transferee, target_approval_organisation)
                if not selected_licence_holder.get('id'):
                    # new licence creation required
                    if selected_licence_holder.get('organisation_id'):
                        proposal_obj.proposal_apiary.target_approval_organisation = Organisation.objects.get(id=selected_licence_holder.get('organisation_id'))
                        proposal_obj.proposal_apiary.transferee = EmailUser.objects.get(id=selected_licence_holder.get('transferee_id'))
                        proposal_obj.proposal_apiary.target_approval = None
                    else:
                        proposal_obj.proposal_apiary.transferee = EmailUser.objects.get(id=selected_licence_holder.get('transferee_id'))
                        proposal_obj.proposal_apiary.target_approval_organisation = None
                        proposal_obj.proposal_apiary.target_approval = None
                else:
                    # Apiary licence already exists
                    proposal_obj.proposal_apiary.transferee = None
                    proposal_obj.proposal_apiary.target_approval_organisation = None
                    proposal_obj.proposal_apiary.target_approval = Approval.objects.get(id=selected_licence_holder.get('id'))
                # save for all paths
                proposal_obj.proposal_apiary.save()


            apiary_sites_local = request.data.get('apiary_sites_local')
            if apiary_sites_local:
                for site in json.loads(apiary_sites_local):
                    #print(site.get('id'))
                    #print(site.get('checked'))
                    checked_value = bool(site.get('checked'))
                    licensed_site = site['properties']['licensed_site'] = bool(site['properties'].get('licensed_site'))
                    site_transfer_apiary_site = SiteTransferApiarySite.objects.get(
                            proposal_apiary=proposal_obj.proposal_apiary, 
                            apiary_site_on_approval__apiary_site__id=site.get('id')
                            )
                    site_transfer_apiary_site.customer_selected = checked_value
                    site_transfer_apiary_site.internal_selected = checked_value
                    #apiary_site_on_approval = transfer_apiary_site.apiary_site_on_approval
                    #apiary_site_on_approval.licensed_site = licensed_site
                    site_transfer_apiary_site.save()
                    apiary_site_on_approval = site_transfer_apiary_site.apiary_site_on_approval
                    apiary_site_on_approval.licensed_site = licensed_site
                    apiary_site_on_approval.save()

            #selected_licence = proposal_apiary_data.get('selected_licence')
            #if selected_licence:
            #    proposal_obj.proposal_apiary.target_approval = Approval.objects.get(id=selected_licence)
            #    proposal_obj.proposal_apiary.save()

            ## On submit, requirements need to be copied for originating and target approvals
            if viewset.action == 'submit':
                # set transferee for applications without a target licence
                #proposal_obj.proposal_apiary.transferee = EmailUser.objects.get(email=proposal_obj.proposal_apiary.transferee_email_text)
                #proposal_obj.proposal_apiary.save()
                # Find originating approval
                originating_approval = proposal_obj.proposal_apiary.retrieve_approval
                if originating_approval:
                    # Copy requirements from approval.current_proposal
                    #origin_req = originating_approval.current_proposal.apiary_requirements(
                     #       approval=originating_approval).exclude(is_deleted=True)
                    origin_req = originating_approval.proposalrequirement_set.exclude(is_deleted=True)
                    from copy import deepcopy
                    if origin_req:
                        for origin_r in origin_req:
                            old_origin_r = deepcopy(origin_r)
                            origin_r.proposal = proposal_obj
                            #origin_r.proposal = None
                            #origin_r.site_transfer_approval = originating_approval
                            #origin_r.apiary_approval = originating_approval
                            origin_r.apiary_approval = None
                            origin_r.sitetransfer_approval = originating_approval
                            origin_r.copied_from=old_origin_r
                            origin_r.id = None
                            origin_r.save()
                # Find target approval
                #approval = proposal_apiary.retrieve_approval
                if proposal_obj.proposal_apiary.target_approval:
                    # Copy requirements from approval.current_proposal
                    #target_req = proposal_obj.proposal_apiary.target_approval.current_proposal.apiary_requirements(
                     #       approval=proposal_obj.proposal_apiary.target_approval).exclude(is_deleted=True)
                    # origin_req = proposal_obj.proposal_apiary.target_approval.proposalrequirement_set.exclude(is_deleted=True)
                    target_req = proposal_obj.proposal_apiary.target_approval.proposalrequirement_set.exclude(is_deleted=True)
                    from copy import deepcopy
                    if target_req:
                        for target_r in target_req:
                            old_target_r = deepcopy(target_r)
                            target_r.proposal = proposal_obj
                            #target_r.apiary_approval = proposal_obj.proposal_apiary.target_approval
                            target_r.apiary_approval = None
                            target_r.sitetransfer_approval = proposal_obj.proposal_apiary.target_approval
                            target_r.copied_from=old_target_r
                            target_r.id = None
                            target_r.save()

            #proposal_obj.save()

        except Exception as e:
            raise


def save_proponent_data_apiary(proposal_obj, request, viewset):
    with transaction.atomic():
        try:
            try:
                schema = request.data.get('schema')
            except:
                schema = request.POST.get('schema')

            sc = json.loads(schema) if schema else {}

            #save Site Locations data
            proposal_apiary_data = sc.get('proposal_apiary', None)

            if proposal_apiary_data:
                # New apairy site application
                local_date = get_local_date(proposal_apiary_data.get('public_liability_insurance_expiry_date', None), )
                proposal_apiary_data['public_liability_insurance_expiry_date'] = local_date.strftime('%Y-%m-%d') if local_date else None
                serializer = ProposalApiarySerializer(proposal_obj.proposal_apiary, data=proposal_apiary_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                # site_locations_received = proposal_apiary_data['apiary_sites']
                site_locations_received = json.loads(request.data.get('all_the_features'))

                # Feature object doesn't have a field named 'id' originally unless manually added
                site_ids_received = []  # Store the apiary site ids already saved in the database
                for feature in site_locations_received:
                    if isinstance(feature['id_'], int):
                        site_ids_received.append(feature['id_'])
                    else:
                        try:
                            # feature['id_'] may have site_guid rather than database id even if it has been already saved.
                            # Because feature.id in the frontend is not updated until the page refreshed
                            site_already_saved = ApiarySite.objects.get(site_guid=feature['id_'])
                            site_ids_received.append(site_already_saved.id)
                        except:
                            pass
                # site_ids_existing = [site.id for site in ApiarySite.objects.filter(proposal_apiary_id=proposal_apiary_data['id'])]
                site_ids_existing = [site.id for site in proposal_obj.proposal_apiary.apiary_sites.all()]
                # site_ids_existing_vacant = [site.id for site in proposal_obj.proposal_apiary.vacant_apiary_sites.all()]
                site_ids_existing_vacant = []  # TODO implement
                site_ids_delete = [id for id in site_ids_existing if id not in site_ids_received]
                # site_ids_delete_vacant = [id for id in site_ids_existing_vacant if id not in site_ids_received] # TODO implement
                site_ids_delete_vacant = []

                # Handle ApiarySites here
                for index, feature in enumerate(site_locations_received):
                    feature['proposal_apiary_id'] = proposal_obj.proposal_apiary.id

                    try:
                        # Update existing
                        # for the newely addes apiary site, 'id_' has its guid
                        # for the existing apiary site, 'value_'.'site_guid' has its guid
                        try:
                            # Try to get this apiary site assuming already saved as 'draft'
                            a_site = ApiarySite.objects.get(site_guid=feature['id_'])

                        except ApiarySite.DoesNotExist:
                            # Try to get this apiary site assuming it is 'vacant' site (available site)
                            a_site = ApiarySite.objects.get(site_guid=feature['values_']['site_guid'])

                        serializer = ApiarySiteSerializer(a_site, data=feature)
                    except KeyError:  # when 'site_guid' is not defined above
                        # Create new apiary site when both of the above queries failed
                        # if feature['values_']['site_category'] == 'south_west':
                        #     category_obj = SiteCategory.objects.get(name='south_west')
                        # else:
                        #     category_obj = SiteCategory.objects.get(name='remote')
                        # feature['site_category_id'] = category_obj.id
                        feature['site_guid'] = feature['id_']

                        serializer = ApiarySiteSerializer(data=feature)
                        # This is test line for gitpush

                    if serializer:
                        serializer.is_valid(raise_exception=True)
                        apiary_site_obj = serializer.save()

                        # Save coordinate
                        geom_str = GEOSGeometry(
                            'POINT(' +
                            str(feature['values_']['geometry']['flatCoordinates'][0]) + ' ' +
                            str(feature['values_']['geometry']['flatCoordinates'][1]) +
                            ')', srid=4326
                        )
                        # Get apiary_site_on_proposal obj
                        apiary_site_on_proposal, created = ApiarySiteOnProposal.objects.get_or_create(apiary_site=apiary_site_obj, proposal_apiary=proposal_obj.proposal_apiary)
                        # Save the coordinate as 'draft' coordinate
                        serializer = ApiarySiteOnProposalDraftGeometrySaveSerializer(apiary_site_on_proposal, data={
                            'wkb_geometry_draft': geom_str,
                            # 'workflow_selected_status': False,
                        })
                        serializer.is_valid(raise_exception=True)
                        serializer.save()

                        if viewset.action == 'submit':
                            # When submit, copy the coordinates from draft to the processed
                            # apiary_site_on_proposal.wkb_geometry_processed = apiary_site_on_proposal.wkb_geometry_draft
                            # apiary_site_on_proposal.site_status = ApiarySiteOnProposal.SITE_STATUS_PENDING_PAYMENT
                            apiary_site_on_proposal.making_payment = True  # This should replace the above line.  site_status should not be overwritten by 'pending_payment'
                            apiary_site_on_proposal.save()

#                        if apiary_site_obj.status in (ApiarySite.STATUS_DRAFT, ApiarySite.STATUS_PENDING, ApiarySite.STATUS_VACANT, ApiarySite.STATUS_CURRENT,):
#                            data = {'wkb_geometry_pending': geom_str}
#                            save_point_serializer = ApiarySiteSavePointPendingSerializer
#                        else:
#                            # Should not reach here?
#                            pass
#                        serializer = save_point_serializer(apiary_site_obj, data=data)
#                        serializer.is_valid(raise_exception=True)
#                        serializer.save()

                        # if apiary_site_obj.is_vacant:
                        #     apiary_site_obj.proposal_apiary = None  # This should be already None
                        #     apiary_site_obj.proposal_apiaries.add(proposal_obj.proposal_apiary)
                        #     apiary_site_obj.save()

                if viewset.action == 'submit':
                    proposal_obj.proposal_apiary.validate_apiary_sites(raise_exception=True)

                save_checklist_answers('applicant', proposal_apiary_data.get('applicant_checklist_answers'))
                # expiry_date = sanitize_date(proposal_apiary_data.get('public_liability_insurance_expiry_date'))
                # proposal_obj.proposal_apiary.public_liability_insurance_expiry_date = expiry_date
                # proposal_obj.proposal_apiary.save()

                # Delete existing
                sites_delete = ApiarySite.objects.filter(id__in=site_ids_delete)
                for site_to_delete in sites_delete:
                    proposal_obj.proposal_apiary.delete_relation(site_to_delete)


                # sites_delete.delete()

                # Update the site(s) which is picked up as proposed site
                # sites_updated = ApiarySite.objects.filter(id__in=site_ids_delete)
                # sites_updated.update(proposal_apiary=None)

                # Delete association with 'vacant' site
                # sites_remove = ApiarySite.objects.filter(id__in=site_ids_delete_vacant, status=ApiarySite.STATUS_VACANT)
                # for vacant_site in sites_remove:
                #     vacant_site.proposal_apiaries.remove(proposal_obj.proposal_apiary)

            # Save Temporary Use data
            temporary_use_data = request.data.get('apiary_temporary_use', None)
            if temporary_use_data:
                # Temporary Use Application
                apiary_temporary_use_obj = ProposalApiaryTemporaryUse.objects.get(id=request.data.get('apiary_temporary_use')['id'])
                apiary_temporary_use_data = request.data.get('apiary_temporary_use')
                update_proposal_apiary_temporary_use(apiary_temporary_use_obj, apiary_temporary_use_data, viewset.action)

                if viewset.action == 'submit':
                    proposal_obj.processing_status = Proposal.PROCESSING_STATUS_WITH_ASSESSOR
                    proposal_obj.customer_status = Proposal.CUSTOMER_STATUS_WITH_ASSESSOR
                    proposal_obj.documents.all().update(can_delete=False)
                    #proposal.required_documents.all().update(can_delete=False)
                    proposal_obj.save()

                # return redirect(reverse('external-proposal-temporary-use-submit-success', kwargs={'proposal_pk': proposal_obj.id}))

            # save/update any additonal special propoerties here
            proposal_obj.title = proposal_obj.proposal_apiary.title if hasattr(proposal_obj, 'proposal_apiary') else proposal_obj.title
            proposal_obj.save()
        except Exception as e:
            raise


def get_local_date(date_string):
    if date_string:
        try:
            date_utc = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            date_utc = datetime.strptime(date_string, '%Y-%m-%d')
        date_utc = date_utc.replace(tzinfo=pytz.UTC)
        date_wa = date_utc.astimezone(pytz.timezone(TIME_ZONE))
        return date_wa
    return None


def save_checklist_answers(checklist_role, checklist_answers=None):
    if checklist_answers and checklist_role == 'referrer':
        for referral_answers in checklist_answers:
            for ref_answer in referral_answers.get('referral_data'):
                r_ans = ApiaryChecklistAnswer.objects.get(id=ref_answer['id'])
                if ref_answer.get('question', {}).get('answer_type') == 'free_text':
                    r_ans.text_answer = ref_answer['text_answer']
                elif ref_answer.get('question', {}).get('answer_type') == 'yes_no':
                    r_ans.answer = ref_answer['answer']
                r_ans.save()
    #elif checklist_answers and checklist_role == 'assessor':
    else:
        for new_answer in checklist_answers:
            ans = ApiaryChecklistAnswer.objects.get(id=new_answer['id'])
            if new_answer.get('question', {}).get('answer_type') == 'free_text':
                ans.text_answer = new_answer['text_answer']
            elif new_answer.get('question', {}).get('answer_type') == 'yes_no':
                ans.answer = new_answer['answer']
            ans.save()


def update_proposal_apiary_temporary_use(temp_use_obj, temp_use_data, action):
    temp_use_data['from_date'] = convert_moment_str_to_python_datetime_obj(temp_use_data['from_date']).date() if temp_use_data['from_date'] else None
    temp_use_data['to_date'] = convert_moment_str_to_python_datetime_obj(temp_use_data['to_date']).date() if temp_use_data['to_date'] else None

    serializer = ProposalApiaryTemporaryUseSerializer(temp_use_obj, data=temp_use_data, context={'action': action})
    serializer.is_valid(raise_exception=True)
    patu = serializer.save()

    # Update TemporaryUseApiarySite
    num_of_sites = 0
    for item in temp_use_data['temporary_use_apiary_sites']:
        # Store all the apiary sites regardless of the selection status
        item['selected'] = item['apiary_site']['checked']
        tuas_obj = TemporaryUseApiarySite.objects.get(id=item['id'])

        serializer = TemporaryUseApiarySiteSerializer(tuas_obj, data=item)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Calculate the numbe of sites selected
        if item['selected']:
            num_of_sites += 1

    if action == 'submit':
        field_errors = {}
        non_field_errors = []

        for item in temp_use_data['temporary_use_apiary_sites']:
            if item['apiary_site']['checked']:
                # apiary_site = ApiarySite.objects.get(id=item['apiary_site']['id'])
                # valid, details = apiary_site.period_valid_for_temporary_use((temp_use_data['from_date'], temp_use_data['to_date']))
                valid, details = temp_use_obj.period_valid_for_temporary_use((temp_use_data['from_date'], temp_use_data['to_date']))
                if not valid:
                    if details['reason'] == 'overlap_existing':
                        non_field_errors.append('Temporary use period you submitted: {} to {} overlaps with the existing temporary use period: {} to {} for the apiary site: {}.'.format(
                            temp_use_data['from_date'], temp_use_data['to_date'], details['period']['from_date'], details['period']['to_date'], details['apiary_site'].id
                        ))
                        break
                    elif details['reason'] == 'out_of_range_of_licence':
                        non_field_errors.append('Temporary use period you submitted: {} to {} is out of range of the period of validity of the licence: {} to {}.'.format(
                            temp_use_data['from_date'], temp_use_data['to_date'], details['period']['from_date'], details['period']['to_date']
                        ))
                        break
                    else:
                        pass
                        # Should not reach here

        if not num_of_sites > 0:
            non_field_errors.append('At least one apiary site must be selected.')
        if not temp_use_obj.proposal.deed_poll_documents.all().count() > 0:
            non_field_errors.append('Deed poll document is required.')

        if field_errors:
            raise serializers.ValidationError(field_errors)
        if non_field_errors:
            raise serializers.ValidationError(non_field_errors)


    # if not temp_use_data['from_date']:
        #     non_field_errors.append('From date must be entered')
        # if not temp_use_data['to_date']:
        #     non_field_errors.append('To date must be entered')



def save_proponent_data_disturbance(instance,request,viewset):
    with transaction.atomic():
        try:
            lookable_fields = ['isTitleColumnForDashboard','isActivityColumnForDashboard','isRegionColumnForDashboard']

            extracted_fields,special_fields, add_info_applicant, refresh_timestamp = create_data_from_form(instance.schema, request.POST, request.FILES, special_fields=lookable_fields)
            instance.data = extracted_fields

            form_data=json.loads(request.POST['schema'])
            sub_activity_level1=form_data.get('sub_activity_level1')

            logger.info("Region: {}, Activity: {}".format(special_fields.get('isRegionColumnForDashboard',None), special_fields.get('isActivityColumnForDashboard',None)))

            data1 = {
                #'region': special_fields.get('isRegionColumnForDashboard',None),
                'title': special_fields.get('isTitleColumnForDashboard',None),
                'activity': special_fields.get('isActivityColumnForDashboard',None),

                'data': extracted_fields,
                'processing_status': instance.PROCESSING_STATUS_CHOICES[1][0] if instance.processing_status == 'temp' else instance.processing_status,
                'customer_status': instance.PROCESSING_STATUS_CHOICES[1][0] if instance.processing_status == 'temp' else instance.customer_status,
                # 'lodgement_sequence': 1 if instance.lodgement_sequence == 0 else instance.lodgement_sequence,

            }
            data = {
                #'region': special_fields.get('isRegionColumnForDashboard',None),
                'title': special_fields.get('isTitleColumnForDashboard',None),

                'data': extracted_fields,
                'add_info_applicant': add_info_applicant,
                'refresh_timestamp': refresh_timestamp,
                'processing_status': instance.PROCESSING_STATUS_CHOICES[1][0] if instance.processing_status == 'temp' else instance.processing_status,
                'customer_status': instance.PROCESSING_STATUS_CHOICES[1][0] if instance.processing_status == 'temp' else instance.customer_status,
                # 'lodgement_sequence': 1 if instance.lodgement_sequence == 0 else instance.lodgement_sequence,
                'activity': form_data.get('activity',None),
                'region': form_data.get('region',None),
                'district': form_data.get('district',None),
                'sub_activity_level1': form_data.get('sub_activity_level1',None),
                'sub_activity_level2': form_data.get('sub_activity_level2',None),
                'management_area': form_data.get('management_area',None),
                'approval_level': form_data.get('approval_level',None),

            }

            serializer = SaveProposalSerializer(instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            viewset.perform_update(serializer)
            instance.log_user_action(ProposalUserAction.ACTION_SAVE_APPLICATION.format(instance.lodgement_number), request)

            # Save Documents
        #            for f in request.FILES:
        #                try:
        #                    #document = instance.documents.get(name=str(request.FILES[f]))
        #                    document = instance.documents.get(input_name=f)
        #                except ProposalDocument.DoesNotExist:
        #                    document = instance.documents.get_or_create(input_name=f)[0]
        #                document.name = str(request.FILES[f])
        #                if document._file and os.path.isfile(document._file.path):
        #                    os.remove(document._file.path)
        #                document._file = request.FILES[f]
        #                document.save()

        #            for f in request.FILES:
        #                try:
        #                   document = instance.documents.get(input_name=f, name=request.FILES[f].name)
        #                except ProposalDocument.DoesNotExist:
        #                   document = instance.documents.get_or_create(input_name=f, name=request.FILES[f].name)[0]
        #                document._file = request.FILES[f]
        #                document.save()

        # End Save Documents
        except:
            raise


def save_assessor_data(instance,request,viewset):
    with transaction.atomic():
        try:
            lookable_fields = ['isTitleColumnForDashboard','isActivityColumnForDashboard','isRegionColumnForDashboard']
            extracted_fields,special_fields,assessor_data,comment_data, add_info_assessor = create_data_from_form(
                instance.schema, request.POST, request.FILES,special_fields=lookable_fields,assessor_data=True)

            logger.info("ASSESSOR DATA - Region: {}, Activity: {}".format(special_fields.get('isRegionColumnForDashboard',None), special_fields.get('isActivityColumnForDashboard',None)))
            data = {
                'data': extracted_fields,
                'assessor_data': assessor_data,
                'comment_data': comment_data,
                'add_info_assessor': add_info_assessor,
            }
            serializer = SaveProposalSerializer(instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            viewset.perform_update(serializer)
            # Save Documents
            for f in request.FILES:
                try:
                    #document = instance.documents.get(name=str(request.FILES[f]))
                    document = instance.documents.get(input_name=f)
                except ProposalDocument.DoesNotExist:
                    document = instance.documents.get_or_create(input_name=f)[0]
                document.name = str(request.FILES[f])
                if document._file and os.path.isfile(document._file.path):
                    os.remove(document._file.path)
                document._file = request.FILES[f]
                document.save()
            # End Save Documents
            instance.log_user_action(ProposalUserAction.ACTION_SAVE_APPLICATION.format(instance.lodgement_number), request)
        except:
            raise


def save_apiary_assessor_data(instance,request,viewset):
    with transaction.atomic():
        try:
            serializer = SaveProposalSerializer(instance, request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            viewset.perform_update(serializer)
            # Save Documents
            for f in request.FILES:
                try:
                    #document = instance.documents.get(name=str(request.FILES[f]))
                    document = instance.documents.get(input_name=f)
                except ProposalDocument.DoesNotExist:
                    document = instance.documents.get_or_create(input_name=f)[0]
                document.name = str(request.FILES[f])
                if document._file and os.path.isfile(document._file.path):
                    os.remove(document._file.path)
                document._file = request.FILES[f]
                document.save()
            # End Save Documents
            # save assessor checklist answers
            try:
                schema = request.data.get('schema')
            except:
                schema = request.POST.get('schema')

            sc = json.loads(schema) if schema else {}

            proposal_apiary_data = sc.get('proposal_apiary')
            if proposal_apiary_data:
                save_checklist_answers('assessor', proposal_apiary_data.get('assessor_checklist_answers'))
                save_checklist_answers('assessor', proposal_apiary_data.get('assessor_checklist_answers_per_site'))
                save_checklist_answers('assessor', proposal_apiary_data.get('site_transfer_assessor_checklist_answers'))
                save_checklist_answers('assessor', proposal_apiary_data.get('site_transfer_assessor_checklist_answers_per_site'))
            # referrer checklist answers
            try:
                referrer_checklist_answers_str = request.data.get('referrer_checklist_answers')
            except:
                referrer_checklist_answers_str = request.POST.get('referrer_checklist_answers')
            referrer_checklist_answers = json.loads(referrer_checklist_answers_str) if referrer_checklist_answers_str else []
            if referrer_checklist_answers:
                save_checklist_answers('referrer', referrer_checklist_answers)
            # referrer checklist answers per site
            try:
                referrer_checklist_answers_per_site_str = request.data.get('referrer_checklist_answers_per_site')
            except:
                referrer_checklist_answers_per_site_str = request.POST.get('referrer_checklist_answers_per_site')
            referrer_checklist_answers_per_site = json.loads(referrer_checklist_answers_per_site_str) if referrer_checklist_answers_per_site_str else []
            if referrer_checklist_answers_per_site:
                save_checklist_answers('referrer', referrer_checklist_answers_per_site)
            # site transfer referrer checklist answers
            try:
                site_transfer_referrer_checklist_answers_str = request.data.get('site_transfer_referrer_checklist_answers')
            except:
                site_transfer_referrer_checklist_answers_str = request.POST.get('site_transfer_referrer_checklist_answers')
            site_transfer_referrer_checklist_answers = json.loads(referrer_checklist_answers_str) if referrer_checklist_answers_str else []
            if site_transfer_referrer_checklist_answers:
                save_checklist_answers('referrer', site_transfer_referrer_checklist_answers)
            # site transfer referrer checklist answers per site
            try:
                site_transfer_referrer_checklist_answers_per_site_str = request.data.get('site_transfer_referrer_checklist_answers_per_site')
            except:
                site_transfer_referrer_checklist_answers_per_site_str = request.POST.get('site_transfer_referrer_checklist_answers_per_site')
            site_transfer_referrer_checklist_answers_per_site = json.loads(referrer_checklist_answers_per_site_str) if referrer_checklist_answers_per_site_str else []
            if site_transfer_referrer_checklist_answers_per_site:
                save_checklist_answers('referrer', site_transfer_referrer_checklist_answers_per_site)

            instance.log_user_action(ProposalUserAction.APIARY_ACTION_SAVE_APPLICATION.format(instance.lodgement_number), request)
        except:
            raise

def proposal_submit_apiary(proposal, request):
    with transaction.atomic():
        if proposal.can_user_edit:
            proposal.submitter = request.user
            #proposal.lodgement_date = datetime.datetime.strptime(timezone.now().strftime('%Y-%m-%d'),'%Y-%m-%d').date()
            proposal.lodgement_date = timezone.now()
            proposal.training_completed = True
            if (proposal.amendment_requests):
                qs = proposal.amendment_requests.filter(status = "requested")
                if (qs):
                    for q in qs:
                        q.status = 'amended'
                        q.save()

            # Create a log entry for the proposal
            proposal.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(proposal.lodgement_number), request)
            # Create a log entry for the organisation
            #proposal.applicant.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(proposal.id),request)
            applicant_field=getattr(proposal, proposal.applicant_field)
            applicant_field.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(proposal.lodgement_number), request)

            ret1 = send_submit_email_notification(request, proposal)
            ret2 = send_external_submit_email_notification(request, proposal)

            #proposal.save_form_tabs(request)
            if ret1 and ret2:
                proposal.processing_status = Proposal.PROCESSING_STATUS_WITH_ASSESSOR
                proposal.customer_status = Proposal.CUSTOMER_STATUS_WITH_ASSESSOR
                proposal.documents.all().update(can_delete=False)
                #proposal.required_documents.all().update(can_delete=False)
                proposal.save()
            else:
                raise ValidationError('An error occurred while submitting proposal (Submit email notifications failed)')

            if proposal.application_type.name == 'Apiary':
                for question in ApiaryChecklistQuestion.objects.filter(
                        checklist_type='apiary',
                        checklist_role='assessor'
                        ):
                    new_answer = ApiaryChecklistAnswer.objects.get_or_create(proposal = proposal.proposal_apiary,
                                                                               question = question)
                # add questions per site
                for question in ApiaryChecklistQuestion.objects.filter(
                        checklist_type='apiary_per_site',
                        checklist_role='assessor'
                        ):
                    # site is an ApiarySiteOnProposal obj
                    for site in proposal.proposal_apiary.get_relations():
                        new_answer = ApiaryChecklistAnswer.objects.get_or_create(proposal = proposal.proposal_apiary,
                                                                                   question = question,
                                                                                   apiary_site=site.apiary_site)
            elif proposal.application_type.name == 'Site Transfer':
                for question in ApiaryChecklistQuestion.objects.filter(
                        checklist_type='site_transfer',
                        checklist_role='assessor'
                        ):
                    new_answer = ApiaryChecklistAnswer.objects.get_or_create(proposal = proposal.proposal_apiary,
                                                                               question = question)
                # add questions per site
                for question in ApiaryChecklistQuestion.objects.filter(
                        checklist_type='site_transfer_per_site',
                        checklist_role='assessor'
                        ):
                    # site is an ApiarySiteOnApproval obj
                    for site in proposal.proposal_apiary.get_relations():
                        new_answer = ApiaryChecklistAnswer.objects.get_or_create(proposal = proposal.proposal_apiary,
                                                                                   question = question,
                                                                                   apiary_site=site.apiary_site)

            return proposal

        else:
            raise ValidationError('You can\'t edit this proposal at this moment')


def clone_proposal_with_status_reset(proposal):
    with transaction.atomic():
        try:
            proposal.customer_status = 'draft'
            proposal.processing_status = 'draft'
            proposal.assessor_data = {}
            proposal.comment_data = {}

            #proposal.id_check_status = 'not_checked'
            #proposal.character_check_status = 'not_checked'
            #proposal.compliance_check_status = 'not_checked'
            #Sproposal.review_status = 'not_reviewed'

            proposal.lodgement_number = ''
            proposal.lodgement_sequence = 0
            proposal.lodgement_date = None

            proposal.assigned_officer = None
            proposal.assigned_approver = None

            proposal.approval = None

            original_proposal_id = proposal.id

            proposal.previous_proposal = proposal.objects.get(id=original_proposal_id)

            proposal.id = None

            #proposal.save(no_revision=True)
            proposal.save()


            # clone documents
            for proposal_document in ProposalDocument.objects.filter(proposal=original_proposal_id):
                proposal_document.proposal = proposal
                proposal_document.id = None
                proposal_document.save()

            return proposal
        except:
            raise

help_site_url='site_url:/help/disturbance/user'
help_site_assessor_url='site_url:/help/disturbance/assessor'

def create_richtext_help(question, name):
    global richtext
    global richtext_assessor
    
    if question.help_text_url and question.help_text:
       
        # richtext += u'<h1><a id="{0}" name="{0}"> {1} </a></h1>'.format(name, question.question)
        richtext += u'<h1 style="text-align:justify"><span style="font-size:14px"><a id="{0}" name="{0}"><span style="color:#2980b9"> <strong> {1}</strong></span></a></span></h1>'.format(name, question.question)
        richtext += question.help_text
        richtext += u'<p>&nbsp;</p>'

    if question.help_text_assessor_url and question.help_text_assessor:
       
        # richtext_assessor += u'<h1><a id="{0}" name="{0}"> {1} </a></h1>'.format(name, question.question)
        richtext_assessor += u'<h1 style="text-align:justify"><span style="font-size:14px"><a id="{0}" name="{0}"><span style="color:#2980b9"> <strong> {1}</strong></span></a></span></h1>'.format(name, question.question)
        richtext_assessor += question.help_text_assessor
        richtext_assessor += u'<p>&nbsp;</p>'

    return richtext

def create_helppage_object(proposal_type, help_type=HelpPage.HELP_TEXT_EXTERNAL):
    """
    Create a new HelpPage object, with latest help_text/label anchors defined in the latest ProposalType.schema
    """
    application_type=proposal_type.name
    try:
        application_type_id = ApplicationType.objects.get(name=application_type).id
    except Exception as e:
        print('application type: {} does not exist, maybe!'.format(application_type, e))

    try:
        help_page = HelpPage.objects.filter(application_type_id=application_type_id, help_type=help_type).latest('version')
        next_version = help_page.version + 1
    except Exception as e:
        next_version = 1

    help_type_assessor=HelpPage.HELP_TEXT_INTERNAL
    try:
        help_page_assessor = HelpPage.objects.filter(application_type_id=application_type_id, help_type=help_type_assessor).latest('version')
        next_version_assessor = help_page_assessor.version + 1
    except Exception as e:
        next_version_assessor = 1
    
    HelpPage.objects.create(application_type_id=application_type_id, help_type=help_type, version=next_version, content=richtext)
    HelpPage.objects.create(application_type_id=application_type_id, help_type=help_type_assessor, version=next_version_assessor, content=richtext_assessor)


def get_options(section_question, question):
    options=[]
    special_types=['radiobuttons', 'multi-select',]
    if question.option.count()>0:
        for op in question.option.all().order_by('-disturbance_masterlistquestion_option.id'):
            op_dict={
                'label': op.label,
                'value': op.label.replace(" ","").lower(),
            }
            options.append(op_dict)
    #For multi-select type questions, the isRequired flag goes to the first option dict instead of question dict
    if 'isRequired' in section_question.get_tag_list() and question.answer_type in special_types:
        if options:
            options[0]['isRequired']='true'
    return options

def get_condition_children(question,section, parent_name=''):
    conditions={}
    options=question.option.all().order_by('-disturbance_masterlistquestion_option.id')
    special_types=['checkbox',]
    group_types=['checkbox', 'radiobuttons', 'multi-select']
    option_count=0
    for op in options:
        condition_questions=SectionQuestion.objects.filter(section=section,parent_question=question,parent_answer=op).order_by('order')
        if condition_questions:
            option_section=[]
            option_children=[]
            condition_question_count=1
            for q in condition_questions:
                #question_name=parent_name+'-'+op.label+condition_question_count
                #question_name='{}-{}{}'.format(parent_name,op.label,condition_question_count)
                question_name='{}-{}{}'.format(parent_name,op.label.replace(" ",""),condition_question_count)
                child={
                    'name': question_name,
                    'type': q.question.answer_type,
                    'label': q.question.question,
                }
                if q.question.answer_type in special_types:
                        q_option_children=get_checkbox_option_children(q, q.question, section, question_name)
                        child['children']=q_option_children
                        child['type']='group'
                else:
                    if q.question.option.count()>0:
                        q_options= get_options(q,q.question)
                        child['options']=q_options
                    if q.question.children_question.exists():
                        q_conditions=get_condition_children(q.question, section, question_name)
                        child['conditions']=q_conditions
                if q.tag:
                    for t in q.tag:
                        if t=='isRequired':
                            if q.question.answer_type not in group_types:
                                child[t]='true'
                        else:
                            child[t]='true'
                        #child[t]='true'
                if q.question.help_text_url:
                    child['help_text_url']='{0}/anchor={1}'.format(help_site_url, question_name)
                if q.question.help_text_assessor_url:
                    child['help_text_assessor_url']='{0}/anchor={1}'.format(help_site_assessor_url, question_name)
                create_richtext_help(q.question, question_name)
                option_children.append(child)
                condition_question_count+=1
            #section_group_name=parent_name+'-'+op.label+'Group'
            section_group_name=parent_name+'-'+op.label.replace(" ","")+'Group'
            option_section_dict={
                'name':section_group_name,
                'type': 'group',
                'label':'',
                'children': option_children
            }
            option_section.append(option_section_dict)
            conditions[op.label.replace(" ","").lower()]=option_section
            option_count+=1
    return conditions


def get_checkbox_option_children(section_question,question,section, parent_name=''):
    conditions={}
    options=question.option.all().order_by('-disturbance_masterlistquestion_option.id')
    options_list=[]
    special_types=['checkbox',]
    group_types=['checkbox', 'radiobuttons', 'multi-select']
    option_count=0
    for op in options:
        #op_name=parent_name+'-'+option_count
        op_name='{}-{}'.format(parent_name,option_count)
        op_dict={
                #'name': op.label,#function generated name
                'name': op_name,
                'label': op.label,
                'type': 'checkbox',
                'group': parent_name #function generated name of parent question
        }
        condition_questions=SectionQuestion.objects.filter(section=section,parent_question=question,parent_answer=op).order_by('order')
        if condition_questions:
            option_section=[]
            option_children=[]
            condition_question_count=1
            for q in condition_questions:
                #question_name=op_name+'-On-'+condition_question_count
                question_name='{}-On-{}'.format(op_name,condition_question_count)
                child={
                    'name': question_name,
                    'type': q.question.answer_type,
                    'label': q.question.question,
                }
                if q.question.answer_type in special_types:
                        q_option_children=get_checkbox_option_children(q,q.question, section, question_name)
                        child['children']=q_option_children
                        child['type']='group'
                else:
                    if q.question.option.count()>0:
                        q_options= get_options(q,q.question)
                        child['options']=q_options
                    if q.question.children_question.exists():
                        q_conditions=get_condition_children(q.question, section, question_name)
                        child['conditions']=q_conditions

                if q.tag:
                    for t in q.tag:
                        #child[t]='true'
                        if t=='isRequired':
                            if q.question.answer_type not in group_types:
                                child[t]='true'
                        else:
                            child[t]='true'
                if q.question.help_text_url:
                    child['help_text_url']='{0}/anchor={1}'.format(help_site_url, question_name)
                if q.question.help_text_assessor_url:
                    child['help_text_assessor_url']='{0}/anchor={1}'.format(help_site_assessor_url, question_name)
                create_richtext_help(q.question, question_name)
                option_children.append(child)
                condition_question_count+=1
            section_group_name=op_name+'-OnGroup'
            option_section_dict={
                'name':section_group_name,
                'type': 'group',
                'label':'',
                'children': option_children
            }
            option_section.append(option_section_dict)
            conditions['on']=option_section
            op_dict['conditions']=conditions
        options_list.append(op_dict)
        option_count+=1
    if 'isRequired' in section_question.get_tag_list():
        if options_list:
            options_list[0]['isRequired']='true'
    return options_list

def get_options_new(section_question, question):
    options=[]
    special_types=['radiobuttons', 'multi-select',]
    if len(section_question.get_options()) > 0:
        for op in section_question.get_options():
            op_dict = {
                    'label': op['label'],
                    'value': op['label'].replace(" ", "").lower(),
                }
            options.append(op_dict)
    #For multi-select type questions, the isRequired flag goes to the first option dict instead of question dict
    if 'isRequired' in section_question.get_tag_list() and question.answer_type in special_types:
        if options:
            options[0]['isRequired']='true'
    return options

def get_condition_children_new(question,section, parent_name=''):
    conditions={}
    # options=question.option.all().order_by('-disturbance_masterlistquestion_option.id')
    options = []
    special_types=['checkbox',]
    group_types=['checkbox', 'radiobuttons', 'multi-select']
    option_count=0
    if len(question.get_options()) > 0:
            for op in question.get_options():
                op_dict = {
                    'label': op.label,
                    'value': op.label.replace(" ", "").lower(),
                    'id': op.value,
                }
                options.append(op_dict)
    for op in options:
        condition_questions=SectionQuestion.objects.filter(section=section,parent_question=question,parent_answer=op['id']).order_by('order')
        if condition_questions:
            option_section=[]
            option_children=[]
            condition_question_count=1
            for q in condition_questions:
                #question_name=parent_name+'-'+op.label+condition_question_count
                question_name='{}-{}{}'.format(parent_name,op['label'].replace(" ", ""),condition_question_count)
                child={
                    'name': question_name,
                    'type': q.question.answer_type,
                    'label': q.question.question,
                }
                if q.question.answer_type in special_types:
                        q_option_children=get_checkbox_option_children_new(q, q.question, section, question_name)
                        child['children']=q_option_children
                        child['type']='group'
                else:
                    if len(q.question.get_options()) > 0:
                        q_options= get_options_new(q,q.question)
                        child['options']=q_options
                    if q.question.children_question.exists():
                        q_conditions=get_condition_children_new(q.question, section, question_name)
                        child['conditions']=q_conditions
                if q.tag:
                    for t in q.tag:
                        if t=='isRequired':
                            if q.question.answer_type not in group_types:
                                child[t]='true'
                        else:
                            child[t]='true'
                        #child[t]='true'
                if q.question.help_text_url:
                    child['help_text_url']='{0}/anchor={1}'.format(help_site_url, question_name)
                if q.question.help_text_assessor_url:
                    child['help_text_assessor_url']='{0}/anchor={1}'.format(help_site_assessor_url, question_name)
                create_richtext_help(q.question, question_name)
                option_children.append(child)
                condition_question_count+=1
            section_group_name=parent_name+'-'+op['label'].replace(" ", "")+'Group'
            option_section_dict={
                'name':section_group_name,
                'type': 'group',
                'label':'',
                'children': option_children
            }
            option_section.append(option_section_dict)
            conditions[op['label'].replace(" ","").lower()]=option_section
            option_count+=1
    return conditions


def get_checkbox_option_children_new(section_question,question,section, parent_name=''):
    conditions={}
    # options=question.option.all().order_by('-disturbance_masterlistquestion_option.id')
    options = []
    options_list=[]
    special_types=['checkbox',]
    group_types=['checkbox', 'radiobuttons', 'multi-select']
    option_count=0
    if len(question.get_options()) > 0:
            for op in question.get_options():
                op_dict = {
                    'label': op.label,
                    'value': op.label.replace(" ", "").lower(),
                    'id': op.value,
                }
                options.append(op_dict)
    for op in options:
        conditions={}
        #op_name=parent_name+'-'+option_count
        op_name='{}-{}'.format(parent_name,option_count)
        op_dict={
                #'name': op.label,#function generated name
                'name': op_name,
                'label': op['label'],
                'type': 'checkbox',
                'group': parent_name #function generated name of parent question
        }
        condition_questions=SectionQuestion.objects.filter(section=section,parent_question=question,parent_answer=op['id']).order_by('order')
        if condition_questions:
            option_section=[]
            option_children=[]
            condition_question_count=1
            for q in condition_questions:
                #question_name=op_name+'-On-'+condition_question_count
                question_name='{}-On-{}'.format(op_name,condition_question_count)
                child={
                    'name': question_name,
                    'type': q.question.answer_type,
                    'label': q.question.question,
                }
                if q.question.answer_type in special_types:
                        q_option_children=get_checkbox_option_children_new(q,q.question, section, question_name)
                        child['children']=q_option_children
                        child['type']='group'
                else:
                    if len(q.question.get_options()) > 0:
                        q_options= get_options_new(q,q.question)
                        child['options']=q_options
                    if q.question.children_question.exists():
                        q_conditions=get_condition_children_new(q.question, section, question_name)
                        child['conditions']=q_conditions

                if q.tag:
                    for t in q.tag:
                        #child[t]='true'
                        if t=='isRequired':
                            if q.question.answer_type not in group_types:
                                child[t]='true'
                        else:
                            child[t]='true'
                if q.question.help_text_url:
                    child['help_text_url']='{0}/anchor={1}'.format(help_site_url, question_name)
                if q.question.help_text_assessor_url:
                    child['help_text_assessor_url']='{0}/anchor={1}'.format(help_site_assessor_url, question_name)
                create_richtext_help(q.question, question_name)
                option_children.append(child)
                condition_question_count+=1
            section_group_name=op_name+'-OnGroup'
            option_section_dict={
                'name':section_group_name,
                'type': 'group',
                'label':'',
                'children': option_children
            }
            option_section.append(option_section_dict)
            conditions['on']=option_section
            op_dict['conditions']=conditions
        options_list.append(op_dict)
        option_count+=1
    if 'isRequired' in section_question.get_tag_list():
        if options_list:
            options_list[0]['isRequired']='true'
    return options_list

def generate_schema_original(proposal_type, request):
    section_list=ProposalTypeSection.objects.filter(proposal_type=proposal_type).order_by('index')
    section_count=0
    schema=[]
    special_types=['checkbox',]
    #'isRequired' tag for following types is added to first option dict instead of question.
    group_types=['checkbox', 'radiobuttons', 'multi-select']
    global richtext
    global richtext_assessor
    global help_site_url, help_site_assessor_url
    richtext = u''
    richtext_assessor=u''
    help_site_url='site_url:/help/{}/user'.format(proposal_type.name)
    help_site_assessor_url='site_url:/help/{}/assessor'.format(proposal_type.name)
    for section in section_list:
        section_dict={
            'name': '{}{}'.format(section.section_label.replace(" ",""), section_count),
            'type': 'section',
            'label': section.section_label,
        }
        section_children=[]
        section_questions=SectionQuestion.objects.filter(section=section,parent_question__isnull=True,parent_answer__isnull=True).order_by('order')
        if section_questions:
            sq_count=0
            for sq in section_questions:
                #sq_name='Section'+section_count+'-'+sq_count
                sq_name='Section{}-{}'.format(section_count,sq_count)
                sc={
                    # 'name': sq.question.name,
                    'name': sq_name,
                    'type': sq.question.answer_type,
                    'label': sq.question.question,                    
                }
                if sq.question.answer_type in special_types:
                    sq_option_children=get_checkbox_option_children(sq,sq.question, section,sq_name)
                    sc['children']=sq_option_children
                    sc['type']='group'
                else:
                    if sq.question.option.count()>0:
                        sq_options= get_options(sq,sq.question)
                        sc['options']=sq_options
                    if sq.question.children_question.exists():
                        sq_children=get_condition_children(sq.question,section, sq_name)
                        sc['conditions']=sq_children
                if sq.tag:
                    for t in sq.tag:
                        if t=='isRequired':
                            if sq.question.answer_type not in group_types:
                                sc[t]='true'
                        else:
                            sc[t]='true'
                if sq.question.help_text_url:
                    sc['help_text_url']='{0}/anchor={1}'.format(help_site_url, sq_name)
                if sq.question.help_text_assessor_url:
                    sc['help_text_assessor_url']='{0}/anchor={1}'.format(help_site_assessor_url, sq_name)
                create_richtext_help(sq.question, sq_name) 
                section_children.append(sc)
                sq_count+=1
        if section_children:
            section_dict['children']= section_children
        section_count+=1
        schema.append(section_dict)
    import json
    new_schema=json.dumps(schema)
    new_Schema_return=json.loads(new_schema)
    if request.method=='POST':
        create_helppage_object(proposal_type)
    return new_Schema_return


def generate_schema(proposal_type, request):
    section_list=ProposalTypeSection.objects.filter(proposal_type=proposal_type).order_by('index')
    section_count=0
    schema=[]
    special_types=['checkbox',]
    select_types = ['select', 'multi-select']
    #'isRequired' tag for following types is added to first option dict instead of question.
    group_types=['checkbox', 'radiobuttons', 'multi-select']
    global richtext
    global richtext_assessor
    global help_site_url, help_site_assessor_url
    richtext = u''
    richtext_assessor=u''
    help_site_url='site_url:/help/{}/user'.format(proposal_type.name)
    help_site_assessor_url='site_url:/help/{}/assessor'.format(proposal_type.name)
    for section in section_list:
        section_name=section.section_label.replace(" ","")
        section_name=section_name.replace(".","")
        section_name=section_name.replace(",","")
        section_dict={
            # 'name': '{}{}'.format(section.section_label.replace(" ",""), section_count),
            'name': '{}{}'.format(section_name, section_count),
            'type': 'section',
            'label': section.section_label,
        } 
        section_children=[]
        section_questions=SectionQuestion.objects.filter(section=section,parent_question__isnull=True,parent_answer__isnull=True).order_by('order')
        if section_questions:
            sq_count=0
            for sq in section_questions:
                #sq_name='Section'+section_count+'-'+sq_count
                sq_name='Section{}-{}'.format(section_count,sq_count)
                sc={
                    # 'name': sq.question.name,
                    'name': sq_name,
                    'type': sq.question.answer_type,
                    'label': sq.question.question,                    
                }
                if sq.question.answer_type in special_types:
                    sq_option_children=get_checkbox_option_children_new(sq,sq.question, section,sq_name)
                    sc['children']=sq_option_children
                    sc['type']='group'
                elif sq.question.answer_type in select_types:
                    '''
                        NOTE: Select type option are defaulted from Masterlist
                        not from the SectionQuestion. Conditions are NOT added.
                        '''
                    if len(sq.question.get_options()) > 0:
                        #sq_options= get_options(sq,sq.question)
                        opts = [
                                {
                                    'label': o.label,
                                    'value': o.label.replace(" ", "").lower(),
                                } for o in sq.question.get_options()
                            ]
                        sq.set_property_cache_options(opts)
                        sq_options = get_options_new(
                                sq, sq.question
                            )
                        sc['options']=sq_options
                    if sq.question.children_question.exists():
                        sq_children=get_condition_children_new(sq.question,section, sq_name)
                        sc['conditions']=sq_children

                else:
                    if len(sq.question.get_options()) > 0:
                        sq_options = get_options_new(
                                sq, sq.question
                            )
                        sc['options']=sq_options
                    if sq.question.children_question.exists():
                        sq_children=get_condition_children_new(sq.question,section, sq_name)
                        sc['conditions']=sq_children

                if sq.tag:
                    for t in sq.tag:
                        if t=='isRequired':
                            if sq.question.answer_type not in group_types:
                                sc[t]='true'
                        else:
                            sc[t]='true'
                if sq.question.help_text_url:
                    sc['help_text_url']='{0}/anchor={1}'.format(help_site_url, sq_name)
                if sq.question.help_text_assessor_url:
                    sc['help_text_assessor_url']='{0}/anchor={1}'.format(help_site_assessor_url, sq_name)
                create_richtext_help(sq.question, sq_name) 
                section_children.append(sc)
                sq_count+=1
        if section_children:
            section_dict['children']= section_children
        section_count+=1
        schema.append(section_dict)
    import json
    new_schema=json.dumps(schema)
    new_Schema_return=json.loads(new_schema)
    if request.method=='POST':
        create_helppage_object(proposal_type)
    return new_Schema_return            


# Populate data in Proposal using the CDDP configuration
def prefill_data_from_shape_original(schema ):
    data = {}
    
    try:
        for item in schema:
            data.update(_populate_data_from_item_original(item, 0, ''))
           
    except:
        traceback.print_exc()
    return [data]

def _populate_data_from_item_original(item, repetition, suffix, sqs_value=None):
    item_data = {}

    if 'name' in item:
        extended_item_name = item['name']
    else:
        raise Exception('Missing name in item %s' % item['label'])

    if 'children' not in item:
        if item['type'] =='checkbox':
            if sqs_value:
                for val in sqs_value:
                    if val==item['label']:
                        item_data[item['name']]='on'
        elif item['type'] == 'file':
            print('file item', item)
        else:
            try:
                if item['type'] == 'multi-select':
                    #Get value from SQS. Value should be an array of the correct options.
                    sqs_value=item['options'][1]['value']
                    sqs_value=[sqs_value]
                    if sqs_value:
                        item_data[item['name']]=[]
                    for val in sqs_value:
                        if item['options']:
                            for op in item['options']:
                                if val==op['value']:
                                    item_data[item['name']].append(op['value'])

                elif item['type'] == 'radiobuttons' or item['type'] == 'select' :
                    #Get value from SQS
                    sqs_value=item['options'][1]['value']
                    if item['options']:
                        for op in item['options']:
                            if sqs_value==op['value']:
                                item_data[item['name']]=op['value']
                                break
                else:
                    #All the other types e.g. textarea, text, date.
                    #This is where we can add API call to SQS to get the answer.
                    sqs_value="test"
                    item_data[item['name']]= sqs_value
                    #print(item)
                    #print('radiobuttons/ textarea/ text/ date etc item', item)
            except Exception as e:
                logger.error(e)

    else:
        if 'repetition' in item:
            item_data = generate_item_data_shape(extended_item_name,item,item_data,1,suffix)
        else:
            #item_data = generate_item_data_shape(extended_item_name, item, item_data,1,suffix)
            #Check if item has checkbox childer
            if check_checkbox_item(extended_item_name, item, item_data,1,suffix):
                #make a call to sqs for item
                sqs_values=['first']
                #pass sqs values as an attribute.
                item_data = generate_item_data_shape(extended_item_name, item, item_data,1,suffix, sqs_values)
            else:
                item_data = generate_item_data_shape(extended_item_name, item, item_data,1,suffix)


    if 'conditions' in item:
        for condition in list(item['conditions'].keys()):
            if condition==item_data[item['name']]:
                for child in item['conditions'][condition]:
                    item_data.update(_populate_data_from_item(child,  repetition, suffix))

    return item_data

def generate_item_data_shape_original(item_name,item,item_data,repetition,suffix, sqs_value=None):
    item_data_list = []
    for rep in range(0, repetition):
        child_data = {}
        for child_item in item.get('children'):
            child_data.update(_populate_data_from_item(child_item, 0,
                                                     '{}-{}'.format(suffix, rep), sqs_value))
            #print('child item in generate item data', child_item)
        item_data_list.append(child_data)

        item_data[item['name']] = item_data_list
    return item_data

def check_checkbox_item_original(item_name,item,item_data,repetition,suffix):
    checkbox_item=False
    for child_item in item.get('children'):
        if child_item['type']=='checkbox':
            checkbox_item=True        
    return checkbox_item

class PrefillData(object):
    """
    from disturbance.components.proposals.utils import PrefillData
    pr=PrefillData()
    pr.prefill_data_from_shape(p.schema)
    """

    def __init__(self, sqs_builder=None):
        self.sqs_builder=sqs_builder
        self.data={}
        self.layer_data=[]
        self.add_info_assessor={}

    def prefill_data_from_shape(self, schema):
        #data = {}
        
        try:
            for item in schema:
                self.data.update(self._populate_data_from_item(item, 0, ''))
               
        except:
            traceback.print_exc()
        return [self.data]

    def _populate_data_from_item(self, item, repetition, suffix, sqs_value=None):
        item_data = {}

        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            if item['type'] =='checkbox':
                if sqs_value:
                    for val in sqs_value:
                        if val==item['label']:
                            item_data[item['name']]='on'
                            item_layer_data={
                            'name': item['name'],
                            'layer_name': 'layer name',
                            'layer_updated': 'layer updated',
                            'new_layer_name': 'new layer name',
                            'new_layer_updated': 'new layer updated'
                            }
                            self.layer_data.append(item_layer_data)
            elif item['type'] == 'file':
                print('file item', item)
            else:
                    if item['type'] == 'multi-select':
                        #Get value from SQS. Value should be an array of the correct options.
                        #sqs_value=item['options'][1]['value']
                        #sqs_value=[sqs_value]
                        sqs_values = [self.sqs_builder.find(question=item['label'], answer=option['label'], widget_type=item['type']) for option in item['options']]
                        sqs_values = [i for i in sqs_values if i is not None] # drop None vlaues
                        
                        if sqs_values:
                            item_data[item['name']]=[]
                        for val in sqs_values:
                            if item['options']:
                                for op in item['options']:
                                    if val==op['value']:
                                        item_data[item['name']].append(op['value'])
                                        item_layer_data={
                                        'name': item['name'],
                                        'layer_name': 'layer name',
                                        'layer_updated': 'layer updated',
                                        'new_layer_name': 'new layer name',
                                        'new_layer_updated': 'new layer updated'
                                        }
                                        self.layer_data.append(item_layer_data)
                                        # add_info_asessor_item={
                                        #     'name': item['name'],
                                        #     'value': 'test'
                                        # }
                                        sqs_assessor_value='test'

                                        self.add_info_assessor[item['name']]= sqs_assessor_value

                    elif item['type'] == 'radiobuttons' or item['type'] == 'select' :
                        #Get value from SQS
                        #sqs_value=item['options'][1]['value']
                        sqs_values = [self.sqs_builder.find(question=item['label'], answer=option['label'], widget_type=item['type']) for option in item['options']]
                        sqs_values = [i for i in sqs_values if i is not None] # drop None vlaues
                        sqs_value = self.get_first_radiobutton(sqs_values) if item['type']=='radiobuttons' else ''.join(sqs_values)
                        if item['options']:
                            for op in item['options']:
                                #if sqs_value==op['value']:
                                if sqs_value==op['label']:
                                    item_data[item['name']]=op['value']
                                    item_layer_data={
                                        'name': item['name'],
                                        'layer_name': 'layer name',
                                        'layer_updated': 'layer updated',
                                        'new_layer_name': 'new layer name',
                                        'new_layer_updated': 'new layer updated'
                                    }
                                    self.layer_data.append(item_layer_data)
                                    break
                    else:
                        #All the other types e.g. textarea, text, date.
                        #This is where we can add API call to SQS to get the answer.
                        #sqs_value="test"
                        #sqs_value = [self.sqs_builder.find(question=item['label'], answer=option['label']) for option in item['options']]
                        sqs_value = self.sqs_builder.find(question=item['label'], answer='', widget_type='other')
                        item_data[item['name']]= sqs_value
                        #item_layer_data = self.update_layer_info(list)
                        item_layer_data={
                        'name': item['name'],
                        'layer_name': 'layer  name',
                        'layer_updated': 'layer updated',
                        'new_layer_name': 'new layer name',
                        'new_layer_updated': 'new layer updated'
                        }
                        self.layer_data.append(item_layer_data)
                        #sqs_assessor_value='test'
                        sqs_assessor_value = self.sqs_builder.find(question=item['label'], answer='', widget_type='other')
                        self.add_info_assessor[item['name']]= sqs_assessor_value
                        #print(item)
                        #print('radiobuttons/ textarea/ text/ date etc item', item)
        else:
            #sqs_values = []
            if 'repetition' in item:
                item_data = self.generate_item_data_shape(extended_item_name,item,item_data,1,suffix)
            else:
                #item_data = generate_item_data_shape(extended_item_name, item, item_data,1,suffix)
                #Check if item has checkbox childer
                if self.check_checkbox_item(extended_item_name, item, item_data,1,suffix):
                    #make a call to sqs for item
                    # 1. question      --> item['label']
                    # 2. checkbox text --> item['children'][0]['label']
                    # 3. request response for all checkbox's ie. send item['children'][all]['label']. 
                    #    SQS will return a list of checkbox's answersfound eg. ['National park', 'Nature reserve']
                    #sqs_values=['Nature reserve']
                    #if item['label'] == 
                    #sqs_values = sqs_query()['proponent_answer']
                    #sqs_value = ['Nature reserve',2]
                    sqs_values = [self.sqs_builder.find(question=item['label'], answer=child['label'], widget_type='checkbox') for child in item['children']]
                    sqs_values = [i for i in sqs_values if i is not None] # drop None vlaues
                    #pass sqs values as an attribute.
                    item_data = self.generate_item_data_shape(extended_item_name, item, item_data,1,suffix, sqs_values)
                else:
                    item_data = self.generate_item_data_shape(extended_item_name, item, item_data,1,suffix)


        if 'conditions' in item:
            for condition in list(item['conditions'].keys()):
                if condition==item_data[item['name']]:
                    for child in item['conditions'][condition]:
                        item_data.update(self._populate_data_from_item(child,  repetition, suffix))

        return item_data

    def generate_item_data_shape(self, item_name,item,item_data,repetition,suffix, sqs_value=None):
        item_data_list = []
        for rep in range(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self._populate_data_from_item(child_item, 0,
                                                         '{}-{}'.format(suffix, rep), sqs_value))
                #print('child item in generate item data', child_item)
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data

    def check_checkbox_item(self, item_name,item,item_data,repetition,suffix):
        checkbox_item=False
        for child_item in item.get('children'):
            if child_item['type']=='checkbox':
                checkbox_item=True        
        return checkbox_item

    def get_first_radiobutton(self, _list):
        """
        If SQS JSON object has multiple radiobuttons returned - select the one with highest priority (1,2,3 --> 1 is highest)
        """
        if not _list:
            return None
         
        tmp_dict = {}
        for i in _list:
            tmp_dict.update(i)
        return tmp_dict.get(min(tmp_dict.keys()))

    def update_layer_info(self, _list):
        return {
            'name': item['name'],
            'layer_name': 'layer name',
            'layer_updated': 'layer updated',
            'new_layer_name': 'new layer name',
            'new_layer_updated': 'new layer updated'
            }
        

def save_prefill_data(proposal):
    prefill_instance= PrefillData()
    try:
        prefill_data = prefill_instance.prefill_data_from_shape(proposal.schema)
        if prefill_data:
            proposal.data=prefill_data
            proposal.layer_data= prefill_instance.layer_data
            print(prefill_instance.add_info_assessor)
            proposal.add_info_assessor=prefill_instance.add_info_assessor
            proposal.save()
            return proposal
    except:
        raise


@traceback_exception_handler
def search_schema(proposal_id, question):
    ''' Checks if Question exists in proposal.schema

    Eg.
        from disturbance.components.proposals.utils import search_schema
        search_schema(proposal_id=1250, question='1.2 In which Local Government Authority (LGA) is this proposal located?')

        Out[5]: 
        {'label': '1.2 In which Local Government Authority (LGA) is this proposal located?',
         'type': 'multi-select'}
    '''
    
    p=Proposal.objects.get(id=proposal_id)
    flattened_schema = search_keys(p.schema, search_list=['type', 'label'])
    #label = 'Will any of the sites require track or slre clearing'


    try:
        res = next(item for item in flattened_schema if item["label"] == question)
    except StopIteration as e:
        return None

    return res


def gen_shapefile(user, qs=Proposal.objects.none(), filter_kwargs={}, geojson=False):
    '''
        Generate and save shapefile from qs of Proposals
        eg.
            from disturbance.components.proposals.utils import gen_shapefile
            filter_kwargs = {'region_id': 1, 'activity': 'Basic raw material', 'processing_status': 'approved', 'applicant_id': 163, 'submitter__email': 'jawaid.mushtaq@dbca.wa.gov.au', 
                             'application_type__name': 'Disturbance', 'lodgement_date__gte': '2024-04-17', 'lodgement_date__lte': '2024-04-24'}
            gen_shapefile(user, qs, filter_kwargs)
            OR
            gen_shapefile(user, filter_kwargs)
    '''
    status_exc = [
        Proposal.PROCESSING_STATUS_TEMP,
        #Proposal.PROCESSING_STATUS_DRAFT,
        Proposal.PROCESSING_STATUS_DECLINED, 
        Proposal.PROCESSING_STATUS_DISCARDED,
    ]

    if qs.exists():
        qs = qs.exclude(Q(processing_status__in=status_exc) | Q(shapefile_json__isnull=True)).filter(**filter_kwargs)
    else:
        qs = Proposal.objects.exclude(Q(processing_status__in=status_exc) | Q(shapefile_json__isnull=True)).filter(**filter_kwargs)
    paginator = Paginator(qs, settings.QS_PAGINATOR_SIZE) # chunks

    t0 = time.time()
    logger.info('create_shapefile: 0')

    columns = ['org','app_no','prop_title','appissdate','appstadate','appexpdate','appstatus','assocprop','proptype','propurl','prop_activ','geometry']
    gdf_concat = gpd.GeoDataFrame(columns=["geometry"], crs=settings.CRS, geometry="geometry")
    for page_num in paginator.page_range:
        for p in paginator.page(page_num).object_list:
            try: 
                gdf = gpd.GeoDataFrame.from_features(p.shapefile_json)
                gdf.set_crs = settings.CRS
                #gdf['geometry'] = gdf['geometry']

                gdf['org']        = p.applicant.name if p.applicant else None
                gdf['app_no']     = p.approval.lodgement_number if p.approval else None
                gdf['prop_title'] = p.title
                gdf['appissdate'] = p.approval.issue_date.strftime("%Y-%d-%d") if p.approval else None
                gdf['appstadate'] = p.approval.start_date.strftime("%Y-%d-%d") if p.approval else None
                gdf['appexpdate'] = p.approval.expiry_date.strftime("%Y-%d-%d") if p.approval else None
                gdf['appstatus']  =  p.approval.status if p.approval else None
                gdf['assocprop']  = list(Proposal.objects.filter(approval__lodgement_number=p.approval.lodgement_number).values_list('lodgement_number', flat=True)) if p.approval else None
                gdf['proptype']   = p.proposal_type
                #gdf['propurl']    = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': p.id}))
                gdf['propurl']    = settings.BASE_URL + reverse('internal-proposal-detail',kwargs={'proposal_pk': p.id})
                gdf['prop_activ'] = p.activity

                #gdf.set_crs = settings.CRS
                gdf_concat = pd.concat([gdf_concat, gdf[columns]], ignore_index=True)

            except Exception as ge:
                logger.error(f'Cannot append proposal {p} to shapefile: {ge}')

    t1 = time.time()
    logger.info(f'create_shapefile: 1 - {t1 - t0}')
    gdf_concat.set_crs = settings.CRS

    if geojson:
        # The .shz extension allows the GeoJSON file to be downloaded (rather than opened in browser)
        filename = f'DAS_layers_{datetime.now().strftime("%Y%m%dT%H%M%S")}.geojson.shz'
        filepath = f'{settings.GEO_EXPORT_FOLDER}/{filename}'
        gdf_concat.to_file(f'private-media/{filepath}', driver='GeoJSON')
    else:
        # The .shz extension allows the shapefile to be zipped
        filename = f'DAS_layers_{datetime.now().strftime("%Y%m%dT%H%M%S")}.shz'
        filepath = f'{settings.GEO_EXPORT_FOLDER}/{filename}'
        gdf_concat.to_file(f'private-media/{filepath}', driver='ESRI Shapefile')

    t2 = time.time()
    logger.info(f'create_shapefile: len(gdf_concat) - {len(gdf_concat)}')
    logger.info(f'create_shapefile: 2 - {t2 - t1}')
    doc = ExportDocument()
    doc._file.name = filepath
    doc._file = filepath
    doc.requester = user
    doc.save()

    t3 = time.time()
    logger.info(f'create_shapefile: 3 - {t3 - t2}')

    return filename


#def gen_shapefile_sql(user, qs=Proposal.objects.none(), filter_kwargs={}, geojson=False):
#    '''
#        Generate and save shapefile from qs of Proposals
#        eg.
#            from disturbance.components.proposals.utils import gen_shapefile
#            filter_kwargs = {'region_id': 1, 'activity': 'Basic raw material', 'processing_status': 'approved', 'applicant_id': 163, 'submitter__email': 'jawaid.mushtaq@dbca.wa.gov.au', 
#                             'application_type__name': 'Disturbance', 'lodgement_date__gte': '2024-04-17', 'lodgement_date__lte': '2024-04-24'}
#            gen_shapefile(user, qs, filter_kwargs)
#            OR
#            gen_shapefile(user, filter_kwargs)
#    '''
#    status_exc = [
#        Proposal.PROCESSING_STATUS_TEMP,
#        #Proposal.PROCESSING_STATUS_DRAFT,
#        Proposal.PROCESSING_STATUS_DECLINED, 
#        Proposal.PROCESSING_STATUS_DISCARDED,
#    ]
#
#    if qs.exists():
#        qs = qs.exclude(Q(processing_status__in=status_exc) | Q(shapefile_json__isnull=True)).filter(**filter_kwargs)
#    else:
#        qs = Proposal.objects.exclude(Q(processing_status__in=status_exc) | Q(shapefile_json__isnull=True)).filter(**filter_kwargs)
#
#    t0 = time.time()
#    logger.info('create_shapefile: 0')
#
#    gdf_concat = gpd.GeoDataFrame(columns=["geometry"], crs=settings.CRS, geometry="geometry")
#    for p in qs:
#        try: 
#            gdf = gpd.GeoDataFrame.from_features(p.shapefile_json)["geometry"] # only "geometry" is needed in addition proposal attrs
#
#            gdf['org']        = p.applicant.name if p.applicant else None
#            gdf['app_no']     = p.approval.lodgement_number if p.approval else None
#            gdf['prop_title'] = p.title
#            gdf['appissdate'] = p.approval.issue_date.strftime("%Y-%d-%d") if p.approval else None
#            gdf['appstadate'] = p.approval.start_date.strftime("%Y-%d-%d") if p.approval else None
#            gdf['appexpdate'] = p.approval.expiry_date.strftime("%Y-%d-%d") if p.approval else None
#            gdf['appstatus']  =  p.approval.status if p.approval else None
#            gdf['assocprop']  = list(Proposal.objects.filter(approval__lodgement_number=p.approval.lodgement_number).values_list('lodgement_number', flat=True)) if p.approval else None
#            gdf['proptype']   = p.proposal_type
#            #gdf['propurl']    = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': p.id}))
#            gdf['propurl']    = settings.BASE_URL + reverse('internal-proposal-detail',kwargs={'proposal_pk': p.id})
#            gdf['prop_activ'] = p.activity
#
#            gdf.set_crs = settings.CRS
#            gdf_concat = pd.concat([gdf_concat, gdf], ignore_index=True)
#
#        except Exception as ge:
#            logger.error(f'Cannot append proposal {p} to shapefile: {ge}')
#
#    t1 = time.time()
#    logger.info(f'create_shapefile: 1 - {t1 - t0}')
#    gdf_concat.set_crs = settings.CRS
#
#    if geojson:
#        # The .shz extension allows the GeoJSON file to be downloaded (rather than opened in browser)
#        filename = f'DAS_layers_{datetime.now().strftime("%Y%m%dT%H%M%S")}.geojson.shz'
#        filepath = f'{settings.GEO_EXPORT_FOLDER}/{filename}'
#        gdf_concat.to_file(f'private-media/{filepath}', driver='GeoJSON')
#    else:
#        # The .shz extension allows the shapefile to be zipped
#        filename = f'DAS_layers_{datetime.now().strftime("%Y%m%dT%H%M%S")}.shz'
#        filepath = f'{settings.GEO_EXPORT_FOLDER}/{filename}'
#        gdf_concat.to_file(f'private-media/{filepath}', driver='ESRI Shapefile')
#
#    t2 = time.time()
#    logger.info(f'create_shapefile: len(gdf_concat) - {len(gdf_concat)}')
#    logger.info(f'create_shapefile: 2 - {t2 - t1}')
#    doc = ExportDocument()
#    doc._file.name = filepath
#    doc._file = filepath
#    doc.requester = user
#    doc.save()
#
#    t3 = time.time()
#    logger.info(f'create_shapefile: 3 - {t3 - t2}')
#
#    return filename



#def prefill_payload(proposal):
#    if proposal.apiary_group_application_type:
#        return
#
#    if not instance.shapefile_json:
#        raise serializers.ValidationError(str('Please upload a valid shapefile'))                   
#
#    try:
#        start_time = time.time()
#
#        # current_ts = request.data.get('current_ts') # format required '%Y-%m-%dT%H:%M:%S'
#        if proposal.prefill_timestamp:
#            current_ts= proposal.prefill_timestamp.strftime('%Y-%m-%dT%H:%M:%S')
#        else:
#            current_ts = proposal.prefill_timestamp
#        geojson=proposal.shapefile_json
#
#        masterlist_question_qs = SpatialQueryQuestion.current_questions.all() # exclude expired questions from SQS Query
#        serializer = DTSpatialQueryQuestionSerializer(masterlist_question_qs, context={'data': request.data}, many=True)
#        rendered = JSONRenderer().render(serializer.data).decode('utf-8')
#        masterlist_questions = json.loads(rendered)
#
#        # ONLY include masterlist_questions that are present in proposal.schema to send to SQS
#        schema_questions = get_schema_questions(proposal.schema) 
#        questions = [i['question'] for i in masterlist_questions if i['question'] in schema_questions]
#        #questions = [i['question'] for i in masterlist_questions if i['question'] in schema_questions and '1.2 In which' in i['question']]
#        unique_questions = list(set(questions))
#
#        # group by question
#        question_group_list = [{'question_group': i, 'questions': []} for i in unique_questions]
#        for question_dict in question_group_list:
#            for sqq_record in masterlist_questions:
#                #print(j['layer_name'])
#                if question_dict['question_group'] in sqq_record.values():
#                    question_dict['questions'].append(sqq_record)
#
#        data = dict(
#            proposal=dict(
#                id=proposal.id,
#                current_ts=current_ts,
#                schema=proposal.schema,
#                data=proposal.data,
#            ),
#            requester = request.user.email,
#            request_type=self.FULL,
#            system=settings.SYSTEM_NAME_SHORT,
#            masterlist_questions = question_group_list,
#            geojson = geojson,
#        )
#
#
#        #url = get_sqs_url('das/spatial_query/')
#        url = get_sqs_url('das/task_queue')
#        #url = get_sqs_url('das_queue/')
#        resp = requests.post(url=url, data={'data': json.dumps(data)}, auth=HTTPBasicAuth(settings.SQS_USER,settings.SQS_PASS), verify=False)
#        resp_data = resp.json()
#        
#        task, created = TaskMonitor.objects.get_or_create(
#                task_id=resp_data['data']['task_id'], 
#                defaults={
#                    'proposal': proposal,
#                    'requester': request.user,
#                }
#            )
#        if not created and task.requester.email != request.user.email:
#            # another user may attempt to Prefill, whilst job is still queued
#            logger.info(f'Task ID {task.id}, Proposal {proposal.lodgement_number} requester updated. Prev {task.requester.email}, New {request.user.email}')
#            task.requester = request.user
#
#        return Response(resp_data, status=resp.status_code)
#
#    except Exception as e:
#        print(traceback.print_exc())
#        raise serializers.ValidationError(str(e))


