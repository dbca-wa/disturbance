from ledger.accounts.models import EmailUser,Address
from django.utils import timezone
from disturbance import settings
from disturbance.components.approvals.models import (
    Approval,
    ApprovalLogEntry,
    ApprovalUserAction, 
    ApprovalDocument,
)
from disturbance.components.organisations.models import Organisation
from disturbance.components.main.serializers import CommunicationLogEntrySerializer
from rest_framework import serializers
from disturbance.components.proposals.models import Proposal


class EmailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = ('id','email','first_name','last_name','title','organisation')


class ApprovalWrapperSerializer(serializers.ModelSerializer):

    class Meta:
        model = Approval
        fields = (
            'id',
            )


class ApprovalDocumentHistorySerializer(serializers.ModelSerializer):
    history_date = serializers.SerializerMethodField()
    history_document_url = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalDocument
        fields = (
            'history_date',
            'history_document_url',
        )

    def get_history_date(self, obj):
        date_format_loc = timezone.localtime(
            obj.uploaded_date
        )
        history_date = date_format_loc.strftime('%d/%m/%Y %H:%M:%S.%f')

        return history_date

    def get_history_document_url(self, obj):
        url = obj._file.url
        return url


class ApprovalSerializerForLicenceDoc(serializers.ModelSerializer):
    authority_holder = serializers.SerializerMethodField()
    authority_holder_address = serializers.SerializerMethodField()
    trading_name = serializers.SerializerMethodField()
    authority_number = serializers.SerializerMethodField()
    licence_start_date = serializers.SerializerMethodField()
    licence_expiry_date = serializers.SerializerMethodField()
    issue_date = serializers.SerializerMethodField()
    approver = serializers.SerializerMethodField()
    requirements = serializers.SerializerMethodField()

    def get_authority_holder(self, approval):
        return approval.relevant_applicant_name

    def get_authority_holder_address(self, approval):
        return approval.relevant_applicant_address.summary if approval.relevant_applicant_address else '(Address not found)'

    def get_trading_name(self, approval):
        #return approval.applicant.trading_name if approval.applicant else ''
        try:
            return approval.applicant.trading_name if approval.applicant.trading_name else ''
        except:
            return ''

    def get_authority_number(self, approval):
        return approval.lodgement_number

    def get_licence_start_date(self, approval):
        return approval.start_date.strftime('%d %B %Y')

    def get_licence_expiry_date(self, approval):
        return approval.expiry_date.strftime('%d %B %Y')

    def get_issue_date(self, approval):
        return approval.issue_date.strftime('%d/%m/%Y')

    def get_approver(self, approval):
        approver = self.context.get('approver')
        return approver.get_full_name()

    def get_requirements(self, approval):
        ret_array = []
        for req in approval.proposalrequirement_set.all():
            ret_array.append({
                'id': req.id,
                'text': req.requirement,
            })
        return ret_array

    class Meta:
        model = Approval
        fields = (
            'id',
            'authority_holder',
            'authority_holder_address',
            'trading_name',
            'authority_number',
            'licence_start_date',
            'licence_expiry_date',
            'issue_date',
            'approver' ,
            'requirements',
        )


class ApplicantAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id',
            'line1',
            'line2',
            'line3',
            'locality',
            'state',
            'country',
            'postcode'
        )

        
from disturbance.components.proposals.serializers import ProposalSerializer
class ApprovalSerializer(serializers.ModelSerializer):
    #applicant = serializers.CharField(source='applicant.name')
    #applicant_id = serializers.ReadOnlyField(source='applicant.id')
    applicant = serializers.SerializerMethodField(read_only=True)
    applicant_type = serializers.SerializerMethodField(read_only=True)
    applicant_id = serializers.SerializerMethodField(read_only=True)
    licence_document = serializers.CharField(source='licence_document._file.url')
    #renewal_document = serializers.CharField(source='renewal_document._file.url')
    renewal_document = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(source='get_status_display')
    allowed_assessors = EmailUserSerializer(many=True)
    region = serializers.CharField(source='current_proposal.region.name')
    district = serializers.CharField(source='current_proposal.district.name', allow_null=True)
    #tenure = serializers.CharField(source='current_proposal.tenure.name')
    #activity = serializers.CharField(source='current_proposal.activity')
    activity = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(source='current_proposal.title')
    #current_proposal = InternalProposalSerializer(many=False)
    can_approver_reissue = serializers.SerializerMethodField(read_only=True)
    application_type = serializers.SerializerMethodField(read_only=True)

    current_proposal = serializers.SerializerMethodField()
    organisation_name = serializers.SerializerMethodField()
    organisation_abn = serializers.SerializerMethodField()
    applicant_first_name = serializers.SerializerMethodField()
    applicant_last_name = serializers.SerializerMethodField()
    applicant_address = serializers.SerializerMethodField()
    requirements = serializers.SerializerMethodField()
    template_group = serializers.SerializerMethodField()

    class Meta:
        model = Approval
        fields = (
            'id',
            'lodgement_number',
            'migrated',
            'licence_document',
            'replaced_by',
            'current_proposal',
            'current_proposal_id',
            'activity',
            'region',
            'district',
            'tenure',
            'title',
            'renewal_document',
            'renewal_sent',
            'issue_date',
            'original_issue_date',
            'start_date',
            'expiry_date',
            'surrender_details',
            'suspension_details',
            'applicant',
            'applicant_type',
            'applicant_id',
            'extracted_fields',
            'status',
            'reference',
            'can_reissue',
            'allowed_assessors',
            'cancellation_date',
            'cancellation_details',
            'applicant_id',
            'can_action',
            'set_to_cancel',
            'set_to_surrender',
            'set_to_suspend',
            'can_renew',
            'can_amend',
            'can_reinstate', 
            'can_approver_reissue',
            'application_type',
            'current_proposal',
            'organisation_name',
            'organisation_abn',
            'applicant_first_name',
            'applicant_last_name',
            'applicant_address',
            'requirements',
            'template_group',
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data' defined are requested from the serializer. We
        # also require the following additional fields for some of the mRender functions
        datatables_always_serialize = (
            'id',
            'migrated',
            'activity',
            'region',
            'title',
            'status',
            'reference',
            'lodgement_number',
            'licence_document',
            'start_date',
            'expiry_date',
            'applicant',
            'can_reissue',
            'can_action',
            'can_reinstate',
            'can_amend',
            'can_renew',
            'set_to_cancel',
            'set_to_suspend',
            'set_to_surrender',
            'current_proposal',
            'current_proposal_id',
            'renewal_document',
            'renewal_sent',
            'allowed_assessors',
            'can_approver_reissue',
            'template_group',
        )

    def get_current_proposal(self, approval):
        return ProposalSerializer(approval.current_proposal, context=self.context).data

    def get_activity(self, approval):
        return approval.current_proposal.activity

    def get_requirements(self, approval):
#        for proposal in approval.proposal_set.all():
#            for requirement in proposal.requirements.all():
#                requirements.append(ApiaryProposalRequirementSerializer(requirement).data)
#        return requirements
        return []

    def get_application_type(self,obj):
        if obj.current_proposal.application_type:
            return obj.current_proposal.application_type.name
        return None

    def get_applicant(self,obj):
        try:
            if obj.proxy_applicant and obj.proxy_applicant.get_full_name():
                return obj.proxy_applicant.get_full_name()
            else:
                return obj.applicant.name if isinstance(obj.applicant, Organisation) else obj.applicant
        except:
            return None

    def get_applicant_type(self,obj):
        try:
            return obj.applicant_type
        except:
            return None

    def get_applicant_id(self,obj):
        try:
            return obj.relevant_applicant_id
        except:
            return None

    def get_organisation_name(self,obj):
        if obj.applicant:
            return obj.applicant.name

    def get_organisation_abn(self,obj):
        if obj.applicant:
            return obj.applicant.abn

    def get_applicant_first_name(self,obj):
        if obj.proxy_applicant:
            return obj.proxy_applicant.first_name

    def get_applicant_last_name(self,obj):
        if obj.proxy_applicant:
            return obj.proxy_applicant.last_name

    def get_applicant_address(self, obj):
        address_serializer = None
        if obj.relevant_applicant_address:
            address_serializer = ApplicantAddressSerializer(obj.relevant_applicant_address)
            return address_serializer.data
        return address_serializer

    def get_renewal_document(self,obj):
        if obj.relevant_renewal_document and obj.relevant_renewal_document._file:
            return obj.relevant_renewal_document._file.url
        return None

    def get_can_approver_reissue(self,obj):
        # Check if currently logged in user has access to process the proposal
        request = self.context['request']
        user = request.user
        if obj.can_reissue:
            if user in obj.allowed_approvers:
                return True
        return False

    def get_template_group(self, obj):
        return self.context.get('template_group')


from disturbance.components.proposals.serializers import ApprovalDTProposalSerializer
class DTApprovalSerializer(serializers.ModelSerializer):
    current_proposal = ApprovalDTProposalSerializer(read_only=True)
    allowed_assessors = EmailUserSerializer(many=True)
    licence_document = serializers.CharField(source='licence_document._file.url')
    #allowed_assessors = serializers.SerializerMethodField(read_only=True)
    can_approver_reissue = serializers.SerializerMethodField(read_only=True)
    template_group = serializers.SerializerMethodField()
    applicant = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(source='get_status_display')
    region = serializers.CharField(source='current_proposal.region')
    activity = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(source='current_proposal.title')
    renewal_document = serializers.SerializerMethodField(read_only=True)
    associated_proposals= serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Approval
        fields = (
            'id',
            'migrated',
            'activity',
            'region',
            'title',
            'status',
            'reference',
            'lodgement_number',
            'licence_document',
            'start_date',
            'expiry_date',
            'applicant',
            'can_reissue',
            'can_action',
            'can_reinstate',
            'can_amend',
            'can_renew',
            'set_to_cancel',
            'set_to_suspend',
            'set_to_surrender',
            'current_proposal',
            'current_proposal_id',
            'renewal_document',
            'renewal_sent',
            'allowed_assessors',
            'can_approver_reissue',
            'template_group',
            'associated_proposals',
            )

    def get_allowed_assessors(self, obj):
        return EmailUserSerializer(obj.current_proposal.compliance_assessors, many=True).data
    
    def get_associated_proposals(self,obj):
        
        if obj.current_proposal:
            qs=Proposal.objects.filter(approval__lodgement_number=obj.lodgement_number).values_list('lodgement_number', flat=True)
            if qs:
                result= [proposal for proposal in qs]
                return result
        return None

    def get_template_group(self, obj):
        return self.context.get('template_group')

    def get_renewal_document(self,obj):
        if obj.relevant_renewal_document and obj.relevant_renewal_document._file:
            return obj.relevant_renewal_document._file.url
        return None

    def get_can_approver_reissue(self,obj):
        # Check if currently logged in user has access to process the proposal
        request = self.context['request']
        user = request.user
        if obj.can_reissue:
            if user in obj.allowed_approvers:
                return True
        return False

    def get_applicant(self,obj):
        try:
            if obj.proxy_applicant and obj.proxy_applicant.get_full_name():
                return obj.proxy_applicant.get_full_name()
            else:
                return obj.applicant.name if isinstance(obj.applicant, Organisation) else obj.applicant
        except:
            return None

    def get_activity(self, approval):
        return approval.current_proposal.activity


class ApprovalCancellationSerializer(serializers.Serializer):
    cancellation_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    cancellation_details = serializers.CharField()


class ApprovalSuspensionSerializer(serializers.Serializer):
    from_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    to_date = serializers.DateField(input_formats=['%d/%m/%Y'], required=False, allow_null=True)
    suspension_details = serializers.CharField()


class ApprovalSurrenderSerializer(serializers.Serializer):
    surrender_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    surrender_details = serializers.CharField()


class ApprovalUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')
    class Meta:
        model = ApprovalUserAction
        fields = '__all__'


class ApprovalLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()
    class Meta:
        model = ApprovalLogEntry
        fields = '__all__'
        read_only_fields = (
            'customer',
        )

    def get_documents(self,obj):
        return [[d.name,d._file.url] for d in obj.documents.all()]


class ApprovalExportSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    region = serializers.CharField(source='current_proposal.region')
    activity = serializers.CharField(source='current_proposal.activity')
    title = serializers.CharField(source='current_proposal.title')
    applicant = serializers.SerializerMethodField(read_only=True)
    associated_proposals= serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Approval
        fields = (
            'lodgement_number',
            'region',
            'activity',
            'title',
            'applicant',
            'associated_proposals',
            'status',
            'start_date',
            'expiry_date',
        )
    
    def get_applicant(self,obj):
        try:
            if obj.proxy_applicant and obj.proxy_applicant.get_full_name():
                return obj.proxy_applicant.get_full_name()
            else:
                return obj.applicant.name if isinstance(obj.applicant, Organisation) else obj.applicant
        except:
            return None
    
    def get_associated_proposals(self,obj):
        
        if obj.current_proposal:
            qs=Proposal.objects.filter(approval__lodgement_number=obj.lodgement_number).values_list('lodgement_number', flat=True)
            if qs:
                # result= [proposal for proposal in qs]
                result = ','.join(proposal for proposal in qs)
                return result
        return None

