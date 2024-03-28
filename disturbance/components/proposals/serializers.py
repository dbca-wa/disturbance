import logging
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import serializers, status

from ledger.payments.models import Invoice
import collections
from disturbance.components.proposals.models import (
                                    ProposalType,
                                    Proposal,
                                    ProposalUserAction,
                                    ProposalLogEntry,
                                    Referral,
                                    ProposalRequirement,
                                    ProposalStandardRequirement,
                                    AmendmentRequest,
                                    AmendmentRequestDocument,
                                    QuestionOption,
                                    SectionQuestion,
                                    ProposalTypeSection,
                                    MasterlistQuestion,
                                    QuestionOption,
                                    SpatialQueryQuestion,
                                    SpatialQueryMetrics,
                                    CddpQuestionGroup,
                                )
from disturbance.components.organisations.models import (
                                Organisation
                            )
from disturbance.components.main.serializers import CommunicationLogEntrySerializer, DASMapLayerSqsSerializer
from disturbance.components.main.models import DASMapLayer

from disturbance.components.proposals.serializers_apiary import ProposalApiarySerializer, \
    ProposalApiaryTemporaryUseSerializer
from disturbance.components.proposals.serializers_base import BaseProposalSerializer, ProposalReferralSerializer, \
    ProposalDeclinedDetailsSerializer, EmailUserSerializer, EmailSerializer
from drf_writable_nested import UniqueFieldsMixin , WritableNestedModelSerializer
from datetime import datetime
from django.core.urlresolvers import reverse


logger = logging.getLogger(__name__)


class ProposalTypeSerializer(serializers.ModelSerializer):
    activities = serializers.SerializerMethodField()
    class Meta:
        model = ProposalType
        fields = (
            'id',
            'schema',
            'activities'
        )

    def get_activities(self,obj):
        return obj.activities.names()


class ProposalWrapperSerializer(serializers.ModelSerializer):
    application_type_name = serializers.SerializerMethodField()
    class Meta:
        model = Proposal
        fields = (
            'id',
            'application_type_name',
        )

    def get_application_type_name(self,obj):
        return obj.application_type.name


class ApprovalDTProposalSerializer(serializers.ModelSerializer):
    application_type = serializers.CharField(source='application_type.name', read_only=True)
    region = serializers.CharField(source='region.name', read_only=True)
    class Meta:
        model = Proposal
        fields = (
            'id',
            'application_type',
            'region',
            'activity',
            'title',
        )


class DTProposalSerializer(BaseProposalSerializer):
    submitter = EmailUserSerializer()
    applicant = serializers.CharField(source='applicant.organisation.name')
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    assigned_officer = serializers.CharField(source='assigned_officer.get_full_name', allow_null=True)

    application_type = serializers.CharField(source='application_type.name', read_only=True)
    region = serializers.CharField(source='region.name', read_only=True)
    district = serializers.CharField(source='district.name', read_only=True)
    #tenure = serializers.CharField(source='tenure.name', read_only=True)


class ListProposalSerializer(BaseProposalSerializer):
    submitter = EmailUserSerializer()
    applicant = serializers.CharField(source='applicant.organisation.name')
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    #assigned_officer = serializers.CharField(source='assigned_officer.get_full_name')
    assigned_officer = serializers.SerializerMethodField(read_only=True)

    application_type = serializers.CharField(source='application_type.name', read_only=True)
    #region = serializers.CharField(source='region.name', read_only=True)
    #district = serializers.CharField(source='district.name', read_only=True)
    region = serializers.SerializerMethodField(read_only=True)
    district = serializers.SerializerMethodField(read_only=True)

    #tenure = serializers.CharField(source='tenure.name', read_only=True)
    assessor_process = serializers.SerializerMethodField(read_only=True)
    relevant_applicant_name = serializers.SerializerMethodField(read_only=True)
    apiary_group_application_type = serializers.SerializerMethodField(read_only=True)
    template_group = serializers.SerializerMethodField(read_only=True)

    fee_invoice_references = serializers.SerializerMethodField()
    approval = serializers.CharField(source='approval.lodgement_number')

    class Meta:
        model = Proposal
        fields = (
                'id',
                'application_type',
                'activity',
                'approval_level',
                'title',
                'region',
                'district',
                'tenure',
                'customer_status',
                'processing_status',
                'review_status',
                'applicant',
                'proxy_applicant',
                'submitter',
                'assigned_officer',
                'previous_application',
                'get_history',
                'lodgement_date',
                'modified_date',
                'readonly',
                'can_user_edit',
                'can_user_view',
                'reference',
                'lodgement_number',
                'migrated',
                'lodgement_sequence',
                'can_officer_process',
                'assessor_process',
                'allowed_assessors',
                'proposal_type',
                # 'fee_invoice_reference',
                'fee_invoice_references',
                'fee_paid',
                'relevant_applicant_name',
                'apiary_group_application_type',
                'template_group',
                'approval',
                )
        # the serverSide functionality of datatables is such that only columns that have field 'data' defined are requested from the serializer. We
        # also require the following additional fields for some of the mRender functions
        datatables_always_serialize = (
                'id',
                'activity',
                'title',
                'region',
                'customer_status',
                'processing_status',
                'applicant',
                'submitter',
                'assigned_officer',
                'lodgement_date',
                'can_user_edit',
                'can_user_view',
                'reference',
                'lodgement_number',
                'migrated',
                'can_officer_process',
                'assessor_process',
                'allowed_assessors',
                # 'fee_invoice_reference',
                'fee_invoice_references',
                'fee_paid',
                'application_type',
                'relevant_applicant_name',
                'apiary_group_application_type',
                'template_group',
                'approval',
                )

    def get_fee_invoice_references(self, obj):
        invoice_references = []
        if obj.fee_invoice_references:
            for inv_ref in obj.fee_invoice_references:
                try:
                    inv = Invoice.objects.get(reference=inv_ref)
                    from disturbance.helpers import is_internal
                    if is_internal(self.context['request']):
                        invoice_references.append(inv_ref)
                    else:
                        # We don't want to show 0 doller invoices to external
                        if inv.amount > 0:
                            invoice_references.append(inv_ref)
                except:
                    pass
        return invoice_references

    def get_relevant_applicant_name(self,obj):
        return obj.relevant_applicant_name

    def get_assigned_officer(self,obj):
        if obj.assigned_officer:
            return obj.assigned_officer.get_full_name()
        return None

    def get_region(self,obj):
        if obj.region:
            return obj.region.name
        return None

    def get_district(self,obj):
        if obj.district:
            return obj.district.name
        return None

    def get_assessor_process(self,obj):
        # Check if currently logged in user has access to process the proposal
        request = self.context['request']
        template_group = self.context.get('template_group')
        user = request.user
        # if obj.can_officer_process and template_group == 'apiary':
        if obj.can_officer_process:
            '''if (obj.assigned_officer and obj.assigned_officer == user) or (user in obj.allowed_assessors):
                return True'''
            if obj.assigned_officer:
                if obj.assigned_officer == user:
                    return True
            elif user in obj.allowed_assessors:
                return True
        return False

    def get_apiary_group_application_type(self, obj):
        return obj.apiary_group_application_type

    def get_template_group(self, obj):
        return self.context.get('template_group')


#class ProposalSqsSerializer(BaseProposalSerializer):
#    class Meta:
#        model = Proposal
#        fields = (
#            'schema',
#            'data',
#        )
 
class ProposalSerializer(BaseProposalSerializer):
    submitter = serializers.CharField(source='submitter.get_full_name')
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)

    application_type = serializers.CharField(source='application_type.name', read_only=True)
    #region = serializers.CharField(source='region.name', read_only=True)
    #district = serializers.CharField(source='district.name', read_only=True)
    #tenure = serializers.CharField(source='tenure.name', read_only=True)
    comment_data= serializers.SerializerMethodField(read_only=True)
    #add_info_applicant= serializers.SerializerMethodField(read_only=True)

    proposal_apiary = serializers.SerializerMethodField()
    apiary_temporary_use = ProposalApiaryTemporaryUseSerializer(many=False, read_only=True)
    # apiary_temporary_use_set = ProposalApiaryTemporaryUseSerializer(many=True, read_only=True)
    apiary_group_application_type = serializers.SerializerMethodField()
    # region_name=serializers.CharField(source='region.name', read_only=True)
    # district_name=serializers.CharField(source='district.name', read_only=True)

    class Meta:
        model = Proposal
        fields = BaseProposalSerializer.Meta.fields + (
            'comment_data',
            'proposal_apiary',
            'apiary_temporary_use',
            'apiary_group_application_type',
            'shapefile_json',
            'add_info_applicant',
            'add_info_assessor',
            'history_add_info_assessor',
            'refresh_timestamp',
            'prefill_timestamp',
            'layer_data',
            'region_name',
            'district_name',
            # 'apiary_temporary_use_set',
        )

    def get_readonly(self,obj):
        return obj.can_user_view

    def get_comment_data(self,obj):
         return obj.comment_data

    def get_proposal_apiary(self, obj):
        if hasattr(obj, 'proposal_apiary'):
            pasl = obj.proposal_apiary
            return ProposalApiarySerializer(pasl, context=self.context).data
        else:
            return ''

    def get_apiary_group_application_type(self, obj):
        return obj.apiary_group_application_type


class SaveProposalSerializer(BaseProposalSerializer):
    assessor_data = serializers.JSONField(required=False)

    class Meta:
        model = Proposal
        fields = (
                'id',
                'application_type',
                'activity',
                'approval_level',
                'title',
                'region',
                'district',
                'tenure',
                'data',
                'assessor_data',
                'comment_data',
                'add_info_applicant',
                'add_info_assessor',
                'history_add_info_assessor',
                'refresh_timestamp',
                'prefill_timestamp',
                'schema',
                'customer_status',
                'processing_status',
                'review_status',
                #'hard_copy',
                'applicant',
                'proxy_applicant',
                'submitter',
                'assigned_officer',
                'previous_application',
                'lodgement_date',
                'documents',
                'requirements',
                'readonly',
                'can_user_edit',
                'can_user_view',
                'reference',
                'lodgement_number',
                'lodgement_sequence',
                'can_officer_process',
                'sub_activity_level1',
                'sub_activity_level2',
                'management_area',
                )
        read_only_fields=('documents','requirements')

class SaveProposalRegionSerializer(BaseProposalSerializer):

    class Meta:
        model = Proposal
        fields = (
                'id',
                'region',
                'district',
                'activity',
                'sub_activity_level1',
                'sub_activity_level2',
                'management_area',
                'approval_level',
                )
        #read_only_fields=('documents','requirements')


class ApplicantSerializer(serializers.ModelSerializer):
    from disturbance.components.organisations.serializers import OrganisationAddressSerializer
    address = OrganisationAddressSerializer()
    class Meta:
        model = Organisation
        fields = (
                    'id',
                    'name',
                    'abn',
                    'address',
                    'email',
                    'phone_number',
                )


class InternalProposalSerializer(BaseProposalSerializer):
    applicant = ApplicantSerializer()
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    submitter = serializers.CharField(source='submitter.get_full_name')
    submitter_email = serializers.CharField(source='submitter.email')
    proposaldeclineddetails = ProposalDeclinedDetailsSerializer()
    #
    assessor_mode = serializers.SerializerMethodField()
    current_assessor = serializers.SerializerMethodField()
    assessor_data = serializers.SerializerMethodField()
    latest_referrals = ProposalReferralSerializer(many=True)
    allowed_assessors = EmailUserSerializer(many=True)
    approval_level_document = serializers.SerializerMethodField()
    application_type = serializers.CharField(source='application_type.name', read_only=True)
    referral_email_list=serializers.SerializerMethodField()
    #region = serializers.CharField(source='region.name', read_only=True)
    #district = serializers.CharField(source='district.name', read_only=True)
    #tenure = serializers.CharField(source='tenure.name', read_only=True)
    apiary_temporary_use = ProposalApiaryTemporaryUseSerializer(many=False, read_only=True)
    requirements_completed=serializers.SerializerMethodField()
    reversion_history = serializers.SerializerMethodField()
    # region_name=serializers.CharField(source='region.name', read_only=True)
    # district_name=serializers.CharField(source='district.name', read_only=True)
    
    class Meta:
        model = Proposal
        fields = (
                'id',
                'application_type',
                'activity',
                'approval_level',
                'approval_level_document',
                'approval_level_comment',
                'region',
                'district',
                'gis_info',
                'tenure',
                'title',
                'data',
                'schema',
                'customer_status',
                'processing_status',
                'review_status',
                #'hard_copy',
                'applicant',
                'proxy_applicant',
                'submitter',
                'submitter_email',
                'assigned_officer',
                'assigned_approver',
                'previous_application',
                'get_history',
                'lodgement_date',
                'modified_date',
                'documents',
                'requirements',
                'readonly',
                'can_user_edit',
                'can_user_view',
                'documents_url',
                'assessor_mode',
                'current_assessor',
                'assessor_data',
                'layer_data',
                'comment_data',
                'add_info_applicant',
                'add_info_assessor',
                'history_add_info_assessor',
                'refresh_timestamp',
                'prefill_timestamp',
                'latest_referrals',
                'allowed_assessors',
                'proposed_issuance_approval',
                'proposed_decline_status',
                'proposaldeclineddetails',
                'permit',
                'reference',
                'lodgement_number',
                'lodgement_sequence',
                'can_officer_process',
                'proposal_type',
                'hasAmendmentRequest',
                'referral_email_list',
                'sub_activity_level1',
                'sub_activity_level2',
                'management_area',
                # 'fee_invoice_reference',
                'fee_invoice_references',
                'fee_paid',
                'apiary_temporary_use',
                'requirements_completed',
                'reversion_history',
                'shapefile_json',
                'reissued',
                'region_name',
                'district_name',
                )
        read_only_fields=('documents','requirements','gis_info',)


    def get_reversion_history(self, obj):
        """ This uses Reversion to get all the revisions made to this Proposal.
        
        The revisions are returned as a dict with the Proposal id and version as key.
        """
        from reversion.models import Version

        # Versions are in reverse order by default
        versions = Version.objects.get_for_object(obj).select_related('revision')\
            .filter(revision__comment__contains='processing_status').get_unique()
        # this seems like inefficient duplication however
        # django reversion wont allow .count() after .get_unique()
        versions_count = len(list(Version.objects.get_for_object(obj).select_related('revision')\
            .filter(revision__comment__contains='processing_status').get_unique()))
        # Build the dictionary of reversions
        version_dictionary = {}
        for index, version in enumerate(versions):
            version_key = f'{obj.lodgement_number}-{versions_count-index}'
            version_dictionary[version_key] = {
                'date': version.revision.date_created,
                'processing_status': version.field_dict['processing_status'],
            }

        return version_dictionary


    def get_approval_level_document(self,obj):
        if obj.approval_level_document is not None:
            return [obj.approval_level_document.name,obj.approval_level_document._file.url]
        else:
            return obj.approval_level_document

    def get_assessor_mode(self,obj):
        # TODO check if the proposal has been accepted or declined
        request = self.context['request']
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        return {
            'assessor_mode': True,
            'has_assessor_mode': obj.has_assessor_mode(user),
            'assessor_can_assess': obj.can_assess(user),
            'assessor_level': 'assessor',
            'assessor_box_view': obj.assessor_comments_view(user),
            'status_without_assessor': obj.status_without_assessor
        }

    def get_readonly(self,obj):
        return True

    def get_current_assessor(self,obj):
        return {
            'id': self.context['request'].user.id,
            'name': self.context['request'].user.get_full_name(),
            'email': self.context['request'].user.email
        }

    def get_assessor_data(self,obj):
        return obj.assessor_data

    def get_referral_email_list(self,obj):
        request = self.context['request']
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        return obj.referral_email_list(user)

    def get_requirements_completed(self,obj):
        return True


class ReferralProposalSerializer(InternalProposalSerializer):
    def get_assessor_mode(self,obj):
        # TODO check if the proposal has been accepted or declined
        request = self.context['request']
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        try:
            referral = Referral.objects.get(proposal=obj,referral=user)
        except:
            referral = None
        return {
            'assessor_mode': True,
            'assessor_can_assess': referral.can_assess_referral(user) if referral else None,
            'assessor_level': 'referral',
            'assessor_box_view': obj.assessor_comments_view(user),
            'status_without_assessor': obj.status_without_assessor
        }

class ReferralWrapperSerializer(serializers.ModelSerializer):
    apiary_referral_exists = serializers.SerializerMethodField()
    class Meta:
        model = Referral
        fields = (
            'id',
            'apiary_referral_exists',
        )

    def get_apiary_referral_exists(self,obj):
        return hasattr(obj, 'apiary_referral')


class ReferralSerializer(serializers.ModelSerializer):
    processing_status = serializers.CharField(source='get_processing_status_display')
    latest_referrals = ProposalReferralSerializer(many=True)
    can_be_completed = serializers.BooleanField()
    class Meta:
        model = Referral
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(ReferralSerializer, self).__init__(*args, **kwargs)
        self.fields['proposal'] = ReferralProposalSerializer(context={'request':self.context['request']})

class ProposalUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')
    class Meta:
        model = ProposalUserAction
        fields = '__all__'

class ProposalLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()
    class Meta:
        model = ProposalLogEntry
        fields = '__all__'
        read_only_fields = (
            'customer',
        )

    def get_documents(self,obj):
        return [[d.name,d._file.url] for d in obj.documents.all()]

class SendReferralSerializer(serializers.Serializer):
    email = serializers.EmailField()
    text = serializers.CharField(allow_blank=True)

class DTReferralSerializer(serializers.ModelSerializer):
    processing_status = serializers.CharField(source='proposal.get_processing_status_display')
    referral_status = serializers.CharField(source='get_processing_status_display')
    proposal_lodgement_date = serializers.CharField(source='proposal.lodgement_date')
    proposal_lodgement_number = serializers.CharField(source='proposal.lodgement_number')
    submitter = serializers.SerializerMethodField()
    region = serializers.CharField(source='region.name', read_only=True)
    referral = EmailUserSerializer()
    relevant_applicant_name = serializers.SerializerMethodField()
    #proposal_application_type = serializers.SerializerMethodField()
    template_group = serializers.SerializerMethodField(read_only=True)
    assigned_officer = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Referral
        fields = (
            'id',
            'region',
            'activity',
            'title',
            #'applicant',
            'relevant_applicant_name',
            'submitter',
            'processing_status',
            'referral_status',
            'lodged_on',
            'proposal',
            'can_be_processed',
            'referral',
            'proposal_lodgement_date',
            'proposal_lodgement_number',
            'referral_text',
            'template_group',
            'assigned_officer',
        )

    def get_submitter(self,obj):
        return EmailUserSerializer(obj.proposal.submitter).data

    def get_assigned_officer(self,obj):
        if obj.proposal.apiary_group_application_type:
            return EmailUserSerializer(obj.apiary_referral.assigned_officer).data

    def get_relevant_applicant_name(self,obj):
        return obj.proposal.relevant_applicant_name

    def get_template_group(self, obj):
        return self.context.get('template_group')


class ProposalRequirementSerializer(serializers.ModelSerializer):
    due_date = serializers.DateField(input_formats=['%d/%m/%Y'],required=False,allow_null=True)
    apiary_renewal = serializers.SerializerMethodField()
    class Meta:
        model = ProposalRequirement
        fields = (
                'id',
                'due_date',
                'free_requirement',
                'standard_requirement',
                'standard',
                'order',
                'proposal',
                'recurrence',
                'recurrence_schedule',
                'recurrence_pattern',
                'requirement',
                'is_deleted',
                'copied_from', 
                'apiary_approval', 
                'sitetransfer_approval', 
                'require_due_date', 
                'copied_for_renewal',
                'apiary_renewal',
                )
        read_only_fields = ('order','requirement', 'copied_from')

    def get_apiary_renewal(self, obj):
        return obj.proposal.apiary_group_application_type and obj.proposal.proposal_type == "renewal"

class ProposalStandardRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalStandardRequirement
        fields = ('id','code','text')


class ProposedApprovalSerializer(serializers.Serializer):
    expiry_date = serializers.DateField(input_formats=['%d/%m/%Y'], required=False)
    start_date = serializers.DateField(input_formats=['%d/%m/%Y'], required=False)
    details = serializers.CharField(required=False, allow_blank=True)
    cc_email = serializers.CharField(required=False,allow_null=True, allow_blank=True)
    confirmation = serializers.BooleanField(required=False,default=False)

#    batch_no = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    cpc_date = serializers.DateField(input_formats=['%d/%m/%Y'], required=False)
#    minister_date = serializers.DateField(input_formats=['%d/%m/%Y'], required=False)
#    map_ref = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    forest_block = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    cog = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    roadtrack = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    zone = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    catchment = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    dra_permit = serializers.BooleanField(required=False,default=False)

    def validate(self, attrs):
        return attrs


class ProposedApprovalSiteTransferSerializer(serializers.Serializer):
    #expiry_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    #start_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    details = serializers.CharField()
    cc_email = serializers.CharField(required=False,allow_null=True, allow_blank=True)

#    batch_no = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    cpc_date = serializers.DateField(input_formats=['%d/%m/%Y'], required=False)
#    minister_date = serializers.DateField(input_formats=['%d/%m/%Y'], required=False)
#    map_ref = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    forest_block = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    cog = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    roadtrack = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    zone = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    catchment = serializers.CharField(required=False,allow_null=True, allow_blank=True)
#    dra_permit = serializers.BooleanField(required=False,default=False)



class PropedDeclineSerializer(serializers.Serializer):
    reason = serializers.CharField()
    cc_email = serializers.CharField(required=False, allow_null=True)

class AmendmentRequestDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmendmentRequestDocument
        fields = ('id', 'name', '_file')
        #fields = '__all__'

class AmendmentRequestSerializer(serializers.ModelSerializer):
    #reason = serializers.SerializerMethodField()
    amendment_request_documents = AmendmentRequestDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = AmendmentRequest
        fields = '__all__'

    #def get_reason (self,obj):
        #return obj.get_reason_display()
        #return obj.reason.reason

class AmendmentRequestDisplaySerializer(serializers.ModelSerializer):
    reason = serializers.SerializerMethodField()
    amendment_request_documents = AmendmentRequestDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = AmendmentRequest
        fields = '__all__'

    def get_reason (self,obj):
        #return obj.get_reason_display()
        return obj.reason.reason if obj.reason else None


class SearchKeywordSerializer(serializers.Serializer):
    number = serializers.CharField()
    id = serializers.IntegerField()
    type = serializers.CharField()
    applicant = serializers.CharField()
    #text = serializers.CharField(required=False,allow_null=True)
    text = serializers.JSONField(required=False)

class SearchReferenceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()

class SearchGeoJsonSerializer(serializers.Serializer):
    search_geojson = serializers.JSONField(required=False)

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ('label',)

class SectionQuestionSerializer(serializers.ModelSerializer):
    question_name=serializers.CharField(source='question.question')
    answer_type=serializers.CharField(source='question.answer_type')
    #question_options= QuestionOptionSerializer(many=True, read_only=True)
    question_options= serializers.SerializerMethodField()

    class Meta:
        model = SectionQuestion
        fields = ('section', 'question_id', 'question_options', 'question_name', 'answer_type',)

    def get_question_options(self, obj):
        options = None
        option_list = obj.question_options
        if option_list:
            options = [
                    {
                        'label': o.label,
                        'value': o.value,
                        #'conditions': obj.ANSWER_TYPE_CONDITIONS,

                    } for o in option_list
                ]

        return options

class ProposalTypeSectionSerializer(serializers.ModelSerializer):
    section_questions = SectionQuestionSerializer(many=True, read_only=True)
    proposal_type_name=serializers.CharField(source='proposal_type.name')
    class Meta:
        model = ProposalTypeSection
        fields = '__all__'

class SearchProposalTypeSerializer(serializers.ModelSerializer):
    '''
    Serializer for Licence ProposalType on the Search Section.
    '''
    sections = ProposalTypeSectionSerializer(many=True, read_only=True)
    class Meta:
        model = ProposalType
        fields = (
                'id',
                'name_with_version',
                'name',
                'sections',
        )

#Schema screen serializers 
class SchemaSectionSerializer(serializers.ModelSerializer):
    '''
    Serializer for Schema builder using Purpose sections.
    '''
    section_name = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = ProposalTypeSection
        fields = '__all__'

class SchemaOptionSerializer(serializers.ModelSerializer):
    '''
    Serializer for Schema builder using Masterlist questions.
    '''
    label = serializers.CharField(allow_blank=True, required=False)
    value = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = QuestionOption
        fields = '__all__'

    def create(self, validated_data):
        return QuestionOption.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.label = validated_data.get('label', instance.label)
        instance.value = validated_data.get('value', instance.value)


class SchemaMasterlistSerializer(serializers.ModelSerializer):
    '''
    Serializer for Schema builder using Masterlist questions.
    '''
    options = serializers.SerializerMethodField()
    headers = serializers.SerializerMethodField()
    expanders = serializers.SerializerMethodField()
    name = serializers.CharField(read_only=True)

    class Meta:
        model = MasterlistQuestion
        fields = '__all__'

    # def get_options_orig(self, obj):
    #     option_labels = []
    #     try:
    #         options = self.initial_data.get('options', None)
    #         for o in options:
    #             option_labels.append(o)
    #             qo = QuestionOption.objects.filter(label=o['label'])
    #             if qo.exists():
    #                 o['value'] = qo[0].id
    #                 continue
    #             option_serializer = SchemaOptionSerializer(data=o)
    #             option_serializer.is_valid(raise_exception=True)
    #             option_serializer.save()
    #             opt_id = option_serializer.data['id']
    #             o['value'] = opt_id
    #         obj.set_property_cache_options(option_labels)
            
    #     except Exception:
    #         options = None
    #         option_list = obj.get_options()
    #         if option_list:
    #             options = [
    #                 {
    #                     'label': o.label,
    #                     'value': o.value,
    #                     #'conditions': obj.ANSWER_TYPE_CONDITIONS,

    #                 } for o in option_list
    #             ]

    #     return options

    def get_options(self, obj):
        option_labels = []
        try:
            options = self.initial_data.get('options', None)
            for o in options:
                o['label']=o['label'].strip()
                #option_labels.append(o)
                qo = QuestionOption.objects.filter(label=o['label'])
                if qo.exists():
                    o['value'] = qo[0].id
                else:
                    option_serializer = SchemaOptionSerializer(data=o)
                    option_serializer.is_valid(raise_exception=True)
                    option_serializer.save()
                    opt_id = option_serializer.data['id']
                    o['value'] = opt_id
                option_labels.append(o)
            obj.set_property_cache_options(option_labels)
            
        except Exception:
            options = None
            option_list = obj.get_options()
            if option_list:
                options = [
                    {
                        'label': o.label,
                        'value': o.value,
                        #'conditions': obj.ANSWER_TYPE_CONDITIONS,

                    } for o in option_list
                ]

        return options

    def get_headers(self, obj):

        try:
            headers = self.initial_data.get('headers', None)
            obj.set_property_cache_headers(headers)
            obj.save()

        except Exception:
            headers = None
            header_list = obj.get_headers()
            if header_list:
                headers = [
                    {
                        'label': h['label'],
                        'value': h['value'],

                    } for h in header_list
                ]

        return headers

    def get_expanders(self, obj):

        try:
            expanders = self.initial_data.get('expanders', None)
            obj.set_property_cache_expanders(expanders)
            obj.save()

        except Exception:
            expanders = None
            expander_list = obj.get_expanders()
            if expander_list:
                expanders = [
                    {
                        'label': e['label'],
                        'value': e['value'],

                    } for e in expander_list
                ]

        return expanders


class SchemaMasterlistOptionSerializer(serializers.ModelSerializer):
    '''
    Serializer for Schema builder using Masterlist questions.
    '''
    options = serializers.SerializerMethodField()
    #question_id = serializers.SerializerMethodField()

    class Meta:
        model = MasterlistQuestion
        fields = ('id', 'question', 'answer_type', 'options')

#    def get_option(self, obj):
#        return obj.option.values()

    #def get_question_id(self, obj):


    def get_options(self, obj):
        if obj.answer_type not in ['radiobuttons', 'checkbox']:
            # Only need options for rb and cb in SpatialQuery CDDP config'n
            return None

        option_labels = []
        try:
            options = self.initial_data.get('options', None)
            for o in options:
                #option_labels.append(o)
                qo = QuestionOption.objects.filter(label=o['label'])
                if qo.exists():
                    o['value'] = qo[0].id
                else:
                    option_serializer = SchemaOptionSerializer(data=o)
                    option_serializer.is_valid(raise_exception=True)
                    option_serializer.save()
                    opt_id = option_serializer.data['id']
                    o['value'] = opt_id
                option_labels.append(o)
            obj.set_property_cache_options(option_labels)
            
        except Exception:
            options = None
            option_list = obj.get_options()
            if option_list:
                options = [
                    {
                        'label': o.label,
                        'value': o.value,
                        #'conditions': obj.ANSWER_TYPE_CONDITIONS,

                    } for o in option_list
                ]

        return options



class SelectSchemaMasterlistSerializer(serializers.ModelSerializer):
    '''
    Serializer for Schema builder using Masterlist questions.
    '''
    options = serializers.SerializerMethodField()
    # headers = serializers.SerializerMethodField()
    # expanders = serializers.SerializerMethodField()
    name = serializers.CharField(read_only=True)

    class Meta:
        model = MasterlistQuestion
        fields = '__all__'

    def get_options(self, obj):
        options = None
        option_list = obj.get_options()
        if option_list:
            options = [
                    {
                        'label': o.label,
                        'value': o.value,
                        #'conditions': obj.ANSWER_TYPE_CONDITIONS,

                    } for o in option_list
                ]

        return options

        # option_labels = []
        # try:
        #     options = self.initial_data.get('options', None)
        #     for o in options:
        #         option_labels.append(o)
        #         qo = QuestionOption.objects.filter(label=o['label'])
        #         if qo.exists():
        #             o['value'] = qo[0].id
        #             continue
        #         option_serializer = SchemaOptionSerializer(data=o)
        #         option_serializer.is_valid(raise_exception=True)
        #         option_serializer.save()
        #         opt_id = option_serializer.data['id']
        #         o['value'] = opt_id
        #     obj.set_property_cache_options(option_labels)
            
        # except Exception:
        #     options = None
        #     option_list = obj.get_options()
        #     if option_list:
        #         options = [
        #             {
        #                 'label': o.label,
        #                 'value': o.value,
        #                 'conditions': obj.ANSWER_TYPE_CONDITIONS,

        #             } for o in option_list
        #         ]

        # return options

    

class DTSchemaMasterlistSerializer(SchemaMasterlistSerializer):
    '''
    Serializer for Schema Masterlist Datatables.
    '''
    options = serializers.SerializerMethodField()
    headers = serializers.SerializerMethodField()
    expanders = serializers.SerializerMethodField()

    class Meta:
        model = MasterlistQuestion
        fields = (
            'id',
            'name',
            'question',
            'answer_type',
            'options',
            'headers',
            'expanders',
            'help_text_url',
            'help_text_assessor_url',
            'help_text',
            'help_text_assessor',
        )
        # the serverSide functionality of datatables is such that only columns
        # that have field 'data' defined are requested from the serializer. Use
        # datatables_always_serialize to force render of fields that are not
        # listed as 'data' in the datatable columns.
        datatables_always_serialize = fields

    def get_options(self, obj):
        options = obj.get_options()
        data = [{'value': o.value, 'label': o.label} for o in options]
        return data

    def get_headers(self, obj):
        headers = obj.get_headers()
        data = [{'value': h['value'], 'label': h['label']} for h in headers]
        return data

    def get_expanders(self, obj):
        expanders = obj.get_expanders()
        data = [{'value': e['value'], 'label': e['label']} for e in expanders]
        return data



class SchemaQuestionSerializer(serializers.ModelSerializer):
    '''
    Serializer for Schema builder using Section Questions.
    '''
    tag = serializers.ListField(child=serializers.CharField())
    # parent_question = SchemaMasterlistSerializer(read_only=True)
    # parent_answer = SchemaOptionSerializer(read_only=True)

    conditions = [
        {'label': 'IncreaseLicenceFee', 'value': ''},
        {'label': 'IncreaseRenewalFee', 'value': ''},
        {'label': 'IncreaseApplicationFee', 'value': ''},
        {'label': 'StandardCondition', 'value': ''},
        {'label': 'RequestInspection', 'value': False},
    ]
    options = serializers.SerializerMethodField()
    # conditions = serializers.SerializerMethodField()

    class Meta:
        model = SectionQuestion
        fields = (
            'section',
            'question',
            'parent_question',
            'parent_answer',
            'order',
            #'section_group',
            'options',
            'tag',
        )

    def get_options(self, obj):
        try:
            options = self.initial_data.get('options', None)
            print(options)
            obj.set_property_cache_options(options)
            obj.save()

        except Exception:
            options = None
            option_list = obj.get_options()
            if option_list:
                options = [
                    {
                        'label': o["label"],
                        'value': o["value"],
                        #'conditions': self.conditions

                    } for o in option_list
                ]

        return options

    # def get_conditions(self, obj):
    #     return self.conditions


class DTSchemaQuestionSerializer(SchemaQuestionSerializer):
    '''
    Serializer for Schema builder using Section Questions.
    '''
    question = serializers.SerializerMethodField()
    section = SchemaSectionSerializer()
    question_id = serializers.SerializerMethodField()
    proposal_type = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    #section_group = SchemaGroupSerializer()

    class Meta:
        model = SectionQuestion
        fields = (
            'id',
            'section',
            'question',
            'question_id',
            'parent_question',
            'parent_answer',
            'proposal_type',
            #'section_group',
            'options',
            'tag',
            'order',
        )

        # the serverSide functionality of datatables is such that only columns
        # that have field 'data' defined are requested from the serializer. Use
        # datatables_always_serialize to force render of fields that are not
        # listed as 'data' in the datatable columns.
        datatables_always_serialize = fields

    def get_question(self, obj):
        masterlist = SchemaMasterlistSerializer(obj.question).data
        return masterlist['question']

    def get_question_id(self, obj):
        return obj.question_id

    def get_proposal_type(self, obj):
        return obj.section.proposal_type.name_with_version

    def get_options(self, obj):
        options = obj.get_options()
        data = [
            {
                'value': o['value'],
                'label': o['label'],
                #'conditions': o['conditions']
            } for o in options
        ]
        return data

class ProposalTypeSerializer(serializers.ModelSerializer):
    '''
    Serializer for Licence ProposalType.
    '''
    class Meta:
        model = ProposalType
        fields = '__all__'

class ProposalTypeSchemaSerializer(serializers.ModelSerializer):
    '''
    Serializer for Licence ProposalType.
    '''
    class Meta:
        model = ProposalType
        fields = (
            'id',
            'name',
            'name_with_version'
        )


class SchemaProposalTypeSerializer(serializers.ModelSerializer):
    '''
    Serializer for Schema builder using ProposalType sections.
    '''
    section_name = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = ProposalTypeSection
        fields = '__all__'


class DTSchemaProposalTypeSerializer(SchemaProposalTypeSerializer):
    '''
    Serializer for datatables using ProposalType sections.
    '''
    proposal_type = serializers.SerializerMethodField()

    class Meta:
        model = ProposalTypeSection
        fields = (
            'id',
            'section_name',
            'section_label',
            'index',
            'proposal_type',
        )

        # the serverSide functionality of datatables is such that only columns
        # that have field 'data' defined are requested from the serializer. Use
        # datatables_always_serialize to force render of fields that are not
        # listed as 'data' in the datatable columns.
        datatables_always_serialize = fields

    def get_proposal_type(self, obj):
        return ProposalTypeSchemaSerializer(obj.proposal_type).data

class CddpQuestionGroupSerializer(serializers.ModelSerializer):

    can_user_edit = serializers.SerializerMethodField()

    class Meta:
        model = CddpQuestionGroup
        fields = ('id', 'name', 'can_user_edit',)#'allowed_editors',)

    def get_can_user_edit(self, obj):
        user = self.context['request'].user if self.context and 'request' in self.context else None
        can_user_edit = obj.name in CddpQuestionGroup.objects.filter(members__in=[user]).values_list('name', flat=True)
        return True if can_user_edit or (user and user.is_superuser) else False

#class MLQuestionSerializer(serializers.ModelSerializer):
#
#    class Meta:
#        model = MasterlistQuestion
#        fields = ('id', 'question',)
#
#class MLQuestionOptionSerializer(serializers.ModelSerializer):
#
#    class Meta:
#        model = QuestionOption
#        fields = ('id', 'label', 'value')


class DTSpatialQueryQuestionSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    '''
    Serializer for Datatable SpatialQueryQuestion.
    '''
    question = serializers.CharField(source='question.question')
    answer_mlq = serializers.CharField(allow_null=True, source='answer_mlq.label')
    #question = MLQuestionSerializer()
    #answer_mlq = SchemaOptionSerializer()

    #expiry = serializers.DateField(read_only=True)
    #buffer = serializers.IntegerField(read_only=True)
    expiry = serializers.DateField(allow_null=True, required=False)
    buffer = serializers.IntegerField(allow_null=True, required=False)
    group = CddpQuestionGroupSerializer()
    layer = DASMapLayerSqsSerializer()
    masterlist_question = serializers.SerializerMethodField(read_only=True)
    #modified_date = serializers.SerializerMethodField(read_only=True)
    modified_date = serializers.DateTimeField(required=False)
    #layer_name = serializers.SerializerMethodField()
    #layer_url = serializers.SerializerMethodField()

    class Meta:
        model = SpatialQueryQuestion
        #fields = '__all__'
        fields = (
          'id',
          'modified_date',
          'masterlist_question',
          'question',
          'answer_mlq',
          #'layer_name',
          #'layer_url',
          'expiry',
          'visible_to_proponent',
          'buffer',
          'how',
          'column_name',
          'operator',
          'value',
          'prefix_answer',
          'no_polygons_proponent',
          'answer',
          'prefix_info',
          'no_polygons_assessor',
          'assessor_info',
          'show_add_info_section_prop',
          'proponent_items',
          'assessor_items',
          'regions',
          'layer',
          'group',
        )
        datatables_always_serialize = fields

#    def _get_modified_date(self, obj):
#        dt = timezone.make_aware(datetime.now(),timezone.get_default_timezone())
#        return datetime.strftime(dt, '%Y-%m-%dT%H:%M:%S%z')

    def create(self, validated_data):
        data = self.context['request'].data

        if data.get('answer_mlq'):
            validated_data.update(
                dict(answer_mlq_id=data.get('answer_mlq_id'))
            )

        [validated_data.pop(key) for key in ['question', 'answer_mlq', 'layer', 'group']]
        return SpatialQueryQuestion.objects.create(
            **validated_data, 
            question_id=data.get('question_id'),
            group_id=data['group'].get('id'),
            layer_id=data['layer'].get('id')
        )

    def update(self, instance, validated_data):
        data = self.context['request'].data

        if data.get('answer_mlq'):
            validated_data.update(
                dict(answer_mlq_id=data.get('answer_mlq_id'))
            )

        [validated_data.pop(key) for key in ['question', 'answer_mlq', 'layer', 'group']]
        return SpatialQueryQuestion.objects.filter(id=instance.id).update(
            **validated_data, 
            question_id=data.get('question_id'),
            group_id=data['group'].get('id'),
            layer_id=data['layer'].get('id')
        )


#    def get_question(self, obj):
#        #return obj.question.question if obj.question else None
#        return obj.question.question
#
#    def get_answer_mlq(self, obj):
#        return obj.answer_mlq.label if obj.answer_mlq else None

    def get_layer_name(self, obj):
        return obj.layer.layer_name

    def get_layer_url(self, obj):
        return obj.layer.layer_url

    def get_masterlist_question(self, obj):
        l = [] 
        qs = MasterlistQuestion.objects.filter(question=obj.question)
        question_id = qs[0].id if qs.exists() else None
        answer_type = qs[0].answer_type if qs.exists() else None

        l.append( 
            dict(
                question_id=question_id,
                answer_type=answer_type
            ) 
        )

        return l

    def _get_allowed_editors(self, obj):
        return obj.email


class DTSpatialQueryMetricsSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    '''
    Serializer for Datatable SpatialQueryQuestion.
    '''
    lodgement_number = serializers.CharField(source='proposal.lodgement_number')
    total_query_time = serializers.SerializerMethodField()
    total_api_time = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = SpatialQueryMetrics
        #fields = '__all__'
        fields = (
          'id',
          'lodgement_number',
          'when',
          'system',
          'request_type',
          'total_query_time',
          'total_api_time',
          'response_cached',
          'metrics',
        )
        datatables_always_serialize = fields

    def get_total_query_time(self, obj):
        return obj.total_query_time

    def get_total_api_time(self, obj):
        ''' Total Time for API Request Response '''
        return obj.time_taken

    def get_metrics(self, obj):
        return obj.metrics


class DTSpatialQueryMetricsDetailsSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    '''
    Serializer for Datatable SpatialQueryQuestion.
    '''
    lodgement_number = serializers.CharField(source='proposal.lodgement_number')
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = SpatialQueryMetrics
        #fields = '__all__'
        fields = (
          'id',
          'lodgement_number',
          'metrics',
        )
        datatables_always_serialize = fields

    def get_metrics(self, obj):
        return obj.metrics
    

class DTSpatialQueryLayersUsedSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    '''
    Serializer for Datatable SpatialQuery Layers Used.
    '''
    class Meta:
        model = Proposal
        #fields = '__all__'
        fields = (
          'id',
          'lodgement_number',
          'layer_data',
        )
        datatables_always_serialize = fields


class DASMapFilterSerializer(BaseProposalSerializer):
    processing_status_display= serializers.SerializerMethodField()
    customer_status_display= serializers.SerializerMethodField()
    approval_lodgement_number= serializers.SerializerMethodField()
    approval_issue_date= serializers.SerializerMethodField()
    approval_start_date= serializers.SerializerMethodField()
    approval_expiry_date= serializers.SerializerMethodField()
    approval_status= serializers.SerializerMethodField()
    submitter_full_name = serializers.CharField(source='submitter.get_full_name')
    submitter = serializers.CharField(source='submitter.email')
    applicant_name= serializers.CharField(source='applicant.name')
    application_type_name= serializers.CharField(source='application_type.name')
    region_name = serializers.CharField(source='region.name', read_only=True)
    associated_proposals= serializers.SerializerMethodField()
    proposal_url = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = (
                'id',
                'activity',
                'title',
                'region',
                'region_name',
                'district',
                'customer_status',
                'processing_status',
                'processing_status_display',
                'customer_status',
                'customer_status_display',
                'submitter', 
                'submitter_full_name',
                'lodgement_number',
                #'shapefile_json',
                'lodgement_date',
                'proposal_type',
                'approval_lodgement_number',
                'approval_issue_date',
                'approval_start_date',
                'approval_expiry_date',
                'approval_status',
                'applicant_id',
                'applicant_name',
                'shapefile_json',
                'application_type_name',
                'associated_proposals',
                'proposal_url',

                )
    
    def get_region(self,obj):
        if obj.region:
            return obj.region.name
        return None

    def get_district(self,obj):
        if obj.district:
            return obj.district.name
        return None
    
    def get_processing_status_display(self,obj):
        return obj.get_processing_status_display()
    
    def get_customer_status_display(self,obj):
        return obj.get_customer_status_display()
    
    def get_approval_lodgement_number(self,obj):
        if obj.approval:
            return obj.approval.lodgement_number
        return None
    def get_approval_issue_date(self,obj):
        if obj.approval:
            return obj.approval.issue_date
        return None
    
    def get_approval_start_date(self,obj):
        if obj.approval:
            return obj.approval.start_date
        return None
    
    def get_approval_expiry_date(self,obj):
        if obj.approval:
            return obj.approval.expiry_date
        return None
    
    def get_approval_status(self,obj):
        if obj.approval:
            return obj.approval.status
        return None
    
    def get_associated_proposals(self,obj):
        if obj.approval:
            qs=Proposal.objects.filter(approval__lodgement_number=obj.approval.lodgement_number).values_list('lodgement_number', flat=True)
            if qs:
                result= [proposal for proposal in qs]
                return result
        return None
    
    def get_proposal_url(self,obj):
        request=self.context['request']
        url=''
        from disturbance.helpers import is_internal
        if is_internal(request):
            url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': obj.id}))
        else:
            url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': obj.id}))
        return url



