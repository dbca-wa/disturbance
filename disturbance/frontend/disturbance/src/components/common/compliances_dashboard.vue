<template id="proposal_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Compliance with requirements <small v-if="is_external">View submitted compliances and submit new ones</small>
                        <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>

                <div class="panel-body collapse in" :id="pBody">
                    <div class="row">
                        <div v-show="!apiaryTemplateGroup && select2Applied">
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label for="">Region</label>
                                    <select style="width:100%" class="form-control input-sm" ref="filterRegion" >
                                        <template v-if="select2Applied">
                                            <option v-for="r in proposal_regions" :value="r">{{r}}</option>
                                        </template>
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
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterComplianceStatus">
                                    <option value="All">All</option>
                                    <option v-for="s in status_values" :value="s">{{s}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <!--<div class="row">
                        <div class="col-md-3">
                            <label for="">Start date From</label>
                            <div class="input-group date" ref="complianceStartDateFromPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterComplianceStartFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Start date To</label>
                            <div class="input-group date" ref="complianceStartDateToPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterComplianceStartTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>-->
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Due date From</label>
                            <div class="input-group date" ref="complianceDueDateFromPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterComplianceDueFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Due date To</label>
                            <div class="input-group date" ref="complianceDueDateToPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterComplianceDueTo">
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
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue'
import Vue from 'vue'
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
import {
    api_endpoints,
    helpers
}from '@/utils/hooks'
export default {
    name: 'CompliancesTableDash',
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
            uuid: 0,
            datatable_id: 'compliances-datatable-'+vm._uid,
            //Profile to check if user has access to process Proposal
            profile: {},
            dasTemplateGroup: false,
            apiaryTemplateGroup: false,
            templateGroupDetermined: false,
            datatableReady: false,
            // Filters for Proposals
            filterProposalRegion: [],
            filterProposalActivity: 'All',
            filterComplianceStatus: 'All',
            filterComplianceStartFrom: '',
            filterComplianceStartTo: '',
            filterComplianceDueFrom: '',
            filterComplianceDueTo: '',
            filterProposalSubmitter: 'All',
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            select2Applied: false,
            /*
            external_status:[
                'Due',
                'Future',
                'Under Review',
                'Approved',
            ],
            internal_status:[
                'Due',
                'Future',
                'With Assessor',
                'Approved',

            ],
            */
            proposal_activityTitles : [],
            proposal_regions: [],
            proposal_submitters: [],
            //proposal_headers:["Number","Region/District","Activity","Title","Approval","Holder","Status","Due Date","Assigned To", "CustomerStatus", "Reference","Action"],
            proposal_options: {},
        }
    },
    components:{
        datatable
    },
    watch:{
        templateGroupDetermined: function(){
            //this.showHideColumns()
            this.set_proposal_options();
        },
        filterProposalRegion: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        //filterProposalRegion: function() {
        //    //this.$refs.proposal_datatable.vmDataTable.draw();
        //    let vm = this;
        //    if (vm.filterProposalRegion!= 'All') {
        //        vm.$refs.proposal_datatable.vmDataTable.column('proposal__region__name:name').search(vm.filterProposalRegion).draw();
        //    } else {
        //        vm.$refs.proposal_datatable.vmDataTable.column('proposal__region__name:name').search('').draw();
        //    }
        //},
        filterProposalActivity: function() {
            let vm = this;
            if (vm.filterProposalActivity!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.column('proposal__activity:name').search(vm.filterProposalActivity).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.column('proposal__activity:name').search('').draw();
            }
        },
        filterComplianceStatus: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalSubmitter: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterComplianceStartFrom: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterComplianceStartTo: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterComplianceDueFrom: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterComplianceDueTo: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        }
    },
    computed: {
        /* status: function(){
            return this.is_external ? this.external_status : this.internal_status;
            //return [];
        }, */
        is_external: function(){
            return this.level == 'external';
        },
        status_values: function() {
            let under_review_or_with_assessor = 'With Assessor'
            if (this.is_external) {
                under_review_or_with_assessor = 'Under Review'
            }
            return [
                'Due',
                'Future',
                under_review_or_with_assessor,
                'Approved',
            ]
        },
        proposal_headers: function() {
            let approval_or_licence = this.dasTemplateGroup ? 'Approval' : 'Licence';
            let holder_or_organisation = this.dasTemplateGroup ? 'Organisation' : 'Holder';
            let columnHeaders = [
                "Number"]
            if (this.dasTemplateGroup) {
                columnHeaders.push("Region")
            };
            columnHeaders.push("Activity");
            if (this.dasTemplateGroup) {
                columnHeaders.push("Title");
            };
            if (this.dasTemplateGroup) {
                columnHeaders.push("Requirement");
            };
            if (this.dasTemplateGroup) {
                columnHeaders.push("Proposal");
            };
            columnHeaders.push(
                "Due Date",
                "District",
                holder_or_organisation,
                approval_or_licence,
                "Status",
                );
            if (!this.is_external) {
                columnHeaders.push("Assigned To");
            }
            columnHeaders.push("Action");
            return columnHeaders;
        },
        tableColumns: function() {
            let vm = this;
            let columnList = [
                    {
                        // 1. Number
                        data: "id",
                        mRender:function (data,type,full) {
                            //return `C${data}`;
                            return full.reference;
                        },
                        name: "id, lodgement_number",
                    }]
            if (this.dasTemplateGroup) {
                columnList.push(
                    {
                        // 2. Region/District
                        data: "regions",
                        name: "proposal__region__name", // will be use like: Approval.objects.filter(proposal__region__name='Kimberley')
                        //visible: false,
                    });
            };
            columnList.push(
                    {
                        // 3. Activity
                        data: "activity",
                        name: "proposal__activity",
                        //visible: true,
                    });
            if (this.dasTemplateGroup) {
                columnList.push(
                    {
                        // 4. Title
                        data: "title",
                        name: "proposal__title",
                        //visible: false,
                    });
            };
            if (this.dasTemplateGroup) {
                columnList.push(
                    {
                        // 5. Requirement
                        data: "requirement",
                        //name: "proposal__title",
                        //visible: false,
                        'render': function (value, type) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-toggle="popover" ' +
                                    'data-trigger="click" ' +
                                    'data-placement="top auto"' +
                                    'data-html="true" ' +
                                    'data-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }
                            //return result;
                            return type=='export' ? value : result;
                        },
                        'createdCell': helpers.dtPopoverCellFn,
                    });
            };
            if (this.dasTemplateGroup) {
                columnList.push(
                    {
                        // 6. Proposal
                        data: "proposal_lodgement_number",
                        name: "proposal__lodgement_number",
                        //visible: false,
                    });
            };
            columnList.push(
                    {
                        // 7. Due Date
                        data: "due_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        }
                    },
                    {
                        // 8. District
                        data: "district",
                        searchable: false,
                    },
                    {
                        // 9. Holder
                        data: "holder",
                        name: "proposal__applicant__organisation__name"
                    },
                    {
                        // 10. Approval/Licence
                        data: "approval_lodgement_number",
                        mRender:function (data,type,full) {
                            return `A${data}`;
                        },
                        name: "approval__lodgement_number"
                    },
                    {
                        // 11. Status
                        data: vm.level == 'external'? "customer_status" : "processing_status",
                        searchable: false,  // There is a filter dropdown for 'Status'
                    },
                    );

            if (!vm.is_external) {
                columnList.push({
                        // 12. Assigned To
                        data: "assigned_to",
                        name: "assigned_to__first_name, assigned_to__last_name, assigned_to__email"
                        // visible: false
                    });
            }
            columnList.push(
                    {
                        // 13. Action
                        data: '',
                        mRender:function (data,type,full) {
                            //console.log(full)
                            let links = '';
                            if (!vm.is_external){
                                if (full.processing_status=='With Assessor' && vm.check_assessor(full)) {
                                    links +=  `<a href='/internal/compliance/${full.id}'>Process</a><br/>`;

                                }
                                else {
                                    links +=  `<a href='/internal/compliance/${full.id}'>View</a><br/>`;
                                }
                            }
                            else{
                                if (full.can_user_view) {
                                    links +=  `<a href='/external/compliance/${full.id}'>View</a><br/>`;

                                }
                                else {
                                    links +=  `<a href='/external/compliance/${full.id}'>Submit</a><br/>`;
                                }
                            }
                            return links;
                        },
                        name: '',
                        className: "noexport",
                    },
                    {
                        data: "reference", 
                        visible: false,
                        className: "noexport",
                    },
                    {
                        data: "customer_status", 
                        visible: false,
                        className: "noexport",
                    },
                    {
                        data: "can_user_view", 
                        visible: false,
                        className: "noexport",
                    },
                    {
                        data: "allowed_assessors", 
                        visible: false,
                        className: "noexport",
                    }
            );
            return columnList;
        },

    },
    methods:{
        set_proposal_options: function() {
            this.datatableReady = false;
            let vm = this;
            this.uuid++;
            this.proposal_options = {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                serverSide: true,
                lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                ajax: {
                    "url": vm.url,
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        //d.start_date_from = vm.filterComplianceStartFrom != '' && vm.filterComplianceStartFrom != null ? moment(vm.filterComplianceStartFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        //d.start_date_to = vm.filterComplianceStartTo != '' && vm.filterComplianceStartTo != null ? moment(vm.filterComplianceStartTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.due_date_from = vm.filterComplianceDueFrom != '' && vm.filterComplianceDueFrom != null ? moment(vm.filterComplianceDueFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.due_date_to = vm.filterComplianceDueTo != '' && vm.filterComplianceDueTo != null ? moment(vm.filterComplianceDueTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.compliance_status = vm.filterComplianceStatus;
                        d.region = vm.filterProposalRegion;
                        d.proposal_activity = vm.filterProposalActivity;
                        d.is_external = vm.is_external;
                        d.regions = vm.filterProposalRegion.join();
                        //Remove the extra unused parameters from the GET url to reduce the length of the url
                        for (var i = 0; i < d.columns.length; i++) {
                            delete d.columns[i].search.regex;
                        }
                    }

                },
                dom: 'lBfrtip',
                /*
                buttons:[
                'excel', 'csv', ],
                */
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
                columns: vm.tableColumns,
                processing: true,
                initComplete: function() {
                    //vm.showHideColumns()
                },
            }
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
            let regionColumn = vm.$refs.proposal_datatable.vmDataTable.column('proposal__region__name:name');
            let activityColumn = vm.$refs.proposal_datatable.vmDataTable.column('proposal__activity:name');
            let titleColumn = vm.$refs.proposal_datatable.vmDataTable.column('proposal__title:name');
            if (vm.dasTemplateGroup) {
                regionColumn.visible(true);
                activityColumn.visible(true);
                titleColumn.visible(true);
            }
        },
        */
        fetchFilterLists: function(){
            let vm = this;

            vm.$http.get(api_endpoints.filter_list_compliances).then((response) => {
                vm.proposal_regions = response.body.regions;
                vm.proposal_activityTitles = response.body.activities;
                vm.status = vm.level == 'external' ? vm.external_status: vm.internal_status;
            },(error) => {
                console.log(error);
            })
            //console.log(vm.regions);
        },


        addEventListeners: function(){
            let vm = this;
            // Initialise Proposal Date Filters
            $(vm.$refs.complianceStartDateToPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.complianceStartDateToPicker).on('dp.change', function(e){
                if ($(vm.$refs.complianceStartDateToPicker).data('DateTimePicker').date()) {
                    vm.filterComplianceStartTo =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.complianceStartDateToPicker).data('date') === "") {
                    vm.filterProposaLodgedTo = "";
                }
             });
            $(vm.$refs.complianceStartDateFromPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.complianceStartDateFromPicker).on('dp.change',function (e) {
                if ($(vm.$refs.complianceStartDateFromPicker).data('DateTimePicker').date()) {
                    vm.filterComplianceStartFrom = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.complianceStartDateToPicker).data("DateTimePicker").minDate(e.date);
                }
                else if ($(vm.$refs.complianceStartDateFromPicker).data('date') === "") {
                    vm.filterComplianceStartFrom = "";
                }
            });
            
            $(vm.$refs.complianceDueDateToPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.complianceDueDateToPicker).on('dp.change', function(e){
                if ($(vm.$refs.complianceDueDateToPicker).data('DateTimePicker').date()) {
                    vm.filterComplianceDueTo =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.complianceDueDateToPicker).data('date') === "") {
                    vm.filterProposaLodgedTo = "";
                }
             });
            $(vm.$refs.complianceDueDateFromPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.complianceDueDateFromPicker).on('dp.change',function (e) {
                if ($(vm.$refs.complianceDueDateFromPicker).data('DateTimePicker').date()) {
                    vm.filterComplianceDueFrom = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.complianceDueDateToPicker).data("DateTimePicker").minDate(e.date);
                }
                else if ($(vm.$refs.complianceDueDateFromPicker).data('date') === "") {
                    vm.filterComplianceDueFrom = "";
                }
            });
            // End Proposal Date Filters

            // Initialise select2 for region
            //vm.applySelect2()
        },
        applySelect2: function(){
            //console.log('in applySelect2')
            let vm = this

            if (!vm.select2Applied){
                //console.log('select2 is being applied')
                $(vm.$refs.filterRegion).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    placeholder: "Select Region",
                    multiple: true,
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
        initialiseSearch:function(){
            this.regionSearch();
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
                    let from = vm.filterComplianceDueFrom;
                    let to = vm.filterComplianceDueTo;
                    let val = original.due_date;

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
        check_assessor: function(compliance){
            let vm = this;
            if (compliance.allowed_assessors) {
                var assessor = compliance.allowed_assessors.filter(function(elem){
                        return(elem.id==vm.profile.id)
                    });

                if (assessor.length > 0){
                    //console.log(proposal.id, assessor)
                    return true;
                }
                else
                    return false;
            } else {
                return false;
            }
        }
    },
    created: function() {
        let vm = this
        vm.$http.get('/template_group',{
            emulateJSON:true
            }).then(res=>{
                if (res.body.template_group === 'apiary') {
                    vm.apiaryTemplateGroup = true;
                } else {
                    vm.dasTemplateGroup = true;
                }
                vm.templateGroupDetermined = true
                vm.applySelect2()
        },err=>{
        console.log(err);
        });
    },
    mounted: function(){
        //console.log('in mounted')
        let vm = this;
        vm.fetchFilterLists();
        vm.fetchProfile();
        $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
        });
        /*
        if(vm.is_external){
            var column = vm.$refs.proposal_datatable.vmDataTable.columns(8); //Hide 'Assigned To column for external'
            column.visible(false);
        }
        */
        /*
        this.$nextTick(() => {
            this.initialiseSearch();
            this.addEventListeners();
        });
        */
    }
}
</script>
<style scoped>
</style>
