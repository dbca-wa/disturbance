<template lang="html">
    <div id="historyDetail" v-show='showApprovalHistory'>

        <modal transition="modal fade" :title="dashboardTitle" large force>
            <div class="container-fluid">

                <form class="form-horizontal" name="approvalHistoryForm">

                    <div class="col-sm-12">

                        <datatable ref="approval_history_table" 
                            id="approval-history-table" 
                            :dtOptions="dtOptionsApprovalHistory"
                            :dtHeaders="dtHeadersApprovalHistory" 
                        />

                    </div>
                </form>

            </div>
            <template #footer />
        </modal>

    </div>
</template>
<script>
import modal from "@vue-utils/bootstrap-modal.vue";
import datatable from "@vue-utils/datatable.vue";
// import alert from '@vue-utils/alert.vue';
import {
    api_endpoints,
    helpers,
    constants
}from '@/utils/hooks'
export default {
    name: 'ApprovalHistoryModal',
    props: {
        approval_id: String,
    },
    components:{
        modal,
        datatable,
    },
    data() {
        let vm = this;
        vm.history_url = helpers.add_endpoint_json(api_endpoints.approvals,'approval_history');
        return {
            isModalOpen: false,
            processingDetails: false,
            apiaryTemplateGroup: false,
            dasTemplateGroup: false,

            //approval_history_id: '0',
            approval_history_id: null,
            historyTable: null,
            popoversInitialised: false,
            dtOptionsApprovalHistory:{
                // language: {
                //     processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                // },
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                deferRender: true, 
                autowidth: true,
                order: [[2, 'desc']],
                dom:
                    "<'row'<'col-sm-5'l><'col-sm-6'f>>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                processing:true,
                ajax: {
                    "url": vm.history_url, 
                    type: 'GET',
                    "dataSrc": '',
                    data: function(_data) {
                        console.log(_data)
                        _data.approval_history_id = vm.approval_history_id
                    return _data;
                    },
                },
                //order: [0],
                columnDefs: [
                    { visible: false, targets: [ 0 ] } // hide order column.
                ],
                columns:[
                    { data:"history_date" },
                    { data:"history_date" },
                    {
                        data:"history_document_url",
                        mRender:function(data){
                            return `<a href="${data}" target="_blank"><i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                        },
                        orderable: false
                    },
                ]
            },
        }
    },
    watch:{

    },
    computed: {
        dtHeadersApprovalHistory: function() {
            if (this.apiaryTemplateGroup) {
                return  ["order","Date","Licence"]
            } else {
                return  ["order","Date","Approval"]
            }
        },

        is_external: function(){
            return this.level == 'external';
        },
        showApprovalHistory: function(){
            if (this.isModalOpen && !this.processingDetails){
                this.getHistory()
            }
            return this.isModalOpen
        },
        dashboardTitle: function() {
            let title = ''
            if (this.apiaryTemplateGroup) {
                title = 'Licence History';
            } else {
                title = 'Approval History';
            }
            return title;
        },

    },
    methods:{
        cancel: function() {
            this.close();
        },
        close: function() {
            this.processingDetails = false;
            this.isModalOpen = false;
        },
        getHistory: function() {
            this.processingDetails = true;  
            this.$refs.approval_history_table.vmDataTable.clear().draw();
            this.url = this.$refs.approval_history_table.vmDataTable.ajax.url
            this.$refs.approval_history_table.vmDataTable.ajax.reload();
        }
    },
    created: function() {
        // retrieve template group
        fetch('/template_group',{
            emulateJSON:true
        }).then(
            async res=>{
                //this.template_group = res.body.template_group;
                let template_group_res= await res.json();
                if (template_group_res.template_group === 'apiary') {
                    this.apiaryTemplateGroup = true;
                } else {
                    this.dasTemplateGroup = true;
                }
            },err=>{
                console.log(err);
            }
        );
    },

}
</script>
