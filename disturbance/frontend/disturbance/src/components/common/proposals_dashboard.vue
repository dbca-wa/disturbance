<template id="proposal_dashboard">
    <div class="row">
        <template v-if="is_local">
            proposals_dashboard.vue
        </template>
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="row">
                    <div v-if="!apiaryTemplateGroup">
                        <div class="col-md-3">
                            <div class="form-group">
                                <div>
                                    <div v-show="select2Applied">
                                        <label for="">Region</label>
                                        <select style="width:100%" class="form-select input-sm" ref="filterRegion" >
                                            <template v-if="select2Applied">
                                                <option v-for="r in proposal_regions" :value="r" :key="r">{{r}}</option>
                                            </template>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div v-if="!apiaryTemplateGroup">
                        <div class="col-md-3">
                            <div class="form-group">
                                <div>
                                    <div v-show="select2bApplied">
                                        <label for="">District</label>
                                        <select style="width:100%" class="form-select input-sm" ref="filterDistrict" >
                                            <template v-if="select2bApplied">
                                                <option v-for="r in proposal_districts" :value="r" :key="r">{{r}}</option>
                                            </template>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">{{ activityFilterLabel }}</label>
                            <select class="form-select" v-model="filterProposalActivity">
                                <option value="All">All</option>
                                <option v-for="a in proposal_activityTitles" :value="a" :key="a">{{a}}</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Status</label>
                            <select class="form-select" v-model="filterProposalStatus">
                                <option value="All">All</option>
                                <option v-for="s in proposal_status" :value="s.value" :key="s.value">{{s.name}}</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Proponent</label>
                            <select class="form-select" v-model="filterProposalApplicant">
                                    <option value="All">All</option>
                                    <option v-for="s in proposal_applicants" :value="s.id" :key="s.id">{{s.search_term}}</option>
                            </select>
                            </div>
                    </div>
                    <!-- <div v-if="is_external" class="col-md-3">
                        <router-link  style="margin-top:25px;" class="btn btn-primary pull-right" :to="{ name: 'apply_proposal' }">{{newProposalText}}</router-link>
                    </div> -->
                    <div class="col-md-3">
                        <label for="">Lodged From</label>
                        <input
                            id="proposal-lodged-from"
                            type="date"
                            class="form-control"
                            v-model="proposal_lodged_from"
                            placeholder="DD/MM/YYYY"
                            :max="proposal_lodged_to"
                        >
                    </div>
                    <div class="col-md-3">
                        <label for="">Lodged To</label>
                        <input
                            id="proposal-lodged-to"
                            type="date"
                            class="form-control"
                            v-model="proposal_lodged_to"
                            placeholder="DD/MM/YYYY"
                            :min="proposal_lodged_from"
                        >
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Submitter</label>
                            <select class="form-select" v-model="filterProposalSubmitter">
                                <option value="All">All</option>
                                <option v-for="s in proposal_submitters" :value="s.email" :key="s.email">{{s.search_term}}</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="row" v-if="!is_external">
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Proposal Type</label>
                            <select class="form-select" v-model="filterProposalApplicationType">
                                <option value="All">All</option>
                                <option v-for="a in proposal_applicationTypes" :value="a" :key="a">{{a}}</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Sort By</label>
                            <select class="form-select" v-model="sortBy">
                                <option value=""></option>
                                <option v-for="s in sort_by" :key="s.value" :value="s.value">{{s.name}}</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div v-if="datatableReady">
                            <datatable ref="proposal_datatable" :id="datatable_id" :dtOptions="dt_options" :dtHeaders="dt_headers"/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { v4 as uuidv4 } from 'uuid';
import datatable from '@/utils/vue/datatable.vue'
// require("select2/dist/css/select2.min.css");
// require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
import {
    api_endpoints,
    helpers,
    constants,
}from '@/utils/hooks'
export default {
    name: 'ProposalTableDash',
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
        },
    },
    data() {
        // let vm = this;

        return {
            assigned_officer_column_name: "assigned_officer__first_name, assigned_officer__last_name, assigned_officer__email",
            submitter_column_name: "submitter__email, submitter__first_name, submitter__last_name",
            proponent_applicant_column_name: 'applicant__organisation__name, proxy_applicant__first_name, proxy_applicant__last_name, proxy_applicant__email',
            pBody: 'pBody' + uuidv4(),
            uuid: 0,
            datatable_id: 'proposal-datatable-'+uuidv4(),
            //datatable_id: 'proposal-datatable-'+uuidv4(),
            //Profile to check if user has access to process Proposal
            profile: {},
            //template_group: '',
            templateGroupResponse: {},
            apiaryTemplateGroup: false,
            dasTemplateGroup: false,
            templateGroupDetermined: false,
            is_das_admin: false,
            is_apiary_admin: false,
            is_das_apiary_admin: false,
            // Filters for Proposals
            filterListsProposal:{},
            filterProposalRegion: [],
            filterProposalDistrict: [],
            filterProposalActivity: 'All',
            filterProposalApplicationType: 'All',
            filterProposalStatus: 'All',
            //filterProposalLodgedFrom: '',
            proposal_lodged_from: '',
            proposal_lodged_to: '',
            //filterProposalLodgedTo: '',
            filterProposalSubmitter: 'All',
            filterProposalApplicant: 'All',
            dashboardTitle: '',
            dashboardDescription: '',
            newProposalText: '',
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            external_status:[
                {value: 'draft', name: 'Draft'},
                {value: 'with_assessor', name: 'Under Review'},
                {value: 'approved', name: 'Approved'},
                {value: 'declined', name: 'Declined'},
            ],
            internal_status:[
                {value: 'draft', name: 'Draft'},
                {value: 'with_assessor', name: 'With Assessor'},
                {value: 'with_referral', name: 'With Referral'},
                {value: 'with_assessor_requirements', name: 'With Assessor (Requirements)'},
                {value: 'with_approver', name: 'With Approver'},
                {value: 'approved', name: 'Approved'},
                {value: 'declined', name: 'Declined'},
                {value: 'discarded', name: 'Discarded'},
            ],
            proposal_activityTitles : [],
            proposal_applicationTypes : [],
            proposal_regions: [],
            proposal_districts: [],
            proposal_submitters: [],
            proposal_applicants:[],
            proposal_status: [],
            is_local: helpers.is_local(),
            select2Applied: false,
            select2bApplied: false,
            dt_options: {},
            datatableReady: false,
            sort_by:[
                {value: 'applicant__organisation__name', name: 'Proponent - Ascending'},
                {value: '-applicant__organisation__name', name: 'Proponent - Descending'},
                {value: 'processing_status', name: 'Status - Ascending'},
                {value: '-processing_status', name: 'Status - Descending'},
                {value: 'lodgement_date', name: 'Lodged On - Ascending'},
                {value: '-lodgement_date', name: 'Lodged On - Descending'},
                {value: 'assigned_officer__first_name', name: 'Assigned Officer - Ascending'},
                {value: '-assigned_officer__first_name', name: 'Assigned Officer - Descending'},
                {value: 'approval__lodgement_number', name: 'Approval - Ascending'},
                {value: '-approval__lodgement_number', name: 'Approval - Descending'},
            ],
            sortBy: '',
        }
    },
    components:{
        datatable
    },
    watch:{
        templateGroupDetermined: function(){
            console.log('in templateGroupDetermined')
            //this.showHideColumns()
            this.set_dt_options();

        },
        filterProposalRegion: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
            //let vm = this;
            //vm.$refs.proposal_datatable.vmDataTable.columns(1).search(vm.filterProposalRegion.join()).draw();
        },
        filterProposalDistrict: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalActivity: function() {
            let vm = this;
            if (vm.filterProposalActivity!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.column('activity:name').search(vm.filterProposalActivity).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.column('activity:name').search('').draw();
            }
        },
        filterProposalApplicationType: function() {
            // let vm = this;
            // if (vm.filterProposalApplicationType!= 'All') {
            //     vm.$refs.proposal_datatable.vmDataTable.column('activity:name').search(vm.filterProposalApplicationType).draw();
            // } else {
            //     vm.$refs.proposal_datatable.vmDataTable.column('activity:name').search('').draw();
            // }
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalSubmitter: function(){
            //this.$refs.proposal_datatable.vmDataTable.draw();
            let vm = this;
            if (vm.filterProposalSubmitter!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.column(vm.submitter_column_name + ':name').search(vm.filterProposalSubmitter).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.column(vm.submitter_column_name + ':name').search('').draw();
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
        filterProposalApplicant: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        // filterProposalLodgedFrom: function(){
        //     this.$refs.proposal_datatable.vmDataTable.draw();
        // },
        // filterProposalLodgedTo: function(){
        //     this.$refs.proposal_datatable.vmDataTable.draw();
        // },
        dateRangeIdentifierForReloadProposalTable: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        sortBy: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        }
    },
    computed: {
        filterProposalLodgedFrom: {
            get() {
                // If our internal date exists, convert it for submission, etc
                if (this.proposal_lodged_from) {
                    return moment(this.proposal_lodged_from, 'YYYY-MM-DD').format('DD/MM/YYYY');
                }
                return ''; // Otherwise, return an empty string.
            }
        },
        filterProposalLodgedTo : {
            get() {
                // If our internal date exists, convert it for submission, etc
                if (this.proposal_lodged_to) {
                    return moment(this.proposal_lodged_to, 'YYYY-MM-DD').format('DD/MM/YYYY');
                }
                return ''; // Otherwise, return an empty string.
            }
        },
        dateRangeIdentifierForReloadProposalTable() {
            return `${this.proposal_lodged_from}|${this.proposal_lodged_to}`;
        },
        activityFilterLabel: function() {
            let label = ''
            if (this.apiaryTemplateGroup) {
                label = 'Application Type';
            } else {
                label = 'Activity';
            }
            return label;
        },
        dt_headers: function(){
            // Defautl DAS
            let activity_or_application_type = this.dasTemplateGroup ? 'Activity' : 'Application Type';
            let proponent_or_applicant = this.dasTemplateGroup ? 'Proponent' : 'Applicant';
            let columnList = ["Number"];
            if (this.dasTemplateGroup){
                columnList.push("Region");
            }
            if (this.dasTemplateGroup&&(!this.is_external)){
                columnList.push("District");
            }
            columnList.push(activity_or_application_type);
            if (this.dasTemplateGroup){
                columnList.push("Title");
            }
            columnList.push("Submitter",
                    proponent_or_applicant,
                    "Status",
                    "Lodged on");
            if (!this.is_external){
                columnList.push("Assigned Officer");
            }
            if (this.dasTemplateGroup&&(!this.is_external)){
                columnList.push("Approval");
            }
            if (this.apiaryTemplateGroup){
                columnList.push("Invoice");
            }
            columnList.push("Action");
            return columnList;
        },
        tableColumns: function() {
            let vm = this;
            let columnList = [
                {
                    // 1. Number
                    data: "id",
                    'render':function(data,type,full){
                        if (full.migrated){
                            return full.lodgement_number + ' (M)'
                        } else {
                            return full.lodgement_number
                        } 
                    },
                    defaultContent: '',
                    orderable: true,
                    searchable: true,
                },
            ];
            if (this.dasTemplateGroup) {
                columnList.push({
                    // 2. Region
                    data: "region",
                    'render': function (value) {
                        return helpers.dtPopover(value);
                    },
                    defaultContent: '',
                    //visible: false,
                    name: 'region__name',
                    searchable: true,
                });
            };
            if (this.dasTemplateGroup&&(!this.is_external)){
                columnList.push({
                    // 2.5. District
                    data: "district",
                    defaultContent: '',
                    name: 'district__name',
                    searchable: true,
                });
            };

            columnList.push({
                    // 3. Activity/Application Type
                    data: "activity",
                    defaultContent: '',
                    searchable: true,
                    name: 'activity',
                });
            if (this.dasTemplateGroup) {
                columnList.push({
                    // 3.5 Title
                    data: "title",
                    'render': function (value, type) {
                        //return helpers.dtPopover(value);
                        var result= helpers.dtPopover(value);
                        return type=='export' ? value : result;
                    },
                    defaultContent: '',
                    //visible: false,
                    name: 'title',
                    searchable: true,
                });
            };
            columnList.push({
                    // 4. Submitter
                    data: "submitter",
                    mRender:function (data) {
                        if (data) {
                            return `${data.first_name} ${data.last_name}`;
                        }
                        return ''
                    },
                    defaultContent: '',
                    //name: vm.submitter_column_name,
                    name: "submitter__email, submitter__first_name, submitter__last_name",
                    searchable: true,
                },
                {
                    // 5. Proponent/Applicant
                    data: "relevant_applicant_name",
                    defaultContent: '',
                    //name: vm.proponent_applicant_column_name,
                    name: "applicant__organisation__name, proxy_applicant__first_name, proxy_applicant__last_name, proxy_applicant__email",
                    searchable: true,
                },
                {
                    // 6. Status
                    mRender:function (data, type, full) {
                        if (vm.is_external){
                            return full.customer_status
                        }
                        return full.processing_status
                    },
                    defaultContent: '',
                    searchable: false,
                    name: vm.is_external? "customer_status":"processing_status",
                },
                {
                    // 7. Lodged on
                    data: "lodgement_date",
                    mRender:function (data) {
                        return data != '' && data  != null ? moment(data).format(vm.dateFormat): '';
                    },
                    defaultContent: '',
                    searchable: true,
                });
            if (!vm.is_external){
                columnList.push({
                    // 8. Assigned Officer
                    data: "assigned_officer",
                    defaultContent: '',
                    //visible: false,
                    name: "assigned_officer__first_name, assigned_officer__last_name, assigned_officer__email",
                    searchable: true,
                });
            };
            if (this.dasTemplateGroup&&(!vm.is_external)){
                columnList.push({
                    // 8. Assigned Officer
                    data: "approval",
                    defaultContent: '',
                    //visible: false,
                    name: "approval__lodgement_number",
                    searchable: true,
                });
            };
            if (this.apiaryTemplateGroup) {
                columnList.push({
                    // 9. Invoice
                    mRender:function (data, type, full) {
                        //console.log(full)
                        let links = '';
                        //if (full.fee_paid) {
                        //    links +=  `<a href='/payments/invoice-pdf/${full.fee_invoice_reference}.pdf' target='_blank'><i style='color:red;' class='fa fa-file-pdf-o'></i></a> &nbsp`;
                        //    if (!vm.is_external){
                        //        links +=  `<a href='/ledger/payments/invoice/payment?invoice=${full.fee_invoice_reference}' target='_blank'>View Payment</a><br/>`;
                        //    }
                        //}
                        if (full.fee_invoice_references){
                            for (let item of full.fee_invoice_references){
                                links += '<div>'
                                links +=  `<a href='/payments/invoice-pdf/${item}.pdf' target='_blank'><i style='color:red;' class='fa fa-file-pdf-o'></i> #${item}</a>`;
                                if (!vm.is_external){
                                    links +=  `&nbsp;&nbsp;&nbsp;<a href='/ledger/payments/invoice/payment?invoice=${item}' target='_blank'>View Payment</a><br/>`;
                                }
                                links += '</div>'
                            }
                        }
                        return links;
                    },
                    name: 'invoice_column',
                    orderable: false,
                    //visible: false,
                    searchable: false,
                });
            };
            columnList.push({
                    // 10. Action
                    mRender:function (data,type,full) {
                        let links = '';
                        if (!vm.is_external){
                            if(full.assessor_process){
                                links +=  `<a href='/internal/proposal/${full.id}'>Process</a><br/>`;
                            } else {
                                links +=  `<a href='/internal/proposal/${full.id}'>View</a><br/>`;
                            }
                        }
                        else{
                            if (full.can_user_edit) {
                                links +=  `<a href='/external/proposal/${full.id}'>Continue</a><br/>`;
                                links +=  `<a href='#${full.id}' data-discard-proposal='${full.id}'>Discard</a><br/>`;
                            }
                            else if (full.can_user_view) {
                                links +=  `<a href='/external/proposal/${full.id}'>View</a><br/>`;
                            }
                        }
                        return links;
                    },
                    defaultContent: '',
                    name: '',
                    searchable: false,
                    orderable: false,
                    className: "noexport",
                });
            console.log(columnList);
            return columnList;
        },

        is_external: function(){
            return this.level == 'external';
        },
        is_referral: function(){
            return this.level == 'referral';
        },
        /*
        apiaryTemplateGroup: function() {
            let returnVal = false;
            if (this.template_group == 'apiary'){
                returnVal = true
            }
            return returnVal;
        },
        dasTemplateGroup: function() {
            let returnVal = false;
            if (this.template_group == 'das'){
                returnVal = true
            }
            return returnVal;
        },
        */

    },
    methods:{
        set_dt_options: function() {
            this.datatableReady = false;
            let vm = this;
            this.uuid++;
            //$(vm.$refs.proposal_datatable.vmDataTable).DataTable().destroy();
            //$(vm.$refs.proposal_datatable.vmDataTable).DataTable({
            this.dt_options = {
                destroy: true,
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
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
                        d.regions = vm.filterProposalRegion.join();
                        d.districts = vm.filterProposalDistrict.join();
                        // d.date_from = vm.filterProposalLodgedFrom != '' && vm.filterProposalLodgedFrom != null ? moment(vm.filterProposalLodgedFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        // d.date_to = vm.filterProposalLodgedTo != '' && vm.filterProposalLodgedTo != null ? moment(vm.filterProposalLodgedTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.date_from = vm.proposal_lodged_from != '' && vm.proposal_lodged_from != null ? moment(vm.proposal_lodged_from, 'YYYY-MM-DD').format('YYYY-MM-DD'): '';
                        d.date_to = vm.proposal_lodged_to != '' && vm.proposal_lodged_to != null ? moment(vm.proposal_lodged_to, 'YYYY-MM-DD').format('YYYY-MM-DD'): '';
                        d.application_type = vm.filterProposalApplicationType;
                        d.proposal_activity = vm.filterProposalActivity;
                        d.submitter = vm.filterProposalSubmitter;
                        d.proposal_status = vm.filterProposalStatus;
                        d.applicant = vm.filterProposalApplicant;
                        d.sort_by= vm.sortBy;
                    }
                },
                dom: "<'d-flex align-items-center'<'me-auto'l>fB>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'d-flex align-items-center'<'me-auto'i>p>",
                buttons:[
                    {
                        extend: 'excel',
                        className: 'btn btn-primary me-2 rounded',
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
                        className: 'btn btn-primary me-2 rounded',
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
                columns: vm.tableColumns,
                processing: true,
                drawCallback: function () {
                    helpers.enablePopovers();
                },
                initComplete: function () {
                    helpers.enablePopovers();
                },
            };
            //});
            this.datatableReady = true;
            this.$nextTick(() => {
                vm.initialiseSearch();
                vm.addEventListeners();
            });
        },
        /*
        showHideColumns: function(){
            console.log('in showHideColumns')
            let vm = this
            let regionColumn = vm.$refs.proposal_datatable.vmDataTable.column('region__name:name');
            let titleColumn = vm.$refs.proposal_datatable.vmDataTable.column('title:name');
            if (vm.dasTemplateGroup) {
                regionColumn.visible(true);
                titleColumn.visible(true);
            }
            let invoiceColumn = vm.$refs.proposal_datatable.vmDataTable.column('invoice_column:name');
            if ((!vm.is_external && vm.dasTemplateGroup && vm.is_das_apiary_admin) || vm.apiaryTemplateGroup){
                invoiceColumn.visible(true);
            }
            let assignedOfficerColumn = vm.$refs.proposal_datatable.vmDataTable.column(vm.assigned_officer_column_name + ':name')
            if (!vm.is_external){
                assignedOfficerColumn.visible(true)
            }
        },
        */
        setDashboardText: function() {
            if (this.apiaryTemplateGroup) {
                this.dashboardTitle = 'Applications';
                this.dashboardDescription = 'View existing applications and lodge new ones';
                this.newProposalText = 'New Application';
            } else {
                this.dashboardTitle = 'Proposals';
                this.dashboardDescription = 'View existing proposals and lodge new ones';
                this.newProposalText = 'New Proposal';
            }
        },

        fetchFilterLists: function(){
            let vm = this;
            //fetch('/api/list_proposal/filter_list/').then((response) => {
            fetch(
                api_endpoints.filter_list
            ).then( async (response) => {
                if (!response.ok) {
                    return response.json().then(err => { throw err });
                }
                vm.filterListsProposal = await response.json();
                vm.proposal_regions = vm.filterListsProposal.regions;
                vm.proposal_districts = vm.filterListsProposal.districts;

                vm.proposal_activityTitles = vm.filterListsProposal.activities;
                vm.proposal_applicationTypes = vm.filterListsProposal.application_types;
                //vm.proposal_activityTitles.push('Apiary');

                vm.proposal_submitters = vm.filterListsProposal.submitters;
                vm.proposal_applicants = vm.filterListsProposal.applicants;
                //vm.proposal_status = vm.level == 'internal' ? response.body.processing_status_choices: response.body.customer_status_choices;
                vm.proposal_status = vm.level == 'internal' ? vm.internal_status: vm.external_status;
            }).catch(error => {
                console.log(error);
            })
        },

        discardProposal:function (proposal_id) {
            let vm = this;
            swal.fire({
                title: "Discard Proposal",
                text: "Are you sure you want to discard this proposal?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: 'Discard Proposal',
                confirmButtonColor:'#d9534f'
            }).then((swalresult) => {
                if (swalresult.isConfirmed) {
                    fetch(api_endpoints.discard_proposal(proposal_id),{
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                   }).then(async (response) => {
                        if (!response.ok) {
                            throw new Error(`Discard Proposal failed: ${response.status}`);
                        }
                        swal.fire({
                            title: 'Discarded',
                            text: 'Your proposal has been discarded',
                            icon: 'success'
                        })
                        vm.$refs.proposal_datatable.vmDataTable.ajax.reload(
                            helpers.enablePopovers,
                            false
                        );
                    }).catch((error) => {
                        console.log(error);
                    });
                }
            },(error) => {
                console.log(error);
            });
        },
        addEventListeners: function(){
            let vm = this;
            // External Discard listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-discard-proposal]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-discard-proposal');
                vm.discardProposal(id);
            });
            //if (this.dasTemplateGroup) {
            //    this.applySelect2()
            //    // Initialise select2 for region
            //}
        },
        applySelect2: function(){
            let vm = this

            if (!vm.select2Applied){
                $(vm.$refs.filterRegion).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    placeholder:"Select Region",
                    multiple:true,
                }).
                on("select2:select",function (e) {
                    var selected = $(e.currentTarget);
                    vm.filterProposalRegion = selected.val();
                }).
                on("select2:unselect",function (e) {
                    var selected = $(e.currentTarget);
                    vm.filterProposalRegion = selected.val();
                });
                vm.select2Applied = true
                console.log('select2Applied')
            }
        },
        applySelect2b: function(){
            let vm = this

            if (!vm.select2bApplied){
                $(vm.$refs.filterDistrict).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    placeholder:"Select District",
                    multiple:true,
                }).
                on("select2:select",function (e) {
                    var selected = $(e.currentTarget);
                    vm.filterProposalDistrict = selected.val();
                }).
                on("select2:unselect",function (e) {
                    var selected = $(e.currentTarget);
                    vm.filterProposalDistrict = selected.val();
                });
                vm.select2bApplied = true
                console.log('select2bApplied')
            }
        },

        initialiseSearch:function(){
            this.regionSearch();
            this.districtSearch();
            this.submitterSearch();
            this.dateSearch();
        },
        regionSearch:function(){
            let vm = this;
            vm.$refs.proposal_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let found = false;
                    let filtered_regions = vm.filterProposalRegion;
                    if (filtered_regions.length == 0){ return true; }

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
        districtSearch:function(){
            let vm = this;
            vm.$refs.proposal_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let found = false;
                    let filtered_districts = vm.filterProposalDistrict;
                    if (filtered_districts.length == 0){ return true; }

                    let districts = original.district != '' && original.district != null ? original.district.split(','): [];

                    $.each(districts,(i,r) => {
                        if (filtered_districts.indexOf(r) != -1){
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
                    let from = vm.filterProposalLodgedFrom;
                    let to = vm.filterProposalLodgedTo;
                    let val = original.lodgement_date;

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
            fetch(api_endpoints.profile).then(
                async (response) => {
                    if (!response.ok) {
                        return response.json().then(err => { throw err });
                    }
                    vm.profile = await response.json();
                }).catch(error => {
                    console.log(error);

                }
            )
        },

        check_assessor: function(proposal){
            let vm = this;
            if (proposal.assigned_officer)
                {
                    { if(proposal.assigned_officer== vm.profile.full_name)
                        return true;
                    else
                        return false;
                }
            }
            else{
                 var assessor = proposal.allowed_assessors.filter(function(elem){
                    return(elem.id=vm.profile.id)
                });

                if (assessor.length > 0)
                    return true;
                else
                    return false;

            }

        },
    },

    mounted: function(){
        console.log('in mounted')
        this.fetchFilterLists();
        this.fetchProfile();
        $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
        });
        /*
        // retrieve template group
        fetch('/template_group',{
            emulateJSON:true
            }).then(res=>{
                vm.template_group = res.body.template_group;
        },err=>{
        console.log(err);
        });
        */

        this.$nextTick(() => {
            //vm.initialiseSearch();
            //vm.addEventListeners();
        });
    },
    created: function() {
        let vm = this;
        console.log('in created')
        // retrieve template group
        fetch('/template_group',{ emulateJSON: true }).then(
            async res=>{
                if (!res.ok) {
                    return res.json().then(err => { throw err });
                }
                //this.template_group = res.body.template_group;
                vm.templateGroupResponse = await res.json();
                if (vm.templateGroupResponse.template_group === 'apiary') {
                    this.apiaryTemplateGroup = true;
                } else {
                    this.dasTemplateGroup = true;
                    this.applySelect2()
                    this.applySelect2b()
                }
                this.templateGroupDetermined = true;
                this.setDashboardText();
                this.is_das_admin = vm.templateGroupResponse.is_das_admin
                this.is_apiary_admin = vm.templateGroupResponse.is_apiary_admin
                this.is_das_apiary_admin = vm.templateGroupResponse.is_das_apiary_admin
            }).catch(err=>{
                console.log(err);
            });
    },
}
</script>
<style scoped>
.dt-buttons{
    float: right;
}
</style>
