<template>
<div class="container" id="internalDash">
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
}
from '@/utils/hooks'
export default {
    name: 'ExternalDashboard',
    data() {
        // let vm = this;
        return {
            //proposals_url: api_endpoints.proposals,
            //proposals_url: api_endpoints.proposals_paginated_internal,
            //proposals_url: '/api/list_proposal/?format=datatables',
            //proposals_url: api_endpoints.list_proposals,
            proposals_url: api_endpoints.proposals_paginated_internal,
            referrals_url: api_endpoints.referrals_paginated_internal,
            apiaryTemplateGroup: false,
            dasTemplateGroup: false,
            template_group_res:{},
        }
    
    },
    watch: {},
    components: {
        ProposalDashTable,
        ReferralDashTable,
        MapDashboard,
    },
    computed: {
        show_das_map : function(){
                if (env && env['show_das_map'] &&  env['show_das_map'].toLowerCase()=="true"  ){
                    return true;
                } else {
                    return false;
                }
            }
    },
    methods: {},
    mounted: function () {
    },

    created: function() {
        let vm= this;
        // retrieve template group
        fetch('/template_group',{ emulateJSON:true }).then(
            async (res)=>{
                if (!res.ok) { return res.json().then(err => { throw err }); }
                //this.template_group = res.body.template_group;
                vm.template_group_res = await res.json();
                if (vm.template_group_res.template_group === 'apiary') {
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
