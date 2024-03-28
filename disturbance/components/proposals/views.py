import json
import traceback

from django.conf import settings
from django.http import HttpResponse, JsonResponse, Http404
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.core.cache import cache
from django.db.models import Q

import requests
from requests.auth import HTTPBasicAuth

from disturbance.components.proposals.utils import create_data_from_form
from disturbance.components.proposals.models import Proposal, Referral, ProposalType, HelpPage
from disturbance.components.approvals.models import Approval
from disturbance.components.compliances.models import Compliance

from reversion.models import Version
import csv
from datetime import datetime


class ProposalView(TemplateView):
    template_name = 'disturbance/proposal.html'

    def post(self, request, *args, **kwargs):
        extracted_fields = []
        try:
            proposal_id = request.POST.pop('proposal_id')
            proposal = Proposal.objects.get(proposal_id)
            schema = json.loads(request.POST.pop('schema')[0])
            extracted_fields = create_data_from_form(schema,request.POST, request.FILES)
            proposal.schema = schema;
            proposal.data = extracted_fields
            proposal.save()
            return redirect(reverse('external'))
        except:
            traceback.print_exc
            return JsonResponse({error:"something went wrong"},safe=False,status=400)


from reversion_compare.views import HistoryCompareDetailView
class ProposalHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = Proposal
    template_name = 'disturbance/reversion_history.html'


class ProposalHistoryLatestCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare that returns on the x most recent revisions
    """
    model = Proposal
    template_name = 'disturbance/reversion_history.html'


class ProposalFilteredHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare - with 'status' in the comment field only'
    """

    model = Proposal
    template_name = 'disturbance/reversion_history.html'

    def _get_action_list(self,):
        """ Get only versions when processing_status changed, and add the most recent (current) version """
        current_revision_id = Version.objects.get_for_object(self.get_object()).first().revision_id
        action_list = [
            {"version": version, "revision": version.revision}
            for version in self._order_version_queryset(
                #Version.objects.get_for_object(self.get_object()).select_related("revision__user").filter(revision__comment__icontains='status')
                Version.objects.get_for_object(self.get_object()).select_related("revision__user").filter(Q(revision__comment__icontains='status') | Q(revision_id=current_revision_id))
            )
        ]
        return action_list


class ReferralHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = Referral
    template_name = 'disturbance/reversion_history.html'


class ExternalProposalTemporaryUseSubmitSuccessView(TemplateView):
    model = Proposal
    template_name = 'disturbance/temporary_use_submit_success.html'

    def post(self, request, *args, **kwargs):
        proposal_id = kwargs['proposal_pk']
        p = Proposal.objects.get(id=proposal_id)
        return render(request, self.template_name, context={'modified_date': p.modified_date})


# def success_view(request):
#     pass


class ApprovalHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = Approval
    template_name = 'disturbance/reversion_history.html'


class ComplianceHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = Compliance
    template_name = 'disturbance/reversion_history.html'



class ProposalTypeHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = ProposalType
    template_name = 'disturbance/reversion_history.html'


class HelpPageHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = HelpPage
    template_name = 'disturbance/reversion_history.html'


class PreviewLicencePDFView(View):
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')

        proposal = self.get_object()
        details = json.loads(request.POST.get('formData'))

        #response.write(proposal.preview_approval(request, details))
        response.content = proposal.preview_approval(request, details)
        return response

    def get_object(self):
        return get_object_or_404(Proposal, id=self.kwargs['proposal_pk'])


class LayersUsedCsvView(TemplateView):

    def get(self, request, *args, **kwargs):
        rows = []
        rows.append(('Proposal Number', 'Proposal Submitter', 'Proposal Section', 'Layer Name', 'Layer Version', 'Layer Modified Date', 'SQS Timestamp'))
        for proposal in Proposal.objects.filter(layer_data__isnull=False):
            for data in proposal.layer_data:
                rows.append((proposal.lodgement_number, proposal.submitter, data['name'], data['layer_name'], data['layer_version'], data['layer_modified_date'], data['sqs_timestamp']))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=layers_used_{datetime.now().strftime("%Y%m%dT%H%M")}.csv'  
        writer = csv.writer(response)
        for row in rows:
            writer.writerow(row)  
        return response



