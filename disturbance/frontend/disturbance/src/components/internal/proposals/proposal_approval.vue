<template id="proposal_requirements">
    <div>
        <template v-if="isFinalised">
            <div class="col-md-12 alert alert-success" v-if="proposal.processing_status == 'Approved'">
                <div v-if="proposal.proposal_apiary">
                    <p>The licence has been issued and has been emailed to {{proposal.applicant.name}}</p>
                    <p>Expiry date: {{approvalExpiryDate}}</p>
                    <p>Licence: <a target="_blank" :href="proposal.permit">licence.pdf</a></p>
                </div>
                <div v-else>
                    <p>The approval has been issued and has been emailed to {{proposal.applicant.name}}</p>
                    <p>Expiry date: {{approvalExpiryDate}}</p>
                    <p>Permit: <a target="_blank" :href="proposal.permit">approval.pdf</a></p>
                </div>
            </div>
            <div v-else class="col-md-12 alert alert-warning">
                <div v-if="proposal.proposal_apiary">
                    <p>The application was declined. The decision was emailed to {{proposal.applicant.name}}</p>
                </div>
                <div v-else>
                    <p>The proposal was declined. The decision was emailed to {{proposal.applicant.name}}</p>
                </div>
            </div>
        </template>

        <template v-if="proposal.proposal_apiary">
        </template>
        <template v-else>
            <div class="col-md-12">
                <div class="row">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">Level of Approval
                                <a class="panelClicker" :href="'#'+proposedLevel" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="proposedLevel">
                                    <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                </a>
                            </h3>
                        </div>
                        <div class="panel-body panel-collapse collapse in" :id="proposedLevel">

                            <div class="row">
                                <div class="col-sm-12">
                                        <template v-if="!isFinalised">
                                            <p><strong>Level of approval: {{proposal.approval_level}}</strong></p>

                                        <div v-if="isApprovalLevel">
                                            <p v-if="proposal.approval_level_document"><strong>Attach documents:</strong> <a :href="proposal.approval_level_document[1]" target="_blank">{{proposal.approval_level_document[0]}}</a>
                                            <span>
                                            <a @click="removeFile()" class="fa fa-trash-o" title="Remove file" style="cursor: pointer; color:red;"></a>
                                            </span></p>
                                            <div v-else>
                                                <p><strong>Attach documents:</strong></p>
                                                <div class="col-sm-12">
                                                <span class="btn btn-info btn-file pull-left">
                                                Attach File <input type="file" ref="uploadedFile" @change="readFile()"/>
                                                </span>
                                                <!--<span class="pull-left" style="margin-left:10px;margin-top:10px;">{{uploadedFileName()}}</span>-->

                                                </div>
                                                <div class="row"><p></p></div>
                                                <div class="row"><p></p></div>
                                                <div class="row"><p></p></div>

                                                <p>
                                                <strong>Comments (if no approval attached)</strong>
                                                </p>
                                                <p>
                                                <textarea name="approval_level_comments"  v-model="proposal.approval_level_comment" class="form-control" style="width:70%;"></textarea>
                                                </p>
                                            </div>

                                        </div>
                                        </template>

                                        <template v-if="isFinalised">
                                            <p><strong>Level of approval: {{proposal.approval_level}}</strong></p>

                                            <div v-if="isApprovalLevel">
                                                <p v-if="proposal.approval_level_document"><strong>Attach documents: </strong><a :href="proposal.approval_level_document[1]" target="_blank">{{proposal.approval_level_document[0]}}</a>
                                                </p>
                                                <p v-if="proposal.approval_level_comment"><strong>Comments: {{proposal.approval_level_comment}}</strong>
                                                </p>
                                            </div>
                                        </template>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </template>

        <div class="col-md-12">
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 v-if="!isFinalised" class="panel-title">Proposed Decision
                            <a class="panelClicker" :href="'#'+proposedDecision" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="proposedDecision">
                                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                            </a>
                        </h3>
                        <h3 v-else class="panel-title">Decision
                            <a class="panelClicker" :href="'#'+proposedDecision" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="proposedDecision">
                                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                            </a>
                        </h3>
                    </div>
                    <div class="panel-body panel-collapse collapse in" :id="proposedDecision">
                        <div class="row">
                            <div class="col-sm-12">
                                <template v-if="!proposal.proposed_decline_status">
                                    <template v-if="isFinalised">
                                        <p><strong>Decision: Issue</strong></p>
                                        <p><strong>Start date: {{proposal.proposed_issuance_approval.start_date}}</strong></p>
                                        <p><strong>Expiry date: {{proposal.proposed_issuance_approval.expiry_date}}</strong></p>
                                        <p><strong>CC emails: {{proposal.proposed_issuance_approval.cc_email}}</strong></p>
                                    </template>
                                    <template v-else>
                                        <p><strong>Proposed decision: Issue</strong></p>
                                        <p><strong>Proposed start date: {{proposal.proposed_issuance_approval.start_date}}</strong></p>
                                        <p><strong>Proposed expiry date: {{proposal.proposed_issuance_approval.expiry_date}}</strong></p>
                                        <p><strong>Proposed cc emails: {{proposal.proposed_issuance_approval.cc_email}}</strong></p>
                                    </template>
                                </template>
                                <template v-else>
                                    <strong v-if="!isFinalised">Proposed decision: Decline</strong>
                                    <strong v-else>Decision: Decline</strong>
                                </template>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { v4 as uuidv4 } from 'uuid';
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks'

export default {
    name: 'InternalProposalRequirements',
    props: {
        proposal: Object
    },
    data: function() {
        // let vm = this;
        return {
            proposedDecision: "proposal-decision-"+uuidv4(),
            proposedLevel: "proposal-level-"+uuidv4(),
            uploadedFile: null,
        }
    },
    watch:{
    },
    components:{
    },
    computed:{
        /*
        approvalStartDate: function() {
            let returnDate = null;
            if (this.proposal && this.proposal.approval) {
                returnDate = moment(this.proposal.approval.start_date, 'YYYY-MM-DD').format('DD/MM/YYYY');
            }
            return returnDate;
        },
        */
        approvalExpiryDate: function() {
            let returnDate = null;
            if (this.proposal && this.proposal.approval) {
                returnDate = moment(this.proposal.approval.expiry_date, 'YYYY-MM-DD').format('DD/MM/YYYY');
            }
            return returnDate;
        },
        hasAssessorMode(){
            return this.proposal.assessor_mode.has_assessor_mode;
        },
        isFinalised: function(){
            return this.proposal.processing_status == 'Approved' || this.proposal.processing_status == 'Declined';
        },
        isApprovalLevel:function(){
            return this.proposal.approval_level != null ? true : false;
        },
        apiary_sites: function() {
            let apiary_sites = null;
            if (this.proposal && this.proposal.proposal_apiary) {
                apiary_sites = this.proposal.proposal_apiary.apiary_sites;
            }
            return apiary_sites;
        },
        apiary_sites_prop: function() {
            let apiary_sites = [];
            if (this.proposal.application_type === 'Site Transfer') {
                for (let site of this.proposal.proposal_apiary.site_transfer_apiary_sites) {
                    if (site.selected) {
                        apiary_sites.push(site.apiary_site);
                    }
                }
            } else {
                apiary_sites = this.proposal.proposal_apiary.apiary_sites;
            }
            return apiary_sites;
        },
        showColCheckbox: function() {
            let checked = true;
            if (this.proposal.proposal_apiary.application_type !== 'Site Transfer') {
                checked = false;
            }
            return checked;
        },

    },
    methods:{
        readFile: function() {
            let vm = this;
            let _file = null;
            var input = $(vm.$refs.uploadedFile)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]);
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            vm.uploadedFile = _file;
            vm.save()
        },
        removeFile: function(){
            let vm = this;
            vm.uploadedFile = null;
            vm.save()
        },
        save: function(){
            let vm = this;
                let data = new FormData(vm.form);
                data.append('approval_level_document', vm.uploadedFile)
                if (vm.proposal.approval_level_document) {
                    data.append('approval_level_document_name', vm.proposal.approval_level_document[0])
                }
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/approval_level_document'),data,{
                emulateJSON:true
            }).then(res=>{
                vm.proposal = res.body;
                vm.$emit('refreshFromResponse',res);

                },err=>{
                swal.fire(
                    'Submit Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });


        },
        uploadedFileName: function() {
            return this.uploadedFile != null ? this.uploadedFile.name: '';
        },
        addRequirement(){
            this.$refs.requirement_detail.isModalOpen = true;
        },
        removeRequirement(_id){
            let vm = this;
            swal.fire({
                title: "Remove Requirement",
                text: "Are you sure you want to remove this requirement?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: 'Remove Requirement',
                confirmButtonColor:'#d9534f'
            }).then((swalresult) => {
                if(swalresult.isConfirmed){
                    vm.$http.delete(helpers.add_endpoint_json(api_endpoints.proposal_requirements,_id))
                    .then(() => {
                        vm.$refs.requirements_datatable.vmDataTable.ajax.reload();
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
                console.log(error);
            });
        },
    },
    mounted: function(){
        // let vm = this;
    }
}
</script>
<style scoped>
</style>
