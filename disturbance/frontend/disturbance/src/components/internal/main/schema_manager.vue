<template>
<div class="container" id="schema-manager">
    <div class="col-md-12">

    <SchemaTabs :tabs="tabs" :initialTab="initialTab">

        <template #tab-panel-masterlist>
            <FormSection :form-collapse="false" label="Schema Masterlist Questions" Index="schema-masterlist">
                <SchemaMasterlist />
            </FormSection>
        </template>
        <template #tab-panel-proposal-type>
            <FormSection :form-collapse="false" label="Schema ProposalType Section" Index="schema-proposal-type">
                <SchemaProposalType />
            </FormSection>
        </template>
        <template #tab-panel-question>
            <FormSection :form-collapse="false" label="Schema Section Question" Index="schema-section-question">
                <SchemaQuestion />
            </FormSection>
        </template>
        <template v-if="show_das_map" #tab-panel-spatial-query-question>
            <FormSection :form-collapse="false" label="Spatial Query Questions" Index="spatial-query-questions">
                <SpatialQueryQuestion />
            </FormSection>
        </template>
        <!--<template v-if="show_das_map" slot="tab-panel-spatial-query-metrics"><SpatialQueryMetrics /></template>-->
        <!-- <template slot="tab-panel-group"><SchemaGroup /></template> -->

    </SchemaTabs>

    </div>
</div>
</template>
<script>
import FormSection from '@/components/forms/section_toggle.vue';
import SchemaTabs from '@/components/forms/tab.vue'
import SchemaQuestion from '@/components/internal/main/schema_question.vue'
import SchemaMasterlist from '@/components/internal/main/schema_masterlist.vue'
import SchemaProposalType from '@/components/internal/main/schema_proposal_type.vue'
import SpatialQueryQuestion from '@/components/internal/main/spatial_query_question.vue'
// import SpatialQueryMetrics from '@/components/internal/main/spatial_query_metrics.vue'

export default {
    name: 'schema-manager',
    components: {
        SchemaTabs,
        SchemaQuestion,
        SchemaMasterlist,
        SchemaProposalType,
        SpatialQueryQuestion,
        //SpatialQueryMetrics,
        // SchemaGroup,
        FormSection,
    },
    computed: {
        show_das_map : function(){
                if (env && env['show_das_map'] &&  env['show_das_map'].toLowerCase()=="true"  ){
                    return true;
                } else {
                    return false;
                }
            },
        tabs: function(){
            if(this.show_das_map){
                return [
                {'masterlist': 'Schema Masterlist'},
                {'proposal-type': 'Proposal Type Sections'},
                // {'group': 'Section Groups'},
                {'question': 'Section Questions'},
                {'spatial-query-question': 'Spatial Query Questions'},
                //{'spatial-query-metrics': 'Spatial Query Metrics'},
                ]
            }
            return [
                    {'masterlist': 'Schema Masterlist'},
                    {'proposal-type': 'Proposal Type Sections'},
                    // {'group': 'Section Groups'},
                    {'question': 'Section Questions'},
                ]
        }
    },
    data() {
        return {
            initialTab: 'masterlist',
            original_tabs: [
                {'masterlist': 'Schema Masterlist'},
                {'proposal-type': 'Proposal Type Sections'},
                // {'group': 'Section Groups'},
                {'question': 'Section Questions'},
                {'spatial-query-question': 'Spatial Query Questions'},
                //{'spatial-query-metrics': 'Spatial Query Metrics'},
            ],
        }
    },
}
</script>
