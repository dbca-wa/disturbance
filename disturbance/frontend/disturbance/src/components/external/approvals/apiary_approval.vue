<template>
<div class="container" id="externalApproval">
    <div class="row">
        <div class="col-md-3">
            <h3>Licence: {{ approval.lodgement_number }}</h3>
        </div>

        <div class="col-sm-9">
            <div class="row">
                <FormSection :formCollapse="false" label="Holder" Index="holder">
                    <div v-if="organisationApplicant">
                        <!--div class="panel-body panel-collapse collapse in" :id="detailsBody"-->
                        <div class="panel-body panel-collapse collapse in">
                            <form class="form-horizontal">
                                <div class="form-group">
                                  <label for="" class="col-sm-3 control-label">Name</label>
                                  <div class="col-sm-6">
                                      <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="approval.organisation_name">
                                  </div>
                                </div>
                                <div class="form-group">
                                  <label for="" class="col-sm-3 control-label" >ABN/ACN</label>
                                  <div class="col-sm-6">
                                      <input disabled type="text" class="form-control" name="applicantABN" placeholder="" v-model="approval.organisation_abn">
                                  </div>
                                </div>
                            </form>
                        </div>
                    </div>
                    <div v-else>
                        <div class="panel-body panel-collapse collapse in">
                            <form class="form-horizontal">
                                <div class="form-group">
                                  <label for="" class="col-sm-3 control-label">Given Name(s)</label>
                                  <div class="col-sm-6">
                                      <input disabled type="text" class="form-control" name="applicantFirstName" placeholder="" v-model="approval.applicant_first_name">
                                  </div>
                                </div>
                                <div class="form-group">
                                  <label for="" class="col-sm-3 control-label" >Last Name</label>
                                  <div class="col-sm-6">
                                      <input disabled type="text" class="form-control" name="applicantLastName" placeholder="" v-model="approval.applicant_last_name">
                                  </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </FormSection>
            </div>

            <div class="row">
                <FormSection :formCollapse="false" label="Address Details" Index="address_details">
                    <form v-if="approval.applicant_address" class="form-horizontal" action="index.html" method="post">
                        <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Street</label>
                            <div class="col-sm-6">
                                <input type="text" disabled class="form-control" name="street" placeholder="" v-model="approval.applicant_address.line1">
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                            <div class="col-sm-6">
                                <input type="text" disabled class="form-control" name="surburb" placeholder="" v-model="approval.applicant_address.locality">
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="" class="col-sm-3 control-label">State</label>
                            <div class="col-sm-3">
                                <input type="text" disabled class="form-control" name="country" placeholder="" v-model="approval.applicant_address.state">
                            </div>
                            <label for="" class="col-sm-1 control-label">Postcode</label>
                            <div class="col-sm-2">
                                <input type="text" disabled class="form-control" name="postcode" placeholder="" v-model="approval.applicant_address.postcode">
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Country</label>
                            <div class="col-sm-4">
                                <input type="text" disabled class="form-control" name="country" v-model="approval.applicant_address.country">
                                </input>
                            </div>
                        </div>
                    </form>
                </FormSection>
            </div>

            <div class="row">
                <FormSection :formCollapse="false" label="Licence Details" Index="approval_details">
                    <form class="form-horizontal" action="index.html" method="post">
                        <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Issue Date</label>
                            <div class="col-sm-6">
                                <label for="" class="control-label pull-left">{{approval.issue_date | formatDate}}</label>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Start Date</label>
                            <div class="col-sm-6">
                                <label for="" class="control-label pull-left">{{approval.start_date | formatDate}}</label>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Expiry Date</label>
                            <div class="col-sm-3">
                                <label for="" class="control-label pull-left">{{approval.expiry_date | formatDate}}</label>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Document</label>
                            <div class="col-sm-4">
                                <p><a target="_blank" :href="approval.latest_apiary_licence_document" class="control-label pull-left">Licence.pdf</a></p>
                            </div>
                        </div>
                        <!--div class="form-group">
                          <label for="" class="col-sm-3 control-label" >Document History</label>
                          <div class="col-sm-4">
                              <div v-for="doc in approval.apiary_licence_document_history">
                                  <p><a target="_blank" :href="doc.url" class="control-label pull-left">{{doc.name}}</a></p>
                              </div>
                          </div>
                        </div-->
                     </form>
                </FormSection>

            </div>

            <div class="row">
                <FormSection :formCollapse="false" label="Site(s)" Index="site_avaiability">
                    <template v-if="approval && approval.id">
                        <SiteAvailability
                            :approval_id="approval.id"
                            :is_internal="false"
                            :is_external="true"
                            :user_can_site_transfer="user_can_interact"
                            ref="site_availability"
                        />
                    </template>
                </FormSection>
            </div>
            <div class="row">
                <FormSection :formCollapse="false" label="Annual Site Fee" Index="annual_rental_fee">
                    <template v-if="approval && approval.id">
                    </template>
                </FormSection>
            </div>

            <div class="row">
                <FormSection :formCollapse="false" label="Temporary Use" Index="temporary_use">
                    <template v-if="approval && approval.id">
                        <TemporaryUse
                            :approval_id="approval.id"
                            :is_internal="false"
                            :is_external="true"
                            :user_can_temporary_use="user_can_interact"
                            ref="tempoary_use"
                        />
                    </template>
                </FormSection>
            </div>

            <div class="row">
                <FormSection :formCollapse="false" label="On Site" Index="on_site">
                    <template v-if="approval && approval.id">
                        <OnSiteInformation
                            :approval_id="approval.id"
                            :is_internal="false"
                            :is_external="true"
                            :user_can_interact="user_can_interact"
                            ref="on_site_information"
                        />
                    </template>
                </FormSection>
            </div>
        </div>
    </div>
</div>
</template>
<script>
import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import FormSection from "@/components/forms/section_toggle.vue"
import { api_endpoints, helpers } from '@/utils/hooks'
import OnSiteInformation from '@/components/common/apiary/section_on_site_information.vue'
import TemporaryUse from '@/components/common/apiary/section_temporary_use.vue'
import SiteAvailability from '@/components/common/apiary/section_site_availability.vue'

export default {
    name: 'ApiaryApprovalExternal',
    props:{
        is_external: {
            type: Boolean,
            default: false
        },
        is_internal: {
            type: Boolean,
            default: false
        },
        approvalId: {
            type: Number,
            default: null,
        }
    },
    data() {
        let vm = this;
        return {
            loading: [],
            approval: {
                applicant_id: null
            },
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            adBody: 'adBody'+vm._uid,
            pBody: 'pBody'+vm._uid,
            cBody: 'cBody'+vm._uid,
            oBody: 'oBody'+vm._uid,
            onBody: 'onBody'+vm._uid,
            org: {
                address: {}
            },

            // variables passed to the child component
            //on_site_information_list: [],
            // Filters

        }
    },
    watch: {
        approval: {
            deep: true,
            handler(){
                console.log('approval in watch');

                // Construct the array, which is passed to the child component, SiteAvailability
                // Construct the array, which is passed to the child component, OnSiteInformation
                //this.on_site_information_list = []

                console.log(this.approval)

                //for (let i=0; i<this.approval.apiary_sites.length; i++){
                    //console.log('in apiary_sites.length')
                    //for (let j=0; j<this.approval.apiary_sites[i].onsiteinformation_set.length; j++){
                        //console.log('in onsiteinformation_setgt.length')
                        //this.on_site_information_list.push(this.approval.apiary_sites[i].onsiteinformation_set[j])
                    //}
                //}

                // Construct the array, which is passed to the child component, TemporaryUse

            }
        }
    },
    filters: {
        formatDate: function(data){
            return moment(data).format('DD/MM/YYYY');
        }
    },
    created: function() {
        if (this.approvalId) {
            this.loadApproval(this.approvalId)
        }
    },
    //beforeRouteEnter: function(to, from, next){
    //    Vue.http.get(helpers.add_endpoint_json(api_endpoints.approvals,to.params.approval_id)).then((response) => {
    //        next(vm => {
    //            console.log('in next');
    //            console.log('response.body: ');
    //            console.log(response.body);
    //            vm.approval = response.body;
    //            vm.approval.applicant_id = response.body.applicant_id;
    //            vm.fetchOrganisation(vm.approval.applicant_id)
    //        })
    //    },(error) => {
    //        console.log(error);
    //    })
    //},
    components: {
        datatable,
        CommsLogs,
        FormSection,
        OnSiteInformation,
        SiteAvailability,
        TemporaryUse,
    },
    computed: {
        isLoading: function () {
            return this.loading.length > 0;
        },
        proposal_apiary_id: function() {
            try {
                return this.approval.current_proposal.proposal_apiary.id;
            } catch(err) {
                return 0;
            }
        },
        organisationApplicant: function() {
            let oApplicant = false;
            if (this.approval && this.approval.organisation_abn) {
                oApplicant = true;
            }
            return oApplicant;
        },
        user_can_interact: function() {
            return this.approval.status.toLowerCase() === 'current' ? true : false
        },
    },
    methods: {
        loadApproval: function(approval_id){
            let vm = this
            console.log('in loadApproval')
            Vue.http.get(helpers.add_endpoint_json(api_endpoints.approvals,approval_id)).then(
                res => {
                    vm.approval = res.body;
                    vm.approval.applicant_id = res.body.applicant_id;
                    vm.fetchOrganisation(vm.approval.applicant_id)
                },
                error => {
                    console.log(error);
                }
            )
        },
        commaToNewline(s){
            return s.replace(/[,;]/g, '\n');
        },
        fetchOrganisation(applicant_id){
            let vm=this;
            Vue.http.get(helpers.add_endpoint_json(api_endpoints.organisations,applicant_id)).then((response) => {
                vm.org = response.body;
                vm.org.address = response.body.address;
        },(error) => {
            console.log(error);
        })

        },
    },
    mounted: function () {
        let vm = this;
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
