<template lang="html">
    <div id="proposalRequirementDetail">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Requirement" large>
            <div class="container-fluid">
                <div class="row">

                    <datatable ref="spatial_query_metrics_details_table"
                        :id="spatial_query_metrics_details_id" 
                        :dtOptions="dtOptionsSchemaMetrics"
                        :dtHeaders="dtHeadersSchemaMetrics"
                    />
                    <!--
                    1:{{metricsData}}<br>
                    2:{{dtOptionsSchemaMetrics}}<br>
                    3:{{spatial_query_metrics}}
                    -->

                </div>
            </div>
        </modal>
    </div>
</template>

<script>
import { v4 as uuidv4 } from 'uuid';
import datatable from '@/utils/vue/datatable.vue'
import modal from '@vue-utils/bootstrap-modal.vue'
import { constants } from '@/utils/hooks';
export default {
    name:'Requirement-Detail',
    components:{
        modal,
        datatable,
    },
    props:{
            proposal_id:{
                type:Number,
                required: true
            },
            metrics: {
                type: Array,
                required: true
            },
    },
    data:function () {
        let vm = this;
        return {
            spatial_query_metrics_details_id: 'spatial_query_metrics_details-datatable-'+uuidv4(),
            pOptionsBody: 'pOptionsBody' + uuidv4(),
            pQuestionBody: 'pQuestionBody' + uuidv4(),
            isModalOpen: false,
            spatial_query_metrics: [],
            //dtHeadersSchemaMetrics: [],
            //dtOptionsSchemaMetrics: {},
            //metricsData: {}, //{"data": []},
            metricsData: {
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "data": [{}]
		//"data": [{"question":"100  initialised"}]
            },

            dtHeadersSchemaMetrics: ["Question"],
            dtOptionsSchemaMetrics:{
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                serverSide: true,
                autowidth: false,
                processing: true,
                "ajax": function (data, callback) {
		    callback(
                      vm.metricsData
		    );
		  },

                columnDefs: [
                    { visible: true } 
                ],
                columns: [
                    { 
                        data: "question",
                        searchable: false,
                    },
                ],
            },



        }
    },
    computed: {
    },
    watch: {
    },
    methods:{
        ok:function () {
            this.close()
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            this.isModalOpen = false;
            $(this.$refs.standard_req).val(null).trigger('change');
        },
       eventListeners:function () {
            // let vm = this;
       }
   },
   mounted:function () {
        let vm =this;
        this.$nextTick(()=>{
            vm.eventListeners();
        });
   }
}
</script>

<style lang="css">
</style>
