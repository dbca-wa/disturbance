<template lang="html">
    <div id="AddComms">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Test CDD Question" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="commsForm">
                        <alert v-if="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                           <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-6">
                                        <label class="control-label pull-left"  for="Proposal">Proposal Lodgement No.</label>
                                    </div>
                                    <div class="col-sm-6">
                                        <input type="text" class="form-control" name="Proposa_ID" v-model="comms.to">
                                    </div>
                                </div>
                           </div>
                        </div>
                    </form>
                </div>
            </div>
            <template #footer>
                <button type="button" v-if="addingComms" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Testing</button>
                <button type="button" v-else class="btn btn-default" @click="ok">Test</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </template>
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import {helpers} from "@/utils/hooks.js"
export default {
    name:'Test-CDDP-Question',
    components:{
        modal,
        alert
    },
    props:{
        question_id: {
            type: Number,
            required: true
        }

    },
    data:function () {
        // let vm = this;
        return {
            isModalOpen:false,
            form:null,
            proposal_id: Number,
            comms: {},
            state: 'proposed_approval',
            addingComms: false,
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
            files: [
                {
                    'file': null,
                    'name': ''
                }
            ],
            sqs_data: {
                question_id: '',
                proposal_id: '',
            },

        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        title: function(){
            return this.processing_status == 'With Approver' ? 'Issue Comms' : 'Propose to issue approval';
        }
    },
    methods:{
        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
            }
        },
        uploadFile(target,file_obj){
            let _file = null;
            var input = $('.'+target)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]); 
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            file_obj.file = _file;
            file_obj.name = _file.name;
        },
        removeFile(index){
            let length = this.files.length;
            $('.file-row-'+index).remove();
            this.files.splice(index,1);
            this.$nextTick(() => {
                length == 1 ? this.attachAnother() : '';
            });
        },
        attachAnother(){
            this.files.push({
                'file': null,
                'name': ''
            })
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            let vm = this;
            this.isModalOpen = false;
            this.comms = {};
            this.errors = false;
            $('.has-error').removeClass('has-error');
            this.validation_form.resetForm();
            let file_length = vm.files.length;
            this.files = [];
            for (var i = 0; i < file_length;i++){
                vm.$nextTick(() => {
                    $('.file-row-'+i).remove();
                });
            }
            this.attachAnother();
        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            let comms = new FormData(vm.form); 
            vm.addingComms = true;
            vm.$http.post(vm.url,comms,{
                }).then(()=>{
                    vm.addingComms = false;
                    vm.close();
                    //vm.$emit('refreshFromResponse',response);
                },(error)=>{
                    vm.errors = true;
                    vm.addingComms = false;
                    vm.errorString = helpers.apiVueResourceError(error);
                });
            
        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    lodgement_number:"required",
//                    fromm:"required",
//                    type:"required",
//                    subject:"required",
//                    text:"required",
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
   },
   mounted:function () {
        let vm =this;
        vm.form = document.forms.commsForm;
        vm.addFormValidations();
   }
}
</script>

<style lang="css">
.btn-file {
    position: relative;
    overflow: hidden;
}
.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
.top-buffer{margin-top: 5px;}
.top-buffer-2x{margin-top: 10px;}
</style>
