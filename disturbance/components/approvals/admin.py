from django.contrib import admin
from disturbance.components.approvals.models import Approval

@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ['lodgement_number','status','applicant','current_proposal']
    raw_id_fields = ('applicant','proxy_applicant','current_proposal')
    readonly_fields = ['replaced_by', 'licence_document', 'cover_letter_document','renewal_document']