<template>
<div class="container" id="externalCompliance">
    <div v-if="isDiscarded" class="row" style="color:red;">
        <h3>You cannot access this Compliance with requirements as this has been discarded.</h3>
    </div>
    <div v-else class="row">
        <div v-if="!isFinalised">
            <div class="col-md-12">
                <div v-if="hasAmendmentRequest" class="row" style="color:red;">
                    <FormSection style="color:red;" :formCollapse="false" label="An amendment has been requested for this Compliance with Requirements" Index="compliance_with_req_amend">
                        <div v-for="a in amendment_request" :key="a.id">                      
                        <p>Reason: {{a.reason}}</p>
                        <p>Details: {{a.text}}</p>                        
                        </div>
                    </FormSection>
                </div>
            </div>
        </div>

        <h3>Compliance with Requirements: {{ compliance.reference }}</h3>

        <div class="col-md-12">
            <div class="row">
                <FormSection :formCollapse="false" label="Compliance with Requirements" Index="compliance_with_req">
                    <div class="row">
                        <div class="col-md-12"> 
                        <form class="form-horizontal" name="complianceForm" method="post">
                            <alert v-if="showError" type="danger">
                                <strong>{{errorString}}</strong>
                            </alert>
                            <div class="row mb-3">
                                <label class="col-sm-3 col-form-label pull-left"  for="Name">Requirement:</label>
                                <div class="col-sm-6">
                                    {{compliance.requirement}}
                                </div>
                            </div>

                            <div class="row mb-3">
                                <label class="col-sm-3 col-form-label pull-left"  for="Name">Details:</label>
                                <div class="col-sm-6">
                                    <textarea :disabled="isFinalised" class="form-control" name="detail" placeholder="" v-model="compliance.text"></textarea>
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div v-if="hasDocuments">
                                    <div class="col-sm-3 col-form-label pull-left" >  
                                        <label  for="Name">Documents:</label>
                                    </div> 
                                    <div class="col-sm-6">
                                        <div class="row" v-for="d in compliance.documents" :key="d.id">
                                            <a :href="d[1]" target="_blank" class="col-form-label pull-left">{{d[0]   }}</a>
                                            <span v-if="!isFinalised && d.can_delete">
                                                <a @click="delete_document(d)" class="fa fa-trash-o col-form-label" title="Remove file" style="cursor: pointer; color:red;"></a>
                                            </span>
                                            <span v-else >
                                                <i class="fa fa-info-circle" aria-hidden="true" title="Previously submitted documents cannot be deleted" style="cursor: pointer;"></i>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div v-if="!isFinalised">
                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                        <label class="col-form-label pull-left" for="Name">Attachments:</label>
                                    </div>
                                    <div class="col-sm-6">
                                        <template v-for="(f,i) in files" :key="i">
                                            <div :class="'row mb-3 top-buffer file-row-'+i">
                                                <div class="col-sm-4">
                                                    <span v-if="f.file == null" class="btn btn-info btn-file btn-primary pull-left">
                                                        Attach File <input type="file" :name="'file-upload-'+i" :class="'file-upload-'+i" @change="uploadFile('file-upload-'+i,f)"/>
                                                    </span>
                                                    <span v-else class="btn btn-info btn-file btn-primary pull-left" style="margin-bottom: 5px">
                                                        Update File <input type="file" :name="'file-upload-'+i" :class="'file-upload-'+i" @change="uploadFile('file-upload-'+i,f)"/>
                                                    </span>
                                                </div>
                                                <div class="col-sm-4">
                                                    <span>{{f.name}}</span>
                                                </div>
                                                <div class="col-sm-4">
                                                    <button @click="removeFile(i)" class="btn btn-danger">Remove</button>
                                                </div>
                                            </div>
                                        </template>
                                        <a href="" @click.prevent="attachAnother"><i class="fa fa-lg fa-plus top-buffer-2x"></i></a>
                                    </div>
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="form-group">
                                    <div class="pull-right">
                                        <button v-if="!isFinalised" @click.prevent="submit()" class="btn btn-primary btn-margin">Submit</button>
                                        <button v-if="!isFinalised" @click.prevent="close()" class="btn btn-secondary">Close</button>
                                    </div>
                                </div>
                            </div>
                        </form>
                        </div>
                    </div>
                </FormSection>
            </div>
        </div>
    </div>
</div>
</template>
<script>
import $ from 'jquery';
import { v4 as uuidv4 } from 'uuid';
import alert from '@vue-utils/alert.vue'
import FormSection from "@/components/forms/section_toggle.vue";
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks';
export default {
  name: 'externalCompliance',
  data() {
    // let vm = this;
    return {
        form:null,
        loading: [],        
        compliance: {},
        original_compliance: {},
        amendment_request: [],
        hasAmendmentRequest: false,
        isFinalised: false,
        errors: false,
        errorString: '',
        pdBody: 'pdBody'+uuidv4(),
        oBody: 'oBody'+uuidv4(),
        hasDocuments: false,
        validation_form: null,
        files: [
                {
                    'file': null,
                    'name': ''
                }
            ]
     
    }
  },
  watch: {
    
    isFinalised: function(){             
        return this.compliance && (this.compliance.customer_status == "Under Review" || this.compliance.customer_status == "Approved");
    },
    hasDocuments: function(){             
        return this.compliance && this.compliance.documents;
    }
  },
  components: {
    alert,
    FormSection,
  },
  computed: {
    showError: function() {
            var vm = this;
            return vm.errors;
        },
    isLoading: function () {
      return this.loading.length > 0;
    },
    isDiscarded: function(){         
        return this.compliance && (this.compliance.customer_status == "Discarded");
    },
    
  },
  methods: {
    formatDate: function(data){
        return moment(data).format('DD/MM/YYYY HH:mm:ss');
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
    submit:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
            }                
                //vm.sendData();
    },

    close:function () {
            let vm = this;           
            this.compliance = {};
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
            vm.$router.push({ name: 'external-proposals-dash'}); //Navigate to dashboard
        },

    addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    detail: "required"
                    
                     
                },
                messages: {              
                    detail: "field is required",
                                         
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


    setAmendmentData: function(amendment_request){
      this.amendment_request = amendment_request;
      
      if (amendment_request.length > 0)
        this.hasAmendmentRequest = true;    
    },

    delete_document: function(doc){
        let vm= this;
        let data = {'document': doc}
        if(doc)
        {
          fetch(helpers.add_endpoint_json(api_endpoints.compliances,vm.compliance.id+'/delete_document'),{
                method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data),
            }).then(async (response)=>{
                if (!response.ok) {
                    throw new Error(`Deleted Document Failed: ${response.status}`);
                }
                const data = await response.json();
                if(data){
                    vm.refreshFromResponse(data);
                    vm.compliance = data;
                }
            }).catch((error)=>{
                vm.errors = true;
                // vm.errorString = helpers.apiVueResourceError(error);
                vm.errorString = error.message;
            });              
        }
    },


    sendData: async function(){
            let vm = this;
            vm.errors = false;
            let data = new FormData(vm.form);
            for (let i = 0; i < vm.files.length; i++) {
                data.append('files', vm.files[i].file);
            }
            vm.addingComms = true;        
            fetch(helpers.add_endpoint_json(api_endpoints.compliances,vm.compliance.id+'/submit'),{
                method: 'POST',
                body: data,
            }).then(async (response)=>{
                if (!response.ok) {
                    throw new Error(`Compliance submit failed: ${response.status}`);
                }
                const data = await response.json();
                if(data){
                    vm.addingCompliance = false;
                    vm.refreshFromResponse(data);                   
                    /*swal.fire(
                    'Submit',
                    'Your Compliance with Requirement has been submitted',
                    'success'
                    );*/
                    vm.compliance = data;
                    vm.$router.push({
                        name: 'submit_compliance',
                        state: {
                            compliance: JSON.stringify(vm.compliance)
                        },
                    });
                }
            }).catch((error)=>{
                vm.errors = true;
                vm.addingCompliance = false;
                vm.errorString = error || 'An error occurred while submitting the compliance';
            });
                
    },

    refreshFromResponse:function(response){
            let vm = this;
            vm.original_compliance = helpers.copyObject(response);
            vm.compliance = helpers.copyObject(response);
            if ( vm.compliance.customer_status == "Under Review" || vm.compliance.customer_status == "Approved" ) { vm.isFinalised = true }
            if (vm.compliance && vm.compliance.documents){ vm.hasDocuments = true}
           
    },  
  },
  mounted: function () {
    let vm = this;
    vm.form = document.forms.complianceForm;
    vm.addFormValidations();     
  },

 beforeRouteEnter: function(to, from, next){
    fetch(helpers.add_endpoint_json(api_endpoints.compliances,to.params.compliance_id)).then(
        async (response) => {
            if (!response.ok) {
                return response.json().then(err => { throw err });
            }
            let compliance_data = await response.json();
            next(vm => {
                vm.compliance = compliance_data;
                if ( vm.compliance.customer_status == "Under Review" || vm.compliance.customer_status == "Approved" ) { vm.isFinalised = true }
                if (vm.compliance && vm.compliance.documents){ vm.hasDocuments = true}

                fetch(helpers.add_endpoint_json(api_endpoints.compliances,to.params.compliance_id+'/amendment_request')).then(
                    async (res) => { 
                        if (!res.ok) {
                            return res.json().then(err => { throw err });
                        }    
                        let amend_data = await res.json();                
                        vm.setAmendmentData(amend_data);                  
                    }).catch(err => {
                            console.log(err);
                    });
            })
        }).catch((error) => {
            console.log(error);
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
.top-buffer{margin-top: 0px;}
.top-buffer-2x{margin-top: 0px;}
</style>
