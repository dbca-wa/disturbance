from ledger.accounts.models import EmailUser
from rest_framework import serializers

from disturbance.components.proposals.models import Proposal, Referral, ProposalDeclinedDetails


class EmailUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = EmailUser
        fields = (
                'id',
                'email',
                'first_name',
                'last_name',
                'title',
                'organisation',
                'name'
                )

    def get_name(self, obj):
        return obj.get_full_name()

class BaseProposalSerializer(serializers.ModelSerializer):
    readonly = serializers.SerializerMethodField(read_only=True)
    documents_url = serializers.SerializerMethodField()
    proposal_type = serializers.SerializerMethodField()
    allowed_assessors = EmailUserSerializer(many=True)

    get_history = serializers.ReadOnlyField()

#    def __init__(self, *args, **kwargs):
#        import ipdb; ipdb.set_trace()
#        user = kwargs['context']['request'].user
#
#        super(BaseProposalSerializer, self).__init__(*args, **kwargs)
#        self.fields['parent'].queryset = self.get_request(user)

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
                #'assessor_data',
                'data',
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
                'get_history',
                'lodgement_date',
                'modified_date',
                'documents',
                'requirements',
                'readonly',
                'can_user_edit',
                'can_user_view',
                'documents_url',
                'reference',
                'lodgement_number',
                'lodgement_sequence',
                'can_officer_process',
                'allowed_assessors',
                'proposal_type',
                'sub_activity_level1',
                'sub_activity_level2',
                'management_area',
                # 'fee_invoice_reference',
                'fee_invoice_references',
                'fee_paid',
                'reissued',
                )
        read_only_fields=('documents',)

    def get_documents_url(self,obj):
        return '/private-media/proposals/{}/documents/'.format(obj.id)

    def get_readonly(self,obj):
        return False

    def get_processing_status(self,obj):
        return obj.get_processing_status_display()

    def get_review_status(self,obj):
        return obj.get_review_status_display()

    def get_customer_status(self,obj):
        return obj.get_customer_status_display()

    def get_proposal_type(self,obj):
        return obj.get_proposal_type_display()


class ProposalReferralSerializer(serializers.ModelSerializer):
    referral = serializers.CharField(source='referral.get_full_name')
    processing_status = serializers.CharField(source='get_processing_status_display')
    class Meta:
        model = Referral
        fields = '__all__'


class ProposalDeclinedDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalDeclinedDetails
        fields = '__all__'


