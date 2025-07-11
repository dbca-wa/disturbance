<template lang="html">
    <div>
        <div class="row col-sm-12" style="margin-bottom: 0.5em;">
            <template v-if="is_external">
                <button :disabled="!onSiteInformationEnabled" class="btn btn-primary pull-right" @click="openOnSiteInformationModalToAdd">Add</button>
            </template>
        </div>

        <div class="row col-sm-12">
            <datatable
                ref="on_site_information_table"
                id="on-site-information-table"
                :dtOptions="dtOptions"
                :dtHeaders="dtHeaders"
            />
        </div>

        <template v-if="approval_id">
        </template>
    </div>
</template>

<script>
    import datatable from '@vue-utils/datatable.vue'
    import { v4 as uuidv4 } from 'uuid';
    import { helpers, } from '@/utils/hooks'

    export default {
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
            user_can_interact: {
                type: Boolean,
                default: false
            }
        },
        data:function () {
            let vm=this;
            return{
                proposal_apiary: null,
                on_site_information_list: [],
                on_site_information_to_edit: {
                    id: null,
                    apiary_site: null,
                    comments: '',
                    period_from: null,
                    period_to: null,
                },
                modalBindId: null,
                // For Expandable row
                td_expand_class_name: 'expand-icon',
                td_collapse_class_name: 'collapse-icon',
                expandable_row_class_name: 'expandable_row_class_name',
                dtHeaders: [
                    'Id',
                    'From',
                    'To',
                    'Site',
                    'Comments',
                    'The proposed location <br />of the hives',
                    'Number of hives proposed<br />to be placed on the site',
                    'The names of the people <br />who are expected to be <br />entering the people_names',
                    'Flora targeted',
                    'Action',
                ],
                dtOptions: {
                    serverSide: false,
                    searchDelay: 1000,
                    autoWidth: false,
                    lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                    order: [
                        [1, 'desc'], [0, 'desc'],
                    ],
                    language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },
                    rowCallback: function (row, obj){
                        return // We disable the expander for now
                        console.log('in rowCallback')
                        let row_jq = $(row)
                        row_jq.children().first().addClass(vm.td_expand_class_name)
                    },
                    responsive: true,
                    processing: true,
                    columnDefs: [
                        { responsivePriority: 1, targets: 0}, // Id
                        { responsivePriority: 2, targets: 9}, // Action
                        { responsivePriority: 3, targets: 1},
                        { responsivePriority: 4, targets: 2},
                        { responsivePriority: 5, targets: 3},
                    ],
                    columns: [
                        {
                            // 0
                            mRender: function (data, type, full) {
                                if (full.id) {
                                    return full.id;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            // 1
                            mRender: function (data, type, full) {
                                if (full.period_from) {
                                    return full.period_from;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            // 2
                            mRender: function (data, type, full) {
                                if (full.period_to) {
                                    return full.period_to;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            // 3
                            mRender: function (data, type, full) {
                                if (full.apiary_site_id) {
                                    return full.apiary_site_id;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            // 4
                            data: 'comments',
                            mRender: function (data, type, full) {
                                var result= helpers.dtPopover(data);
                                return type=='display' ? result : data;
                            },
                            createdCell: helpers.dtPopoverCellFn,
                        },
                        {
                            // 5
                            data: 'hives_loc',
                            render: function (data, type, full, meta) {
                                var result= helpers.dtPopover(data);
                                return type=='display' ? result : data;
                            },
                            createdCell: helpers.dtPopoverCellFn,
                        },
                        {
                            // 6
                            mRender: function (data, type, full) {
                                if (full.hives_num) {
                                    return full.hives_num;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            // 7
                            data: 'people_names',
                            mRender: function (data, type, full) {
                                var result= helpers.dtPopover(data);
                                return type=='display' ? result : data;
                            },
                            createdCell: helpers.dtPopoverCellFn,
                        },
                        {
                            // 8
                            data: 'flora',
                            mRender: function (data, type, full) {
                                var result= helpers.dtPopover(data);
                                return type=='display' ? result : data;
                            },
                            createdCell: helpers.dtPopoverCellFn,
                        },
                        {
                            // 9
                            visible: true,
                            mRender: function (data, type, full) {
                                if (vm.is_external && vm.onSiteInformationEnabled){
                                    if (full.action) {
                                        return full.action;
                                    } else {
                                        let ret = '<a><span class="delete_on_site_information" data-on-site-information-id="' + full.id + '"/>Delete</span></a>';
                                        ret += '<br />'
                                        ret += '<a><span class="edit_on_site_information" data-on-site-information-id="' + full.id + '"/>Edit</span></a>';
                                        return ret;
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
            OnSiteInformationModal,
            datatable,
        },
        computed:{
            column_id: () => {
            },
            column_from: () => {
            },
            column_to: () => {
            },
            column_site: () => {
            },
            column_comments: () => {
            },
            column_hives_loc: () => {
            },
            column_hives_num: () => {
            },
            column_people_names: () => {
            },
            column_flora: () => {
            },
            column_action: () => {
            },
            number_of_columns: function() {
                let num =  this.$refs.on_site_information_table.vmDataTable.columns(':visible').nodes().length;
                return num
            },
            onSiteInformationEnabled: function() {
                let enabled = false;
                try {
                    if(this.approval_id && this.user_can_interact){
                        enabled = true
                    }
                } catch(err) { }
                return enabled;
            }
        },
        watch:{

        },
        methods:{
            get_content: function(data){
                let hives_loc = '<tr><td><strong>The proposed location of the hives</strong></td><td>' + data.hives_loc + '</td></tr>'
                let hives_num = '<tr><td><strong>Number of hives proposed to be <br />placed on the site</strong></td><td>' + data.hives_num + '</td></tr>'
                let people_names = '<tr><td><strong>The names of the people who <br />are expected to be entering the <br />site for apiary purposes</strong></td><td>' + data.people_names + '</td></tr>'
                let flora = '<tr><td><strong>Flora targeted</strong></td><td>' + data.flora + '</td></tr>'

                let contents = '<table class="child_table">' + hives_loc + hives_num + people_names + flora + '</table>'
                return contents
            },
            onSiteInformationAdded: async function() {
                await this.loadOnSiteInformation(this.approval_id);
                this.constructOnSiteInformationTable();
            },
            openOnSiteInformationModalToAdd: async function(e){
                this.openOnSiteInformationModal({
                    id: null,
                    apiary_site: null,
                    comments: '',
                    period_from: null,
                    period_to: null,
                });
            },
            openOnSiteInformationModal: async function(obj_to_edit) {
                console.log('openOnSiteInformationModal')
                console.log('obj_to_edit: ')
                console.log(obj_to_edit)

                // Refresh the component key
                this.modalBindId = uuidv4()

                this.on_site_information_to_edit = obj_to_edit;

                try {
                    this.$nextTick(() => {
                    });
                } catch (err) {
                    helpers.processError(err)
                }
            },
            constructOnSiteInformationTable: function(){
                // Clear table
                this.$refs.on_site_information_table.vmDataTable.clear().draw();

                // Construct table
                if (this.on_site_information_list.length > 0){
                    for(let i=0; i<this.on_site_information_list.length; i++){
                        this.addOnSiteInformationToTable(this.on_site_information_list[i]);
                    }
                }
            },
            addOnSiteInformationToTable: function(on_site_information) {
                this.$refs.on_site_information_table.vmDataTable.row.add(on_site_information).draw();
            },
            addEventListeners: function() {
                let vm = this
                $("#on-site-information-table").on("click", ".delete_on_site_information", this.deleteOnSiteInformation);
                $("#on-site-information-table").on("click", ".edit_on_site_information", this.editOnSiteInformation);
                // this.$refs.on_site_information_table.vmDataTable.on( 'childRow.dt', function () {
                //     console.log('childRow.dt')
                // });
                

                // $('#example').on('childRow.dt', function(e, show, row) {
                //     console.log((show ? "Showing " : "Hiding ") + "row " + row.index());
                // });

                // Listener for thr row
                //let vm = this
                vm.$refs.on_site_information_table.vmDataTable.on('click', 'td', function(e) {
                //    return  // We disable the expander for now
                    let td_link = $(this)

                //    if (!(td_link.hasClass(vm.td_expand_class_name) || td_link.hasClass(vm.td_collapse_class_name))){
                //        // This row is not configured as expandable row (at the rowCallback)
                //        return
                //    }

                //    // Get <tr> element as jQuery object
                    let tr = td_link.closest('tr')

                //    // Get full data of this row
                    let $row = vm.$refs.on_site_information_table.vmDataTable.row(tr)
                    if($row.child.isShown()){
                        tr.siblings('.child').find('[data-toggle="popover"]')
                        .popover()
                        .on('click', function (e) {
                            e.preventDefault();
                            return true;
                        });
                    }
                })
                //    let full_data = $row.data()

                //    //------------
                ////    if ($row.child.isShown()){
                ////        $row.child.hide()
                ////    } else {
                ////        $row.child(vm.get_content(full_data)).show()
                ////    }
                //    //------------
                //    let first_td = tr.children().first()
                //    if(first_td.hasClass(vm.td_expand_class_name)){
                //        let $next_elem = tr.next()
                //        if ($next_elem.hasClass('details_row')){
                //            console.log('1')
                //        } else {
                //            console.log('2')
                //            // Expand
                //            let contents = vm.get_content(full_data)

                //            let details_elem = $('<tr class="details_row ' + vm.expandable_row_class_name +'"><td colspan="' + vm.number_of_columns + '">' + contents + '</td></tr>')
                //            details_elem.hide()
                //            details_elem.insertAfter(tr)
                //            details_elem.fadeIn(1000)

                //            // Change icon class name to vm.td_collapse_class_name
                //            first_td.removeClass(vm.td_expand_class_name).addClass(vm.td_collapse_class_name)
                //        }
                //    } else {
                //        let nextElem = tr.next()
                //        // Collapse
                //        if(nextElem.is('tr') & nextElem.hasClass(vm.expandable_row_class_name)){
                //            // Details row is already shown.  Remove it.
                //            nextElem.fadeOut(500, function(){
                //                nextElem.remove()
                //            })
                //        }
                //        // Change icon class name to vm.td_expand_class_name
                //        first_td.removeClass(vm.td_collapse_class_name).addClass(vm.td_expand_class_name)
                //    }
                //})
                //vm.$refs.on_site_information_table.vmDataTable.on('responsive-resize', function(e, datatable, columns) {
                //    // Responsive has changed the visibility of columns in the table in response to a resize or recalculation event.
                //})
                //vm.$refs.on_site_information_table.vmDataTable.on('click', '.more-button', function(e) {
                //    e.preventDefault()
                //    let td_link = $(this)
                //    let tr = td_link.closest('tr')
                //    let $row = vm.$refs.on_site_information_table.vmDataTable.row(tr)
                //    let full_data = $row.data()
                //    //let rowData = tr.data().toArray()[0];
                //    //let fullText = rowData[3];
                //    console.log(full_data)
                //    // showMore: function(node, rowId) {
                //        //let rowData = this.$refs.on_site_information_table.vmDataTable.rows( rowId ).data().toArray()[0];
                //        //let fullText = rowData[3];
                //        //console.log(fullText)
                //        //$( node.parentNode ).text( fullText );
                //    // },
                //})
            },
            editOnSiteInformation: async function(e) {
                console.log('in editOnSiteInformation')

                let vm = this;
                let on_site_information_id = e.target.getAttribute("data-on-site-information-id");
                
                console.log('on_site_information_id: ' + on_site_information_id)

                let obj_to_edit = {
                    id: null,
                    apiary_site: null,
                    comments: '',
                    period_from: null,
                    period_to: null,
                }

                for(let i=0; i<this.on_site_information_list.length; i++){
                    if(this.on_site_information_list[i].id == on_site_information_id){
                        obj_to_edit = this.on_site_information_list[i];
                        break;
                    }
                }

                this.openOnSiteInformationModal(obj_to_edit);

            },
            deleteOnSiteInformation: async function(e) {
                let vm = this;
                let on_site_information_id = e.target.getAttribute("data-on-site-information-id");

                swal({
                      title: "Delete on site information",
                      text: "Are you sure you want to delete this?",
                      type: "warning",
                      showCancelButton: true,
                      confirmButtonClass: "btn-danger",
                      confirmButtonText: "Yes, delete it",
                }).then(
                    (accept) => {
                        vm.$http.delete('/api/on_site_information/' + on_site_information_id + '/').then(
                            async function(accept){
                                await vm.loadOnSiteInformation(this.approval_id);
                                vm.constructOnSiteInformationTable();
                            },
                            reject=>{
                                swal(
                                    'Submit Error',
                                    helpers.apiVueResourceError(err),
                                    'error'
                                )
                            }
                        );
                    },
                    (reject)=>{

                    }
                )
            },
            loadOnSiteInformation: async function(){
                await this.$http.get('/api/approvals/' + this.approval_id + '/on_site_information/').then(
                    (accept)=>{
                        this.on_site_information_list = accept.body
                        this.constructOnSiteInformationTable()
                    },
                    (reject)=>{
                    },
                )
            }
        },
        created: function() {
            this.loadOnSiteInformation()
        },
        mounted: function() {
            let vm = this;
            this.$nextTick(() => {
                this.constructOnSiteInformationTable();
                vm.addEventListeners();
            });
        }
    }
</script>

<style>
.collapse-icon {
    cursor: pointer;
}
.collapse-icon::before {
    top: 5px;
    left: 4px;
    height: 14px;
    width: 14px;
    border-radius: 14px;
    line-height: 14px;
    border: 2px solid white;
    line-height: 14px;
    content: '-';
    color: white;
    background-color: #d33333;
    display: inline-block;
    box-shadow: 0px 0px 3px #444;
    box-sizing: content-box;
    text-align: center;
    text-indent: 0 !important;
    font-family: 'Courier New', Courier monospace;
    margin: 5px;
}
.expand-icon {
    cursor: pointer;
}
.expand-icon::before {
    top: 5px;
    left: 4px;
    height: 14px;
    width: 14px;
    border-radius: 14px;
    line-height: 14px;
    border: 2px solid white;
    line-height: 14px;
    content: '+';
    color: white;
    background-color: #337ab7;
    display: inline-block;
    box-shadow: 0px 0px 3px #444;
    box-sizing: content-box;
    text-align: center;
    text-indent: 0 !important;
    font-family: 'Courier New', Courier monospace;
    margin: 5px;
}
.child_table {
    border-collapse: collapse;
    width: 100%;
}
.child_table tr {
    border-bottom: 1px solid #ccc;
}
.child_table td {
    padding: 0.5em;
}
</style>
