<template>
<div class="container" id="internalDash">
    <div class="row">
        <div class="col-sm-12">
            <FormSection :form-collapse="false" label="Approvals" index="approvals">
                    <ApprovalDashTable level="internal" :url="approvals_url" />
            </FormSection>
        </div>
    </div>
</div>
</template>
<script>
import FormSection from '@/components/forms/section_toggle.vue';
import ApprovalDashTable from '@common-utils/approvals_dashboard.vue'
import {
  api_endpoints,
}
from '@/utils/hooks'
export default {
    name: 'InternalApprovalDashboard',
    data() {
        // let vm = this;
        return {
            //approvals_url: api_endpoints.approvals,
            approvals_url: api_endpoints.approvals_paginated_internal,
        }
    
    },
    watch: {},
    components: {
        FormSection,
        ApprovalDashTable,
    },
    computed: {
    },
    methods: {},
    mounted: function () {
    }
}
</script>
