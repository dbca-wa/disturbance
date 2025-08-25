<template lang="html">
  <div id="schema-question">

    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Schema Section Question
                        <a :href="'#'+pQuestionBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pQuestionBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pQuestionBody">
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
                            <button class="btn btn-primary pull-right" @click.prevent="addTableEntry()" name="add_purpose">New Question</button>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="">Section</label>
                                <select class="form-control" v-model="filterTableSection" >
                                    <option value="All">All</option>
                                    <option v-for="(s, sid) in schemaSections" :value="s.value" v-bind:key="`section_${sid}`">{{s.label}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <!-- <div class="row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="">Group</label>
                                <select class="form-control" v-model="filterTableGroup" >
                                    <option value="All">All</option>
                                    <option v-for="(g, gid) in schemaGroups" :value="g.value" v-bind:key="`group_${gid}`">{{g.label}}</option>
                                </select>
                            </div>
                        </div>
                    </div> -->
                    <div class="row"><br/></div> 
                    <div class="row">
                        <div class="col-md-12">
                            <div class="form-group">

                                <datatable ref="schema_question_table"
                                    :id="schema_question_id" 
                                    :dtOptions="dtOptionsSchemaQuestion"
                                    :dtHeaders="dtHeadersSchemaQuestion" 
                                />

                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <modal transition="modal fade" @ok="ok()" title="Schema Section Question" large>
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
                <form class="form-horizontal" name="schema_question">

                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Licence Proposal Type</label>
                        </div>
                        <div class="col-md-6" v-if="isNewEntry">
                            <select class="form-control" ref="select_purpose" name="select-purpose" v-model="filterQuestionProposalType" >
                                <option value="All">All</option>
                                <option v-for="(p, pid) in schemaProposalTypes" :value="p.value" v-bind:key="`purpose_${pid}`">{{p.label}}</option>
                            </select>                               
                        </div>
                        <div class="col-md-6" v-else >
                            <select disabled class="form-control" ref="select_purpose" name="select-purpose" v-model="filterQuestionProposalType" >
                                <option v-for="(p, pid) in schemaProposalTypes" :value="p.value" v-bind:key="`purpose_${pid}`">{{p.label}}</option>
                            </select>                         
                        </div>
                    </div>
                    <div class="row">&nbsp;</div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Section</label>
                        </div>
                        <div class="col-md-6" v-if="isNewEntry">
                            <select class="form-control" ref="select_section" name="select-section" v-model="filterQuestionSection" >
                                <option value="All">All</option>
                                <option v-for="(s, sid) in schemaSections" :value="s.value" v-bind:key="`section_${sid}`">{{s.label}}</option>
                            </select>                          
                        </div>
                        <div class="col-md-6" v-else >
                            <select disabled class="form-control" ref="select_section" name="select-section" v-model="filterQuestionSection" >
                                <option v-for="(s, sid) in schemaSections" :value="s.value" v-bind:key="`section_${sid}`">{{s.label}}</option>
                            </select>                      
                        </div>
                    </div>
                    <div class="row">&nbsp;</div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Question</label>
                        </div>
                        <div class="col-md-9" v-if="isNewEntry">
                            <select class="form-control" ref="select_question" name="select-question" v-model="sectionQuestion.question" >
                                <option v-for="(m, mid) in masterlist" :value="m.id" v-bind:key="`question_${mid}`">{{m.question}}</option>
                            </select>                         
                        </div>
                        <div class="col-md-9" v-else >
                            <select disabled class="form-control" ref="select_question" name="select-question" v-model="sectionQuestion.question" >
                                <option v-for="(m, mid) in masterlist" :value="m.id" v-bind:key="`question_${mid}`">{{m.question}}</option>
                            </select>                          
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-12">&nbsp; </div>
                    </div>
                    <div class="row" v-if="showOptions">

                        <SchemaOption ref="schema_option" :addedOptions="addedOptions" :canAddMore="false" />

                    </div>
                    <!-- <div class="row">
                        <div class="col-md-6">
                        <div v-for="(c, cid) in ['isRepeatable', 'isRequired','isCopiedToPermit','canBeEditedByAssessor' ]" v-bind:key="`check_${cid}`" >
                            <input type="checkbox" :value="true" v-model="getCheckedTag(c).isChecked" >&nbsp;&nbsp;<label>{{c.label}}</label></input><label>{{ c }}</label>
                        </div>
                        </div>
                    </div> -->

                    <div class="row">
                        <div class="col-md-6">
                            <label><input type="checkbox" :value="true" v-model="getCheckedTag('isRepeatable').isChecked"/>&nbsp;&nbsp;&nbsp;is Repeatable</label>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <label><input type="checkbox" :value="true" v-model="getCheckedTag('isRequired').isChecked" />&nbsp;&nbsp;&nbsp;is Required</label>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <label><input type="checkbox" :value="true" v-model="getCheckedTag('isCopiedToPermit').isChecked" />&nbsp;&nbsp;&nbsp;is Copied To Permit</label>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <label><input type="checkbox" :value="true" v-model="getCheckedTag('canBeEditedByAssessor').isChecked" />&nbsp;&nbsp;&nbsp;can Be Edited By Assessor</label>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <label><input type="checkbox" :value="true" v-model="getCheckedTag('isTitleColumnForDashboard').isChecked" />&nbsp;&nbsp;&nbsp;is Title Column For Dashboard</label>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Parent Question</label>
                        </div>
                        <div class="col-md-9">
                            <select class="form-control" ref="select_parent" name="select-parent" v-if="filterQuestionParent(sectionQuestion.parent_question)" v-model="sectionQuestion.parent_question" >
                                <option value=""></option>
                                <option v-for="(qp, qpid) in parentList" :value="qp.value" v-bind:key="`qparent_${qpid}`" >{{qp.label}}</option>
                            </select>                            
                        </div>
                    </div>
                    <div class="row">&nbsp;</div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Parent Answer</label>
                        </div>
                        <div class="col-md-3">
                            <select class="form-control" ref="select_answer" name="select-answer" v-model="sectionQuestion.parent_answer" >
                                <option value=""></option>
                                <option v-for="(an,anid) in answerList" :value="an.value" v-bind:key="`an_${anid}`">{{an.label}}</option>
                            </select>                            
                        </div>
                    </div>
                    <div class="row">&nbsp;</div>
                   <!--  <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Group</label>
                        </div>
                        <div class="col-md-6" >
                            <select class="form-control" ref="select_groupp" name="select-groupp" v-if="filterQuestionGroup(sectionQuestion.section_group)" v-model="sectionQuestion.section_group">
                                <option value=""></option>
                                <option v-for="(g, gid) in schemaGroups" :value="g.value" v-bind:key="`g_${gid}`" >{{g.label}}</option>
                            </select>                            
                        </div>
                    </div> -->
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left" >Index</label>
                        </div>
                        <div class="col-md-3">
                            <input type="text" class="form-control" v-model="sectionQuestion.order"/>
                        </div>
                    </div>
                </form>
            </div>
        </div>
        <template #footer>
            <button type="button" class="btn btn-primary" @click="saveQuestion">Save</button>
        </template>
    </modal>

  </div>
</template>

<script>
import { v4 as uuidv4 } from 'uuid';
import datatable from '@/utils/vue/datatable.vue'
import modal from '@vue-utils/bootstrap-modal.vue'
import SchemaOption from './schema_add_option.vue'
import {
  api_endpoints,
  helpers,
  constants
}
from '@/utils/hooks';

// var select2 = require('select2');
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");

export default {
    name:'schema-question',
    components: {
        modal,
        datatable,
        SchemaOption,
    },
    props:{
    },
    data:function () {
        let vm = this;
        vm.schema_question_url = helpers.add_endpoint_join(api_endpoints.schema_question_paginated, 'schema_question_datatable_list/?format=datatables');

        return {
            schema_question_id: 'schema-question-datatable-'+uuidv4(),
            pOptionsBody: 'pOptionsBody' + uuidv4(),
            pQuestionBody: 'pQuestionBody' + uuidv4(),
            isModalOpen: false,
            isNewEntry: false,
            missing_fields: [],
            filterTableProposalType: 'All',
            filterParentQuestion: 'All',
            filterTableSection: 'All',
            filterQuestionSection: 'All',
            filterQuestionProposalType: 'All',
            filterTableGroup: 'All',
            dtHeadersSchemaQuestion: ["ID", "SectionID", "OptionID", "Proposal Type", "Section", "Question", "Index", "Action"],
            dtOptionsSchemaQuestion:{
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                serverSide: true,
                autowidth: false,
                processing: true,
                searchDelay: 1000,
                ajax: {
                    "url": vm.schema_question_url,
                    "dataSrc": 'data',
                    "data": function (d) {
                        d.proposal_type_id = vm.filterTableProposalType;
                        d.section_id = vm.filterTableSection;
                        d.group_id = vm.filterTableGroup;
                    }
                },
                columnDefs: [
                    { visible: false, targets: [ 0, 1, 2, ] } 
                ],
                columns: [
                    { 
                        data: "id",
                        searchable: false,
                    },
                    { 
                        data: "section",
                        searchable: false,
                    },
                    { 
                        data: "options",
                        searchable: false,
                    },
                    { 
                        data: "proposal_type",
                        searchable: false,
                        name:'section__proposal_type_id'
                    },
                    { 
                        data: "section",
                        searchable: false,
                        mRender:function (data) {
                            return data.section_label;
                        }
                    },
                    // { 
                    //     data: "section_group",
                    //     searchable: false,
                    //     mRender:function (data,type,full) {
                    //         let label = data ? data.group_label : ''
                    //         return label
                    //     }
                    // },
                    { 
                        data: "question",
                        width: "80%",
                        searchable: false,
                        mRender:function (data) {
                            var ellipsis = '...',
                                truncated = _.truncate(data, {
                                    length: 40,
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
                                    text: data
                                });
                            }

                            return result
                        },
                        'createdCell': helpers.dtPopoverCellFn,
                    },
                    { 
                        data: "order",
                        searchable: false,
                    },
                    { 
                        data: "id",
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
                            vm.$refs.schema_question_table.vmDataTable.search( this.value ).draw();
                        }
                    }, 0)));
                }
            },
            sectionQuestion: {
                id: '',
                section: '',
                question: '',
                section_group: '',
                order: '0',
                conditions: '',
                purpose_id: '',
                parent_question: null,
                parent_answer: null,
                tag: []
            },
            masterlist: null,
            checked: false,
            selectedType: '',
            showOptions: false,
            optionList: [],
            addedOptions: [],
            addedOption: {
                label: '',
                value: '',
                conditions: '',
            },
            defaultOptions: [],
            schemaProposalTypes: [],
            schemaSections: [],
            schemaGroups: [],
            parentList: [],
            answerList: [],
            checkedTag: [{
                tag: null,
                isChecked: false,
            }],
        }

    },
    watch:{
        filterTableProposalType: function() {
            this.$refs.schema_question_table.vmDataTable.draw();
        },
        filterTableSection: function(){
            this.$refs.schema_question_table.vmDataTable.draw();
        },
        filterTableGroup: function(){
            this.$refs.schema_question_table.vmDataTable.draw();
        },
        filterQuestionProposalType: function(){
            if (this.filterQuestionProposalType==='All') {
                return true
            }
            const proposal_type_id = this.filterQuestionProposalType;
            var url = api_endpoints.schema_question.split( ".json" )
            fetch(url[ 0 ] + `/1/get_question_sections?proposal_type_id=${encodeURIComponent(proposal_type_id)}`,{
                // params: { proposal_type_id: this.filterQuestionProposalType },
            }).then(async (res)=>{
                let data = await res.json();
                this.schemaGroups = data.question_groups; 
                this.schemaSections = data.question_sections;
            },err=>{
                console.log(err);
            });
        },
        filterQuestionSection: function(){
            if (this.filterQuestionSection==='All') {
                return true
            }
            const section_id = this.filterQuestionSection;
            var url = api_endpoints.schema_question.split( ".json" )
            fetch(url[ 0 ] + `/1/get_question_parents?section_id=${encodeURIComponent(section_id)}`,{
                // params: { section_id: this.filterQuestionSection },
            }).then(async (res)=>{
                let data = await res.json();
                this.sectionQuestion.section = this.filterQuestionSection;
                this.parentList = data.question_parents;
            },err=>{
                console.log(err);
            });
        },
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
        filterQuestionGroup: function(g_id){
            if (!this.isModalOpen || g_id == '' || g_id == null) {
                return true
            }
            // fetch(helpers.add_endpoint_json(api_endpoints.schema_question,'1/get_question_order'),{
            //     params: { group_id: g_id },
            // }).then(async (res)=>{
                // let data = await res.json();
            //     this.sectionQuestion.order = data.question_order;
            // },err=>{

            // });
            return true;
        },
        filterQuestionParent: function(q_id){
            if (q_id == '' || q_id == null || !this.masterlist) {
                return true
            }
            let master = this.masterlist.find( m => m.id == q_id)
            if (master) {
                this.sectionQuestion.parent_question = q_id;
                this.answerList = master.options;
                let parent = this.parentList.find( q => q.value == q_id)
                if (parent) {
                    this.sectionQuestion.section_group = parent.group
                }
            } else {
                this.sectionQuestion.parent_question = '';
            }
            return true;
        },
        getCheckedTag: function(atag, set_checked=false){
            let checked = this.checkedTag.find(ch => {return ch.tag===atag})

            if (!checked) {
                checked = {
                    tag: atag,
                    isChecked: set_checked,
                }
                if (['isRepeatable','isRequired', 'isCopiedToPermit', 'canBeEditedByAssessor', 'isTitleColumnForDashboard'].includes(atag)){
                    this.checkedTag.push(checked)
                }
            }
            return checked;
        },
        close: function() {
            const self = this;

            if (!self.errors) {
                $(this.$refs.select_question).val(null).trigger('change');
                $('.has-error').removeClass('has-error');
                self.addedOptions = [];
                self.showOptions = false;
                self.isModalOpen = false;
            }
        },
        setShowOptions: function(selected_id) {
            let show = this.masterlist.filter( m => {
                return m.id == selected_id && ['checkbox','radiobuttons'].includes(m.answer_type)
            })[0]
            if (show && this.isNewEntry){
                let newOption = Object.assign(show)
                this.addedOptions.push(newOption);
                this.addedOptions = show.options;
            }

            this.showOptions = show ? true : false
        },
        saveQuestion: async function() {
            const self = this;
            const data = self.sectionQuestion
            data.options = self.addedOptions;
    
            if (self.checkedTag.length>0){
                data.tag = []
                self.checkedTag.filter( t => {
                    if (t.isChecked) {
                        data.tag.push(t.tag)
                    }
                    return
                })
            }

            if (data.id === '') {

                await fetch(api_endpoints.schema_question,{
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)

                }).then(async (response) => {
                    if (!response.ok) {
                        const errorText = await response.text();
                        throw new Error(errorText);
                    }
                    self.$refs.schema_question_table.vmDataTable.ajax.reload();
                    self.close();

                }).catch(error => {
                    
                    swal.fire(
                        'Save Error',
                        // helpers.apiVueResourceError(error),
                        error.message,
                        'error'
                    )
                });

            } else {

                await fetch(helpers.add_endpoint_json(api_endpoints.schema_question,data.id+'/save_question'),{
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)

                }).then(async (response)=>{
                    if (!response.ok) {
                        const errorText = await response.text();
                        throw new Error(errorText);
                    }
                    self.$refs.schema_question_table.vmDataTable.ajax.reload();
                    self.close();

                }).catch(error => {
                    
                    swal.fire(
                        'Save Error',
                        // helpers.apiVueResourceError(error),
                        error.message,
                        'error'
                    )
                });

            }
            this.isNewEntry = false;

        },
        addTableEntry: function() {
            this.isNewEntry = true
            this.sectionQuestion.id = '';
            this.sectionQuestion.section = '';
            this.sectionQuestion.question = '';
            this.sectionQuestion.section_group = '';
            this.sectionQuestion.order = 0;
            this.sectionQuestion.parent_question = null;
            this.sectionQuestion.parent_answer = null;
            this.sectionQuestion.tag = [];

            this.filterQuestionSection = 'All';
            this.filterQuestionProposalType = 'All';

            this.checkedTag = [];
            $(this.$refs.select_parent).val(this.sectionQuestion.parent_question).trigger('change');
            this.sectionQuestion.tag.filter( t => { this.getCheckedTag(t, true); return });

            this.isModalOpen = true;
        },
        initEventListeners: function(){
            const self = this;

            self.$refs.schema_question_table.vmDataTable.on('click','.edit-row', function(e) {
                e.preventDefault();
                self.isNewEntry = false;
                self.$refs.schema_question_table.row_of_data = self.$refs.schema_question_table.vmDataTable.row('#'+$(this).attr('data-rowid'));

                self.sectionQuestion.id = self.$refs.schema_question_table.row_of_data.data().id;
                self.sectionQuestion.section = self.$refs.schema_question_table.row_of_data.data().section.id;
                self.filterQuestionSection = self.$refs.schema_question_table.row_of_data.data().section.id;
                self.filterQuestionProposalType = self.$refs.schema_question_table.row_of_data.data().section.proposal_type;
                // self.sectionQuestion.question_id = self.$refs.schema_question_table.row_of_data.data().question_id;
                self.sectionQuestion.question = self.$refs.schema_question_table.row_of_data.data().question_id;
                self.sectionQuestion.order = self.$refs.schema_question_table.row_of_data.data().order;

                self.sectionQuestion.section_group = self.$refs.schema_question_table.row_of_data.data().section_group ? self.$refs.schema_question_table.row_of_data.data().section_group.id : '';
                // self.filterQuestionGroup = self.sectionQuestion.section_group
                // $(self.$refs.select_group).val(self.sectionQuestion.section_group).trigger('change');

                self.sectionQuestion.parent_question = self.$refs.schema_question_table.row_of_data.data().parent_question;
                self.sectionQuestion.parent_answer = self.$refs.schema_question_table.row_of_data.data().parent_answer;
                $(self.$refs.select_parent).val(self.sectionQuestion.parent_question).trigger('change');
                if (self.masterlist) {
                    let master = self.masterlist.find( m => m.id == self.sectionQuestion.parent_question)
                    if (master) {
                        self.answerList = master.options
                    }
                }

                self.checkedTag = [];
                self.sectionQuestion.tag = self.$refs.schema_question_table.row_of_data.data().tag;
                self.sectionQuestion.tag.filter( t => { self.getCheckedTag(t, true); return });

                self.addedOptions = Object.assign(self.$refs.schema_question_table.row_of_data.data().options);
                $(self.$refs.select_question).val(self.sectionQuestion.question).trigger('change');
                self.setShowOptions(self.sectionQuestion.question)

                self.isModalOpen = true;
            });

            self.$refs.schema_question_table.vmDataTable.on('click','.delete-row', function(e) {
                e.preventDefault();
                self.$refs.schema_question_table.row_of_data = self.$refs.schema_question_table.vmDataTable.row('#'+$(this).attr('data-rowid'));
                self.sectionQuestion.id = self.$refs.schema_question_table.row_of_data.data().id;

                swal.fire({
                    title: "Delete Section Question",
                    text: "Are you sure you want to delete?",
                    icon: "question",
                    showCancelButton: true,
                    confirmButtonText: 'Accept'

                }).then(async (result) => {
                    //console.log(result);

                    if (result.isConfirmed) {

                        await fetch(helpers.add_endpoint_json(api_endpoints.schema_question,(self.sectionQuestion.id+'/delete_question')),{
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        }).then(async (response) => {
                            if (!response.ok) {
                                const errorData = await response.json();
                                throw errorData;
                            }
                            self.$refs.schema_question_table.vmDataTable.ajax.reload();

                        }).catch((error) => {
                            console.log(error.message);
                        });
    
                    }

                },(error) => {
                    console.log(error);
                });                
            });

        },
        initQuestionSelector: function () {
                const self = this;
                $(self.$refs.select_question).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    minimumInputLength: 2,
                    placeholder:"Select Question..."
                }).
                on("select2:select",function (e) {
                    let selected = $(e.currentTarget);
                    self.sectionQuestion.question=selected.val()
                    self.setShowOptions(selected.val())
                }).
                on("select2:unselect",function (e) {
                    let selected = $(e.currentTarget);
                    self.sectionQuestion.question=selected.val()
                });
        },
        initParentSelector: function () {
                const self = this;
                $(self.$refs.select_parent).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    minimumInputLength: 2,
                    placeholder:"Select Parent Question..."
                }).
                on("select2:select",function (e) {
                    let selected = $(e.currentTarget);
                    self.sectionQuestion.parent_question=selected.val()
                }).
                on("select2:unselect",function (e) {
                    let selected = $(e.currentTarget);
                    self.sectionQuestion.parent_question=selected.val()
                });
        },
        // initAnswerSelector: function () {
        //         const self = this;
        //         $(self.$refs.select_answer).select2({
        //             "theme": "bootstrap",
        //             allowClear: true,
        //             minimumInputLength: 2,
        //             placeholder:"Select Parent Answer..."
        //         }).
        //         on("select2:selecting",function (e) {
        //             let selected = $(e.currentTarget);
        //         }).
        //         on("select2:select",function (e) {
        //             let selected = $(e.currentTarget);
        //         }).
        //         on("select2:unselect",function (e) {
        //             let selected = $(e.currentTarget);
        //         });
        // },
        initGroupSelector: function () {
                const self = this;
                $(self.$refs.select_group).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    minimumInputLength: 2,
                    placeholder:"Select Section Group..."
                }).
                on("select2:select",function (e) {
                    let selected = $(e.currentTarget);
                    self.sectionQuestion.section_group=selected.val()
                }).
                on("select2:unselect",function (e) {
                    let selected = $(e.currentTarget);
                    self.sectionQuestion.section_group=selected.val()
                });
        },
        initSelects: function() {

            fetch(helpers.add_endpoint_json(api_endpoints.schema_question,'1/get_question_selects'))
            .then(async (res)=>{
                    let data = await res.json();
                    this.masterlist = data.all_masterlist;
                    this.schemaProposalTypes = data.all_proposal_types;
                    this.schemaSections = data.all_section;
                    this.schemaGroups = data.all_group

            },err=>{
                swal.fire(
                    'Get Application Selects Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });
            this.initQuestionSelector();
            this.initParentSelector();
            // this.initAnswerSelector();
            this.initGroupSelector();
        },
    },
    mounted: function() {
        this.form = document.forms.schema_question;
        this.$nextTick(() => {
            this.initEventListeners();
            this.initSelects();
        });
    }
}
</script>
