<template>
<!--div class="container" id="referralWrapper"-->
<div class="container">
       <!--ApplicationDashTable level='external' :url='applications_url'/>
    <div>
        <LicenceDashTable level='external' :url='licences_url'/>
        <ReturnDashTable level='external' :url='returns_url'/>
    </div-->
    <div v-if="proposalId">
        <div v-if="apiaryGroupApplication">
            <ProposalApiary :proposalId="proposalId"/>
        </div>
        <div v-else-if="temporaryUseApplication">
            <ProposalTemporaryUse :proposalId="proposalId" />
        </div>
        <div v-else>
            <Proposal :proposalId="proposalId"/>
        </div>
    </div>

</div>
</template>
<script>

/*import datatable from '@/utils/vue/datatable.vue'
import ApplicationDashTable from '@common-components/applications_dashboard.vue'
import LicenceDashTable from '@common-components/licences_dashboard.vue'
import ReturnDashTable from '@common-components/returns_dashboard.vue'
*/
//import Referral from './referral.vue';
//import ApiaryReferral from './apiary_referral.vue';
import ProposalApiary from './proposal_apiary.vue';
import ProposalTemporaryUse from '@/components/internal/proposals/proposal_temporary_use.vue'
import Proposal from './proposal.vue';
export default {
    name: 'InternalProposalWrapper',
    data() {
        let vm = this;
        return {
            //proposal: {},
            proposalId: null,
            applicationTypeName: '',
            //apiaryApplication: false,
            /*
            applications_url: helpers.add_endpoint_join(api_endpoints.applications_paginated,'external_datatable_list/?format=datatables'),
            licences_url: helpers.add_endpoint_join(api_endpoints.licences_paginated,'external_datatable_list/?format=datatables'),
            returns_url: helpers.add_endpoint_join(api_endpoints.returns_paginated,'user_datatable_list/?format=datatables'),
            empty_list: '/api/empty_list',
            */
        }
    },
    components:{
        /*
        ApplicationDashTable,
        LicenceDashTable,
        ReturnDashTable,
        */
        Proposal,
        ProposalApiary,
        ProposalTemporaryUse,
    },
    watch: {},
    computed: {
        apiaryGroupApplication: function() {
            let retVal = false;
            //if (this.applicationTypeName === 'Apiary'){
            if (['Apiary', 'Site Transfer'].includes(this.applicationTypeName)) {
                retVal = true;
            }
            return retVal;
        },
        temporaryUseApplication: function() {
            let retVal = false;
            if (this.applicationTypeName === 'Temporary Use'){
                retVal = true;
            }
            return retVal;
        },
        /*
        proposalId: function() {
            let retVal = false;
            if (this.proposal && this.proposal.id) {
                retVal = true;
            }
            return retVal;
        },
        apiaryApplication: function() {
            let returnVal = false;
            if (this.proposal && this.proposal.application_type === 'Apiary') {
                returnVal = true;
            }
            console.log(returnVal)
            return returnVal;
        },
        */
    },
    methods: {
    },
    mounted: function () {
    },
    beforeRouteEnter: function(to, from, next) {
          Vue.http.get(`/api/proposal/${to.params.proposal_id}/internal_proposal_wrapper.json`).then(res => {
              next(vm => {
                  vm.proposalId = res.body.id;
                  vm.applicationTypeName = res.body.application_type_name;
                  /*
                  vm.original_proposal = helpers.copyObject(res.body);
                  if (vm.proposal.applicant) {
                      vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                  }
                  // Create boolean values for each application type and add logic to the following conditional
                  if (vm.proposal && vm.proposal.application_type === 'Apiary') {
                      vm.apiaryApplication = true;
                  }
                  */
              });
            },
            err => {
              console.log(err);
            });
    },
}
</script>
