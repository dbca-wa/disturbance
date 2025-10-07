<template>
<div id="internalApproval">
    <div class="row">
        <h3>Approval {{ approval.lodgement_number }}</h3>
        <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            <div class="mb-3">
                <div class="card card-default">
                    <div class="card-header">Submission</div>
                    <div class="card-body py-2">
                        <strong>Issued on</strong><br/>
                        {{ formatDate(approval.issue_date) }}
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
                    <div class="card-header">Workflow</div>
                    <div class="card-body">
                        <strong>Status</strong><br/>
                        {{ approval.status }}
                    </div>                        
                </div>
            </div>
        </div>
        <!-- <div class="col-md-1"></div> -->
        <div class="col-md-9">
            <FormSection :formCollapse="false" label="Holder" Index="holder">
                <form class="form-horizontal" name="approval_form">
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">Organisation</label>
                        <div class="col-sm-6">
                            <input type="text" disabled class="form-control" name="name" placeholder="" v-model="org.name">
                        </div>
                    </div>   
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">ABN</label>
                        <div class="col-sm-6">
                            <input type="text" disabled class="form-control" name="abn" placeholder="" v-model="org.abn">
                        </div>
                    </div>                                      
                </form>
            </FormSection>
            
            <FormSection :formCollapse="true" label="Address Details" Index="address_details">
                <form class="form-horizontal" action="index.html" method="post">
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">Street</label>
                        <div class="col-sm-6">
                            <input type="text" disabled class="form-control" name="street" placeholder="" v-model="org.address.line1">
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">Town/Suburb</label>
                        <div class="col-sm-6">
                            <input type="text" disabled class="form-control" name="surburb" placeholder="" v-model="org.address.locality">
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">State</label>
                        <div class="col-sm-3">
                            <input type="text" disabled class="form-control" name="country" placeholder="" v-model="org.address.state">
                        </div>
                        <label for="" class="col-sm-2 col-form-label">Postcode</label>
                        <div class="col-sm-2">
                            <input type="text" disabled class="form-control" name="postcode" placeholder="" v-model="org.address.postcode">
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label" >Country</label>
                        <div class="col-sm-6">
                            <input type="text" disabled class="form-control" name="country" v-model="org.address.country"/>
                        </div>
                    </div>
                </form>
            </FormSection>
            
            <FormSection :formCollapse="true" label="Approval Details" Index="approval_details">
                <form class="form-horizontal" action="index.html" method="post">
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">Issue Date</label>
                        <div class="col-sm-6">
                            <label for="" class="col-form-label float-start">{{ formatDate(approval.issue_date) }}</label>
                        </div>
                <!---    <div class="col-sm-6">
                        <p>{{ formatDate(approval.issue_date) }}</p>
                    </div> -->
                    </div>
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label" >Start Date</label>
                        <div class="col-sm-6">
                            <label for="" class="col-form-label float-start">{{ formatDate(approval.start_date) }}</label>
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">Expiry Date</label>
                        <div class="col-sm-3">
                            <label for="" class="col-form-label float-start">{{ formatDate(approval.expiry_date) }}</label>
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label" >Document</label>
                        <div class="col-sm-4">
                            <!-- <p><a target="_blank" :href="approval.licence_document" class="control-label pull-left">Approval.pdf</a></p> -->
                            <p><a :href="'#'+approval.id" class="col-form-label float-start" @click="viewApprovalPDF(approval.id, approval.licence_document)">Approval.pdf</a></p>
                        </div>
                    </div>
                </form>
            </FormSection>
        </div>
    </div>
</div>
</template>
<script>
// import datatable from '@vue-utils/datatable.vue'
import { v4 as uuidv4 } from 'uuid';
import CommsLogs from '@common-utils/comms_logs.vue'
import FormSection from "@/components/forms/section_toggle.vue";
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'ApprovalComponent',
  data() {
    let vm = this;
    return {
        loading: [],
        approval: {
            applicant_id: null
            
        },
        DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
        adBody: 'adBody'+uuidv4(),
        pBody: 'pBody'+uuidv4(),
        cBody: 'cBody'+uuidv4(),
        oBody: 'oBody'+uuidv4(),
        org: {
            address: {}
        },
        
        // Filters
        logs_url: helpers.add_endpoint_json(api_endpoints.approvals,vm.$route.params.approval_id+'/action_log'),
        comms_url: helpers.add_endpoint_json(api_endpoints.approvals,vm.$route.params.approval_id+'/comms_log'),  
        comms_add_url: helpers.add_endpoint_json(api_endpoints.approvals,vm.$route.params.approval_id+'/add_comms_log'),
    }
  },
  watch: {},
  props: {
    approvalId: {
        type: Number,
    },
  },
  created: function(){
    fetch(helpers.add_endpoint_json(api_endpoints.approvals,this.approvalId)).then(
        async (response) => {
            if (!response.ok) { return response.json().then(err => { throw err }); }
            let data = await response.json();
            this.approval = data;
            this.approval.applicant_id = data.applicant_id;
            this.fetchOrganisation(this.approval.applicant_id)
        }).catch((error) => {
            console.log(error);
        });
  },
/*
  beforeRouteEnter: function(to, from, next){
    fetch(helpers.add_endpoint_json(api_endpoints.approvals,to.params.approval_id)).then((response) => {
        next(vm => {
            vm.approval = response.body;
            vm.approval.applicant_id = response.body.applicant_id;
            vm.fetchOrganisation(vm.approval.applicant_id)

        })
    },(error) => {
        console.log(error);
    }) 
  },
  */
  components: {
    CommsLogs,
    FormSection,
  },
  computed: {
    isLoading: function () {
      return this.loading.length > 0;
    },
    
  },
  methods: {
    commaToNewline(s){
        return s.replace(/[,;]/g, '\n');
    },
    formatDate: function(data){
        return moment(data).format('DD/MM/YYYY');
    },
    fetchOrganisation(applicant_id){
        let vm=this;
        fetch(helpers.add_endpoint_json(api_endpoints.organisations,applicant_id)).then(
            async (response) => {
                if (!response.ok) { return response.json().then(err => { throw err }); }
                let data = await response.json();
                vm.org = data;
                vm.org.address = data.address;
            }).catch((error) => {
                console.log(error);
            });
    },
    viewApprovalPDF: function(id,media_link){
            //console.log(approval);
            fetch(helpers.add_endpoint_json(api_endpoints.approvals,(id+'/approval_pdf_view_log')),{
                })
                .then(async (response) => {  
                    if (!response.ok) { return response.json().then(err => { throw err }); }
                }).catch((error) => {
                    console.log(error);
                });
            window.open(media_link, '_blank');
    },
  
  
  },
  mounted: function () {
    // let vm = this;
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
