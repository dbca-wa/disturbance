<template>
<div class="container">
    <div v-if="proposalId">
        <div v-if="temporaryProposal">
        </div>
        <div v-else>
            <Proposal :proposalId="proposalId"/>
        </div>
    </div>
</div>
</template>

<script>
import Proposal from '@/components/external/proposal_external.vue'

export default {
    name: 'ExternalProposalWrapper',
    data() {
        // let vm = this;
        return {
            proposalId: null,
            applicationTypeName: '',
        }
    },
    components:{
        Proposal,
    },
    computed: {
        temporaryProposal: function() {
            let retVal = false;
            if (this.applicationTypeName === 'Temporary Use') {
                retVal = true;
            }
            return retVal;
        },

    },
    beforeRouteEnter: async function(to) {
        // let vm = this
        // fetch(`/api/proposal/${to.params.proposal_id}/internal_proposal_wrapper.json`).then(
        //     async res => {
        //         if (!res.ok) {
        //             return res.json().then(err => { throw err });
        //         }
        //         let data = await res.json();
        //         next(vm => {
        //             vm.proposalId = data.id;
        //             vm.applicationTypeName = data.application_type_name;
        //         });
        //   }).catch(err => {
        //     console.log(err);
        //   });
        // return a callback from beforeRouteEnter instead of calling next(vm => ...) as it's deprecated.
        try {
            const response = await fetch(`/api/proposal/${to.params.proposal_id}/internal_proposal_wrapper.json`);
            if (!response.ok) {
                return response.json().then(err => { throw err });
            }
            const data = await response.json();
            return (vm) => {
                vm.proposalId = data.id;
                vm.applicationTypeName = data.application_type_name;
            };
        } catch (err) {
            console.log(err);
        }
    },
}
</script>
