<template lang="html">
    <div class="row">
        <div class="col-md-3">
        </div>
        <div :class="das_sections_classname">
            <FormSection :formCollapse="false" label="Map" Index="1">
                <div class="row col-sm-12">
                    <ComponentMap
                        ref="component_map"
                        :is_internal="is_internal"
                        :is_external="is_external"
                        :can_modify="true"
                        :display_at_time_of_submitted="true"
                        :shapefile_json="shapefile_json"
                        :key="componentMapKey"
                        
                    />
                </div>
                <div class="noPrint">  
                    <div button-sec>
                    <File 
                        ref="map_doc"
                        :name="map_doc_name" 
                        label="Upload Shapefile" :id="map_doc_id"  
                        :isRepeatable="true" 
                        :readonly="proposal.readonly"   
                        :proposal_id="proposal.id" 
                        :isRequired="true"
                        :key="fileKey">
                    </File>
                    </div>
                    <ul>
                            <li>
                                Upload a shapefile identifying the maximum area affected by the proposal, including all associated activities.
                            </li>
                            <li>
                                The shapefile can be made up of one multi-part polygon.
                            </li>
                            <li>
                                It is preferable that the Shapefile is in GDA94 latitude/longitude only.
                            </li>
                            <li>
                                Max file size is 10MB.
                            </li>
                            <li>
                                Valid shapefile must include 4 files, in .dbf .prj .shp and .shx format.
                            </li>
                            <li>
                                You must validate the shapefile and prefill the proposal before proceeding.
                            </li>
                            <li>
                                Further information <a :href="shapefile_info_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a>
                            </li>
                        </ul>
                </div>

                <alert v-if="showError" type="danger" style="color: red" class="noPrint"><strong>{{errorString}}</strong></alert>
                <div class="noPrint button-sec">
                    <div class="row">
                        <div class="col-sm-2">
                            <span v-if="validating">
                                <button disabled class="btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Validating</button>
                            </span>
                            <span v-else>
                                <input
                                    :disabled="valid_button_disabled"
                                    @click="validate_map_docs"
                                    type="button"
                                    value="Validate"
                                    class="btn btn-primary w-100"
                                />
                            </span>
                        </div>
                        <div class="col-sm-2 prefill-btn">
                            <input
                                :disabled="prefill_button_disabled"
                                @click="prefill_proposal"
                                type="button"
                                :value=prefill_button_text
                                class="btn btn-primary w-100"
                                :title=prefill_timestamp
                            />
                                <!--:style=prefill_button_color-->
                        </div>
                        <div v-if="proposal.in_prefill_queue" class="col-sm-4 prefill-btn">
                            <label class="control-label pull-left" :style=prefill_button_color>Prefill Processing ...</label>
                        </div>
                    </div>
                </div>
            </FormSection>  
        </div>
    </div>
</template>

<script>
    import { v4 as uuidv4 } from 'uuid';
    import File from '@/components/forms/map_file.vue'
    import FormSection from "@/components/forms/section_toggle.vue"
    import ComponentMap from '@/components/common/das/das_component_map.vue'
    import { api_endpoints, helpers }from '@/utils/hooks'
    import alert from '@vue-utils/alert.vue'
    export default {
        name: 'DASMapSection',
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
            // let vm = this;
            return{
                values:null,
                pBody: 'pBody'+uuidv4(),
                componentMapKey: 0,
                fileKey: 0,
                showError:false,
                errorString:'',
                isValidating:false,
                global_settings:[],
            }
        },
        components: {
            FormSection,
            ComponentMap,
            File,
            alert,
        },
        computed:{
            das_sections_classname: function() {
                // For external page, we need 'col-md-9' classname
                // but not for the internal.
                // This is a hacky way, though...
                if(this.is_internal){
                    return ''
                } else {
                    return 'col-md-9'
                }
            },
            map_doc_name: function(){
                if(this.proposal){
                    return "proposal_"+this.proposal.id+"_map_doc";
                }
                return "proposal_map_doc"
            },
            map_doc_id: function(){
                if(this.proposal){
                    return "proposal_"+this.proposal.id+"_map_doc_id";
                }
                return "proposal_map_doc"
            },
            valid_button_disabled: function(){
                 if(this.is_external && this.proposal && !this.proposal.readonly){
                    return false;
                }
                if(this.is_internal && this.proposal && this.proposal.draft_assessor_mode){
                    return false;
                }
                return true;
            },
            validating: function(){
                return this.isValidating;
            },
            shapefile_json: function(){
                return (this.proposal && this.proposal.shapefile_json) ? this.proposal.shapefile_json : {};
            },
            proposal_id: function(){
                return (this.proposal && this.proposal.id) ? this.proposal.id : null;
            },
            prefill_timestamp: function(){
                return (this.proposal && this.proposal.prefill_timestamp) ? 'This Proposal was last prefilled at ' + moment(this.proposal.prefill_timestamp).format('DD/MM/YYYY') + moment(this.proposal.prefill_timestamp).format(' h:mm:ss a') : '';
            },
            prefill_button_disabled: function(){
                if(this.is_external && this.proposal && !this.proposal.readonly && this.proposal.shapefile_json){
                    return false;
                }
                if(this.is_internal && this.proposal && this.proposal.draft_assessor_mode && this.proposal.shapefile_json){
                    return false;
                }
                return true;
            },
            prefill_button_text: function(){
                //if (this.proposal.in_prefill_queue) {
		//    return 'Prefill (processing ..)'
                //}
                return 'Prefill'
            },
            prefill_button_color: function(){
                if (this.proposal.in_prefill_queue) {
                    return "color: red; opacity: 0.8;"
                }
                return ""
            },

            shapefile_info_url: function(){
                let vm=this;
                if(vm.global_settings){
                    for(var i=0; i<vm.global_settings.length; i++){
                        if(vm.global_settings[i].key=='shapefile_info'){
                            // return vm.global_settings[i].value;
                            return '/help/' + vm.proposal.application_type + '/user/#' + vm.global_settings[i].key;
                        }
                    }
                }
                return '';
            },
        },
        methods:{
             incrementComponentMapKey: function() {
                this.componentMapKey++;
            },
            incrementFileKey: function() {
                this.fileKey++;
            },
            validate_map_docs: async function(){
                let vm = this;
                vm.showError=false;
                vm.errorString='';
                vm.isValidating=true;
                try {
                        const response = await fetch(helpers.add_endpoint_json(api_endpoints.proposals, vm.proposal.id + '/validate_map_files'), {
                            method: 'POST',
                            headers: {
                            'Content-Type': 'application/json',
                            },
                            
                        });

                        if (!response.ok) {
                            console.error('validate_map_docs response error', response);
                            const errorText = await response.text();
                            throw new Error(errorText);
                        }

                        const res = await response.json();
                        // vm.$emit('refreshFromResponse', res);
                        vm.$emit('refreshFromResponseProposal', res);
                        vm.proposal.shapefile_json = res.shapefile_json;
                        vm.$nextTick(() => {
                            vm.$refs.component_map.updateShape();
                        });
                    } catch (err) {
                        vm.showError = true;
                        //vm.errorString = helpers.apiVueResourceError(err);
                        vm.errorString = err.message || 'An error occurred while validating the map files';
                        vm.proposal.shapefile_json = null;
                        vm.incrementFileKey();
                        vm.incrementComponentMapKey();
                    }
                    
                // vm.$refs.component_map.updateShape();
                vm.isValidating=false;
            },
            prefill_proposal: async function(){
                let vm = this;
                vm.showError=false;
                vm.errorString='';
                var inputOptions = {};
                var html_text='<p>Are you sure you want to prefill this Proposal?</p>'
                if(vm.proposal.data && vm.proposal.data.length > 0) {
                    // inputOptions = {
                    //     'clear_sqs': 'Clear only Spatial data from the Proposal',
                    //     'clear_all': 'Clear all Proposal data',
                    // }
                    inputOptions = {
                        'clear_sqs': 'Refresh/ Renew GIS data only',
                        'clear_all': 'Clear ALL information from the Proposal',
                    }
                    html_text ='<p>Are you sure you want to prefill this Proposal?<br>Select the Applicable:</p>'
                }
                const swalConfig = {
                    title: "Prefill Proposal",
                    html: html_text,
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonText: 'Prefill Proposal',
                    confirmButtonColor: '#d9534f'
                };

                if (Object.keys(inputOptions).length > 0) {
                    swalConfig.input = 'radio';
                    swalConfig.inputOptions = { ...inputOptions };
                    swalConfig.inputValidator = (value) => {
                        if (!value) {
                            return 'Please select an option';
                        }
                        return null;
                    };
                }
                await swal.fire(
                    // title: "Prefill Proposal",
                    // //html: '<p>Are you sure you want to prefill this Proposal?<br>Select the Applicable:</p>',
                    // html: html_text,
                    // icon: "warning",
                    // showCancelButton: true,
                    // confirmButtonText: 'Prefill Proposal',
                    // confirmButtonColor:'#d9534f',
                    // input: 'radio',
                    // inputOptions: inputOptions,
                    swalConfig
                ).then(async (result) => {
                    if (result.isConfirmed) {
                        if (Object.keys(inputOptions).length > 0 && !result.value) {
                            swal.fire({
                                title: 'Please select an option',
                                text: null,
                                icon: 'warning'
                            })
                            return;
                        }  else if (Object.keys(inputOptions).length == 0) {
                            result = 'clear_all';
                        }
                        //vm.prefilling=true;
                        swal.fire({
                            title: "Loading...",
                            //text: "Loading...",
                            allowOutsideClick: false,
                            allowEscapeKey:false,
                            didOpen: () =>{
                                swal.showLoading()
                            }
                        })
                        var data={};
                        // data.option = result;
                        data.option = result && result.value ? result.value : result;
                        try {
                            const response = await fetch(
                                helpers.add_endpoint_json(api_endpoints.proposals_sqs, vm.proposal.id + '/prefill_proposal'),
                                {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify(data)
                                }
                            );

                            const res = await response.json();
                            swal.hideLoading();
                            swal.close();
                            if (!response.ok) {
                                const errorText = await res;
                                throw new Error(errorText);
                            }
                            let resp_proposal = null;
                            resp_proposal = res.proposal;
                            vm.$emit('refreshFromResponseProposal', resp_proposal);

                            let title = res.message.includes('updated') ? "Processing Proposal (UPDATED)" : "Processing Proposal";
                            let queue_position = res.position;

                            swal.fire({
                                title: title,
                                html: `<p><strong>Your proposal is in the process of being prefilled based on your uploaded shapefile.</strong><br>
                                    <span style="font-size:0.8em">You can close your browser and come back later. You will receive an email when it is complete. (${queue_position})</span>
                                    </p>`
                            });

                        } catch (err) {
                            console.log(err);
                            vm.showError = true;
                            //vm.errorString = helpers.apiVueResourceError(err);
                            vm.errorString = err.message || 'An error occurred while pre-filling the proposal';
                            swal.hideLoading();
                        }
                        
                    }
                },(error) => {
                   swal.hideLoading();
                   console.log(error);

                });
                
            },
            refreshFromResponse:function(response){
                let vm = this;
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = helpers.copyObject(response.body);
                // vm.$refs.component_map.shapefile_json=helpers.copyObject(vm.proposal.shapefile_json);
                //vm.$refs.component_map.updateShape();
            },
            fetchGlobalSettings: function(){
                let vm = this;
                fetch('/api/global_settings.json').then(
                    async (response) => {
                        if (!response.ok) {
                            console.error('fetchGlobalSettings response error', response);
                            return;
                        }
                        vm.global_settings = await response.json();

                    }).catch((error) => {
                        console.log(error);
                    });
            },
        },
        created: function() {
        },
        mounted: function() {
            let vm = this;
            vm.fetchGlobalSettings();
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
    @media print { 
        .panel-default {
            margin-top: 30px;
        }
    }
     .button-sec {
        position: relative;
        z-index: 1100;
    }
    .swal2-container {
        z-index: 15000 !important;
    }
</style>

