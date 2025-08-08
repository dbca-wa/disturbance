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
        </div>
        <div v-else>
            <Proposal :proposalId="proposalId"/>
        </div>
    </div>

</div>
</template>
<script>

import ProposalApiary from './proposal_apiary.vue';
import Proposal from './proposal.vue';
export default {
    name: 'InternalProposalWrapper',
    data() {
        return {
            //proposal: {},
            proposalId: null,
            applicationTypeName: '',
        }
    },
    components:{
        Proposal,
        ProposalApiary,
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
        fetch(`/api/proposal/${to.params.proposal_id}/internal_proposal_wrapper.json`)
        .then(async res => {
            const data = await res.json();
            next(vm => {
                vm.proposalId = data.id;
                vm.applicationTypeName = data.application_type_name;
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
