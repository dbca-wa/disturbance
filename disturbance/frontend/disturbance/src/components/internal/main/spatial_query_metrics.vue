<template lang="html">
  <div id="schema-question">

    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Spatial Query Metrics
                        <a :href="'#'+pQuestionBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pQuestionBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pQuestionBody">
                    <div class="row"><br/></div> 
                    <div class="row">
                        <div class="col-md-12">
                            <div class="form-group">

                                <datatable ref="spatial_query_metrics_table"
                                    :id="spatial_query_metrics_id" 
                                    :dtOptions="dtOptionsSchemaQuestion"
                                    :dtHeaders="dtHeadersSchemaQuestion" 
                                />

<!--
                                <datatable ref="spatial_query_layers_used_table"
                                    :id="spatial_query_layers_used_id" 
                                    :dtOptions="dtOptionsLayersUsed"
                                    :dtHeaders="dtHeadersLayersUsed" 
                                />
-->


                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <modal class="my-modal" transition="modal fade" @ok="ok()" title="Metrics" xxlarge>
        <div class="container-fluid">
	<div class="row">
	    <div class="col-md-12">
		<div class="form-group">
		    <datatable ref="spatial_query_metrics_details_table"
			:id="spatial_query_metrics_details_id" 
			:dtOptions="dtOptionsSchemaMetrics"
			:dtHeaders="dtHeadersSchemaMetrics"
		    />
		</div>
	    </div>
	</div>
        </div>

    </modal>

  </div>
</template>

<script>
import MetricsDetails from '@/components/internal/main/spatial_query_metrics.vue'
import datatable from '@/utils/vue/datatable.vue'
import modal from '@vue-utils/bootstrap-modal.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'

export default {
    name:'schema-question',
    components: {
        modal,
        datatable,
        MetricsDetails,
    },
    props:{
    },
    data:function () {
        let vm = this;
        vm.spatial_query_metrics_url = helpers.add_endpoint_join(api_endpoints.spatial_query_metrics_paginated, 'spatial_query_metrics_datatable_list/?format=datatables');
        vm.spatial_query_layer_used_url = helpers.add_endpoint_join(api_endpoints.spatial_query_layers_used_paginated, 'spatial_query_layers_used_datatable_list/?format=datatables');
        console.log(vm.spatial_query_metrics_url)
        console.log(vm.spatial_query_layer_used_url)

        return {
            spatial_query_metrics_id: 'spatial_query_metrics-datatable-'+vm._uid,
            spatial_query_metrics_details_id: 'spatial_query_metrics_details-datatable-'+vm._uid,
            spatial_query_layers_used_id: 'spatial_query_layers_used-datatable-'+vm._uid,
            pOptionsBody: 'pOptionsBody' + vm._uid,
            pQuestionBody: 'pQuestionBody' + vm._uid,
            isModalOpen: false,
            isNewEntry: false,
            missing_fields: [],
            spatial_query_metrics: [],
            modal_id: 0,

            metricsData: {}, //{"data": []},
//            metricsData: {
//                "recordsTotal": 2,
//                "recordsFiltered": 2,
//                //"data": []
//		"data": [{"question":"100  initialised"}]
//            },

            dtHeadersSchemaQuestion: ["ID", "Lodgement Number", "When", "Query Time", "API Time (s)", "Request Type", "Action"],
            dtOptionsSchemaQuestion:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                serverSide: true,
                autowidth: false,
                processing: true,
                searchDelay: 1000,
                ajax: {
                    "url": vm.spatial_query_metrics_url,
                    "dataSrc": 'data',
                    //"data": function (d) {
                    //    d.proposal_type_id = vm.filterTableProposalType;
                    //    d.section_id = vm.filterTableSection;
                    //    d.group_id = vm.filterTableGroup;
                    //}
                },
                dom: 'lBfrtip',
                buttons:[
                    {
                        extend: 'excel',
                        exportOptions: {
                            columns: ':not(.noexport)',
                            orthogonal:'export'
                        }
                    },
                    {
                        extend: 'csv',
                        exportOptions: {
                            columns: ':not(.noexport)',
                            orthogonal:'export'
                        }
                    },
                ],
              
                //columnDefs: [
                //    { visible: false, targets: [ 0, 1, 2, ] } 
                //],
                columnDefs: [
                    { visible: true } 
                ],
                columns: [
                    { 
                        data: "id",
                        searchable: true,
                    },
                    { 
                        data: "lodgement_number",
                        searchable: true,
                    },
                    { 
                        data: "when",
                        mRender:function (data,type,full) {
                            return data.replace('T',' ').replace('Z','');
                        },
                        searchable: false,
                    },
                    { 
                        data: "total_query_time",
                        searchable: false,
                        orderable: true,
                    },
                    { 
                        data: "total_api_time",
                        mRender:function (data,type,full) {
                            return full.response_cached ? data + ' (Cached)' : data
                        }

                    },
                    { 
                        data: "request_type",
                        searchable: true,
                    },
                    { 
                        data: "id",
                        searchable: false,
                        mRender:function (data,type,full) {
                            //var column = `<a class="view-row" data-metrics=data.metrics data-rowid=\"__ROWID__\">View</a><br/>`;
                            //return column.replace(/__ROWID__/g, full.id);
                            let links = '';
                            links +=  `<a href='#' class="updatedMetricsDetails" data-id="${full.id}">View</a><br/>`;
                            console.log(data)
                            return links;
                        }
                    },
                ],
                rowId: function(_data) {
                    return _data.id
                },
            },

//            dtHeadersLayersUsed: ["ID", "Lodgement Number", "Layer name"],
//            dtOptionsLayersUsed:{
//                language: {
//                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
//                },
//                responsive: true,
//                serverSide: true,
//                processing: true,
//                ajax: {
//                    "url": vm.spatial_query_layer_used_url,
//                    "dataSrc": 'data',
//                },
//                columnDefs: [
//                    { visible: true } 
//                ],
//                columns: [
//                    { 
//                        data: "id",
//                    },
//                    { 
//                        data: "lodgement_number",
//                    },
//                    { 
//                        data: "layer_data.name",
//                    },
//                ],
//                rowId: function(_data) {
//                    return _data.id
//                },
//            },


            dtHeadersSchemaMetrics: ["Question", "Answer", "Layer Name", "Condition", "Result", "Assessor Info", "Query Time (s)", "Error", "Retrive Layer Time (s)", "Operator Response"],
            //dtHeadersSchemaMetrics: ["Question", "Answer", "Layer Name", "Condition", "Result", "Assessor Info", "Query Time (s)", "Layer Cached", "Error", "Retrive Layer Time (s)", "Operator Response"],
            //dtHeadersSchemaMetrics: ["Question", "Answer", "Layer Name"],
            //dtHeadersSchemaMetrics: ["Question"],
            dtOptionsSchemaMetrics:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
//    fixedColumns: {
//        left: 1,
//        right: 1
//    },
//    paging: true,
    //scrollCollapse: true,
    //scrollX: true,
    //scrollY: 300,

                //serverSide: false,
                //////autowidth: false,
                //processing: true,
//                "ajax": function (data, callback, settings) {
//		    callback(
//                        //vm.metricsData
//			{
//			    "recordsTotal": 0,
//			    "recordsFiltered": 0,
//			    //"data": [{"question":"1.2  ddd"}, {"question":"2.2  eee", }]
//			    "data": []
//			}
//
//		    );
//		  },
                dom: 'lBfrtip',
                buttons:[
                    {
                        extend: 'excel',
                        exportOptions: {
                            columns: ':not(.noexport)',
                            orthogonal:'export'
                        }
                        /*
                        exportOptions: {
                            columns: ':visible'
                            //columns: vm.dt_headers
                        }
                        */
                    },
                    {
                        extend: 'csv',
                        exportOptions: {
                            columns: ':not(.noexport)',
                            orthogonal:'export'
                        }
                        /*
                        exportOptions: {
                            columns: ':visible'
                            //columns: vm.dt_headers
                            //columns: 'lodgement_number'
                        }
                        */
                    },
                ],


                columnDefs: [
                    { visible: true } 
                ],
                columns: [
                    {
                        data: "question",
                        searchable: true,
			'render': function (value) {
	  		    return helpers.dtPopover(value, 35);
			},
                        'createdCell': helpers.dtPopoverCellFn,
                    },
                    {
                        data: "answer_mlq",
                        searchable: true,
			'render': function (value) {
	  		    return helpers.dtPopover(value, 35);
			},
                        'createdCell': helpers.dtPopoverCellFn,
                    },
                    {
                        data: "layer_name",
                        searchable: true,
                    },
		    {
			data: "condition",
			searchable: false,
		    },
		    {
			data: "result",
			'render': function (value) {
	  		    return helpers.dtPopover(value, 20);
			},
                        'createdCell': helpers.dtPopoverCellFn,
		    },
		    {
			data: "assessor_answer",
			'render': function (value) {
	  		    return helpers.dtPopover(value, 20);
			},
                        'createdCell': helpers.dtPopoverCellFn,
		    },
		    {
			data: "time",
			searchable: false,
		    },
//                    {
//	 	        data: "layer_cached",
//			'render': function (value) {
//	  		    return value=='true' ? 'Yes' : 'No';
//			},
//		    },

		    {
			data: "error",
			'render': function (value) {
                            if (value=='None') {
                                return '';
                            }
	  		    //return helpers.dtPopover(value, 20);
			},
                        //'createdCell': helpers.dtPopoverCellFn,
		    },
		    {
			data: "time_retrieve_layer",
			searchable: false,
                        visible: false,
		    },
		    {
			data: "operator_response",
//			'render': function (value) {
//	  		    return helpers.dtPopover(value, 20);
//			},
//                        'createdCell': helpers.dtPopoverCellFn,
		    },


                ],
            },
        }

    },
    watch:{
    },
    computed: {    
    },
    methods: {
        updatedMetricsDetails(rowid){
            let self = this;
            self.$refs.spatial_query_metrics_table.row_of_data = self.$refs.spatial_query_metrics_table.vmDataTable.row('#'+rowid);
            let spatial_query_metrics = self.$refs.spatial_query_metrics_table.row_of_data.data().metrics; 
            console.log(spatial_query_metrics)

            //this.$refs.spatial_query_metrics_details_table.vmDataTable.clear().rows.add( spatial_query_metrics ).draw()
            this.isModalOpen = true;
            this.$refs.spatial_query_metrics_details_table.vmDataTable.clear().draw()
            this.$refs.spatial_query_metrics_details_table.vmDataTable.rows.add( spatial_query_metrics )
            this.$refs.spatial_query_metrics_details_table.vmDataTable.columns.adjust().draw()
        },
        close: function() {
            const self = this;
            self.isModalOpen = false;
        },
        initEventListeners: function(){
            let self = this;

            self.$refs.spatial_query_metrics_table.vmDataTable.on('click', '.updatedMetricsDetails', function(e) {
                e.preventDefault();
                var rowid = $(this).attr('data-id');
                //console.log(rowid)
                self.updatedMetricsDetails(rowid);
            });
        },
    },
    mounted: function() {
        this.form = document.forms.spatial_query_metrics;
        this.$nextTick(() => {
            this.initEventListeners();
        });
    }
}
</script>

<style lang="css">


</style>
