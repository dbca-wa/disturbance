import logging
from io import BytesIO
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.urls import reverse
from django.utils.encoding import smart_str
from django.conf import settings

from disturbance.components.emails.emails import TemplateEmailBase
from ledger.accounts.models import EmailUser

from disturbance.components.main.email import _extract_email_headers
from disturbance.components.main.models import Region, District
from disturbance.settings import SITE_DOMAIN, SITE_URL

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

class ApprovalExpireNotificationEmail(TemplateEmailBase):
    subject = 'Your Approval has expired.'
    html_template = 'disturbance/emails/approval_expire_notification.html'
    txt_template = 'disturbance/emails/approval_expire_notification.txt'


class ApprovalCancelNotificationEmail(TemplateEmailBase):
    subject = 'Your Approval has been cancelled.'
    html_template = 'disturbance/emails/approval_cancel_notification.html'
    txt_template = 'disturbance/emails/approval_cancel_notification.txt'


class ApprovalSuspendNotificationEmail(TemplateEmailBase):
    subject = 'Your Approval has been suspended.'
    html_template = 'disturbance/emails/approval_suspend_notification.html'
    txt_template = 'disturbance/emails/approval_suspend_notification.txt'


class ApprovalSurrenderNotificationEmail(TemplateEmailBase):
    subject = 'Your Approval has been surrendered.'
    html_template = 'disturbance/emails/approval_surrender_notification.html'
    txt_template = 'disturbance/emails/approval_surrender_notification.txt'


class ApprovalReinstateNotificationEmail(TemplateEmailBase):
    subject = 'Your Approval has been reinstated.'
    html_template = 'disturbance/emails/approval_reinstate_notification.html'
    txt_template = 'disturbance/emails/approval_reinstate_notification.txt'


class ApprovalRenewalNotificationEmail(TemplateEmailBase):
    subject = 'Your Approval is due for renewal.'
    html_template = 'disturbance/emails/approval_renewal_notification.html'
    txt_template = 'disturbance/emails/approval_renewal_notification.txt'


def send_approval_expire_email_notification(approval):
    email = ApprovalExpireNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
        'proposal': proposal
    } 
    all_ccs = []
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email:
        cc_list = proposal.relevant_applicant_email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(proposal.submitter.email,cc=all_ccs, context=context)
    sender = get_sender_user()

    _log_approval_email(msg, approval, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)


def send_approval_cancel_email_notification(approval, future_cancel=False):
    email = ApprovalCancelNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
        'future_cancel': future_cancel,
        'proposal': proposal,
        
    }

    all_ccs = []
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email:
        cc_list = proposal.relevant_applicant_email

        if cc_list:
            all_ccs = [cc_list]

    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        EmailUser.objects.create(email=sender, password='')
        sender_user = EmailUser.objects.get(email__icontains=sender)    
    msg = email.send(proposal.submitter.email, cc=all_ccs, context=context)
    sender = settings.DEFAULT_FROM_EMAIL    
    _log_approval_email(msg, approval, sender=sender_user)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender_user)


def send_approval_suspend_email_notification(approval, future_suspend=False):
    email = ApprovalSuspendNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
        'details': approval.suspension_details['details'],
        'from_date': approval.suspension_details['from_date'],
        'to_date': approval.suspension_details['to_date'],
        'future_suspend': future_suspend,
        'proposal': proposal,
    }

    all_ccs = []
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email:
        cc_list = proposal.relevant_applicant_email
        if cc_list:
            all_ccs = [cc_list]

    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        EmailUser.objects.create(email=sender, password='')
        sender_user = EmailUser.objects.get(email__icontains=sender)   
    msg = email.send(proposal.submitter.email, cc=all_ccs, context=context)
    sender = settings.DEFAULT_FROM_EMAIL    
    _log_approval_email(msg, approval, sender=sender_user)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender_user)


def send_approval_surrender_email_notification(approval, future_surrender=False):
    email = ApprovalSurrenderNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
        'details': approval.surrender_details['details'],
        'surrender_date': approval.surrender_details['surrender_date'], 
        'future_surrender': future_surrender  ,
        'proposal' : proposal,
    }
    all_ccs = []
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email:
        cc_list = proposal.relevant_applicant_email
        if cc_list:
            all_ccs = [cc_list]

    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        EmailUser.objects.create(email=sender, password='')
        sender_user = EmailUser.objects.get(email__icontains=sender)   
    msg = email.send(proposal.submitter.email, cc=all_ccs, context=context)
    _log_approval_email(msg, approval, sender=sender_user)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender_user)

#approval renewal notice
def send_approval_renewal_email_notification(approval):
    email = ApprovalRenewalNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
        'proposal': approval.current_proposal,
        'submitter': approval.current_proposal.submitter.get_full_name(),
                    
    }
    all_ccs = []
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email:
        cc_list = proposal.relevant_applicant_email
        if cc_list:
            all_ccs = [cc_list]

    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        EmailUser.objects.create(email=sender, password='')
        sender_user = EmailUser.objects.get(email__icontains=sender)

    if approval.renewal_document is not None:
        file_name = approval.renewal_document.name
        attachment = (file_name, approval.renewal_document._file.file.read(), 'application/pdf')
        attachment = [attachment]
    else:
        attachment = []
    msg = email.send(proposal.submitter.email, cc=all_ccs, attachments=attachment, context=context)
    sender = settings.DEFAULT_FROM_EMAIL    
    _log_approval_email(msg, approval, sender=sender_user)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender_user)


def send_approval_reinstate_email_notification(approval, request):
    email = ApprovalReinstateNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
                
    }    
    all_ccs = []
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email:
        cc_list = proposal.relevant_applicant_email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(proposal.submitter.email,cc=all_ccs, context=context)
    sender = get_sender_user()   
    _log_approval_email(msg, approval, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)


def _log_approval_email(email_message, approval, sender=None):
    from disturbance.components.approvals.models import ApprovalLogEntry
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_str(sender) if sender else smart_str(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ','.join(list(filter(None, email_message.to)))
        else:
            to = smart_str(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(list(filter(None, all_ccs)))

    else:
        text = smart_str(email_message)
        subject = ''
        to = approval.current_proposal.submitter.email
        fromm = smart_str(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = approval.current_proposal.submitter

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'approval': approval,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = ApprovalLogEntry.objects.create(**kwargs)

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
            to = ','.join(list(filter(None, email_message.to)))
        else:
            to = smart_str(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(list(filter(None, all_ccs)))

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
