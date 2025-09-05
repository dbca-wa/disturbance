<template lang="html">
    <div id="approvalSurrender">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="approvalForm">
                        <alert v-if="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">

                                        <label class="control-label pull-left"  for="Name">Surrender Date</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="surrender_date" style="width: 70%;">
                                            <input
                                                v-model="
                                                    approval.surrender_date
                                                "
                                                type="date"
                                                class="form-control"
                                                name="surrender_date"
                                                placeholder="DD/MM/YYYY"
                                                required
                                            />
                                            <div class="invalid-feedback">
                                                Please enter a valid date
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">

                                        <label class="control-label pull-left"  for="Name">Surrender Details</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <textarea name="surrender_details" class="form-control" style="width:70%;" v-model="approval.surrender_details"></textarea>
                                    </div>
                                </div>
                            </div>

                        </div>
                    </form>
                </div>
            </div>
            <template #footer>
                <button type="button" v-if="issuingApproval" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Processing</button>
                <button type="button" v-else class="btn btn-default" @click="ok">Ok</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </template>
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import {helpers,api_endpoints} from "@/utils/hooks.js"
export default {
    name:'Surrender-Approval',
    components:{
        modal,
        alert
    },
    props:{
        //approval_id: {
        //    type: Number,
        //    required: true
        //},
    },
    data:function () {
        // let vm = this;
        return {
            isModalOpen:false,
            form:null,
            approval: {},
            approval_id: Number,
            state: 'proposed_approval',
            issuingApproval: false,
            validation_form: null,
            errors: false,
            errorString: '',
            successString: '',
            success:false,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        title: function(){
            return 'Surrender Approval';
        }
    },
    methods:{
        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();

            }
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            this.isModalOpen = false;
            this.approval = {};
            this.errors = false;
            $('.has-error').removeClass('has-error');
            this.validation_form.resetForm();
        },
        fetchContact: function(id){
            let vm = this;
            fetch(api_endpoints.contact(id)).then(
                async (response) => {
                    if (!response.ok) { return response.json().then(err => { throw err }); }
                    vm.contact = await response.json(); 
                    vm.isModalOpen = true;
                }).catch((error) => {
                    console.log(error);
                });
        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            let approval = JSON.parse(JSON.stringify(vm.approval));
            vm.issuingApproval = true;

            fetch(helpers.add_endpoint_json(api_endpoints.approvals,vm.approval_id+'/approval_surrender'),{
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(approval),
            }).then(async (response)=>{
                if (!response.ok) {
                    //throw new Error(`Approval Surrender failed: ${response.status}`);
                    return response.json().then(err => { throw err });
                }

                const data = await response.json();
                vm.issuingApproval = false;
                vm.close();
                swal.fire(
                        'Surrender',
                        'An email has been sent to the proponent about surrender of this approval',
                        'success'
                );
                vm.$emit('refreshFromResponse',data);

            }).catch((error) => {
                vm.errors = true;
                vm.issuingApproval = false;
                // vm.errorString = helpers.apiVueResourceError(error);
                vm.errorString = error;
            });


        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    to_date:"required",
                    surrender_details:"required",
                },
                messages: {
                    surrender_details:"Field is required",
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
