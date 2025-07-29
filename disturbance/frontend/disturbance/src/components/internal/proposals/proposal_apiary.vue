<template lang="html">
    <div v-if="proposal" class="container" id="internalProposal">
        <template v-if="is_local">
        </template>
      <div class="row">
        <h3>Application: {{ proposal.lodgement_number }}</h3>
        <h4>Application Type: {{proposal.activity }}</h4>
        <div v-if="!proposal.apiary_group_application_type">
            <h4>Approval Level: {{proposal.approval_level }}</h4>
        </div>
        <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            <div class="row" v-if="canSeeSubmission">
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
                                {{ formatDate(proposal.lodgement_date)}}
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


            <!--
            <div class="row" v-if="canSeeSubmission">
                <div class="panel panel-default">
                    <div class="panel-heading">
                       History
                    </div>
                                    <table class="table small-table">
                                        <tr>
                                            <th>ID</th>
                                            <th>Last Modified</th>
                                        </tr>
                                        <tr v-for="p in proposal.get_history">
                                            <td>{{ p.id }}</td>
                                            <td>{{ p.modified | formatDate}}</td>
                                        </tr>
                                    </table>
                </div>
            </div>
            -->

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
                                        <select :disabled="!canLimitedAction" ref="apiary_referral_groups" class="form-control">
                                            <option value="null"></option>
                                            <option v-for="group in apiaryReferralGroups" :value="group.id" :key="group.id">{{group.name}}</option>
                                        </select>
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
                                        <tr v-for="r in proposal.latest_referrals" :key="r.id">
                                            <td>
                                                <small><strong>{{r.apiary_referral.referral_group.name}}</strong></small><br/>
                                                <small><strong>{{ formatDate( r.lodged_on) }}</strong></small>
                                            </td>
                                            <td>
                                                <small><strong>{{r.processing_status}}</strong></small><br/>
                                                <template v-if="r.processing_status == 'Awaiting'">
                                                    <small v-if="canLimitedAction"><a @click.prevent="remindReferral(r)" href="#">Remind</a> / <a @click.prevent="recallReferral(r)" href="#">Recall</a></small>
                                                </template>
                                                <template v-else>
                                                    <small v-if="canLimitedAction"><a @click.prevent="resendReferral(r)" href="#">Resend</a></small>
                                                </template>
                                            </td>
                                        </tr>
                                    </table>
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
                                            <option v-for="member in proposal.allowed_assessors" :value="member.id" :key="member.id">{{member.first_name}} {{member.last_name}}</option>
                                        </select>
                                        <a v-if="canAssess && proposal.assigned_approver != proposal.current_assessor.id" @click.prevent="assignRequestUser()" class="actionBtn pull-right">Assign to me</a>
                                    </template>
                                    <template v-else>
                                        <select ref="assigned_officer" :disabled="!canAction" class="form-control" v-model="proposal.assigned_officer">
                                            <option v-for="member in proposal.allowed_assessors" :value="member.id" :key="member.id">{{member.first_name}} {{member.last_name}}</option>
                                        </select>
                                        <a v-if="canAssess && proposal.assigned_officer != proposal.current_assessor.id" @click.prevent="assignRequestUser()" class="actionBtn pull-right">Assign to me</a>
                                    </template>
                                </div>
                            </div>
                            <template v-if="proposal.processing_status == 'With Assessor (Requirements)' || proposal.processing_status == 'With Approver' || isFinalised">
                                <div class="col-sm-12">
                                    <div v-if="proposal.proposal_apiary">
                                        <strong>Application</strong><br/>
                                        <a class="actionBtn" v-if="!showingProposal" @click.prevent="toggleProposal()">Show Application</a>
                                        <a class="actionBtn" v-else @click.prevent="toggleProposal()">Hide Application</a>
                                    </div>
                                    <div v-else>
                                        <strong>Proposal</strong><br/>
                                        <a class="actionBtn" v-if="!showingProposal" @click.prevent="toggleProposal()">Show Proposal</a>
                                        <a class="actionBtn" v-else @click.prevent="toggleProposal()">Hide Proposal</a>
                                    </div>
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
            <div class="row">
                <template v-if="proposal.processing_status == 'With Approver' || isFinalised">
                    <div v-if="siteTransferTemporaryUse">
                        <!-- <ApprovalScreenSiteTransferTemporaryUse
                            :proposal="proposal"
                            ref="approval_screen"
                            @refreshFromResponse="refreshFromResponse"
                        /> -->
                    </div>
                    <div v-else>
                        <ApprovalScreen
                            :proposal="proposal"
                            ref="approval_screen"
                            @refreshFromResponse="refreshFromResponse"
                        />
                    </div>
                </template>
                <template v-if="canLimitedAction && proposal.processing_status == 'With Assessor (Requirements)' || ((proposal.processing_status == 'With Approver' || isFinalised) && showingRequirements)">
                    <div v-if="siteTransfer">
                        <OriginatingApprovalRequirements
                        :proposal="proposal"
                        :originatingApprovalId="originatingApprovalId"
                        :originatingApprovalLodgementNumber="originatingApprovalLodgementNumber"
                        />
                        <TargetApprovalRequirements
                        :proposal="proposal"
                        :targetApprovalId="targetApprovalId"
                        :targetApprovalLodgementNumber="targetApprovalLodgementNumber"
                        />
                    </div>
                    <div v-else>
                        <Requirements
                            :proposal="proposal"
                            @refreshRequirements="refreshRequirements"
                        />
                    </div>
                </template>
                <!--template v-show="canSeeSubmission || (!canSeeSubmission && showingProposal)"-->
                <div v-show="canSeeProposal">
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
                                <div v-if="organisationApplicant">
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
                                <div v-else>
                                    <div class="panel-body panel-collapse collapse in" :id="detailsBody">
                                          <form class="form-horizontal">
                                              <div class="form-group">
                                                <label for="" class="col-sm-3 control-label">Given Name(s)</label>
                                                <div class="col-sm-6">
                                                    <input disabled type="text" class="form-control" name="applicantFirstName" placeholder="" v-model="proposal.applicant_first_name">
                                                </div>
                                              </div>
                                              <div class="form-group">
                                                <label for="" class="col-sm-3 control-label" >Last Name</label>
                                                <div class="col-sm-6">
                                                    <input disabled type="text" class="form-control" name="applicantLastName" placeholder="" v-model="proposal.applicant_last_name">
                                                </div>
                                              </div>
                                          </form>
                                    </div>
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
                                                <input disabled type="text" class="form-control" name="street" placeholder="" v-model="applicantAddressLine1">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="surburb" placeholder="" v-model="applicantAddressLocality">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">State</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="country" placeholder="" v-model="applicantAddressState">
                                            </div>
                                            <label for="" class="col-sm-2 control-label">Postcode</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="postcode" placeholder="" v-model="applicantAddressPostcode">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Country</label>
                                            <div class="col-sm-4">
                                                <input disabled type="text" class="form-control" name="country" v-model="applicantAddressCountry"/>
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
                                    <div v-if="organisationApplicant">
                                        <table ref="contacts_datatable" :id="contacts_table_id" class="hover table table-striped table-bordered dt-responsive" cellspacing="0" width="100%">
                                        </table>
                                    </div>
                                    <div v-else>
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Phone (work)</label>
                                            <div class="col-md-8">
                                                <input disabled type="text" class="form-control" name="applicantWorkPhone" placeholder="" v-model="proposal.applicant_phone_number">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Mobile</label>
                                            <div class="col-md-8">
                                                <input disabled type="text" class="form-control" name="applicantMobileNumber" placeholder="" v-model="proposal.applicant_mobile_number">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Email</label>
                                            <div class="col-md-8">
                                                <input disabled type="text" class="form-control" name="applicantEmail" placeholder="" v-model="proposal.applicant_email">
                                            </div>
                                          </div>
                                      </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-12">
                        <div class="row">
                            <form :action="proposal_form_url" method="post" name="new_proposal" enctype="multipart/form-data">
                                <div v-if="proposal && proposal.application_type=='Apiary'">
                                    <ApiaryForm
                                        v-if="proposal"
                                        :proposal="proposal"
                                        id="proposalStart"
                                        ref="apiary_form"
                                        :hasAssessorMode="hasAssessorMode"
                                        :is_external="false"
                                        :is_internal="true"
                                        :show_col_vacant_when_submitted="true"
                                    />
                                </div>
                                <div v-else-if="proposal && proposal.application_type=='Site Transfer'">
                                    <ApiarySiteTransfer
                                        v-if="proposal"
                                        :proposal="proposal"
                                        id="proposalStart"
                                        ref="site_transfer"
                                        :hasAssessorMode="hasAssessorMode"
                                        :is_external="false"
                                        :is_internal="true"
                                    />
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
                </div>
            </div>
        </div>
        </div>
        <ProposedDecline ref="proposed_decline" :processing_status="proposal.processing_status" :proposal_id="proposal.id" @refreshFromResponse="refreshFromResponse"></ProposedDecline>
        <AmendmentRequest
        ref="amendment_request"
        :proposal_id="proposal.id"
        :is_apiary_proposal="isApiaryProposal"
        @refreshFromResponse="refreshFromResponse"
        />
    </div>
</template>
<script>
import { v4 as uuidv4 } from 'uuid';
import ApiaryForm from '@/components/form_apiary.vue'
// import NewApply from '../../external/proposal_apply_new.vue'
import ProposedDecline from './proposal_proposed_decline.vue'
import AmendmentRequest from './amendment_request.vue'
import Requirements from './proposal_requirements.vue'
import OriginatingApprovalRequirements from './originating_approval_requirements.vue'
import TargetApprovalRequirements from './target_approval_requirements.vue'
import ApprovalScreen from './proposal_approval.vue'
// import ApprovalScreenSiteTransferTemporaryUse from './proposal_approval_site_transfer_temporary_use.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import { api_endpoints, helpers, constants } from '@/utils/hooks'
import ApiarySiteTransfer from '@/components/form_apiary_site_transfer.vue'

export default {
    name: 'InternalProposalApiary',
    data: function() {
        let vm = this;
        return {
            requirementsComplete:true,
            detailsBody: 'detailsBody'+uuidv4(),
            addressBody: 'addressBody'+uuidv4(),
            contactsBody: 'contactsBody'+uuidv4(),
            siteLocations: 'siteLocations'+uuidv4(),
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
            apiaryReferralGroups: [],
            //contacts_table_initialised: false,
            initialisedSelects: false,
            showingProposal:false,
            showingRequirements:false,
            hasAmendmentRequest: false,
            state_options: ['requirements','processing'],
            contacts_table_id: uuidv4()+'contacts-table',
            contacts_options:{
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                ajax: {
                    "url": '',
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
            panelClickersInitialised: false,
            sendingReferral: false,
            is_local: helpers.is_local(),
        }
    },
    components: {
        //ProposalApiary,
        ApiaryForm,
        ProposedDecline,
        AmendmentRequest,
        Requirements,
        OriginatingApprovalRequirements,
        TargetApprovalRequirements,
        ApprovalScreen,
        // ApprovalScreenSiteTransferTemporaryUse,
        CommsLogs,
        //MoreReferrals,
        //MapLocations,
        ApiarySiteTransfer,
    },
    props: {
        proposalId: {
            type: Number,
        },
    },
    watch: {
    },
    computed: {
        formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
        },
        referralListURL: function(){
            return this.proposal!= null ? helpers.add_endpoint_json(api_endpoints.apiary_referrals,'datatable_list')+'?proposal='+this.proposal.id : '';
        },
        isLoading: function() {
          return this.loading.length > 0
        },
        csrf_token: function() {
          return helpers.getCookie('csrftoken')
        },
        proposal_form_url: function() {
            var url = "";
          //return (this.proposal) ? `/api/proposal/${this.proposal.id}/assessor_save.json` : '';
            if (this.apiaryProposal) {
                url = `/api/proposal_apiary/${this.apiaryProposal.id}/assessor_save.json`;
            }
            return url;
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
        canSeeProposal: function(){
            return this.canSeeSubmission || this.showingProposal;
        },
        isApprovalLevelDocument: function(){
            return this.proposal && this.proposal.processing_status == 'With Approver' && this.proposal.approval_level != null && this.proposal.approval_level_document == null ? true : false;
        },
        applicant_email:function(){
            return this.proposal && this.proposal.applicant.email ? this.proposal.applicant.email : '';
        },
        applicantAddress: function() {
            var addr="";
            if (this.proposal && this.proposal.applicant_address) {
                addr=this.proposal.applicant_address;
            }
            return addr;
        },
        applicantAddressLine1: function() {
            var addr1="";
            if (this.proposal && this.proposal.applicant_address) {
                addr1=this.proposal.applicant_address.line1;
            }
            return addr1;
        },
        applicantAddressCountry: function() {
            var country="";
            if (this.proposal && this.proposal.applicant_address) {
                country=this.proposal.applicant_address.country;
            }
            return country;
        },
        applicantAddressLocality: function() {
            var locality="";
            if (this.proposal && this.proposal.applicant_address) {
                locality=this.proposal.applicant_address.locality;
            }
            return locality;
        },
        applicantAddressState: function() {
            var state="";
            if (this.proposal && this.proposal.applicant_address) {
                state=this.proposal.applicant_address.state;
            }
            return state;
        },
        applicantAddressPostcode: function() {
            var postcode="";
            if (this.proposal && this.proposal.applicant_address) {
                postcode=this.proposal.applicant_address.postcode;
            }
            return postcode;
        },
        organisationApplicant: function() {
            let oApplicant = false;
            if (this.proposal && this.proposal.applicant_type === 'organisation') {
                oApplicant = true;
            }
            return oApplicant;
        },
        individualApplicant: function() {
            let iApplicant = false;
            if (this.proposal && this.proposal.applicant_type === 'proxy') {
                iApplicant = true;
            }
            return iApplicant;
        },
        isApiaryProposal: function() {
            let returnVal = false;
            if (this.proposal && this.proposal.proposal_apiary) {
                returnVal = true;
            }
            return returnVal;
        },
        apiaryProposal: function() {
            let returnVal = null;
            if (this.proposal && this.proposal.proposal_apiary) {
                returnVal = this.proposal.proposal_apiary;
            }
            return returnVal;
        },
        siteTransferTemporaryUse: function() {
            let returnVal = false;
            if (this.proposal && ['Site Transfer', 'Temporary Use'].includes(this.proposal.application_type)) {
                returnVal = true;
            }
            return returnVal;
        },
        siteTransfer: function() {
            let returnVal = false;
            if (this.proposal.application_type === 'Site Transfer') {
                returnVal = true;
            }
            return returnVal;
        },
        originatingApprovalId: function() {
            let returnVal = null;
            if (this.proposal.application_type === 'Site Transfer') {
                returnVal = this.proposal.proposal_apiary.originating_approval_id;
            }
            return returnVal;
        },
        originatingApprovalLodgementNumber: function() {
            let returnVal = null;
            if (this.proposal.application_type === 'Site Transfer') {
                returnVal = this.proposal.proposal_apiary.originating_approval_lodgement_number;
            }
            return returnVal;
        },
        targetApprovalId: function() {
            let returnVal = null;
            if (this.proposal.application_type === 'Site Transfer') {
                returnVal = this.proposal.proposal_apiary.target_approval_id;
            }
            return returnVal;
        },
        targetApprovalLodgementNumber: function() {
            let returnVal = '';
            if (this.proposal.application_type === 'Site Transfer') {
                returnVal = this.proposal.proposal_apiary.target_approval_lodgement_number;
            }
            return returnVal;
        },
    },
    methods: {
        refreshRequirements: function(bool){
              let vm=this;
              vm.requirementsComplete=bool;
        },
        locationUpdated: function(){
            console.log('in locationUpdated()');
        },
        checkAssessorData: function(){
            //check assessor boxes and clear value of hidden assessor boxes so it won't get printed on approval pdf.

            //select all fields including hidden fields
            var all_fields = $('input[type=text]:required, textarea:required, input[type=checkbox]:required, input[type=radio]:required, input[type=file]:required, select:required')

            all_fields.each(function() {
                var ele=null;
                //check the fields which has assessor boxes.
                ele = $("[name="+this.name+"-Assessor]");
                if(ele.length>0){
                    var visiblity=$("[name="+this.name+"-Assessor]").is(':visible')
                    if(!visiblity){
                        if(ele[0].value!=''){
                            ele[0].value=''
                        }
                    }
                }
            });
        },
        initialiseOrgContactTable: function(){
            let vm = this;
            //if (vm.proposal && !vm.contacts_table_initialised){
            if (vm.proposal){
                vm.contacts_options.ajax.url = helpers.add_endpoint_json(api_endpoints.organisations,vm.proposal.applicant.id+'/contacts');
                vm.contacts_table = $('#'+vm.contacts_table_id).DataTable(vm.contacts_options);
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
            let copiedProposedIssuanceApproval = helpers.copyObject(this.proposal.proposed_issuance_approval);
            if (this.proposal.proposal_type == 'Renewal') {
                copiedProposedIssuanceApproval.expiry_date = null;
            }
            this.$refs.proposed_approval.approval = this.proposal.proposed_issuance_approval != null ? copiedProposedIssuanceApproval : {};
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
            // Force to refresh the map to display it in case it is not shown.
            // When the map is in modal, it is often not shown unless the map is resized
            this.$refs.proposed_approval.forceToRefreshMap()
        },
        issueProposal:function(){
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
                //this.$refs.proposed_approval.submitter_email=helpers.copyObject(this.proposal.submitter_email);
                // if(this.proposal.applicant.email){
                //     this.$refs.proposed_approval.applicant_email=helpers.copyObject(this.proposal.applicant.email);
                // }
                this.$refs.proposed_approval.isModalOpen = true;

                // Force to refresh the map to display it in case it is not shown.
                // When the map is in modal, it is often not shown unless the map is resized
                this.$refs.proposed_approval.forceToRefreshMap()
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
                }
            });
            vm.highlight_deficient_fields(deficient_fields);
        },
        save: function() {
          let vm = this;
          vm.checkAssessorData();
          let formData = new FormData(vm.form);
          vm.$http.post(vm.proposal_form_url,formData).then(()=>{
              swal(
                'Saved',
                'Your proposal has been saved',
                'success'
              )
          },err=>{
            console.log(err);
          });
        },
        save_wo: function() {
          let vm = this;
          vm.checkAssessorData();
          let formData = new FormData(vm.form);
          vm.$http.post(vm.proposal_form_url,formData).then(()=>{
        
          },err=>{
              console.log(err);
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
            if (vm.$refs.approval_screen){
                vm.$refs.approval_screen.updateComponentSiteSelectionKey()
            }
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
            vm.$http.post(vm.proposal_form_url,formData).then(()=>{ //save Proposal before changing status so that unsaved assessor data is saved.

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
            console.log(err);
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
        fetchApiaryReferralGroups: function() {
            this.loading.push('Loading Apiary Referral Groups');
            this.$http.get(api_endpoints.apiary_referral_groups).then((response) => {
                for (let group of response.body) {
                    this.apiaryReferralGroups.push(group)
                }
                this.loading.splice('Loading Apiary Referral Groups',1);
            },(error) => {
                console.log(error);
                this.loading.splice('Loading Apiary Referral Groups',1);
            })

        },
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
            }).on("select2:unselecting", function() {
                var self = $(this);
                setTimeout(() => {
                    self.select2('close');
                }, 0);
            }).on("select2:unselect",function () {
                // var selected = $(e.currentTarget);
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
                $(vm.$refs.apiary_referral_groups).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    placeholder:"Select Referral"
                }).
                on("select2:select",function (e) {
                    var selected = $(e.currentTarget);
                    vm.selected_referral = selected.val();
                }).
                on("select2:unselect",function () {
                    // var selected = $(e.currentTarget);
                    vm.selected_referral = ''
                });
                vm.initialiseAssignedOfficerSelect();
                vm.initialisedSelects = true;
            }
        },
        sendReferral: function(){
            let vm = this;
            //vm.save_wo();
            vm.checkAssessorData();
            let formData = new FormData(vm.form);
            vm.sendingReferral = true;
            vm.$http.post(vm.proposal_form_url,formData).then(()=>{

            let data = {'group_id':vm.selected_referral, 'text': vm.referral_text};
            //vm.sendingReferral = true;
            // need to create Referral, ApiaryReferral at this point
            let url = helpers.add_endpoint_json(api_endpoints.proposal_apiary,(vm.proposal.proposal_apiary.id+'/apiary_assessor_send_referral'))
            //vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,(vm.proposal.id+'/assesor_send_referral')),JSON.stringify(data),{
            //vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposal_apiary,(vm.proposal.id+'/apiary_assessor_send_referral')),JSON.stringify(data),{
            vm.$http.post(url,JSON.stringify(data),{
                emulateJSON:true
            }).then((response) => {
                vm.sendingReferral = false;
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = response.body;
                //vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                vm.proposal.relevant_applicant_address = vm.proposal.relevant_applicant_address != null ? vm.proposal.relevant_applicant_address : {};
                swal(
                    'Referral Sent',
                    'The referral has been sent to '+vm.apiaryReferralGroups.find(d => d.id == vm.selected_referral).name,
                    'success'
                )
                $(vm.$refs.apiaryReferralGroups).val(null).trigger("change");
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
              console.log(err);
          });

        },
        remindReferral:function(r){
            let vm = this;

            vm.$http.get(helpers.add_endpoint_json(api_endpoints.apiary_referrals,r.apiary_referral.id+'/remind')).then(response => {
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = response.body;
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Referral Reminder',
                    'A reminder has been sent to '+r.apiary_referral.referral_group.name,
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

            vm.$http.get(helpers.add_endpoint_json(api_endpoints.apiary_referrals,r.apiary_referral.id+'/resend')).then(response => {
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = response.body;
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Referral Resent',
                    'The referral has been resent to '+r.apiary_referral.referral_group.name,
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
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.apiary_referrals,r.apiary_referral.id+'/recall')).then(response => {
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = response.body;
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Referral Recall',
                    'The referral has been recalled from '+r.apiary_referral.referral_group.name,
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
        }

    },
    mounted: async function() {
        await this.fetchApiaryReferralGroups();
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
            vm.initialiseSelects();
            vm.form = document.forms.new_proposal;
            if(vm.hasAmendmentRequest){
                vm.deficientFields();
            }
        });
    },
    created: async function() {
        try {
            const res = await Vue.http.get(`/api/proposal/${this.proposalId}/internal_proposal.json/?with_apiary_sites=true`);
            this.proposal = Object.assign({}, res.body);
            //this.original_proposal = helpers.copyObject(res.body);
            if (this.proposal.applicant) {
                this.proposal.applicant.address = this.proposal.applicant.address != null ? this.proposal.applicant.address : {};
            }
            this.hasAmendmentRequest = this.proposal.hasAmendmentRequest;
            this.$nextTick(async () => {
                if (this.organisationApplicant) {
                    await this.initialiseOrgContactTable();
                }
            });
        } catch(err) {
            console.log(err);
        }
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
.separator {
    border: 1px solid;
    margin-top: 15px;
    margin-bottom: 10px;
    width: 100%;
}
</style>
