<template>
    <div class="row">
        <div class="col-md-3">
            <h3 v-if="proposal">Application: {{ proposal.lodgement_number }}</h3>
            <h4>Temporary Use</h4>
        </div>

        <div class="col-md-9 sections-proposal-temporary-use">
            <div>
                <SectionsProposalTemporaryUse
                    :is_internal="false"
                    :is_external="true"
                    :proposal="proposal"
                />
            </div>
        </div>

        <div style="margin-bottom: 50px">
            <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                <div class="navbar-inner">
                    <div class="container">
                        <p class="pull-right" style="margin-top:5px;">
                            <input type="button" @click.prevent="save_exit" class="btn btn-primary btn-margin" value="Save and Exit"/>
                            <input type="button" @click.prevent="save" class="btn btn-primary btn-margin" value="Save and Continue"/>
                            <input v-if="!isSubmitting" type="button" @click.prevent="submit" class="btn btn-primary btn-margin" value="Submit"/>
                            <button v-else disabled class="btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Submitting</button>
                        </p>
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
    import {v4 as uuidv4 } from 'uuid';
    import { helpers } from '@/utils/hooks'
    import SectionsProposalTemporaryUse from '@/components/common/apiary/sections_proposal_temporary_use.vue'

    export default {
        name: 'ExternalProposalTemporaryUse',
        props: {
            is_external: {
                type: Boolean,
                default: false
            },
            is_internal: {
                type: Boolean,
                default: false
            },
            proposalId: {
                type: Number,
                default: null,
            }
        },
        data() {
            let vm = this;
            return {
                //proposalId: null,
                applicationTypeName: '',
                isSubmitting: false,
                proposal: null,
            }
        },
        components:{
            SectionsProposalTemporaryUse,
        },
        computed: {
            csrf_token: function() {
              return helpers.getCookie('csrftoken')
            },
            temporaryProposal: function() {
                let retVal = false;
                if (this.applicationTypeName === 'Temporary Use') {
                    retVal = true;
                }
                return retVal;
            },

        },
        created: function() {
            if (this.$route.params.proposal_id) {
                this.loadProposal(this.$route.params.proposal_id)
            }
        },
        methods: {
            loadProposal: async function(proposal_id) {
                let vm = this
                Vue.http.get(`/api/proposal/${proposal_id}.json`).then(re => {
                    console.log('in loadProposal');
                    console.log(re.body)

                    vm.proposal = re.body

                    //let temp_use = re.body.apiary_temporary_use
                    vm.apiary_temporary_use = re.body.apiary_temporary_use
                    if (vm.apiary_temporary_use.from_date){
                        console.log(vm.apiary_temporary_use.from_date);
                        vm.apiary_temporary_use.from_date = moment(vm.apiary_temporary_use.from_date, 'YYYY-MM-DD');
                        console.log(vm.apiary_temporary_use.from_date);
                    }
                    if (vm.apiary_temporary_use.to_date){
                        console.log(vm.apiary_temporary_use.to_date);
                        vm.apiary_temporary_use.to_date = moment(vm.apiary_temporary_use.to_date, 'YYYY-MM-DD');
                        console.log(vm.apiary_temporary_use.to_date);
                    }

                    // Update PeriodAndSites component
                    vm.period_and_sites_key = uuidv4();
                    // Update TemporaryOccupier component
                    vm.temporary_occupier_key = uuidv4();
                });
            },
            save: function(){
                this.proposal_update();
            },
            save_exit: async function() {
                await this.proposal_update();
                this.exit();
            },
            submit: async function() {
                console.log('in submit()')
                await this.proposal_submit();
                //this.exit();
            },
            exit: function() {
                console.log('in exit()');
                this.$router.push({
                    name: 'external-proposals-dash'
                });
            },
            _get_basic_data: function(){
                let data = {
                    'category': '',
                    'profile': '', // TODO how to determine this?
                    'district': '',
                    'application': '3',  // TODO Retrieve the id of the 'Temporary Use' type or handle it at the server side
                                         //      like if there is apiary_temporary_use attribute, it must be a temporary use application, or so.
                    'sub_activity2': '',
                    'region': '',
                    'approval_level': '',
                    'behalf_of': '',  // TODO how to determine this?
                    'activity': '',
                    'sub_activity1': '',
                    'apiary_temporary_use': this.apiary_temporary_use,
                    'application_type_str': 'temporary_use',
                }
                return data
            },
            perform_redirect: function(url, postData) {
                /* http.post and ajax do not allow redirect from Django View (post method),
                   this function allows redirect by mimicking a form submit.

                   usage:  vm.post_and_redirect(vm.application_fee_url, {'csrfmiddlewaretoken' : vm.csrf_token});
                */
                console.log('in perform_redirect');
                var postFormStr = "<form method='POST' action='" + url + "'>";

                for (var key in postData) {
                    if (postData.hasOwnProperty(key)) {
                        postFormStr += "<input type='hidden' name='" + key + "' value='" + postData[key] + "'>";
                    }
                }
                postFormStr += "</form>";
                console.log(postFormStr);
                var formElement = $(postFormStr);
                $('body').append(formElement);
                $(formElement).submit();
            },
            proposal_submit: function() {
                console.log('in proposal_submit')

                let vm = this;
                let data = vm._get_basic_data();
                let proposal_id = this.$route.params.proposal_id

                this.$http.post('/api/proposal/' + proposal_id + '/submit/', data).then(
                    res=>{
                        console.log('success')
                        vm.perform_redirect('/external/proposal/' + proposal_id + '/submit_temp_use_success/', {
                            'csrfmiddlewaretoken': vm.csrf_token,
                            'proposal_id': proposal_id,
                        })
                    },
                    err=>{
                        helpers.processError(err)
                    }
                );
            },
            proposal_update: async function(){
                console.log('in proposal_update');

                let vm = this;
                let data = vm._get_basic_data();
                let proposal_id = this.$route.params.proposal_id

                await this.$http.post('/api/proposal/' + proposal_id + '/draft/', data).then(
                    res=>{
                        swal(
                            'Saved',
                            'Your proposal has been updated',
                            'success'
                        );
                    },
                    err=>{
                        helpers.processError(err)
                    }
                );
            },

        }
    }
</script>
<style>
.sections-proposal-temporary-use {
    margin: 0 0 4em 0;
}
</style>
