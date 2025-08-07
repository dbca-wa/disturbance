<template>
<div class="container" id="internalOrgAccess">
    <div class="row">
        <h3>Organisation Access Request {{ access.id }}</h3>
        <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                       Submission 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Submitted by</strong><br/>
                                {{ access.requester.full_name }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Lodged on</strong><br/>
                                {{ formatDate(access.lodgement_date) }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <table class="table small-table">
                                    <thead>
                                        <tr>
                                            <th>Lodgement</th>
                                            <th>Date</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        Workflow 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Status</strong><br/>
                                {{ access.status }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Currently assigned to</strong><br/>
                                <div class="form-group">
                                    <select v-show="isLoading" class="form-control">
                                        <option value="">Loading...</option>
                                    </select>
                                    <select @change="assignTo" :disabled="isFinalised || !check_assessor()" v-if="!isLoading" class="form-control" v-model="access.assigned_officer">
                                        <option value="null">Unassigned</option>
                                        <option v-for="member in members" :value="member.id" :key="member.id">{{member.name}}</option>
                                    </select>
                                    <a v-if="!isFinalised && check_assessor()" @click.prevent="assignMyself()" class="actionBtn pull-right">Assign to me</a>
                                </div>
                            </div>
                            <div class="col-sm-12 top-buffer-s" v-if="!isFinalised && check_assessor()">
                                <strong>Action</strong><br/>
                                <button class="btn btn-primary btn-margin" @click.prevent="acceptRequest()">Accept</button><br/>
                                <button class="btn btn-primary top-buffer-s" @click.prevent="declineRequest()">Decline</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-8">
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3>Organisation Access Request</h3> 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <form class="form-horizontal" name="access_form">
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Organisation</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="name" placeholder="" v-model="access.name">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">ABN</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="abn" placeholder="" v-model="access.abn">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Letter</label>
                                        <div class="col-sm-6">
                                            <a target="_blank" :href="access.identification"><i class="fa fa-file-pdf-o"></i>&nbsp;Letter</a>
                                        </div>
                                    </div>   
                                    <div class="form-group" style="margin-top:50px;">
                                        <label for="" class="col-sm-3 control-label">Phone</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="phone" placeholder="" v-model="access.requester.phone_number">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Mobile</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="mobile" placeholder="" v-model="access.requester.mobile_number">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Email</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="email" placeholder="" v-model="access.requester.email">
                                        </div>
                                    </div>   
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
</template>
<script>
import $ from 'jquery'
import CommsLogs from '@common-utils/comms_logs.vue'
import {
  api_endpoints,
  helpers,
  constants
}
from '@/utils/hooks'
export default {
  name: 'OrganisationAccess',
  data() {
    let vm = this;
    return {
        dasTemplateGroup: false,
        apiaryTemplateGroup: false,
        loading: [],
        profile:{},
        access: {
            requester: {}
        },
        DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
        members: [],
        // Filters
        logs_url: helpers.add_endpoint_json(api_endpoints.organisation_requests,vm.$route.params.access_id+'/action_log'),
        comms_url: helpers.add_endpoint_json(api_endpoints.organisation_requests,vm.$route.params.access_id+'/comms_log'),
        comms_add_url: helpers.add_endpoint_json(api_endpoints.organisation_requests,vm.$route.params.access_id+'/add_comms_log'),
        actionDtOptions:{
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
                "url": helpers.add_endpoint_json(api_endpoints.organisation_requests,vm.$route.params.access_id+'/action_log'),
                "dataSrc": '',
            },
            columns:[
                {
                    data:"who",
                },
                {
                    data:"what",
                },
                {
                    data:"when",
                    mRender:function(data){
                        return moment(data).format(vm.DATE_TIME_FORMAT)
                    }
                },
            ]
        },
        dtHeaders:["Who","What","When"],
        actionsTable : null,
        commsDtOptions:{
            language: {
                processing: constants.DATATABLE_PROCESSING_HTML,
            },
            responsive: true,
            deferRender: true, 
            autowidth: true,
            order: [[0, 'desc']],
            processing:true,
            ajax: {
                "url": helpers.add_endpoint_json(api_endpoints.organisation_requests,vm.$route.params.access_id+'/comms_log'),
                "dataSrc": '',
            },
            columns:[
                {
                    title: 'Date',
                    data: 'created',
                    render: function (date) {
                        return moment(date).format(vm.DATE_TIME_FORMAT);
                    }
                },
                {
                    title: 'Type',
                    data: 'type'
                },
                {
                    title: 'Reference',
                    data: 'reference'
                },
                {
                    title: 'To',
                    data: 'to',
                    render: vm.commaToNewline
                },
                {
                    title: 'CC',
                    data: 'cc',
                    render: vm.commaToNewline
                },
                {
                    title: 'From',
                    data: 'fromm',
                    render: vm.commaToNewline
                },
                {
                    title: 'Subject/Desc.',
                    data: 'subject'
                },
                {
                    title: 'Text',
                    data: 'text',
                    'render': function (value) {
                        var ellipsis = '...',
                            truncated = _.truncate(value, {
                                length: 100,
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

                        return result;
                    },
                    'createdCell': function (cell) {
                        //TODO why this is not working?
                        // the call to popover is done in the 'draw' event
                        $(cell).popover();
                    }
                },
                {
                    title: 'Documents',
                    data: 'documents',
                    'render': function (values) {
                        var result = '';
                        _.forEach(values, function (value) {
                            // We expect an array [docName, url]
                            // if it's a string it is the url
                            var docName = '',
                                url = '';
                            if (_.isArray(value) && value.length > 1){
                                docName = value[0];
                                url = value[1];
                            }
                            if (typeof s === 'string'){
                                url = value;
                                // display the first  chars of the filename
                                docName = _.last(value.split('/'));
                                docName = _.truncate(docName, {
                                    length: 18,
                                    omission: '...',
                                    separator: ' '
                                });
                            }
                            result += '<a href="' + url + '" target="_blank"><p>' + docName+ '</p></a><br>';
                        });
                        return result;
                    }
                }
            ]
        },
        commsTable : null,
    }
  },
  watch: {},
  beforeRouteEnter: function(to, from, next){
    fetch(helpers.add_endpoint_json(api_endpoints.organisation_requests,to.params.access_id)).then(async (response) => {
        let data = await response.json();
        next(vm => {
            vm.access = data;
        })
    },(error) => {
        console.log(error);
    })
  },
  components: {
    CommsLogs
  },
  computed: {
    isLoading: function () {
      return this.loading.length > 0;
    },
    isFinalised: function(){
        return this.access.status == 'With Assesor' || this.access.status == 'Approved' || this.access.status == 'Declined' ;
    },
  },
  methods: {
    commaToNewline(s){
        return s.replace(/[,;]/g, '\n');
    },
    formatDate: function(data){
        return moment(data).format('DD/MM/YYYY HH:mm:ss');
    },
    fetchAccessGroupMembers: async function(){
        //let vm = this;
        this.loading.push('Loading Access Group Members');
        let url = api_endpoints.organisation_access_group_members;
        if (this.apiaryTemplateGroup) {
            url = api_endpoints.apiary_organisation_access_group_members;
        }
        const response = await fetch(url)
        const data = await response.json(); 
        this.members = data;
        this.loading.splice('Loading Access Group Members',1);
    },
    assignMyself: function(){
        let vm = this;
        fetch(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.access.id+'/assign_request_user')))
        .then(async (response) => {
            console.log(response);
            let data = await response.json();
            vm.access = data;
        }, (error) => {
            console.log(error);
        });
    },
    assignTo: function(){
        let vm = this;
        if ( vm.access.assigned_officer != 'null'){
            let data = {'user_id': vm.access.assigned_officer};
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.access.id+'/assign_to')),JSON.stringify(data),{
                emulateJSON:true
            }).then((response) => {
                console.log(response);
                vm.access = response.body;
            }, (error) => {
                console.log(error);
            });
            console.log('there');
        }
        else{
            fetch(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.access.id+'/unassign')))
            .then(async (response) => {
                console.log(response);
                let data = await response.json();
                vm.access = data;
            }, (error) => {
                console.log(error);
            });
        }
    },
    acceptRequest: function() {
        let vm = this;
        swal.fire({
            title: "Accept Organisation Request",
            text: "Are you sure you want to accept this organisation request?",
            icon: "question",
            showCancelButton: true,
            confirmButtonText: 'Accept'
        }).then((swalresult) => {
            if(swalresult.isConfirmed) {
                fetch(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.access.id+'/accept')))
                .then(async (response) => {
                    console.log(response);
                    let data = await response.json();
                    vm.access = data;
                }, (error) => {
                    console.log(error);
                });
            }
        },(error) => {
            console.log(error);
        });

    },

    declineRequest: function() {
        let vm = this;
        swal.fire({
            title: "Decline Organisation Request",
            text: "Are you sure you want to decline this organisation request?",
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Decline'
        }).then((swalresult) => {
            if(swalresult.isConfirmed) {
                fetch(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.access.id+'/decline')))
                .then(async (response) => {
                    console.log(response);
                    let data = await response.json();
                    vm.access = data;
                }, (error) => {
                    console.log(error);
                });
            }
        },(error) => {
            console.log(error);
        });
    },

    fetchProfile: async function(){
        const response = await fetch(api_endpoints.profile);
        const data = await response.json(); 
        this.profile = data;
    },

    check_assessor: function(){
        let vm = this;
        
        var assessor = vm.members.filter(function(elem){
            return(elem.name==vm.profile.full_name);
        });
        console.log(vm.members)
        console.log(assessor)
                if (assessor.length > 0)
                    return true;
                else
                    return false;
     },
  },
/*
  mounted: function () {
    let vm = this;
    this.fetchAccessGroupMembers();
    this.fetchProfile();
    
  },
  */
    created: async function() {
        // retrieve template group
        const res = await fetch('/template_group',{
            emulateJSON:true
            })
        const data = await res.json(); 
        if (data.template_group === 'apiary') {
            this.apiaryTemplateGroup = true;
        } else {
            this.dasTemplateGroup = true;
        }
        await this.fetchAccessGroupMembers();
        await this.fetchProfile();
    },

}
</script>
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
.hidePopover {
    display: none;
}
</style>
