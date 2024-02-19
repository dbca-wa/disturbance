import logging
from datetime import datetime

from django.http import HttpResponse, Http404
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from ledger.payments.invoice.models import Invoice
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from disturbance.components.main.decorators import timeit
from disturbance.components.main.serializers import WaCoastSerializer, WaCoastOptimisedSerializer
from disturbance.components.main.utils import get_feature_in_wa_coastline_smoothed, get_feature_in_wa_coastline_original
from disturbance.helpers import is_internal, is_disturbance_admin, is_apiary_admin, is_das_apiary_admin, is_customer
from disturbance.forms import *
from disturbance.components.proposals.models import Referral, Proposal, HelpPage
from disturbance.components.compliances.models import Compliance
from disturbance.components.proposals.mixins import ReferralOwnerMixin
from django.core.management import call_command
from rest_framework.response import Response
from rest_framework import views
import os
import mimetypes
from disturbance.components.proposals.models import Proposal
from disturbance.components.organisations.models import Organisation,OrganisationContact
from disturbance.components.approvals.models import Approval
from django.db.models import Q

logger = logging.getLogger(__name__)


class InternalView(UserPassesTestMixin, TemplateView):
    template_name = 'disturbance/dash/index.html'

    def test_func(self):
        return is_internal(self.request)

    def get_context_data(self, **kwargs):
        context = super(InternalView, self).get_context_data(**kwargs)
        context['dev'] = settings.DEV_STATIC
        context['dev_url'] = settings.DEV_STATIC_URL
        if hasattr(settings, 'DEV_APP_BUILD_URL') and settings.DEV_APP_BUILD_URL:
            context['app_build_url'] = settings.DEV_APP_BUILD_URL
        return context


class ExternalView(LoginRequiredMixin, TemplateView):
    template_name = 'disturbance/dash/index.html'

    def get_context_data(self, **kwargs):
        context = super(ExternalView, self).get_context_data(**kwargs)
        context['dev'] = settings.DEV_STATIC
        context['dev_url'] = settings.DEV_STATIC_URL
        if hasattr(settings, 'DEV_APP_BUILD_URL') and settings.DEV_APP_BUILD_URL:
            context['app_build_url'] = settings.DEV_APP_BUILD_URL
        return context

class ReferralView(ReferralOwnerMixin, DetailView):
    model = Referral
    template_name = 'disturbance/dash/index.html'

class ExternalProposalView(DetailView):
    model = Proposal
    template_name = 'disturbance/dash/index.html'

class ExternalComplianceView(DetailView):
    model = Compliance
    template_name = 'disturbance/dash/index.html'

class InternalComplianceView(DetailView):
    model = Compliance
    template_name = 'disturbance/dash/index.html'

class DisturbanceRoutingView(TemplateView):
    template_name = 'disturbance/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_internal(self.request):
                return redirect('internal')
            return redirect('external')
        kwargs['form'] = LoginForm
        return super(DisturbanceRoutingView, self).get(*args, **kwargs)

class DisturbanceContactView(TemplateView):
    template_name = 'disturbance/contact.html'

class DisturbanceFurtherInformationView(TemplateView):
    template_name = 'disturbance/further_info.html'

class InternalProposalView(DetailView):
    #template_name = 'disturbance/index.html'
    model = Proposal
    template_name = 'disturbance/dash/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_internal(self.request):
                #return redirect('internal-proposal-detail')
                return super(InternalProposalView, self).get(*args, **kwargs)
            return redirect('external-proposal-detail')
        kwargs['form'] = LoginForm
        return super(DisturbanceRoutingDetailView, self).get(*args, **kwargs)


@login_required(login_url='ds_home')
def first_time(request):
    context = {}
    if request.method == 'POST':
        form = FirstTimeForm(request.POST)
        redirect_url = form.data['redirect_url']
        if not redirect_url:
            redirect_url = '/'
        if form.is_valid():
            # set user attributes
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.dob = form.cleaned_data['dob']
            request.user.save()
            return redirect(redirect_url)
        context['form'] = form
        context['redirect_url'] = redirect_url
        return render(request, 'disturbance/user_profile.html', context)
    # GET default
    if 'next' in request.GET:
        context['redirect_url'] = request.GET['next']
    else:
        context['redirect_url'] = '/'
    context['dev'] = settings.DEV_STATIC
    context['dev_url'] = settings.DEV_STATIC_URL
    #return render(request, 'disturbance/user_profile.html', context)
    return render(request, 'disturbance/dash/index.html', context)


class HelpView(LoginRequiredMixin, TemplateView):
    template_name = 'disturbance/help.html'

    def get_context_data(self, **kwargs):
        context = super(HelpView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            application_type = kwargs.get('application_type', None) 
            if kwargs.get('help_type', None)=='assessor':
                if is_internal(self.request):
                    qs = HelpPage.objects.filter(application_type__name__icontains=application_type, help_type=HelpPage.HELP_TEXT_INTERNAL).order_by('-version')
                    context['help'] = qs.first()
#                else:
#                    return TemplateResponse(self.request, 'disturbance/not-permitted.html', context)
#                    context['permitted'] = False
            else:
                qs = HelpPage.objects.filter(application_type__name__icontains=application_type, help_type=HelpPage.HELP_TEXT_EXTERNAL).order_by('-version')
                context['help'] = qs.first()
        return context


class ManagementCommandsView(LoginRequiredMixin, TemplateView):
    template_name = 'disturbance/mgt-commands.html'

    def post(self, request):
        data = {}
        command_script = request.POST.get('script', None)
        if command_script:
            print('running {}'.format(command_script))
            call_command(command_script)
            data.update({command_script: 'true'})

        return render(request, self.template_name, data)


class TemplateGroupView(views.APIView):

    def get(self, request, format=None):
        return Response({
            'template_group': settings.DOMAIN_DETECTED,
            'is_das_admin': True if is_disturbance_admin(request) else False,
            'is_apiary_admin': True if is_apiary_admin(request) else False,
            'is_das_apiary_admin': True if is_das_apiary_admin(request) else False,
        })


@timeit
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def gisdata(request):
    layer = request.GET.get('layer', None)
    lat = request.GET.get('lat', None)
    lng = request.GET.get('lng', None)
    include_feature = request.GET.get('include_feature', False)  # feature(polygon) data could be large

    geom_str = GEOSGeometry('POINT(' + lng + ' ' + lat + ')', srid=4326)

    if layer == 'wa_coast_smoothed':
        feature = get_feature_in_wa_coastline_smoothed(geom_str)
    elif layer == 'wa_coast_original':
        feature = get_feature_in_wa_coastline_original(geom_str)

    if include_feature:
        serializer = WaCoastSerializer(feature)
    else:
        serializer = WaCoastOptimisedSerializer(feature)

    return Response(serializer.data)


class LedgerPayView(TemplateView):
    template_name = 'disturbance/dash/index.html'

    def get_context_data(self, **kwargs):
        context = super(LedgerPayView, self).get_context_data(**kwargs)
        context['dev'] = settings.DEV_STATIC
        context['dev_url'] = settings.DEV_STATIC_URL
        context['empty_menu'] = True  # We don't want any menu items for now
        if hasattr(settings, 'DEV_APP_BUILD_URL') and settings.DEV_APP_BUILD_URL:
            context['app_build_url'] = settings.DEV_APP_BUILD_URL
        return context
    

@api_view(['POST',])
def validate_invoice_details(request):
    invoice_reference = request.data.get('invoice_reference', None)
    invoice_date = request.data.get('invoice_date', None)

    try:
        datetime_object = datetime.strptime(invoice_date, '%d/%m/%Y').date()
        invoice = Invoice.objects.get(reference=invoice_reference)
        invoice_created_date = invoice.created.date()

        if invoice_created_date == datetime_object and invoice.payment_status in ('unpaid', 'partially_paid'):
            return Response({
                "unpaid_invoice_exists": True
            })
        else:
            return Response({
                "unpaid_invoice_exists": False,
                "alert_message": "There are no unpaid invoices that meet the criteria.",
            })

    except Exception as e:
        return Response({
            "unpaid_invoice_exists": False,
            "alert_message": "There are no unpaid invoices that meet the criteria.",
        })

def is_authorised_to_access_proposal_document(request,document_id):
    if is_internal(request):
        return True
    elif is_customer(request):
        user = request.user
        user_orgs = [org.id for org in user.disturbance_organisations.all()]
        return Proposal.objects.filter(id=document_id).filter(
                Q(applicant_id__in=user_orgs) |
                Q(submitter=user)).exists()

def is_authorised_to_access_approval_document(request,document_id):
    if is_internal(request):
        return True
    elif is_customer(request):
        user = request.user
        user_orgs = [org.id for org in user.disturbance_organisations.all()]
        return Approval.objects.filter(id=document_id).filter(
                Q(applicant_id__in = user_orgs) |
                Q(proxy_applicant_id=user.id)).exists()

def is_authorised_to_access_organisation_document(request,document_id):
    if is_internal(request):
        return True
    elif is_customer(request):
        user = request.user
        org_contacts = OrganisationContact.objects.filter(is_admin=True).filter(email=user.email)
        user_admin_orgs = [org.organisation.id for org in org_contacts]
        return Organisation.objects.filter(id=document_id).filter(id__in=user_admin_orgs).exists()
    
def get_file_path_id(check_str,file_path):
    file_name_path_split = file_path.split("/")
    #if the check_str is in the file path, the next value should be the id
    if check_str in file_name_path_split:
        id_index = file_name_path_split.index(check_str)+1
        if len(file_name_path_split) > id_index and file_name_path_split[id_index].isnumeric():
            return int(file_name_path_split[id_index])
        else:
            return False
    else:
        return False

def is_authorised_to_access_document(request):
    
    if is_internal(request):
        return True
    elif is_customer(request):
        p_document_id = get_file_path_id("proposals",request.path)
        if p_document_id:
            return is_authorised_to_access_proposal_document(request,p_document_id)
        
        a_document_id = get_file_path_id("approvals",request.path)
        if a_document_id:
            return is_authorised_to_access_approval_document(request,a_document_id)
        
        #for organisation requests, this will fail and they are stored in a request subdir and by date (which is fine for current use cases)
        o_document_id = get_file_path_id("organisations",request.path)
        if o_document_id:
            return is_authorised_to_access_organisation_document(request,a_document_id)
    else:
        return False

def getPrivateFile(request):

    if is_authorised_to_access_document(request):
        file_name_path =  request.path
        #norm path will convert any traversal or repeat / in to its normalised form
        full_file_path= os.path.normpath(settings.BASE_DIR+file_name_path) 
        #we then ensure the normalised path is within the BASE_DIR (and the file exists)
        if full_file_path.startswith(settings.BASE_DIR) and os.path.isfile(full_file_path):
            extension = file_name_path.split(".")[-1]
            the_file = open(full_file_path, 'rb')
            the_data = the_file.read()
            the_file.close()
            if extension == 'msg':
                return HttpResponse(the_data, content_type="application/vnd.ms-outlook")
            if extension == 'eml':
                return HttpResponse(the_data, content_type="application/vnd.ms-outlook")

            return HttpResponse(the_data, content_type=mimetypes.types_map['.'+str(extension)])
       
    return HttpResponse()