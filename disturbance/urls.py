from django.conf import settings
from django.contrib import admin
from django.urls import re_path as url, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework import routers
from disturbance import views
from disturbance.admin import disturbance_admin_site
from disturbance.components.main.views import GeocodingAddressSearchTokenView, FileDownloadView, FileListView
from disturbance.components.proposals import views as proposal_views
from disturbance.components.organisations import views as organisation_views
from disturbance.components.proposals.views import ExternalProposalTemporaryUseSubmitSuccessView

from disturbance.components.users import api as users_api
from disturbance.components.organisations import api as org_api
from disturbance.components.proposals import api as proposal_api
from disturbance.components.proposals.sqs_utils import api as proposal_sqs_api
from disturbance.components.approvals import api as approval_api
from disturbance.components.compliances import api as compliances_api
from disturbance.components.main import api as main_api
from disturbance.components.history import api as history_api

from ledger.urls import urlpatterns as ledger_patterns
from django_media_serv.urls import urlpatterns as media_serv_patterns

# API patterns
#from disturbance.management.default_data_manager import DefaultDataManager
#from disturbance.utils import are_migrations_running
#from disturbance.views import LedgerPayView

router = routers.DefaultRouter()
router.include_root_view = settings.SHOW_ROOT_API

router.register(r'organisations',org_api.OrganisationViewSet,"organisations")
router.register(r'proposal',proposal_api.ProposalViewSet,"proposal")
router.register(r'proposal_sqs',proposal_sqs_api.ProposalSqsViewSet,"proposal_sqs")
router.register(r'proposal_paginated',proposal_api.ProposalPaginatedViewSet,"proposal_paginated")
router.register(r'approval_paginated',approval_api.ApprovalPaginatedViewSet,"approval_paginated_view")
router.register(r'compliance_paginated',compliances_api.CompliancePaginatedViewSet,"compliance_paginated")
router.register(r'referrals',proposal_api.ReferralViewSet,"referrals")
router.register(r'approvals',approval_api.ApprovalViewSet,"approvals")
router.register(r'compliances',compliances_api.ComplianceViewSet,"compliances")
router.register(r'proposal_requirements',proposal_api.ProposalRequirementViewSet,"proposal_requirements")
router.register(r'proposal_standard_requirements',proposal_api.ProposalStandardRequirementViewSet,"proposal_standard_requirements")
router.register(r'organisation_requests',org_api.OrganisationRequestsViewSet,"organisation_requests")
router.register(r'organisation_contacts',org_api.OrganisationContactViewSet,"organisation_contacts")
router.register(r'my_organisations',org_api.MyOrganisationsViewSet,"my_organisations")
router.register(r'users',users_api.UserViewSet,"users")
router.register(r'amendment_request',proposal_api.AmendmentRequestViewSet,"amendment_request")
router.register(r'compliance_amendment_request',compliances_api.ComplianceAmendmentRequestViewSet,"compliance_amendment_request")
router.register(r'regions', main_api.RegionViewSet,"regions")
router.register(r'activity_matrix', main_api.ActivityMatrixViewSet,"activity_matrix")
#router.register(r'tenure', main_api.TenureViewSet)
router.register(r'global_settings', main_api.GlobalSettingsViewSet, "global_settings")
router.register(r'application_types', main_api.ApplicationTypeViewSet,"application_types")
#router.register(r'payment',payment_api.PaymentViewSet)
router.register(r'proposal_type_sections', proposal_api.ProposalTypeSectionViewSet,"proposal_type_sections")
router.register(r'search_proposal_types', proposal_api.SearchProposalTypeViewSet)

router.register(
    r'schema_question_paginated', proposal_api.SchemaQuestionPaginatedViewSet,"schema_question_paginated")

router.register(
    r'schema_question', proposal_api.SchemaQuestionViewSet,"schema_question")

router.register(
    r'schema_masterlist',
    proposal_api.SchemaMasterlistViewSet,
    "schema_masterlist"
)
router.register(
    r'schema_masterlist_paginated', proposal_api.SchemaMasterlistPaginatedViewSet,"schema_masterlist_paginated")
router.register(
    r'schema_proposal_type', proposal_api.SchemaProposalTypeViewSet,"schema_proposal_type")
router.register(
    r'schema_proposal_type_paginated', proposal_api.SchemaProposalTypePaginatedViewSet,"schema_proposal_type_paginated")
router.register(r'map_layers', main_api.MapLayerViewSet,"map_layers")
router.register(r'das_map_layers', main_api.DASMapLayerViewSet)

router.register(
    r'spatial_query_paginated', proposal_sqs_api.SpatialQueryQuestionPaginatedViewSet)
router.register(
    r'spatial_query_metrics_paginated', proposal_sqs_api.SpatialQueryMetricsPaginatedViewSet)
router.register(
    r'spatial_query',
    proposal_sqs_api.SpatialQueryQuestionViewSet, basename='spatial_query'
)
router.register(
    r'spatial_query_layer',
    proposal_sqs_api.SpatialQueryLayerViewSet
)
router.register(r'das_map_proposal',proposal_api.DASMapFilterViewSet, basename='das_map_proposal')

api_patterns = [
    url(r'^api/profile$', users_api.GetProfile.as_view(), name='get-profile'),
    url(r'^api/countries$', users_api.GetCountries.as_view(), name='get-countries'),
    #url(r'^api/department_users$', users_api.DepartmentUserList.as_view(), name='department-users-list'),
    url(r'^api/proposal_type$', proposal_api.GetProposalType.as_view(), name='get-proposal-type'),
    url(r'^api/empty_list$', proposal_api.GetEmptyList.as_view(), name='get-empty-list'),
    url(r'^api/organisation_access_group_members',org_api.OrganisationAccessGroupMembers.as_view(),name='organisation-access-group-members'),
    url(r'^api/',include(router.urls)),
    url(r'^api/amendment_request_reason_choices',proposal_api.AmendmentRequestReasonChoicesView.as_view(),name='amendment_request_reason_choices'),
    url(r'^api/compliance_amendment_reason_choices',compliances_api.ComplianceAmendmentReasonChoicesView.as_view(),name='amendment_request_reason_choices'),
    url(r'^api/search_keywords',proposal_api.SearchKeywordsView.as_view(),name='search_keywords'),
    url(r'^api/search_reference',proposal_api.SearchReferenceView.as_view(),name='search_reference'),
    url(r'^api/search_sections',proposal_api.SearchSectionsView.as_view(),name='search_sections'),
    url(r'^api/get_search_geojson',proposal_api.GetSearchGeoJsonView.as_view(),name='get_search_geojson'),
    #url(r'^api/reports/payment_settlements$', main_api.PaymentSettlementReportView.as_view(),name='payment-settlements-report'),
#    url(r'^api/das/spatial_query$' proposal_api.SpatialQueryQuestionViewSet, name='sqs_spatial_query'),

    url(r'^api/history/compare/serialized/(?P<app_label>[\w-]+)/(?P<component_name>[\w-]+)/(?P<model_name>[\w-]+)/(?P<serializer_name>[\w-]+)/(?P<pk>\d+)/(?P<newer_version>\d+)/(?P<older_version>\d+)/$',
            history_api.GetCompareSerializedVersionsView.as_view(), name='get-compare-serialized-versions'),
    url(r'^api/history/compare/root/fields/(?P<app_label>[\w-]+)/(?P<model_name>[\w-]+)/(?P<pk>\d+)/(?P<newer_version>\d+)/(?P<older_version>\d+)/$',
            history_api.GetCompareRootLevelFieldsVersionsView.as_view(), name='get-compare-root-level-fields-versions'),
    url(r'^api/history/compare/field/(?P<app_label>[\w-]+)/(?P<model_name>[\w-]+)/(?P<pk>\d+)/(?P<newer_version>\d+)/(?P<older_version>\d+)/(?P<compare_field>[\w-]+)/$',
            history_api.GetCompareFieldVersionsView.as_view(), name='get-compare-field-versions'),
    url(r'^api/history/compare/(?P<app_label>[\w-]+)/(?P<model_name>[\w-]+)/(?P<pk>\d+)/(?P<newer_version>\d+)/(?P<older_version>\d+)/$',
            history_api.GetCompareVersionsView.as_view(), name='get-compare-versions'),
    url(r'^api/history/versions/(?P<app_label>[\w-]+)/(?P<component_name>[\w-]+)/(?P<model_name>[\w-]+)/(?P<pk>\d+)/(?P<reference_id_field>[\w-]+)/$',
            history_api.GetVersionsView.as_view(), name='get-versions'),
    url(r'^api/history/version/(?P<app_label>[\w-]+)/(?P<component_name>[\w-]+)/(?P<model_name>[\w-]+)/(?P<serializer_name>[\w-]+)/(?P<pk>\d+)/(?P<version_number>\d+)/$',
            history_api.GetVersionView.as_view(), name='get-version'),
    url(r'^api/geocoding_address_search_token', GeocodingAddressSearchTokenView.as_view(), name='geocoding_address_search_token'),
]

# URL Patterns
# You have to be careful about the order of the urls below.
# Django searches matching url from the top of the list, and once found a matching url, it never goes through the urls below it.
urlpatterns = [
    #url(r'^admin/', disturbance_admin_site.urls),
    # url(r'^ledger/admin/', admin.site.urls, name='ledger_admin'),
    url(r'^chaining/', include('smart_selects.urls')),
    url('summernote/', include('django_summernote.urls')),
    url(r'', include(api_patterns)),
    url(r'^$', views.DisturbanceRoutingView.as_view(), name='ds_home'),
    url(r'^contact/', views.DisturbanceContactView.as_view(), name='ds_contact'),
    url(r'^further_info/', views.DisturbanceFurtherInformationView.as_view(), name='ds_further_info'),
    #url(r'^internal/layer_json/(?P<layer_name>[^/]+)/$',proposal_views.LayerJsonView.as_view(), name='layer_json'),
    url(r'^internal/', views.InternalView.as_view(), name='internal'),
    url(r'^internal/proposal/(?P<proposal_pk>\d+)/referral/(?P<referral_pk>\d+)/$', views.ReferralView.as_view(), name='internal-referral-detail'),
    #url(r'^layer_json/(?P<layer_name>[^/]+)/$',proposal_views.LayerJsonView.as_view(), name='layer_json'),
    url(r'^external/proposal/(?P<proposal_pk>\d+)/submit_temp_use_success/$', ExternalProposalTemporaryUseSubmitSuccessView.as_view(),),
    url(r'^external/', views.ExternalView.as_view(), name='external'),
    url(r'^firsttime/$', views.first_time, name='first_time'),
    url(r'^gisdata/$', views.gisdata, name='gisdata'),
    # url(r'^ledgerpay/$', views.ledgerpay, name='ledgerpay'),
    # url(r'^ledgerpay/$', LedgerPayView.as_view(), name='ledgerpay'),
    url(r'^account/$', views.ExternalView.as_view(), name='manage-account'),
    url(r'^help/(?P<application_type>[^/]+)/(?P<help_type>[^/]+)/$', views.HelpView.as_view(), name='help'),
    url(r'^mgt-commands/$', views.ManagementCommandsView.as_view(), name='mgt-commands'),
    url(r'^email-exports/$', views.EmailExportsView.as_view(), name='email-exports'),
    #url(r'^external/organisations/manage/$', views.ExternalView.as_view(), name='manage-org'),
    #following url is used to include url path when sending Proposal amendment request to user.
    url(r'^proposal/$', proposal_views.ProposalView.as_view(), name='proposal'),
    url(r'^preview/licence-pdf/(?P<proposal_pk>\d+)',proposal_views.PreviewLicencePDFView.as_view(), name='preview_licence_pdf'),

    # following url is defined so that to include url path when sending Proposal amendment request to user.
    url(r'^external/proposal/(?P<proposal_pk>\d+)/$', views.ExternalProposalView.as_view(), name='external-proposal-detail'),
    url(r'^internal/proposal/(?P<proposal_pk>\d+)/$', views.InternalProposalView.as_view(), name='internal-proposal-detail'),
    url(r'^external/compliance/(?P<compliance_pk>\d+)/$', views.ExternalComplianceView.as_view(), name='external-compliance-detail'),
    url(r'^internal/compliance/(?P<compliance_pk>\d+)/$', views.InternalComplianceView.as_view(), name='internal-compliance-detail'),
    url(r'filelist/$', FileListView.as_view(), name='file-list'),
    url(r'filedownload/(?P<filename>[\w\s ().-]+)/$', FileDownloadView.as_view(), name='file-download'),

    #url(r'^organisations/(?P<pk>\d+)/confirm-delegate-access/(?P<uid>[0-9A-Za-z]+)-(?P<token>.+)/$', views.ConfirmDelegateAccess.as_view(), name='organisation_confirm_delegate_access'),
    # reversion history-compare
    url(r'^history/proposal/latest/(?P<pk>\d+)/(?P<count>\d+)/$', proposal_views.ProposalHistoryLatestCompareView.as_view(), name='proposal_history_latest'),
    url(r'^history/proposal/(?P<pk>\d+)/$', proposal_views.ProposalHistoryCompareView.as_view(), name='proposal_history'),
    url(r'^history/proposal/filtered/(?P<pk>\d+)/$', proposal_views.ProposalFilteredHistoryCompareView.as_view(), name='proposal_filtered_history'),
    url(r'^history/referral/(?P<pk>\d+)/$', proposal_views.ReferralHistoryCompareView.as_view(), name='referral_history'),
    url(r'^history/approval/(?P<pk>\d+)/$', proposal_views.ApprovalHistoryCompareView.as_view(), name='approval_history'),
    url(r'^history/compliance/(?P<pk>\d+)/$', proposal_views.ComplianceHistoryCompareView.as_view(), name='compliance_history'),
    url(r'^history/proposaltype/(?P<pk>\d+)/$', proposal_views.ProposalTypeHistoryCompareView.as_view(), name='proposaltype_history'),
    url(r'^history/helppage/(?P<pk>\d+)/$', proposal_views.HelpPageHistoryCompareView.as_view(), name='helppage_history'),
    url(r'^history/organisation/(?P<pk>\d+)/$', organisation_views.OrganisationHistoryCompareView.as_view(), name='organisation_history'),
    url(r'^template_group$', views.TemplateGroupView.as_view(), name='template-group'),
    url(r'^private-media/', views.getPrivateFile, name='view_private_file'),
    url(r'^ckeditor5/', include('django_ckeditor_5.urls')),

    # Reports
    # url('kmi-proxy/(?P<path>.*)', views.kmiProxyView),
    # url('kb-proxy/(?P<path>.*)', views.kbProxyView),
    # url('kmi-proxy/(?P<path>.*)', views.mapProxyView),
    url('kb-proxy/(?P<path>.*)', views.mapProxyView),

                  # url(r'^external/proposal/(?P<proposal_pk>\d+)/submit_temp_use_success/$', success_view, name='external-proposal-temporary-use-submit-success'),
] + ledger_patterns #+ media_serv_patterns

#if not are_migrations_running():
#    DefaultDataManager()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# DBCA Template URLs
urlpatterns.append(url("logout/", auth_views.LogoutView.as_view(), {"next_page": "/"}, name="logout"))
if settings.ENABLE_DJANGO_LOGIN:
    urlpatterns.append(url(r"^ssologin/", auth_views.LoginView.as_view(), name="ssologin"))
    