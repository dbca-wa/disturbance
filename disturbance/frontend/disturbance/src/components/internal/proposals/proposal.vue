<template lang="html">
    <div v-if="proposal" class="container" id="internalProposal">

        <template v-if="is_local">
            proposal.vue
        </template>
      <div class="row">
        <h3 v-if="proposal.migrated">Proposal: {{ proposal.lodgement_number }} (Migrated)</h3>
        <h3 v-else>Proposal: {{ proposal.lodgement_number }}</h3>
        <h4>Proposal Type: {{proposal.proposal_type }}</h4>
        <div v-if="proposal.application_type!='Apiary'">
            <h4>Approval Level: {{proposal.approval_level }}</h4>
        </div>
        <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            <div class="row" v-if="canSeeSubmission || (!canSeeSubmission && showingProposal) || versionCurrentlyShowing>0">
                <div class="panel panel-default">
                    <div class="panel-heading">
                       Submission
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Submitted by</strong><br/>
                                {{ proposal.submitter }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Lodged on</strong><br/>
                                {{ proposal.lodgement_date | formatDate }}
                                <input type="hidden" id="lodgement_date" value="">
                            </div>
                        </div>
                        <RevisionHistory v-if="showHistory" ref="revision_history" :revision_history_url="revision_history_url" :model_object="proposal" :history_context="history_context" @update_model_object="updateProposalVersion" @compare_model_versions="compareProposalVersions" />
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
                                {{ proposal.processing_status }}
                                <input type="hidden" id="processing_status" value="">
                            </div>
                            <div class="col-sm-12">
                                <div class="separator"></div>
                            </div>
                            <template v-if="proposal.processing_status == 'With Assessor' || proposal.processing_status == 'With Referral'">
                                <div class="col-sm-12 top-buffer-s">
                                    <strong>Referrals</strong><br/>
                                    <div class="form-group">
                                        <!--select :disabled="!canLimitedAction" ref="department_users" class="form-control">
                                            <option value="null"></option>
                                            <option v-for="user in department_users" :value="user.email">{{user.name}}</option>
                                        </select-->
                                        <select 
                                            id="department_users"  
                                            name="department_users"  
                                            ref="department_users" 
                                            class="form-control" 
                                        />
                                        <template v-if='!sendingReferral'>
                                            <template v-if="selected_referral">
                                                <label class="control-label pull-left"  for="Name">Comments</label>
                                                <textarea class="form-control" name="name" v-model="referral_text"></textarea>
                                                <a v-if="canLimitedAction" @click.prevent="sendReferral()" class="actionBtn pull-right">Send</a>
                                            </template>
                                        </template>
                                        <template v-else>
                                            <span v-if="canLimitedAction" @click.prevent="sendReferral()" disabled class="actionBtn text-primary pull-right">
                                                Sending Referral&nbsp;
                                                <i class="fa fa-circle-o-notch fa-spin fa-fw"></i>
                                            </span>
                                        </template>
                                    </div>
                                    <table class="table small-table">
                                        <tr>
                                            <th>Referral</th>
                                            <th>Status/Action</th>
                                        </tr>
                                        <tr v-for="r in proposal.latest_referrals">
                                            <td>
                                                <small><strong>{{r.referral}}</strong></small><br/>
                                                <small><strong>{{r.lodged_on | formatDate}}</strong></small>
                                            </td>
                                            <td>
                                                <small><strong>{{r.processing_status}}</strong></small><br/>
                                                <template v-if="r.processing_status == 'Awaiting'">
                                                    <small v-if="canLimitedAction"><a @click.prevent="remindReferral(r)" href="#">Remind</a> / <a @click.prevent="recallReferral(r)"href="#">Recall</a></small>
                                                </template>
                                                <template v-else>
                                                    <small v-if="canLimitedAction"><a @click.prevent="resendReferral(r)" href="#">Resend</a></small>
                                                </template>
                                            </td>
                                        </tr>
                                    </table>
                                    <template>

                                    </template>
                                    <MoreReferrals @refreshFromResponse="refreshFromResponse" :proposal="proposal" :canAction="canLimitedAction" :isFinalised="isFinalised" :referral_url="referralListURL"/>
                                </div>
                                <div class="col-sm-12">
                                    <div class="separator"></div>
                                </div>
                            </template>
                            <div v-if="!isFinalised" class="col-sm-12 top-buffer-s">
                                <strong>Currently assigned to</strong><br/>
                                <div class="form-group">
                                    <template v-if="proposal.processing_status == 'With Approver'">
                                        <select ref="assigned_officer" :disabled="!canAction" class="form-control" v-model="proposal.assigned_approver">
                                            <option v-for="member in proposal.allowed_assessors" :value="member.id">{{member.first_name}} {{member.last_name}}</option>
                                        </select>
                                        <a v-if="canAssess && proposal.assigned_approver != proposal.current_assessor.id" @click.prevent="assignRequestUser()" class="actionBtn pull-right">Assign to me</a>
                                    </template>
                                    <template v-else>
                                        <select ref="assigned_officer" :disabled="!canAction" class="form-control" v-model="proposal.assigned_officer">
                                            <option v-for="member in proposal.allowed_assessors" :value="member.id">{{member.first_name}} {{member.last_name}}</option>
                                        </select>
                                        <a v-if="canAssess && proposal.assigned_officer != proposal.current_assessor.id" @click.prevent="assignRequestUser()" class="actionBtn pull-right">Assign to me</a>
                                    </template>
                                </div>
                            </div>
                            <template v-if="proposal.processing_status == 'With Assessor (Requirements)' || proposal.processing_status == 'With Approver' || isFinalised">
                                <div class="col-sm-12">
                                    <strong>Proposal</strong><br/>
                                    <a class="actionBtn" v-if="!showingProposal" @click.prevent="toggleProposal()">Show Proposal</a>
                                    <a class="actionBtn" v-else @click.prevent="toggleProposal()">Hide Proposal</a>
                                </div>
                                <div class="col-sm-12">
                                    <div class="separator"></div>
                                </div>
                            </template>
                            <template v-if="proposal.processing_status == 'With Approver' || isFinalised">
                                <div class="col-sm-12">
                                    <strong>Requirements</strong><br/>
                                    <a class="actionBtn" v-if="!showingRequirements" @click.prevent="toggleRequirements()">Show Requirements</a>
                                    <a class="actionBtn" v-else @click.prevent="toggleRequirements()">Hide Requirements</a>
                                </div>
                                <div class="col-sm-12">
                                    <div class="separator"></div>
                                </div>
                            </template>
                            <div class="col-sm-12 top-buffer-s" v-if="!isFinalised && canAction">
                                <template v-if="proposal.processing_status == 'With Assessor' || proposal.processing_status == 'With Referral'">
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <strong>Action</strong><br/>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary" :disabled="proposal.can_user_edit" @click.prevent="switchStatus('with_assessor_requirements')">Enter Requirements</button><br/>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="proposal.can_user_edit" @click.prevent="amendmentRequest()">Request Amendment</button><br/>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="proposal.can_user_edit" @click.prevent="proposedDecline()">Propose to Decline</button>
                                        </div>
                                    </div>
                                </template>
                                <template v-else-if="proposal.processing_status == 'With Assessor (Requirements)'">
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <strong>Action</strong><br/>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary" :disabled="proposal.can_user_edit" @click.prevent="switchStatus('with_assessor')">Back To Processing</button><br/>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-12" v-if="requirementsComplete">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="proposal.can_user_edit" @click.prevent="proposedApproval()">Propose to Approve</button><br/>
                                        </div>
                                    </div>
                                </template>
                                <template v-else-if="proposal.processing_status == 'With Approver'">
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <strong>Action</strong><br/>
                                        </div>
                                    </div>

                                    <div class="row">
                                        <div class="col-sm-12">
                                            <label class="control-label pull-left"  for="Name">Approver Comments</label>
                                            <textarea class="form-control" name="name" v-model="approver_comment"></textarea><br>
                                        </div>
                                    </div>

                                    <div class="row">
                                        <div class="col-sm-12" v-if="proposal.proposed_decline_status">
                                            <button style="width:80%;" class="btn btn-primary" :disabled="proposal.can_user_edit" @click.prevent="switchStatus('with_assessor')"><!-- Back To Processing -->Back To Assessor</button><br/>
                                        </div>
                                        <div class="col-sm-12" v-else>
                                            <button style="width:80%;" class="btn btn-primary" :disabled="proposal.can_user_edit" @click.prevent="switchStatus('with_assessor_requirements')"><!-- Back To Requirements -->Back To Assessor</button><br/>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <!-- v-if="!proposal.proposed_decline_status" -->
                                        <div class="col-sm-12" >
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="proposal.can_user_edit" @click.prevent="issueProposal()">Approve</button><br/>
                                        </div>
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="proposal.can_user_edit" @click.prevent="declineProposal()">Decline</button><br/>
                                        </div>
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-8">
            <div v-if="proposal_compare_version!=0" class="panel panel-default sticky-footer">
                Comparing
                <span class="label label-default">
                    {{proposal.lodgement_number}}-{{reversion_history_length}}: {{proposal.lodgement_date | formatDate }}   
                </span>&nbsp;
                with
                <span class="label label-danger">
                    {{proposal.lodgement_number}}-{{reversion_history_length - proposal_compare_version}}:
                    {{compare_version_lodgement_date | formatDate}} ({{proposal_compare_version}} Older than current)
                </span>
                
            </div>
            <div class="row">
                <template v-if="proposal.processing_status == 'With Approver' || isFinalised">
                    <ApprovalScreen :proposal="proposal" @refreshFromResponse="refreshFromResponse"/>
                </template>
                <template v-if="proposal.processing_status == 'With Assessor (Requirements)' || ((proposal.processing_status == 'With Approver' || isFinalised) && showingRequirements)">
                    <Requirements :proposal="proposal" @refreshRequirements="refreshRequirements"/>
                </template>
                <template v-if="canSeeSubmission || (!canSeeSubmission && showingProposal)">
                    <div class="col-md-12">
                        <div class="row">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Applicant
                                        <a class="panelClicker" :href="'#'+detailsBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="detailsBody">
                                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                        </a>
                                    </h3>
                                </div>
                                <div class="panel-body panel-collapse collapse in" :id="detailsBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Name</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="proposal.applicant.name">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >ABN/ACN</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantABN" placeholder="" v-model="proposal.applicant.abn">
                                            </div>
                                          </div>
                                      </form>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-12">
                        <div class="row">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Address Details
                                        <a class="panelClicker" :href="'#'+addressBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="addressBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3>
                                </div>
                                <div class="panel-body panel-collapse collapse" :id="addressBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Street</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="street" placeholder="" v-model="proposal.applicant.address.line1">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="surburb" placeholder="" v-model="proposal.applicant.address.locality">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">State</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="country" placeholder="" v-model="proposal.applicant.address.state">
                                            </div>
                                            <label for="" class="col-sm-2 control-label">Postcode</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="postcode" placeholder="" v-model="proposal.applicant.address.postcode">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Country</label>
                                            <div class="col-sm-4">
                                                <input disabled type="text" class="form-control" name="country" v-model="proposal.applicant.address.country"/>
                                            </div>
                                          </div>
                                       </form>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-12">
                        <div class="row">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Contact Details
                                        <a class="panelClicker" :href="'#'+contactsBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="contactsBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3>
                                </div>
                                <div class="panel-body panel-collapse collapse" :id="contactsBody">
                                    <table ref="contacts_datatable" :id="contacts_table_id" class="hover table table-striped table-bordered dt-responsive" cellspacing="0" width="100%">
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-12">
                        <div class="row">
                            <form :action="proposal_form_url" method="post" name="new_proposal" enctype="multipart/form-data">

                                <div v-if="proposal.application_type=='Apiary'">
                                    <ProposalApiary v-if="proposal" :proposal="proposal" id="proposalStart" :showSections="sectionShow" ref="proposal_apiary" :is_external="false" :is_internal="true" :hasAssessorMode="hasAssessorMode"></ProposalApiary>
                                </div>
                                <div v-else>
                                    <ProposalDisturbance 
                                    ref="proposal_disturbance"
                                    :key="'proposal_disturbance' + uuid"
                                    form_width="inherit" 
                                    :withSectionsSelector="false" 
                                    v-if="proposal" 
                                    :proposal="proposal"
                                    />
                                    <NewApply v-if="proposal" :proposal="proposal"></NewApply>
                                </div>


                                <div>
                                    <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                                    <input type='hidden' name="schema" :value="JSON.stringify(proposal)" />
                                    <input type='hidden' name="proposal_id" :value="1" />
                                    <div class="row" style="margin-bottom: 50px">
                                      <div class="navbar navbar-fixed-bottom" v-if="hasAssessorMode" style="background-color: #f5f5f5;">
                                        <div class="navbar-inner">
                                            <div v-if="hasAssessorMode" class="container">
                                              <p class="pull-right">
                                                <button class="btn btn-primary pull-right" style="margin-top:5px;" @click.prevent="save()">Save Changes</button>
                                              </p>
                                            </div>
                                        </div>
                                      </div>
                                    </div>

                                </div>
                            </form>
                        </div>
                    </div>
                </template>
            </div>
        </div>
        </div>
        <ProposedDecline ref="proposed_decline" :processing_status="proposal.processing_status" :proposal_id="proposal.id" @refreshFromResponse="refreshFromResponse"></ProposedDecline>
        <AmendmentRequest ref="amendment_request" :proposal_id="proposal.id" @refreshFromResponse="refreshFromResponse"></AmendmentRequest>
        <ProposedApproval ref="proposed_approval" :processing_status="proposal.processing_status" :proposal_id="proposal.id" :proposal_type='proposal.proposal_type' :isApprovalLevelDocument="isApprovalLevelDocument" :submitter_email="proposal.submitter_email" :applicant_email="applicant_email" :relevant_applicant_address="proposal.applicant.address" :relevant_applicant_name="proposal.applicant.name" :reissued="proposal.reissued" @refreshFromResponse="refreshFromResponse"/>
    

    
    </div>
    
</template>
<script>
var select2 = require('select2');
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
import ProposalDisturbance from '../../form.vue'
import ProposalApiary from '@/components/form_apiary.vue'
import NewApply from '../../external/proposal_apply_new.vue'
import Vue from 'vue'
import ProposedDecline from './proposal_proposed_decline.vue'
import AmendmentRequest from './amendment_request.vue'
import datatable from '@vue-utils/datatable.vue'
import Requirements from './proposal_requirements.vue'
import ProposedApproval from './proposed_issuance.vue'
import ApprovalScreen from './proposal_approval.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import RevisionHistory from '@common-utils/revision_history.vue'
import MoreReferrals from '@common-utils/more_referrals.vue'
import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js"
import { api_endpoints, helpers } from '@/utils/hooks'
export default {
    name: 'InternalProposal',
    data: function() {
        let vm = this;
        return {
            detailsBody: 'detailsBody'+vm._uid,
            addressBody: 'addressBody'+vm._uid,
            contactsBody: 'contactsBody'+vm._uid,
            siteLocations: 'siteLocations'+vm._uid,
            defaultKey: "aho",
            "proposal": null,
            "original_proposal": null,
            "loading": [],
            selected_referral: '',
            referral_text: '',
            approver_comment: '',
            form: null,
            members: [],
            //department_users : [],
            contacts_table_initialised: false,
            initialisedSelects: false,
            showingProposal:false,
            showingRequirements:false,
            hasAmendmentRequest: false,
            requirementsComplete:true,
            state_options: ['requirements','processing'],
            contacts_table_id: vm._uid+'contacts-table',
            is_local: helpers.is_local(),
            contacts_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": vm.contactsURL,
                    "dataSrc": ''
                },
                columns: [
                    {
                        title: 'Name',
                        mRender:function (data,type,full) {
                            return full.first_name + " " + full.last_name;
                        }
                    },
                    {
                        title: 'Phone',
                        data:'phone_number'
                    },
                    {
                        title: 'Mobile',
                        data:'mobile_number'
                    },
                    {
                        title: 'Fax',
                        data:'fax_number'
                    },
                    {
                        title: 'Email',
                        data:'email'
                    },
                  ],
                  processing: true
            },
            contacts_table: null,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            comms_url: helpers.add_endpoint_json(api_endpoints.proposals,vm.$route.params.proposal_id+'/comms_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.proposals,vm.$route.params.proposal_id+'/add_comms_log'),
            logs_url: helpers.add_endpoint_json(api_endpoints.proposals,vm.$route.params.proposal_id+'/action_log'),
            revision_history_url: helpers.add_endpoint_json(api_endpoints.proposals,vm.$route.params.proposal_id+'/revision_history'),
            panelClickersInitialised: false,
            sendingReferral: false,
            versionCurrentlyShowing: 0,
            showHistory: false,
            history_context: {
                reference_id_field: 'lodgement_number',
                app_label: 'disturbance',
                component_name: 'proposals',
                model_name: 'Proposal',
                serializer_name: 'InternalProposalSerializer',
            },
            proposal_compare_version: 0,
            reversion_history_length: 0,
            compare_version_lodgement_date: '',
            uuid: 0,
        }
    },
    components: {
        ProposalDisturbance,
        ProposalApiary,
        datatable,
        ProposedDecline,
        AmendmentRequest,
        Requirements,
        ProposedApproval,
        ApprovalScreen,
        CommsLogs,
        RevisionHistory,
        MoreReferrals,
        NewApply,
    },
    filters: {
        formatDate: function(data){
            // The only time the lodgement_date field should be empty is when viewing the final draft (just prior to submission)
            return data ? moment(data).format('MMMM Do YYYY') + ' at ' + moment(data).format('h:mm:ss a'): 'Draft just prior to lodgement.';
        },
    },
    props: {
        proposalId: {
            type: Number,
        },
    },
    watch: {

    },
    computed: {
        console: () => console,
        contactsURL: function(){
            return this.proposal!= null ? helpers.add_endpoint_json(api_endpoints.organisations,this.proposal.applicant.id+'/contacts') : '';
        },
        referralListURL: function(){
            return this.proposal!= null ? helpers.add_endpoint_json(api_endpoints.referrals,'datatable_list')+'?proposal='+this.proposal.id : '';
        },
        isLoading: function() {
          return this.loading.length > 0
        },
        csrf_token: function() {
          return helpers.getCookie('csrftoken')
        },
        proposal_form_url: function() {
          return (this.proposal) ? `/api/proposal/${this.proposal.id}/assessor_save.json` : '';
        },
        isFinalised: function(){
            return this.proposal.processing_status == 'Declined' || this.proposal.processing_status == 'Approved';
        },
        canAssess: function(){
            return this.proposal && this.proposal.assessor_mode.assessor_can_assess ? true : false;
        },
        hasAssessorMode:function(){
            return this.proposal && this.proposal.assessor_mode.has_assessor_mode ? true : false;
        },
        canAction: function(){
            if (this.proposal.processing_status == 'With Approver'){
                return this.proposal && (this.proposal.processing_status == 'With Approver' || this.proposal.processing_status == 'With Assessor' || this.proposal.processing_status == 'With Assessor (Requirements)') && !this.isFinalised && !this.proposal.can_user_edit && (this.proposal.current_assessor.id == this.proposal.assigned_approver || this.proposal.assigned_approver == null ) && this.proposal.assessor_mode.assessor_can_assess? true : false;
            }
            else{
                return this.proposal && (this.proposal.processing_status == 'With Approver' || this.proposal.processing_status == 'With Assessor' || this.proposal.processing_status == 'With Assessor (Requirements)') && !this.isFinalised && !this.proposal.can_user_edit && (this.proposal.current_assessor.id == this.proposal.assigned_officer || this.proposal.assigned_officer == null ) && this.proposal.assessor_mode.assessor_can_assess? true : false;
            }
        },
        canLimitedAction: function(){
            if (this.proposal.processing_status == 'With Approver'){
                return this.proposal && (this.proposal.processing_status == 'With Assessor' || this.proposal.processing_status == 'With Referral' || this.proposal.processing_status == 'With Assessor (Requirements)') && !this.isFinalised && !this.proposal.can_user_edit && (this.proposal.current_assessor.id == this.proposal.assigned_approver || this.proposal.assigned_approver == null ) && this.proposal.assessor_mode.assessor_can_assess? true : false;
            }
            else{
                return this.proposal && (this.proposal.processing_status == 'With Assessor' || this.proposal.processing_status == 'With Referral' || this.proposal.processing_status == 'With Assessor (Requirements)') && !this.isFinalised && !this.proposal.can_user_edit && (this.proposal.current_assessor.id == this.proposal.assigned_officer || this.proposal.assigned_officer == null ) && this.proposal.assessor_mode.assessor_can_assess? true : false;
            }
        },
        canSeeSubmission: function(){
            return this.proposal && (this.proposal.processing_status != 'With Assessor (Requirements)' && this.proposal.processing_status != 'With Approver' && !this.isFinalised)
        },
        isApprovalLevelDocument: function(){
            return this.proposal && this.proposal.processing_status == 'With Approver' && this.proposal.approval_level != null && this.proposal.approval_level_document == null ? true : false;
        },
        applicant_email:function(){
            return this.proposal && this.proposal.applicant.email ? this.proposal.applicant.email : '';
        },
    },
    methods: {
        updateProposalVersion: async function(proposal_version) {
            /* Changes the currently viewed Proposal and updates the values object on the ProposalDisturbace
            component so data field values change in the DOM. 
            */

            this.versionCurrentlyShowing = proposal_version

            // Reset this as viewing versions cancels any compare
            this.proposal_compare_version = 0

            $(".revision_note").remove()  // Remove any revision notes that may be visible

            let url = `/api/history/version/disturbance/proposals/Proposal/InternalProposalSerializer/${this.proposalId}/${proposal_version}/`

            // Get the required Proposal data
            const res = await Vue.http.get(url);

            // Set the model data to the version requested
            this.proposal = Object.assign({}, res.body);

            /*  If we are not viewing the current version (which is always 0),
                disable any action buttons and fields.
                The most simple way to achieve this without changing the vue template is to just
                modify the assessor_mode variables to appropriate values.
            */
            
            if(proposal_version!=0) {
                //console.log('Viewing older version: Disabling buttons and fields')
                this.proposal.assessor_mode.has_assessor_mode = false;
                this.proposal.assessor_mode.assessor_can_assess = false;
                this.proposal.lodgement_number = this.proposal.lodgement_number + `-${this.reversion_history_length - proposal_version} (${proposal_version} Older than current version)`
                document.body.style.backgroundColor = '#f5f5dc';
            } else {
                 document.body.style.backgroundColor = '#ffffff';             
            }

            // Update the DOM values to the correct data.
            this.$refs.proposal_disturbance.values = Object.assign({}, res.body.data[0]);

            // Rerender the form so it drops any unused sections and creates any required sections
            this.$nextTick(function(){
                this.uuid++;
            });
        },
        compareProposalVersions: async function({compare_version, lodgement_date}) {
            /* This handles the user clicks. Change the labels of entries and add all selected 
               revision differences to the DOM. */

            // Always Compare against the most recent version.
            if(0 != this.versionCurrentlyShowing) {
                this.updateProposalVersion(0)
                this.versionCurrentlyShowing = 0
            }

            this.compare_version_lodgement_date = lodgement_date
            this.proposal_compare_version = compare_version

            // Remove any previous revisions
            $(".revision_note").remove()

            // Compare the data field and apply the revision notes
            const url = '/api/history/compare/field/' + 
            this.history_context.app_label + '/' +
            this.history_context.model_name + '/' +
            this.proposal.id + '/' +
            this.versionCurrentlyShowing + '/' +
            compare_version + '/' +
            'data/' +
            '?differences_only=True';

            const data_diffs = await Vue.http.get(url).then();
            this.applyRevisionNotes(data_diffs.data)

            // Compare the assessor_data field and apply revision notes
            const assessor_data_url = `/api/proposal/${this.proposal.id}/version_differences_assessor_data.json?newer_version=${this.versionCurrentlyShowing}&older_version=${compare_version}`
            const assessor_data_diffs = await Vue.http.get(assessor_data_url);
            this.applyRevisionNotes(assessor_data_diffs.data)

            // Compare the comment_data field and apply revision notes
            const comment_data_url = `/api/proposal/${this.proposal.id}/version_differences_comment_data.json?newer_version=${this.versionCurrentlyShowing}&older_version=${compare_version}`
            const comment_data_diffs = await Vue.http.get(comment_data_url);
            this.applyRevisionNotes(comment_data_diffs.data)

            // Compare the proposal documents and apply revision notes
            const document_data_url = `/api/proposal/${this.proposal.id}/version_differences_documents.json?newer_version=${this.versionCurrentlyShowing}&older_version=${compare_version}`
            const document_data_diffs = await Vue.http.get(document_data_url);
            this.applyFileRevisionNotes(document_data_diffs.data)            
        },
        applyRevisionNotes: async function (diffdata) {
            let vm = this;
            // Append a revision note to the appropriate location in the DOM 
            for (let entry in diffdata) {
                //console.log('!@#$ entry = ' + entry)
                for (let k in diffdata[entry]) {
                    //console.log('!@#$ diffdata[entry] = ' + diffdata[entry])
                    let revision_text = diffdata[entry][k]
                    // The section identifier for referrer comments contains an email address
                    // jQuery selectors don't like the @ symbol (and other special characters)
                    if(k.includes('@')) {
                        k = k.replace('@','\\@')
                        //console.log('k changed to: ' + k)
                    }
                    let replacement = $("#id_" + k ).parent().find('input');
                    if(replacement.length!=1) {
                        replacement = $('[name="' + k + '"]')
                    }
                    const previously_blank_text = '(Previously Blank)';
                    if (revision_text == '') {
                        revision_text = previously_blank_text;
                    }
                    //console.log('!@#$ k = ' + k)
                    //console.log('!@#$ revision_text = ' + revision_text)

                    if(replacement.is(':checkbox')) {
                        //console.log('!@#$ is checkbox')
                        //console.log('!@#$ replacement ' + replacement)
                        //console.log('!@#$ replacement.text ' + replacement.parent().text() )
                        
                        let replacement_html = '<div class="revision_note" style="border:1px solid red; width: 100%; margin-top: 3px; padding-top: 0px; color: red; padding:10px 0 15px 10px;">';
                        if('-'==revision_text){
                            //console.log('revision_text = ' + revision_text)
                            //console.log('previously_blank_text = ' + previously_blank_text)
                            replacement_html += '<input type="checkbox" disabled="disabled"> '
                        } else {
                            //console.log('revision_text = ' + revision_text)
                            //console.log('previously_blank_text = ' + previously_blank_text)
                            replacement_html += '<input type="checkbox" checked="checked" disabled="disabled""> '
                        }              
                        replacement_html += replacement.parent().text().trim()
                        replacement_html += '</div>'
                        replacement.parent().parent().after(replacement_html)
                    } else if(replacement.is('textarea')){
                        const replacement_html = "<textarea disabled class='revision_note' style='width: 100%; margin-top: 3px; padding-top: 0px; color: red; border: 1px solid red;'>" + 
                                                 revision_text + 
                                                 "</textarea>"
                        replacement.after(replacement_html)
                    }
                    else if (replacement.attr('type') == "text") {
                        const replacement_html = "<input disabled class='revision_note' style='width: 100%; margin-top: 3px; color: red; border: 1px solid red;' value='" + 
                                                 revision_text + 
                                                 "'><br class='revision_note'>"
                        replacement.after(replacement_html)
                    }
                    else if (replacement.attr('type') == "radio") {
                        let replacement_html = ''
                        if (previously_blank_text == revision_text) {
                            replacement_html =  '<div class="revision_note" style="border:1px solid red; padding:5px;"><span class="revision_note" style="margin:0; color:red;">'
                            replacement_html += revision_text
                            replacement_html += '</span></div>'
                        } else {
                        replacement_html =   "<div class='revision_note' style='border:1px solid red; padding:5px;'><div class='radio'><input style='margin:0; color:red;' disabled class='revision_note' type='radio' id='radio' checked>" + 
                                                "<label class='revision_note' for='radio'" +
                                                "style='text-transform: capitalize; color: red;'>" + 
                                                revision_text +
                                                "</label></div></div>"  
                        }
                        replacement.last().parent().after(replacement_html)
                    }
                    else {
                        /*  Find out if we are dealing with a select field
                            Basically cloning the select2 and then adding and removing items
                            to show the state of the older version.
                        */
                        let select_found = false;
                        $.each(replacement.siblings(), (function(i, obj){
                            let compare_select = null;
                            let compare_select_id = k + '_compare_select';
                            if ($(this).is('select:not(.revision_note)')){
                                select_found = true;
                                if(0==$('#' + k + '_compare_select').length){
                                    compare_select = $(this).clone();
                                    compare_select.attr('id', compare_select_id);
                                    compare_select.addClass('revision_note');
                                    replacement.last().after(compare_select);
                                    vm.$nextTick(function(e){
                                        $('#'+compare_select_id).select2({
                                            "theme": "bootstrap",
                                            allowClear: true,
                                            placeholder:"Select..."
                                        });
                                    });
                                    vm.$nextTick(function(e){
                                        compare_select = $('#' + compare_select_id);
                                        compare_select.next().attr('style','margin-top:15px; border:1px solid red;');
                                        compare_select.next().attr('id', k + '_compare_select2');
                                        compare_select.next().addClass('revision_note');
                                    });
                                    // Add all the existing options
                                    const current_version_options = $(this).siblings('input:hidden');
                                    $.each(current_version_options, function(i, current_version){
                                        const option_text = $('body').find('option[value=' + current_version.value + ']').first().text();
                                        console.log('!@#$ option_text = ' + option_text );
                                        console.log('!@#$ current_version.value = ' + current_version.value);
                                        var newOption = new Option(option_text, current_version.value, true, true);
                                        $('#'+compare_select_id).append(newOption).trigger('change');                                            
                                    });
                                }
                                if($(this)[0].hasAttribute('multiple')){
                                    vm.$nextTick(function(e){
                                        if(revision_text.includes(',')){
                                            const item_to_remove = revision_text.split(',')[0];
                                            const option_value_remove = item_to_remove.substring(1);
                                            console.log('Removing item = ' + option_value_remove);
                                            const option_text = $('body').find('option[value=' + option_value_remove + ']').first().text();
                                            vm.$nextTick(function(e){
                                                $('#' + k + '_compare_select2').find("li.select2-selection__choice[title|='" + option_text + "']").remove();          
                                            });
                                            const item_to_add = revision_text.split(',')[1];
                                            const option_text_add = item_to_add.substring(1).replace(/([A-Z])/g, ' $1').trim();
                                            const option_value_add = item_to_add.substring(1);
                                            const newOption = new Option(option_text_add, option_value_add, true, true);
                                            $('#'+compare_select_id).append(newOption).trigger('change');
                                        }
                                        // Remove item from compare multi-select 
                                        else if('-' == revision_text.substring(0,1)){
                                            const option_value = revision_text.substring(1);
                                            const option_text = $('body').find('option[value=' + option_value + ']').first().text();
                                            $('#' + k + '_compare_select2').find('li.select2-selection__choice[title|="' + option_text + '"]').remove();
                                            $('#' + k + '_compare_select2').trigger('change');
                                        // Add item to compare multi-select
                                        } else if ('+' == revision_text.substring(0,1)) {
                                            const option_text = revision_text.substring(1).replace(/([A-Z])/g, ' $1').trim();
                                            const option_value = revision_text.substring(1);
                                            const newOption = new Option(option_text, option_value, true, true);
                                            $('#'+compare_select_id).append(newOption).trigger('change');
                                        }
                                    });
                                } else {
                                    //console.log('!@#$ is regular select ------------_>' );
                                    $('#'+compare_select_id).val(revision_text).trigger('change');
                                }
                            }
                        }));
                        if(!select_found){
                            const replacement_html = "<input disabled class='revision_note' style='width: 100%; margin-top: 3px; padding-top: 0px; color: red; border: 1px solid red;' value='" + 
                                                    revision_text + 
                                                    "'>"
                            replacement.last().after(replacement_html)
                        }
                    }
                }
            }
        },
        applyFileRevisionNotes: function(diffdata){
            let vm = this;
            for (let entry in diffdata) {
                
                for (let k in diffdata[entry]) {
                    let file = diffdata[entry][k]
                    //console.log('!@#$ FILES ================ diffdata[entry][k] = ' + diffdata[entry][k])
                    const operation = file[0]
                    const name = file[1]
                    const path = file[2]
                    let replacement = $("#id_" + k );
                    if(replacement.length!=1) {
                        replacement = $('[name="' + k + '"]')
                    }

                    //console.log('!@#$ FILES ================ k = ' + k)
                    //console.log('!@#$ operation ================ operation = ' + operation)
                    //console.log('!@#$ name ================ name = ' + name)
                    //console.log('!@#$ path ================ path = ' + path)

                    let compare_files_div = null;
                    let compare_files_div_id = k + '_compare_files';

                    if(0 == $('#' + compare_files_div_id).length){
                        compare_files_div = replacement.siblings('div.files').clone();
                        compare_files_div.attr('id', compare_files_div_id);
                        compare_files_div.removeClass('files');
                        compare_files_div.addClass('revision_note');
                        compare_files_div.attr('style','margin-top:15px; padding:15px 0 5px 15px; border:1px solid red;');
                        replacement.siblings('div.files').after(compare_files_div);  
                    }
                    
                    // Depending on the operation swap, add or remove files
                    // Replace item in compare multi-select
                    if('-' == operation){
                        $('#' + compare_files_div_id).find('div[data-file-name="' + name +'"]').remove();
                    }
                    // Add item to files list
                    else if('+' == operation){
                        //const file_div = '<div><p>File: <span>' + name + '</span> (deleted by applicant)</p></div>'
                        const file_div = `<div data-file-name="${name}"><p>File: <a href="${path}" target="_blank">${name}</a></p></div>`
                        $('#' + compare_files_div_id + ':last-child').append(file_div);
                    }
                }
            }          
        },
        getFieldTypeFromID: function(id) {
            const data = this.proposal.schema;
            const field = data.filter(function(data){
                return data.name == id;
            });
            return field.type;
        },
        checkAssessorData: function(){
            //check assessor boxes and clear value of hidden assessor boxes so it won't get printed on approval pdf.

            //select all fields including hidden fields
            //console.log("here");
            var all_fields = $('input[type=text]:required, textarea:required, input[type=checkbox]:required, input[type=radio]:required, input[type=file]:required, select:required')

            all_fields.each(function() {
                var ele=null;
                //check the fields which has assessor boxes.
                ele = $("[name="+this.name+"-Assessor]");
                if(ele.length>0){
                    var visiblity=$("[name="+this.name+"-Assessor]").is(':visible')
                    if(!visiblity){
                        if(ele[0].value!=''){
                            //console.log(visiblity, ele[0].name, ele[0].value)
                            ele[0].value=''
                        }
                    }
                }
            });
        },
        initialiseOrgContactTable: function(){
            let vm = this;
            if (vm.proposal && !vm.contacts_table_initialised){
                vm.contacts_options.ajax.url = helpers.add_endpoint_json(api_endpoints.organisations,vm.proposal.applicant.id+'/contacts');
                vm.contacts_table = $('#'+vm.contacts_table_id).DataTable(vm.contacts_options);
                vm.contacts_table_initialised = true;
            }
        },
        commaToNewline(s){
            return s.replace(/[,;]/g, '\n');
        },
        proposedDecline: function(){
            this.save_wo();
            this.$refs.proposed_decline.decline = this.proposal.proposaldeclineddetails != null ? helpers.copyObject(this.proposal.proposaldeclineddetails): {};
            this.$refs.proposed_decline.isModalOpen = true;
        },
        proposedApproval: function(){
            this.$refs.proposed_approval.approval = this.proposal.proposed_issuance_approval != null ? helpers.copyObject(this.proposal.proposed_issuance_approval) : {};
            if(this.proposal.proposed_issuance_approval == null){
                var test_approval={
                'cc_email': this.proposal.referral_email_list
            };
            this.$refs.proposed_approval.approval=helpers.copyObject(test_approval);
                // this.$refs.proposed_approval.$refs.bcc_email=this.proposal.referral_email_list;
            }
            //this.$refs.proposed_approval.submitter_email=helpers.copyObject(this.proposal.submitter_email);
            // if(this.proposal.applicant.email){
            //     this.$refs.proposed_approval.applicant_email=helpers.copyObject(this.proposal.applicant.email);
            // }
            this.$refs.proposed_approval.isModalOpen = true;
        },
        issueProposal:function(){
            //this.$refs.proposed_approval.approval = helpers.copyObject(this.proposal.proposed_issuance_approval);

            //save approval level comment before opening 'issue approval' modal
            if(this.proposal && this.proposal.processing_status == 'With Approver' && this.proposal.approval_level != null && this.proposal.approval_level_document == null){
                if (this.proposal.approval_level_comment!='')
                {
                    let vm = this;
                    let data = new FormData();
                    data.append('approval_level_comment', vm.proposal.approval_level_comment)
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/approval_level_comment'),data,{
                        emulateJSON:true
                        }).then(res=>{
                    vm.proposal = res.body;
                    vm.refreshFromResponse(res);
                    },err=>{
                    console.log(err);
                    });
                }
            }
            if(this.isApprovalLevelDocument && this.proposal.approval_level_comment=='')
            {
                swal(
                    'Error',
                    'Please add Approval document or comments before final approval',
                    'error'
                )
            }
            else{
            this.$refs.proposed_approval.approval = this.proposal.proposed_issuance_approval != null ? helpers.copyObject(this.proposal.proposed_issuance_approval) : {};
            this.$refs.proposed_approval.state = 'final_approval';
            this.$refs.proposed_approval.isApprovalLevelDocument = this.isApprovalLevelDocument;
            if(this.proposal.proposed_issuance_approval != null && this.proposal.proposed_issuance_approval.start_date!=null){
                var start_date=new Date();
                start_date=moment(this.proposal.proposed_issuance_approval.start_date, 'DD/MM/YYYY')

                $(this.$refs.proposed_approval.$refs.start_date).data('DateTimePicker').date(start_date);
            }
            if(this.proposal.proposed_issuance_approval != null && this.proposal.proposed_issuance_approval.expiry_date!=null){
                var expiry_date=new Date();
                expiry_date=moment(this.proposal.proposed_issuance_approval.expiry_date, 'DD/MM/YYYY')

                $(this.$refs.proposed_approval.$refs.due_date).data('DateTimePicker').date(expiry_date);
            }
            //this.$refs.proposed_approval.submitter_email=helpers.copyObject(this.proposal.submitter_email);
            // if(this.proposal.applicant.email){
            //     this.$refs.proposed_approval.applicant_email=helpers.copyObject(this.proposal.applicant.email);
            // }
            this.$refs.proposed_approval.isModalOpen = true;
            }

        },
        declineProposal:function(){
            this.$refs.proposed_decline.decline = this.proposal.proposaldeclineddetails != null ? helpers.copyObject(this.proposal.proposaldeclineddetails): {};
            this.$refs.proposed_decline.isModalOpen = true;
        },
        amendmentRequest: function(){
            this.save_wo();
            let values = '';
            $('.deficiency').each((i,d) => {
                values +=  $(d).val() != '' ? `Question - ${$(d).data('question')}\nDeficiency - ${$(d).val()}\n\n`: '';
            });
            //this.deficientFields();
            this.$refs.amendment_request.amendment.text = values;

            this.$refs.amendment_request.isModalOpen = true;
        },
        highlight_deficient_fields: function(deficient_fields){
            let vm = this;
            for (var deficient_field of deficient_fields) {
                $("#" + "id_"+deficient_field).css("color", 'red');
            }
        },
        deficientFields(){
            let vm=this;
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
        save: function(e) {
          let vm = this;
          vm.checkAssessorData();
          let formData = new FormData(vm.form);
          vm.$http.post(vm.proposal_form_url,formData).then(res=>{
              swal(
                'Saved',
                'Your proposal has been saved',
                'success'
              )
          },err=>{
          });
        },
        save_wo: function() {
          let vm = this;
          vm.checkAssessorData();
          let formData = new FormData(vm.form);
          vm.$http.post(vm.proposal_form_url,formData).then(res=>{


          },err=>{
          });
        },

        toggleProposal:function(){
            this.showingProposal = !this.showingProposal;
        },
        toggleRequirements:function(){
            this.showingRequirements = !this.showingRequirements;
        },
        updateAssignedOfficerSelect:function(){
            let vm = this;
            if (vm.proposal.processing_status == 'With Approver'){
                $(vm.$refs.assigned_officer).val(vm.proposal.assigned_approver);
                $(vm.$refs.assigned_officer).trigger('change');
            }
            else{
                $(vm.$refs.assigned_officer).val(vm.proposal.assigned_officer);
                $(vm.$refs.assigned_officer).trigger('change');
            }
        },
        assignRequestUser: function(){
            let vm = this;
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.proposals,(vm.proposal.id+'/assign_request_user')))
            .then((response) => {
                vm.proposal = response.body;
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                vm.updateAssignedOfficerSelect();
            }, (error) => {
                vm.proposal = helpers.copyObject(vm.original_proposal)
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                vm.updateAssignedOfficerSelect();
                swal(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        refreshFromResponse:function(response){
            let vm = this;
            vm.original_proposal = helpers.copyObject(response.body);
            vm.proposal = helpers.copyObject(response.body);
            vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
            vm.$nextTick(() => {
                vm.initialiseAssignedOfficerSelect(true);
                vm.updateAssignedOfficerSelect();
            });
        },
        refreshRequirements: function(bool){
              let vm=this;
              //vm.proposal.requirements_completed=bool;
              //console.log('here', bool);
              vm.requirementsComplete=bool;
        },
        assignTo: function(){
            let vm = this;
            let unassign = true;
            let data = {};
            if (vm.processing_status == 'With Approver'){
                unassign = vm.proposal.assigned_approver != null && vm.proposal.assigned_approver != 'undefined' ? false: true;
                data = {'assessor_id': vm.proposal.assigned_approver};
            }
            else{
                unassign = vm.proposal.assigned_officer != null && vm.proposal.assigned_officer != 'undefined' ? false: true;
                data = {'assessor_id': vm.proposal.assigned_officer};
            }
            if (!unassign){
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,(vm.proposal.id+'/assign_to')),JSON.stringify(data),{
                    emulateJSON:true
                }).then((response) => {
                    vm.proposal = response.body;
                    vm.original_proposal = helpers.copyObject(response.body);
                    vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                    vm.updateAssignedOfficerSelect();
                }, (error) => {
                    vm.proposal = helpers.copyObject(vm.original_proposal)
                    vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                    vm.updateAssignedOfficerSelect();
                    swal(
                        'Proposal Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });
            }
            else{
                vm.$http.get(helpers.add_endpoint_json(api_endpoints.proposals,(vm.proposal.id+'/unassign')))
                .then((response) => {
                    vm.proposal = response.body;
                    vm.original_proposal = helpers.copyObject(response.body);
                    vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                    vm.updateAssignedOfficerSelect();
                }, (error) => {
                    vm.proposal = helpers.copyObject(vm.original_proposal)
                    vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                    vm.updateAssignedOfficerSelect();
                    swal(
                        'Proposal Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });
            }
        },
        switchStatus: function(status){
            let vm = this;
            //vm.save_wo();
            //let vm = this;
            if(vm.proposal.processing_status == 'With Assessor' && status == 'with_assessor_requirements'){
            vm.checkAssessorData();
            let formData = new FormData(vm.form);
            vm.$http.post(vm.proposal_form_url,formData).then(res=>{ //save Proposal before changing status so that unsaved assessor data is saved.

            let data = {'status': status, 'approver_comment': vm.approver_comment}
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,(vm.proposal.id+'/switch_status')),JSON.stringify(data),{
                emulateJSON:true,
            })
            .then((response) => {
                vm.proposal = response.body;
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                vm.approver_comment='';
                vm.$nextTick(() => {
                    vm.initialiseAssignedOfficerSelect(true);
                    vm.updateAssignedOfficerSelect();
                });

            }, (error) => {
                vm.proposal = helpers.copyObject(vm.original_proposal)
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });

          },err=>{
          });
        }

        //if approver is pushing back proposal to Assessor then navigate the approver back to dashboard page
        if(vm.proposal.processing_status == 'With Approver' && (status == 'with_assessor_requirements' || status=='with_assessor')) {
            let data = {'status': status, 'approver_comment': vm.approver_comment}
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,(vm.proposal.id+'/switch_status')),JSON.stringify(data),{
                emulateJSON:true,
            })
            .then((response) => {
                vm.proposal = response.body;
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                vm.approver_comment='';
                vm.$nextTick(() => {
                    vm.initialiseAssignedOfficerSelect(true);
                    vm.updateAssignedOfficerSelect();
                });
                vm.$router.push({ path: '/internal' });
            }, (error) => {
                vm.proposal = helpers.copyObject(vm.original_proposal)
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });

        }

        else{


         let data = {'status': status, 'approver_comment': vm.approver_comment}
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,(vm.proposal.id+'/switch_status')),JSON.stringify(data),{
                emulateJSON:true,
            })
            .then((response) => {
                vm.proposal = response.body;
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                vm.approver_comment='';
                vm.$nextTick(() => {
                    vm.initialiseAssignedOfficerSelect(true);
                    vm.updateAssignedOfficerSelect();
                });
            }, (error) => {
                vm.proposal = helpers.copyObject(vm.original_proposal)
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
            }
        },
        /*
        fetchDeparmentUsers: function(){
            let vm = this;
            vm.loading.push('Loading Department Users');
            vm.$http.get(api_endpoints.department_users).then((response) => {
                vm.department_users = response.body
                vm.loading.splice('Loading Department Users',1);
            },(error) => {
                vm.loading.splice('Loading Department Users',1);
            })
        },
        */
        initialiseAssignedOfficerSelect:function(reinit=false){
            let vm = this;
            if (reinit){
                $(vm.$refs.assigned_officer).data('select2') ? $(vm.$refs.assigned_officer).select2('destroy'): '';
            }
            // Assigned officer select
            $(vm.$refs.assigned_officer).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select Officer"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                if (vm.proposal.processing_status == 'With Approver'){
                    vm.proposal.assigned_approver = selected.val();
                }
                else{
                    vm.proposal.assigned_officer = selected.val();
                }
                vm.assignTo();
            }).on("select2:unselecting", function(e) {
                var self = $(this);
                setTimeout(() => {
                    self.select2('close');
                }, 0);
            }).on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                if (vm.proposal.processing_status == 'With Approver'){
                    vm.proposal.assigned_approver = null;
                }
                else{
                    vm.proposal.assigned_officer = null;
                }
                vm.assignTo();
            });
        },
        initialiseSelects: function(){
            let vm = this;
            if (!vm.initialisedSelects){
                /*
                $(vm.$refs.department_users).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    placeholder:"Select Referral"
                }).
                on("select2:select",function (e) {
                    var selected = $(e.currentTarget);
                    vm.selected_referral = selected.val();
                }).
                on("select2:unselect",function (e) {
                    var selected = $(e.currentTarget);
                    vm.selected_referral = ''
                });
                */
                vm.initialiseAssignedOfficerSelect();
                this.initialiseReferralSelect();
                vm.initialisedSelects = true;
            }
        },
        sendReferral: function(){
            let vm = this;
            //vm.save_wo();
            vm.checkAssessorData();
            let formData = new FormData(vm.form);
            vm.sendingReferral = true;
            vm.$http.post(vm.proposal_form_url,formData).then(res=>{

            let data = {'email':vm.selected_referral, 'text': vm.referral_text};
            //vm.sendingReferral = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,(vm.proposal.id+'/assesor_send_referral')),JSON.stringify(data),{
                emulateJSON:true
            }).then((response) => {
                vm.sendingReferral = false;
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = response.body;
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Referral Sent',
                    'The referral has been sent to '+ vm.selected_referral,
                    'success'
                )
                $(vm.$refs.department_users).val(null).trigger("change");
                vm.selected_referral = '';
                vm.referral_text = '';
            }, (error) => {
                console.log(error);
                swal(
                    'Referral Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
                vm.sendingReferral = false;
            });


          },err=>{
          });

        //this.$refs.referral_comment.selected_referral = vm.selected_referral;
        //this.$refs.referral_comment.isModalOpen = true;

          /*  let data = {'email':vm.selected_referral};
            vm.sendingReferral = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,(vm.proposal.id+'/assesor_send_referral')),JSON.stringify(data),{
                emulateJSON:true
            }).then((response) => {
                vm.sendingReferral = false;
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = response.body;
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Referral Sent',
                    'The referral has been sent to '+vm.department_users.find(d => d.email == vm.selected_referral).name,
                    'success'
                )
                $(vm.$refs.department_users).val(null).trigger("change");
                vm.selected_referral = '';
            }, (error) => {
                console.log(error);
                swal(
                    'Referral Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
                vm.sendingReferral = false;
            }); */
        },
        remindReferral:function(r){
            let vm = this;

            vm.$http.get(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/remind')).then(response => {
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = response.body;
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Referral Reminder',
                    'A reminder has been sent to '+r.referral,
                    'success'
                )
            },
            error => {
                swal(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        resendReferral:function(r){
            let vm = this;

            vm.$http.get(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/resend')).then(response => {
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = response.body;
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Referral Resent',
                    'The referral has been resent to '+r.referral,
                    'success'
                )
            },
            error => {
                swal(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        recallReferral:function(r){
            let vm = this;
            swal({
                    title: "Loading...",
                    //text: "Loading...",
                    allowOutsideClick: false,
                    allowEscapeKey:false,
                    onOpen: () =>{
                        swal.showLoading()
                    }
            })

            vm.$http.get(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/recall')).then(response => {
                swal.hideLoading();
                swal.close();
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = response.body;
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Referral Recall',
                    'The referall has been recalled from '+r.referral,
                    'success'
                )
            },
            error => {
                swal(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        initialiseReferralSelect: function() {
            let vm = this;
            $(vm.$refs.department_users).select2({
                minimumInputLength: 2,
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select Referrer",
                ajax: {
                    url: api_endpoints.users_api + '/get_department_users/',
                    dataType: 'json',
                    data: function(params) {
                        var query = {
                            term: params.term,
                            type: 'public',
                        }
                        return query;
                    },
                },
            }).
            on("select2:select", function (e) {
                var selected = $(e.currentTarget);
                //vm.selected_referral = selected.val();
                let data = e.params.data.id;
                vm.selected_referral = data;
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.selected_referral = null;
            })/*.
            on("select2:open",function (e) {
                //const searchField = $(".select2-search__field")
                const searchField = $('[aria-controls="select2-mooring_lookup-results"]')
                // move focus to select2 field
                searchField[0].focus();
            });
            */
        },
    },
    mounted: function() {
    },
    updated: function(){
        let vm = this;
        if (!vm.panelClickersInitialised){
            $('.panelClicker[data-toggle="collapse"]').on('click', function () {
                var chev = $(this).children()[0];
                window.setTimeout(function () {
                    $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
                },100);
            });
            vm.panelClickersInitialised = true;
        }
        this.$nextTick(() => {
            vm.initialiseOrgContactTable();
            vm.initialiseSelects();
            vm.form = document.forms.new_proposal;
            if(vm.hasAmendmentRequest){
                vm.deficientFields();
            }
        });
    },
    created: function() {
        Vue.http.get(`/api/proposal/${this.proposalId}/internal_proposal.json`).then(res => {
            this.proposal = res.body;
            this.original_proposal = helpers.copyObject(res.body);
            this.proposal.applicant.address = this.proposal.applicant.address != null ? this.proposal.applicant.address : {};
            this.hasAmendmentRequest=this.proposal.hasAmendmentRequest;
            this.reversion_history_length = Object.keys(this.proposal.reversion_history).length
            if(this.reversion_history_length>1){
                this.showHistory = true;
            }
        },
        err => {
          console.log(err);
        });

    },
    /*
    beforeRouteEnter: function(to, from, next) {
          Vue.http.get(`/api/proposal/${to.params.proposal_id}/internal_proposal.json`).then(res => {
              next(vm => {
                vm.proposal = res.body;
                vm.original_proposal = helpers.copyObject(res.body);
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                vm.hasAmendmentRequest=vm.proposal.hasAmendmentRequest;
              });
            },
            err => {
              console.log(err);
            });
    },
    */
    beforeRouteUpdate: function(to, from, next) {
        console.log("beforeRouteUpdate")
          Vue.http.get(`/api/proposal/${to.params.proposal_id}.json`).then(res => {
              next(vm => {
                vm.proposal = res.body;
                vm.original_proposal = helpers.copyObject(res.body);
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
              });
            },
            err => {
              console.log(err);
            });
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
.separator {
    border: 1px solid;
    margin-top: 15px;
    margin-bottom: 10px;
    width: 100%;
}

.sticky-footer {
    /*margin: auto;*/
    font-size:1.2em;
    position:fixed;
    top:0;
    /*border:2px solid #000;*/
    z-index: 99 !important;
    background: #efefef;
    padding:10px;
    margin:0 0 0 -15px;
}

</style>
