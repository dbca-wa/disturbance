<template lang="html">
    <div class="container" >
        <template v-if="is_local">
            proposal_external.vue
        </template>
        <form :action="proposal_form_url" method="post" name="new_proposal" enctype="multipart/form-data">
            <div v-if="!proposal_readonly">
              <div v-if="hasAmendmentRequest" class="row" style="color:red;">
                <div class="col-lg-12 pull-right">
                    <div class="panel panel-default">
                      <div class="panel-heading">
                          <h3 class="panel-title" style="color:red;">{{ amendmentRequestText }}
                          <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                          </a>
                        </h3>
                      </div>
                      <div class="panel-body collapse in" :id="pBody">
                        <div v-for="a in amendment_request">
                          <p>Reason: {{a.reason}}</p>
                          <p v-if="a.amendment_request_documents">Documents:<p v-for="d in a.amendment_request_documents"><a :href="d._file" target="_blank" class="control-label pull-left">{{d.name   }}</a><br></p></p>
                          <p>Details: <p v-for="t in splitText(a.text)">{{t}}</p></p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!--
            <label for="region-label">Region(*)</label>
            <input type="text" name="region-text"class="form-control" disabled="true">
            -->

            <div id="error" v-if="missing_fields.length > 0" style="margin: 10px; padding: 5px; color: red; border:1px solid red;">
                <b>Please answer the following mandatory question(s):</b>
                <ul>
                    <li v-for="error in missing_fields">
                        {{ error.label }}
                    </li>
                </ul>
            </div>

            <template v-if="proposal && proposal.application_type=='Apiary'">
                <ProposalApiary
                    v-if="proposal"
                    :proposal="proposal"
                    id="proposalStart"
                    :showSections="sectionShow"
                    ref="proposal_apiary"
                    :is_external="true"
                    @total_fee_south_west="update_total_fee_south_west"
                    @total_fee_remote="update_total_fee_remote"
                    @total_fee_south_west_renewal="update_total_fee_south_west_renewal"
                    @total_fee_remote_renewal="update_total_fee_remote_renewal"
                    @num_of_sites_remain_south_west="update_num_of_sites_remain_south_west"
                    @num_of_sites_remain_remote="update_num_of_sites_remain_remote"
                    @num_of_sites_remain_south_west_renewal="update_num_of_sites_remain_south_west_renewal"
                    @num_of_sites_remain_remote_renewal="update_num_of_sites_remain_remote_renewal"
                    @num_of_sites_south_west_to_add_as_remainder="update_num_of_sites_south_west_to_add_as_remainder"
                    @num_of_sites_remote_to_add_as_remainder="update_num_of_sites_remote_to_add_as_remainder"
                    @num_of_sites_south_west_renewal_to_add_as_remainder="update_num_of_sites_south_west_renewal_to_add_as_remainder"
                    @num_of_sites_remote_renewal_to_add_as_remainder="update_num_of_sites_remote_renewal_to_add_as_remainder"
                    @expiry_date_changed="expiry_date_changed"
                    @total_num_of_sites_on_map_unpaid="total_num_of_sites_on_map_unpaid_changed"
                    @total_num_of_sites_on_map="total_num_of_sites_on_map_changed"
                    @fee_remote_renewal="update_fee_remote_renewal"
                    @fee_south_west_renewal="update_fee_south_west_renewal"
                />
            </template>
            <template v-else-if="proposal && proposal.application_type=='Site Transfer'">
                <ApiarySiteTransfer
                    v-if="proposal"
                    :proposal="proposal"
                    id="proposalStart"
                    :showSections="sectionShow"
                    ref="apiary_site_transfer"
                    :is_external="true"
                    @button_text="button_text"
                    @site_transfer_application_fee="setSiteTransferApplicationFee"
                    @selectedLicenceHolderChanged="selectedLicenceHolderChanged"
                />
            </template>

            <template v-if="proposal && proposal.apiary_group_application_type">
                <div>
                    <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                    <input type='hidden' name="schema" :value="JSON.stringify(proposal)" />
                    <input type='hidden' name="proposal_id" :value="1" />

                    <div class="row" style="margin-bottom: 50px">
                        <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                            <div class="navbar-inner">
                                <div v-if="proposal && !proposal.readonly" class="container">
                                    <div class="row payment-details-buttons">

                                        <template v-if="is_proposal_type_new">
                                            <div class="col-sm-3 text-right">
                                            </div>
                                            <div class="col-sm-3 text-right">
                                                <div class="text-center payment-description-title">New sites</div>
                                                <div>{{ num_of_sites_south_west_remain_after_payment }}</div>
                                                <div>{{ num_of_sites_remote_remain_after_payment }}</div>
                                            </div>
                                        </template>

                                        <template v-if="is_proposal_type_transfer">
                                            <div class="col-sm-3 text-right">
                                            </div>
                                            <div class="col-sm-3 text-right">
                                                <div class="text-center payment-description-title"></div>
                                                <div></div>
                                                <div></div>
                                            </div>
                                        </template>

                                        <template v-if="is_proposal_type_renewal">
                                            <template v-if="!show_renewal_price_section">
                                                <div class="col-sm-3 text-right">
                                                </div>
                                            </template>
                                            <div class="col-sm-3 text-right">
                                                <div class="text-center payment-description-title">New sites</div>
                                                <div>{{ num_of_sites_south_west_remain_after_payment }}</div>
                                                <div>{{ num_of_sites_remote_remain_after_payment }}</div>
                                            </div>
                                            <template v-if="show_renewal_price_section">
                                                <div class="col-sm-3 text-right">
                                                    <div class="text-center payment-description-title">Renew sites</div>
                                                    <div v-if="fee_south_west_renewal > 0">
                                                        {{ num_of_sites_south_west_renewal_remain_after_payment }}
                                                    </div>
                                                    <div v-if="fee_remote_renewal > 0">
                                                        {{ num_of_sites_remote_renewal_remain_after_payment }}
                                                    </div>
                                                </div>
                                            </template>
                                        </template>

                                        <div class="col-sm-2 text-center">
                                            <div class="payment-description-title">Application fee</div>
                                            <div v-if="is_proposal_type_transfer">
                                                <div class="payment-description-total-fee">${{ siteTransferApplicationFee }}</div>
                                            </div>
                                            <div v-else>
                                                <div class="payment-description-total-fee">${{ sum_of_total_fees }}</div>
                                            </div>
                                        </div>
                                        <div class="col-sm-4 text-right no-padding">
                                            <span v-if="!isSubmitting">
                                                <input type="button" @click.prevent="save_exit" class="btn btn-primary" value="Save and Exit"/>
                                                <input type="button" @click.prevent="save(true)" class="btn btn-primary" value="Save and Continue"/>
                                                <span v-if="!isSaving">
                                                    <span v-if="proposal_type_name==='transfer'">
                                                        <input
                                                            type="button"
                                                            @click.prevent="submit"
                                                            class="btn btn-primary"
                                                            value="Pay and Submit"
                                                            :disabled="pay_button_disabled"
                                                        />
                                                    </span>
                                                    <span v-else>
                                                        <input
                                                            type="button"
                                                            @click.prevent="submit"
                                                            class="btn btn-primary"
                                                            :value="submit_button_text"
                                                            :disabled="!total_num_of_sites_on_map > 0"
                                                        />
                                                    </span>
                                                </span>
                                            </span>
                                            <span v-else-if="isSubmitting">
                                                <button disabled class="btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Submitting</button>
                                            </span>

                                            <input id="save_and_continue_btn" type="hidden" @click.prevent="save(false)" class="btn btn-primary" value="Save Without Confirmation"/>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
            <template v-else>
                <MapSection v-if="proposal && show_das_map" :proposal="proposal" @refreshFromResponse="refreshFromResponse" ref="mapSection" :is_external="true" />
                <ProposalDisturbance v-if="proposal" :proposal="proposal" id="proposalStart" :showSections="sectionShow" :key="proposalComponentMapKey">
                <NewApply v-if="proposal" :proposal="proposal"></NewApply>

                <!-- From master 28-Mar-2024 TODO remove this commented section
                <ProposalDisturbance v-if="proposal" :proposal="proposal" id="proposalStart" :showSections="sectionShow">
                <NewApply v-if="proposal" :proposal="proposal" ref="proposal_apply"></NewApply>
                -->
                <div>
                    <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                    <input type='hidden' name="schema" :value="JSON.stringify(proposal)" />
                    <input type='hidden' name="proposal_id" :value="1" />

                    <div class="row" style="margin-bottom: 50px">
                      <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                      <div class="navbar-inner">
                        <div v-if="proposal && !proposal.readonly" class="container">
                            <template v-if="proposal && proposal.apiary_group_application_type">
                            </template>
                            <template v-else>
                                <p class="pull-right" style="margin-top:5px;">
                                    <button id="sectionHide" @click.prevent="sectionHide" class="btn btn-primary">Show/Hide sections</button>
                                    <span v-if="!isSubmitting">
                                        <input type="button" @click.prevent="save_exit" class="btn btn-primary" value="Save and Exit"/>
                                        <input type="button" @click.prevent="save(true)" class="btn btn-primary" value="Save and Continue"/>
                                        <span v-if="!isSaving">
                                            <input type="button" @click.prevent="submit" class="btn btn-primary" value="Submit"/>
                                        </span>
                                    </span>
                                    <span v-else-if="isSubmitting">
                                        <button disabled class="btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Submitting</button>
                                    </span>
                                    <input id="save_and_continue_btn" type="hidden" @click.prevent="save_wo_confirm" class="btn btn-primary" value="Save Without Confirmation"/>
                                </p>
                            </template>
                        </div>
                        <div v-else class="container">
                          <p class="pull-right" style="margin-top:5px;">
                            <!--button id="sectionHide" @click.prevent="sectionHide" class="btn btn-primary">Show/Hide sections</button-->
                            <input
                            id="sectionHide"
                            v-if="proposal && !proposal.apiary_group_application_type"
                            type="button"
                            @click.prevent="sectionHide"
                            class="btn btn-primary"
                            value="Show/Hide Sections"/>

                            <router-link class="btn btn-primary" :to="{name: 'external-proposals-dash'}">Back to Dashboard</router-link>
                          </p>
                        </div>
                      </div>
                      </div>
                    </div>
                </div>
                </ProposalDisturbance>
            </template>


        </form>
        <div v-if="isSubmitting" id="overlay">
        </div>
    </div>
</template>
<script>
import ProposalDisturbance from '../form.vue'
import ProposalApiary from '../form_apiary.vue'
import ApiarySiteTransfer from '../form_apiary_site_transfer.vue'
import NewApply from './proposal_apply_new.vue'
import MapSection from '@/components/common/das/map_section.vue'
import Vue from 'vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    data: function() {
        return {
            "proposal": null,
            "loading": [],
            original_proposal: null,
            form: null,
            amendment_request: [],
            proposalComponentMapKey: 0,
            //isDataSaved: false,
            proposal_readonly: true,
            hasAmendmentRequest: false,
            submitting: false,
            submittingProposal: false,
            isSaving: false,
            newText: "",
            pBody: 'pBody',
            missing_fields: [],
            sectionShow: true,
            //submit_button_text: 'Pay and submit',
            submit_button_text: 'Submit',
            //pay_button_disabled: true,
            selectedHolder: null,

            // Fee
            total_fee_south_west: 0,
            total_fee_remote: 0,
            total_fee_south_west_renewal: 0,
            total_fee_remote_renewal: 0,
            fee_remote_renewal: 0,  // Used for toggling the 'renewal price section'
            fee_south_west_renewal: 0,  // Used for toggling the 'renewal price section'
            num_of_sites_remain_south_west: 0,
            num_of_sites_remain_remote: 0,
            num_of_sites_remain_south_west_renewal: 0,
            num_of_sites_remain_remote_renewal: 0,
            num_of_sites_south_west_to_add_as_remainder: 0,
            num_of_sites_remote_to_add_as_remainder: 0,
            num_of_sites_south_west_renewal_to_add_as_remainder: 0,
            num_of_sites_remote_renewal_to_add_as_remainder: 0,
            // Template group
            apiaryTemplateGroup: false,
            dasTemplateGroup: false,
            siteTransferApplicationFee: "0.00",
            total_num_of_sites_on_map_unpaid: 0,
            total_num_of_sites_on_map: 0,

            is_local: helpers.is_local(),
        }
    },
    components: {
        ProposalDisturbance,
        ProposalApiary,
        NewApply,
        ApiarySiteTransfer,
        MapSection,
    },
    computed: {
        show_das_map : function(){
                if (env && env['show_das_map'] &&  env['show_das_map'].toLowerCase()=="true"  ){
                    return true;
                } else {
                    return false;
                }
        },
        amendmentRequestText: function() {
            let requestText = 'An amendment has been requested for this proposal';
            if (this.apiaryTemplateGroup) {
                requestText = 'An amendment has been requested for this application';
            }
            return requestText;
        },
        show_renewal_price_section: function(){
            if (this.fee_remote_renewal + this.fee_south_west_renewal > 0){
                return true
            } else {
                return false
            }
        },
        num_of_sites_south_west_remain_after_payment: function() {
            let total = this.num_of_sites_remain_south_west + this.num_of_sites_south_west_to_add_as_remainder
            if (this.num_of_sites_south_west_to_add_as_remainder <= 0){
                return 'Previously paid sites (south west): ' + total
            } else {
                return 'Paid sites (south west) after payment: ' + total
            }
        },
        num_of_sites_remote_remain_after_payment: function() {
            let total = this.num_of_sites_remain_remote + this.num_of_sites_remote_to_add_as_remainder
            if (this.num_of_sites_remote_to_add_as_remainder <= 0){
                return 'Previously paid sites (remote): ' + total
            } else {
                return 'Paid sites (remote) after payment: ' + total
            }
        },
        num_of_sites_south_west_renewal_remain_after_payment: function() {
            let total = this.num_of_sites_remain_south_west_renewal + this.num_of_sites_south_west_renewal_to_add_as_remainder
            if (this.num_of_sites_south_west_renewal_to_add_as_remainder <= 0){
                return 'Previously paid sites (south west): ' + total
            } else {
                return 'Paid sites (south west) after payment: ' + total
            }
        },
        num_of_sites_remote_renewal_remain_after_payment: function() {
            let total = this.num_of_sites_remain_remote_renewal + this.num_of_sites_remote_renewal_to_add_as_remainder
            if (this.num_of_sites_remote_renewal_to_add_as_remainder <= 0){
                return 'Previously paid sites (remote): ' + total
            } else {
                return 'Paid sites (remote) after payment: ' + total
            }
        },
        isLoading: function() {
          return this.loading.length > 0
        },
        isSubmitting: function() {
          return this.submittingProposal;
        },
        csrf_token: function() {
          return helpers.getCookie('csrftoken')
        },
        application_fee_url: function() {
          return (this.proposal) ? `/application_fee/${this.proposal.id}/` : '';
        },
        proposal_form_url: function() {
          return (this.proposal) ? `/api/proposal/${this.proposal.id}/draft.json` : '';
        },
        proposal_submit_url: function() {
          return (this.proposal) ? `/api/proposal/${this.proposal.id}/submit.json` : '';
          //return this.submit();
        },
        remove_apiary_site_url: function() {
          return (this.proposal) ? `/api/proposal/${this.proposal.id}/remove_apiary_site.json` : '';
        },
        //submit_button_text: function() {
        //    if (!this.proposal.fee_paid && this.proposal.application_type=='Apiary') {
        //        return 'Pay and submit'
        //    } else {
        //        return 'Submit'
        //    }
        //}
        sum_of_total_fees: function(){
            let sum = this.total_fee_south_west + this.total_fee_remote + this.total_fee_south_west_renewal + this.total_fee_remote_renewal
            return sum
        },
        is_proposal_type_new: function(){
            if (this.proposal_type_name === 'new'){
                return true
            }
            return false
        },
        is_proposal_type_renewal: function(){
            if (this.proposal_type_name === 'renewal'){
                return true
            }
            return false
        },
        is_proposal_type_transfer: function(){
            if (this.proposal_type_name === 'transfer'){
                return true
            }
            return false
        },
        proposal_type_name: function() {
            if (this.proposal.application_type === 'Apiary'){
                if (this.proposal.proposal_type.toLowerCase() === 'renewal'){
                    return 'renewal'
                } else {
                    return 'new'
                }
            } else if (this.proposal.application_type === 'Site Transfer'){
                return 'transfer'
            } else {
                return '---'
            }
        },
        pay_button_disabled: function(){
            if (this.selectedHolder && this.siteTransferApplicationFee > 0){
                return false
            }
            return true
        }
    },
    watch: {
        sum_of_total_fees: function(){
            console.log('in sum_of_total_fees in watch')
            if (this.sum_of_total_fees > 0){
                this.submit_button_text = 'Pay and Submit'
            } else {
                this.submit_button_text = 'Submit'
            }
        },
        //siteTransferApplicationFee: function(){
        //    if (this.siteTransferApplicationFee> 0){
        //        this.pay_button_disabled = false
        //    } else {
        //        this.pay_button_disabled = true
        //    }
        //}
    },
    methods: {
        update_fee_remote_renewal: function(value){
            this.fee_remote_renewal = value
        },
        update_fee_south_west_renewal: function(value){
            this.fee_south_west_renewal = value
        },
        selectedLicenceHolderChanged: function(selectedHolder){
            this.selectedHolder = selectedHolder
        },
        total_num_of_sites_on_map_unpaid_changed: function(value){
            this.total_num_of_sites_on_map_unpaid = value
        },
        total_num_of_sites_on_map_changed: function(value){
            this.total_num_of_sites_on_map = value
        },
        expiry_date_changed: function(value){
            this.proposal.proposal_apiary.public_liability_insurance_expiry_date = moment(value, 'DD/MM/YYYY');
        },
        setSiteTransferApplicationFee: function(fee) {
            this.siteTransferApplicationFee = fee;
        },
        update_num_of_sites_south_west_to_add_as_remainder: function(value){
            this.num_of_sites_south_west_to_add_as_remainder = value
        },
        update_num_of_sites_remote_to_add_as_remainder: function(value){
            this.num_of_sites_remote_to_add_as_remainder = value
        },
        update_num_of_sites_south_west_renewal_to_add_as_remainder: function(value){
            this.num_of_sites_south_west_renewal_to_add_as_remainder = value
        },
        update_num_of_sites_remote_renewal_to_add_as_remainder: function(value){
            this.num_of_sites_remote_renewal_to_add_as_remainder = value
        },
        update_num_of_sites_remain_south_west: function(value){
            this.num_of_sites_remain_south_west = value
        },
        update_num_of_sites_remain_remote: function(value){
            this.num_of_sites_remain_remote = value
        },
        update_num_of_sites_remain_south_west_renewal: function(value){
            this.num_of_sites_remain_south_west_renewal = value
        },
        update_num_of_sites_remain_remote_renewal: function(value){
            this.num_of_sites_remain_remote_renewal = value
        },
        update_total_fee_south_west: function(total_fee){
            console.log('in update_total_fee_south_west: ' + total_fee)
            this.total_fee_south_west = total_fee
        },
        update_total_fee_remote: function(total_fee){
            console.log('in update_total_fee_remote: ' + total_fee)
            this.total_fee_remote = total_fee
        },
        update_total_fee_south_west_renewal: function(total_fee){
            console.log('in update_total_fee_south_west_renewal: ' + total_fee)
            this.total_fee_south_west_renewal = total_fee
        },
        update_total_fee_remote_renewal: function(total_fee){
            console.log('in update_total_fee_remote_renewal: ' + total_fee)
            this.total_fee_remote_renewal = total_fee
        },
        button_text: function(button_text){
            console.log('button text updated: ' + button_text)
            this.submit_button_text = button_text
        },
        //updateApiarySitesData: function() {
        //    if (this.proposal && this.proposal.proposal_apiary){
        //        this.$refs.proposal_apiary.$refs.apiary_site_locations.updateApiarySitesData()
        //    }
        //},
        //getFeatures: function() {
        //    let ret_obj = null
        //    if (this.proposal && this.proposal.proposal_apiary){
        //        ret_obj = this.$refs.proposal_apiary.$refs.apiary_site_locations.getFeatures()
        //    }
        //    return ret_obj
        //},
        attach_apiary_sites_data: function(formData){
            try {
                // Append apiary_sites edited data
                if (this.proposal && this.proposal.proposal_apiary){
                    let allFeatures = this.$refs.proposal_apiary.$refs.apiary_site_locations.getFeatures()
                    let json_features = JSON.stringify(allFeatures)
                    formData.append('all_the_features', json_features)
                }
                return formData
            } catch (err) {
                return formData
            }
        },
        save: async function(confirmation_required) {
            console.log('in save');
            this.isSaving = true;
            await this.$nextTick();

            let vm = this;
            vm.form=document.forms.new_proposal;

            let formData = new FormData(vm.form);
            // Add apiary_sites data if needed
            formData = this.attach_apiary_sites_data(formData)
            // Add site_transfer_apiary_sites data if needed
            /*
            if (this.$refs.apiary_site_transfer && this.$refs.apiary_site_transfer.site_transfer_apiary_sites) {
                console.log(this.$refs.apiary_site_transfer.site_transfer_apiary_sites)
                formData.append('site_transfer_apiary_sites', JSON.stringify(this.$refs.apiary_site_transfer.site_transfer_apiary_sites));
            }
            */
            if (this.$refs.apiary_site_transfer && this.$refs.apiary_site_transfer.apiary_sites_local) {
                //console.log(this.$refs.apiary_site_transfer.site_transfer_apiary_sites)
                formData.append('apiary_sites_local', JSON.stringify(this.$refs.apiary_site_transfer.apiary_sites_local));
            }
            if (this.$refs.apiary_site_transfer && this.$refs.apiary_site_transfer.selectedLicenceHolder){
                //let selectedLicenceHolder = this.$refs.apiary_site_transfer.selectedLicenceHolder
                formData.append('selected_licence_holder', JSON.stringify(this.$refs.apiary_site_transfer.selectedLicenceHolder));
            }
            if (this.$refs.apiary_site_transfer && this.$refs.apiary_site_transfer.transfereeEmail){
                let transfereeEmail = this.$refs.apiary_site_transfer.transfereeEmail
                formData.append('transferee_email_text', transfereeEmail);
            }

            console.log('http.post: ' + vm.proposal_form_url)
            vm.$http.post(vm.proposal_form_url, formData).then(
                res=>{
                    if (confirmation_required){
                        if (this.apiaryTemplateGroup) {
                            swal(
                                'Saved',
                                'Your application has been saved',
                                'success'
                            );
                        } else {
                            swal(
                                'Saved',
                                'Your proposal has been saved',
                                'success'
                            );
                        }
                    }
                    this.isSaving = false;
                },
                err=>{
                    console.log('err')
                    console.log(err)
                    if(err.body.type && err.body.type[0] === 'site_no_longer_available'){
                        vm.display_site_no_longer_available_modal(err)
                    } else {
                        helpers.processError(err)
                    }
                }
            );
        },
        save_exit: async function(e) {
            let vm = this;
            this.isSaving = true;
            vm.form=document.forms.new_proposal;
            this.submitting = true;
            await this.save(true);

            // redirect back to dashboard
            vm.$router.push({
                name: 'external-proposals-dash'
            });
            this.isSaving = false;
        },
        sectionHide: function(e) {
            let vm = this;
            vm.sectionShow=!vm.sectionShow
            //console.log(vm.sectionShow);
        },
        setdata: function(readonly){
            this.proposal_readonly = readonly;
        },
        setAmendmentData: function(amendment_request){
            this.amendment_request = amendment_request;
            if (amendment_request.length > 0)
                this.hasAmendmentRequest = true;
        },
        splitText: function(aText){
            let newText = '';
            newText = aText.split("\n");
            return newText;
        },
        leaving: function(e) {
            let vm = this;
            var dialogText = 'You have some unsaved changes.';
            if (!vm.proposal_readonly && !vm.submitting){
                e.returnValue = dialogText;
                return dialogText;
            }
            else{
                return null;
            }
        },
        highlight_missing_fields: function(){
            let vm = this;
            for (var missing_field of vm.missing_fields) {
                $("#" + missing_field.id).css("color", 'red');
            }
        },
        validate: function(){
            let vm = this;

            // reset default colour
            for (var field of vm.missing_fields) {
                $("#" + field.id).css("color", '#515151');
            }
            vm.missing_fields = [];

            // get all required fields, that are not hidden in the DOM
            //var hidden_fields = $('input[type=text]:hidden, textarea:hidden, input[type=checkbox]:hidden, input[type=radio]:hidden, input[type=file]:hidden');
            //hidden_fields.prop('required', null);
            //var required_fields = $('select:required').not(':hidden');
            var required_fields = $('input[type=text]:required, textarea:required, input[type=checkbox]:required, input[type=radio]:required, input[type=file]:required, select:required').not(':hidden');

            // loop through all (non-hidden) required fields, and check data has been entered
            required_fields.each(function() {
                //console.log('type: ' + this.type + ' ' + this.name)
                var id = 'id_' + this.name
                if (this.type == 'radio') {
                    //if (this.type == 'radio' && !$("input[name="+this.name+"]").is(':checked')) {
                    if (!$("input[name="+this.name+"]").is(':checked')) {
                        var text = $('#'+id).text()
                        console.log('radio not checked: ' + this.type + ' ' + text)
                        vm.missing_fields.push({id: id, label: text});
                    }
                }

                if (this.type == 'checkbox') {
                    var id = 'id_' + this.className
                    if ($("[class="+this.className+"]:checked").length == 0) {
                        try { var text = $('#'+id).text() } catch(error) { var text = $('#'+id).textContent }
                        console.log('checkbox not checked: ' + this.type + ' ' + text)
                        vm.missing_fields.push({id: id, label: text});
                    }
                }

                if (this.type == 'select-one') {
                    if ($(this).val() == '') {
                        var text = $('#'+id).text()  // this is the (question) label
                        var id = 'id_' + $(this).prop('name'); // the label id
                        console.log('selector not selected: ' + this.type + ' ' + text)
                        vm.missing_fields.push({id: id, label: text});
                    }
                }

                if (this.type == 'file') {
                    var num_files = $('#'+id).attr('num_files')
                    if (num_files == "0") {
                        var text = $('#'+id).text()
                        console.log('file not uploaded: ' + this.type + ' ' + this.name)
                        vm.missing_fields.push({id: id, label: text});
                    }
                }

                if (this.type == 'text') {
                    if (this.value == '') {
                        var text = $('#'+id).text()
                        console.log('text not provided: ' + this.type + ' ' + this.name)
                        vm.missing_fields.push({id: id, label: text});
                    }
                }

                if (this.type == 'textarea') {
                    if (this.value == '') {
                        var text = $('#'+id).text()
                        console.log('textarea not provided: ' + this.type + ' ' + this.name)
                        vm.missing_fields.push({id: id, label: text});
                    }
                }

                /*
                if (this.type == 'select') {
                    if (this.value == '') {
                        var text = $('#'+id).text()
                        console.log('select not provided: ' + this.type + ' ' + this.name)
                        vm.missing_fields.push({id: id, label: text});
                    }
                }

                if (this.type == 'multi-select') {
                    if (this.value == '') {
                        var text = $('#'+id).text()
                        console.log('multi-select not provided: ' + this.type + ' ' + this.name)
                        vm.missing_fields.push({id: id, label: text});
                    }
                }
                */
            });

            return vm.missing_fields.length

            /*
            if (emptyFields === 0) {
                $('#form').submit();
            } else {
                $('#error').show();
                return false;
            }
            */
        },

        check_org_details_complete: function(org) {
            //let org = this.$refs.proposal_apiary.$refs.mu_details.org
            let blank_fields = []

            // Org Details
            if (org) {
                if (!org.name) { blank_fields.push('org name') }
                if (!org.abn) { blank_fields.push('org abn') }
                if (!org.email) { blank_fields.push('org email') }

                // Address Details
                if (!org.address.line1) { blank_fields.push('street') }
                if (!org.address.locality) { blank_fields.push('town/suburb') }
                if (!org.address.state) { blank_fields.push('state') }
                if (!org.address.postcode) { blank_fields.push('postcode') }
                if (!org.address.country) { blank_fields.push('country') }
            }

            return blank_fields;
        },
        can_submit: function() {
            let vm=this;
            let blank_fields = []

            //console.log('can_submit checklistq check' +vm.$refs.proposal_apiary.getUnansweredChecklistQuestions());

             if(vm.proposal.application_type == 'Apiary'){
                let org = vm.$refs.proposal_apiary.$refs.mu_details.org
                if( vm.$refs.proposal_apiary.getUnansweredChecklistQuestions ){
                    blank_fields.push(' You have unanswered checklist questions');
                }
                if(vm.$refs.proposal_apiary.$refs.deed_poll_component.$refs.deed_poll_documents.documents.length==0){
                    blank_fields.push(' Deed poll document is missing')
                }
                if(vm.$refs.proposal_apiary.$refs.public_liability_insurance_documents.documents.length==0){
                    blank_fields.push(' Public liability insurance document is missing')
                }
                if (!this.proposal.proposal_apiary.public_liability_insurance_expiry_date) {
                    blank_fields.push(' Public liability expiry date is missing')
                }

                //this.$refs.proposal_apiary.$refs.mu_details.updateDetails(false);
                //this.$refs.proposal_apiary.$refs.mu_details.updateAddress(false);
                let blank_org_fields = vm.check_org_details_complete(org)
                if(blank_org_fields.length>0){
                    blank_fields.push(' Organisation details missing: [' + blank_org_fields.join(", ") + ']')
                }
             }
             if(vm.proposal.application_type == 'Site Transfer'){
                if( vm.$refs.apiary_site_transfer.getUnansweredChecklistQuestions ){
                    blank_fields.push(' You have unanswered checklist questions');
                }

                if(vm.$refs.apiary_site_transfer.$refs.deed_poll_component.$refs.deed_poll_documents.documents.length==0){
                    blank_fields.push(' Deed poll document is missing')
                }
                 /*
                if(!vm.$refs.apiary_site_transfer.selectedLicence){
                    blank_fields.push(' Transferee licence cannot be blank')
                }
                */
                if (!(this.$refs.apiary_site_transfer.num_of_sites_selected > 0)){
                    blank_fields.push(' You must select at least one site to transfer')
                }
             }
             else{
                if((!vm.proposal.region) || (!vm.proposal.district) || (vm.proposal.approval_level=='')) {
                    if((vm.proposal.management_area=='') && (vm.proposal.sub_activity_level1='')) {
                        blank_fields.push('Region or District or Category/Sub Activity cannot be blank')
                    }
                }
             }

             if(vm.proposal.application_type == 'Disturbance'){
                if(vm.proposal && vm.proposal.region && vm.proposal.district){
                    let districts=vm.$refs.proposal_apply.districts
                    let district_exists=false;
                    if(districts){
                        district_exists = [...districts.filter(district => district.value == vm.proposal.district)]
                    }
                    if(!district_exists || district_exists.length<1){
                        vm.proposal.district=null;
                        blank_fields.push(' You must select at least one District')
                    }
                }
             }

            if(blank_fields.length==0){
                return true;
            }
            else {
                return blank_fields;
            }
        },

        highlight_deficient_fields: function(deficient_fields){
            let vm = this;
            for (var deficient_field of deficient_fields) {
                $("#" + "id_"+deficient_field).css("color", 'red');
            }
        },

        deficientFields(){
            let vm=this;
            //console.log("I am here");
            let deficient_fields=[]
            $('.deficiency').each((i,d) => {
                if($(d).val() != ''){
                    var name=$(d)[0].name
                    var tmp=name.replace("-comment-field","")
                    deficient_fields.push(tmp);
                    //console.log('data', $("#"+"id_" + tmp))
                }
            });
            //console.log('deficient fields', deficient_fields);
            vm.highlight_deficient_fields(deficient_fields);
        },
        submit: function(){
            console.log('in submit');

            let vm = this;
            vm.form=document.forms.new_proposal;
            let formData = new FormData(vm.form);
            // Add apiary_sites data if needed
            formData = this.attach_apiary_sites_data(formData)

            let missing_data = vm.can_submit();
            if(missing_data!=true){
              swal({
                title: "Please fix following errors before submitting",
                text: missing_data,
                type:'error'
              })
            //vm.paySubmitting=false;
            return false;
            }

            var num_missing_fields = vm.validate()
            if (num_missing_fields > 0) {
                vm.highlight_missing_fields()
                var top = ($('#error').offset() || { "top": NaN }).top;
                $('html, body').animate({
                    scrollTop: top
                }, 1);
                return false;
            }

            // remove the confirm prompt when navigating away from window (on button 'Submit' click)
            vm.submitting = true;
            let swalTitle = "Submit Proposal";
            let swalText = "Are you sure you want to submit this proposal?";
            if (this.apiaryTemplateGroup) {
                swalTitle = "Submit Application";
                swalText = "Are you sure you want to submit this application?";
            }
            swal({
                title: swalTitle,
                text: swalText,
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Submit'
            }).then(async () => {
                console.log('in then()');
                vm.submittingProposal = true;
                // Only Apiary has an application fee
                //if (!vm.proposal.fee_paid && ['Apiary', 'Site Transfer'].includes(vm.proposal.application_type)) {
                if (['Apiary', 'Site Transfer'].includes(vm.proposal.application_type)) {
                    //if (this.submit_button_text === 'Pay and submit' && ['Apiary', 'Site Transfer'].includes(vm.proposal.application_type)) {
                    console.log('--- save and pay ---')
                    vm.save_and_redirect();
                } else {
                    /* just save and submit - no payment required (probably application was pushed back by assessor for amendment */
                    try {
                        console.log('http.post(submit)')
                        console.log('http.post: ' + helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/submit'))

                        const res = await vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/submit'),formData);
                        vm.proposal = res.body;
                        vm.$router.push({
                            name: 'submit_proposal',
                            params: { proposal: vm.proposal}
                        });
                    } catch (err) {
                        swal(
                            'Submit Error',
                            helpers.apiVueResourceError(err),
                            'error'
                        )
                    }
                    /*
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/submit'),formData).then(res=>{
                        vm.proposal = res.body;
                        vm.$router.push({
                            name: 'submit_proposal',
                            params: { proposal: vm.proposal}
                        });
                    },err=>{
                        swal(
                            'Submit Error',
                            helpers.apiVueResourceError(err),
                            'error'
                        )
                    });
                    */
                }
            },(error) => {
              vm.paySubmitting=false;
            });
            vm.submittingProposal= false;
        },
        // Apiary submission
        save_and_redirect: async function(e) {
            console.log('in save_and_redirect');
            this.isSaving = true;
            let vm = this;
            vm.form=document.forms.new_proposal;
            let formData = new FormData(vm.form);
            // Add apiary_sites data if needed
            if (this.proposal.application_type === 'Apiary') {
                formData = this.attach_apiary_sites_data(formData);
            }
            if (this.$refs.apiary_site_transfer && this.$refs.apiary_site_transfer.apiary_sites_local) {
                //console.log(this.$refs.apiary_site_transfer.site_transfer_apiary_sites)
                formData.append('apiary_sites_local', JSON.stringify(this.$refs.apiary_site_transfer.apiary_sites_local));
            }
            if (this.$refs.apiary_site_transfer && this.$refs.apiary_site_transfer.selectedLicenceHolder){
                //let selectedLicenceHolder = this.$refs.apiary_site_transfer.selectedLicenceHolder
                formData.append('selected_licence_holder', JSON.stringify(this.$refs.apiary_site_transfer.selectedLicenceHolder));
            }
            if (this.$refs.apiary_site_transfer && this.$refs.apiary_site_transfer.transfereeEmail){
                let transfereeEmail = this.$refs.apiary_site_transfer.transfereeEmail
                formData.append('transferee_email_text', transfereeEmail);
            }
            vm.$http.post(vm.proposal_submit_url, formData).then(
                res=>{
                    /* after the above save, redirect to the Django post() method in ApplicationFeeView */
                    vm.post_and_redirect(vm.application_fee_url, {'csrfmiddlewaretoken' : vm.csrf_token});
                },
                err=>{
                    if (err.body.type && err.body.type[0] === 'site_no_longer_available'){
                        console.log('1')
                        vm.display_site_no_longer_available_modal(err)
                    } else {
                        console.log('2')
                        helpers.processError(err)
                        vm.submittingProposal = false
                    }
                }
            );
            this.isSaving = false;
        },
        display_site_no_longer_available_modal: function(err){
            let vm = this
            let apiary_site_id = err.body.apiary_site_id[0]

            swal({
                title: "Vacant site no longer available",
                text: err.body.message[0],
                type: "warning",
                confirmButtonText: 'Remove the site from the application',
                allowOutsideClick: false
            }).then(function(){
                console.log('confirmed')
                vm.$refs.proposal_apiary.remove_apiary_site(apiary_site_id)
                console.log('confirmed2')
                // vm.save(false)
                vm.$http.post(vm.remove_apiary_site_url, {'apiary_site_id': apiary_site_id}).then(
                    res => {
                        console.log('res')
                        console.log(res);
                    },
                    err => {
                        console.log('err')
                        console.log(err);
                    },
                )
            });
        },
        post_and_redirect: function(url, postData) {
            console.log('in post_and_redirect')
            console.log('url: ' + url)
            /* http.post and ajax do not allow redirect from Django View (post method),
               this function allows redirect by mimicking a form submit.

               usage:  vm.post_and_redirect(vm.application_fee_url, {'csrfmiddlewaretoken' : vm.csrf_token});
            */
            var postFormStr = "<form method='POST' action='" + url + "'>";

            for (var key in postData) {
                if (postData.hasOwnProperty(key)) {
                    postFormStr += "<input type='hidden' name='" + key + "' value='" + postData[key] + "'>";
                }
            }
            postFormStr += "</form>";
            var formElement = $(postFormStr);
            $('body').append(formElement);
            $(formElement).submit();
        },
        incrementProposalComponentMapKey: function() {
                this.proposalComponentMapKey++;
            },
        refreshFromResponse:function(response){
            let vm = this;
            console.log('inside refresh');
            vm.original_proposal = helpers.copyObject(response.body);
            vm.proposal = helpers.copyObject(response.body);
            this.incrementProposalComponentMapKey();
            // vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
            
        },
    },
    mounted: function() {
        console.log('in mounted')

        let vm = this;
        vm.form = document.forms.new_proposal;
        window.addEventListener('beforeunload', vm.leaving);
        window.addEventListener('onblur', vm.leaving);
        // this.$nextTick(() => {
        //   console.log("I am here1");
        //         if(vm.hasAmendmentRequest){
        //           console.log("I am here2");
        //             vm.deficientFields();
        //         }
        //     });
    },
    updated: function(){
        let vm=this;
        this.$nextTick(() => {
            if(vm.hasAmendmentRequest){
                vm.deficientFields();
            }
        });
    },
    created: function() {
        console.log('in created')
        console.log('proposal_id: ' + this.$route.params.proposal_id)
        let proposal_id = this.$route.params.proposal_id

        let vm = this;
        Vue.http.get(`/api/proposal/${ proposal_id }.json`).then(
            res => {
                vm.loading.push('fetching proposal')
                vm.proposal = res.body;
                console.log('vm.proposal')
                console.log(vm.proposal)
                vm.loading.splice('fetching proposal', 1);
                vm.setdata(vm.proposal.readonly);

                Vue.http.get(helpers.add_endpoint_json(api_endpoints.proposals, proposal_id + '/amendment_request')).then((res) => {
                    vm.setAmendmentData(res.body);
                },
                err => {
                    console.log(err);
                });
            },
            err => {
                console.log(err);
            }
        );
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
        },err=>{
        console.log(err);
        });
    },

    beforeRouteEnter: function(to, from, next) {
        console.log('in beforeRouteEnter')
        console.log('id: ' + to.params.proposal_id)
    }
}
</script>

<style lang="css">
.payment-description-total-fee {
    font-weight: bold;
    font-size: 1.3em;
}
.payment-description-title {
    font-weight: bold;
}
.no-padding {
    padding: 0 !important;
}
.payment-details-buttons {
    display: flex;
    align-items: center;
}
#overlay {
    width: 100%;
    height: 100%;
    position: fixed;
    left: 0px;
    top: 0px;
    background-color:#000;
    opacity: .25;
    z-index: 2000;
}
</style>
