import logging
from io import BytesIO
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.urls import reverse
from django.utils.encoding import smart_text
from django.conf import settings

from disturbance.components.das_payments.awaiting_payment_invoice_pdf import \
    create_annual_rental_fee_awaiting_payment_confirmation
from disturbance.components.das_payments.invoice_pdf import create_annual_rental_fee_invoice
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

### Apiary templates

class ApiaryApprovalExpireNotificationEmail(TemplateEmailBase):
    subject = 'Your Licence has expired.'
    html_template = 'disturbance/emails/apiary_approval_expire_notification.html'
    txt_template = 'disturbance/emails/apiary_approval_expire_notification.txt'


class ApiaryApprovalCancelNotificationEmail(TemplateEmailBase):
    subject = 'Your Licence has been cancelled.'
    html_template = 'disturbance/emails/apiary_approval_cancel_notification.html'
    txt_template = 'disturbance/emails/apiary_approval_cancel_notification.txt'


class ApiaryApprovalSuspendNotificationEmail(TemplateEmailBase):
    subject = 'Your Licence has been suspended.'
    html_template = 'disturbance/emails/apiary_approval_suspend_notification.html'
    txt_template = 'disturbance/emails/apiary_approval_suspend_notification.txt'


class ApiaryApprovalSurrenderNotificationEmail(TemplateEmailBase):
    subject = 'Your Licence has been surrendered.'
    html_template = 'disturbance/emails/apiary_approval_surrender_notification.html'
    txt_template = 'disturbance/emails/apiary_approval_surrender_notification.txt'


class ApiaryApprovalReinstateNotificationEmail(TemplateEmailBase):
    subject = 'Your Licence has been reinstated.'
    html_template = 'disturbance/emails/apiary_approval_reinstate_notification.html'
    txt_template = 'disturbance/emails/apiary_approval_reinstate_notification.txt'


class ApiaryApprovalRenewalNotificationEmail(TemplateEmailBase):
    subject = 'Your Licence is due for renewal.'
    html_template = 'disturbance/emails/apiary_approval_renewal_notification.html'
    txt_template = 'disturbance/emails/apiary_approval_renewal_notification.txt'


class ApprovalAnnualRentalFeeInvoiceEmail(TemplateEmailBase):
    subject = 'Annual site fee invoice for your licensed apiary sites.'
    html_template = 'disturbance/emails/approval_annual_rental_fee_invoice.html'
    txt_template = 'disturbance/emails/approval_annual_rental_fee_invoice.txt'


class ApprovalAnnualRentalFeeAwaitingPaymentConfirmationEmail(TemplateEmailBase):
    #subject = 'Annual site fee awaiting payment confirmation for your licence has been issued.'
    subject = 'Annual site fee invoice for your licensed apiary sites.'
    html_template = 'disturbance/emails/approval_annual_rental_fee_awaiting_payment_confirmation.html'
    txt_template = 'disturbance/emails/approval_annual_rental_fee_awaiting_payment_confirmation.txt'


class ContactLicenceHolderEmail(TemplateEmailBase):
    subject = 'Someone is interested in your apiary site available.'
    html_template = 'disturbance/emails/contact_licence_holder_email.html'
    txt_template = 'disturbance/emails/contact_licence_holder_email.txt'


class OnSiteNotificationEmail(TemplateEmailBase):
    subject = 'On-site notification submitted for site'
    html_template = 'disturbance/emails/onsite-notification_email.html'
    txt_template = 'disturbance/emails/onsite-notification_email.txt'

class OnSiteNotificationUpdateEmail(TemplateEmailBase):
    subject = 'On-site notification update submitted for site'
    html_template = 'disturbance/emails/onsite-notification_update_email.html'
    txt_template = 'disturbance/emails/onsite-notification_update_email.txt'


def get_value_of_annual_rental_fee_awaiting_payment_confirmation(annual_rental_fee):
    invoice_buffer = BytesIO()
    create_annual_rental_fee_awaiting_payment_confirmation(invoice_buffer, annual_rental_fee)
    value = invoice_buffer.getvalue() # Get the value of the BytesIO buffer
    invoice_buffer.close()
    return value


def get_value_of_annual_rental_fee_invoice(approval, invoice):
    invoice_buffer = BytesIO()
    create_annual_rental_fee_invoice(invoice_buffer, approval, invoice)
    value = invoice_buffer.getvalue() # Get the value of the BytesIO buffer
    invoice_buffer.close()
    return value


def send_contact_licence_holder_email(apiary_site_on_approval, comments, sender):
    email = ContactLicenceHolderEmail()

    context = {
        'apiary_site': apiary_site_on_approval.apiary_site,
        'comments': comments,
        'sender': sender,
    }
    to_address = [apiary_site_on_approval.approval.relevant_applicant_email,]
    cc = []
    bcc = []

    msg = email.send(
        to_address,
        context=context,
        attachments=[],
        cc=cc,
        bcc=bcc,
    )

    # sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = settings.DEFAULT_FROM_EMAIL
    email_data = _extract_email_headers(msg, sender=sender)
    return email_data


from disturbance.components.main.utils import get_region_district
def send_on_site_notification_email(request_data, sender, update=False):

    def get_recipients():
        rd=get_region_district(asoa.wkb_geometry)

        try:
            district=District.objects.get(name__icontains=rd.split('/')[1])
        except:
            try:
                district_name = rd.title().split('/')[0].split(' ')[0]
                region = Region.objects.get(name=district_name)
                no_region_district_name = region.name + ' Region'
                district = District.objects.get(name=no_region_district_name)
            except:
                logger.error('Error sending onsite-notification email - District not found: {rd}')
                raise Exception(f'District not found: {rd}')
        
        try:
            recipients = ApiaryReferralGroup.objects.get(district=district).members_email
            return recipients
        except:
            logger.error('Error sending onsite-notification email - Cannot find Apiary Referral Group for District {district.name}')
            raise Exception(f'Cannot find Apiary Referral Group for District {district.name}')
            

    email = OnSiteNotificationUpdateEmail() if update else OnSiteNotificationEmail()

    from disturbance.components.approvals.models import ApiarySiteOnApproval
    from disturbance.components.proposals.models import ApiaryReferralGroup
    from disturbance.components.organisations.models import Organisation
    asoa = ApiarySiteOnApproval.objects.get(id=request_data.get('apiary_site_on_approval_id'))
    period_from = request_data.get('period_from')
    period_to = request_data.get('period_to')
    comments = request_data.get('comments')
    hives_loc = request_data.get('hives_loc')
    hives_num = request_data.get('hives_num')
    people_names = request_data.get('people_names')
    flora = request_data.get('flora')
    approval = asoa.approval
    proposal = asoa.approval.current_proposal

    applicant = approval.relevant_applicant if isinstance(approval.relevant_applicant, Organisation) else approval.relevant_applicant.get_full_name()
    if isinstance(approval.relevant_applicant, Organisation):
        applicant = approval.relevant_applicant.name
        delegate = approval.relevant_applicant.delegates.all()[0]
        contact = delegate.phone_number if delegate.phone_number else delegate.mobile_number
    else:
        applicant = approval.relevant_applicant.get_full_name()
        contact = approval.relevant_applicant.phone_number if approval.relevant_applicant.phone_number else approval.relevant_applicant.mobile_number

    context = {
        'apiary_site': asoa.apiary_site,
        'approval': approval,
        'applicant': applicant,
        'contact': contact,
        'period_from': period_from,
        'period_to': period_to,
        'comments': comments,
        'hives_loc': hives_loc,
        'hives_num': hives_num,
        'people_names': people_names,
        'flora': flora,
        'sender': sender,
        'licence_url': SITE_URL + f'{reverse("external")}approval/{approval.id}'
    }

    # sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    #sender = settings.DEFAULT_FROM_EMAIL
    cc = [approval.relevant_applicant.email] if hasattr(approval.relevant_applicant, 'email') else []
    msg = email.send(get_recipients(), cc=cc, context=context)
    _log_approval_email(msg, approval, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)


def send_annual_rental_fee_awaiting_payment_confirmation(approval, annual_rental_fee, invoice):
    email = ApprovalAnnualRentalFeeAwaitingPaymentConfirmationEmail()
    path_to_pay = reverse('annual_rental_fee', kwargs={'annual_rental_fee_id': annual_rental_fee.id})
    url_to_pay = SITE_DOMAIN + path_to_pay
    if 'localhost' in SITE_DOMAIN:
        url = 'http://localhost:8071' + path_to_pay
    else:
        url = SITE_URL + path_to_pay

    context = {
        'approval': approval,
        'annual_rental_fee': annual_rental_fee,
        'invoice': invoice,
        'url_to_pay': url,
    }

    attachments = []
    # contents = get_value_of_annual_rental_fee_awaiting_payment_confirmation(annual_rental_fee)
    # attachments.append(('awaiting_payment_confirmation.pdf', contents, 'application/pdf'))
    contents = get_value_of_annual_rental_fee_invoice(approval, invoice)
    attachments.append(('invoice#{}.pdf'.format(invoice.reference), contents, 'application/pdf'))

    to_address = [approval.relevant_applicant_email]
    cc = []
    bcc = []

    msg = email.send(
        to_address,
        context=context,
        attachments=attachments,
        cc=cc,
        bcc=bcc,
    )

    # sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = settings.DEFAULT_FROM_EMAIL
    email_data = _extract_email_headers(msg, sender=sender)
    return email_data


def send_annual_rental_fee_invoice(approval, invoice, to_email_addresses):
    email = ApprovalAnnualRentalFeeInvoiceEmail()

    context = {
        'approval': approval,
    }

    attachments = []
    contents = get_value_of_annual_rental_fee_invoice(approval, invoice)
    attachments.append(('invoice#{}.pdf'.format(invoice.reference), contents, 'application/pdf'))

    to_address = to_email_addresses
    cc = []
    bcc = []

    msg = email.send(
        to_address,
        context=context,
        attachments=attachments,
        cc=cc,
        bcc=bcc,
    )

    # sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = settings.DEFAULT_FROM_EMAIL
    email_data = _extract_email_headers(msg, sender=sender)
    return email_data


def send_approval_expire_email_notification(approval):
    if approval.apiary_approval:
        email = ApiaryApprovalExpireNotificationEmail()
    else:
        email = ApprovalExpireNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
        'proposal': proposal
    } 
    all_ccs = []
    #if proposal.applicant.email:
     #   cc_list = proposal.applicant.email
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email:
        cc_list = proposal.relevant_applicant_email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(proposal.submitter.email,cc=all_ccs, context=context)
    #sender = settings.DEFAULT_FROM_EMAIL
    sender = get_sender_user()
    # try:
    #   sender_user = EmailUser.objects.get(email__icontains=sender)
    # except:
    #     EmailUser.objects.create(email=sender, password='')
    #     sender_user = EmailUser.objects.get(email__icontains=sender)

    _log_approval_email(msg, approval, sender=sender)
    if proposal.applicant:
        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)


def send_approval_cancel_email_notification(approval, future_cancel=False):
    if approval.apiary_approval:
        email = ApiaryApprovalCancelNotificationEmail()
    else:
        email = ApprovalCancelNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
        'future_cancel': future_cancel
        
    }

    all_ccs = []
    #if proposal.applicant.email:
     #   cc_list = proposal.applicant.email
    #if proposal.relevant_applicant_email:
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email:
    #if proposal.relevant_applicant_email and proposal.relevant_applicant_email != proposal.submitter.email:
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
    if approval.apiary_approval:
        email = ApiaryApprovalSuspendNotificationEmail()
    else:
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
    #if proposal.applicant.email:
     #   cc_list = proposal.applicant.email
    #if proposal.relevant_applicant_email:
    #if proposal.relevant_applicant_email and proposal.relevant_applicant_email != proposal.submitter.email:
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
    if approval.apiary_approval:
        email = ApiaryApprovalSurrenderNotificationEmail()
    else:
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
    #if proposal.applicant and proposal.applicant.email:
     #   cc_list = proposal.applicant.email
    #if proposal.relevant_applicant_email:
    #if proposal.relevant_applicant_email and proposal.relevant_applicant_email != proposal.submitter.email:
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
    #import ipdb; ipdb.set_trace()
    if approval.apiary_approval:
        email = ApiaryApprovalRenewalNotificationEmail()
    else:
        email = ApprovalRenewalNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
        'proposal': approval.current_proposal,
        'submitter': approval.current_proposal.submitter.get_full_name(),
                    
    }
    all_ccs = []
    #if proposal.applicant.email:
     #   cc_list = proposal.applicant.email
    #if proposal.relevant_applicant_email:
    #if proposal.relevant_applicant_email and proposal.relevant_applicant_email != proposal.submitter.email:
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
    #attach renewal notice
    #renewal_document= approval.renewal_document._file
    # if approval.apiary_renewal_document is not None:
    if approval.apiary_approval:
        # file_name = approval.apiary_renewal_document.name
        file_name = approval.relevant_renewal_document.name
        attachment = (file_name, approval.relevant_renewal_document._file.file.read(), 'application/pdf')
        attachment = [attachment]
    #renewal_document= approval.renewal_document._file
    elif approval.renewal_document is not None:
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
    if approval.apiary_approval:
        email = ApiaryApprovalReinstateNotificationEmail()
    else:
        email = ApprovalReinstateNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
                
    }    
    all_ccs = []
    #if proposal.applicant.email:
     #   cc_list = proposal.applicant.email
    #if proposal.relevant_applicant_email:
    #if proposal.relevant_applicant_email and proposal.relevant_applicant_email != proposal.submitter.email:
    if proposal.applicant and proposal.applicant.email != proposal.submitter.email:
        cc_list = proposal.relevant_applicant_email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(proposal.submitter.email,cc=all_ccs, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL 
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
        fromm = smart_text(sender) if sender else smart_text(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ','.join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(all_ccs)

    else:
        text = smart_text(email_message)
        subject = ''
        to = approval.current_proposal.submitter.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
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
        fromm = smart_text(sender) if sender else smart_text(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ','.join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(all_ccs)

    else:
        text = smart_text(email_message)
        subject = ''
        to = customer
        fromm = smart_text(sender) if sender else SYSTEM_NAME
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
