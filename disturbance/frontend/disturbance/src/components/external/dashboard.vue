<template>
<div class="container" id="externalDash">
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
    
    <template v-if="show_das_map && !apiaryTemplateGroup">
        <MapDashboard level="external" :is_external="true"/>
    </template>
    <!-- <MapDashboard  v-if="show_das_map && !apiaryTemplateGroup" level="external" :is_external="true"/> -->
    <ProposalDashTable level='external' :url='proposals_url'/>
    <ApprovalDashTable level='external' :url='approvals_url'/>
    <ComplianceDashTable level='external' :url='compliances_url'/>
    <!-- <MapDashboard  v-if="show_das_map" level="external" :is_external="true"/> -->
</div>
</template>
<script>

import datatable from '@/utils/vue/datatable.vue'
import ProposalDashTable from '@common-utils/proposals_dashboard.vue'
import ApprovalDashTable from '@common-utils/approvals_dashboard.vue'
import ComplianceDashTable from '@common-utils/compliances_dashboard.vue'
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
            show_das_map: false,
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
        dasChangeMsg: function() {
            let dasChangeText = ``;
            if (this.dasTemplateGroup) {
                dasChangeText = `Welcome to DAS Phase II. For more information and FAQ's please visit <a href="https://www.dbca.wa.gov.au/licences-and-permits/online-disturbance-approval-system" target="_blank">Online Disturbance Approval System </a>
                    for all external users and <a href="https://dpaw.sharepoint.com/Divisions/pws/cem/SitePages/Disturbance-Approval-System-(DAS).aspx" target="_blank">Disturbance Approval System (DAS) </a>
                    for all internal users or you can email <a href="mailto:das@dbca.wa.gov.au">das@dbca.wa.gov.au.</a> <p/><p/>`
            }
            return dasChangeText;
        },
        // show_das_map : function(){
        //         if (env && env['show_das_map'] &&  env['show_das_map'].toLowerCase()=="true"  ){
        //             return true;
        //         } else {
        //             return false;
        //         }
        //     },
        show_das_change_msg : function(){
                if (env && env['show_das_change_msg'] &&  env['show_das_change_msg'].toLowerCase()=="true"  ){
                    return true;
                } else {
                    return false;
                }
            },

    },
    methods: {
    },
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
        
        if (env && env['show_das_map'] &&  env['show_das_map'].toLowerCase()=="true"  ){
            this.show_das_map = true;
        } else {
            this.show_das_map = false;
        }
    },
    

}
</script>
