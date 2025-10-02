<template lang="html">
    <div id="internal-compliance-amend">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Amendment Request" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="amendForm">
                        <alert v-if="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                        <label class="col-form-label float-start"  for="Name">Reason</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <select class="form-select" name="reason" ref="reason" v-model="amendment.reason">
                                            <option v-for="r in reason_choices" :value="r.key" :key="r.key">{{r.value}}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                        <label class="col-form-label float-start"  for="Name">Details</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <textarea class="form-control" name="name" v-model="amendment.text"></textarea>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'

// import { helpers } from "@/utils/hooks.js"
export default {
    name:'compliance-amendment-request',
    components:{
        modal,
        alert
    },
    props:{
            compliance_id:{
                type:Number,
            },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            amendment: {
                reason:'',
                amendingcompliance: false,
                compliance: vm.compliance_id
            },
            reason_choices: {},
            errors: false,
            errorString: '',
            validation_form: null,
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
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
            let vm = this;
            vm.close();
        },
        close:function () {
            this.isModalOpen = false;
            this.amendment = {
                reason: '',
                compliance: this.compliance_id
            };
            this.errors = false;
            $(this.$refs.reason).val(null).trigger('change');
            $('.has-error').removeClass('has-error');

            this.validation_form.resetForm();
        },
        fetchAmendmentChoices: function(){
            let vm = this;
            fetch('/api/compliance_amendment_reason_choices.json')
            .then(async (response) => {
                if (!response.ok) { return response.json().then(err => { throw err }); }
                vm.reason_choices = await response.json();
            }).catch((error) => {
                console.log(error);
            });
        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            //console.log(vm.amendment);
            let amendment = JSON.parse(JSON.stringify(vm.amendment));
            fetch('/api/compliance_amendment_request.json',{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(amendment)
            }).then(async (response)=>{
                //vm.$parent.loading.splice('processing contact',1);
                if (!response.ok) {
                    throw new Error(`Compliance Amendment Request Failed: ${response.status}`);
                }
                const res = await response.json();
                swal.fire(
                        'Sent',
                        'An email has been sent to the proponent with the request to amend this compliance',
                        'success'
                );
                vm.amendingcompliance = true;
                console.log(res)
                vm.close();
                //vm.$emit('refreshFromResponse',response);

                vm.$router.push({ path: '/internal' }); //Navigate to dashboard after creating Amendment request

            }).catch((error)=>{
                console.log(error);
                vm.errors = true;
                // vm.errorString = helpers.apiVueResourceError(error);
                vm.errorString = error.message || 'An error occurred while requesting compliance amendment';
                vm.amendingcompliance = true;
            });


        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    reason: "required"


                },
                messages: {
                    reason: "field is required",

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
       eventListerners:function () {
            let vm = this;

            // Intialise select2
            $(vm.$refs.reason).select2({
                dropdownParent: $(vm.$refs.reason).parent(),
                "theme": "bootstrap-5",
                allowClear: true,
                placeholder:"Select Reason"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.amendment.reason = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.amendment.reason = selected.val();
            });
       }
   },
   mounted:function () {
       let vm =this;
       vm.form = document.forms.amendForm;
       vm.fetchAmendmentChoices();
       vm.addFormValidations();
       this.$nextTick(()=>{
            vm.eventListerners();
        });
    //console.log(validate);
   }
}
</script>

<style lang="css">
</style>
