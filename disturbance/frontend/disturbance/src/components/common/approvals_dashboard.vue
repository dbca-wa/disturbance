<template id="proposal_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">{{dashboardTitle}} <small v-if="is_external">{{dashboardDescription}}</small>
                        <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <div class="row">
                        <div v-if="templateGroupDetermined && !apiaryTemplateGroup">
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label for="">Region</label>
                                    <select class="form-control" v-model="filterProposalRegion">
                                        <option value="All">All</option>
                                        <option v-for="r in proposal_regions" :value="r">{{r}}</option>
                                    </select>
                                    <!--
                                    <select style="width:100%" class="form-control input-sm" multiple ref="filterRegion" >
                                        <option v-for="r in proposal_regions" :value="r">{{r}}</option>
                                    </select>
                                    -->
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label for="">Activity</label>
                                    <select class="form-control" v-model="filterProposalActivity">
                                        <option value="All">All</option>
                                        <option v-for="a in proposal_activityTitles" :value="a">{{a}}</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!--div class="col-md-3">
                            <div class="form-group">
                                <label for="">Region</label>
                                <select class="form-control" v-model="filterProposalRegion">
                                    <option value="All">All</option>
                                    <option v-for="r in proposal_regions" :value="r">{{r}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Activity</label>
                                <select class="form-control" v-model="filterProposalActivity">
                                    <option value="All">All</option>
                                    <option v-for="a in proposal_activityTitles" :value="a">{{a}}</option>
                                </select>
                            </div>
                        </div-->
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterProposalStatus">
                                    <option value="All">All</option>
                                    <option v-for="s in approval_status" :value="s">{{s}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Start From</label>
                            <div class="input-group date" ref="proposalStartDateFromPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalStartFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Start To</label>
                            <div class="input-group date" ref="proposalStartDateToPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalStartTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Expiry From</label>
                            <div class="input-group date" ref="proposalExpiryDateFromPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalExpiryFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Expiry To</label>
                            <div class="input-group date" ref="proposalExpiryDateToPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalExpiryTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-12" style="margin-top:25px;">
                            <div v-if="datatableReady">
                                <datatable ref="proposal_datatable" :id="datatable_id" :dtOptions="proposal_options" :dtHeaders="proposal_headers"/>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <ApprovalCancellation ref="approval_cancellation"  @refreshFromResponse="refreshFromResponse"></ApprovalCancellation>
        <ApprovalSuspension ref="approval_suspension"  @refreshFromResponse="refreshFromResponse"></ApprovalSuspension>
        <ApprovalSurrender ref="approval_surrender"  @refreshFromResponse="refreshFromResponse"></ApprovalSurrender>
        <ApprovalHistory ref="approval_history" />

    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue'
import Vue from 'vue'
import ApprovalCancellation from '../internal/approvals/approval_cancellation.vue'
import ApprovalSuspension from '../internal/approvals/approval_suspension.vue'
import ApprovalSurrender from '../internal/approvals/approval_surrender.vue'
import ApprovalHistory from './approval_history_modal.vue';
import {
    api_endpoints,
    helpers
}from '@/utils/hooks'
export default {
    name: 'ApprovalsTableDash',
    props: {
        level:{
            type: String,
            required: true,
            validator:function(val) {
                let options = ['internal','referral','external'];
                return options.indexOf(val) != -1 ? true: false;
            }
        },
        url:{
            type: String,
            required: true
        }
    },
    data() {
        let vm = this;
        return {
            pBody: 'pBody' + vm._uid,
            datatable_id: 'approvals-datatable-'+vm._uid,
            uuid: 0,
            //datatable_id: 'proposal-datatable-'+vm.uuid,
            //Profile to check if user has access to process Proposal
            profile: {},
            approval_history: {
                isModalOpen: false,
                approval_history_id: null,
            },
            // Filters for Proposals
            filterProposalRegion: 'All',
            filterProposalActivity: 'All',
            filterProposalStatus: 'All',
            filterProposalStartFrom: '',
            filterProposalStartTo: '',
            filterProposalExpiryFrom: '',
            filterProposalExpiryTo: '',
            filterProposalSubmitter: 'All',
            dashboardTitle: '',
            dashboardDescription: '',
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            approval_status:[],
            proposal_activityTitles : [],
            proposal_regions: [],
            proposal_submitters: [],
            //template_group: '',
            dasTemplateGroup: false,
            apiaryTemplateGroup: false,
            templateGroupDetermined: false,
            select2Applied: false,
            proposal_options: {},
            datatableReady: false,
        }
    },
    components:{
        datatable,
        ApprovalCancellation,
        ApprovalSuspension,
        ApprovalSurrender,
        ApprovalHistory
    },
    watch:{
        templateGroupDetermined: function(){
            //this.showHideColumns()
            this.set_proposal_options();
        },
        filterProposalRegion: function(){
            //this.$refs.proposal_datatable.vmDataTable.draw();
            let vm = this;
            if (vm.filterProposalRegion!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.column('current_proposal__region__name:name').search(vm.filterProposalRegion).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.column('current_proposal__region__name:name').search('').draw();
            }
        },
        filterProposalActivity: function() {
            let vm = this;
            if (vm.filterProposalActivity!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.column('current_proposal__activity:name').search(vm.filterProposalActivity).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.column('current_proposal__activity:name').search('').draw();
            }
        },
        filterProposalSubmitter: function(){
            //this.$refs.proposal_datatable.vmDataTable.draw();
            let vm = this;
            if (vm.filterProposalSubmitter!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.columns(4).search(vm.filterProposalSubmitter).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.columns(4).search('').draw();
            }
        },
        filterProposalStatus: function() {
            let vm = this;
            if (vm.filterProposalStatus!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.column('status:name').search(vm.filterProposalStatus).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.column('status:name').search('').draw();
            }
        },
        filterProposalStartFrom: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalStartTo: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalExpiryFrom: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalExpiryTo: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        }
    },
    computed: {
        status: function(){
            //return this.is_external ? this.external_status : this.internal_status;
            return [];
        },
        is_external: function(){
            return this.level == 'external';
        },
        is_referral: function(){
            return this.level == 'referral';
        },
        proposal_headers: function() {
            let approval_or_licence = this.dasTemplateGroup ? 'Approval' : 'Licence';
            let columnHeaders = ["Number",];
            if (this.dasTemplateGroup) {
                columnHeaders.push("Region",
                "Activity",
                "Title",);
                if(!this.is_external){
                    columnHeaders.push("Associated Proposals");
                }
            }
            columnHeaders.push("Holder",
                "Status",
                "Start Date",
                "Expiry Date",
                approval_or_licence,
                "Action");
                /*
                "Action", 
                "");
                */
            return columnHeaders;
        },
        tableColumns: function() {
            let vm = this;
            let columnList = [
                {
                    data: "id",
                    'render':function(data,type,full){
                    if(!vm.is_external){
                        var result = '';
                        var popTemplate = '';
                        var message = '';
                        let tick = '';
                        tick = "<i class='fa fa-exclamation-triangle' style='color:red'></i>"
                        result = '<span>' + full.lodgement_number + '</span>';
                        if (full.migrated){
                            result = '<span>' + full.lodgement_number + ' (M)</span>';
                        } else {
                            result = '<span>' + full.lodgement_number + '</span>';
                        }

                        if(full.can_reissue){
                            if(!full.can_action){
                                if(full.set_to_cancel){
                                    message = 'This Approval is marked for cancellation to future date';
                                }
                                if(full.set_to_suspend){
                                    message = 'This Approval is marked for suspension to future date';
                                }
                                if(full.set_to_surrender){
                                    message = 'This Approval is marked for surrendering to future date';
                                }
                                popTemplate = _.template('<a href="#" ' +
                                        'role="button" ' +
                                        'data-toggle="popover" ' +
                                        'data-trigger="hover" ' +
                                        'data-placement="top auto"' +
                                        'data-html="true" ' +
                                        'data-content="<%= text %>" ' +
                                        '><%= tick %></a>');
                                result += popTemplate({
                                    text: message,
                                    tick: tick
                                });

                            }
                        }
                        return result;
                    }
                    else { 
                        if (full.migrated){
                            return full.lodgement_number + ' (M)'
                        } else {
                            return full.lodgement_number
                        }
                    }
                    },
                    'createdCell': helpers.dtPopoverCellFn,
                    name: "id, lodgement_number",
                    searchable: true,
                }];
            if (this.dasTemplateGroup) {
                columnList.push({
                    data: "region",
                    'render': function (value) {
                        return helpers.dtPopover(value);
                    },
                    'createdCell': helpers.dtPopoverCellFn,
                    name: 'current_proposal__region__name',
                    //visible: false,
                    searchable: true,
                },
                {
                    data: "activity",
                    name: "current_proposal__activity",
                    //visible: false,
                    searchable: true,
                },
                {
                    data: "title",
                    'render': function (value) {
                        return helpers.dtPopover(value);
                    },
                    'createdCell': helpers.dtPopoverCellFn,
                    name: "current_proposal__title",
                    //visible: false,
                    searchable: true,
                });
                if (!this.is_external){
                    columnList.push(
                    {
                        data: "associated_proposals",
                        //name: "current_proposal__activity",
                        //visible: false,
                        searchable: false,
                    });
                }
                
            };
            columnList.push({
                    data: "applicant",
                    name: "applicant__organisation__name, proxy_applicant__first_name, proxy_applicant__last_name, proxy_applicant__email",
                    searchable: true,
                },
                {
                    data: "status",
                    name: 'status',
                },
                {
                    data: "start_date",
                    mRender:function (data,type,full) {
                        return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                    },
                    searchable: false
                },
                {
                    data: "expiry_date",
                    mRender:function (data,type,full) {
                        return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                    },
                    searchable: true
                },
                {
                    data: "licence_document",
                    mRender:function(data,type,full){
                        //let link='';
                        //return `<a href="${data}" target="_blank"><i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                        // link=`<a href='#${full.id}'<i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                        if (full.apiary_approval) {
                            return `<a href="${full.latest_apiary_licence_document}" target="_blank"><i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                        } else {
                            if(vm.is_external){
                                return `<a href="${data}" target="_blank"><i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                            }
                            else{
                                return `<a href="#${full.id}" data-pdf-approval='${full.id}' media-link='${data}'><i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                            }
                        }
                        //return link;
                    },
                    name: 'licence_document__name',
                    searchable: false,
                    //visible: false,
                    className: "noexport",
                },
                {
                    data: '',
                    mRender:function (data,type,full) {
                        let links = '';
                        if (!vm.is_external){
                            //if(full.can_approver_reissue && full.current_proposal && full.current_proposal.application_type !== 'Site Transfer'){
                            if(full.can_approver_reissue && full.current_proposal){
                                    links +=  `<a href='#${full.id}' data-reissue-approval='${full.current_proposal_id}'>Reissue</a><br/>`;
                            }
                            if(vm.check_assessor(full)){
                                // if(full.can_approver_reissue){
                                //     links +=  `<a href='#${full.id}' data-reissue-approval='${full.current_proposal}'>Reissue</a><br/>`;
                                // }
                                if(full.can_reissue && full.can_action){
                                    links +=  `<a href='#${full.id}' data-cancel-approval='${full.id}'>Cancel</a><br/>`;
                                    links +=  `<a href='#${full.id}' data-surrender-approval='${full.id}'>Surrender</a><br/>`;
                                }
                                if(full.status == 'Current' && full.can_action){
                                    links +=  `<a href='#${full.id}' data-suspend-approval='${full.id}'>Suspend</a><br/>`;
                                }
                                if(full.can_reinstate)
                                {
                                    links +=  `<a href='#${full.id}' data-reinstate-approval='${full.id}'>Reinstate</a><br/>`;
                                }
                                links +=  `<a href='/internal/approval/${full.id}'>View</a><br/>`;
                            }
                            else{
                                links +=  `<a href='/internal/approval/${full.id}'>View</a><br/>`;

                            }
                            if(full.renewal_document && full.renewal_sent){
                              links +=  `<a href='${full.renewal_document}' target='_blank'>Renewal Notice</a><br/>`;

                            }
                            // if(full.can_approver_reissue){
                            //         links +=  `<a href='#${full.id}' data-reissue-approval='${full.current_proposal}'>Reissue</a><br/>`;
                            // }
                        }
                        else{
                            if (full.can_reissue) {
                                links +=  `<a href='/external/approval/${full.id}'>View</a><br/>`;
                                if(full.can_action){
                                    links +=  `<a href='#${full.id}' data-surrender-approval='${full.id}'>Surrender</a><br/>`;
                                    if(full.can_amend){
                                       links +=  `<a href='#${full.id}' data-amend-approval='${full.current_proposal_id}'>Amend</a><br/>`;
                                   }
                                }
                                if(full.renewal_document && full.renewal_sent && full.can_renew) {
                                    links +=  `<a href='#${full.id}' data-renew-approval='${full.current_proposal_id}'>Renew</a><br/>`;
                                }
                            }
                            else {
                                links +=  `<a href='/external/approval/${full.id}'>View</a><br/>`;

                            }
                        }
                        if (full.apiary_approval) {
                            links +=  `<a href='#${full.id}' approval-history='${full.id}'>Licence History</a><br/>`;
                        } else {
                            links +=  `<a href='#${full.id}' approval-history='${full.id}'>Approval History</a><br/>`;
                        }
                        return links;
                    },
                    searchable: false,
                    orderable: false,
                    name: '',
                    className: "noexport",
                },
                {
                    data: 'template_group',
                    searchable: false,
                    orderable: false,
                    visible: false,
                    className: "noexport",
                }
                );
            return columnList;
        }
    },
    methods:{
        set_proposal_options: function() {
            this.datatableReady = false;
            let vm = this;
            this.uuid++;
            //$(vm.$refs.proposal_datatable.vmDataTable).DataTable().destroy();
            //$(vm.$refs.proposal_datatable.vmDataTable).DataTable({
            this.proposal_options = {
                destroy: true,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                serverSide: true,
                lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                order: [
                    [0, 'desc']
                    ],
                ajax: {
                    "url": vm.url,
                    "dataSrc": 'data',
                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        //d.regions = vm.filterProposalRegion.join(); // no need to add this since we can filter normally (filter is not multi-select in Approval table)
                        d.start_date_from = vm.filterProposalStartFrom != '' && vm.filterProposalStartFrom != null ? moment(vm.filterProposalStartFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.start_date_to = vm.filterProposalStartTo != '' && vm.filterProposalStartTo != null ? moment(vm.filterProposalStartTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.expiry_date_from = vm.filterProposalExpiryFrom != '' && vm.filterProposalExpiryFrom != null ? moment(vm.filterProposalExpiryFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.expiry_date_to = vm.filterProposalExpiryTo != '' && vm.filterProposalExpiryTo != null ? moment(vm.filterProposalExpiryTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.region = vm.filterProposalRegion;
                        d.proposal_activity = vm.filterProposalActivity;
                        d.approval_status = vm.filterProposalStatus;
                    }
                },
                dom: 'lBfrtip',
                buttons:[
                    {
                        extend: 'excel',
                        exportOptions: {
                            //columns: ':not(:last-child)'
                            columns: ':not(.noexport)'
                        }
                    },
                    {
                        extend: 'csv',
                        exportOptions: {
                            //columns: ':not(:last-child)'
                            columns: ':not(.noexport)'
                        }
                    },
                ],
                columns: vm.tableColumns,
                processing: true,
                initComplete: function() {
                    //vm.showHideColumns()
                },
            };
            this.datatableReady = true;
            this.$nextTick(() => {
                this.initialiseSearch();
                this.addEventListeners();
            });
        },
        /*
        showHideColumns: function(){
            let vm = this
            // set column visibility and headers according to template group
            let regionColumn = vm.$refs.proposal_datatable.vmDataTable.column('current_proposal__region__name:name');
            let activityColumn = vm.$refs.proposal_datatable.vmDataTable.column('current_proposal__activity:name');
            let titleColumn = vm.$refs.proposal_datatable.vmDataTable.column('current_proposal__title:name');
            let approvalColumn = vm.$refs.proposal_datatable.vmDataTable.column('licence_document__name:name');
            if (vm.dasTemplateGroup) {
                regionColumn.visible(true);
                activityColumn.visible(true);
                titleColumn.visible(true)
                approvalColumn.visible(true)
            } else {
                approvalColumn.visible(true)
            }
        },
        */
        setDashboardText: function() {
            //let title = ''
            if (this.apiaryTemplateGroup) {
                this.dashboardTitle = 'Licences';
                this.dashboardDescription = 'View existing licences and amend or renew them';
            } else {
                this.dashboardTitle = 'Approvals';
                this.dashboardDescription = 'View existing approvals and amend or renew them';
            }
            //return title;
        },

        fetchFilterLists: function(){
            let vm = this;

            vm.$http.get(api_endpoints.filter_list_approvals).then((response) => {
                vm.proposal_regions = response.body.regions;
                vm.proposal_activityTitles = response.body.activities;
                vm.proposal_submitters = response.body.submitters;
                vm.approval_status = response.body.approval_status_choices;
            },(error) => {
                console.log(error);
            })
            //console.log(vm.regions);
        },

        addEventListeners: function(){
            let vm = this;
            // Initialise Proposal Date Filters
            $(vm.$refs.proposalStartDateToPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.proposalStartDateToPicker).on('dp.change', function(e){
                if ($(vm.$refs.proposalStartDateToPicker).data('DateTimePicker').date()) {
                    vm.filterProposalStartTo =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.proposalStartDateToPicker).data('date') === "") {
                    vm.filterProposaStartTo = "";
                }
             });
            $(vm.$refs.proposalStartDateFromPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.proposalStartDateFromPicker).on('dp.change',function (e) {
                if ($(vm.$refs.proposalStartDateFromPicker).data('DateTimePicker').date()) {
                    vm.filterProposalStartFrom = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.proposalStartDateToPicker).data("DateTimePicker").minDate(e.date);
                }
                else if ($(vm.$refs.proposalStartDateFromPicker).data('date') === "") {
                    vm.filterProposalStartFrom = "";
                }
            });
            $(vm.$refs.proposalExpiryDateToPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.proposalExpiryDateToPicker).on('dp.change', function(e){
                if ($(vm.$refs.proposalExpiryDateToPicker).data('DateTimePicker').date()) {
                    vm.filterProposalExpiryTo =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.proposalExpiryDateToPicker).data('date') === "") {
                    vm.filterProposaExpiryTo = "";
                }
             });
            $(vm.$refs.proposalExpiryDateFromPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.proposalExpiryDateFromPicker).on('dp.change',function (e) {
                if ($(vm.$refs.proposalExpiryDateFromPicker).data('DateTimePicker').date()) {
                    vm.filterProposalExpiryFrom = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.proposalExpiryDateToPicker).data("DateTimePicker").minDate(e.date);
                }
                else if ($(vm.$refs.proposalExpiryDateFromPicker).data('date') === "") {
                    vm.filterProposalExpiryFrom = "";
                }
            });

            // End Proposal Date Filters
            // Internal Reissue listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-reissue-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-reissue-approval');
                vm.reissueApproval(id);
            });

            //Internal Cancel listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-cancel-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-cancel-approval');
                vm.cancelApproval(id);
            });

            //Internal Suspend listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-suspend-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-suspend-approval');
                vm.suspendApproval(id);
            });

            // Internal Reinstate listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-reinstate-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-reinstate-approval');
                vm.reinstateApproval(id);
            });

            //Internal/ External Surrender listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-surrender-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-surrender-approval');
                vm.surrenderApproval(id);
            });

            // External renewal listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-renew-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-renew-approval');
                vm.renewApproval(id);
            });

            // External amend listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-amend-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-amend-approval');
                vm.amendApproval(id);
            });

            // Internal view pdf listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-pdf-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-pdf-approval');
                var media_link = $(this).attr('media-link');
                vm.viewApprovalPDF(id, media_link);
            });
            // Create Licence History Listener.
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[approval-history]', function(e) {
                e.preventDefault();
                let approval_id = $(this).attr('approval-history');
                vm.$refs.approval_history.approval_history_id = approval_id;
                vm.$refs.approval_history.isModalOpen = true;
            });

        },
        initialiseSearch:function(){
            this.regionSearch();
            this.dateSearch();
        },
        regionSearch:function(){
            let vm = this;
            vm.$refs.proposal_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let found = false;
                    let filtered_regions = vm.filterProposalRegion.split(',');
                    if (filtered_regions == 'All'){ return true; }

                    let regions = original.region != '' && original.region != null ? original.region.split(','): [];

                    $.each(regions,(i,r) => {
                        if (filtered_regions.indexOf(r) != -1){
                            found = true;
                            return false;
                        }
                    });
                    if  (found) { return true; }

                    return false;
                }
            );
        },
        submitterSearch:function(){
            let vm = this;
            vm.$refs.proposal_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let filtered_submitter = vm.filterProposalSubmitter;
                    if (filtered_submitter == 'All'){ return true; }
                    return filtered_submitter == original.submitter.email;
                }
            );
        },
        dateSearch:function(){
            let vm = this;
            vm.$refs.proposal_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let from = vm.filterProposalExpiryFrom;
                    let to = vm.filterProposalExpiryTo;
                    let val = original.expiry_date;

                    if ( from == '' && to == ''){
                        return true;
                    }
                    else if (from != '' && to != ''){
                        return val != null && val != '' ? moment().range(moment(from,vm.dateFormat),moment(to,vm.dateFormat)).contains(moment(val)) :false;
                    }
                    else if(from == '' && to != ''){
                        if (val != null && val != ''){
                            return moment(to,vm.dateFormat).diff(moment(val)) >= 0 ? true : false;
                        }
                        else{
                            return false;
                        }
                    }
                    else if (to == '' && from != ''){
                        if (val != null && val != ''){
                            return moment(val).diff(moment(from,vm.dateFormat)) >= 0 ? true : false;
                        }
                        else{
                            return false;
                        }
                    }
                    else{
                        return false;
                    }
                }
            );
        },

        fetchProfile: function(){
            let vm = this;
            Vue.http.get(api_endpoints.profile).then((response) => {
                vm.profile = response.body

            },(error) => {
                console.log(error);

            })
        },

        check_assessor: function(proposal){
            let vm = this;
            //console.log(proposal.id, proposal.can_approver_reissue);
            var assessor = proposal.allowed_assessors.filter(function(elem){
                    return(elem.id==vm.profile.id)

                });

            if (assessor.length > 0){
                //console.log(proposal.id, assessor)
                return true;
            }
            else
                return false;

            return false;
        },

        reissueApproval:function (proposal_id) {
            let vm = this;
            let status= 'with_approver'
            let data = {'status': status}
            swal({
                title: "Reissue Approval",
                text: "Are you sure you want to reissue this approval?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Reissue approval',
                //confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,(proposal_id+'/reissue_approval')),JSON.stringify(data),{
                emulateJSON:true,
                })
                .then((response) => {

                    vm.$router.push({
                    name:"internal-proposal",
                    params:{proposal_id:proposal_id}
                    });
                }, (error) => {
                    console.log(error);
                    swal({
                    title: "Reissue Approval",
                    text: error.body,
                    type: "error",
                    })
                });
            },(error) => {

            });
        },

        reinstateApproval:function (approval_id) {
            let vm = this;
            let status= 'with_approver'
            //let data = {'status': status}
            swal({
                title: "Reinstate Approval",
                text: "Are you sure you want to reinstate this approval?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Reinstate approval',
                //confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.approvals,(approval_id+'/approval_reinstate')),{

                })
                .then((response) => {
                    swal(
                        'Reinstate',
                        'Your approval has been reinstated',
                        'success'
                    )
                    vm.$refs.proposal_datatable.vmDataTable.ajax.reload();

                }, (error) => {
                    console.log(error);
                    swal({
                    title: "Reinstate Approval",
                    text: error.body,
                    type: "error",
                    })
                });
            },(error) => {

            });
        },

        renewApproval:function (proposal_id) {
            let vm = this;
            let status= 'with_approver'
            //let data = {'status': status}
            swal({
                title: "Renew Approval",
                text: "Are you sure you want to renew this approval?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Renew approval',
                //confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.get(helpers.add_endpoint_json(api_endpoints.proposals,(proposal_id+'/renew_approval')),{

                })
                .then((response) => {
                   let proposal = {}
                   proposal = response.body
                   vm.$router.push({
                    name:"draft_proposal",
                    params:{proposal_id: proposal.id}
                   });

                }, (error) => {
                    console.log(error);
                    swal({
                    title: "Renew Approval",
                    text: error.body,
                    type: "error",
                    })
                });
            },(error) => {

            });
        },

        amendApproval:function (proposal_id) {
            let vm = this;
            swal({
                title: "Amend Approval",
                text: "Are you sure you want to amend this approval?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Amend approval',
                //confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.get(helpers.add_endpoint_json(api_endpoints.proposals,(proposal_id+'/amend_approval')),{

                })
                .then((response) => {
                   let proposal = {}
                   proposal = response.body
                   vm.$router.push({
                    name:"draft_proposal",
                    params:{proposal_id: proposal.id}
                   });

                }, (error) => {
                    console.log(error);
                    swal({
                    title: "Amend Approval",
                    text: error.body,
                    type: "error",
                    })

                });
            },(error) => {

            });
        },

        cancelApproval: function(approval_id){

            this.$refs.approval_cancellation.approval_id = approval_id;
            this.$refs.approval_cancellation.isModalOpen = true;
        },

        suspendApproval: function(approval_id){
            this.$refs.approval_suspension.approval = {};
            this.$refs.approval_suspension.approval_id = approval_id;
            this.$refs.approval_suspension.isModalOpen = true;
        },

        surrenderApproval: function(approval_id){

            this.$refs.approval_surrender.approval_id = approval_id;
            this.$refs.approval_surrender.isModalOpen = true;
        },

        refreshFromResponse: function(){
            this.$refs.proposal_datatable.vmDataTable.ajax.reload();
        },

        viewApprovalPDF: function(id,media_link){
            let vm=this;
            //console.log(approval);
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.approvals,(id+'/approval_pdf_view_log')),{
                })
                .then((response) => {
                    //console.log(response)
                }, (error) => {
                    console.log(error);
                });
            window.open(media_link, '_blank');
        },
        applySelect2: function(){
            console.log('in applySelect2')
            let vm = this

            if (!vm.select2Applied){
                console.log('select2 is being applied')
                $(vm.$refs.filterRegion).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    placeholder:"Select Region"
                }).
                on("select2:select",function (e) {
                    var selected = $(e.currentTarget);
                    vm.filterProposalRegion = selected.val();
                }).
                on("select2:unselect",function (e) {
                    var selected = $(e.currentTarget);
                    vm.filterProposalRegion = selected.val();
                });
            }
            vm.select2Applied = true
        },

    },
    mounted: function(){
		this.fetchFilterLists();
        this.fetchProfile();
        let vm = this;
        $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
        });
        /*
        this.$nextTick(() => {
            this.initialiseSearch();
            this.addEventListeners();
        });
        */
    },
    created: function() {
        // retrieve template group
        this.$http.get('/template_group',{
            emulateJSON:true
            }).then(res=>{
                //this.template_group = res.body.template_group;
                if (res.body.template_group === 'apiary') {
                    this.apiaryTemplateGroup = true;
                } else {
                    this.dasTemplateGroup = true;
                }
                this.setDashboardText();
                this.templateGroupDetermined = true;
        },err=>{
        console.log(err);
        });
    },
}
</script>
<style scoped>
</style>
