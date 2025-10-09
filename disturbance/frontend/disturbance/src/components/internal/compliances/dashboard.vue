<template>
<div class="container" id="internalDash">
    <div class="row">
        <div class="col-sm-12">
            <FormSection :form-collapse="false" label="Compliances with requirements" Index="compliances">
                <ComplianceDashTable level="internal" :url="compliances_url"/>
            </FormSection>
        </div>
    </div>
</div>
</template>
<script>
import ComplianceDashTable from '@common-utils/compliances_dashboard.vue'
import {
  api_endpoints,
}
from '@/utils/hooks'
import FormSection from '@/components/forms/section_toggle.vue';
export default {
    name: 'InternalCompliancesDashboard',
    data() {
        // let vm = this;
        return {
            //compliances_url: api_endpoints.compliances,
            compliances_url: api_endpoints.compliances_paginated_internal,
        }
    
    },
    watch: {},
    components: {
        ComplianceDashTable,
        FormSection,
    },
    computed: {
    },
    methods: {},
    mounted: function () {
    }
}
</script>
