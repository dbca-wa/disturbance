<template lang="html">
    <div id="historyDetail">

        <modal transition="modal fade" :title="dashboardTitle" :showOK='false' :showCancel="false" large force>
            <div class="container-fluid">

                <form class="form-horizontal" name="approvalHistoryForm">

                    <div class="col-sm-12" v-if="approval_id">

                        <datatable ref="approval_history_table" 
                            :id="datatable_id" 
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
import { v4 as uuid } from 'uuid';
// import alert from '@vue-utils/alert.vue';
import {
    api_endpoints,
    helpers,
    constants
}from '@/utils/hooks'
export default {
    name: 'ApprovalHistoryModal',
    props: {
        approval_id: {
            type: Number,
            required: true,
        },
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
            approval_history_id: null,
            datatable_id: 'history-datatable-' + uuid(),
        }
    },
    watch:{
        isModalOpen() {
            if (this.isModalOpen) {
                this.$refs.approval_history_table.vmDataTable.ajax.reload();
            }
        },
    },
    computed: {
        dtHeadersApprovalHistory: function() {
                return  ["order","Date","Approval"]
        },

        is_external: function(){
            return this.level == 'external';
        },
        dashboardTitle: function() {
            let title = ''
            title = 'Approval History';
            return title;
        },
        dtOptionsApprovalHistory: function () {
            //let vm = this;
            let columns = [
                    { data:"history_date" },
                    { data:"history_date" },
                    {
                        data:"history_document_url",
                        mRender:function(data){
                            return `<a href="${data}" target="_blank"><i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                        },
                        orderable: false
                    },
                ];
            return {
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                searching: true,
                ordering: true,
                order: [[0, 'asc']],
                serverSide: true,
                ajax: {
                    url:
                        api_endpoints.lookup_history_approvals(this.approval_id) +
                        '?format=datatables',
                    dataSrc: 'data',
                    data: function (d) {
                        d.approval_id = this.approval_id;
                    },
                },
                buttons: [],
                dom:
                    "<'d-flex align-items-center'<'me-auto'l>fB>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'d-flex align-items-center'<'me-auto'i>p>",
                columns: columns,
                processing: true,
            };
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
    },
    created: function() {
        
    },

}
</script>
