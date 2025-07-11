<template lang="html">
    <div>
        <div class="row col-sm-12">
            <template v-if="is_external">
                <!--button 
                    v-if="!creatingProposal" 
                    class="btn btn-primary pull-right" 
                    @click="openNewTemporaryUse"
                    :disabled="!user_can_temporary_use"
                >New Temporary Use</button-->
            </template>
        </div>

        <div class="row col-sm-12">
            <datatable
                ref="temporary_use_table"
                id="temporary-use-table"
                :dtOptions="dtOptions"
                :dtHeaders="dtHeaders"
            />
        </div>

    </div>
</template>

<script>
    import datatable from '@vue-utils/datatable.vue'
    
    export default {
        props:{
            approval_id: {
                type: Number,
                required: true,
            },
            is_external:{
              type: Boolean,
              default: false
            },
            is_internal:{
              type: Boolean,
              default: false
            },
            user_can_temporary_use: {
                type: Boolean,
                default: false
            },
        },
        data:function () {
            let vm = this;
            return{
                proposal_apiary: null,
                creatingProposal: false,
                temporary_uses: [],
                dtHeaders: [
                    'Number',
                    'From',
                    'To',
                    'Site(s)',
                    'Status',
                    'Temporary Occupier',
                    'Deed Poll',
                    'Action',
                ],
                dtOptions: {
                    serverSide: false,
                    searchDelay: 1000,
                    lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                    order: [
                        [1, 'desc'], [0, 'desc'],
                    ],
                    language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },
                    responsive: true,
                    processing: true,
                    columns: [
                        {
                            // Number
                            visible: true,
                            mRender: function (data, type, full) {
                                return full.lodgement_number;
                            }
                        },
                        {
                            // From date
                            mRender: function (data, type, full) {
                                return full.from_date;
                            }
                        },
                        {
                            // To date
                            mRender: function (data, type, full) {
                                return full.to_date;
                            }
                        },
                        {
                            // Site(s)
                            mRender: function (data, type, full) {
                                let ret_str = ''
                                for (let i=0; i<full.temporary_use_apiary_sites.length; i++){
                                    if (full.temporary_use_apiary_sites[i].selected){
                                        ret_str += 'apiary site ID: ' + full.temporary_use_apiary_sites[i].apiary_site.id + '<br />'
                                    }
                                }
                                return ret_str
                            }
                        },
                        {
                            // Status (customer status)
                            mRender: function (data, type, full) {
                                return full.customer_status;
                            }
                        },
                        {
                            // Occupier name
                            mRender: function (data, type, full) {
                                return full.temporary_occupier_name;
                            }
                        },
                        {
                            // Deed poll
                            mRender: function (data, type, full) {
                                return full.deed_poll_documents;
                            }
                        },
                        {
                            // Action
                            mRender: function (data, type, full) {
                                if (full.customer_status.toLowerCase() === 'draft' && vm.user_can_temporary_use){
                                    if (vm.is_internal){
                                        return '<a href="/internal/proposal/' + full.proposal_id + '/">Edit</a>'
                                    } else if (vm.is_external){
                                        return '<a href="/external/proposal/' + full.proposal_id + '/">Edit</a>'
                                    }
                                } else {
                                    return ''
                                }
                            }
                        },
                    ],
                },
            }
        },
        components: {
            datatable,
        },
        computed:{

        },
        watch:{

        },
        methods:{
            loadTemporaryUses: async function(){

                await this.$http.get('/api/approvals/' + this.approval_id + '/temporary_use/').then(
                    (accept)=>{
                        this.temporary_uses = accept.body
                        this.constructTemporaryUseTable()
                    },
                    (reject)=>{
                    },
                )
            },
            constructTemporaryUseTable: function() {
                this.$refs.temporary_use_table.vmDataTable.clear().draw();

                for (let i=0; i<this.temporary_uses.length; i++){
                    this.addTemporaryUseToTable(this.temporary_uses[i]);
                }
            },
            addTemporaryUseToTable: function(temporary_use) {
                this.$refs.temporary_use_table.vmDataTable.row.add(temporary_use).draw();
            },
            openNewTemporaryUse: function() {
                let vm = this

                swal({
                    title: "Create Temporary Use Application",
                    text: "Are you sure you want to create temporary use application?",
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
                    'application_type_str': 'temporary_use',
                    'approval_id': this.approval_id,
                }
                return data
            },
            createProposal:function () {

                let vm = this;
                vm.creatingProposal = true;
                let data = vm._get_basic_data();

                vm.$http.post('/api/proposal.json', data).then(res => {
                    vm.proposal = res.body;

                    vm.$router.push({ name:"draft_proposal", params:{ proposal_id: vm.proposal.id }});
                    vm.creatingProposal = false;
                },
                err => {
                    console.log(err);
                });
            },
            addEventListeners: function() {

            },
        },
        created: function() {
            this.loadTemporaryUses()
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
