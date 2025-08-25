<template>
<div class="container">
    <div v-if="approvalId">
        <div v-if="apiaryApproval">
        </div>
        <div v-else>
            <Approval 
                :approvalId="approvalId"
                :is_internal="false"
                :is_external="true"
            />
        </div>
    </div>

</div>
</template>
<script>

import Approval from './approval.vue';
export default {
    name: 'ApprovalWrapper',
    data() {
        // let vm = this;
        return {
            approvalId: null,
            apiaryApproval: false,
        }
    },
    components:{
        Approval,
    },
    watch: {},
    computed: {
    },
    methods: {
    },
    mounted: function () {
    },
    beforeRouteEnter: function(to, from, next) {
        fetch(`/api/approvals/${to.params.approval_id}/approval_wrapper.json`).then(
            async (res) => {
                if (!res.ok) {
                    return res.json().then(err => { throw err });
                }
                let data = await res.json();
                next(vm => {
                    console.log(data)
                    vm.approvalId = data.id;
                    //   vm.apiaryApproval = res.body.apiary_approval;
                });
            }).catch(err => {
              console.log(err);
            });
    },
}
</script>
