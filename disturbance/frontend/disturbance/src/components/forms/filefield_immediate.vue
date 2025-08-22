<template lang="html">
    <div class="ffu-wrapper">
        <label :id="id" :num_files="num_documents()" style="display: none;">{{label}}</label>
        <!--template v-if="help_text">
            <HelpText :help_text="help_text" />
        </template-->

        <!--template v-if="help_text_url">
            <HelpTextUrl :help_text_url="help_text_url" />
        </template-->

        <!--CommentBlock 
            :label="label"
            :name="name"
            :field_data="field_data"
            /-->

        <template v-if="files">
            <template v-for="v in documents" :key="v.id">
                <div>
                    File: <a :href="v.file" target="_blank">{{v.name}}</a> &nbsp;
                    <span v-if="!readonly">
                        <a @click="delete_document(v)" class="fa fa-trash-o" title="Remove file" :filename="v.name" style="cursor: pointer; color:red;"></a>
                    </span>
                </div>
            </template>
            <div v-if="show_spinner"><i class='fa fa-2x fa-spinner fa-spin'></i></div>
        </template>
        <template v-if="!readonly">
            <template v-for="n in repeat" :key="n">
                <template v-if="isRepeatable || (!isRepeatable && num_documents()==0) && !show_spinner">
                    <input 
                        :id="name + n" 
                        :name="name" type="file" 
                        :data-que="n" 
                        :accept="fileTypes" 
                        @change="handleChangeWrapper" 
                        :class="ffu_input_element_classname" />
                    <template v-if="replace_button_by_text">
                        <span :id="'button-' + name + n" @click="button_clicked(name + n)" class="ffu-input-text">{{ text_string }}</span>
                    </template>
                </template>
            </template>
        </template>
    </div>
</template>

<script>
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks';
export default {
    name: "FileField",
    props:{
        name:String,
        label:String,
        id:String,
        fileTypes:{
            default:function () {
                var file_types = 
                    "image/*," + 
                    "video/*," +
                    "audio/*," +
                    "application/pdf,text/csv,application/msword,application/vnd.ms-excel,application/x-msaccess," +
                    "application/x-7z-compressed,application/x-bzip,application/x-bzip2,application/zip," + 
                    ".dbf,.gdb,.gpx,.prj,.shp,.shx," + 
                    ".json,.kml,.gpx,.txt,";
                return file_types;
            }
        },
        isRepeatable:Boolean,
        readonly:Boolean,
        documentActionUrl: String,

        // For optional text button
        replace_button_by_text: {
            type: Boolean,
            default: false
        },
        text_string: {
            type: String,
            default: 'Attach Document'
        }
    },
    //components: {CommentBlock, HelpText},
    data:function(){
        return {
            repeat:1,
            files:[],
            show_spinner: false,
            documents:[],
            filename:null,
            help_text_url:'',
            commsLogId: null,
            temporary_document_collection_id: null,
            //document_action_url: this.documentActionUrl,
        }
    },
    computed: {
        ffu_input_element_classname: function(){
            if (this.replace_button_by_text){
                return 'ffu-input-elem'
            }
            return ''
        },
        csrf_token: function() {
            return helpers.getCookie('csrftoken')
        },
        document_action_url: function() {
            let url = ''
            if (this.documentActionUrl == 'temporary_document') {
                if (!this.temporary_document_collection_id) {
                    url = api_endpoints.temporary_document
                } else {
                    url = api_endpoints.temporary_document + this.temporary_document_collection_id + '/process_temp_comms_log_document/'
                }
            } else {
                url = this.documentActionUrl
            }
            return url;
        },
    },
    watch: {
        documents: {
            handler: async function () {
                await this.$emit('update-parent');
            },
            deep: true
        },
    },

    methods:{
        button_clicked: function(value){
            if(this.replace_button_by_text){
                $("#" + value).trigger('click');
            }
        },
        handleChange: function (e) {
            let vm = this;

            if (vm.isRepeatable && e.target.files) {
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
                this.$nextTick(() => {
                    this.save_document(e);
                });
            }

        },

        get_documents: async function() {
            this.show_spinner = true;

            if (this.document_action_url) {
                var formData = new FormData();
                formData.append('action', 'list');
                if (this.commsLogId) {
                    formData.append('comms_log_id', this.commsLogId);
                }
                formData.append('input_name', this.name);
                formData.append('csrfmiddlewaretoken', this.csrf_token);
                try {
                    const response = await fetch(this.document_action_url, {
                        method: 'POST',
                        body: formData,
                        credentials: 'same-origin' // Ensures cookies like CSRF token are sent
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }

                    const data = await response.json();
                    this.documents = data.filedata;
                    this.commsLogId = data.comms_instance_id;
                } catch (error) {
                    console.error('Fetch error:', error);
                    // Optionally handle error state here
                }

            }
            this.show_spinner = false;

        },

        delete_document: async function(file) {
            this.show_spinner = true;

            var formData = new FormData();
            formData.append('action', 'delete');
            formData.append('input_name', this.name);
            if (this.commsLogId) {
                formData.append('comms_log_id', this.commsLogId);
            }
            formData.append('document_id', file.id);
            formData.append('csrfmiddlewaretoken', this.csrf_token);
            if (this.document_action_url) {
                try {
                    const response = await fetch(this.document_action_url, {
                        method: 'POST',
                        body: formData,
                        credentials: 'same-origin'
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }

                    const data = await response.json();
                    this.documents = data.filedata;
                    this.commsLogId = data.comms_instance_id;
                } catch (error) {
                    console.error('Fetch error:', error);
                    // Optionally handle error state here
                }
            }
            //vm.documents = res.body;
            this.show_spinner = false;

        },
        cancel: async function() {
            this.show_spinner = true;

            let formData = new FormData();
            formData.append('action', 'cancel');
                formData.append('input_name', this.name);
            if (this.commsLogId) {
                formData.append('comms_log_id', this.commsLogId);
            }
            formData.append('csrfmiddlewaretoken', this.csrf_token);
            if (this.document_action_url) {
                try {
                    const response = await fetch(this.document_action_url, {
                        method: 'POST',
                        body: formData,
                        credentials: 'same-origin'
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }

                } catch (error) {
                    console.error('Fetch error:', error);
                }
            }
            this.show_spinner = false;
        },
        
        uploadFile(e){
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

        handleChangeWrapper: async function(e) {
            if (this.documentActionUrl === 'temporary_document' && !this.temporary_document_collection_id) {
                // If temporary_document, create TemporaryDocumentCollection object and allow document_action_url to update
                try {
                    const response = await fetch(this.document_action_url, {
                        method: 'POST',
                        credentials: 'same-origin'
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }

                    const data = await response.json();
                    this.temporary_document_collection_id = data.id;

                    await this.$emit('update-temp-doc-coll-id', {
                        temp_doc_id: this.temporary_document_collection_id,
                        input_name: this.name,
                    });

                    this.$nextTick(async () => {
                        this.handleChange(e);
                    });
                } catch (error) {
                    console.error('Fetch error:', error);
                    // Optionally handle error state here
                }
            } else {
                this.handleChange(e);
            }
        },

        save_document: async function(e) {
            this.show_spinner = true;

            if (this.document_action_url) {
                var formData = new FormData();
                formData.append('action', 'save');
                if (this.commsLogId) {
                    formData.append('comms_log_id', this.commsLogId);
                }
                if (this.temporary_document_collection_id) {
                    formData.append('temporary_document_collection_id', this.temporary_document_collection_id);
                }
                formData.append('input_name', this.name);
                formData.append('filename', e.target.files[0].name);
                formData.append('_file', this.uploadFile(e));
                formData.append('csrfmiddlewaretoken', this.csrf_token);
                try {
                    const response = await fetch(this.document_action_url, {
                        method: 'POST',
                        body: formData,
                        credentials: 'same-origin'
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }

                    const data = await response.json();

                    if (this.replace_button_by_text) {
                        const button_name = 'button-' + this.name + e.target.dataset.que;
                        const elem_to_remove = document.getElementById(button_name);
                        if (elem_to_remove) {
                            elem_to_remove.remove();
                        }
                    }

                    this.documents = data.filedata;
                    this.commsLogId = data.comms_instance_id;

                } catch (error) {
                    console.error('Fetch error:', error);
                }
                this.show_spinner = false;
            } else {
                console.log("no documentActionUrl");
            }

        },

        num_documents: function() {
            if (this.documents) {
                return this.documents.length;
            }
            return 0;
        },
    },
    mounted:function () {
        if (this.value) {
            //vm.files = (Array.isArray(vm.value))? vm.value : [vm.value];
            if (Array.isArray(this.value)) {
                this.value;
            } else {
                let file_names = this.value.replace(/ /g,'_').split(",")
                this.files = file_names.map(function( file_name ) { 
                      return {name: file_name}; 
                });
            }
        }
        this.$nextTick(async () => {
            if (this.documentActionUrl === 'temporary_document' && !this.temporary_document_collection_id) {
                // pass
            } else {
                await this.get_documents();
            }
        });
    },
}

</script>

<style lang="css">
    input {
        box-shadow:none;
    }
    .ffu-input-elem {
        display: none !important;
    }
    .ffu-input-text {
        color: #337ab7;
        cursor: pointer;
    }
    .ffu-input-text:hover {
        color: #23527c;
        text-decoration: underline;
    }
</style>
