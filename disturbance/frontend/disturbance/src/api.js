var site_url = location.origin

export default {
    organisations: '/api/organisations.json',
    organisation_requests: '/api/organisation_requests.json',
    organisation_contacts: '/api/organisation_contacts.json',
    organisation_access_group_members: '/api/organisation_access_group_members',
    apiary_organisation_access_group_members: '/api/apiary_organisation_access_group_members',
    users_api: '/api/users',
    users: '/api/users.json',
    profile: '/api/profile',
    //department_users: '/api/department_users',
    //other
    //countries: "https://restcountries.eu/rest/v1/?fullText=true",
    countries: '/api/countries',
    proposal_type:"/api/proposal_type",
    proposals:"/api/proposal.json",
    //list_proposals:"/api/proposal/list_proposal.json",
    approvals:"/api/approvals.json",
    referrals:"/api/referrals.json",
    compliances:"/api/compliances.json",
    proposal_standard_requirements:"/api/proposal_standard_requirements.json",
    disturbance_standard_requirements:"/api/proposal_standard_requirements/disturbance_standard_requirements.json",
    apiary_standard_requirements:"/api/proposal_standard_requirements/apiary_standard_requirements.json",
    proposal_requirements:"/api/proposal_requirements.json",
    amendment_request:"/api/amendment_request.json",
    regions:"/api/regions.json",
    activity_matrix:"/api/activity_matrix.json",
    application_types:"/api/application_types.json",
    searchable_application_types:"/api/application_types/searchable_application_types.json",
    searchable_proposal_types:"/api/search_proposal_types.json",
    proposal_type_sections:"/api/proposal_type_sections.json",

    // used in internal and external dashboards
    proposals_paginated_external:   "/api/proposal_paginated/proposals_external/?format=datatables",
    approvals_paginated_external:   "/api/approval_paginated/approvals_external/?format=datatables",
    // internal_revision_proposal:     "/api/proposal/internal_revision_proposal.json/?revision_number",
    compliances_paginated_external: "/api/compliance_paginated/compliances_external/?format=datatables",
    proposals_paginated_internal:   "/api/proposal_paginated/proposals_internal/?format=datatables",
    referrals_paginated_internal:   "/api/proposal_paginated/referrals_internal/?format=datatables",
    approvals_paginated_internal:   "/api/approval_paginated/approvals_internal/?format=datatables",
    compliances_paginated_internal: "/api/compliance_paginated/compliances_internal/?format=datatables",
    //filter_list:                    "/api/proposal_paginated/filter_list.json",
    filter_list:                    "/api/proposal/filter_list.json",
    filter_list_approvals:          "/api/approvals/filter_list.json",
    filter_list_compliances:        "/api/compliances/filter_list.json",
    filter_list_referrals:          "/api/referrals/filter_list.json",
    das_map_proposal:"/api/das_map_proposal.json",
    filter_list_map:"/api/das_map_proposal/filter_list.json",

    //approvals_paginated:"/api/approvals/user_list_paginated/?format=datatables",
    //compliances_paginated:"/api/compliances/user_list_paginated/?format=datatables",
    //list_proposals:"/api/list_proposal/?format=datatables",
    //list_referrals:"/api/list_proposal/referral_list/?format=datatables",

    discard_proposal:function (id) {
      return `/api/proposal/${id}.json`;
    },
    site_url: site_url,
    //dep_name: 'Department of Biodiversity, Conservation and Attractions',
    //dep_name_short: 'DBCA',
    system_name: 'Disturbance Approval System',
    //system_name_short: 'DAS',

    // Apiary specific endpoints
    apiary_referral_groups:"/api/apiary_referral_groups.json",
    proposal_apiary:"/api/proposal_apiary.json",
    apiary_referrals:"/api/apiary_referrals.json",
    apiary_site_transfer_fees:"/api/apiary_site_fees/get_site_transfer_fees.json",

    //schema api's
    //schema_masterlist:"/api/schema_masterlist/",
    schema_masterlist:"/api/schema_masterlist.json",
    schema_masterlist_paginated:"/api/schema_masterlist_paginated/",
    //schema_proposal_type:"/api/schema_proposal_type/",
    schema_proposal_type:"/api/schema_proposal_type.json",
    schema_proposal_type_paginated:"/api/schema_proposal_type_paginated/",

    // SQS
    proposals_sqs:"/api/proposal_sqs.json",
    spatial_query:"/api/spatial_query",
    spatial_query_layer:"/api/spatial_query_layer",
    spatial_query_paginated:"/api/spatial_query_paginated/",
    spatial_query_metrics_paginated:"/api/spatial_query_metrics_paginated/",
    spatial_query_layers_used_paginated:"/api/proposal_paginated/",

    schema_group:"/api/schema_group/",
    schema_group_paginated:"/api/schema_group_paginated/",
    //schema_question:"/api/schema_question/",
    schema_question:"/api/schema_question.json",
    schema_question_paginated:"/api/schema_question_paginated/",

    history_version_compare_field: "/api/history/compare/field/",
    history_version_compare: "/api/history/compare/",
    history_versions: "/api/history/versions/",
    history_version: "/api/history/version/",
    geocoding_address_search: "https://api.mapbox.com/geocoding/v5/mapbox.places/",
}
