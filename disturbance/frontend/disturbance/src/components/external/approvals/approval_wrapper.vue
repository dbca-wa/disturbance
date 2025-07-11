<template>
<div class="container">
    <div v-if="approvalId">
        <div v-if="apiaryApproval">
            <ApiaryApproval 
                :approvalId="approvalId"
                :is_internal="false"
                :is_external="true"
            />
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

import ApiaryApproval from './apiary_approval.vue';
import Approval from './approval.vue';
export default {
    name: 'ApprovalWrapper',
    data() {
        let vm = this;
        return {
            approvalId: null,
            apiaryApproval: false,
        }
    },
    components:{
        Approval,
        ApiaryApproval,
    },
    watch: {},
    computed: {
    },
    methods: {
    },
    mounted: function () {
    },
    beforeRouteEnter: function(to, from, next) {
          Vue.http.get(`/api/approvals/${to.params.approval_id}/approval_wrapper.json`).then(res => {
              next(vm => {
                  console.log(res.body)
                  vm.approvalId = res.body.id;
                  vm.apiaryApproval = res.body.apiary_approval;
              });
            },
            err => {
              console.log(err);
            });
    },
}
</script>
