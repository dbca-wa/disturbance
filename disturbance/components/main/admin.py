from django.contrib import admin
from django.forms import ModelForm
from django.conf.urls import url
from django.utils.html import format_html
from django.core.urlresolvers import reverse

from disturbance.components.main.models import MapLayer, MapColumn, RegionDbca, DistrictDbca, DASMapLayer, TaskMonitor
from disturbance.settings import KMI_SERVER_URL


class MyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        self.fields['layer_name'].help_text = "Enter the layer name defined in geoserver (<a href='{}' target='_blank'>GeoServer</a>)<br /><div>Example:</div><span style='padding:1em;'>public:dbca_legislated_lands_and_waters</span>".format(KMI_SERVER_URL)
        self.fields['display_all_columns'].help_text = "When checked, display all the attributes(columns) in the table regardless of the configurations below"
        self.fields['option_for_internal'].help_text = "When checked, a checkbox for this layer is displayed for the internal user"
        self.fields['option_for_external'].help_text = "When checked, a checkbox for this layer is displayed for the external user"

class DASMapLayerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(DASMapLayerForm, self).__init__(*args, **kwargs)
        self.fields['layer_name'].help_text = "Enter the layer name defined in geoserver (<a href='{}' target='_blank'>GeoServer</a>)<br /><div>Example:</div><span style='padding:1em;'>public:dbca_legislated_lands_and_waters</span>".format(KMI_SERVER_URL)
        self.fields['display_all_columns'].help_text = "When checked, display all the attributes(columns) in the table regardless of the configurations below"
        self.fields['option_for_internal'].help_text = "When checked, a checkbox for this layer is displayed for the internal user"
        self.fields['option_for_external'].help_text = "When checked, a checkbox for this layer is displayed for the external user"

class MapColumnInline(admin.TabularInline):
    model = MapColumn
    extra = 0


@admin.register(MapLayer)
class MapLayerAdmin(admin.ModelAdmin):
    list_display = [
        'display_name',
        'layer_name',
        'option_for_internal',
        'option_for_external',
        'display_all_columns',
        'column_names',
    ]
    list_filter = ['option_for_internal', 'option_for_external', 'display_all_columns',]
    form = MyForm
    inlines = [MapColumnInline,]

@admin.register(DASMapLayer)
class DASMapLayerAdmin(admin.ModelAdmin):
    list_display = [
        'display_name',
        'layer_name',
        'layer_url',
        'option_for_internal',
        'option_for_external',
        #'create_update_layer_in_sqs',
    ]
    list_filter = ['option_for_internal', 'option_for_external', ]
    readonly_fields = ['layer_url',]
    search_fields = ['layer_name',]
    form = DASMapLayerForm
#    readonly_fields = ('create_update_layer_in_sqs',)


@admin.register(TaskMonitor)
class TaskMonitorAdmin(admin.ModelAdmin):
    list_display = [
        'task_id',
        'status',
        'retries',
        'proposal',
        'requester',
        'created',
    ]
    list_filter = ["status"]
    readonly_fields = ['info',]
    search_fields = ['task_id', 'status', 'proposal__lodgement_number', 'requester__email']


#    def get_urls(self):
#        urls = super().get_urls()
#        custom_urls = [
#            url(
#                r'^(?P<proposal_type_id>.+)/process_create_update_layer/$',
#                self.admin_site.admin_view(self.process_create_update_layer),
#                name='create_update_layer_in_sqs',
#            ),
#        ]
#        return custom_urls + urls
#
#    def create_update_layer_in_sqs(self, obj):
#        # if obj.name=='Disturbance':
#        return format_html(
#            '<a class="button" href="{}">Create/Update SQS Layer</a>&nbsp;',
#            reverse('admin:create_update_layer_in_sqs', args=[obj.pk]),
#        )
#        return ''
#    create_update_layer_in_sqs.short_description = 'Layer Actions'
#    create_update_layer_in_sqs.allow_tags = True
#
#    def process_create_update_layer(self, request, proposal_type_id, *args, **kwargs):
#        return self.process_action(
#            request=request,
#            proposal_type_id=proposal_type_id,
#            action_form=forms.GenerateSchemaForm,
#            action_title='CreateUpdateLayerInSqs',
#        )
#
#    def process_action(
#        self,
#        request,
#        proposal_type_id,
#        action_form,
#        action_title
#   ):
#        proposal_type = self.get_object(request, proposal_type_id)
#        new_schema=generate_schema(proposal_type, request)
#        if request.method != 'POST':
#            form = action_form()
#        else:
#            form = action_form(request.POST)            
#            if form.is_valid():
#                try:
#                    #form.save(proposal_type)
#                    proposal_type.schema=new_schema
#                    proposal_type.save()
#                except:
#                    # If save() raised, the form will a have a non
#                    # field error containing an informative message.
#                    pass
#                else:
#                    self.message_user(request, 'Success')
#                    url = reverse(
#                        'admin:disturbance_proposaltype_change',
#                       args=[proposal_type.pk],
#                        current_app=self.admin_site.name,
#                    )
#                    return HttpResponseRedirect(url)
#        
#        context = self.admin_site.each_context(request)
#        context['opts'] = self.model._meta
#        context['form'] = form
#        context['proposal_type'] = proposal_type
#        context['title'] = action_title
#        context['new_schema']=new_schema
#        return TemplateResponse(
#            request,
#            'disturbance/admin/proposaltype_action.html',
#            context,
#        )
    


# @admin.register(RegionDbca)
# class RegionAdmin(admin.ModelAdmin):
#     list_display = ['id', 'region_name', 'office', 'enabled']
#     list_filter = ['enabled',]
#     readonly_fields = ['region_name', 'office', 'enabled', 'object_id',]
#
#
# @admin.register(DistrictDbca)
# class DistrictAdmin(admin.ModelAdmin):
#     list_display = ['id', 'district_name', 'office', 'enabled']
#     list_filter = ['enabled',]
#     readonly_fields = ['district_name', 'office', 'enabled', 'object_id',]

