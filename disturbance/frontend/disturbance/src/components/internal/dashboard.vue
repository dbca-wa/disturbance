<template>
<div class="container" id="internalDash">
    <div v-if="show_das_change_msg && dasTemplateGroup" class="row">
        <div class="col-sm-12">
            <div class="alert alert-info">
                <div class="col-md-9">
                    <span v-html="dasChangeMsg"></span>
                </div>
                <div class="row">
                   
                </div>
                <!--p>
                    Welcome to the {{system_name}} online system dashboard.<br/><br/> Here you can access your existing approvals/licences, view any proposals/applications in progress, lodge new<br/> proposals/applications or submit information required to comply with requirements listed on your approval/license
                </p-->
            </div>
        </div>
    </div>
    <MapDashboard v-if="show_das_map  && !apiaryTemplateGroup" level="internal" :is_internal="true" />
    <ProposalDashTable level="internal" :url="proposals_url"/>
    <ReferralDashTable :url="referrals_url"/>
    <!-- <MapDashboard v-if="show_das_map" level="internal" :is_internal="true" /> -->
</div>
</template>
<script>
import ProposalDashTable from '@common-utils/proposals_dashboard.vue'
import ReferralDashTable from '@common-utils/referrals_dashboard.vue'
import MapDashboard from '@/components/common/das/map_dashboard_internal.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'ExternalDashboard',
    data() {
        let vm = this;
        return {
            //proposals_url: api_endpoints.proposals,
            //proposals_url: api_endpoints.proposals_paginated_internal,
            //proposals_url: '/api/list_proposal/?format=datatables',
            //proposals_url: api_endpoints.list_proposals,
            proposals_url: api_endpoints.proposals_paginated_internal,
            referrals_url: api_endpoints.referrals_paginated_internal,
            apiaryTemplateGroup: false,
            dasTemplateGroup: false,
        }
    
    },
    watch: {},
    components: {
        ProposalDashTable,
        ReferralDashTable,
        MapDashboard,
    },
    computed: {
        dasChangeMsg: function() {
            let dasChangeText = ``;
            if (this.dasTemplateGroup) {
                dasChangeText = `Welcome to DAS Phase II. For more information and FAQ's please visit <a href="https://www.dbca.wa.gov.au/licences-and-permits/online-disturbance-approval-system" target="_blank">Online Disturbance Approval System </a>
                    for all external users and <a href="https://dpaw.sharepoint.com/Divisions/pws/cem/SitePages/Disturbance-Approval-System-(DAS).aspx" target="_blank">Disturbance Approval System (DAS) </a>
                    for all internal users or you can email <a href="mailto:das@dbca.wa.gov.au">das@dbca.wa.gov.au.</a> <p/><p/>`
            }
            return dasChangeText;
        },
        show_das_map : function(){
                if (env && env['show_das_map'] &&  env['show_das_map'].toLowerCase()=="true"  ){
                    return true;
                } else {
                    return false;
                }
            },
        show_das_change_msg : function(){
                if (env && env['show_das_change_msg'] &&  env['show_das_change_msg'].toLowerCase()=="true"  ){
                    return true;
                } else {
                    return false;
                }
            },

    },
    methods: {},
    mounted: function () {
    },

    created: function() {
        // retrieve template group
        this.$http.get('/template_group',{
            emulateJSON:true
            }).then(res=>{
                //this.template_group = res.body.template_group;
                if (res.body.template_group === 'apiary') {
                    this.apiaryTemplateGroup = true;
                } else {
                    this.dasTemplateGroup = true;
                }
        },err=>{
        console.log(err);
        });
    },

}
</script>
