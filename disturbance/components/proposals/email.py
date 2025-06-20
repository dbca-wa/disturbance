import logging
from email.mime.text import MIMEText
import json
from datetime import datetime

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_str
from django.urls import reverse
from django.conf import settings

from disturbance.components.emails.emails import TemplateEmailBase
from ledger.accounts.models import EmailUser
from disturbance.components.main.models import GlobalSettings

logger = logging.getLogger(__name__)

SYSTEM_NAME = settings.SYSTEM_NAME_SHORT + ' Automated Message'

def get_sender_user():
    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        EmailUser.objects.create(email=sender, password='')
        sender_user = EmailUser.objects.get(email__icontains=sender)
    return sender_user

def get_das_sharepoint_url():
    sharepoint_url = ''
    try:
        sharepoint_url = GlobalSettings.objects.get(key=GlobalSettings.DAS_SHAREPOINT_PAGE).value
    except:
        sharepoint_url = ''
    return sharepoint_url

def get_proposal_assess_help_url():
    proposal_assess_help_url = ''
    try:
        proposal_assess_help_url = GlobalSettings.objects.get(key=GlobalSettings.PROPOSAL_ASSESS_HELP_PAGE).value
    except:
        proposal_assess_help_url = ''
    return proposal_assess_help_url

def get_proposal_approver_help_url():
    proposal_assess_help_url = ''
    try:
        proposal_approver_help_url = GlobalSettings.objects.get(key=GlobalSettings.PROPOSAL_APPROVER_HELP_PAGE).value
    except:
        proposal_approver_help_url = ''
    return proposal_approver_help_url

def get_referral_assess_help_url():
    referral_assess_help_url = ''
    try:
        referral_assess_help_url = GlobalSettings.objects.get(key=GlobalSettings.REFERRAL_ASSESS_HELP_PAGE).value
    except:
        referral_assess_help_url = ''
    return referral_assess_help_url

def get_assessment_reminder_days():
    assessment_reminder_days= settings.ASSESSMENT_REMINDER_DAYS
    try:
        assessment_reminder_days = GlobalSettings.objects.get(key='assessment_reminder_days').value
    except:
        assessment_reminder_days= settings.ASSESSMENT_REMINDER_DAYS
    return assessment_reminder_days


class ReferralSendNotificationEmail(TemplateEmailBase):
    subject = 'A referral for a proposal has been sent to you.'
    html_template = 'disturbance/emails/proposals/send_referral_notification.html'
    txt_template = 'disturbance/emails/proposals/send_referral_notification.txt'

class ReferralCompleteNotificationEmail(TemplateEmailBase):
    subject = 'A referral for a proposal has been completed.'
    html_template = 'disturbance/emails/proposals/send_referral_complete_notification.html'
    txt_template = 'disturbance/emails/proposals/send_referral_complete_notification.txt'

class ReferralRecallNotificationEmail(TemplateEmailBase):
    subject = 'A referral for a proposal has been recalled.'
    html_template = 'disturbance/emails/proposals/send_referral_recall_notification.html'
    txt_template = 'disturbance/emails/proposals/send_referral_recall_notification.txt'    

class ProposalDeclineSendNotificationEmail(TemplateEmailBase):
    subject = 'Your Proposal has been declined.'
    html_template = 'disturbance/emails/proposals/send_decline_notification.html'
    txt_template = 'disturbance/emails/proposals/send_decline_notification.txt'

class ProposalApprovalSendNotificationEmail(TemplateEmailBase):
    subject = 'Your Proposal has been approved.'
    html_template = 'disturbance/emails/proposals/send_approval_notification.html'
    txt_template = 'disturbance/emails/proposals/send_approval_notification.txt'

class AmendmentRequestSendNotificationEmail(TemplateEmailBase):
    subject = 'An amendment to your Proposal is required.'
    html_template = 'disturbance/emails/proposals/send_amendment_notification.html'
    txt_template = 'disturbance/emails/proposals/send_amendment_notification.txt'

class SubmitSendNotificationEmail(TemplateEmailBase):
    subject = 'A new Proposal has been submitted.'
    html_template = 'disturbance/emails/proposals/send_submit_notification.html'
    txt_template = 'disturbance/emails/proposals/send_submit_notification.txt'

class AssessmentReminderSendNotificationEmail(TemplateEmailBase):
    subject = 'A Proposal is waiting for assessment.'
    html_template = 'disturbance/emails/proposals/send_assessment_reminder_notification.html'
    txt_template = 'disturbance/emails/proposals/send_assessment_reminder_notification.txt'

class ExternalSubmitSendNotificationEmail(TemplateEmailBase):
    subject = 'A new Proposal has been submitted.'
    html_template = 'disturbance/emails/proposals/send_external_submit_notification.html'
    txt_template = 'disturbance/emails/proposals/send_external_submit_notification.txt'

class ApproverDeclineSendNotificationEmail(TemplateEmailBase):
    subject = 'A Proposal has been recommended for decline.'
    html_template = 'disturbance/emails/proposals/send_approver_decline_notification.html'
    txt_template = 'disturbance/emails/proposals/send_approver_decline_notification.txt'

class ApproverApproveSendNotificationEmail(TemplateEmailBase):
    subject = 'A Proposal has been recommended for approval.'
    html_template = 'disturbance/emails/proposals/send_approver_approve_notification.html'
    txt_template = 'disturbance/emails/proposals/send_approver_approve_notification.txt'

class ApproverSendBackNotificationEmail(TemplateEmailBase):
    subject = 'A Proposal has been sent back by approver.'
    html_template = 'disturbance/emails/proposals/send_approver_sendback_notification.html'
    txt_template = 'disturbance/emails/proposals/send_approver_sendback_notification.txt'

## Apiary Templates
class ApiaryReferralSendNotificationEmail(TemplateEmailBase):
    subject = 'A referral for an application has been sent to you.'
    html_template = 'disturbance/emails/proposals/apiary_send_referral_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_referral_notification.txt'

class ApiaryReferralCompleteNotificationEmail(TemplateEmailBase):
    subject = 'A referral for an application has been completed.'
    html_template = 'disturbance/emails/proposals/apiary_send_referral_complete_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_referral_complete_notification.txt'

class ApiaryReferralRecallNotificationEmail(TemplateEmailBase):
    subject = 'A referral for an application has been recalled.'
    html_template = 'disturbance/emails/proposals/apiary_send_referral_recall_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_referral_recall_notification.txt'    

class ApiaryProposalDeclineSendNotificationEmail(TemplateEmailBase):
    subject = 'Your Application has been declined.'
    html_template = 'disturbance/emails/proposals/apiary_send_decline_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_decline_notification.txt'

class ApiaryProposalApprovalSiteTransferSendNotificationEmail(TemplateEmailBase):
    #subject = 'Your Application has been approved.'
    subject = 'Your Licence has been issued.'
    html_template = 'disturbance/emails/proposals/apiary_send_approval_site_transfer_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_approval_site_transfer_notification.txt'

class ApiaryProposalApprovalSendNotificationEmail(TemplateEmailBase):
    subject = 'Your Application has been approved.'
    html_template = 'disturbance/emails/proposals/apiary_send_approval_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_approval_notification.txt'

class ApiaryAmendmentRequestSendNotificationEmail(TemplateEmailBase):
    subject = 'An amendment to your Application is required.'
    html_template = 'disturbance/emails/proposals/apiary_send_amendment_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_amendment_notification.txt'

class ApiarySubmitSendNotificationEmail(TemplateEmailBase):
    subject = 'A new Application has been submitted.'
    html_template = 'disturbance/emails/proposals/apiary_send_submit_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_submit_notification.txt'

class ApiaryAssessmentReminderSendNotificationEmail(TemplateEmailBase):
    subject = 'An Application is waiting for assessment.'
    html_template = 'disturbance/emails/proposals/apiary_send_assessment_reminder_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_assessment_reminder_notification.txt'

class ApiaryExternalSubmitSendNotificationEmail(TemplateEmailBase):
    subject = 'A new Application has been submitted.'
    html_template = 'disturbance/emails/proposals/apiary_send_external_submit_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_external_submit_notification.txt'

class ApiaryApproverDeclineSendNotificationEmail(TemplateEmailBase):
    subject = 'An Application has been recommended for decline.'
    html_template = 'disturbance/emails/proposals/apiary_send_approver_decline_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_approver_decline_notification.txt'

class ApiaryApproverApproveSendNotificationEmail(TemplateEmailBase):
    subject = 'An Application has been recommended for approval.'
    html_template = 'disturbance/emails/proposals/apiary_send_approver_approve_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_approver_approve_notification.txt'

class ApiaryApproverSendBackNotificationEmail(TemplateEmailBase):
    subject = 'An Application has been sent back by approver.'
    html_template = 'disturbance/emails/proposals/apiary_send_approver_sendback_notification.html'
    txt_template = 'disturbance/emails/proposals/apiary_send_approver_sendback_notification.txt'

class ProposalPrefillRequestSentSendNotificationEmail(TemplateEmailBase):
    subject = 'Proposal prefill request has been sent.'
    html_template = 'disturbance/emails/proposals/proposal_prefill_request_sent_notification.html'
    txt_template = 'disturbance/emails/proposals/proposal_prefill_request_sent_notification.txt'

class ProposalPrefillCompletedSendNotificationEmail(TemplateEmailBase):
    subject = 'Proposal prefill has completed.'
    html_template = 'disturbance/emails/proposals/proposal_prefill_completed_notification.html'
    txt_template = 'disturbance/emails/proposals/proposal_prefill_completed_notification.txt'

class ProposalPrefillErrorSendNotificationEmail(TemplateEmailBase):
    subject = 'ERROR: Proposal prefill'
    html_template = 'disturbance/emails/proposals/proposal_prefill_error_notification.html'
    txt_template = 'disturbance/emails/proposals/proposal_prefill_error_notification.txt'

class ProposalRefreshRequestSentSendNotificationEmail(TemplateEmailBase):
    subject = 'Proposal refresh request has been sent.'
    html_template = 'disturbance/emails/proposals/proposal_refresh_request_sent_notification.html'
    txt_template = 'disturbance/emails/proposals/proposal_refresh_request_sent_notification.txt'

class ProposalRefreshCompletedSendNotificationEmail(TemplateEmailBase):
    subject = 'Proposal refresh has completed.'
    html_template = 'disturbance/emails/proposals/proposal_refresh_completed_notification.html'
    txt_template = 'disturbance/emails/proposals/proposal_refresh_completed_notification.txt'

class ProposalRefreshErrorSendNotificationEmail(TemplateEmailBase):
    subject = 'ERROR: Proposal refresh'
    html_template = 'disturbance/emails/proposals/proposal_refresh_error_notification.html'
    txt_template = 'disturbance/emails/proposals/proposal_refresh_error_notification.txt'

class ProposalTestSqqRequestSentSendNotificationEmail(TemplateEmailBase):
    subject = 'Proposal TEST SQQ request has been sent.'
    html_template = 'disturbance/emails/proposals/proposal_test_sqq_request_sent_notification.html'
    txt_template = 'disturbance/emails/proposals/proposal_test_sqq_request_sent_notification.txt'

class ProposalTestSqqCompletedSendNotificationEmail(TemplateEmailBase):
    subject = 'Proposal TEST SQQ has completed.'
    html_template = 'disturbance/emails/proposals/proposal_test_sqq_completed_notification.html'
    txt_template = 'disturbance/emails/proposals/proposal_test_sqq_completed_notification.txt'

class ProposalTestSqqErrorSendNotificationEmail(TemplateEmailBase):
    subject = 'ERROR: Proposal TEST SQQ'
    html_template = 'disturbance/emails/proposals/proposal_test_sqq_error_notification.html'
    txt_template = 'disturbance/emails/proposals/proposal_test_sqq_error_notification.txt'



def send_referral_email_notification(referral,request,reminder=False):
    email = ReferralSendNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-referral-detail',kwargs={'proposal_pk':referral.proposal.id,'referral_pk':referral.id}))
    assessor_name=referral.proposal.assigned_officer.get_full_name() if referral.proposal.assigned_officer else ''
    context = {
        'proposal': referral.proposal,
        'url': url,
        'reminder':reminder,
        'comments': referral.text,
        'greeting': 'Referee',
        'referral_assess_help_page': get_referral_assess_help_url(),
        'assessor_footer': True,
        'DAS_sharepoint_page': get_das_sharepoint_url(),
        'assessor_name': assessor_name,
    }

    msg = email.send(referral.referral.email, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_referral_email(msg, referral, sender=sender)
    if referral.proposal.applicant:
        _log_org_email(msg, referral.proposal.applicant, referral.referral, sender=sender)

def send_referral_recall_email_notification(referral,request):
    email = ReferralRecallNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-referral-detail',kwargs={'proposal_pk':referral.proposal.id,'referral_pk':referral.id}))
    assessor_name=referral.proposal.assigned_officer.get_full_name() if referral.proposal.assigned_officer else ''
    context = {
        'proposal': referral.proposal,
        'url': url,
        'greeting': 'Referee',
        'referral_assess_help_page': get_referral_assess_help_url(),
        'assessor_footer': True,
        'DAS_sharepoint_page': get_das_sharepoint_url(),
        'assessor_name': assessor_name,
    }

    msg = email.send(referral.referral.email, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_referral_email(msg, referral, sender=sender)
    if referral.proposal.applicant:
        _log_org_email(msg, referral.proposal.applicant, referral.referral, sender=sender)


def send_referral_complete_email_notification(referral,request):
    email = ReferralCompleteNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': referral.proposal.id}))
    referral_name=referral.referral.get_full_name() if referral.referral else ''
    context = {
        'proposal': referral.proposal,
        'url': url,
        'referral_comments': referral.referral_text,
        'greeting': 'Assessor',
        'referral_assess_help_page': get_referral_assess_help_url(),
        'assessor_footer': True,
        'DAS_sharepoint_page': get_das_sharepoint_url(),
        'referral_name': referral_name,
    }

    msg = email.send(referral.sent_by.email, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_referral_email(msg, referral, sender=sender)
    if referral.proposal.applicant:
        _log_org_email(msg, referral.proposal.applicant, referral.referral, sender=sender)

def send_apiary_referral_email_notification(referral,recipients,request,reminder=False):
    email = ApiaryReferralSendNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-referral-detail',kwargs={'proposal_pk':referral.proposal.id,'referral_pk':referral.id}))

    context = {
        'proposal': referral.proposal,
        'url': url,
        'reminder':reminder,
        'comments': referral.text
    }

    #msg = email.send(referral.referral.email, context=context)
    #recipients = list(ReferralRecipientGroup.objects.get(name=referral.email_group).members.all().values_list('email', flat=True))
    msg = email.send(recipients, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_referral_email(msg, referral, sender=sender)
    #if referral.proposal.applicant:
    #    _log_org_email(msg, referral.proposal.applicant, referral.apiary_referral.referral_group.members_email, sender=sender)
    #elif referral.proposal.applicant_field == 'proxy_applicant':
    #    _log_user_email(msg, referral.proposal.proxy_applicant, referral.apiary_referral.referral_group.members_email, sender=sender)
    #else:
    #    _log_user_email(msg, referral.proposal.submitter, referral.apiary_referral.referral_group.members_email, sender=sender)
    if referral.proposal.applicant:
        _log_org_email(email_message=msg, organisation=referral.proposal.applicant, customer=None, sender=sender)
    else:
        _log_user_email(email_message=msg, emailuser=referral.proposal.submitter, customer=None, sender=sender)

## BB 20200610 this is not called at present, in line with existing DAS behaviour
#def send_apiary_referral_recall_email_notification(referral,recipients,request):
#    email = ReferralRecallNotificationEmail()
#    url = request.build_absolute_uri(reverse('internal-referral-detail',kwargs={'proposal_pk':referral.proposal.id,'referral_pk':referral.id}))
#
#    context = {
#        'proposal': referral.proposal,
#        'url': url,
#    }
#
#    #msg = email.send(referral.referral.email, context=context)
#    msg = email.send(recipients, context=context)
#    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
#    _log_proposal_referral_email(msg, referral, sender=sender)
#    if referral.proposal.applicant:
#        _log_org_email(msg, referral.proposal.applicant, referral.apiary_referral.referral_group.members_email, sender=sender)
#    elif referral.proposal.applicant_field == 'proxy_applicant':
#        _log_user_email(msg, referral.proposal.proxy_applicant, referral.apiary_referral.referral_group.members_email, sender=sender)
#    else:
#        _log_user_email(msg, referral.proposal.submitter, referral.apiary_referral.referral_group.members_email, sender=sender)


def send_apiary_referral_complete_email_notification(referral,request, completed_by):
    email = ApiaryReferralCompleteNotificationEmail()
    email.subject = referral.sent_by.email + ': ' + email.subject
    url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': referral.proposal.id}))

    context = {
        #'completed_by': referral.referral,
        'completed_by': completed_by,
        'proposal': referral.proposal,
        'url': url,
        'referral_comments': referral.referral_text
    }

    #msg = email.send(referral.sent_by.email,attachments=attachments, context=context)
    msg = email.send(referral.sent_by.email, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_referral_email(msg, referral, sender=sender)
    #if referral.proposal.applicant:
    #    _log_org_email(msg, referral.proposal.applicant, referral.apiary_referral.referral_group.members_email, sender=sender)
    #elif referral.proposal.applicant_field == 'proxy_applicant':
    #    _log_user_email(msg, referral.proposal.proxy_applicant, referral.apiary_referral.referral_group.members_email, sender=sender)
    #else:
    #    _log_user_email(msg, referral.proposal.submitter, referral.apiary_referral.referral_group.members_email, sender=sender)
    if referral.proposal.applicant:
        _log_org_email(email_message=msg, organisation=referral.proposal.applicant, customer=None, sender=sender)
    else:
        _log_user_email(email_message=msg, emailuser=referral.proposal.submitter, customer=None, sender=sender)

def send_amendment_email_notification(amendment_request, request, proposal):
    # if proposal.apiary_group_application_type:
    #     email = ApiaryAmendmentRequestSendNotificationEmail()
    # else:
    #     email = AmendmentRequestSendNotificationEmail()
    email = AmendmentRequestSendNotificationEmail()
    #reason = amendment_request.get_reason_display()
    reason = amendment_request.reason.reason
    url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    if "-internal" in url:
        # remove '-internal'. This email is for external submitters 
        url = ''.join(url.split('-internal'))

    attachments = []
    if amendment_request.amendment_request_documents:
        for doc in amendment_request.amendment_request_documents.all():
            #file_name = doc._file.name
            file_name = doc.name
            attachment = (file_name, doc._file.file.read())
            attachments.append(attachment)


    context = {
        'proposal': proposal,
        'reason': reason,
        'amendment_request_text': amendment_request.text,
        'url': url
    }

    all_ccs = []
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email and proposal.applicant.email:
            cc_list = proposal.applicant.email
            if cc_list:
                all_ccs = [cc_list]

    msg = email.send(proposal.submitter.email, cc=all_ccs, context=context,  attachments=attachments)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_submit_email_notification(request, proposal):
    # if proposal.apiary_group_application_type:
    #     email = ApiarySubmitSendNotificationEmail()
    # else:
    #     email = SubmitSendNotificationEmail()
    email = SubmitSendNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': proposal.id}))
    if "-internal" not in url:
        # add it. This email is for internal staff (assessors)
        url = '-internal.{}'.format(settings.SITE_DOMAIN).join(url.split('.' + settings.SITE_DOMAIN))
    context = {
        'proposal': proposal,
        'url': url,
        'greeting': 'Assessor',
        'proposal_assess_help_page': get_proposal_assess_help_url(),
        'assessor_footer': True,
        'DAS_sharepoint_page': get_das_sharepoint_url()
    }

    msg = email.send(proposal.assessor_recipients, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    # Don't log organisation if application submitted on behalf of an individual
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)
    return msg

def send_external_submit_email_notification(request, proposal):
    # if proposal.apiary_group_application_type:
    #     email = ApiaryExternalSubmitSendNotificationEmail()
    # else:
    #     email = ExternalSubmitSendNotificationEmail()
    email = ExternalSubmitSendNotificationEmail()
    url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    if "-internal" in url:
        # remove '-internal'. This email is for external submitters 
        url = ''.join(url.split('-internal'))

    context = {
        'proposal': proposal,
        'submitter': proposal.submitter.get_full_name(),
        'url': url
    }

    all_ccs = []
    #if proposal.applicant and proposal.applicant.email:
    #if proposal.applicant and proposal.applicant.email != proposal.submitter.email:
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email and proposal.applicant.email:
        cc_list = proposal.applicant.email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(proposal.submitter.email, cc= all_ccs, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    # Don't log organisation if application submitted on behalf of an individual
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)
    return msg

#send email when Proposal is 'proposed to decline' by assessor.
def send_approver_decline_email_notification(reason, request, proposal):
    # if proposal.apiary_group_application_type:
    #     email = ApiaryApproverDeclineSendNotificationEmail()
    # else:
    #     email = ApproverDeclineSendNotificationEmail()
    email = ApproverDeclineSendNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': proposal.id}))
    assessor_name=proposal.assigned_officer.get_full_name() if proposal.assigned_officer else ''
    context = {
        'proposal': proposal,
        'reason': reason,
        'url': url,
        'assessor_name': assessor_name,
        'greeting': 'Approver',
        'proposal_assess_help_page': get_proposal_assess_help_url(),
        'assessor_footer': True,
        'DAS_sharepoint_page': get_das_sharepoint_url(),
    }

    msg = email.send(proposal.approver_recipients, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_approver_approve_email_notification(request, proposal):
    # if proposal.apiary_group_application_type:
    #     email = ApiaryApproverApproveSendNotificationEmail()
    # else:
    #     email = ApproverApproveSendNotificationEmail()
    email = ApproverApproveSendNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': proposal.id}))
    assessor_name=proposal.assigned_officer.get_full_name() if proposal.assigned_officer else ''
    context = {
        'start_date' : proposal.proposed_issuance_approval.get('start_date'),
        'expiry_date' : proposal.proposed_issuance_approval.get('expiry_date'),
        'details': proposal.proposed_issuance_approval.get('details'),
        'proposal': proposal,
        'url': url,
        'assessor_name': assessor_name,
        # 'greeting': 'Assessor',
        'greeting': 'Approver',
        'proposal_approver_help_page': get_proposal_approver_help_url(),
        'assessor_footer': True,
        'DAS_sharepoint_page': get_das_sharepoint_url(),
        'assessment_reminder_days': get_assessment_reminder_days(),
    }
    msg = email.send(proposal.approver_recipients, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)


def send_proposal_decline_email_notification(proposal,request,proposal_decline):
    # if proposal.apiary_group_application_type:
    #     email = ApiaryProposalDeclineSendNotificationEmail()
    # else:
    #     email = ProposalDeclineSendNotificationEmail()
    email = ProposalDeclineSendNotificationEmail()
    reason=proposal_decline.reason
    context = {
        'proposal': proposal,
        'reason': reason,
    }
    cc_list = proposal_decline.cc_email
    all_ccs = []
    if cc_list:
        all_ccs = cc_list.split(',')
    #if proposal.applicant:
    #if proposal.applicant and proposal.applicant.email != proposal.submitter.email:
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email and proposal.applicant.email:
     #   if proposal.applicant.email:
            all_ccs.append(proposal.applicant.email)

    msg = email.send(proposal.submitter.email, bcc=all_ccs, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)


def send_proposal_approver_sendback_email_notification(request, proposal):
    # if proposal.apiary_group_application_type:
    #     email = ApiaryApproverSendBackNotificationEmail()
    # else:
    #     email = ApproverSendBackNotificationEmail()
    email = ApproverSendBackNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': proposal.id}))
    approver_name=proposal.assigned_approver.get_full_name() if proposal.assigned_approver else ''
    context = {
        'proposal': proposal,
        'url': url,
        'approver_comment': proposal.approver_comment,
        'approver_name': approver_name,
        'greeting': 'Assessor',
        'proposal_assess_help_page': get_proposal_assess_help_url(),
        'assessor_footer': True,
        'DAS_sharepoint_page': get_das_sharepoint_url(),
        'assessment_reminder_days': get_assessment_reminder_days(),
    }

    msg = email.send(proposal.assessor_recipients, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)


def send_proposal_approval_email_notification(proposal,request):
    # if proposal.apiary_group_application_type:
    #     email = ApiaryProposalApprovalSendNotificationEmail()
    # else:
    #     email = ProposalApprovalSendNotificationEmail()
    email = ProposalApprovalSendNotificationEmail()
    if proposal.approval.reissued:
        email.subject= 'Your Approval has been reissued.'

    context = {
        'proposal': proposal,

    }
    cc_list = proposal.proposed_issuance_approval['cc_email']
    all_ccs = []
    if cc_list:
        all_ccs = cc_list.split(',')
    #if proposal.applicant:
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email and proposal.applicant.email:
     #   if proposal.applicant.email:
            all_ccs.append(proposal.applicant.email)

    licence_document= proposal.approval.licence_document._file
    if licence_document is not None:
        file_name = proposal.approval.licence_document.name
        attachment = (file_name, licence_document.file.read(), 'application/pdf')
        attachment = [attachment]
    else:
        attachment = []

    msg = email.send(proposal.submitter.email, bcc= all_ccs, attachments=attachment, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_site_transfer_approval_email_notification(proposal, request, approval):
    email = ApiaryProposalApprovalSiteTransferSendNotificationEmail()
    if approval.reissued:
        email.subject= 'Your Licence has been reissued.'

    context = {
        'approval': approval,
        'proposal': proposal,
    }
    cc_list = proposal.proposed_issuance_approval['cc_email']
    all_ccs = []
    if cc_list:
        all_ccs = cc_list.split(',')
    #if proposal.applicant:
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email and proposal.applicant.email:
     #   if proposal.applicant.email:
            all_ccs.append(proposal.applicant.email)

    licence_document= approval.licence_document._file
    if licence_document is not None:
        file_name = approval.licence_document.name
        attachment = (file_name, licence_document.file.read(), 'application/pdf')
        attachment = [attachment]
    else:
        attachment = []

    #msg = email.send(proposal.submitter.email, bcc= all_ccs, attachments=attachment, context=context)
    msg = email.send(approval.relevant_applicant_email, bcc= all_ccs, attachments=attachment, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_assessment_reminder_email_notification(proposal):
    # if proposal.apiary_group_application_type:
    #     email = ApiaryAssessmentReminderSendNotificationEmail()
    # else:
    #     email = AssessmentReminderSendNotificationEmail()
    email = AssessmentReminderSendNotificationEmail()
    #url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': proposal.id}))
    url=settings.SITE_URL if settings.SITE_URL else ''
    url+=reverse('internal-proposal-detail',kwargs={'proposal_pk': proposal.id})
    if "-internal" not in url:
        # add it. This email is for internal staff (assessors)
        url = '-internal.{}'.format(settings.SITE_DOMAIN).join(url.split('.' + settings.SITE_DOMAIN))
    assessor_name=proposal.assigned_officer.get_full_name() if proposal.assigned_officer else ''

    context = {
        'proposal': proposal,
        'url': url,
        'assessor_name': assessor_name,
        'greeting': 'Assessor',
        'proposal_assess_help_page': get_proposal_assess_help_url(),
        'assessor_footer': True,
        'DAS_sharepoint_page': get_das_sharepoint_url(),
        'assessment_reminder_days': get_assessment_reminder_days(),
    }

    msg = email.send(proposal.assessor_recipients, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    # try:
    #     sender_user = EmailUser.objects.get(email__icontains=sender)
    # except:
    #     EmailUser.objects.create(email=sender, password='')
    #     sender_user = EmailUser.objects.get(email__icontains=sender)
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)
    return msg

def send_proposal_prefill_request_sent_email_notification(proposal, user):
    email = ProposalPrefillRequestSentSendNotificationEmail()
    #base_url = settings.BASE_URL if settings.BASE_URL.endswith('/') else settings.BASE_URL + '/'
    #url = base_url + reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id})
    url = settings.BASE_URL + reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id})
    context = {
        'proposal': proposal,
        'url': url,
    }

    msg = email.send(user.email, bcc=[], attachments=[], context=context)
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_proposal_prefill_completed_email_notification(proposal, user):
    email = ProposalPrefillCompletedSendNotificationEmail()
    #base_url = settings.BASE_URL if settings.BASE_URL.endswith('/') else settings.BASE_URL + '/'
    #url = base_url + reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id})
    url = settings.BASE_URL + reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id})
    context = {
        'proposal': proposal,
        'url': url,
    }

    msg = email.send(user.email, bcc=[], attachments=[], context=context)
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_proposal_prefill_error_email_notification(proposal, user, task_id):
    email = ProposalPrefillErrorSendNotificationEmail()
    #base_url = settings.BASE_URL if settings.BASE_URL.endswith('/') else settings.BASE_URL + '/'
    #url = base_url + reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id})
    url = settings.BASE_URL + reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id})
    context = {
        'proposal': proposal,
        'task_id': task_id,
        #'greeting': 'Assessor',
        'url': url,
    }

    msg = email.send(user.email, context=context)
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_proposal_refresh_request_sent_email_notification(proposal, user):
    email = ProposalRefreshRequestSentSendNotificationEmail()
    #base_url = settings.BASE_URL if settings.BASE_URL.endswith('/') else settings.BASE_URL + '/'
    #url = base_url + reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id})
    url = settings.BASE_URL + reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id})
    context = {
        'proposal': proposal,
        'url': url,
    }

    msg = email.send(user.email, bcc=[], attachments=[], context=context)
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_proposal_refresh_completed_email_notification(proposal, user):
    email = ProposalRefreshCompletedSendNotificationEmail()
    #base_url = settings.BASE_URL if settings.BASE_URL.endswith('/') else settings.BASE_URL + '/'
    #url = base_url + reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id})
    url = settings.BASE_URL + reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id})
    context = {
        'proposal': proposal,
        'url': url,
    }

    msg = email.send(user.email, bcc=[], attachments=[], context=context)
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_proposal_refresh_error_email_notification(proposal, user, task_id):
    email = ProposalRefreshErrorSendNotificationEmail()
    #base_url = settings.BASE_URL if settings.BASE_URL.endswith('/') else settings.BASE_URL + '/'
    #url = base_url + reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id})
    url = settings.BASE_URL + reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id})
    context = {
        'proposal': proposal,
        'task_id': task_id,
        'greeting': 'Assessor',
        'url': url,
    }

    msg = email.send(user.email, context=context)
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_proposal_test_sqq_request_sent_email_notification(proposal, user, task_id):
    email = ProposalTestSqqRequestSentSendNotificationEmail()
    context = {
        'proposal': proposal,
        'task_id': task_id,
    }

    msg = email.send(user.email, bcc=[], attachments=[], context=context)
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_proposal_test_sqq_completed_email_notification(proposal, user, task_id, data):
    email = ProposalTestSqqCompletedSendNotificationEmail()
    sqs_response = json.dumps(data, indent=4)
    context = {
        'proposal': proposal,
        #'url': url,
        'task_id': task_id,
        'sqs_response': sqs_response,
    }

     # for attachment
#    dt = datetime.now().strftime('%Y%m%dT%H%M%S')
#    filename = f'TEST_SQQ_{proposal.lodgement_number}_{dt}.json'
#    #attachment = MIMEText(sqs_response)
#    attachment = sqs_response
#    attachment.add_header('Content-Disposition', 'attachment', filename=filename)

    msg = email.send(user.email, bcc=[], attachments=[], context=context)
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_proposal_test_sqq_error_email_notification(proposal, user, task_id):
    email = ProposalTestSqqErrorSendNotificationEmail()
    context = {
        'proposal': proposal,
        'task_id': task_id,
        'greeting': 'Assessor',
    }

    msg = email.send(user.email, context=context)
    sender = get_sender_user()
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)



def _log_proposal_referral_email(email_message, referral, sender=None):
    from disturbance.components.proposals.models import ProposalLogEntry
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_str(sender) if sender else smart_str(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ','.join(email_message.to)
        else:
            to = smart_str(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(all_ccs)

    else:
        text = smart_str(email_message)
        subject = ''
        to = referral.proposal.applicant.email if referral.proposal.applicant.email else ''
        fromm = smart_str(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = referral.referral

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'proposal': referral.proposal,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = ProposalLogEntry.objects.create(**kwargs)

    return email_entry

def _log_proposal_email(email_message, proposal, sender=None):
    from disturbance.components.proposals.models import ProposalLogEntry
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_str(sender) if sender else smart_str(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ','.join(email_message.to)
        else:
            to = smart_str(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(all_ccs)

    else:
        text = smart_str(email_message)
        subject = ''
        to = proposal.submitter.email
        fromm = smart_str(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = proposal.submitter

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'proposal': proposal,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = ProposalLogEntry.objects.create(**kwargs)

    return email_entry


def _log_org_email(email_message, organisation, customer ,sender=None):
    from disturbance.components.organisations.models import OrganisationLogEntry
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_str(sender) if sender else smart_str(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ','.join(email_message.to)
        else:
            to = smart_str(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(all_ccs)

    else:
        text = smart_str(email_message)
        subject = ''
        to = customer
        fromm = smart_str(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = customer

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'organisation': organisation,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = OrganisationLogEntry.objects.create(**kwargs)

    return email_entry

def _log_user_email(email_message, emailuser, customer ,sender=None):
    from ledger.accounts.models import EmailUserLogEntry
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_str(sender) if sender else smart_str(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ','.join(email_message.to)
        else:
            to = smart_str(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(all_ccs)

    else:
        text = smart_str(email_message)
        subject = ''
        to = customer
        fromm = smart_str(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = customer

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'emailuser': emailuser,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = EmailUserLogEntry.objects.create(**kwargs)

    return email_entry


#def _log_org_email(email_message, organisation, customer ,sender=None):
#    from disturbance.components.organisations.models import OrganisationLogEntry
#    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
#        # TODO this will log the plain text body, should we log the html instead
#        text = email_message.body
#        subject = email_message.subject
#        fromm = smart_text(sender) if sender else smart_text(email_message.from_email)
#        # the to email is normally a list
#        if isinstance(email_message.to, list):
#            to = ','.join(email_message.to)
#        else:
#            to = smart_text(email_message.to)
#        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
#        all_ccs = []
#        if email_message.cc:
#            all_ccs += list(email_message.cc)
#        if email_message.bcc:
#            all_ccs += list(email_message.bcc)
#        all_ccs = ','.join(all_ccs)
#
#    else:
#        text = smart_text(email_message)
#        subject = ''
#        to = customer
#        fromm = smart_text(sender) if sender else SYSTEM_NAME
#        all_ccs = ''
#
#    customer = customer
#
#    staff = sender
#
#    kwargs = {
#        'subject': subject,
#        'text': text,
#        'organisation': organisation,
#        'customer': customer,
#        'staff': staff,
#        'to': to,
#        'fromm': fromm,
#        'cc': all_ccs
#    }
#
#    email_entry = OrganisationLogEntry.objects.create(**kwargs)
#
#    return email_entry
#
#def _log_user_email(email_message, emailuser, referral_group_email_list, sender=None):
#    from ledger.accounts.models import EmailUserLogEntry
#    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
#        # TODO this will log the plain text body, should we log the html instead
#        text = email_message.body
#        subject = email_message.subject
#        fromm = smart_text(sender) if sender else smart_text(email_message.from_email)
#        # the to email is normally a list
#        if isinstance(email_message.to, list):
#            to = ','.join(email_message.to)
#        else:
#            to = smart_text(email_message.to)
#        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
#        all_ccs = []
#        if email_message.cc:
#            all_ccs += list(email_message.cc)
#        if email_message.bcc:
#            all_ccs += list(email_message.bcc)
#        all_ccs = ','.join(all_ccs)
#
#    else:
#        text = smart_text(email_message)
#        subject = ''
#        to = customer
#        fromm = smart_text(sender) if sender else SYSTEM_NAME
#        all_ccs = ''
#
#    for customer in referral_group_email_list:
#        customer_email_user = EmailUser.objects.get(email=customer)
#
#        staff = sender
#
#        kwargs = {
#            'subject': subject,
#            'text': text,
#            #'emailuser': emailuser,
#            'emailuser': customer_email_user,
#            'customer': customer_email_user,
#            'staff': staff,
#            'to': to,
#            'fromm': fromm,
#            'cc': all_ccs
#        }
#
#        email_entry = EmailUserLogEntry.objects.create(**kwargs)
#    # TODO - fix return statement
#    return email_entry
#
