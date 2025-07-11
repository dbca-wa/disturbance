<template lang="html">
    <div id="proposedIssuanceApproval">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <template v-if="is_local">
                proposed_apiary_issuance.vue
            </template>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="approvalForm">
                        <!-- <alert v-if="isApprovalLevelDocument" type="warning"><strong>{{warningString}}</strong></alert> -->
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">

                            <div v-if="!siteTransferApplication">
                                <div class="form-group">
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label v-if="processing_status == 'With Approver'" class="control-label pull-left"  for="Name">Start Date</label>
                                            <label v-else class="control-label pull-left"  for="Name">Proposed Start Date</label>
                                        </div>
                                        <div class="col-sm-9">
                                            <template v-if="!startDateCanBeModified">
                                                {{ approvalStartDateDisplay }}
                                            </template>
                                            <template v-else>
                                                <div class="input-group date" ref="start_date" style="width: 70%;">
                                                    <input type="text" class="form-control" name="start_date" placeholder="DD/MM/YYYY" v-model="approval.start_date">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </template>
                                        </div>
                                    </div>
                                    <div class="row" v-show="showstartDateError">
                                        <alert  class="col-sm-12" type="danger"><strong>{{startDateErrorString}}</strong></alert>
                                    </div>
                                </div>

                                <div class="form-group">
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label v-if="processing_status == 'With Approver'" class="control-label pull-left"  for="Name">Expiry Date</label>
                                            <label v-else class="control-label pull-left"  for="Name">Proposed Expiry Date</label>
                                        </div>
                                        <div class="col-sm-9">
                                            <template v-if="!expiryDateCanBeModified">
                                                {{ approvalExpiryDateDisplay }}
                                            </template>
                                            <template v-else>
                                                <div class="input-group date" ref="due_date" style="width: 70%;">
                                                    <input type="text" class="form-control" name="due_date" placeholder="DD/MM/YYYY" v-model="approval.expiry_date" :readonly="is_amendment">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </template>
                                        </div>
                                    </div>
                                    <div class="row" v-show="showtoDateError">
                                        <alert  class="col-sm-12" type="danger"><strong>{{toDateErrorString}}</strong></alert>
                                    </div>
                                </div>
                            </div>
                            <div v-else>
                                <div v-if="creatingSiteTransferTargetApproval" class="form-group">
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label v-if="processing_status == 'With Approver'" class="control-label pull-left"  for="Name">Start Date</label>
                                            <label v-else class="control-label pull-left"  for="Name">Proposed Start Date</label>
                                        </div>
                                        <div class="col-sm-9">
                                            <template>
                                                <div class="input-group date" ref="start_date" style="width: 70%;">
                                                    <input type="text" class="form-control" name="start_date" placeholder="DD/MM/YYYY" v-model="approval.start_date">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </template>
                                        </div>
                                    </div>
                                    <div class="row" v-show="showstartDateError">
                                        <alert  class="col-sm-12" type="danger"><strong>{{startDateErrorString}}</strong></alert>
                                    </div>
                                </div>

                                <div v-if="creatingSiteTransferTargetApproval" class="form-group">
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label v-if="processing_status == 'With Approver'" class="control-label pull-left"  for="Name">Expiry Date</label>
                                            <label v-else class="control-label pull-left"  for="Name">Proposed Expiry Date</label>
                                        </div>
                                        <div class="col-sm-9">
                                            <template>
                                                <div class="input-group date" ref="due_date" style="width: 70%;">
                                                    <input type="text" class="form-control" name="due_date" placeholder="DD/MM/YYYY" v-model="approval.expiry_date">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </template>
                                        </div>
                                    </div>
                                    <div class="row" v-show="showtoDateError">
                                        <alert  class="col-sm-12" type="danger"><strong>{{toDateErrorString}}</strong></alert>
                                    </div>

                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label v-if="processing_status == 'With Approver'" class="control-label pull-left"  for="Name">Details</label>
                                        <label v-else class="control-label pull-left"  for="Name">Proposed Details</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <textarea name="approval_details" class="form-control" style="width:70%;" v-model="approval.details"></textarea>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label v-if="processing_status == 'With Approver'" class="control-label pull-left"  for="Name">BCC email</label>
                                        <label v-else class="control-label pull-left"  for="Name">Proposed BCC email</label>
                                    </div>
                                    <div class="col-sm-9">
                                            <input type="text" class="form-control" name="approval_cc" style="width:70%;" ref="bcc_email" v-model="approval.cc_email">
                                    </div>
                                </div>
                            </div>

<!--
                            <pre>{{ issuance_details }}</pre>
                                    <pre>{{ site.properties }}</pre>
                                    <pre>{{ site.properties.licensed_site }}</pre>
-->
                            <div v-for="(site, index) in apiary_sites_updated_ordered">
                                <div v-if="!site.properties.licensed_site">
				    <div class="col-md-12">
					<div class="row">
					    <div class="panel panel-default">
						<div class="panel-heading">
						    <h2 class="panel-title">Permit details for site {{ site.id }}
							<a class="panelClicker" :href="'#details-info-'+site.id" data-toggle="collapse"  :data-parent="'#userInfo-'+site.id" expanded="false" :aria-controls="'details-info-'+site.id">
							    <span class="glyphicon glyphicon-chevron-down pull-right "></span>
							</a>
						    </h2>
						</div>

						<div class="panel-body panel-collapse collapse" :id="'details-info-'+site.id">
						    <div class="row">
						        <div class="col-sm-12">
							    <div class="form-group">
								<div class="col-sm-4">
								    <label class="control-label pull-left"  for="name">Batch Number</label><br>
								    <input type="text" class="form-control" name="site_batch_no" style="width:100%;" ref="batch_no"
                                                                        v-model="site.properties.batch_no"
                                                                    >
								</div>
<!--
                                                                        v-model="issuance_details[index].batch_no"
                                                                        v-model="site.properties.issuance_details.batch_no"
                                    <pre>{{ site.properties.issuance_details }}</pre>
								<div class="col-sm-4">
								    <label class="control-label pull-left"  for="name">Batch Number</label><br>
								    <input type="text" class="form-control" name="approval_batch_no" style="width:100%;" ref="batch_no"
                                                                        v-model="issuance_details.batch_no"
                                                                    >
								</div>
-->

<!--
								<div class="col-sm-4">
								  <label class="control-label pull-left" style="text-align:left" for="name">Conservation and Parks Commission</label>
								  <div class="input-group date" ref="site_cpc_date" style="width: 70%;">
								    <input type="text" class="form-control" name="site_cpc_date" placeholder="DD/MM/YYYY" v-model="site.properties.approval_cpc_date">
								    <span class="input-group-addon">
									<span class="glyphicon glyphicon-calendar"></span>
								    </span>
								  </div>
								</div>
-->

								<div class="col-sm-4">
								    <label class="control-label pull-left" style="text-align:left" for="name">Conservation and Parks Commission</label>
								    <input type="text" class="form-control" name="site_cpc_date" placeholder="YYYY-MM-DD" style="width:100%;" ref="cpc_date" 
                                                                        v-model="site.properties.approval_cpc_date"
                                                                    >
								</div>
								<div class="col-sm-4">
								    <label class="control-label pull-left" style="text-align:left" for="name">Minister for Environment or Delegate</label>
								    <input type="text" class="form-control" name="site_minister_date" placeholder="YYYY-MM-DD" style="width:100%;" ref="minister_date" 
                                                                        v-model="site.properties.approval_minister_date"
                                                                    >
								</div>
							    </div>

<!--
-->
							    <div class="form-group">
								<div class="col-sm-4">
								    <label class="control-label pull-left"  for="name">Map Reference</label><br>
								    <input type="text" class="form-control" name="site_map_ref" style="width:100%;" ref="map_ref" v-model="site.properties.map_ref">
								</div>
								<div class="col-sm-4">
								    <label class="control-label pull-left" style="text-align:left" for="name">Forest Block</label>
								    <input type="text" class="form-control" name="site_forest_block" style="width:100%;" ref="forest_block" v-model="site.properties.forest_block">
								</div>
								<div class="col-sm-4">
								    <label class="control-label pull-left" style="text-align:left" for="name">COG</label>
								    <input type="text" class="form-control" name="site_cog" style="width:100%;" ref="cog" v-model="site.properties.cog">
								</div>
							    </div>

							    <div class="form-group">
								<div class="col-sm-4">
								    <label class="control-label pull-left"  for="name">Apiary Zone</label><br>
								    <input type="text" class="form-control" name="site_zone" style="width:100%;" ref="zone" v-model="site.properties.zone">
								</div>
								<div class="col-sm-4">
								    <label class="control-label pull-left" style="text-align:left" for="name">Water Catchment Area</label>
								    <input type="text" class="form-control" name="site_catchment" style="width:100%;" ref="catchment" v-model="site.properties.catchment">
								</div>
								<div class="col-sm-4">
								    <label class="control-label pull-left" style="text-align:left" for="name">Nearest Road/Track</label>
								    <input type="text" class="form-control" name="site_roadtrack" style="width:100%;" ref="roadtrack" v-model="site.properties.roadtrack">
								</div>
							    </div>

							    <div class="form-group">
								<div class="col-sm-3">
								    <label class="control-label pull-left"  for="Name">DRA Permit Required</label>
								</div>
								<div class="col-sm-1">
								    <input type="checkbox" class="form-control" name="site_dra_permit" style="width:50%;" ref="dra_permit" v-model="site.properties.dra_permit">
								</div>
							    </div>

						        </div>
					            </div>
				  	        </div>

					    </div>

                                        </div>
                                    </div>
                                </div>
                            </div>


<!--
                            <pre>{{ apiary_sites_updated }}</pre>
                <div v-for="site in apiary_sites_updated">
                    <div v-if="site.properties.licensed_site" style="border">
                        {{ site.id }}: {{ site.properties.licensed_site}}
                    </div>
                </div>
-->


                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <div v-if="!siteTransferApplication">
                                            <label v-if="submitter_email && applicant_email" class="control-label pull-left"  for="Name">After approving this application, the apiary authority will be emailed to {{proposalNotificationList}}.</label>
                                            <label v-else class="control-label pull-left"  for="Name">After approving this application, licence will be emailed to {{submitter_email}}.</label>
                                        </div>
                                        <div v-else>
                                            <label class="control-label pull-left">After approving this application, the originating apiary authority will be emailed to {{originatingLicenceRecipients}}.</label>
                                            <label class="control-label pull-left">After approving this application, the target apiary authority will be emailed to {{targetLicenceRecipients}}.</label>
                                        </div>
                                    </div>

                                </div>
                            </div>
                        </div>
                    </form>
                </div>

                <template v-if="proposal && proposal.proposal_apiary.apiary_sites">
                </template>

            </div>
            <div v-if="can_preview">
                <div v-if="siteTransferApplication">
                    <div>
                        Click <a href="#" @click.prevent="preview_originating_approval">here</a> to preview the originating licence letter.
                    </div>
                    <div>
                        Click <a href="#" @click.prevent="preview_target_approval">here</a> to preview the target licence letter.
                    </div>
                </div>
                <div v-else>
                    Click <a href="#" @click.prevent="preview">here</a> to preview the licence letter.
                </div>
            </div>

<!--
            <div>
                <div v-for="site in apiary_sites_updated">
                    <div v-if="site.properties.licensed_site">
                        {{ site }}
                    </div>
                </div>
            </div>
-->

            <div slot="footer">
                <button type="button" v-if="issuingApproval" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Processing</button>
                <span v-else-if="ok_button_disabled" class="d-inline-block" tabindex="0" data-toggle="tooltip" title="Please select at least one site to issue">
                    <button type="button" style="pointer-events: none;" class="btn btn-default" @click="ok" disabled>Ok</button>
                </span>
                <button v-else type="button" class="btn btn-default" @click="ok" >Ok</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import {v4 as uuidv4} from 'uuid';
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import {helpers,api_endpoints} from "@/utils/hooks.js"
import moment from 'moment'
export default {
    name:'ProposedApiaryIssuance',
    components:{
        modal,
        alert,
    },
    props:{
        proposal_apiary_id: {
            type: Number,
            required: true
        },
        proposal_id: {
            type: Number,
            required: true
        },
        proposal: {
            type: Object,
            default: null,
        },
        processing_status: {
            type: String,
            required: true
        },
        proposal_type: {
            type: String,
            required: true
        },
        isApprovalLevelDocument: {
            type: Boolean,
            required: true
        },
        submitter_email: {
            type: String,
            required: true
        },
        applicant_email: {
            type: String,
            //default: ''
        },
    },
    data:function () {
        let vm = this;
        return {
            //furtherInfo: "further-info-"+vm._uid,
            isModalOpen:false,
            form:null,
            approval: {},
            state: 'proposed_approval',
            issuingApproval: false,
            validation_form: null,
            errors: false,
            toDateError:false,
            startDateError:false,
            errorString: '',
            toDateErrorString:'',
            startDateErrorString:'',
            successString: '',
            success:false,
            apiary_sites_updated: null,
            apiary_licensed_sites_updated: null,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            warningString: 'Please attach Level of Approval document before issuing Approval',
            component_site_selection_key: '',
            num_of_sites_selected: 0,
            is_local: helpers.is_local(),
            issuance_details: [
		{
                    batch_no: null,
                }
	    ],
        }
    },
    computed: {
        approvalStartDateDisplay: function() {
            let displayDate = null;
            if (this.proposal && this.proposal.approval && this.proposal.approval.start_date) {
                displayDate = moment(this.proposal.approval.start_date, 'YYYY-MM-DD').format('DD/MM/YYYY');
            }
            return displayDate;
        },
        approvalExpiryDateDisplay: function() {
            let displayDate = null;
            if (this.proposal && this.proposal.approval && this.proposal.approval.expiry_date) {
                displayDate = moment(this.proposal.approval.expiry_date, 'YYYY-MM-DD').format('DD/MM/YYYY');
            }
            return displayDate;
        },
        proposalNotificationList: function (){
            let returnVal = `${this.submitter_email} and ${this.applicant_email}.`
            if (this.submitter_email === this.applicant_email){
                returnVal = `${this.submitter_email}.`
            }
            return returnVal;
        },
        ok_button_disabled: function(){
            if (this.num_of_sites_selected > 0){
                return false
            }
            return true
        },
        startDateCanBeModified: function() {
            let returnVal = false;
            if (this.proposal && this.proposal.approval && this.proposal.approval.reissued) {
                returnVal = true;
            } else if (this.proposal && !this.proposal.approval) {
                returnVal = true;
            }
            return returnVal;
        },
        expiryDateCanBeModified: function() {
            let returnVal = false;
            if (this.proposal && this.proposal.approval && this.proposal.approval.reissued) {
                returnVal = true;
            } else if (this.proposal && !this.proposal.approval) {
                returnVal = true;
            } else if (this.proposal && this.proposal.proposal_type === 'Renewal') {
                returnVal = true;
            }
            return returnVal;
        },
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        showtoDateError: function() {
            var vm = this;
            return vm.toDateError;
        },
        showstartDateError: function() {
            var vm = this;
            return vm.startDateError;
        },
        title: function(){
            //return this.processing_status == 'With Approver' ? 'Issue Application' : 'Propose to issue licence';
            return this.processing_status == 'With Approver' ? 'Issue Application' : 'Propose to Issue';
        },
        is_amendment: function(){
            return this.proposal_type == 'Amendment' ? true : false;
        },
        csrf_token: function() {
          return helpers.getCookie('csrftoken')
        },
        can_preview: function(){
            return this.processing_status == 'With Approver' ? true : false;
        },
        preview_licence_url: function() {
          return (this.proposal_id) ? `/preview/licence-pdf/${this.proposal_id}` : '';
        },
        apiary_sites_prop: function() {
            let apiary_sites = [];
            if (this.proposal.application_type === 'Site Transfer') {
                for (let site of this.proposal.proposal_apiary.transfer_apiary_sites) {
                    /*
                    if (site.selected) {
                        apiary_sites.push(site.apiary_site);
                    }
                    */
                    apiary_sites.push(site.apiary_site);
                }
            } else {
                apiary_sites = this.proposal.proposal_apiary.apiary_sites;
            }
            return apiary_sites;
        },
        /*
        showColCheckbox: function() {
            let checked = true;
            if (this.proposal.application_type === 'Site Transfer') {
                checked = false;
            }
            return checked;
        },
        */
        siteTransferApplication: function() {
            let siteTransfer = false;
            if (this.proposal.application_type === 'Site Transfer') {
                siteTransfer = true;
            }
            return siteTransfer;
        },
        creatingSiteTransferTargetApproval: function() {
            let creatingApproval = false;
            if (!this.siteTransferTargetApprovalExists || (this.proposal.proposal_apiary && this.proposal.proposal_apiary.transferee_id)) {
                creatingApproval = true;
            }
            return creatingApproval;
        },
        siteTransferTargetApprovalExists: function() {
            let targetApprovalExists = false;
            if (this.proposal.proposal_apiary && this.proposal.proposal_apiary.target_approval_id) {
                targetApprovalExists = true;
            }
            return targetApprovalExists;
        },
        targetLicenceRecipients: function() {
            if (this.proposal.proposal_apiary && this.proposal.proposal_apiary.transferee_email_text){
                return  this.proposal.proposal_apiary.transferee_email_text;
            }
        },
        originatingLicenceRecipients: function() {
            if (this.proposal.proposal_apiary && this.proposal.proposal_apiary.transferee_email_text && this.proposal.applicant){
                return  this.proposal.applicant.email;
            }
        },
        apiary_sites_updated_ordered: function () {
            // adding ordering here on client-side, because iserver-side serializer is ordered for 'apiary_site_id'
            // to allow for PDF ordered output of permits and licences (ApprovalSerializerForLicenceDoc)
            return _.orderBy(this.apiary_sites_updated, 'id')
        },

    },
    watch: {

    },
    methods:{

        //detailsInfo: function(site){
        //    return 'details-info-' + site.id
        //},

        featureGeometryUpdated: function(feature){
            for (let i=0; i<this.apiary_sites_updated.length; i++){
                if (this.apiary_sites_updated[i].id == feature.id){
                    this.apiary_sites_updated[i].coordinates_moved = feature.coordinates
                }
            }
        },
        apiarySitesUpdated: function(apiary_sites) {
            this.apiary_sites_updated = apiary_sites
            //this.proposal.proposal_apiary.apiary_sites = JSON.parse(JSON.stringify(apiary_sites))

            // Update this.num_of_sites_selected
            let temp = 0
            for (let i=0; i<apiary_sites.length; i++){
                if (apiary_sites[i].checked){
                    temp += 1
                }
                if (apiary_sites[i].checked){
                    temp += 1
                }
            }
            this.num_of_sites_selected = temp
        },
        setApiarySiteCheckedStatuses: function() {
            if(this.proposal && this.proposal.proposal_apiary){
                for (let i=0; i<this.proposal.proposal_apiary.apiary_sites.length; i++){
                    this.proposal.proposal_apiary.apiary_sites[i].checked = (this.proposal.proposal_apiary.apiary_sites[i].properties.workflow_selected_status || this.proposal.proposal_apiary.apiary_sites[i].properties.status === 'approved')
                    //this.proposal.proposal_apiary.apiary_sites[i].checked = (this.proposal.proposal_apiary.apiary_sites[i].properties.workflow_selected_status)
                }
            }
        },
        setApiarySiteCheckedStatusesSiteTransfer: function() {
            if(this.proposal && this.proposal.proposal_apiary){
                for (let i=0; i<this.proposal.proposal_apiary.transfer_apiary_sites.length; i++){
                    this.proposal.proposal_apiary.transfer_apiary_sites[i].apiary_site.checked = this.proposal.proposal_apiary.transfer_apiary_sites[i].internal_selected
                }
            }
        },

        forceToRefreshMap: function() {
        },
        /*
        preview:function () {
            let vm =this;
            let formData = new FormData(vm.form)
            if (this.proposal.approval && this.proposal.approval.start_date && this.proposal.approval.expiry_date) {
                formData.append('start_date', moment(this.proposal.approval.start_date, 'YYYY-MM-DD').format('DD/MM/YYYY'));
                formData.append('due_date', moment(this.proposal.approval.expiry_date, 'YYYY-MM-DD').format('DD/MM/YYYY'));
            }
            // convert formData to json
            let jsonObject = {};
            for (const [key, value] of formData.entries()) {
                jsonObject[key] = value;
            }
            vm.post_and_redirect(vm.preview_licence_url, {'csrfmiddlewaretoken' : vm.csrf_token, 'formData': JSON.stringify(jsonObject)});
        },
        */
        preview:function () {
            //this.sendData(true);
            this.previewData();
        },
        preview_originating_approval:function () {
            this.previewData('originating');
        },
        preview_target_approval:function () {
            this.previewData('target')
        },
        /*
        preview_originating_approval:function () {
            let vm =this;
            let formData = new FormData(vm.form)
            if (this.proposal.approval && this.proposal.approval.start_date && this.proposal.approval.expiry_date) {
                formData.append('start_date', moment(this.proposal.approval.start_date, 'YYYY-MM-DD').format('DD/MM/YYYY'));
                formData.append('due_date', moment(this.proposal.approval.expiry_date, 'YYYY-MM-DD').format('DD/MM/YYYY'));
            }
            // convert formData to json
            let jsonObject = {};
            for (const [key, value] of formData.entries()) {
                jsonObject[key] = value;
            }
            jsonObject['originating_approval_id'] = this.proposal.proposal_apiary.originating_approval_id;
            vm.post_and_redirect(vm.preview_licence_url, {'csrfmiddlewaretoken' : vm.csrf_token, 'formData': JSON.stringify(jsonObject)});
        },
        preview_target_approval:function () {
            let vm =this;
            let formData = new FormData(vm.form)
            if (this.proposal.approval && this.proposal.approval.start_date && this.proposal.approval.expiry_date) {
                formData.append('start_date', moment(this.proposal.approval.start_date, 'YYYY-MM-DD').format('DD/MM/YYYY'));
                formData.append('due_date', moment(this.proposal.approval.expiry_date, 'YYYY-MM-DD').format('DD/MM/YYYY'));
            }
            // convert formData to json
            let jsonObject = {};
            for (const [key, value] of formData.entries()) {
                jsonObject[key] = value;
            }
            jsonObject['target_approval_id'] = this.proposal.proposal_apiary.target_approval_id;
            vm.post_and_redirect(vm.preview_licence_url, {'csrfmiddlewaretoken' : vm.csrf_token, 'formData': JSON.stringify(jsonObject)});
        },
        */
        post_and_redirect: function(url, postData) {
            /* http.post and ajax do not allow redirect from Django View (post method),
               this function allows redirect by mimicking a form submit.
               usage:  vm.post_and_redirect(vm.application_fee_url, {'csrfmiddlewaretoken' : vm.csrf_token});
            */
            var postFormStr = "<form method='POST' target='_blank' name='Preview Licence' action='" + url + "'>";
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
        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
                //vm.$router.push({ path: '/internal' });
            }
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            this.isModalOpen = false;
            this.approval = {};
            this.errors = false;
            this.toDateError = false;
            this.startDateError = false;
            $('.has-error').removeClass('has-error');
            if (this.$refs.due_date) {
                $(this.$refs.due_date).data('DateTimePicker').clear();
            }
            if (this.$refs.start_date) {
                $(this.$refs.start_date).data('DateTimePicker').clear();
            }
            this.validation_form.resetForm();
        },
        fetchContact: function(id){
            let vm = this;
            vm.$http.get(api_endpoints.contact(id)).then((response) => {
                vm.contact = response.body; vm.isModalOpen = true;
            },(error) => {
                console.log(error);
            } );
        },
        previewData:function(originating_target=null){
            //let previewWindow = window.open(' ', '_blank');
            let previewWindow = window.open();

            this.approval.preview = true;
            if (originating_target) {
                this.approval.originating_target = originating_target;
            }
            this.approval.apiary_sites = this.apiary_sites_updated
            if (!this.startDateCanBeModified && !this.siteTransferApplication){
                // There is an existing licence. Therefore start_date and expiry_date are fixed to that dates
                this.approval.start_date = moment(this.proposal.approval.start_date, 'YYYY-MM-DD').format('DD/MM/YYYY')
            }
            if (!this.expiryDateCanBeModified && !this.siteTransferApplication){
                // There is an existing licence. Therefore start_date and expiry_date are fixed to that dates
                this.approval.expiry_date = moment(this.proposal.approval.expiry_date, 'YYYY-MM-DD').format('DD/MM/YYYY')
            }
            if (!this.approval.start_date) {
                delete this.approval.start_date;
            }
            if (!this.approval.expiry_date) {
                delete this.approval.expiry_date;
            }
            let approval = JSON.parse(JSON.stringify(this.approval)); // Deep copy

            this.issuingApproval = true;
            if (this.state == 'final_approval'){
                /*
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposal_apiary,vm.proposal_apiary_id+'/final_approval'),JSON.stringify(approval),{
                        emulateJSON:true,
                }).then((response) => {
                        //const blob = new Blob([response.body],{type: 'image/pdf'});
                        const pdfBlob = new Blob([response.body],{type: 'application/pdf'});
                        const objectURL = window.URL.createObjectURL(pdfBlob);
                        let link = document.createElement('a');
                        link.href = objectURL;
                        link.download="file.pdf";
                        link.click();
                    },(error)=>{
                        vm.errors = true;
                        //vm.issuingApproval = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
                */
                fetch(helpers.add_endpoint_json(api_endpoints.proposal_apiary,this.proposal_apiary_id+'/final_approval'), {
                    method: 'POST',
                    body: JSON.stringify(approval),
                    //body: this.approval,
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": this.csrf_token,
                    },
                })
                    /*
                    .then((response) => {
                        previewWindow.document.write(response);
                        previewWindow.focus();
                    });
                    */

                    .then(response => response.blob())
                    .then(function(myBlob) {
                        const objectURL = URL.createObjectURL(myBlob);
                        previewWindow.location.href = objectURL;
                    });

            }
            this.approval.preview = false;
            this.issuingApproval = false;
        },
        //sendData:function(preview=false,originating_target=null){
        sendData:function(preview=false){
            let vm = this;
            vm.errors = false;
            /*
            if (preview) {
                vm.approval.preview = preview;
            }
            */
            //vm.approval.apiary_sites = vm.proposal.proposal_apiary.apiary_sites
            vm.approval.apiary_sites = vm.apiary_sites_updated
            if (!this.startDateCanBeModified  && !this.siteTransferApplication){
                // There is an existing licence. Therefore start_date and expiry_date are fixed to that dates
                this.approval.start_date = moment(this.proposal.approval.start_date, 'YYYY-MM-DD').format('DD/MM/YYYY')
            }
            if (!this.expiryDateCanBeModified && !this.siteTransferApplication){
                // There is an existing licence. Therefore start_date and expiry_date are fixed to that dates
                this.approval.expiry_date = moment(this.proposal.approval.expiry_date, 'YYYY-MM-DD').format('DD/MM/YYYY')
            }
            if (!this.approval.start_date) {
                delete this.approval.start_date;
            }
            if (!this.approval.expiry_date) {
                delete this.approval.expiry_date;
            }
            let approval = JSON.parse(JSON.stringify(vm.approval)); // Deep copy

            vm.issuingApproval = true;
            if (vm.state == 'proposed_approval'){
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals, vm.proposal.id+'/proposed_approval'),JSON.stringify(approval),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.issuingApproval = false;
                        vm.close();
                        vm.$emit('refreshFromResponse',response);
                        vm.$router.push({ path: '/internal' }); //Navigate to dashboard page after Propose issue.

                    },(error)=>{
                        vm.errors = true;
                        vm.issuingApproval = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
            }
            else if (vm.state == 'final_approval' && preview){
                /*
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposal_apiary,vm.proposal_apiary_id+'/final_approval'),JSON.stringify(approval),{
                        emulateJSON:true,
                }).then((response) => {
                        //const blob = new Blob([response.body],{type: 'image/pdf'});
                        const pdfBlob = new Blob([response.body],{type: 'application/pdf'});
                        const objectURL = window.URL.createObjectURL(pdfBlob);
                        let link = document.createElement('a');
                        link.href = objectURL;
                        link.download="file.pdf";
                        link.click();
                    },(error)=>{
                        vm.errors = true;
                        //vm.issuingApproval = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
                */
                fetch(helpers.add_endpoint_json(api_endpoints.proposal_apiary,vm.proposal_apiary_id+'/final_approval'), {
                    method: 'POST',
                    body: JSON.stringify(approval),
                    //body: this.approval,
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": vm.csrf_token,
                    },
                })
                    .then(response => response.blob())
                    .then(function(myBlob) {
                        //const blob = new Blob([response.body],{type: 'image/pdf'});
                        //const blob = new Blob([response.body],{type: 'application/pdf'});
                        const objectURL = URL.createObjectURL(myBlob);
                        let link = document.createElement('a');
                        link.href = objectURL;
                        link.download="file.pdf";
                        link.click();
                        vm.issuingApproval = false;
                    });

            }
            else if (vm.state == 'final_approval'){
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposal_apiary,vm.proposal_apiary_id+'/final_approval'),JSON.stringify(approval),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.issuingApproval = false;
                        vm.close();
                        vm.$emit('refreshFromResponse',response);
                    },(error)=>{
                        vm.errors = true;
                        vm.issuingApproval = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
            }
        },
        addFormValidations: function() {
            let vm = this;
            let rulesVar = {}
            if (this.siteTransferApplication) {
                rulesVar = {
                    approval_details:"required",
                }
            } else {
                rulesVar = {
                    start_date:"required",
                    due_date:"required",
                    approval_details:"required",
                }
            }

            vm.validation_form = $(vm.form).validate({
                rules: rulesVar,
                messages: {
                },
                showErrors: function(errorMap, errorList) {
                    $.each(this.validElements(), function(index, element) {
                        var $element = $(element);
                        $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
                    });
                    // destroy tooltips on valid elements
                    $("." + this.settings.validClass).tooltip("destroy");
                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: "focus"
                            })
                            .attr("data-original-title", error.message)
                            .parents('.form-group').addClass('has-error');
                    }
                }
            });
       },
       eventListeners:function () {
            let vm = this;
            // Initialise Date Picker
            $(vm.$refs.site_cpc_date).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.site_cpc_date).on('dp.change', function(e){
                console.log('e: ' + e)
            });

            $(vm.$refs.due_date).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.due_date).on('dp.change', function(e){
                if ($(vm.$refs.due_date).data('DateTimePicker').date()) {
                    //let proposalApprovalStartDate = moment(vm.proposal.approval.start_date, 'YYYY-MM-DD').format('DD/MM/YYYY')
                    let proposalApprovalStartDate = vm.proposal.approval && vm.proposal.approval.start_date ?
                        moment(vm.proposal.approval.start_date, 'YYYY-MM-DD') :
                        null;
                    let startDate = Object.keys($(vm.$refs.start_date)).length ?
                        $(vm.$refs.start_date).data('DateTimePicker').date() :
                        proposalApprovalStartDate;
                    if ($(vm.$refs.due_date).data('DateTimePicker').date() < startDate) {
                            vm.toDateError = true;
                            vm.toDateErrorString = 'Please select Expiry date that is after Start date';
                            vm.approval.expiry_date = ""
                    }
                    else{
                        vm.toDateError = false;
                        vm.toDateErrorString = '';
                        vm.approval.expiry_date =  e.date.format('DD/MM/YYYY');
                    }
                    //vm.approval.expiry_date =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.due_date).data('date') === "") {
                    vm.approval.expiry_date = "";
                }
             });
            $(vm.$refs.start_date).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.start_date).on('dp.change', function(e){
                if ($(vm.$refs.start_date).data('DateTimePicker').date()) {

                    if (($(vm.$refs.due_date).data('DateTimePicker').date()!= null)&& ($(vm.$refs.due_date).data('DateTimePicker').date() < $(vm.$refs.start_date).data('DateTimePicker').date())){
                        vm.startDateError = true;
                        vm.startDateErrorString = 'Please select Start date that is before Expiry date';
                        vm.approval.start_date = ""
                    }
                    else{
                        vm.startDateError = false;
                        vm.startDateErrorString = '';
                        vm.approval.start_date =  e.date.format('DD/MM/YYYY');
                    }

                    //vm.approval.start_date =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.start_date).data('date') === "") {
                    vm.approval.start_date = "";
                }
             });
             /*
             $(document).ready(function() {
                 $('[data-toggle="tooltip"]').tooltip();
             });
             */
       }
   },
    mounted:function () {
        let vm =this;
        vm.form = document.forms.approvalForm;
        vm.addFormValidations();
        this.$nextTick(()=>{
            vm.eventListeners();
        });
        if (this.proposal.application_type === 'Site Transfer') {
            this.setApiarySiteCheckedStatusesSiteTransfer();
        } else {
            this.setApiarySiteCheckedStatuses();
        }
        this.component_site_selection_key = uuidv4()
    }
}
</script>

<style lang="css">
.boxed {
  border: 1px solid black ;
}
</style>

<!--
						<div class="col-sm-12">
						    <div class="form-group">
							<div class="row">
							    <div class="col-sm-4">
								<label class="control-label pull-left"  for="Name">Batch Number</label>
							    </div>
							    <div class="col-sm-8">
								    <input type="text" class="form-control" name="approval_batch_no" style="width:70%;" ref="batch_no" v-model="approval.batch_no">
							    </div>
							</div>
						    </div>

						    <div class="form-group">
							<div class="row">
							    <div class="col-sm-4">
								<label class="control-label pull-left" style="text-align:left" for="Name">Conservation and Parks Commission</label>
							    </div>
							    <div class="col-sm-8">
								    <input type="text" class="form-control" name="approval_cpc_date" style="width:70%;" ref="cpc_date" v-model="approval.cpc_date">
							    </div>
							</div>
						    </div>

						    <div class="form-group">
							<div class="row">
							    <div class="col-sm-4">
								<label class="control-label pull-left" style="text-align:left" for="Name">Minister for Environment or Delegate</label>
							    </div>
							    <div class="col-sm-8">
								    <input type="text" class="form-control" name="approval_minister_date" style="width:70%;" ref="minister_date" v-model="approval.minister_date">
							    </div>
							</div>
						    </div>


						    <div class="form-group">
							<div class="row">
							    <div class="col-sm-4">
								<label class="control-label pull-left"  for="Name">Map Reference</label>
							    </div>
							    <div class="col-sm-8">
								    <input type="text" class="form-control" name="approval_map_ref" style="width:70%;" ref="map_ref" v-model="approval.map_ref">
							    </div>
							</div>
						    </div>

						    <div class="form-group">
							<div class="row">
							    <div class="col-sm-4">
								<label class="control-label pull-left"  for="Name">Forest Block</label>
							    </div>
							    <div class="col-sm-8">
								    <input type="text" class="form-control" name="approval_forest_block" style="width:70%;" ref="forest_block" v-model="approval.forest_block">
							    </div>
							</div>
						    </div>

						    <div class="form-group">
							<div class="row">
							    <div class="col-sm-4">
								<label class="control-label pull-left"  for="Name">COG Map Reference</label>
							    </div>
							    <div class="col-sm-8">
								    <input type="text" class="form-control" name="approval_cog" style="width:70%;" ref="cog" v-model="approval.cog">
							    </div>
							</div>
						    </div>
						    <div class="form-group">
							<div class="row">
							    <div class="col-sm-4">
								<label class="control-label pull-left"  for="Name">Nearest Road/Track</label>
							    </div>
							    <div class="col-sm-8">
								    <input type="text" class="form-control" name="approval_roadtrack" style="width:70%;" ref="roadtrack" v-model="approval.roadtrack">
							    </div>
							</div>
						    </div>
						    <div class="form-group">
							<div class="row">
							    <div class="col-sm-4">
								<label class="control-label pull-left"  for="Name">Apiary Zone</label>
							    </div>
							    <div class="col-sm-8">
								    <input type="text" class="form-control" name="approval_zone" style="width:70%;" ref="zone" v-model="approval.zone">
							    </div>
							</div>
						    </div>
						    <div class="form-group">
							<div class="row">
							    <div class="col-sm-4">
								<label class="control-label pull-left"  for="Name">Water Catchment Area</label>
							    </div>
							    <div class="col-sm-8">
								    <input type="text" class="form-control" name="approval_catchment" style="width:70%;" ref="catchment" v-model="approval.catchment">
							    </div>
							</div>
						    </div>
						    <div class="form-group">
							<div class="row">
							    <div class="col-sm-4">
								<label class="control-label pull-left"  for="Name">DRA Permit Required</label>
							    </div>
							    <div class="col-sm-1">
								    <input type="checkbox" class="form-control" name="approval_dra_permit" style="width:70%;" ref="dra_permit" v-model="approval.dra_permit">
							    </div>
							</div>
						    </div>
-->

