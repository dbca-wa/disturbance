<template>
<div class="container" id="externalDash">
    <div class="row">
        <div class="col-sm-12">
            <div class="well well-sm">
                <div class="col-md-9">
                    <span v-html="welcomeMessage"></span>
                </div>
                <div class="row">
                    <div class="col-md-3 text-right">
                        <router-link  style="margin-top:25px;" class="btn btn-primary" :to="{ name: 'apply_proposal' }">New Proposal</router-link>
                    </div>
                </div>
                <!--p>
                    Welcome to the {{system_name}} online system dashboard.<br/><br/> Here you can access your existing approvals/licences, view any proposals/applications in progress, lodge new<br/> proposals/applications or submit information required to comply with requirements listed on your approval/license
                </p-->
            </div>
        </div>
    </div>
    <MapDashboard  v-if="show_das_map && !apiaryTemplateGroup" level="external" :is_external="true"/>
    <ProposalDashTable level='external' :url='proposals_url'/>
    <ApprovalDashTable level='external' :url='approvals_url'/>
    <ComplianceDashTable level='external' :url='compliances_url'/>
    <!-- <MapDashboard  v-if="show_das_map" level="external" :is_external="true"/> -->
</div>
</template>
<script>

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
        MapDashboard
    },
    watch: {},
    computed: {
        welcomeMessage: function() {
            let welcomeText = ``;
            if (this.dasTemplateGroup) {
                welcomeText = `Welcome to the ${this.dasSystemName} online system dashboard.<p/><p/>
                    Here you can access your existing approvals, view any proposals in progress, lodge new
                    proposals or submit information required to comply with requirements listed on your approval.`
            } else if (this.apiaryTemplateGroup) {
                welcomeText = `Welcome to the ${this.apiarySystemName} online dashboard.<p/><p/>
                    Here you can access your existing apiary authorities, view any applications in progress, lodge new
                    applications or submit information required to comply with requirements listed on your authority.`
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
                //this.template_group = res.body.template_group;
                let data = await res.json();
                if (data.template_group === 'apiary') {
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
