<template>
<div class="container" id="internalApproval">
    <div class="row">
        <h3>Licence {{ approval.lodgement_number }}</h3>
        <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                       Submission
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">

                            <div class="col-sm-12 top-buffer-s">
                                <strong>Issued on</strong><br/>
                                {{ approval.issue_date | formatDate}}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <table class="table small-table">
                                    <tr>
                                        <th>Lodgement</th>
                                        <th>Date</th>
                                        <th>Action</th>
                                    </tr>
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
                                {{ approval.status }}
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
                        <h3 class="panel-title">Holder
                            <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse" expanded="false"  data-parent="#userInfo" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                        </h3>
                    </div>
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

                    <!--div class="panel-body panel-collapse" :id="pBody">
                        <div class="row">
                            <div class="col-sm-12">
                                <form class="form-horizontal" name="approval_form">
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Organisation</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="name" placeholder="" v-model="org.name">
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">ABN</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="abn" placeholder="" v-model="org.abn">
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div-->
                </div>
            </div>

            <div class="row">

                <div class="panel panel-default">
                  <div class="panel-heading">
                    <h3 class="panel-title">Address Details
                        <a class="panelClicker" :href="'#'+adBody" data-toggle="collapse" expanded="true"  data-parent="#userInfo" :aria-controls="adBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                  </div>
                  <div v-if="loading.length == 0 && approval && approval.applicant_address" class="panel-body collapse" :id="adBody">
                      <form class="form-horizontal" action="index.html" method="post">
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
                  </div>
                </div>

            </div>

            <div class="row">

                <div class="panel panel-default">
                  <div class="panel-heading">
                    <h3 class="panel-title">Licence Details
                        <a class="panelClicker" :href="'#'+oBody" data-toggle="collapse" expanded="true"  data-parent="#userInfo" :aria-controls="oBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                  </div>
                  <div v-if="loading.length == 0" class="panel-body collapse" :id="oBody">
                      <form class="form-horizontal" action="index.html" method="post">
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Issue Date</label>
                            <div class="col-sm-6">
                                <label for="" class="control-label pull-left">{{approval.issue_date | formatDate}}</label>
                            </div>
                        <!---    <div class="col-sm-6">
                                <p>{{approval.issue_date | formatDate}}</p>
                            </div> -->
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
                                <!-- <p><a target="_blank" :href="approval.licence_document" class="control-label pull-left">Approval.pdf</a></p> -->
                                <!--p><a :href="'#'+approval.id" class="control-label pull-left" @click="viewApprovalPDF(approval.id, approval.latest_apiary_licence_document)">Approval.pdf</a></p-->
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
                  </div>
                </div>
            </div>

            <div class="row">
                <FormSection :formCollapse="false" label="Site(s)" Index="site_avaiability">
                    <template v-if="approval && approval.id">
                        <ComponentSiteSelection
                            :apiary_sites="approval.apiary_sites"
                            :show_col_checkbox="false"
                            :show_col_status="true"
                            :apiary_approval_id="approval.id"
                        />
                    </template>
                </FormSection>
            </div>

            <div class="row">
                <FormSection :formCollapse="false" label="Annual Site Fee" Index="annual_rental_fee">
                    <template v-if="approval && approval.id">
                        <SectionAnnualRentalFee
                            :is_readonly="false"
                            :is_internal="true"
                            :is_external="false"
                            :approval_id="approval.id"
                            :annual_rental_fee_periods="approval.annual_rental_fee_periods"
                            :no_annual_rental_fee_until="approval.no_annual_rental_fee_until"
                        />
                    </template>
                </FormSection>
            </div>

            <div class="row">
                <FormSection :formCollapse="false" label="Temporary Use" Index="temporary_use">
                    <template v-if="approval && approval.id">
                        <TemporaryUse
                            :approval_id="approval.id"
                            :is_internal="true"
                            :is_external="false"
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
                            :is_internal="true"
                            :is_external="false"
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
import ComponentSiteSelection from '@/components/common/apiary/component_site_selection.vue'
import SectionAnnualRentalFee from '@/components/common/apiary/section_annual_rental_fee.vue'
export default {
  name: 'ApiaryApproval',
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
  filters: {
    formatDate: function(data){
        return moment(data).format('DD/MM/YYYY');
    }
  },
    props: {
        approvalId: {
            type: Number,
        },
    },
  created: function(){
    let url_approval = helpers.add_endpoint_json(api_endpoints.approvals,this.approvalId)
    url_approval = url_approval + '?with_apiary_sites=false'

    //Vue.http.get(helpers.add_endpoint_json(api_endpoints.approvals,this.approvalId)).then((response) => {
    Vue.http.get(url_approval).then(
        (response) => {
            this.approval = response.body;
            this.approval.applicant_id = response.body.applicant_id;
            if (this.approval.organisation_abn) {
                this.fetchOrganisation(this.approval.applicant_id)
            }
        },
        (error) => {
            console.log(error);
        }
    )
  },
  components: {
        SectionAnnualRentalFee,
        datatable,
        CommsLogs,
        FormSection,
        OnSiteInformation,
        TemporaryUse,
        ComponentSiteSelection,
  },
  computed: {
    isLoading: function () {
      return this.loading.length > 0;
    },
    organisationApplicant: function() {
        let oApplicant = false;
        if (this.approval && this.approval.organisation_abn) {
            oApplicant = true;
        }
        return oApplicant;
    },

  },
  methods: {
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
