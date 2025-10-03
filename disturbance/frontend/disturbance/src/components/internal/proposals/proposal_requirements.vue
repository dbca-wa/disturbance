<template id="proposal_requirements">
    <FormSection :formCollapse="false" label="Requirements" Index="requirements">
        <form class="form-horizontal" action="index.html" method="post">
            <div class="row">
                <div class="col-sm-12">
                    <button v-if="hasAssessorMode" @click.prevent="addRequirement()" style="margin-bottom:10px;" class="btn btn-primary pull-right">Add Requirement</button>
                </div>
            </div>
            <!-- <div class="col-sm-12">
                <button v-if="hasAssessorMode" @click.prevent="addRequirement()" style="margin-bottom:10px;" class="btn btn-primary pull-right">Add Requirement</button>
            </div> -->
            <datatable ref="requirements_datatable" :id="'requirements-datatable-'+_uid" :dtOptions="requirement_options" :dtHeaders="requirement_headers"/>
        </form>
    </FormSection>
        <RequirementDetail ref="requirement_detail" :proposal_id="proposal.id" :requirements="requirements"/>
</template>
<script>
import { v4 as uuidv4 } from 'uuid';
import {
    api_endpoints,
    helpers,
    constants
}
from '@/utils/hooks'
import datatable from '@vue-utils/datatable.vue'
import RequirementDetail from './proposal_add_requirement.vue'
import FormSection from "@/components/forms/section_toggle.vue";
export default {
    name: 'InternalProposalRequirements',
    props: {
        proposal: Object
    },
    data: function() {
        let vm = this;
        return {
            panelBody: "proposal-requirements-"+uuidv4(),
            requirements: [],
            requirement_headers:["Requirement","Due Date","Recurrence","Action","Order"],
            requirement_options:{
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/requirements'),
                    "dataSrc": ''
                },
                order: [],
                dom: "<'d-flex align-items-center'<'me-auto'l>fB>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'d-flex align-items-center'<'me-auto'i>p>",
                // buttons:[
                // 'excel', 'csv', ], //'copy'
                buttons:[
                    {
                        extend: 'excel',
                        className: 'btn btn-primary me-2 rounded',
                        exportOptions: {
                            columns: ':not(.noexport)',
                            orthogonal:'export'
                        }
                    },
                    {
                        extend: 'csv',
                        className: 'btn btn-primary me-2 rounded',
                        exportOptions: {
                            columns: ':not(.noexport)',
                            orthogonal:'export'
                        }
                    },
                ],
                columnDefs: [
                    { responsivePriority: 1, targets: 0 }, // First visible column has top priority (e.g. proposal_number
                    { responsivePriority: 2, targets: -1 }, // If the actions is the last entry in columns then this will make it 2nd top priority soo as long as the screen is a decent size it will always be shown
                ],
                columns: [
                    {
                        data: "requirement",
                        //orderable: false,
                        'render': function (value, type) {
                            var result= helpers.dtPopover(value);
                            //return result;
                            return type=='export' ? value : result;
                        },
                        defaultContent: '',

                        /*'createdCell': function (cell) {
                            //TODO why this is not working?
                            // the call to popover is done in the 'draw' event
                            $(cell).popover();
                        }*/

                    },
                    {
                        data: "due_date",
                        mRender:function (data) {
                            return data != '' && data != null ? moment(data).format('DD/MM/YYYY'): '';
                        },
                        orderable: false,
                        defaultContent: '',
                    },
                    {
                        data: "recurrence",
                        mRender:function (data,type,full) {
                            if (full.recurrence){
                                switch(full.recurrence_pattern){
                                    case 1:
                                        return `Once per ${full.recurrence_schedule} week(s)`;
                                    case 2:
                                        return `Once per ${full.recurrence_schedule} month(s)`;
                                    case 3:
                                        return `Once per ${full.recurrence_schedule} year(s)`;
                                    default:
                                        return '';
                                }
                            }
                            return '';
                        },
                        orderable: false,
                        defaultContent: '',
                    },
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            if (vm.proposal.assessor_mode.has_assessor_mode){
                                if(full.copied_from==null || full.apiary_renewal)
                                {
                                    links +=  `<a href='#' class="editRequirement" data-id="${full.id}">Edit</a><br/>`;
                                }
                                //links +=  `<a href='#' class="editRequirement" data-id="${full.id}">Edit</a><br/>`;
                                links +=  `<a href='#' class="deleteRequirement" data-id="${full.id}">Delete</a><br/>`;
                            }
                            return links;
                        },
                        orderable: false,
                        defaultContent: '',
                    },
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            // TODO check permission to change the order
                            if (vm.proposal.assessor_mode.has_assessor_mode){
                                links +=  `<a class="dtMoveUp" data-id="${full.id}" href='#'><i class="fa fa-angle-up fa-2x"></i></a><br/>`;
                                links +=  `<a class="dtMoveDown" data-id="${full.id}" href='#'><i class="fa fa-angle-down fa-2x"></i></a><br/>`;
                            }
                            return links;
                        },
                        orderable: false,
                        defaultContent: '',
                    }
                ],
                processing: true,
                rowCallback: function ( row, data) {
                    if (data.copied_for_renewal && data.require_due_date && !data.due_date) {
                        $('td', row).css('background-color', 'Red');
                        vm.setApplicationWorkflowState(false)
                        //vm.$emit('refreshRequirements',false);
                    }
                },
                drawCallback: function () {
                    if (!vm.$refs.requirements_datatable || !vm.$refs.requirements_datatable.table) return;
                    $(vm.$refs.requirements_datatable.table).find('tr:last .dtMoveDown').remove();
                    $(vm.$refs.requirements_datatable.table).children('tbody').find('tr:first .dtMoveUp').remove();

                    // Remove previous binding before adding it
                    $('.dtMoveUp').unbind('click');
                    $('.dtMoveDown').unbind('click');

                    // Bind clicks to functions
                    $('.dtMoveUp').click(vm.moveUp);
                    $('.dtMoveDown').click(vm.moveDown);
                    helpers.enablePopovers();
                },
                preDrawCallback: function () {
                    vm.setApplicationWorkflowState(true)
                    //vm.$emit('refreshRequirements',true);
                },
                initComplete: function () {
                    helpers.enablePopovers();
                }
            }
        }
    },
    watch:{
        hasAssessorMode(){
            // reload the table
            this.updatedRequirements();
        }
    },
    components:{
        datatable,
        RequirementDetail,
        FormSection
    },
    computed:{
        hasAssessorMode(){
            return this.proposal.assessor_mode.has_assessor_mode;
        }
    },
    methods:{
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
                customClass: {
                    confirmButton: 'btn btn-primary',
                    cancelButton: 'btn btn-secondary',
                },
            }).then((swalresult) => {
                if(swalresult.isConfirmed) {
                    // vm.$http.delete(helpers.add_endpoint_json(api_endpoints.proposal_requirements,_id))
                    // .then((response) => {
                    //     vm.$refs.requirements_datatable.vmDataTable.ajax.reload();
                    // }, (error) => {
                    //     console.log(error);
                    // });

                    fetch(helpers.add_endpoint_json(api_endpoints.proposal_requirements,_id+'/discard'))
                    .then(async (response) => {
                        if (!response.ok) { return response.json().then(err => { throw err }); }
                        vm.$refs.requirements_datatable.vmDataTable.ajax.reload(
                            helpers.enablePopovers,
                            false
                        );
                    }).catch((error) => {
                        console.log(error);
                    });
                }
            },(error) => {
                console.log(error); 
            });
        },
        fetchRequirements(){
            let vm = this;
            let url = api_endpoints.disturbance_standard_requirements
            if (this.proposal.proposal_apiary) {
                url = api_endpoints.apiary_standard_requirements;
            }
            fetch(url).then(
                async (response) => {
                    if (!response.ok) { return response.json().then(err => { throw err }); }
                    vm.requirements = await response.json();
                }).catch((error) => {
                    console.log(error);
                }
            )
        },
        editRequirement(_id){
            fetch(helpers.add_endpoint_json(api_endpoints.proposal_requirements,_id))
            .then(async (response) => {
                if (!response.ok) { return response.json().then(err => { throw err }); }
                const data = await response.json();
                this.$refs.requirement_detail.requirement = data;
                // this.$refs.requirement_detail.requirement.due_date =  data.due_date != null && data.due_date != undefined ? moment(data.due_date).format('DD/MM/YYYY'): '';
                this.$refs.requirement_detail.requirement.due_date =  data.due_date != null && data.due_date != undefined ? data.due_date: '';
                data.standard ? $(this.$refs.requirement_detail.$refs.standard_req).val(data.standard_requirement).trigger('change'): '';
                this.addRequirement();
            }).catch((error) => {
                console.log(error);
            })
        },
        updatedRequirements(){
            this.$refs.requirements_datatable.vmDataTable.ajax.reload(
                helpers.enablePopovers,
                false
            );
        },
        eventListeners(){
            let vm = this;
            vm.$refs.requirements_datatable.vmDataTable.on('click', '.deleteRequirement', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-id');
                vm.removeRequirement(id);
            });
            vm.$refs.requirements_datatable.vmDataTable.on('click', '.editRequirement', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-id');
                vm.editRequirement(id);
            });
        },
        sendDirection(req,direction){
            let movement = direction == 'down'? 'move_down': 'move_up';
            fetch(helpers.add_endpoint_json(api_endpoints.proposal_requirements,req+'/'+movement)).then(() => {
            },(error) => {
                console.log(error);
                
            })
        },
        moveUp(e) {
            // Move the row up
            let vm = this;
            e.preventDefault();
            var tr = $(e.target).parents('tr');
            vm.moveRow(tr, 'up');
            vm.sendDirection($(e.target).parent().data('id'),'up');
        },
        moveDown(e) {
            // Move the row down
            e.preventDefault();
            let vm = this;
            var tr = $(e.target).parents('tr');
            vm.moveRow(tr, 'down');
            vm.sendDirection($(e.target).parent().data('id'),'down');
        },
        moveRow(row, direction) {
            // Move up or down (depending...)
            var table = this.$refs.requirements_datatable.vmDataTable;
            var index = table.row(row).index();

            var order = -1;
            if (direction === 'down') {
              order = 1;
            }

            var data1 = table.row(index).data();
            data1.order += order;

            var data2 = table.row(index + order).data();
            data2.order += -order;

            table.row(index).data(data2);
            table.row(index + order).data(data1);

            table.page(0).draw(false);
        },
        setApplicationWorkflowState(bool){
            let vm=this;
            //vm.proposal.requirements_completed=bool;
            //console.log('child', bool);
            vm.$emit('refreshRequirements',bool);
        }

    },
    mounted: function(){
        let vm = this;
        this.fetchRequirements();
        vm.$nextTick(() => {
            this.eventListeners();
        });
    }
}
</script>
<style scoped>
/* .dataTables_wrapper .dt-buttons{
    float: right;
} */
</style>
