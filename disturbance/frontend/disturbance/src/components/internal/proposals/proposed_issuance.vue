<template lang="html">
    <div id="proposedIssuanceApproval">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <template v-if="is_local">
                proposed_issuance.vue
            </template>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="approvalForm">
                        <!-- <alert v-if="isApprovalLevelDocument" type="warning"><strong>{{warningString}}</strong></alert> -->
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label v-if="processing_status == 'With Approver'" class="control-label pull-left"  for="Name">Start Date</label>
                                        <label v-else class="control-label pull-left"  for="Name">Proposed Start Date</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="start_date" style="width: 70%;">
                                            <input type="text" class="form-control" name="start_date" placeholder="DD/MM/YYYY" v-model="approval.start_date">
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
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
                                        <div class="input-group date" ref="due_date" style="width: 70%;">
                                            <input type="text" class="form-control" name="due_date" placeholder="DD/MM/YYYY" v-model="approval.expiry_date" :readonly="is_amendment">
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div class="row" v-show="showtoDateError">
                                    <alert  class="col-sm-12" type="danger"><strong>{{toDateErrorString}}</strong></alert>
                    
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
                                <div class="row" v-show="showApprovalCCError">
                                    <alert  class="col-sm-12" type="danger"><strong>{{approvalCCErrorString}}</strong></alert>
                    
                                </div>

                            </div>
                            <div v-if="processing_status != 'With Approver' || !approval.confirmation" class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label>
                                            <input  name="confirmation" type="checkbox" class="control-label pull-left"  v-model="approval.confirmation" /> &nbsp;
                                            As the Assessor I confirm the following.
                                            <ul>
                                                <li>
                                                    The assessment data is up-to-date and used within its limitations.
                                                </li>
                                                <li>
                                                    The management actions are consistent with departmental protocols, management plans, and tenure. 
                                                </li>
                                                <li>
                                                    Where appropriate this proposal includes specialist referral advice, particularly important if this proposal has the potential to significantly affect another output programs (NC, PVS, SFM, FMS).
                                                </li>
                                            </ul>
                                        </label>
                                    </div>
                                    
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label v-if="submitter_email && applicant_email" class="control-label pull-left"  for="Name">After approving this proposal, approval will be emailed to {{submitter_email}} and {{applicant_email}}.</label>
                                        <label v-else class="control-label pull-left"  for="Name">After approving this proposal, approval will be emailed to {{submitter_email}}.</label>
                                    </div>
                                    
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <p v-if="can_preview">Click <a href="#" @click.prevent="preview">here</a> to preview the approval letter.</p>
            <div class="row" v-show="showApplicantAddressError">
                <alert  class="col-sm-12" type="danger"><strong>{{applicantAddressErrorString}}</strong></alert>

            </div>

            <div slot="footer">
                <button type="button" v-if="issuingApproval" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Processing</button>
                <button type="button" v-else-if="approval && approval.start_date && approval.confirmation" class="btn btn-default" @click="ok">Ok</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import {helpers, api_endpoints} from "@/utils/hooks.js"
import moment from 'moment'
export default {
    name:'Proposed-Approval',
    components:{
        modal,
        alert
    },
    props:{
        proposal_id: {
            type: Number,
            required: true
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
        relevant_applicant_address: {
            type: Object,
        },
        relevant_applicant_name: {
            type: String,
        },
        reissued: {
            type: Boolean,
            default: false
        },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            approval: {},
            state: 'proposed_approval',
            issuingApproval: false,
            validation_form: null,
            errors: false,
            applicantAddressError: false,
            applicantAddressErrorString:'',
            toDateError:false,
            startDateError:false,
            errorString: '',
            toDateErrorString:'',
            startDateErrorString:'',
            successString: '',
            success:false,
            approvalCCError: false,
            approvalCCErrorString: '',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            warningString: 'Please attach Level of Approval document before issuing Approval',
            is_local: helpers.is_local(),
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        showApplicantAddressError: function() {
            var vm = this;
            return vm.applicantAddressError;
        },
        showtoDateError: function() {
            var vm = this;
            return vm.toDateError;
        },
        showstartDateError: function() {
            var vm = this;
            return vm.startDateError;
        },
        showApprovalCCError: function() {
            var vm = this;
            return vm.approvalCCError;
        },
        title: function(){
            //return this.processing_status == 'With Approver' ? 'Issue Approval' : 'Propose to issue approval';
            return this.processing_status == 'With Approver' ? 'Issue Approval' : 'Submit to Approver';
        },
        is_amendment: function(){
            return (this.proposal_type == 'Amendment' && !this.reissued) ? true : false;
        },
        csrf_token: function() {
          return helpers.getCookie('csrftoken')
        },
        can_preview: function(){
            return this.processing_status == 'With Approver' && this.validateApplicantAddress() ? true : false;
        },
        preview_licence_url: function() {
          return (this.proposal_id) ? `/preview/licence-pdf/${this.proposal_id}` : '';
        },

    },
    methods:{
        preview:function () {
            let vm =this;
            let formData = new FormData(vm.form)
            // convert formData to json
            let jsonObject = {};
            for (const [key, value] of formData.entries()) {
                jsonObject[key] = value;
            }
            vm.post_and_redirect(vm.preview_licence_url, {'csrfmiddlewaretoken' : vm.csrf_token, 'formData': JSON.stringify(jsonObject)});
        },
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
            if(vm.validateApprovalCC() && !vm.applicantAddressError && $(vm.form).valid()){
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
            $(this.$refs.due_date).data('DateTimePicker').clear();
            $(this.$refs.start_date).data('DateTimePicker').clear();
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
        sendData:function(){
            let vm = this;
            vm.errors = false;
            let approval = JSON.parse(JSON.stringify(vm.approval));
            
            vm.issuingApproval = true;
            if (vm.state == 'proposed_approval'){
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal_id+'/proposed_approval'),JSON.stringify(approval),{
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
            else if (vm.state == 'final_approval'){
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal_id+'/final_approval'),JSON.stringify(approval),{
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
        validateApprovalCC: function() {
            let vm = this;
            const ccRegex = new RegExp(/^(([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5}){1,25})+([,.](([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5}){1,25})+)*$/)
            if (!vm.approval.cc_email || ccRegex.test(vm.approval.cc_email)) {
                vm.approvalCCError = false;
                vm.approvalCCErrorString = '';
                return true;
            }
            else {
                vm.approvalCCError = true;
                vm.approvalCCErrorString = 'Please ensure each BCC email is valid and separated with a ,';
                return false;
            }
        },
        validateApplicantAddress: function() {
            let vm = this;
            if (vm.relevant_applicant_address.hasOwnProperty("id")) {
                vm.applicantAddressError = false;
                vm.applicantAddressErrorString = '';
                return true;
            }
            else {
                vm.applicantAddressError = true;
                vm.applicantAddressErrorString = `The applicant needs to have set their postal address before approving this proposal. (Applicant: ${vm.relevant_applicant_name})`;
                return false;
            }
        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    start_date:"required",
                    due_date:"required",
                    //approval_details:"required",
                },
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
            let today= moment().format('DD/MM/YYYY')
            // Initialise Date Picker
            $(vm.$refs.due_date).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.due_date).on('dp.change', function(e){
                if ($(vm.$refs.due_date).data('DateTimePicker').date()) {
                    if ($(vm.$refs.due_date).data('DateTimePicker').date() < $(vm.$refs.start_date).data('DateTimePicker').date()){
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
                    if (($(vm.$refs.start_date).data('DateTimePicker').date().format('DD/MM/YYYY') < today)&&(!vm.is_amendment)){
                        vm.startDateError = true;
                        vm.startDateErrorString = 'Please select Start date from today';
                        vm.approval.start_date = ""
                    }
                    else if (($(vm.$refs.due_date).data('DateTimePicker').date()!= null)&& ($(vm.$refs.due_date).data('DateTimePicker').date() < $(vm.$refs.start_date).data('DateTimePicker').date())){
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
       }
   },
   mounted:function () {
        let vm =this;
        vm.form = document.forms.approvalForm;
        vm.addFormValidations();
        this.$nextTick(()=>{
            vm.eventListeners();
        });
   }
}
</script>

<style lang="css">
</style>
