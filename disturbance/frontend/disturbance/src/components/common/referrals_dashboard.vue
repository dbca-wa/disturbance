<template id="proposal_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">{{ dashboardTitle }}
                        <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <div class="row">
                        <div v-if="!apiaryTemplateGroup">
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label for="">Region</label>
                                    <template v-show="select2Applied">
                                        <select style="width:100%" class="form-control input-sm" id="region_dropdown">
                                            <template v-if="select2Applied">
                                                <option v-for="r in proposal_regions" :value="r">{{r}}</option>
                                            </template>
                                        </select>
                                    </template>
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
                        <div v-else>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label for="">Application Type</label>
                                    <select class="form-control" v-model="filterProposalApplicationType">
                                        <option value="All">All</option>
                                        <option v-for="a in proposal_applicationTypes" :value="a">{{a}}</option>
                                    </select>
                                </div>
                            </div>
                        </div>


                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterProposalStatus">
                                    <option value="All">All</option>
                                    <option v-for="s in proposal_status" :value="s.value">{{s.name}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Lodged From</label>
                            <div class="input-group date" ref="proposalDateFromPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Lodged To</label>
                            <div class="input-group date" ref="proposalDateToPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Submitter</label>
                                <select class="form-control" v-model="filterProposalSubmitter">
                                    <option value="All">All</option>
                                    <option v-for="s in proposal_submitters" :value="s.email">{{s.search_term}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="proposal_datatable" :id="datatable_id" :dtOptions="proposal_options" :dtHeaders="proposal_headers"/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue'
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
import {
    api_endpoints,
    helpers
}from '@/utils/hooks'
export default {
    name: 'RefferralsTableDash',
    props: {
        url:{
            type: String,
            required: true
        },
    },

    data() {
        let vm = this;
        return {
            pBody: 'pBody' + vm._uid,
            datatable_id: 'proposal-datatable-'+vm._uid,
            //template_group: '',
            dasTemplateGroup: false,
            apiaryTemplateGroup: false,
            select2Applied: false,
            // Filters for Proposals
            filterProposalRegion: [],
            filterProposalActivity: 'All',
            filterProposalApplicationType: 'All',
            filterProposalStatus: 'All',
            filterProposalLodgedFrom: '',
            filterProposalLodgedTo: '',
            filterProposalSubmitter: 'All',
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            proposal_status:[],
            proposal_activityTitles : [],
            proposal_applicationTypes : [],
            proposal_regions: [],
            proposal_submitters: [],
            //proposal_headers:["Number","Region","Activity","Title","Submitter","Proponent","Status","Lodged on","Action","Template Group"],
            proposal_options:{
                customProposalSearch: true,
                tableID: 'proposal-datatable-'+vm._uid,
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
                    //"url": helpers.add_endpoint_json(api_endpoints.referrals,'user_list'),
                    //"url": api_endpoints.list_referrals,
                    "url": vm.url,
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        d.regions = vm.filterProposalRegion.join();
                        //d.processing_status = vm.filterProposalStatus;
                        d.date_from = vm.filterProposalLodgedFrom != '' && vm.filterProposalLodgedFrom != null ? moment(vm.filterProposalLodgedFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.date_to = vm.filterProposalLodgedTo != '' && vm.filterProposalLodgedTo != null ? moment(vm.filterProposalLodgedTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.application_type = vm.filterProposalApplicationType;
                        d.proposal_activity = vm.filterProposalActivity;
                        d.submitter = vm.filterProposalSubmitter;
                        d.proposal_status = vm.filterProposalStatus;
        		    }

                },
                columns: [
                    {
                        data: "proposal",
                        mRender:function(data,type,full){
                            let tick='';
                            if (full.can_be_processed){
                                // tick = "<span class='fa-stack'><i class='fa fa-circle fa-stack-1x' style='color:yellow'></i><i class='fa fa-exclamation fa-stack-1x' style=''></i></span>";
                                tick = "<i class='fa fa-exclamation-circle' style='color:#FFBF00'></i>";
                            }
                            else
                            {
                                tick = "<i class='fa fa-check-circle' style='color:green'></i>";
                            }
                            return full.proposal_lodgement_number+tick;
                        },
                        name: "proposal__id, proposal__lodgement_number",
                    },
                    {
                        data: "region",
                        searchable: false, // handles by filter_queryset override method - class ProposalFilterBackend
                        visible: false,
                    },
                    {
                        data: "activity",
                        name: "proposal__activity",
                        //searchable: false, // handles by filter_queryset override method - class ProposalFilterBackend
                    },
                    {
                        data: "title",
                        name: "proposal__title",
                        visible: false,
                    },
                    {
                        data: "submitter",
                        mRender:function (data,type,full) {
                            if (data) {
                                return `${data.first_name} ${data.last_name}`;
                            }
                            return ''
                        },
                        name: "proposal__submitter__email",
                    },
                    /*
                    {
                        data: "applicant",
                        mRender:function (data,type,full) {
                            if (data) {
                                return `${data}`;
                            } else if (full.proposal_proxy_applicant) {
                                return full.proposal_proxy_applicant.name;
                            } else {
                                return '';
                            }
                        },
                        name: "proposal__applicant__organisation__name",
                    },
                    */
                    {
                        data: "relevant_applicant_name",
                        name: "proposal__applicant__organisation__name",
                    },
                    {
                        data: "processing_status",
                        name: "proposal__processing_status",
                    },
                    {
                        data: "assigned_officer",
                        name: "assigned_officer",
                        mRender:function (data,type,full) {
                            if (data) {
                                return `${data.first_name} ${data.last_name}`;
                            }
                            return ''
                        },
                        visible: false,
                        searchable: false,
                    },
                    {
                        data: "proposal_lodgement_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        },
                        name: "proposal__lodgement_date",
                    },
                    {
                        data: '',
                        mRender:function (data,type,full) {
                            let links = '';
                            links +=  full.can_be_processed ? `<a href='/internal/proposal/${full.proposal}/referral/${full.id}'>Process</a><br/>`: `<a href='/internal/proposal/${full.proposal}/referral/${full.id}'>View</a><br/>`;
                            return links;
                        },
                        searchable: false,
                        orderable: false,
                        name: ''
                    },
                    {data: "can_be_processed", visible: false},
                    {data: "proposal_lodgement_number", visible: false},
                    {data: "id", visible: false},
                    {
                        data: 'template_group',
                        searchable: false,
                        orderable: false,
                        visible: false,
                    },

                ],
                processing: true,
                initComplete: function() {
                    // set column visibility and headers according to template group
                    // region
                    //let regionColumn = vm.$refs.proposal_datatable.vmDataTable.columns(1);
                    let regionColumn = vm.$refs.proposal_datatable.vmDataTable.column('region:name');
                    let titleColumn = vm.$refs.proposal_datatable.vmDataTable.column('proposal__title:name');
                    let assignedOfficerColumn = vm.$refs.proposal_datatable.vmDataTable.column('assigned_officer:name');
                    if (vm.dasTemplateGroup) {
                        regionColumn.visible(true);
                        titleColumn.visible(true);
                    } else {
                        assignedOfficerColumn.visible(true);
                    }
                },
                /*
                initComplete: function () {
                    // Grab Regions from the data in the table
                    var regionColumn = vm.$refs.proposal_datatable.vmDataTable.columns(1);
                    regionColumn.data().unique().sort().each( function ( d, j ) {
                        let regionTitles = [];
                        $.each(d,(index,a) => {
                            // Split region string to array
                            if (a != null){
                                $.each(a.split(','),(i,r) => {
                                    r != null && regionTitles.indexOf(r) < 0 ? regionTitles.push(r): '';
                                });
                            }
                        })
                        vm.proposal_regions = regionTitles;
                    });
                    // Grab Activity from the data in the table
                    var titleColumn = vm.$refs.proposal_datatable.vmDataTable.columns(2);
                    titleColumn.data().unique().sort().each( function ( d, j ) {
                        let activityTitles = [];
                        $.each(d,(index,a) => {
                            a != null && activityTitles.indexOf(a) < 0 ? activityTitles.push(a): '';
                        })
                        vm.proposal_activityTitles = activityTitles;
                    });
                    // Grab submitters from the data in the table
                    var submittersColumn = vm.$refs.proposal_datatable.vmDataTable.columns(4);
                    submittersColumn.data().unique().sort().each( function ( d, j ) {
                        var submitters = [];
                        $.each(d,(index,s) => {
                            if (!submitters.find(submitter => submitter.email == s.email) || submitters.length == 0){
                                submitters.push({
                                    'email':s.email,
                                    'search_term': `${s.first_name} ${s.last_name} (${s.email})`
                                });
                            }
                        });
                        vm.proposal_submitters = submitters;
                    });
                    // Grab Status from the data in the table
                    var statusColumn = vm.$refs.proposal_datatable.vmDataTable.columns(6);
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusTitles = [];
                        $.each(d,(index,a) => {
                            a != null && statusTitles.indexOf(a) < 0 ? statusTitles.push(a): '';
                        })
                        vm.proposal_status = statusTitles;
                    });
                }
                */
            }
        }
    },
    components:{
        datatable
    },
    watch:{
        filterProposalActivity: function() {
            let vm = this;
            if (vm.filterProposalActivity!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.column('proposal__activity:name').search(vm.filterProposalActivity).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.column('proposal__activity:name').search('').draw();
            }
        },
        filterProposalApplicationType: function() {
            let vm = this;
            if (vm.filterProposalApplicationType!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.column('proposal__activity:name').search(vm.filterProposalApplicationType).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.column('proposal__activity:name').search('').draw();
            }
        },
        filterProposalStatus: function() {
            let vm = this;
            if (vm.filterProposalStatus!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.column('proposal__processing_status:name').search(vm.filterProposalStatus).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.column('proposal__processing_status:name').search('').draw();
            }
        },
        filterProposalRegion: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalSubmitter: function(){
            //this.$refs.proposal_datatable.vmDataTable.draw();
            let vm = this;
            if (vm.filterProposalSubmitter!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.column('proposal__submitter__email:name').search(vm.filterProposalSubmitter).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.column('proposal__submitter__email:name').search('').draw();
            }
        },
        filterProposalLodgedFrom: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalLodgedTo: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        }
    },
    computed: {
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
        dashboardTitle: function() {
            let title = ''
            if (this.apiaryTemplateGroup) {
                title = 'Applications referred to me';
            } else {
                title = 'Proposals referred to me';
            }
            return title;
        },
        proposal_headers: function() {
            let activity_or_application_type = 'Activity'
            let proponent_or_applicant = 'Proponent'
            if (this.apiaryTemplateGroup) {
                activity_or_application_type = 'Application Type'
                proponent_or_applicant = 'Applicant'
            }
            return [
                "Number",
                "Region",
                activity_or_application_type,
                "Title",
                "Submitter",
                proponent_or_applicant,
                "Status",
                "Assigned Officer",
                "Lodged on",
                "Action",
                "Template Group"
            ]
        },
    },
    methods:{
        fetchFilterLists: function(){
            let vm = this;

            vm.$http.get(api_endpoints.filter_list_referrals).then((response) => {
                vm.proposal_regions = response.body.regions;
                //vm.proposal_districts = response.body.districts;
                vm.proposal_activityTitles = response.body.activities;
                vm.proposal_applicationTypes = response.body.application_types;
                vm.proposal_submitters = response.body.submitters;
                vm.proposal_status = response.body.processing_status_choices;
            },(error) => {
                console.log(error);
            })
            //console.log(vm.regions);
        },

        addEventListeners: function(){
            let vm = this;
            // Initialise Proposal Date Filters
            $(vm.$refs.proposalDateToPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.proposalDateToPicker).on('dp.change', function(e){
                if ($(vm.$refs.proposalDateToPicker).data('DateTimePicker').date()) {
                    vm.filterProposalLodgedTo =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.proposalDateToPicker).data('date') === "") {
                    vm.filterProposaLodgedTo = "";
                }
             });
            $(vm.$refs.proposalDateFromPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.proposalDateFromPicker).on('dp.change',function (e) {
                if ($(vm.$refs.proposalDateFromPicker).data('DateTimePicker').date()) {
                    vm.filterProposalLodgedFrom = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.proposalDateToPicker).data("DateTimePicker").minDate(e.date);
                }
                else if ($(vm.$refs.proposalDateFromPicker).data('date') === "") {
                    vm.filterProposalLodgedFrom = "";
                }
            });
            // End Proposal Date Filters
            // External Discard listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-discard-proposal]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-discard-proposal');
                vm.discardProposal(id);
            });
            //if (this.dasTemplateGroup) {
            //    // Initialise select2 for region
            //    $(vm.$refs.filterRegion).select2({
            //        "theme": "bootstrap",
            //        allowClear: true,
            //        placeholder:"Select Region"
            //    }).
            //    on("select2:select",function (e) {
            //        var selected = $(e.currentTarget);
            //        vm.filterProposalRegion = selected.val();
            //    }).
            //    on("select2:unselect",function (e) {
            //        var selected = $(e.currentTarget);
            //        vm.filterProposalRegion = selected.val();
            //    });
            //}
        },
        initialiseSearch:function(){
            this.regionSearch();
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
        applySelect2: function(){
            console.log('in applySelect2')
            let vm = this

            if (!vm.select2Applied){
                console.log('select2 is being applied')
                //$(vm.$refs.filterRegion).select2({
                let target = $('#region_dropdown')
                console.log(target)
                target.select2({
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
        }
    },
    mounted: function(){
        let vm = this;
        vm.fetchFilterLists();
        $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
        });
        this.$nextTick(() => {
            vm.addEventListeners();
            //vm.initialiseSearch();
        });
    },
    updated: function() {
        this.$nextTick(() => {
            this.initialiseSearch();
            //this.addEventListeners();
        });
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
                    this.applySelect2()
                }
        },err=>{
        console.log(err);
        });
    },
    /*
    created: function() {
        // retrieve template group
        this.$http.get('/template_group',{
            emulateJSON:true
            }).then(res=>{
                this.template_group = res.body.template_group;
        },err=>{
        console.log(err);
        });

    },
    */
}
</script>
<style scoped>
</style>
