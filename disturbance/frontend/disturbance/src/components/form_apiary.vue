<template lang="html">
    <div>
        <template v-if="is_local">
            form_apiary.vue
        </template>
        <div v-if="is_external" class="col-md-3">
            <div>
                <h3>Application: {{ proposal.lodgement_number }}</h3>
                <h4>Application Type: {{proposal.application_type }}</h4>
                <h4>Status: {{proposal.customer_status }}</h4>
            </div>
        </div>

        <div :class="apiary_sections_classname">
            <ManageUser
                :org_id="proposal.applicant" 
                :isApplication="true" 
                :show_linked="false" 
                :show_address="true" 
                :org_collapse="true" 
                :div_container="false"
                ref="mu_details" 
            />

            <FormSection :formCollapse="false" label="Site Locations" Index="site_locations">
                <div v-if="draftApiaryApplication">

                    <SiteLocations
                        :proposal="proposal"
                        id="site_locations"
                        ref="apiary_site_locations"
                        :is_external="is_external"
                        :is_internal="is_internal"
                        @button_text="button_text"
                        @total_fee_south_west="total_fee_south_west"
                        @total_fee_remote="total_fee_remote"
                        @total_fee_south_west_renewal="total_fee_south_west_renewal"
                        @total_fee_remote_renewal="total_fee_remote_renewal"
                        @num_of_sites_remain_south_west="num_of_sites_remain_south_west"
                        @num_of_sites_remain_remote="num_of_sites_remain_remote"
                        @num_of_sites_remain_south_west_renewal="num_of_sites_remain_south_west_renewal"
                        @num_of_sites_remain_remote_renewal="num_of_sites_remain_remote_renewal"
                        @num_of_sites_south_west_to_add_as_remainder="num_of_sites_south_west_to_add_as_remainder"
                        @num_of_sites_remote_to_add_as_remainder="num_of_sites_remote_to_add_as_remainder"
                        @num_of_sites_south_west_renewal_to_add_as_remainder="num_of_sites_south_west_renewal_to_add_as_remainder"
                        @num_of_sites_remote_renewal_to_add_as_remainder="num_of_sites_remote_renewal_to_add_as_remainder"
                        @total_num_of_sites_on_map_unpaid="total_num_of_sites_on_map_unpaid"
                        @total_num_of_sites_on_map="total_num_of_sites_on_map"
                        @fee_remote_renewal="fee_remote_renewal"
                        @fee_south_west_renewal="fee_south_west_renewal"
                    />

                </div>
                <div v-else>
                    <ComponentSiteSelection
                        :apiary_sites="apiary_sites"
                        :is_internal="is_internal"
                        :is_external="is_external"
                        :show_col_site="false"
                        :show_col_site_when_submitted="true"
                        :show_col_checkbox="false"
                        :show_action_available_unavailable="showActionAvailableUnavailable"
                        :show_col_status="false"
                        :show_col_status_when_submitted="true"
                        :show_col_vacant_when_submitted="show_col_vacant_when_submitted"
                        :key="component_site_selection_key"
                      />
                </div>
            </FormSection>

            <FormSection :formCollapse="false" label="Supporting Application Documents" Index="supporting_application_documents">
                <div class="row">
                    <div class="col-sm-12">
                        <label>
                            Please provide supporting documents to your application this includes site photos, proposed access routes and details on native vegetation clearing (if applicable).
                        </label>
                        <div class="input-file-wrapper">
                            <FileField
                                ref="supporting_application_documents"
                                name="supporting-application-documents"
                                :isRepeatable="true"
                                :documentActionUrl="supportingApplicationDocumentUrl"
                                :readonly="readonly"
                                :replace_button_by_text="true"
                            />
                        </div>
                    </div>
                </div>
            </FormSection>

            <FormSection :formCollapse="false" label="Public Liability Insurance" Index="public_liability_insurance">
                <div class="row">
                    <div class="col-sm-12">
                        <label>
                            <ol type="a" class="insurance-items">
                            <li>Attach your policy for public liability insurance that covers the areas and operations allowed under the apiary authority, and in the name of the applicant to the extent of its rights and interests, for a sum of not less than AU$10 million per event.</li>
                            <li>It is a requirement of all apiary authority holders to maintain appropriate public liability insurance.</li>
                            </ol>
                        </label>
                    </div>
                </div>
                    <div class="my-container input-file-wrapper">
                        <div class="grow1">
                            <label>Certificate of currency</label>
                        </div>
                        <div class="grow2">
                            <FileField
                                ref="public_liability_insurance_documents"
                                name="public-liability-insurance-documents"
                                :isRepeatable="false"
                                :documentActionUrl="publicLiabilityInsuranceDocumentUrl"
                                :readonly="readonly"
                                :replace_button_by_text="true"
                            />
                        </div>
                        <div class="grow1">
                            <label>Expiry Date</label>
                        </div>
                        <div class="grow1">
                            <div class="input-group date" ref="expiryDatePicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" id="expiry_date_input_element" :readonly="readonly"/>
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
            </FormSection>

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
                <ul class="list-unstyled col-sm-12" v-for="q in proposal.proposal_apiary.applicant_checklist_answers">
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
    import ManageUser from '@/components/external/organisations/manage.vue'
    import ComponentSiteSelection from '@/components/common/apiary/component_site_selection.vue'
    import FileField from '@/components/forms/filefield_immediate.vue'
    import FormSection from "@/components/forms/section_toggle.vue"
    import SiteLocations from '@/components/common/apiary/site_locations.vue'
    import ApiaryChecklist from '@/components/common/apiary/section_checklist.vue'
    import uuid from 'uuid'
    import DeedPoll from "@/components/common/apiary/section_deed_poll.vue"
    import { api_endpoints, helpers }from '@/utils/hooks'
    export default {
        name: 'ApiaryForm',
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
            show_col_vacant_when_submitted: {
                type: Boolean,
                default: false
            },
        },
        data:function () {
            let vm = this;
            return{
                values:null,
                pBody: 'pBody'+vm._uid,
                component_site_selection_key: '',
                expiry_date_local: '',
                deed_poll_url: '',
                is_local: helpers.is_local(),
            }
        },
        components: {
            SiteLocations,
            ComponentSiteSelection,
            FileField,
            FormSection,
            ApiaryChecklist,
            DeedPoll,
            ManageUser,
        },
        computed:{
            showVacantWhenSubmitted: function(){
                return this.is_internal
            },
            showActionAvailableUnavailable: function() {
                let show = false
                if(this.is_external){
                    if(this.proposal && ['approved', 'Approved'].includes(this.proposal.customer_status)){
                        show = true
                    }
                }
                return show
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
                        '/api/proposal_apiary/',
                        this.proposal.proposal_apiary.id + '/process_deed_poll_document/'
                    )
                }
                return url;
            },
            supportingApplicationDocumentUrl: function() {
                let url = '';
                if (this.proposal && this.proposal.proposal_apiary) {
                    url = helpers.add_endpoint_join(
                        '/api/proposal_apiary/',
                        this.proposal.proposal_apiary.id + '/process_supporting_application_document/'
                    )
                }
                return url;
            },
            publicLiabilityInsuranceDocumentUrl: function() {
                let url = '';
                if (this.proposal && this.proposal.proposal_apiary) {
                    url = helpers.add_endpoint_join(
                        '/api/proposal_apiary/',
                        this.proposal.proposal_apiary.id + '/process_public_liability_insurance_document/'
                    )
                }
                return url;
            },
            /*
            referralChecklistTitle: function() {
                let title = 'Referral Checklist ';
                if (this.referral &&
                */
            readonly: function() {
                let readonlyStatus = true;
                if (this.proposal.customer_status === 'Draft' && !this.is_internal) {
                    readonlyStatus = false;
                }
                return readonlyStatus;
            },
            assessorChecklistReadonly: function() {
                let readonlyStatus = true;
                if (this.is_internal && this.proposal && this.proposal.assessor_mode && this.proposal.assessor_mode.assessor_can_assess) {
                    readonlyStatus = false;
                }
                return readonlyStatus;
            },
            assessorChecklistVisibility: function() {
                let visibility = false;
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
            apiary_sites: function() {
                if (this.proposal && this.proposal.proposal_apiary) {
                    return this.proposal.proposal_apiary.apiary_sites;
                }
            },
            draftApiaryApplication: function() {
                let draftStatus = false;
                if (this.is_external && this.proposal && this.proposal.application_type === 'Apiary' && this.proposal.customer_status === 'Draft') {
                    draftStatus = true;
                }
                return draftStatus;
            },
            applicantChecklistAnswers: function() {
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.applicant_checklist_answers &&
                    this.proposal.proposal_apiary.applicant_checklist_answers.length > 0) {
                    return this.proposal.proposal_apiary.applicant_checklist_answers;
                }
            },
            assessorChecklistAnswers: function() {
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.assessor_checklist_answers &&
                    this.proposal.proposal_apiary.assessor_checklist_answers.length > 0) {
                    return this.proposal.proposal_apiary.assessor_checklist_answers;
                }
            },
            referrerChecklistAnswers: function() {
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.referrer_checklist_answers &&
                    this.proposal.proposal_apiary.referrer_checklist_answers.length > 0) {
                    return this.proposal.proposal_apiary.referrer_checklist_answers;
                }
            },
          //applicantType: function(){
          //  return this.proposal.applicant_type;
          //},
        },
        methods:{
            fee_remote_renewal: function(value){
                this.$emit('fee_remote_renewal', value)
            },
            fee_south_west_renewal: function(value){
                this.$emit('fee_south_west_renewal', value)
            },
            fetchDeedPollUrl: function(){
                let vm = this;
                vm.$http.get('/api/deed_poll_url').then((response) => {
                    vm.deed_poll_url = response.body;
                },(error) => {
                    console.log(error);
                });
            },
            total_num_of_sites_on_map: function(value){
                this.$emit('total_num_of_sites_on_map', value)
            },
            total_num_of_sites_on_map_unpaid: function(value){
                this.$emit('total_num_of_sites_on_map_unpaid', value)
            },
            addEventListeners: function () {
                let vm = this;
                let el_fr = $(vm.$refs.expiryDatePicker);
                let options = {
                    format: "DD/MM/YYYY",
                    showClear: true ,
                    useCurrent: false,
                };
                el_fr.datetimepicker(options);
                el_fr.on("dp.change", function(e) {
                    if (e.date){
                        // Date selected
                        vm.expiry_date_local= e.date.format('DD/MM/YYYY')  // e.date is moment object
                    } else {
                        // Date not selected
                        vm.expiry_date_local = null;
                    }
                    vm.$emit('expiry_date_changed', vm.expiry_date_local)
                });
                //***
                // Set dates in case they are passed from the parent component
                //***
                let searchPattern = /^[0-9]{4}/
                let expiry_date_passed = vm.proposal.proposal_apiary.public_liability_insurance_expiry_date;
                console.log('passed')
                console.log(expiry_date_passed)
                if (expiry_date_passed) {
                    // If date passed
                    if (searchPattern.test(expiry_date_passed)) {
                        // Convert YYYY-MM-DD to DD/MM/YYYY
                        expiry_date_passed = moment(expiry_date_passed, 'YYYY-MM-DD').format('DD/MM/YYYY');
                    }
                    $('#expiry_date_input_element').val(expiry_date_passed);
                }
            },
            assessorChecklistAnswersPerSite: function(siteId) {
                let siteList = []
                if (this.proposal && this.proposal.proposal_apiary && this.proposal.proposal_apiary.assessor_checklist_answers_per_site &&
                    this.proposal.proposal_apiary.assessor_checklist_answers_per_site.length > 0) {
                    for (let answer of this.proposal.proposal_apiary.assessor_checklist_answers_per_site) {
                        if (answer.apiary_site_id === siteId) {
                            siteList.push(answer)
                        }
                    }
                }
                return siteList;
            },
            referrerChecklistAnswersPerSite: function(referralId, siteId) {
                let siteList = []
                if (this.proposal.proposal_apiary && this.proposal.proposal_apiary.referrer_checklist_answers_per_site) {
                    for (let referral of this.proposal.proposal_apiary.referrer_checklist_answers_per_site) {
                        if (referral.referral_data && referral.referral_data.length > 0) {
                            for (let answer of referral.referral_data) {
                                if (answer.apiary_site_id && answer.apiary_site_id === siteId && answer.apiary_referral_id === referralId) {
                                    siteList.push(answer)
                                }
                            }
                        }
                    }
                }
                console.log(siteList)
                return siteList;
            },
            num_of_sites_south_west_to_add_as_remainder: function(value){
                this.$emit('num_of_sites_south_west_to_add_as_remainder', value)
            },
            num_of_sites_remote_to_add_as_remainder: function(value){
                this.$emit('num_of_sites_remote_to_add_as_remainder', value)
            },
            num_of_sites_south_west_renewal_to_add_as_remainder: function(value){
                this.$emit('num_of_sites_south_west_renewal_to_add_as_remainder', value)
            },
            num_of_sites_remote_renewal_to_add_as_remainder: function(value){
                this.$emit('num_of_sites_remote_renewal_to_add_as_remainder', value)
            },
            button_text: function(button_text) {
                this.$emit('button_text', button_text)
            },
            total_fee_south_west: function(total_fee){
                this.$emit('total_fee_south_west', total_fee)
            },
            total_fee_remote: function(total_fee){
                this.$emit('total_fee_remote', total_fee)
            },
            total_fee_south_west_renewal: function(total_fee){
                this.$emit('total_fee_south_west_renewal', total_fee)
            },
            total_fee_remote_renewal: function(total_fee){
                this.$emit('total_fee_remote_renewal', total_fee)
            },
            num_of_sites_remain_south_west: function(value){
                this.$emit('num_of_sites_remain_south_west', value)
            },
            num_of_sites_remain_remote: function(value){
                this.$emit('num_of_sites_remain_remote', value)
            },
            num_of_sites_remain_south_west_renewal: function(value){
                this.$emit('num_of_sites_remain_south_west_renewal', value)
            },
            num_of_sites_remain_remote_renewal: function(value){
                this.$emit('num_of_sites_remain_remote_renewal', value)
            },
            remove_apiary_site: function(apiary_site_id){
                this.$refs.apiary_site_locations.removeApiarySiteById(apiary_site_id)
            },
            /*
            getChecklistAnswers: function() {
                let vm = this;
                this.checklist_answers.push({
                    'id' : 'this.proposal.proposal_apiary.checklist_answers.id',
                    'answer' : 'this.proposal.proposal_apiary.checklist_answers.answer'
                 })
             return checklist_answers;
            },
            */
        },
        created: function() {
            this.fetchDeedPollUrl()
        },
        mounted: function() {
            let vm = this;
            this.component_site_selection_key = uuid()
            this.$nextTick(() => {
                vm.addEventListeners();
            });
            //vm.form = document.forms.new_proposal;
            //window.addEventListener('beforeunload', vm.leaving);
            //window.addEventListener('onblur', vm.leaving);
        }
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
    .insurance-items {
        padding-inline-start: 1em;
    }
    .my-container {
        display: flex;
        flex-direction: row;
        align-items: center;
    }
    .grow1 {
        flex-grow: 1;
    }
    .grow2 {
        flex-grow: 2;
    }
    .input-file-wrapper {
        margin: 1.5em 0 0 0;
    }
</style>

