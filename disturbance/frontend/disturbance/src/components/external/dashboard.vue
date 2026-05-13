<template>
<div class="container" id="externalDash">
    <div class="row">
        <div class="col-sm-12">
            <div class="card mb-2 bg-light">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-9">
                            <span v-html="welcomeMessage"></span>
                        </div>
                        <div class="col-md-3 text-md-end mt-3 mt-md-0">
                            <router-link  class="btn btn-primary" :to="{ name: 'apply_proposal' }">New Proposal</router-link>
                        </div>
                    </div>
                    
                </div>
            </div>
        
            <FormSection
                    :form-collapse="false"
                    label="Proposals Map"
                    Index="proposals_map"
                >
                <MapDashboard  v-if="show_das_map && !apiaryTemplateGroup" level="external" :is_external="true"/>
            </FormSection>      
            <FormSection
                    :form-collapse="false"
                    label="Proposals"
                    Index="proposals"
                    subtitle="View existing proposals and lodge new ones"
                >
                <ProposalDashTable level='external' :url='proposals_url'/>
            </FormSection>
            <FormSection
                    :form-collapse="false"
                    label="Approvals"
                    Index="approvals"
                    subtitle="View existing approvals and amend or renew them"
                >
                <ApprovalDashTable level='external' :url='approvals_url'/>
            </FormSection>
            <FormSection
                    :form-collapse="false"
                    label="Compliances with requirements"
                    Index="compliances"
                    subtitle="View submitted compliances and submit new ones"
                >
                <ComplianceDashTable level='external' :url='compliances_url'/>
            </FormSection>
            <!-- <MapDashboard  v-if="show_das_map" level="external" :is_external="true"/> -->
     </div>
    </div>
</div>
</template>
<script>

import FormSection from '@/components/forms/section_toggle.vue';
import ProposalDashTable from '@common-utils/proposals_dashboard.vue'
import ApprovalDashTable from '@common-utils/approvals_dashboard.vue'
import ComplianceDashTable from '@common-utils/compliances_dashboard.vue'
import MapDashboard from '@/components/common/das/map_dashboard_internal.vue'
import {
  api_endpoints,
}
from '@/utils/hooks'
export default {
    name: 'ExternalDashboard',
    data() {
        // let vm = this;
        return {
            empty_list: '/api/empty_list',
            //proposals_url: helpers.add_endpoint_json(api_endpoints.proposals,'user_list'),
            //approvals_url: helpers.add_endpoint_json(api_endpoints.approvals,'user_list'),
            //compliances_url: helpers.add_endpoint_json(api_endpoints.compliances,'user_list'),

            proposals_url: api_endpoints.proposals_paginated_external,
            approvals_url: api_endpoints.approvals_paginated_external,
            compliances_url: api_endpoints.compliances_paginated_external,

            system_name: api_endpoints.system_name,
            apiaryTemplateGroup: false,
            dasTemplateGroup: false,
            // from env var?
            apiarySystemName: 'Apiary System',
            dasSystemName: 'Disturbance Approval System',
        }
    },
    components:{
        ProposalDashTable,
        ApprovalDashTable,
        ComplianceDashTable,
        MapDashboard,
        FormSection,
    },
    watch: {},
    computed: {
        welcomeMessage: function() {
            let welcomeText = ``;
            if (this.dasTemplateGroup) {
                const external_das_info = (env && env['external_das_info_url']) || 'https://www.dbca.wa.gov.au/licences-and-permits/online-disturbance-approval-system';
                const internal_das_info = (env && env['internal_das_info_url']) || 'https://dpaw.sharepoint.com/Divisions/pws/cem/SitePages/Disturbance-Approval-System-%28DAS%29.aspx';
                const das_support_email = (env && env['support_email']) || 'das@dbca.wa.gov.au';
                welcomeText = `Welcome to the ${this.dasSystemName} online system dashboard.<p/><p/>
                    Here you can access your existing approvals, view any proposals in progress, lodge new
                    proposals or submit information required to comply with requirements listed on your approval.<p/><p/>
                    For further information and FAQ's please visit <a href="${external_das_info}" target="_blank">Online Disturbance Approval System</a> for all external users
                    and <a href="${internal_das_info}" target="_blank">Disturbance Approval System (DAS)</a> for all internal users or you can email <a href="mailto:${das_support_email}">${das_support_email}</a>.`
            }
            return welcomeText;
        },
        show_das_map : function(){
                if (env && env['show_das_map'] &&  env['show_das_map'].toLowerCase()=="true"  ){
                    return true;
                } else {
                    return false;
                }
            }

    },
    methods: {
    },
    mounted: function () {
    },
    created: function() {
        // retrieve template group
        fetch('/template_group',{
            emulateJSON:true
            }).then(async (res)=>{
                if (!res.ok) {
                    return await res.json().then(err => { throw err });
                }
                //this.template_group = res.body.template_group;
                let data = await res.json();
                if (data.template_group === 'apiary') {
                    this.apiaryTemplateGroup = true;
                } else {
                    this.dasTemplateGroup = true;
                }
        }).catch(err=>{
            console.log(err);
        });
    },

}
</script>
