import os
import datetime
import pytz
from ledger.settings_base import TIME_ZONE

from django.contrib import admin
from ledger.accounts.models import EmailUser

import disturbance
from disturbance.components.main.utils import custom_strftime
from disturbance.components.proposals import models
from disturbance.components.proposals import forms
from disturbance.components.main.models import ActivityMatrix, SystemMaintenance, ApplicationType, GlobalSettings
#from disturbance.components.main.models import Activity, SubActivityLevel1, SubActivityLevel2, SubCategory
from reversion.admin import VersionAdmin
from django.urls import re_path as url
from django.template.response import TemplateResponse
from django.http import HttpResponse, HttpResponseRedirect

from disturbance.utils import create_helppage_object
from disturbance.helpers import is_disturbance_admin
# Register your models here.
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse


from disturbance.components.proposals.utils import generate_schema


@admin.register(models.ProposalType)
class ProposalTypeAdmin(admin.ModelAdmin):
    list_display = ['name','description', 'version', 'proposal_type_actions', ]
    ordering = ('name', '-version')
    list_filter = ('name',)
    readonly_fields = (
        'proposal_type_actions', 
    )
    #exclude=("site",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<proposal_type_id>.+)/process_generate_schema/$',
                self.admin_site.admin_view(self.process_generate_schema),
                name='generate-schema',
            ),
        ]
        return custom_urls + urls

    def proposal_type_actions(self, obj):
        # if obj.name=='Disturbance':
        if obj.latest:
            return format_html(
                '<a class="button" href="{}">Generate Schema</a>&nbsp;',
                reverse('admin:generate-schema', args=[obj.pk]),
            )
        return ''
    proposal_type_actions.short_description = 'Proposal Type Actions'
    proposal_type_actions.allow_tags = True

    def process_generate_schema(self, request, proposal_type_id, *args, **kwargs):
        return self.process_action(
            request=request,
            proposal_type_id=proposal_type_id,
            action_form=forms.GenerateSchemaForm,
            action_title='GenerateSchema',
        )

    def process_action(
        self,
        request,
        proposal_type_id,
        action_form,
        action_title
   ):
        proposal_type = self.get_object(request, proposal_type_id)
        new_schema=generate_schema(proposal_type, request)
        if request.method != 'POST':
            form = action_form()
        else:
            form = action_form(request.POST)            
            if form.is_valid():
                try:
                    #form.save(proposal_type)
                    proposal_type.schema=new_schema
                    proposal_type.save()
                except:
                    # If save() raised, the form will a have a non
                    # field error containing an informative message.
                    pass
                else:
                    self.message_user(request, 'Success')
                    url = reverse(
                        'admin:disturbance_proposaltype_change',
                       args=[proposal_type.pk],
                        current_app=self.admin_site.name,
                    )
                    return HttpResponseRedirect(url)
        
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['proposal_type'] = proposal_type
        context['title'] = action_title
        context['new_schema']=new_schema
        return TemplateResponse(
            request,
            'disturbance/admin/proposaltype_action.html',
            context,
        )
    

class ProposalDocumentInline(admin.TabularInline):
    model = models.ProposalDocument
    extra = 0


@admin.register(models.AmendmentReason)
class AmendmentReasonAdmin(admin.ModelAdmin):
    list_display = ['reason']


@admin.register(models.Proposal)
class ProposalAdmin(VersionAdmin):
    inlines =[ProposalDocumentInline,]
    raw_id_fields = ('applicant','proxy_applicant','submitter','previous_application', 'assigned_officer', 'assigned_approver')


@admin.register(models.ProposalAssessorGroup)
class ProposalAssessorGroupAdmin(admin.ModelAdmin):
    list_display = ['name','default']
    filter_horizontal = ('members',)
    form = forms.ProposalAssessorGroupAdminForm
    readonly_fields = ['default']
    #readonly_fields = ['regions', 'activities']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.default:
            return False
        return super(ProposalAssessorGroupAdmin, self).has_delete_permission(request, obj)

@admin.register(models.ProposalApproverGroup)
class ProposalApproverGroupAdmin(admin.ModelAdmin):
    list_display = ['name','default']
    filter_horizontal = ('members',)
    form = forms.ProposalApproverGroupAdminForm
    readonly_fields = ['default']
    #readonly_fields = ['default', 'regions', 'activities']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.default:
            return False
        return super(ProposalApproverGroupAdmin, self).has_delete_permission(request, obj)


@admin.register(models.CddpQuestionGroup)
class CddpQuestionGroupAdmin(admin.ModelAdmin):
    list_display = ['name','default']
    filter_horizontal = ('members',)
    form = forms.CddpQuestionGroupAdminForm
    readonly_fields = ['default']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.default:
            return False
        return super(CddpQuestionGroupAdmin, self).has_delete_permission(request, obj)


@admin.register(models.ProposalStandardRequirement)
class ProposalStandardRequirementAdmin(admin.ModelAdmin):
    list_display = ['code','text','system','obsolete']
    #readonly_fields=('system',)
    #list_filter=('system',)

    def get_queryset(self, request):
        # filter based on membership of Apiary Admin or Disturbance Admin
        qs = super(ProposalStandardRequirementAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group_list = []
        if is_disturbance_admin(request):
            group_list.append('disturbance')
        return qs.filter(system__in=group_list)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'system':
            if (request.user.is_superuser or is_disturbance_admin(request)):
                # user will see both choices
                kwargs["choices"] = (
                        ('disturbance', 'Disturbance'),
                        )
            elif is_disturbance_admin(request):
                kwargs["choices"] = (('disturbance', 'Disturbance'),)
        return super(ProposalStandardRequirementAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)


@admin.register(models.HelpPage)
class HelpPageAdmin(admin.ModelAdmin):
    list_display = ['application_type','help_type', 'description', 'version']
    form = forms.DisturbanceHelpPageAdminForm
    change_list_template = "disturbance/help_page_changelist.html"
    ordering = ('application_type', 'help_type', '-version')
    list_filter = ('application_type', 'help_type')

    class Media:
        css = {
            'all': ('disturbance/css/admin_extra.css',)
        }


    def get_urls(self):
        urls = super(HelpPageAdmin, self).get_urls()
        my_urls = [
            url('create_disturbance_help/', self.admin_site.admin_view(self.create_disturbance_help)),
            url('create_disturbance_help_assessor/', self.admin_site.admin_view(self.create_disturbance_help_assessor)),
        ]
        return my_urls + urls

    def create_disturbance_help(self, request):
        create_helppage_object(application_type='Disturbance', help_type=models.HelpPage.HELP_TEXT_EXTERNAL)
        return HttpResponseRedirect("../")

    def create_disturbance_help_assessor(self, request):
        create_helppage_object(application_type='Disturbance', help_type=models.HelpPage.HELP_TEXT_INTERNAL)
        return HttpResponseRedirect("../")


@admin.register(ActivityMatrix)
class ActivityMatrixAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'version']
    ordering = ('name', '-version')


@admin.register(SystemMaintenance)
class SystemMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'start_date', 'end_date', 'duration']
    ordering = ('start_date',)
    readonly_fields = ('duration',)
    form = forms.SystemMaintenanceAdminForm


@admin.register(ApplicationType)
class ApplicationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'visible', 'domain_used',]
    ordering = ('order',)


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'help_text_required', 'help_text' ]
    ordering = ('key',)
    class Media:
        css = {
            'all': ('disturbance/css/admin_extra.css',)
        }


@admin.register(models.QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ['label',]
    fields = ('label',)

@admin.register(models.MasterlistQuestion)
class MasterlistQuestionAdmin(admin.ModelAdmin):
    list_display = ['question',]
    filter_horizontal = ('option',)
    form = forms.MasterlistQuestionAdminForm
    class Media:
        css = {
            'all': ('disturbance/css/admin_extra.css',)
        }
    

@admin.register(models.ProposalTypeSection)
class ProposalTypeSectionAdmin(admin.ModelAdmin):
    list_display = ['proposal_type', 'index', 'section_label',]
    fields = ('section_label','index', 'proposal_type')
   
@admin.register(models.SectionQuestion)
class SectionQuestionAdmin(admin.ModelAdmin):
    list_display = ['section', 'question','order', 'parent_question','parent_answer']
    #list_display = ['section', 'question','parent_question',]
    form = forms.SectionQuestionAdminForm

#@admin.register(models.SpatialQueryQuestion)
#class SpatialQueryQuestionAdmin(admin.ModelAdmin):
#    list_display = ['layer_name', 'how', 'column_name','operator', 'value']
#    #fields = ['question', 'options']
#    #list_display = ['question','answer_mlq', 'layer_name','how', 'column_name','operator', 'value']
#    #list_display = ['section', 'question','parent_question',]
#    #form = forms.SpatialQueryQuestionAdminForm

   
