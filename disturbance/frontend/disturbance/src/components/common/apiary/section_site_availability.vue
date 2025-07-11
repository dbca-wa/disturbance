<template lang="html">
    <div class="row col-sm-12">
        <div class="row col-sm-12">
            <template v-if="is_external">
                <!--button 
                    class="btn btn-primary pull-right" 
                    @click="openNewSiteTransfer"
                    :disabled="!user_can_site_transfer"
                >
                    Site Transfer
                </button-->
            </template>
        </div>

        <ComponentSiteSelection
            :apiary_sites="apiary_sites"
            :is_internal="false"
            :is_external="true"
            :key="component_site_selection_key"
            :show_col_checkbox="false"
            :show_col_status="true"
            :show_action_available_unavailable="show_action_available_unavailable"
        />
    </div>
</template>

<script>
    import { v4 as uuidv4 } from 'uuid';
    import ComponentSiteSelection from '@/components/common/apiary/component_site_selection.vue'

    export default {
        name: 'ApiarySiteAvailability',
        props:{
            approval_id: {
                type: Number,
                required: true,
                default: 0,
            },
            is_external:{
              type: Boolean,
              default: false
            },
            is_internal:{
              type: Boolean,
              default: false
            },
            user_can_site_transfer: {
              type: Boolean,
              default: false
            }
        },
        data:function () {
            let vm=this;
            return{
                component_site_selection_key: '',
                proposal_apiary: null,
                modalBindId: null,
                apiary_sites: [],
                component_map_key: '',
            }
        },
        components: {
            ComponentSiteSelection,
        },
        computed:{
            show_action_available_unavailable: function() {
                let show = false
                if (this.is_external && this.user_can_site_transfer){
                    show = true
                }
                return show
            },
            addButtonEnabled: function() {
                let enabled = false;
                try {
                    if(this.proposal_apiary.apiary_sites.length > 0){
                        enabled = true
                    }
                } catch(err) { }
                return enabled;
            },
            /*
            apiary_sites_minimal: function() {
                let apiary_sites = [];
                for (let site of this.apiary_sites) {
                    if (site.checked) {
                        apiary_sites.push(site.id)
                    }
                }
                return apiary_sites;
            },
            */
        },
        watch:{

        },
        methods:{
            _get_basic_data: function(){
                let data = {
                    'category': '',
                    'profile': '', // TODO how to determine this?
                    'district': '',
                    //'application': '3',  // TODO Retrieve the id of the 'Temporary Use' type or handle it at the server side 
                                         //      like if there is apiary_temporary_use attribute, it must be a temporary use application, or so.
                    'sub_activity2': '',
                    'region': '',
                    'approval_level': '',
                    'behalf_of': '',  // TODO how to determine this?
                    'activity': '',
                    'sub_activity1': '',
                    'application_type_str': 'site_transfer',
                    'originating_approval_id': this.approval_id,
                    //'apiary_sites_minimal': this.apiary_sites_minimal,
                    //'approval_id': this.approval_id,
                }
                return data
            },

            createProposal:function () {
                console.log('createProposal');

                let vm = this;
                vm.creatingProposal = true;
                let data = vm._get_basic_data();

                vm.$http.post('/api/proposal.json', data).then(res => {
                    vm.proposal = res.body;

                    console.log('returned: ')
                    console.log(vm.proposal)

                    vm.$router.push({ name:"draft_proposal", params:{ proposal_id: vm.proposal.id }});
                    vm.creatingProposal = false;
                },
                err => {
                    console.log(err);
                });
            },

            openNewSiteTransfer: function() {
                let vm = this

                swal({
                    title: "Create Site Transfer Application",
                    text: "Are you sure you want to create a new site transfer application?",
                    type: "question",
                    showCancelButton: true,
                    confirmButtonText: 'Create'
                }).then(
                    () => {
                        vm.createProposal();
                    },
                    (error) => {

                    }
                );
            },

            loadApiarySites: async function(){
                console.log('loadApiarySites');

                await this.$http.get('/api/approvals/' + this.approval_id + '/apiary_site/').then(
                    (accept)=>{
                        console.log(accept.body)
                        this.apiary_sites = accept.body
                        this.component_site_selection_key = uuidv4()
                    },
                    (reject)=>{
                    },
                )
            },
            addEventListeners: function() {
            },
        },
        created: function() {
            console.log('in created')
            console.log('approval_id: ' + this.approval_id)
            this.loadApiarySites()
        },
        mounted: function() {
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners();
            });
        }
    }
</script>

<style lang="css" scoped>

</style>
