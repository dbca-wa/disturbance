<template id="proposal_requirements">
    <div class="col-md-12">
        <div class="row">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Requirements for {{originatingApprovalLodgementNumber}}
                        <a class="panelClicker" :href="'#'+panelBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="panelBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body panel-collapse collapse in" :id="panelBody">
                    <form class="form-horizontal" action="index.html" method="post">
                        <!--div class="col-sm-12">
                            <button v-if="hasAssessorMode" @click.prevent="addRequirement()" style="margin-bottom:10px;" class="btn btn-primary pull-right">Add Requirement</button>
                        </div-->
                        <datatable ref="originating_requirements_datatable" :id="'originating-approval-requirements-datatable-'+_uid" :dtOptions="requirement_options" :dtHeaders="requirement_headers"/>
                    </form>
                </div>
            </div>
        </div>
    </div>
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
export default {
    name: 'OriginatingApprovalRequirements',
    props: {
        proposal: Object,
        originatingApprovalId: Number,
        originatingApprovalLodgementNumber: String,
    },
    data: function() {
        let vm = this;
        return {
            panelBody: "proposal-requirements-"+uuidv4(),
            //originatingApproval: {},
            requirements: [],
            requirement_headers:[
                "Requirement",
                "Due Date",
                "Recurrence",
                "Action",
                "Order"
            ],
            requirement_options:{
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/apiary_site_transfer_originating_approval_requirements'),
                    "dataSrc": ''
                },
                order: [],
                dom: 'lBfrtip',
                buttons:[
                'excel', 'csv', ], //'copy'
                columns: [
                    {
                        data: "requirement",
                        //title: originatingLicence,
                        //orderable: false,
                        'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-toggle="popover" ' +
                                    'data-trigger="click" ' +
                                    'data-placement="top auto"' +
                                    'data-html="true" ' +
                                    'data-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            return result;
                        },
                        'createdCell': helpers.dtPopoverCellFn,

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
                        orderable: false
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
                        orderable: false
                    },
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            if (vm.proposal.assessor_mode.has_assessor_mode){
                                /*
                                if(full.copied_from==null)
                                {
                                    links +=  `<a href='#' class="editRequirement" data-id="${full.id}">Edit</a><br/>`;
                                }
                                */
                                links +=  `<a href='#' class="editRequirement" data-id="${full.id}">Edit</a><br/>`;
                                links +=  `<a href='#' class="deleteRequirement" data-id="${full.id}">Delete</a><br/>`;
                            }
                            return links;
                        },
                        orderable: false
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
                        orderable: false
                    }
                ],
                processing: true,
                drawCallback: function () {
                    $(vm.$refs.originating_requirements_datatable.table).find('tr:last .dtMoveDown').remove();
                    $(vm.$refs.originating_requirements_datatable.table).children('tbody').find('tr:first .dtMoveUp').remove();

                    // Remove previous binding before adding it
                    $('.dtMoveUp').unbind('click');
                    $('.dtMoveDown').unbind('click');

                    // Bind clicks to functions
                    $('.dtMoveUp').click(vm.moveUp);
                    $('.dtMoveDown').click(vm.moveDown);
                    //$(this).show();
                }
            }
        }
    },
    watch:{
        hasAssessorMode(){
            // reload the table
            this.updatedRequirements();
        },
    },
    components:{
        datatable,
    },
    computed:{
        hasAssessorMode(){
            return this.proposal.assessor_mode.has_assessor_mode;
        },
        /*
        originatingApprovalId: function() {
            let returnVal = '';
            if (this.originatingApproval) {
                return this.originatingApproval.id;
            }
            return returnVal;

        },
        originatingApprovalApplicant: function() {
            let returnVal = '';
            if (this.originatingApproval) {
                return this.originatingApproval.applicant
            }
            return returnVal;
        },
        originatingApprovalLodgementNumber: function() {
            let returnVal = '';
            if (this.originatingApproval) {
                return this.originatingApproval.lodgement_number;
            }
            return returnVal;
        },
        */
    },
    methods:{
        addRequirement(){
            this.$refs.originating_requirement_detail.isModalOpen = true;
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
                    // vm.$http.delete(helpers.add_endpoint_json(api_endpoints.proposal_requirements,_id))
                    // .then((response) => {
                    //     vm.$refs.requirements_datatable.vmDataTable.ajax.reload();
                    // }, (error) => {
                    //     console.log(error);
                    // });

                    vm.$http.get(helpers.add_endpoint_json(api_endpoints.proposal_requirements,_id+'/discard'))
                    .then(() => {
                        vm.$refs.originating_requirements_datatable.vmDataTable.ajax.reload();
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
                console.log(error);
            });
        },
        fetchRequirements(){
            let vm = this;
            
            vm.$http.get(api_endpoints.proposal_standard_requirements).then((response) => {
                vm.requirements = response.body
            },(error) => {
                console.log(error);
            })
        },
        editRequirement(_id){
            let vm = this;
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.proposal_requirements,_id)).then((response) => {
                this.$refs.originating_requirement_detail.requirement = response.body;
                this.$refs.originating_requirement_detail.requirement.due_date =  response.body.due_date != null && response.body.due_date != undefined ? moment(response.body.due_date).format('DD/MM/YYYY'): '';
                response.body.standard ? $(this.$refs.originating_requirement_detail.$refs.standard_req).val(response.body.standard_requirement).trigger('change'): '';
                this.addRequirement();
            },(error) => {
                console.log(error);
            })
        },
        updatedRequirements(){
            this.$refs.originating_requirements_datatable.vmDataTable.ajax.reload();
        },
        eventListeners(){
            let vm = this;
            vm.$refs.originating_requirements_datatable.vmDataTable.on('click', '.deleteRequirement', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-id');
                vm.removeRequirement(id);
            });
            vm.$refs.originating_requirements_datatable.vmDataTable.on('click', '.editRequirement', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-id');
                vm.editRequirement(id);
            });
        },
        sendDirection(req,direction){
            let movement = direction == 'down'? 'move_down': 'move_up';
            this.$http.get(helpers.add_endpoint_json(api_endpoints.proposal_requirements,req+'/'+movement)).then(() => {
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
            var table = this.$refs.originating_requirements_datatable.vmDataTable;
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
        }
    },
    created: function() {
        /*
        this.$http.get(helpers.add_endpoint_json(api_endpoints.approvals,this.proposal.proposal_apiary.originating_approval_id))
        .then((response) => {
            //vm.$refs.requirements_datatable.vmDataTable.ajax.reload();
            //Object.assign(this.originatingApproval, response.body);
            this.originatingApproval = helpers.copyObject(response.body);
        }, (error) => {
            console.log(error);
        });
        */
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
.dataTables_wrapper .dt-buttons{
    float: right;
}
</style>
