from __future__ import unicode_literals
from ledger.accounts.models import EmailUser
from django.conf import settings

import logging

from rest_framework import serializers

from disturbance.components.organisations.models import Organisation
logger = logging.getLogger(__name__)

def belongs_to(user, group_name):
    """
    Check if the user belongs to the given group.
    :param user:
    :param group_name:
    :return:
    """
    return user.groups.filter(name=group_name).exists()

def is_model_backend(request):
    # Return True if user logged in via single sign-on (i.e. an internal)
    return 'ModelBackend' in request.session.get('_auth_user_backend')

def is_email_auth_backend(request):
    # Return True if user logged in via social_auth (i.e. an external user signing in with a login-token)
    return 'EmailAuth' in request.session.get('_auth_user_backend')

def is_disturbance_admin(request):
  #  #logger.info('settings.ADMIN_GROUP: {}'.format(settings.ADMIN_GROUP))
    return request.user.is_authenticated() and is_model_backend(request) and in_dbca_domain(request) and (belongs_to(request.user, settings.ADMIN_GROUP))

def is_apiary_admin(request):
  #  #logger.info('settings.ADMIN_GROUP: {}'.format(settings.ADMIN_GROUP))
    return request.user.is_authenticated() and is_model_backend(request) and in_dbca_domain(request) and (belongs_to(request.user, settings.APIARY_ADMIN_GROUP))

def is_das_apiary_admin(request):
  #  #logger.info('settings.ADMIN_GROUP: {}'.format(settings.ADMIN_GROUP))
    return request.user.is_authenticated() and is_model_backend(request) and in_dbca_domain(request) and (belongs_to(request.user, settings.DAS_APIARY_ADMIN_GROUP))

def in_dbca_domain(request):
    user = request.user
    domain = user.email.split('@')[1]
    if domain in settings.DEPT_DOMAINS:
        if not user.is_staff:
            # hack to reset department user to is_staff==True, if the user logged in externally (external departmentUser login defaults to is_staff=False)
            user.is_staff = True
            user.save()
        return True
    return False

def is_in_organisation_contacts(request, organisation):
    return request.user.email in organisation.contacts.all().values_list('email', flat=True)

def is_approved_external_user(request):
    http_host = request.META.get('HTTP_HOST', None)
    if http_host and ('apiary' in http_host.lower() or http_host in settings.APIARY_URL):
        if belongs_to(request.user, settings.APPROVED_APIARY_EXTERNAL_USERS_GROUP):
            return True
    else:
        if belongs_to(request.user, settings.APPROVED_DAS_EXTERNAL_USERS_GROUP):
            return True
    return False

def is_departmentUser(request):
    return request.user.is_authenticated() and ( (is_model_backend(request) and in_dbca_domain(request)) or is_approved_external_user(request) )

def is_customer(request):
    return request.user.is_authenticated() and is_email_auth_backend(request)

def is_internal(request):
    return is_departmentUser(request)

def get_all_officers():
    return EmailUser.objects.filter(groups__name='Disturbance Admin')

def is_authorised_to_modify(request, instance):
    authorised = True

    # print('1. Application', instance.application_type )
    # print("2. Apiary", str(instance.application_type) == "Apiary")

    # Getting Organisation is different in DAS and Apiary
    if str(instance.application_type) == "Apiary":
        # Get Organisation if in Apiary
        applicant = instance.relevant_applicant
        # print("3. Apiary Applicant", applicant)
    else:
        # Get Organisation if in DAS
        # There can only ever be one Organisation associated with an application so it is
        # ok to just pull the first element from organisation_set.
        applicant = instance.applicant.organisation.organisation_set.all()[0]
        # print("4. DAS Applicant", applicant)
    applicantIsIndividual = isinstance(applicant, EmailUser)
    # print('5. applicantIsIndividual', applicantIsIndividual)
    if is_internal(request):
        # the status must be 'with_assessor'
        authorised &= instance.processing_status == 'with_assessor'
        # print("6. Internal with assessor", instance.processing_status == 'with_assessor')
        # the user must be an assessor for this type of application
        authorised &= instance.can_process()
        # print('7. Can process', instance.can_process())
    elif is_customer(request):
        # the status of the application must be DRAFT for customer to modify
        authorised &= instance.processing_status == 'draft'
        # print('8. Processing status draft', instance.processing_status == 'draft')
        if applicantIsIndividual:
                        # it is an individual so the applicant and submitter must be the same
            authorised &= str(request.user.email) == str(instance.relevant_applicant)
            # print('9. Indiv submitter matches applicant', str(request.user.email) == str(instance.relevant_applicant))
        else:
            # the applicant is an organisation so make sure the submitter is in the organisation
            authorised &= is_in_organisation_contacts(request, instance.relevant_applicant)
            # print('10. Applicant is in Org', is_in_organisation_contacts(request, instance.relevant_applicant))

    # print('11. Authorised', authorised)
    if not authorised:
        raise serializers.ValidationError('You are not authorised to modify this application.')

def is_authorised_to_modify_draft(request, instance):
    #import ipdb; ipdb.set_trace()
    authorised = True

    # Getting Organisation is different in DAS and Apiary
    if str(instance.application_type) == "Apiary":
        # Get Organisation if in Apiary
        applicant = instance.relevant_applicant
    else:
        # Get Organisation if in DAS
        # There can only ever be one Organisation associated with an application so it is
        # ok to just pull the first element from organisation_set.
        applicant = instance.applicant.organisation.organisation_set.all()[0]
    applicantIsIndividual = isinstance(applicant, EmailUser)
    if instance.processing_status=='draft':
        if is_customer(request):
            # the status of the application must be DRAFT for customer to modify
            if applicantIsIndividual:
                # it is an individual so the applicant and submitter must be the same
                authorised &= str(request.user.email) == str(instance.relevant_applicant)
            else:
                # the applicant is an organisation so make sure the submitter is in the organisation
                authorised &= is_in_organisation_contacts(request, instance.relevant_applicant)
        else:
            authorised = False
    else:
        if is_internal(request):
            # the status must be 'with_assessor'
            # the user must be an assessor for this type of application
            authorised &= instance.can_assess()
        else:
            authorised=False

    if not authorised:
        raise serializers.ValidationError('You are not authorised to modify this application.')