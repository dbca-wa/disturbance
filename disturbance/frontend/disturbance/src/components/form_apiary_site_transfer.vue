<template lang="html">
    <div>
        <div v-if="is_external" class="col-md-3">
            <div>
                <h3>Application: {{ proposal.lodgement_number }}</h3>
                <h4>Application Type: {{proposal.application_type }}</h4>
                <h4>Status: {{proposal.customer_status }}</h4>
            </div>
        </div>

        <div :class="apiary_sections_classname">
            <!--FormSection :formCollapse="false" label="Site Locations" Index="site_locations">
                <SiteLocations
                    :proposal="proposal"
                    id="site_locations"
                    ref="apiary_site_locations"
                    :is_external="is_external"
                    :is_internal="is_internal"
                    @button_text="button_text"
                />
            </FormSection-->
            <FormSection :formCollapse="false" label="Transferee" Index="transferee">
                <!--span class="row col-sm-12"-->
                <div v-if="is_external" class="row col-sm-12">
                    <div class="form-group">
                        <!--div class="row form-control">
                            <label class="inline">Title:</label>
                        </div-->
                        <label class="col-sm-6 emailLabel">Enter the email address of the licence holder you want to transfer sites to:</label>
                        <input
                            type="text"
                            class="form-control"
                            v-model="transfereeEmail"
                            :readonly="readonly"
                        />
                        <input type="button" @click="lookupTransferee" value="Find licence details" class="btn btn-primary">
                    </div>
                    <div class="form-group">
                            <div class="col-sm-12">
                                <div v-if="lookupErrorText">
                                    {{lookupErrorText}}
                                </div>
                                <div v-if="lookupNotification">
                                    {{lookupNotification}}
                                </div>
                                <div v-else-if="licenceHolders && licenceHolders.length">
                                    <!--label class="col-sm-6 emailLabel">Select the licence you want to transfer to:</label-->
                                    <label>Select the licence you want to transfer to:</label>
                                    <div v-for="holder in licenceHolders">
                                        <!--input type="radio" name="approval_choice" :value="approval.id" v-model="proposal.proposal_apiary.selected_licence"/-->
                                        <input type="radio" name="holder_choice" :value="holder" v-model="selectedLicenceHolder" :disabled="readonlyLicenceHolders"/>
                                        <span v-if="holder.lodgement_number">

                                            {{ holder.licence_holder }}: Licence {{holder.lodgement_number}}
                                        </span>
                                        <span v-else>
                                            {{ holder.licence_holder }}: create new licence
                                        </span>
                                    </div>
                                </div>
                                <div v-else-if="targetApprovalLodgementNumber">
                                    <div><label>Transferee Email:</label> {{ transfereeEmailText }}</div>
                                    <div><label>Licence:</label> {{targetApprovalLodgementNumber}}</div>
                                </div>
                            </div>
                    </div>

                </div>
                <div v-else>
                    <div v-if="transfereeOrgName" class="col-sm-8">
                        Organisation Name: {{ transfereeOrgName }}
                    </div>
                    <div v-else>
                        <div class="col-sm-8">
                            First Name: {{ transfereeFirstName }}
                        </div>
                        <div class="col-sm-8">
                            Last Name: {{ transfereeLastName }}
                        </div>
                    </div>
                    <div class="col-sm-8">
                        <span v-if="targetApprovalLodgementNumber">
                            Licence: {{ targetApprovalLodgementNumber }}
                        </span>
                        <span v-else>
                            Licence: to be created
                        </span>
                    </div>
                </div>
                <!--/span-->
                <!--div class="row col-sm-12">
                    <div class="form-group">
                        <div v-if="lookupErrorText">
                            Error: {{lookupErrorText}}
                        </div>
                        <div v-else-if="apiaryApprovals">
                            <div v-for="approval in apiaryApprovals">
                                <input type="radio" name="approval_choice" :value="approval.id" v-model="proposal.proposal_apiary.selected_licence"/>
                                Licence: {{approval.lodgement_number}}
                            </div>
                        </div>
                        <div v-else-if="targetApprovalLodgementNumber">
                            Licence: {{targetApprovalLodgementNumber}}
                        </div>
                    </div>
                </div-->

            </FormSection>
           
            <!--
            <FormSection :formCollapse="false" label="Deed Poll" Index="deed_poll">
                <div class="row">
                    <div class="col-sm-12">
                        <label>Print <a :href="deedPollUrl" target="_blank">the deed poll</a>, sign it, have it witnessed and attach it to this application.</label>
                    </div>
                </div>
                <div class="row">
                    <div class="col-sm-12">
                        <FileField
                            ref="deed_poll_documents"
                            name="deed-poll-documents"
                            :isRepeatable="false"
                            :documentActionUrl="deedPollDocumentUrl"
                            :readonly="readonly"
                            :replace_button_by_text="true"
                        />
                    </div>
                </div>
            </FormSection>
            -->

            <FormSection :formCollapse="false" label="Deed Poll" Index="deed_poll">
                <DeedPoll
                    ref="deed_poll_component"
                    :isRepeatable="false"
                    :isReadonly="readonly"
                    :documentActionUrl="deedPollDocumentUrl"
                />
            </FormSection>

            <ApiaryChecklist
                :checklist="applicantChecklistAnswers"
                section_title="Applicant Checklist"
                :readonly="readonly"
                ref="applicant_checklist"
                index="1"
            />
            <div v-if="assessorChecklistVisibility">
                <ApiaryChecklist
                :checklist="assessorChecklistAnswers"
                section_title="Assessor Checklist"
                :readonly="assessorChecklistReadonly"
                ref="assessor_checklist"
                index="2"
                />
                <div v-for="site in apiary_sites">
                    <ApiaryChecklist
                    :checklist="assessorChecklistAnswersPerSite(site.id)"
                    :section_title="'Assessor checklist for site ' + site.id"
                    :readonly="assessorChecklistReadonly"
                    v-bind:key="'assessor_checklist_per_site_' + site.id"
                    :index="'2_' + site.id"
                    />
                </div>
            </div>
            <div v-for="r in referrerChecklistAnswers">
                <!--div v-if="(referral && r.referral_id === referral.id) || (assessorChecklistVisibility && proposal.processing_status === 'With Assessor')"-->
                <div v-if="(referral && r.referral_id === referral.id) || (assessorChecklistVisibility)">
                <!--div v-if="r.id = referral.id"-->
                    <ApiaryChecklist
                    :checklist="r.referral_data"
                    :section_title="'Referral Checklist: ' + r.referrer_group_name"
                    :readonly="referrerChecklistReadonly"
                    ref="referrer_checklist"
                    index="3"
                    />
                    <div v-for="site in apiary_sites">
                        <ApiaryChecklist
                        :checklist="referrerChecklistAnswersPerSite(r.apiary_referral_id, site.id)"
                        :section_title="'Referral Checklist: ' + r.referrer_group_name + ' for site ' + site.id"
                        :readonly="referrerChecklistReadonly"
                        v-bind:key="'referrer_checklist_per_site_' + r.apiary_referral_id + site.id"
                        :index="'3_' + r.apiary_referral_id + '_' + site.id"
                        />
                    </div>
                </div>
            </div>


            <!--FormSection :formCollapse="false" label="Checklist" Index="checklist">
                <ul class="list-unstyled col-sm-12" v-for="q in proposal.proposal_apiary.checklist_answers">
                    <div class="row">
                        <div class="col-sm-12">
                            <li class="col-sm-6">
                                <label class="control-label">{{q.question.text}}</label>
                            </li>

                            <ul  class="list-inline col-sm-6">
                                <li class="list-inline-item">
                                    <input  class="form-check-input" v-model="q.answer" ref="Checkbox" type="radio" :name="'option'+q.id" :id="'answer_one'+q.id":value="true" data-parsley-required :disabled="readonly"/> Yes
                                </li>
                                <li class="list-inline-item">
                                    <input  class="form-check-input" v-model="q.answer" ref="Checkbox" type="radio" :name="'option'+q.id" :id="'answer_two'+q.id" :value="false" data-parsley-required :disabled="readonly"/> No
                                </li>
                            </ul>
                        </div>
                    </div>
                </ul>
            </FormSection-->
        </div>

    </div>
</template>

<script>

    import FileField from '@/components/forms/filefield_immediate.vue'
    import FormSection from "@/components/forms/section_toggle.vue"
    import ApiaryChecklist from '@/components/common/apiary/section_checklist.vue'
    import {v4 as uuidv4 } from 'uuid';
    import DeedPoll from "@/components/common/apiary/section_deed_poll.vue"
    import { api_endpoints, helpers }from '@/utils/hooks'

    export default {
        name: 'ApiarySiteTransferForm',
        props:{
            proposal:{
                type: Object,
                required:true
            },
            canEditActivities:{
              type: Boolean,
              default: true
            },
            is_external:{
              type: Boolean,
              default: false
            },
            is_internal:{
              type: Boolean,
              default: false
            },
            is_referral:{
              type: Boolean,
              default: false
            },
            hasReferralMode:{
                type:Boolean,
                default: false
            },
            hasAssessorMode:{
                type:Boolean,
                default: false
            },
            referral:{
                type: Object,
                required:false
            },
            proposal_parks:{
                type:Object,
                default:null
            },
        },
        data:function () {
            let vm=this;
            return{
                values:null,
                pBody: 'pBody'+vm._uid,
                checklist_answers : [],
                transfereeEmail: '',
                //apiaryApprovals: {},
                //apiaryApprovals: null,
                licenceHolders: null,
                lookupErrorText: '',
                lookupNotification: '',
                selectedLicenceHolder: null,
                component_site_selection_key: '',
                apiary_sites_local: [],
                siteTransferFees: [],
                num_of_sites_selected: null,
                //applicationFee: null,
            }
        },
        components: {
            //SiteLocations,
            FileField,
            FormSection,
            ApiaryChecklist,
            DeedPoll,
        },
        watch: {
            applicationFee: function() {
                this.$nextTick(() => {
                    this.$emit('site_transfer_application_fee', this.applicationFee);
                });
            },
            licenceHolders: function() {
                this.$nextTick(() => {
                    console.log(this.readonlyLicenceHolders)
                    if (this.readonlyLicenceHolders) {
                        // only one option available
                        this.selectedLicenceHolder = this.licenceHolders[0];
                    } else if (this.proposal.proposal_apiary.target_approval_id) {
                        // approval has already been selected
                        for (let holder of this.licenceHolders) {
                            if (holder.id === this.proposal.proposal_apiary.target_approval_id) {
                                this.selectedLicenceHolder = holder;
                            }
                        }
                    } else if (this.proposal.proposal_apiary.transferee_id) {
                        // transferee_id and/or target_approval_organisation_id have already been selected
                        for (let holder of this.licenceHolders) {
                            if (holder.transferee_id === this.proposal.proposal_apiary.transferee_id && 
                                (!this.proposal.proposal_apiary.target_approval_organisation_id || 
                                    this.proposal.proposal_apiary.target_approval_organisation_id === holder.organisation_id)
                            ) {
                                this.selectedLicenceHolder = holder;
                            }
                        }
                    } else {
                        this.selectedLicenceHolder = null;
                    }
                });
            },
            selectedLicenceHolder: function() {
                this.$emit('selectedLicenceHolderChanged', this.selectedLicenceHolder)
            },
        },
        computed:{
            readonlyLicenceHolders: function() {
                let readonly = true;
                if (this.licenceHolders && this.licenceHolders.length > 1) {
                    readonly = false;
                }
                return readonly;
            },
            remoteSiteTransferFee: function() {
                let remoteFee = null;
                if (this.siteTransferFees && this.siteTransferFees.length) {
                    for (let fee of this.siteTransferFees) {
                        if (fee.site_category.name === 'remote') {
                            remoteFee = fee.amount;
                        }
                    }
                }
                return remoteFee
            },
            southWestSiteTransferFee: function() {
                let southWestFee = null;
                if (this.siteTransferFees && this.siteTransferFees.length) {
                    for (let fee of this.siteTransferFees) {
                        if (fee.site_category.name === 'south_west') {
                            southWestFee = fee.amount;
                        }
                    }
                }
                return southWestFee;
            },
            applicationFee: function() {
                let totalFee = 0;
                if (this.apiary_sites_local && this.apiary_sites_local.length && this.southWestSiteTransferFee && this.remoteSiteTransferFee) {
                    for (let site of this.apiary_sites_local) {
                        if (site.checked && site.properties.site_category === 'remote') {
                            //totalFee += parseFloat(this.remoteSiteTransferFee);
                            totalFee += parseFloat(this.remoteSiteTransferFee);
                        } else if (site.checked && site.properties.site_category === 'south_west') {
                            //totalFee += parseFloat(this.southWestSiteTransferFee);
                            totalFee += parseFloat(this.southWestSiteTransferFee);
                        }
                    }
                }
                //console.log(totalFee)
                //console.log(typeof(totalFee))
                return parseFloat(totalFee).toFixed(2);
            },

            getUnansweredChecklistQuestions: function() {
                let UnansweredChecklistQuestions = false;

                if(this.applicantChecklistAnswers){
                    let numOfAnswers = this.applicantChecklistAnswers.length;
                    for( let i=0; i< numOfAnswers ; i ++){
                        if(this.applicantChecklistAnswers[i].answer == null && !this.applicantChecklistAnswers[i].text_answer){
                            UnansweredChecklistQuestions = true;
                        }
                    }
                }
                return UnansweredChecklistQuestions;
            },
            applicantChecklistAnswers: function() {
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.applicant_checklist_answers &&
                    this.proposal.proposal_apiary.applicant_checklist_answers.length > 0) {
                    return this.proposal.proposal_apiary.applicant_checklist_answers;
                }
            },
            transfereeName: function() {
                if (this.proposal && this.proposal.proposal_apiary) {
                    return this.proposal.proposal_apiary.transferee_name;
                }
            },
            transfereeOrgName: function() {
                if (this.proposal && this.proposal.proposal_apiary) {
                    return this.proposal.proposal_apiary.transferee_org_name;
                }
            },
            transfereeFirstName: function() {
                if (this.proposal && this.proposal.proposal_apiary) {
                    return this.proposal.proposal_apiary.transferee_first_name;
                }
            },
            transfereeLastName: function() {
                if (this.proposal && this.proposal.proposal_apiary) {
                    return this.proposal.proposal_apiary.transferee_last_name;
                }
            },
            targetApprovalLodgementNumber: function() {
                if (this.proposal && this.proposal.proposal_apiary) {
                    return this.proposal.proposal_apiary.target_approval_lodgement_number;
                }
            },
            transfereeEmailText: function() {
                if (this.proposal && this.proposal.proposal_apiary) {
                    return this.proposal.proposal_apiary.transferee_email_text;
                }
            },
            apiary_sections_classname: function() {
                // For external page, we need 'col-md-9' classname
                // but not for the internal.
                // This is a hacky way, though...
                if(this.is_internal){
                    return ''
                } else {
                    return 'col-md-9'
                }
            },
            deedPollDocumentUrl: function() {
                let url = '';
                if (this.proposal && this.proposal.proposal_apiary) {
                    url = helpers.add_endpoint_join(
                        //api_endpoints.proposal_apiary,
                        '/api/proposal_apiary/',
                        this.proposal.proposal_apiary.id + '/process_deed_poll_document/'
                        )
                }
                return url;
            },
            deedPollUrl: function() {
                return '';
            },
            readonly: function() {
                let readonlyStatus = true;
                if (this.proposal.customer_status === 'Draft' && !this.is_internal) {
                    readonlyStatus = false;
                }
                return readonlyStatus;
            },
            /*
            getUnansweredChecklistQuestions: function() {
                let UnansweredChecklistQuestions = false;

                if(this.proposal && this.proposal.proposal_apiary.checklist_answers){
                    let numOfAnswers = this.proposal.proposal_apiary.checklist_answers.length;
                    for( let i=0; i< numOfAnswers ; i ++){
                        //console.log('ans [ '+i+'] '+this.proposal.proposal_apiary.checklist_answers[i].answer)
                        if(this.proposal.proposal_apiary.checklist_answers[i].answer == null){
                            UnansweredChecklistQuestions = true;
                        }
                    }
                }
                return UnansweredChecklistQuestions;
            },
            */
            apiary_sites: function() {
                let sites = []
                if (this.proposal && this.proposal.proposal_apiary) {
                    for (let site of this.proposal.proposal_apiary.transfer_apiary_sites) {
                        // show all sites in Draft; only selected sites after customer submits
                        if (this.proposal.customer_status === 'Draft' || site.customer_selected) {
                            sites.push(site.apiary_site);
                        }
                    }
                }
                return sites;
            },
            showColCheckbox: function() {
                let show = false;
                if (this.proposal && this.proposal.customer_status === 'Draft') {
                    show = true;
                }
                return show;
            },
            /*
            receivingApprovalLodgementNumber: function() {
                let lodgement_number = '';
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.receiving_approval_lodgement_number) {
                    lodgement_number = this.proposal.proposal_apiary.receiving_approval_lodgement_number;
                }
                return lodgement_number;
            },
            */
            /*
            selectedLicence: function() {
                let licence = null;
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.target_approval_lodgement_number) {
                    licence = this.proposal.proposal_apiary.target_approval_lodgement_number;
                } else if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.selected_licence) {
                    licence = this.proposal.proposal_apiary.selected_licence;
                }
                return licence;
            },
            */
            /*
            site_transfer_apiary_sites: function(){
                let sites = []
                if (this.proposal && this.proposal.proposal_apiary) {
                    for (let site of this.proposal.proposal_apiary.site_transfer_apiary_sites) {
                        sites.push({'id': site.id, 'checked': site.apiary_site.checked})
                    }
                }
                return sites;
            },
            */
          //applicantType: function(){
          //  return this.proposal.applicant_type;
          //},
            assessorChecklistReadonly: function() {
                let readonlyStatus = true;
                //if (this.proposal.processing_status === 'With Assessor' && this.is_internal) {
                if (this.is_internal && this.proposal && this.proposal.assessor_mode && this.proposal.assessor_mode.assessor_can_assess) {
                    readonlyStatus = false;
                }
                return readonlyStatus;
            },
            assessorChecklistVisibility: function() {
                let visibility = false;
                //if (this.proposal.processing_status === 'With Assessor' && this.is_internal) {
                if (this.is_internal && this.proposal && this.proposal.assessor_mode && this.proposal.assessor_mode.has_assessor_mode) {
                    visibility = true;
                }
                return visibility;
            },
            referrerChecklistReadonly: function() {
                let readonlyStatus = true;
                // referrer must have access
                if (this.is_internal && this.proposal.processing_status === 'With Referral' &&
                    this.referral && this.referral.processing_status === 'Awaiting' &&
                    this.referral.apiary_referral && this.referral.apiary_referral.can_process) {
                    readonlyStatus = false;
                }
                return readonlyStatus;
            },
            referrerChecklistVisibility: function() {
                let visibility = false;
                // must be relevant referral
                if ((!this.referrerChecklistReadonly && r.id === this.referral.id) || this.assessorChecklistVisibility) {
                    visibility = true;
                }
                return visibility;
            },
            assessorChecklistAnswers: function() {
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.site_transfer_assessor_checklist_answers &&
                    this.proposal.proposal_apiary.site_transfer_assessor_checklist_answers.length > 0) {
                    return this.proposal.proposal_apiary.site_transfer_assessor_checklist_answers;
                }
            },
            referrerChecklistAnswers: function() {
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.site_transfer_referrer_checklist_answers &&
                    this.proposal.proposal_apiary.site_transfer_referrer_checklist_answers.length > 0) {
                    return this.proposal.proposal_apiary.site_transfer_referrer_checklist_answers;
                }
            },

        },
        methods:{
            assessorChecklistAnswersPerSite: function(siteId) {
                let siteList = []
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.site_transfer_assessor_checklist_answers_per_site &&
                    this.proposal.proposal_apiary.site_transfer_assessor_checklist_answers_per_site.length > 0) {
                    for (let answer of this.proposal.proposal_apiary.site_transfer_assessor_checklist_answers_per_site) {
                        if (answer.apiary_site_id === siteId) {
                            siteList.push(answer)
                        }
                    }
                }
                return siteList;
            },
            referrerChecklistAnswersPerSite: function(referralId, siteId) {
                let siteList = []
                if (this.proposal.proposal_apiary && this.proposal.proposal_apiary.site_transfer_referrer_checklist_answers_per_site) {
                    for (let referral of this.proposal.proposal_apiary.site_transfer_referrer_checklist_answers_per_site) {
                        if (referral.referral_data && referral.referral_data.length > 0) {
                            for (let answer of referral.referral_data) {
                                if (answer.apiary_site_id === siteId && answer.apiary_referral_id === referralId) {
                                    siteList.push(answer)
                                }
                            }
                        }
                    }
                }
                console.log(siteList)
                return siteList;
            },

            apiarySitesUpdated: function(apiarySitesLocal) {
                this.apiary_sites_local = apiarySitesLocal;
                // Update this.num_of_sites_selected
                let temp = 0
                for (let i=0; i<this.apiary_sites_local.length; i++){
                    if (this.apiary_sites_local[i].checked){
                        temp += 1
                    }
                }
                this.num_of_sites_selected = temp
            },
            button_text: function(button_text) {
                this.$emit('button_text', button_text)
            },
            getChecklistAnswers: function() {
                let vm = this;
                this.checklist_answers.push({
                    'id' : 'this.proposal.proposal_apiary.checklist_answers.id',
                    'answer' : 'this.proposal.proposal_apiary.checklist_answers.answer'
                 })
             return checklist_answers;
            },
            lookupTransferee: function() {
                this.lookupErrorText = '';
                this.lookupNotification = '';
                console.log(this.transfereeEmail);
                //let url = `/api/proposal_apiary/${this.proposal.proposal_apiary.id}/get_apiary_approvals.json`
                Vue.http.post(helpers.add_endpoint_json(
                    api_endpoints.proposal_apiary,this.proposal.proposal_apiary.id+'/get_licence_holders'),
                    //data,{
                    {
                        'user_email': this.transfereeEmail,
                        'originating_approval_id': this.proposal.proposal_apiary.originating_approval_id,
                    }).then(res => {
                        console.log(res.body);
                        if (res.body && res.body.licence_holders) {
                            this.licenceHolders = res.body.licence_holders.licence_holders;
                            //this.apiaryApprovals = res.body.apiary_approvals.approvals;
                            /*
                            if (this.licenceHolders.length < 1) {
                                //this.lookupErrorText = 'No current licence for the transferee';
                                this.lookupNotification = 'No current licence for the transferee - one will be created';
                            }
                            */
                        } else {
                            this.lookupErrorText = res.body;
                        }
                },
                err => {
                  console.log(err);
                });

            },

        },
        mounted: function() {
            //let vm = this;
            this.component_site_selection_key = uuidv4()
            // set initial checked status
            if (this.proposal && this.proposal.proposal_apiary) {
                for (let site of this.proposal.proposal_apiary.transfer_apiary_sites) {
                    if (this.is_external) {
                        site.apiary_site.checked = site.customer_selected;
                    } else {
                        site.apiary_site.checked = site.internal_selected;
                    }
                }
            }
            Vue.http.get(api_endpoints.apiary_site_transfer_fees)
                .then(res => {
                    for (let fee of res.body) {
                        this.siteTransferFees.push(fee)
                    }
            },
            err => {
              console.log(err);
            });
            // update transferreeEmail
            if (this.proposal && this.proposal.proposal_apiary) {
                this.transfereeEmail = this.proposal.proposal_apiary.transferee_email_text;
            }
            this.$nextTick(() => {
                if (this.transfereeEmail) {
                    this.lookupTransferee();
                }
            })

            //vm.form = document.forms.new_proposal;
            //window.addEventListener('beforeunload', vm.leaving);
            //window.addEventListener('onblur', vm.leaving);
        },
    }
</script>

<style lang="css" scoped>
    .section{
        text-transform: capitalize;
    }
    .list-group{
        margin-bottom: 0;
    }
    .fixed-top{
        position: fixed;
        top:56px;
    }
    .emailLabel{
        text-align: left;
    }
</style>

