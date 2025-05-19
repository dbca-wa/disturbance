<template>
<div class="container" id="internalOrgAccessDash">
<div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">

                <div class="panel-heading">
                    <h3 class="panel-title">Organisation Access Requests
                        <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>


<div class="panel-body collapse in" :id="pBody">
    <div class="row">
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Organisation</label>
                <select class="form-control" v-model="filterOrganisation">
                    <option value="All">All</option>
                    <option v-for="o in organisationChoices" :value="o">{{o}}</option>
                </select>
            </div>
        </div>
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Applicant</label>
                <select class="form-control" v-model="filterApplicant">
                    <option value="All">All</option>
                    <option v-for="a  in applicantChoices" :value="a">{{a}}</option>
                </select>
            </div>
        </div>
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Role</label>
                <select class="form-control" v-model="filterRole">
                    <option value="All">All</option>
                    <option v-for="r in roleChoices" :value="r">{{r}}</option>
                </select>
            </div>
        </div>
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Status</label>
                <select class="form-control" v-model="filterStatus">
                    <option value="All">All</option>
                    <option v-for="s in statusChoices" :value="s">{{s}}</option>
                </select>
            </div>
        </div>
    </div>
    <template v-if="table_id">
        <datatable
            ref="org_access_table"
            id="org-access-table"
            :dtOptions="dtOptions"
            :dtHeaders="dtHeaders"
            :key="table_id">
        </datatable>
    </template>
</div>
</div>
</div>
</div>


</div>
</template>
<script>
import Vue from 'vue'
import $ from 'jquery'
import datatable from '@vue-utils/datatable.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
import {v4 as uuidv4} from 'uuid';
export default {
  name: 'OrganisationAccessDashboard',
  data() {
    let vm = this;
    return {
        dasTemplateGroup: false,
        apiaryTemplateGroup: false,
        // Filters
        pBody: 'pBody' + vm._uid,
        filterOrganisation: 'All',
        filterApplicant : 'All',
        filterRole : 'All',
        filterStatus: 'All',
        organisationChoices: [],
        applicantChoices: [],
        statusChoices: [],
        roleChoices: [],
        members:[],
        profile: {},
        table_id: 0,
        dtOptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                processing:true,
                order: [[0, "desc"]],
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisation_requests,'datatable_list'),
                    "dataSrc": '',
                },
                columns:[
                    {
                        data:"id",
                    },
                    {
                        data:"name",
                    },
                    {
                        data:"requester",
                    },
                    {
                        data:"role",
                    },
                    {
                        data:"status",
                    },
                    {
                        data:"lodgement_date",
                        mRender:function(data,type,full){
                            return moment(data).format('DD/MM/YYYY')
                        },
                        orderable: false,
                    },
                    {
                        data:"assigned_officer",
                    },
                    {
                        data:"id",
                        mRender:function(data, type, full){
                            if (full.status == 'Approved' || full.status == 'Declined'){
                                var column = "<a href='/internal/organisations/access/\__ID__\' >View </a>";
                            }
                            else{
                                if(vm.is_assessor){
                                    var column = "<a href='/internal/organisations/access/\__ID__\'> Process </a>";
                                }
                                else{
                                    var column = "<a href='/internal/organisations/access/\__ID__\' >View </a>";
                                }
                                //var column = "<a href='/internal/organisations/access/\__ID__\'> Process </a>";
                            }
                            return column.replace(/__ID__/g, data);
                        },
                        orderable: false,
                    },
                ],
                initComplete: function(){
                    // Grab Organisation from the data in the table
                    var organisationColumn = vm.$refs.org_access_table.vmDataTable.columns(1);
                    organisationColumn.data().unique().sort().each( function ( d, j ) {
                        let organisationChoices = [];
                        $.each(d,(index,a) => {
                            a != null && organisationChoices.indexOf(a) < 0 ? organisationChoices.push(a): '';
                        })
                        vm.organisationChoices = organisationChoices;
                    });
                    // Grab Applicant from the data in the table
                    var applicantColumn = vm.$refs.org_access_table.vmDataTable.columns(2);
                    applicantColumn.data().unique().sort().each( function ( d, j ) {
                        let applicationChoices = [];
                        $.each(d,(index,a) => {
                            a != null && applicationChoices.indexOf(a) < 0 ? applicationChoices.push(a): '';
                        })
                        vm.applicantChoices = applicationChoices;
                    });
                    // Grab Role from the data in the table
                    var roleColumn = vm.$refs.org_access_table.vmDataTable.columns(3);
                    roleColumn.data().unique().sort().each( function ( d, j ) {
                        let roleChoices = [];
                        $.each(d,(index,a) => {
                            a != null && roleChoices.indexOf(a) < 0 ? roleChoices.push(a): '';
                        })
                        vm.roleChoices = roleChoices;
                    });
                    // Grab Status from the data in the table
                    var statusColumn = vm.$refs.org_access_table.vmDataTable.columns(4);
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusChoices = [];
                        $.each(d,(index,a) => {
                            a != null && statusChoices.indexOf(a) < 0 ? statusChoices.push(a): '';
                        })
                        vm.statusChoices = statusChoices;
                    });
                }
            },
            dtHeaders:["Request Number","Organisation","Applicant","Role","Status","Lodged on","Assigned To","Action"],
        }
    },
    watch: {
        filterOrganisation: function() {
            let vm = this;
            if (vm.filterOrganisation!= 'All') {
                vm.$refs.org_access_table.vmDataTable.columns(1).search(vm.filterOrganisation).draw();
            } else {
                vm.$refs.org_access_table.vmDataTable.columns(1).search('').draw();
            }
        },
        filterApplicant: function() {
            let vm = this;
            if (vm.filterApplicant != 'All') {
                vm.$refs.org_access_table.vmDataTable.columns(2).search(vm.filterApplicant).draw();
            } else {
                vm.$refs.org_access_table.vmDataTable.columns(2).search('').draw();
            }
        },
        filterRole: function() {
            let vm = this;
            if (vm.filterRole != 'All') {
                vm.$refs.org_access_table.vmDataTable.columns(3).search(vm.filterRole).draw();
            } else {
                vm.$refs.org_access_table.vmDataTable.columns(3).search('').draw();
            }
        },
        filterStatus: function() {
            let vm = this;
            if (vm.filterStatus!= 'All') {
                vm.$refs.org_access_table.vmDataTable.columns(4).search(vm.filterStatus).draw();
            } else {
                vm.$refs.org_access_table.vmDataTable.columns(4).search('').draw();
            }
        },
    },
    components: {
        datatable
    },
    computed: {
        isLoading: function () {
            return this.loading.length == 0;
        },
        is_assessor: function(){
            return this.check_assessor()
        },
    },
    methods: {
        /*

        fetchAccessGroupMembers: function(){
        let vm = this;
        //vm.loading.push('Loading Access Group Members');
        vm.$http.get(api_endpoints.organisation_access_group_members).then((response) => {
            vm.members = response.body
            //vm.loading.splice('Loading Access Group Members',1);
        },(error) => {
            //vm.loading.splice('Loading Access Group Members',1);
        })
        },
        fetchProfile: function(){
        let vm = this;
        Vue.http.get(api_endpoints.profile).then((response) => {
            vm.profile = response.body

         },(error) => {

        })
        },
        */
        fetchAccessGroupMembers: async function(){
            //let vm = this;
            //this.loading.push('Loading Access Group Members');
            let url = api_endpoints.organisation_access_group_members;
            if (this.apiaryTemplateGroup) {
                url = api_endpoints.apiary_organisation_access_group_members;
            }
            const response = await this.$http.get(url)
            this.members = response.body
            //this.loading.splice('Loading Access Group Members',1);
            this.table_id = uuidv4()
        },
        fetchProfile: async function(){
            const response = await Vue.http.get(api_endpoints.profile);
            this.profile = response.body
        },

        check_assessor: function(){
            let vm = this
            let assessor = vm.members.filter(elem => elem.id == vm.profile.id)
            if (assessor.length > 0)
                return true;
            else
                return false;
        },
    },
    mounted: async function () {
        //await this.fetchAccessGroupMembers();
        //await this.fetchProfile();
    },
    created: async function() {
        // retrieve template group
        const res = await this.$http.get('/template_group',{
            emulateJSON:true
            })
        if (res.body.template_group === 'apiary') {
            this.apiaryTemplateGroup = true;
        } else {
            this.dasTemplateGroup = true;
        }
        await this.fetchProfile();
        await this.fetchAccessGroupMembers();
    },

}
</script>
