<template lang="html">
  <div id="schema-purpose">

    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Schema ProposalType Section
                        <a :href="'#'+pProposalTypeBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pProposalTypeBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pProposalTypeBody">

                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="">Proposal Type</label>
                                <select class="form-control" v-model="filterTableProposalType" >
                                    <option value="All">All</option>
                                    <option v-for="(p, pid) in schemaProposalTypes" :value="p.value" v-bind:key="`purpose_${pid}`">{{p.label}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <button class="btn btn-primary pull-right" @click.prevent="addTableEntry()" name="add_purpose">New Section</button>
                        </div>
                    </div>
                    <div class="row"><br/></div> 
                    <div class="row">
                        <div class="col-md-12">
                            <div class="form-group">

                                <datatable ref="schema_purpose_table"
                                    :id="schema_purpose_id" 
                                    :dtOptions="dtOptionsSchemaProposalType"
                                    :dtHeaders="dtHeadersSchemaProposalType" 
                                />

                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <modal transition="modal fade" @ok="ok()" title="Schema ProposalType Section" large>
        <div class="container-fluid">
            <div id="error" v-if="missing_fields.length > 0" style="margin: 10px; padding: 5px; color: red; border:1px solid red;">
                <b>Please answer the following mandatory question(s):</b>
                <ul>
                    <li v-for="error in missing_fields" :key="error.label">
                        {{ error.label }}
                    </li>
                </ul>
            </div>
            <div>
                <form class="form-horizontal" name="schema_purpose">
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Proposal Type</label>
                        </div>
                        <div class="col-md-6">
                            <select class="form-control" ref="select_purpose" name="select-purpose" v-model="sectionProposalType.proposal_type" >
                                <option value="All">Select...</option>
                                <option v-for="(p, pid) in schemaProposalTypes" :value="p.value" v-bind:key="`purpose_${pid}`">{{p.label}}</option>
                            </select>                            
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Section Label</label>
                        </div>
                        <div class="col-md-6">
                            <input type='text' class="form-control" v-model='sectionProposalType.section_label' >
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Section Index</label>
                        </div>
                        <div class="col-md-3">
                            <input type='text' class="form-control" v-model='sectionProposalType.index' >
                        </div>
                    </div>
                </form>
            </div>
        </div>
        <template #footer>
            <button type="button" class="btn btn-primary" @click="saveProposalType()">Save</button>
        </template>
    </modal>

  </div>
</template>

<script>
import { v4 as uuidv4 } from 'uuid';
import datatable from '@/utils/vue/datatable.vue'
import modal from '@vue-utils/bootstrap-modal.vue'
import {
  api_endpoints,
  helpers,
  constants
}
from '@/utils/hooks'
export default {
    name:'schema-purpose',
    components: {
        modal,
        datatable,
    },
    props:{
    },
    watch:{
        filterTableProposalType: function() {
            this.$refs.schema_purpose_table.vmDataTable.draw();
        },
    },
    data:function () {
        let vm = this;
        vm.schema_purpose_url = helpers.add_endpoint_join(api_endpoints.schema_proposal_type_paginated, 'schema_proposal_type_datatable_list/?format=datatables');
        return {
            schema_purpose_id: 'schema-purpose-datatable-'+uuidv4(),
            pProposalTypeBody: 'pProposalTypeBody' + uuidv4(),
            isModalOpen:false,
            missing_fields: [],
            filterTableProposalType: 'All',
            filterProposalTypeSection: 'All',
            // masterlist table
            dtHeadersSchemaProposalType: ["ID", "Proposal Type", "Section Label", "Index", "Action"],
            dtOptionsSchemaProposalType:{
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                searchDelay: 1000,
                responsive: true,
                serverSide: true,
                autowidth: false,
                processing: true,
                ajax: {
                    "url": vm.schema_purpose_url, 
                    "dataSrc": 'data',
                    "data": function (d) {
                        d.proposal_type_id = vm.filterTableProposalType;
                    }
                },
                columnDefs: [
                    { visible: false, targets: [ 0 ] } 
                ],
                columns: [
                    { 
                        data: "id",
                        width: "10%",
                        searchable: false,
                    },
                    { 
                        data: "proposal_type",
                        width: "20%",
                        searchable: false,
                        mRender:function (data) {
                            return data.name_with_version
                        }
                    },
                    { 
                        data: "section_label",
                        width: "50%",
                        searchable: false,
                    },
                    { 
                        data: "index",
                        width: "10%",
                        searchable: false,
                    },
                    { 
                        data: "id",
                        width: "10%",
                        searchable: false,
                        mRender:function (data,type,full) {
                            var column = `<a class="edit-row" data-rowid="__ROWID__">Edit</a><br/>`;
                            column += `<a class="delete-row" data-rowid="__ROWID__">Delete</a><br/>`;
                            return column.replace(/__ROWID__/g, full.id);
                        }
                    },
                ],
                rowId: function(_data) {
                    return _data.id
                },
                initComplete: function () {
                    var $searchInput = $('div.dataTables_filter input');
                    $searchInput.unbind('keyup search input');
                    $searchInput.bind('keypress', (vm.delay(function(e) {
                        if (e.which == 13) {
                            vm.$refs.schema_purpose_table.vmDataTable.search( this.value ).draw();
                        }
                    }, 0)));
                }
            },
            section_label: '',
            proposal_type: '',
            schemaProposalTypes: [],
            sectionProposalType: {
                id: '',
                section_name: '',
                section_label: '',
                index: '',
                proposal_type: '',
            }
        }

    },
    computed: {
    },
    methods: {
        delay(callback, ms) {
            var timer = 0;
            return function () {
                var context = this, args = arguments;
                clearTimeout(timer);
                timer = setTimeout(function () {
                    callback.apply(context, args);
                }, ms || 0);
            };
        },
        close: function() {
            const self = this;

            if (!self.errors) {

                self.isModalOpen = false;
            }
        },
        saveProposalType: async function() {
            const self = this;
            const data = self.sectionProposalType;

            if (data.id === '') {

                await self.$http.post(api_endpoints.schema_proposal_type, JSON.stringify(data),{
                    emulateJSON:true

                }).then(() => {

                    self.$refs.schema_purpose_table.vmDataTable.ajax.reload();
                    self.close();

                }, (error) => {
                    swal(
                        'Save Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });

            } else {

                await self.$http.post(helpers.add_endpoint_json(api_endpoints.schema_proposal_type,data.id+'/save_proposal_type'),JSON.stringify(data),{
                        emulateJSON:true,

                }).then(()=>{

                    self.$refs.schema_purpose_table.vmDataTable.ajax.reload();
                    self.close();

                },(error)=>{
                    swal(
                        'Save Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });

            }

        },
        cancel: function() {
            const self = this;
            self.isModalOpen = false;
        },
        addTableEntry: function() {
            this.sectionProposalType.id = '';
            this.sectionProposalType.section_label = '';
            this.sectionProposalType.index = '';
            this.sectionProposalType.proposal_type = '';
            this.isModalOpen = true;
        },
        addEventListeners: function(){
            const self = this;

            self.$refs.schema_purpose_table.vmDataTable.on('click','.edit-row', function(e) {
                e.preventDefault();
                self.$refs.schema_purpose_table.row_of_data = self.$refs.schema_purpose_table.vmDataTable.row('#'+$(this).attr('data-rowid'));

                self.sectionProposalType.id = self.$refs.schema_purpose_table.row_of_data.data().id;
                self.sectionProposalType.section_label = self.$refs.schema_purpose_table.row_of_data.data().section_label;
                self.sectionProposalType.index = self.$refs.schema_purpose_table.row_of_data.data().index;
                self.sectionProposalType.proposal_type = self.$refs.schema_purpose_table.row_of_data.data().proposal_type.id;

                self.isModalOpen = true;
            });

            self.$refs.schema_purpose_table.vmDataTable.on('click','.delete-row', function(e) {
                e.preventDefault();
                self.$refs.schema_purpose_table.row_of_data = self.$refs.schema_purpose_table.vmDataTable.row('#'+$(this).attr('data-rowid'));
                self.sectionProposalType.id = self.$refs.schema_purpose_table.row_of_data.data().id;

                swal({
                    title: "Delete ProposalType Section",
                    text: "Are you sure you want to delete?",
                    type: "question",
                    showCancelButton: true,
                    confirmButtonText: 'Accept'

                }).then(async (result) => {

                    if (result) {

                        await self.$http.delete(helpers.add_endpoint_json(api_endpoints.schema_proposal_type,(self.sectionProposalType.id+'/delete_proposal_type')))
    
                        .then(() => {

                            self.$refs.schema_purpose_table.vmDataTable.ajax.reload();

                        }, (error) => {
                            console.error(error);
                        });
    
                    }

                },(error) => {
                    console.error(error);
                });                
            });
        },
        initSelects: async function() {

            await this.$http.get(helpers.add_endpoint_json(api_endpoints.schema_proposal_type,'1/get_proposal_type_selects')).then(res=>{

                    this.schemaProposalTypes = res.body.all_proposal_type;

            },err=>{

                swal(
                    'Get Application Selects Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });
        },
    },
    mounted: function() {
        this.form = document.forms.schema_purpose;
        this.$nextTick(() => {
            this.addEventListeners();
            this.initSelects();
        });
    }
}
</script>
