<template lang="html">
    <div>
        <div class="form-group">
            <!-- using num_files to determine if files have been uploaded for this question/label (used in disturbance/frontend/disturbance/src/components/external/proposal.vue) -->
            <label :id="id" :num_files="num_documents()">{{label}}</label>
            <span v-if="show_spinner"><i class='fa fa-2x fa-spinner fa-spin'></i></span>
            <!-- <i id="file-spinner" class=""></i> -->
            <!-- <div v-if="numDocuments > 0"> -->
            <div v-if="files">
                <div v-for="v in documents" :key="v.id">
                    <p>
                        File: <a :href="v.file" target="_blank">{{v.name}}</a> &nbsp;
                        <span v-if="!readonly && v.can_delete">
                            <a @click="delete_document(v)" class="fa fa-trash-o" title="Remove file" :filename="v.name" style="cursor: pointer; color:red;"></a>
                        </span>
                        <span v-else-if="!readonly && !v.can_delete && v.can_hide">
                            <a @click="hide_document(v)" class="fa fa-trash-o" title="Remove file" :filename="v.name" style="cursor: pointer; color:red;"></a>
                        </span>
                        <span v-else>
                            <span v-if="!assessorMode">
                                <i class="fa fa-info-circle" aria-hidden="true" title="Previously submitted documents cannot be deleted" style="cursor: pointer;"></i>
                            </span>
                        </span>
                    </p>
                </div>
            </div>
            <div v-if="!readonly">
                <template v-for="n in repeat">
                    <div v-if="isRepeatable || (!isRepeatable && num_documents()==0)" :key="n">
                        <input :name="name" type="file" class="form-control" :data-que="n" :accept="fileTypes" @change="handleChange" :required="isRequired"/>
                        <!-- <alert v-if="showError" type="danger" style="color: red"><strong>{{errorString}}</strong></alert> -->
                    </div>
                </template>
            </div><br v-if="showError">
            <alert v-if="showError" type="danger" style="color: red"><strong>{{errorString}}</strong></alert>

        </div>
         
    </div>
</template>

<script>
import {
  helpers
}
from '@/utils/hooks'
import alert from '@vue-utils/alert.vue'
export default {
    name: 'MapFile',
    props:{
        proposal_id: null,
        name:String,
        label:String,
        id:String,
        isRequired:Boolean,
        assessor_readonly: Boolean,
        assessorMode:{
            default:function(){
                return false;
            },
        },
        value:{
            default:function () {
                return null;
            }
        },
        fileTypes:{
            default:function () {
                var file_types =  
                    ".dbf,.gdb,.gpx,.prj,.shp,.shx," ;
                return file_types;
            }
        },
        isRepeatable:Boolean,
        readonly:Boolean,
        docsUrl: String,
    },
    components: {
        alert,
     },
    data:function(){
        return {
            repeat:1,
            files:[],
            show_spinner: false,
            documents:[],
            filename:null,
            showError:false,
            errorString:'',
        }
    },

    //computed: {
    //    csrf_token: function() {
    //        return helpers.getCookie('csrftoken')
    //    }
    //},

    computed: {
        csrf_token: function() {
            return helpers.getCookie('csrftoken')
        },
        proposal_document_action: function() {
          return (this.proposal_id) ? `/api/proposal/${this.proposal_id}/process_map_document/` : '';
        },
        numDocuments: function() {
            if (this.documents) {
                return this.documents.length;
            }
            return 0;
        },  
    },

    methods:{

        handleChange:function (e) {
            let vm = this;
            vm.showError=false;
            vm.errorString='';
            //vm.show_spinner = true;
            if (vm.isRepeatable) {
                let  el = $(e.target).attr('data-que');
                let avail = $('input[name='+e.target.name+']');
                avail = [...avail.map(id => {
                    return $(avail[id]).attr('data-que');
                })];
                avail.pop();
                if (vm.repeat == 1) {
                    vm.repeat+=1;
                }else {
                    if (avail.indexOf(el) < 0 ){
                        vm.repeat+=1;
                    }
                }
                $(e.target).css({ 'display': 'none'});

            } else {
                vm.files = [];
            }
            vm.files.push(e.target.files[0]);

            if (e.target.files.length > 0) {
                //vm.upload_file(e)
                vm.save_document(e);
            }

            vm.show_spinner = false;
        },

        /*
        upload_file: function(e) {
            let vm = this;
            $("[id=save_and_continue_btn][value='Save Without Confirmation']").trigger( "click" );
        },
		*/

        get_documents: async function() {
            let vm = this;

            var formData = new FormData();
            formData.append('action', 'list');
            formData.append('input_name', vm.name);
            formData.append('csrfmiddlewaretoken', vm.csrf_token);
            await fetch(vm.proposal_document_action, {
                method: 'POST',
                body: formData // No need to set Content-Type; browser handles it for FormData
            })
            .then(async response => {
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(errorText);
                }
                const data = await response.json();
                vm.documents = data;
            })
            // .then(data => {
                
            //     vm.documents = data;
            // })
            .catch(err => {
                console.error('Get documents failed:', err.message);
            });

        },

        delete_document: function(file) {
            let vm = this;
            vm.showError=false;
            vm.errorString='';

            vm.show_spinner = true;
            var formData = new FormData();
            formData.append('action', 'delete');
            formData.append('document_id', file.id);
            formData.append('csrfmiddlewaretoken', vm.csrf_token);

            fetch(vm.proposal_document_action, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    return;
                }
            })
            .then(() => {
                vm.documents = vm.get_documents();
                vm.show_spinner = false;
            })
            .catch(err => {
                console.error('Delete document failed:', err.message);
                vm.show_spinner = false;
            });
        },

        hide_document: function(file) {
            let vm = this;
            vm.showError=false;
            vm.errorString='';
            vm.show_spinner = true;
            var formData = new FormData();
            formData.append('action', 'hide');
            formData.append('document_id', file.id);
            formData.append('csrfmiddlewaretoken', vm.csrf_token);

            fetch(vm.proposal_document_action, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    return;
                }
            })
            .then(() => {
                vm.documents = vm.get_documents(); // Assuming this is a synchronous method
                vm.show_spinner = false;
            })
            .catch(err => {
                console.error('Hide document failed:', err.message);
                vm.show_spinner = false;
            });

        },
        
        uploadFile(e){
            // let vm = this;
            let _file = null;

            if (e.target.files && e.target.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(e.target.files[0]); 
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = e.target.files[0];
            }
            return _file
        },

        save_document: function(e) {
            let vm = this; 
            //var $spinner = $("#file-spinner");
            //$spinner.toggleClass("fa fa-cog fa-spin");
            vm.show_spinner = true;
            if(e.target.files[0].name.length > 255){
                vm.show_spinner=false;
                vm.showError=true;
                vm.errorString='File name exceeds maximum file name length limit';
            }
            else{
            vm.showError=false;
            vm.errorString='';
            var formData = new FormData();
            formData.append('action', 'save');
            formData.append('proposal_id', vm.proposal_id);
            formData.append('input_name', vm.name);
            formData.append('filename', e.target.files[0].name);
            formData.append('_file', vm.uploadFile(e));
            formData.append('csrfmiddlewaretoken', vm.csrf_token);

            fetch(vm.proposal_document_action, {
                method: 'POST',
                body: formData
            })
            .then(async response => {
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(errorText);
                }
                const data = await response.json();
                vm.documents = data;
                //return response.json(); // Assuming the response body is JSON
            })
            // .then(res => {
            //     vm.documents = res.body;
            //     vm.show_spinner = false;
            // })
            .catch(err => {
                vm.show_spinner = false;
                vm.showError = true;
                //vm.errorString = helpers.apiVueResourceError(err);
                vm.errorString = err.message || 'An error occurred while saving the document';
            });
        }
        },

        num_documents: function() {
            if (this.documents) {
                return this.documents.length;
            }
            return 0;
        },

    },
    mounted: async function () {
        let vm = this;
        //vm.documents = vm.get_documents();
        await this.get_documents();
        if (vm.value) {
            //vm.files = (Array.isArray(vm.value))? vm.value : [vm.value];
            if (Array.isArray(vm.value)) {
                vm.value;
            } else {
                var file_names = vm.value.replace(/ /g,'_').split(",")
                vm.files = file_names.map(function( file_name ) { 
                      return {name: file_name}; 
                });
            }
        }
    }
}

</script>

<style lang="css">
    input {
        box-shadow:none;
    }
</style>
