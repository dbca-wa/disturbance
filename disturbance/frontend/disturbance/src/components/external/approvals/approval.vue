<template>
<div class="container" id="externalApproval">
    <div class="row">
        <h3>Approval {{ approval.lodgement_number }}</h3>

        <div class="col-sm-12">
            <div class="row">
                <FormSection :formCollapse="false" label="Holder" Index="holder">
                        <div class="row">
                            <div class="col-sm-12">
                                <form class="form-horizontal" name="approval_form">
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Organisation</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="name" placeholder="" v-model="org.name">
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">ABN</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="abn" placeholder="" v-model="org.abn">
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                </FormSection>
            </div>

            <div class="row">
                <FormSection :formCollapse="false" label="Address Details" Index="address_details">
                        <form class="form-horizontal" action="index.html" method="post">
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">Street</label>
                                <div class="col-sm-6">
                                    <input type="text" disabled class="form-control" name="street" placeholder="" v-model="org.address.line1">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                <div class="col-sm-6">
                                    <input type="text" disabled class="form-control" name="surburb" placeholder="" v-model="org.address.locality">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">State</label>
                                <div class="col-sm-3">
                                    <input type="text" disabled class="form-control" name="country" placeholder="" v-model="org.address.state">
                                </div>
                                <label for="" class="col-sm-1 control-label">Postcode</label>
                                <div class="col-sm-2">
                                    <input type="text" disabled class="form-control" name="postcode" placeholder="" v-model="org.address.postcode">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label" >Country</label>
                                <div class="col-sm-4">
                                    <input type="text" disabled class="form-control" name="country" v-model="org.address.country"/>
                                </div>
                            </div>
                         </form>
                </FormSection>
            </div>

            <div class="row">
                <FormSection :formCollapse="false" label="Approval Details" Index="approval_details">
                    <form class="form-horizontal" action="index.html" method="post">
                        <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Issue Date</label>
                            <div class="col-sm-6">
                                <label for="" class="control-label pull-left">{{formatDate(approval.issue_date)}}</label>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Start Date</label>
                            <div class="col-sm-6">
                                <label for="" class="control-label pull-left">{{formatDate(approval.start_date)}}</label>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Expiry Date</label>
                            <div class="col-sm-3">
                                <label for="" class="control-label pull-left">{{formatDate(approval.expiry_date)}}</label>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Document</label>
                            <div class="col-sm-4">
                                <p><a target="_blank" :href="approval.licence_document" class="control-label pull-left">Approval.pdf</a></p>
                            </div>
                        </div>
                     </form>
                </FormSection>

            </div>

        </div>
    </div>
</div>
</template>
<script>
import FormSection from "@/components/forms/section_toggle.vue";
import { api_endpoints, helpers } from '@/utils/hooks';
import { v4 as uuidv4 } from 'uuid';

export default {
    name: 'ApprovalComponent',
    props:{
        is_external: {
            type: Boolean,
            default: false
        },
        is_internal: {
            type: Boolean,
            default: false
        },
        approvalId: {
            type: Number,
            default: null,
        }
    },
    data() {
        // let vm = this;
        return {
            loading: [],
            approval: {
                applicant_id: null
            },
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            adBody: 'adBody'+ uuidv4(),
            pBody: 'pBody'+ uuidv4(),
            cBody: 'cBody'+ uuidv4(),
            oBody: 'oBody'+ uuidv4(),
            onBody: 'onBody'+ uuidv4(),
            org: {
                address: {}
            },

            // variables passed to the child component
            test_apiary_sites: [],
            on_site_information_list: [],
            // Filters

        }
    },
    watch: {
        // approval: {
        //     deep: true,
        //     handler(){
        //         console.log('approval in watch');

        //         // Construct the array, which is passed to the child component, SiteAvailability
        //         // Construct the array, which is passed to the child component, OnSiteInformation
        //         this.test_apiary_sites = []
        //         this.on_site_information_list = []

        //         for (let i=0; i<this.approval.apiary_sites.length; i++){
        //             console.log(this.approval.apiary_sites[i]);
        //             this.test_apiary_sites.push(this.approval.apiary_sites[i].apiary_site)
        //             for (let j=0; j<this.approval.apiary_sites[i].apiary_site.onsiteinformation_set.length; j++){
        //                 this.on_site_information_list.push(this.approval.apiary_sites[i].apiary_site.onsiteinformation_set[j])
        //             }
        //         }

        //         // Construct the array, which is passed to the child component, TemporaryUse

        //     }
        // }
    },
    created: function() {
        if (this.approvalId) {
            this.loadApproval(this.approvalId)
        }
    },
    components: {
        FormSection,
    },
    computed: {
        isLoading: function () {
            return this.loading.length > 0;
        },
        proposal_apiary_id: function() {
            try {
                return this.approval.current_proposal.proposal_apiary.id;
            } catch(err) {
                console.error(err);
                return 0;
            }
        },
    },
    methods: {
        formatDate: function(data){
            return moment(data).format('DD/MM/YYYY');
        },
        loadApproval: function(approval_id){
            let vm = this
            fetch(helpers.add_endpoint_json(api_endpoints.approvals,approval_id)).then(
                async (res) => {
                    if (!res.ok) {
                        return await res.json().then(err => { throw err });
                    }
                    let data = await res.json();
                    vm.approval = data;
                    vm.approval.applicant_id = data.applicant_id;
                    vm.fetchOrganisation(vm.approval.applicant_id)
                }).catch(error => {
                    console.log(error);
                });
        },
        commaToNewline(s){
            return s.replace(/[,;]/g, '\n');
        },
        fetchOrganisation(applicant_id){
            let vm=this;
            fetch(helpers.add_endpoint_json(api_endpoints.organisations,applicant_id)).then(
                async (response) => {
                    if (!response.ok) {
                        return await response.json().then(err => { throw err });
                    }
                    let data = await response.json();
                    vm.org = data;
                    vm.org.address = data.address;
                }).catch((error) => {
                    console.log(error);
                });
        },
    },
    mounted: function () {
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
</style>
