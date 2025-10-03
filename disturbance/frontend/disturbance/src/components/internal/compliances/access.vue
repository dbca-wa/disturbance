<template>
<div class="container" id="internalCompliance">
    <div class="row">
        <h3>Compliance with Requirements {{ compliance.reference }}</h3>
        <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            <div class="mb-3">
                <div class="card card-default">
                    <div class="card-header">
                       Submission 
                    </div>
                    <div class="card-body py-2">
                        <strong>Submitted by</strong><br/>
                        {{ compliance.submitter}}
                    </div>
                    <div class="card-body border-top py-2">
                        <strong>Lodged on</strong><br/>
                        {{ formatDate(compliance.lodgement_date) }}
                    </div>
                    <div class="card-body border-top py-2">
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
            <div class="mb-3">
                <div class="card card-default sticky-top">
                    <div class="card-header">
                        Workflow 
                    </div>
                    <div class="card-body py-2">
                        <strong>Status</strong><br/>
                        {{ compliance.processing_status }}
                    </div>
                    <div class="card-body border-top">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Currently assigned to</strong><br/>
                                <div class="form-group">
                                    <select v-show="isLoading" class="form-select">
                                        <option value="">Loading...</option>
                                    </select>
                                    <select @change="assignTo" :disabled="canViewonly || !check_assessor()" v-if="!isLoading" class="form-select" v-model="compliance.assigned_to">
                                        <option value="null">Unassigned</option>
                                        <option v-for="member in compliance.allowed_assessors" :value="member.id" :key="member.id">{{member.first_name}} {{member.last_name}}</option>
                                    </select>
                                    <a v-if="!canViewonly && check_assessor()" @click.prevent="assignMyself()" class="actionBtn float-end">Assign to me</a>
                                </div>
                            </div>  
                        </div>
                    </div>
                    <div class="card-body border-top" v-if="!canViewonly && check_assessor()">
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="row mb-2">
                                    <strong>Action</strong><br/>
                                </div>
                                <div class="col-sm-12">
                                    <button style="width: 90%" class="btn btn-primary" @click.prevent="acceptCompliance()">Accept</button><br/>
                                </div>
                                <div class="col-sm-12">
                                    <button style="width: 90%" class="btn btn-primary top-buffer-s" @click.prevent="amendmentRequest()">Request Amendment</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div> 
        </div>
        <div class="col-md-8">
            <FormSection :formCollapse="false" label="Compliance with Requirements" Index="compliance_with_req">
                <form class="form-horizontal" name="compliance_form">
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">Requirement</label>
                        <div class="col-sm-6">
                            {{compliance.requirement}}
                        </div>
                    </div>   
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">Details</label>
                        <div class="col-sm-6">
                            <textarea disabled class="form-control" name="details" placeholder="" v-model="compliance.text"></textarea>
                        </div>
                    </div>   
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">Documents</label>
                        <div class="col-sm-6">
                            <div class="row" v-for="d in compliance.documents" :key="d">
                                    <a :href="d[1]" target="_blank" class="control-label float-start">{{d[0]}}</a>
                            </div>
                        </div>
                    </div>                               
                </form>
            </FormSection>
        </div>
    </div>
    <ComplianceAmendmentRequest ref="amendment_request" :compliance_id="compliance.id"></ComplianceAmendmentRequest>
</div>
</template>
<script>
// import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import ComplianceAmendmentRequest from './compliance_amendment_request.vue'
import FormSection from "@/components/forms/section_toggle.vue";
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'complianceAccess',
  data() {
    let vm = this;
    return {
        loading: [],
        profile:{},
        compliance: {
            requester: {}
        },
        DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
        members: [],
        // Filters
        logs_url: helpers.add_endpoint_json(api_endpoints.compliances,vm.$route.params.compliance_id+'/action_log'),
        comms_url: helpers.add_endpoint_json(api_endpoints.compliances,vm.$route.params.compliance_id+'/comms_log'),
        comms_add_url: helpers.add_endpoint_json(api_endpoints.compliances,vm.$route.params.compliance_id+'/add_comms_log'),
      
    }
  },
  watch: {},
  beforeRouteEnter: function(to, from, next){
    fetch(helpers.add_endpoint_json(api_endpoints.compliances,to.params.compliance_id)).then(
        async (response) => {
            if (!response.ok) { return response.json().then(err => { throw err }); }
            let data = await response.json();
            next(vm => {
                vm.compliance = data;
                vm.members = vm.compliance.allowed_assessors
            })
        }).catch((error) => {
            console.log(error);
        });
  },
  components: {
    CommsLogs,
    ComplianceAmendmentRequest,
    FormSection,
  },
  computed: {
    isLoading: function () {
      return this.loading.length > 0;
    },
    canViewonly: function(){
        return this.compliance.processing_status == 'Due' || this.compliance.processing_status == 'Future' || this.compliance.processing_status == 'Approved';
    },
  },
  methods: {
    commaToNewline(s){
        return s.replace(/[,;]/g, '\n');
    },
    formatDate: function(data){
        return data ? moment(data).format('DD/MM/YYYY'): '';
    },
    assignMyself: function(){
        let vm = this;
        fetch(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/assign_request_user'))).then(
            async (response) => { 
                if (!response.ok) { return response.json().then(err => { throw err }); }           
                vm.compliance = await response.json();
            }).catch((error) => {
                console.log(error);
            });
    },
    assignTo: function(){
        let vm = this;
        if ( vm.compliance.assigned_to != 'null'){
            let data = {'user_id': vm.compliance.assigned_to};
            fetch(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/assign_to')),{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            }).then(async (response) => {  
                const res = await response.json();            
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                vm.compliance = res;
            }).catch((error) => {
                console.log(error);
            });
            
        }
        else{
            fetch(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/unassign'))).then(
                async (response) => {
                    if (!response.ok) { return response.json().then(err => { throw err }); }
                    console.log(response);
                    vm.compliance = await response.json();
                }).catch((error) => {
                    console.log(error);
                }
            );
        }
    },
    acceptCompliance: function() {
        let vm = this;
        swal.fire({
            title: "Accept Compliance with requirements",
            text: "Are you sure you want to accept this compliance with requirements?",
            icon: "question",
            showCancelButton: true,
            confirmButtonText: 'Accept',
            customClass: {
                confirmButton: 'btn btn-primary',
                cancelButton: 'btn btn-secondary',
            },
        }).then((swalresult) => {
            if(swalresult.isConfirmed){
                fetch(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/accept'))).then(
                    async (response) => {
                        if (!response.ok) { return response.json().then(err => { throw err }); }
                        console.log(response);
                        vm.compliance = await response.json();
                    }).catch((error) => {
                        console.log(error);
                    }
                );
            }
        },(error) => {
            console.log(error);
        });

    },
    amendmentRequest: function(){   
            this.$refs.amendment_request.amendment.compliance = this.compliance.id;                     
            this.$refs.amendment_request.isModalOpen = true;
    },
    fetchProfile: function(){
        let vm = this;
        fetch(api_endpoints.profile).then(async (response) => {
            if (!response.ok) { return response.json().then(err => { throw err }); }
            vm.profile = await response.json();
        }).catch((error) => {
            console.log(error);
                
        })
    },

    check_assessor: function(){
        let vm = this;
        //vm.members = vm.compliance.allowed_assessors
        if (vm.members) {
            var assessor = vm.members.filter(function(elem){
                        return(elem.id==vm.profile.id);
                    });
                    if (assessor.length > 0)
                        return true;
                    else
                        return false;
        } else {
            return false;
        }
     },
  },
  mounted: function () {
    // let vm = this;
    this.fetchProfile();
  }
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
