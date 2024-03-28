<template lang="html">
  <div id="spatialQueryQuestion">

    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Spatial Query Questions
                        <a :href="'#'+pSpatialQueryQuestionBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pSpatialQueryQuestionBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pSpatialQueryQuestionBody">

                    <!--
                    <div id="info" v-if="missing_sqs_layers.length > 0" style="margin: 10px; padding: 5px; color: blue; border:1px solid blue;">
                        <b>The following layer(s) are not available or are inactive on SQS:</b>
                        <ul>
                            <li v-for="error in missing_sqs_layers">
                              <div class="col-md-10">
                                {{ error.label }}
                              </div>
                              <div>
                                <a @click="create_or_update_sqs_layer(error.layer)" ><button>Create/Update in SQS</button></a>
                              </div>
                              <br/>
                            </li>
                        </ul>
                    </div>
                    -->

                    <div class="row">
                        <div class="col-md-12">
                            <button class="btn btn-primary pull-right" @click.prevent="addTableEntry()" name="add-spatialquery">New Question</button>
                        </div>
                    </div>

                    <div class="text-center">
                        <span v-if="show_spinner"><i class='fa fa-2x fa-spinner fa-spin' style="font-size:72px;color:blue"></i></span>
                    </div>

                    <div class="row"><br/></div> 
                    <div class="row">
                        <div class="col-md-12">
                            <div class="form-group">
                                <!--{{profile}}-->

                                <datatable ref="spatial_query_question_table"
                                    :id="spatial_query_question_id" 
                                    :dtOptions="dtOptionsSpatialQueryQuestion"
                                    :dtHeaders="dtHeadersSpatialQueryQuestion" 
                                />

                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div v-show="showQuestionModal">
    <modal id="showQuestionModal" transition="modal fade" @ok="ok()" title="Spatial Query Question">
        <div class="container-fluid">
<!--
            <div id="error" v-if="missing_fields.length > 0" style="margin: 10px; padding: 5px; color: red; border:1px solid red;">
                <b>Please answer the following mandatory question(s):</b>
                <ul>
                    <li v-for="error in missing_fields">
                        {{ error.label }}
                    </li>
                </ul>
            </div>
-->
            <div>
                <form class="form-horizontal" name="spatial_query_question">

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div>
                        <div class="row">
                            <div class="col-md-1"></div>
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Question</label><label class="superscript">*</label>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-1"></div>
                            <div class="col-md-10">
                                <select class="form-control" ref="select_question" name="select-question" v-model="filterMasterlistQuestion" >
                                    <option v-for="(m, mid) in masterlist_questions" :value="m.question" v-bind:key="`question_${mid}`" :disabled="option_disabled(m)">{{m.question}}</option>
                                </select>                         
                                <i>{{spatialquery.answer_type}}</i>
                            </div>
                        </div>
                    </div>


<!--
                    {{sq_questions}}
-->

                    <div class="row"><div class="col-md-12" ></div></div>
                    <!-- Only show widget if there are options for the given masterlist question i.e. radiobuttons and checkboxes -->
                    <div v-if="spatialquery.question && masterlistQuestionOptions">
                        <div class="row">
                            <div class="col-md-1"></div>
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Answer</label><label class="superscript">*</label>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-1"></div>
                            <div class="col-md-10">
                                <select class="form-control" ref="select_answer" name="select-answer" v-model="filterMasterlistOption" >
                                    <option v-for="(o, oid) in masterlistQuestionOptions" :value="o.label" v-bind:key="`answer_${oid}`">{{o.label}}</option>
                                </select>                         
                            </div>
                        </div>
                    </div>

<!--
                    1. {{ masterlistQuestionOptions }}<br>
                    2. a. {{ filterMasterlistQuestion }} b. {{ spatialquery.question }}<br>
                    3. {{ spatialquery.answer_mlq }}<br>
                    4. {{ filterMasterlistOption }}<br>
-->

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div>
                        <div class="row">
                            <div class="col-md-1"></div>
                            <div class="col-md-9">
                                <label class="control-label pull-left" >Layer name</label><label class="superscript">*</label>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-1"></div>
                            <div class="col-md-10">
                                <select class="form-control" ref="select_layer" name="select-layer" v-model="spatialquery.layer">
                                    <option v-for="layer in spatialquery_selects.das_map_layers" :value="layer" >{{layer.layer_name}}</option>
                                </select>     
                            </div>
                            <span v-if="spatialquery.layer">
                                <a @click="check_sqs_layer_form" href="#"><i class="fa fa-lg fa-info-circle" style="color: blue;" title="Check/Update/Create Layer in SQS">&nbsp;</i></a>
                            </span>
                            <span v-else>
                                <i class="fa fa-lg fa-info-circle" style="color: grey;" title="Must select Layer name">&nbsp;</i>
                            </span>
                        </div>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <br>
                        <div class="col-md-1"></div>
             	        <div class="col-md-10" v-if="spatialquery.layer && is_admin">
                            <button type="button" class="btn btn-primary" @click="show_layer_attrs_and_values()" title="Show Layer Attrs and Values">View Layer Summary</button>
                            <button type="button" class="btn btn-primary" @click="output_vars()" title="Output SQQ form data to console log">To Console Log</button>
			</div>
                    </div>



                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div>
                        <div class="row">
                            <div class="col-md-1"></div>
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="control-label pull-left" >Question Group</label><label class="superscript">*</label>
                                </div>
                                <div class="col-md-3">
                                    <label class="control-label pull-left" >Intersection operator</label><label class="superscript">*</label>
                                </div>
                                <div class="col-md-3" v-if="spatialquery.question && is_text_widget()">
                                    <label class="control-label pull-left" >Visible to proponent</label><label class="superscript">*</label>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-1"></div>
                            <div class="col-md-3">
                                <!--{{spatialquery.group}}-->
                                <select class="form-control" ref="select_group" name="select-group" v-model="spatialquery.group">
                                    <option v-if="group.can_user_edit" v-for="group in spatialquery_selects.cddp_groups" :value="group" >{{group.name}}</option>
                                </select>     
                            </div>
                            <div class="col-md-3">
                                <select class="form-control" ref="select_how" name="select-how" v-model="spatialquery.how">
                                    <option v-for="operator in spatialquery_selects.how" :value="operator.value" >{{operator.label}}</option>
                                </select>     
                            </div>
                            <div class="col-md-3" v-if="spatialquery.question && is_text_widget(spatialquery.question && is_text_widget())">
                                <input type="radio" id="visible_to_proponent_yes" name="visible_to_proponent" value="true" v-model="spatialquery.visible_to_proponent">
                                <label for="visible_to_proponent_yes">Yes</label>&nbsp;&nbsp;&nbsp;
                                <input type="radio" id="visible_to_proponent_no" name="visible_to_proponent" value="false" v-model="spatialquery.visible_to_proponent">
                                <label for="visible_to_proponent_no">No</label>
                            </div>
                        </div>
                        <div class="row" v-if="showQuestionModal && has_no_editable_groups()">
                            <div class="col-md-1"></div>
                            <div  class="col-md-3">
                                <p style="color:red;">You are currently not a member of any Spatial Question Group. To create a new Spatial Query Question, you must first be added to at least one Spatial Question Group.</p>
                            </div>
                        </div>
                    </div>

                    <div class="text-center">
                        <span v-if="show_spinner"><i class='fa fa-2x fa-spinner fa-spin' style="font-size:72px;color:blue"></i></span>
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div>
                        <div class="row">
                            <div class="col-md-1"></div>
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Attribute name</label><label class="superscript">*</label>
                                <span v-if="spatialquery.layer">
                                    <a @click="show_layer_attrs" href="#"><i class="fa fa-lg fa-info-circle" style="color: blue;" title="View attributes available">&nbsp;</i></a>
                                    <!--<a @click="show_layer_polygon_overlay" href="#"><i class="fa fa-lg fa-globe" style="color: blue;" title="View Layer/Polygon overlay">&nbsp;</i></a>-->
                                </span>
                                <span v-else>
                                    <i class="fa fa-lg fa-info-circle" style="color: grey;" title="Must select Layer name">&nbsp;</i>
                                </span>
                            </div>
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Operator</label><label class="superscript">*</label>
                            </div>
                            <div class="col-md-3" v-if="showValue()">
                                <label class="control-label pull-left" >Value</label><label class="superscript">*</label>
                                <span v-if="spatialquery.column_name">
                                    <a @click="show_layer_attr_values" href="#"><i class="fa fa-lg fa-info-circle" style="color: blue;" title="View attribute values available">&nbsp;</i></a>
                                </span>
                                <span v-else>
                                    <i class="fa fa-lg fa-info-circle" style="color: grey;" title="Must select Layer name and Column name">&nbsp;</i>
                                </span>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-1"></div>
                            <div class="col-md-3">
                                <input type="text" class="form-control" name="column_name" v-model="spatialquery.column_name" style="width:100%;"></input>
                            </div>
                            <div class="col-md-3">
                                <select class="form-control" ref="select_operator" name="select-operator" v-model="filterCddpOperator">
                                    <option v-for="operator in spatialquery_selects.operators" :value="operator.value" >{{operator.label}}</option>
                                </select>     
                            </div>
                            <div class="col-md-3" v-if="showValue()">
                                <input type="text" class="form-control" name="value" v-model="spatialquery.value" style="width:100%;"></input>
                            </div>
                        </div>
                        <!--
                        Layer: {{spatialquery.layer}}<br>
                        Column_Name: {{spatialquery.column_name}}
                        Operator: {{spatialquery.operator}}
                        -->
                    </div>

                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div>
                        <div class="row">
                            <div class="col-md-1"></div>
                            <div class="col-md-3">
                                <label class="control-label pull-left" style="font-weight:normal !important;">Expiry</label>
                            </div>
                            <div class="col-md-3">
                                <label class="control-label pull-left" style="font-weight:normal !important;">Buffer (metres)</label>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-1"></div>
                            <div class="col-md-3">
                                <input type="date" class="form-control" name="expiry" v-model="spatialquery.expiry"></input>
                            </div>
                            <div class="col-md-3">
                                <input type="number" min="0" class="form-control" name="buffer" v-model="spatialquery.buffer"></input>
                            </div>
                        </div>
                    </div>

                    <div v-if="spatialquery.question && is_text_widget()">
			<hr />
			<div class="row"><div class="col-md-12" ></div></div>
			<div class="row">
                            <div class="col-md-1"></div>
			    <div class="col-md-3">
			        <label><i>Proponent Section</i></label>
			    </div>
			    <div class="col-md-5" style="text-align: right;">
                                <input type="checkbox" :value="false" v-model="spatialquery.show_add_info_section_prop" >&nbsp;&nbsp;&nbsp;<label>Show additional info section?</label></input>
			    </div>
			    <div class="col-md-2" style="text-align: right;">
				<button v-on:click="spatialquery.proponent_items.push({})" type="button">Add</button><br>
			    </div>
			</div>
			<div v-for="(item, index) in spatialquery.proponent_items" :key="`proponent_${index}`">
			    <div class="row"><div class="col-md-12" ></div></div>
			    <div>
				<div class="row">
				    <div class="col-md-1"></div>
				    <div class="col-md-5">
					<label :for="`data[${index}]prefix`" class="control-label pull-left" style="font-weight:normal !important;">Proponent Prefix</label>
				    </div>
				    <div class="col-md-5">
                                        <div v-if="index==0">
					    <label :for="`data[${index}]answer`" class="control-label pull-left" >Proponent Answer</label><label class="superscript">*</label>
				        </div>
                                        <div v-else>
					    <label :for="`data[${index}]answer`" class="control-label pull-left" style="font-weight:normal !important;">Proponent Answer</label>
				        </div>
				    </div>
				</div>
				<div class="row">
				    <div class="col-md-1"></div>
				    <div class="col-md-5">
					<input :name="`data[${index}]prefix`" class="form-control" placeholder="Prefix" v-model="item.prefix"></input>
				    </div>
				    <div class="col-md-5">
			                <input :name="`data[${index}]answer`" class="form-control" placeholder="<Attribute-Name>" v-model="item.answer"></input>
				    </div>
  		                    <a v-if="spatialquery.proponent_items.length>1" v-on:click="spatialquery.proponent_items.splice(index, 1)" href="#"><i class="fa fa-lg fa-trash">&nbsp;</i></a>
				</div>
			    </div>
			</div>
                        <!--{{spatialquery.proponent_items}}-->


			<hr />
			<div class="row"><div class="col-md-12" ></div></div>
			<div class="row">
                            <div class="col-md-1"></div>
			    <div class="col-md-3">
			        <label><i>Assessor Section</i></label>
			    </div>
			    <div class="col-md-7" style="text-align: right;">
				<button v-on:click="spatialquery.assessor_items.push({})" type="button">Add</button><br>
			    </div>
			</div>
			<div v-for="(item, index) in spatialquery.assessor_items" :key="`assessor_${index}`">
			    <div class="row"><div class="col-md-12" ></div></div>
			    <div>
				<div class="row">
				    <div class="col-md-1"></div>
				    <div class="col-md-5">
					<label :for="`data[${index}]prefix`" class="control-label pull-left" style="font-weight:normal !important;">Assessor Prefix</label>
				    </div>
				    <div class="col-md-5">
					<label :for="`data[${index}]info`" class="control-label pull-left" style="font-weight:normal !important;">Assessor Info</label>
				    </div>
				</div>
				<div class="row">
				    <div class="col-md-1"></div>
				    <div class="col-md-5">
					<input :name="`data[${index}]prefix`" class="form-control" placeholder="Prefix" v-model="item.prefix"></input>
				    </div>
				    <div class="col-md-5">
			                <input :name="`data[${index}]info`" class="form-control" placeholder="<Attribuet-Name>" v-model="item.info"></input>
				    </div>
  		                    <a v-if="spatialquery.assessor_items.length>1" v-on:click="spatialquery.assessor_items.splice(index, 1)" href="#"><i class="fa fa-lg fa-trash">&nbsp;</i></a>
				</div>
			    </div>
			</div>
                        <!--{{spatialquery.assessor_items}}-->

                    </div>
                </form>
            </div>
            <div id="error" v-if="missing_fields.length > 0" style="margin: 10px; padding: 5px; color: red; border:1px solid red;">
                <b>Please answer the following mandatory question(s):</b>
                <ul>
                    <li v-for="error in missing_fields">
                        {{ error.label }}
                    </li>
                </ul>
            </div>

        </div>
        <div slot="footer">
            <button type="button" class="btn btn-primary" @click="saveSpatialquery()">Save</button>
        </div>
    </modal>
    </div>

    <div v-show="showTestModal">
    <modal id="test-id"  @ok.prevent="ok()" title="Spatial Query Question - Test" large>
        <div class="container-fluid">
            <div id="error" v-if="missing_fields.length > 0" style="margin: 10px; padding: 5px; color: red; border:1px solid red;">
                <b>Please answer the following mandatory question(s):</b>
                <ul>
                    <li v-for="error in missing_fields">
                        {{ error.label }}
                    </li>
                </ul>
            </div>
            <div>
                <form class="form-horizontal" name="proposal_id">
                    <div class="row"><div class="col-md-12" >&nbsp;</div></div>
                    <div class="row">
                        <div class="col-md-3">
                            <label class="control-label pull-left">Proposal Lodgement No.</label>
                        </div>
                        <div class="col-md-2">
                            <input class="form-control" name="layer_name" placeholder="P000123" v-model="proposal.lodgement_number"></input>
                        </div>
                        <div v-if="is_admin">
			    <div class="col-md-2">
				<label class="control-label pull-right">Grouped MLQ's</label>
				<label class="control-label pull-right">All MLQ's</label>
			    </div>
			    <div class="col-md-1">
				<input class="med" type="checkbox" id="group_mlqs" name="group_mlqs" title="Request non-expired Grouped MasterList Questions (grouped by Radiobutton, Checkbox, Select, Multiselect)" v-model="proposal.group_mlqs"><br>
				<input class="med" type="checkbox" id="all_mlqs" name="all_mlqs" title="Request with all non-expired MasterList Questions" v-model="proposal.all_mlqs">
			    </div>
                        </div>
                        <div v-if="request_time" class="col-md-4">
                            <p><b>Request Time:   </b> {{request_time}}ms</p>
                            <p><b>No. Questions:  </b> {{num_questions}}</p>
                            <p><b>Layers Utilised:</b> {{num_layers_utilised}}</p>
                        </div>

                    </div>
                </form>
                <br>
                <textarea id="output" cols="100" rows="35" v-model="sqs_response"></textarea>
            </div>
        </div>
        <div slot="footer">
            <!--
            <button type="button" style="bckground-color: red;" v-if="requesting" disabled class="btn btn-default" @click="test_spatialquery()"><i class="fa fa-spinner fa-spin"></i> Processing</button>
            <button type="button" v-else class="btn btn-primary" @click="test_spatialquery()">Test</button>
            -->
            <!--
            <button type="button" class="btn btn-primary" @click="test_spatialquery()">Test</button>
            -->
            <!--
            <button type="button" style="background-color: red;" v-if="requesting" class="btn btn-default" @click="test_spatialquery()"><i class="fa fa-spinner fa-spin"></i> Processing</button>
            -->
            <button type="button" v-if="requesting" class="btn btn-default" @click="test_spatialquery()"><i class="fa fa-spinner fa-spin"></i> Processing</button>
            <button type="button" v-else class="btn btn-primary" @click="test_spatialquery()">Test</button>
        </div>
    </modal>
    </div>

    <div v-show="showLayerAttrsModal">
      <modal id="layer-attr-id"  @ok.prevent="ok()" title="Layer Attributes" large>
        <div class="container-fluid">
          <textarea id="output" cols="100" rows="35" v-model="sqs_attrs_response"></textarea>
        </div> 
        <div slot="footer">
            <button type="button" class="btn btn-primary" @click="showLayerAttrsModal=false">Close</button>
        </div>

      </modal>
    </div>

    <div v-show="showLayerAttrValuesModal">
      <modal id="layer-attr-id"  @ok.prevent="ok()" title="Layer Attributes" large>
        <div class="container-fluid">
          <textarea id="output" cols="100" rows="35" v-model="sqs_attr_vals_response"></textarea>
        </div> 
        <div slot="footer">
            <button type="button" class="btn btn-primary" @click="showLayerAttrValuesModal=false">Close</button>
        </div>

      </modal>
    </div>



  </div>
</template>

<script>
import Vue from 'vue'
import datatable from '@/utils/vue/datatable.vue'
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import SchemaOption from './schema_add_option.vue'
import moment from 'moment'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'

var select2 = require('select2');
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");

export default {
    name:'spatialQueryQuestionModal',
    components: {
        modal,
        alert,
        datatable,
        SchemaOption,
    },
    props:{
    },
    data:function () {
        let vm = this;
        vm.spatial_query_question_url = helpers.add_endpoint_join(api_endpoints.spatial_query_paginated, 'spatial_query_question_datatable_list/?format=datatables');
        console.log(vm.spatial_query_question_url)

//        vm.proposal = {
//            lodgement_number: '',
//            masterlist_question_id: '',
//            group_mlqs: true,
//            all_mlqs: false,
//        };
        //vm.proposal.group_mlqs=true;

        return {
            spatial_query_question_id: 'spatial-query-question-datatable-'+vm._uid,
            pSpatialQueryQuestionBody: 'pSpatialQueryQuestionBody' + vm._uid,
            pOptionBody: 'pOptionBody' + vm._uid,
            pHeaderBody: 'pHeaderBody' + vm._uid,
            pExpanderBody: 'pOptionBody' + vm._uid,
            show_spinner: false,
            filterOptions: '',
            isModalOpen:false,
            spatialquery_selects: [],
            masterlist_questions: [],
            filterMasterlistQuestion: '',
            filterMasterlistOption: '',
            masterlistQuestionOptions: '',
            filterCddpOperator: '',
            available_sqs_layers: [],
            missing_sqs_layers: [],
            missing_fields: [],
            expired_questions: [],
            current_layers: [],
            question_id: Number,
            showQuestionModal: false,
            showTestModal: false,
            showLayerAttrsModal: false,
            showLayerAttrValuesModal: false,
            showTestJsonResponse: false,
            sqs_response: false,
            sqs_attrs_response: false,
            sqs_attr_vals_response: false,
            requesting: false,
            request_time: null,
            num_questions: null,
            num_layers_utilised: null,
            profile: {},
            column_name: null,
            sq_questions: [],
            is_admin: false,

//	    proponent_items: [
//	      {
//		prefix: '',
//		answer: '',
//	      },
//	    ],
//	    assessor_items: [
//	      {
//		prefix: '',
//		info: '',
//	      },
//	    ],

            dtHeadersSpatialQueryQuestion: ["ID", "Question", "Answer Option", "Layer name", "Visible to proponent", "Buffer (m)", "Group", "Overlapping/Outside", "Column", "Operator", "Value", "Layer URL", "Expiry", "Prefix Answer", "Number of polygons (Proponent)", "Answer", "Prefix Info", "Number of polygons (Assessor)", "Assessor Info", "Regions", "Action"],
            dtOptionsSpatialQueryQuestion:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                serverSide: true,
                autowidth: false,
                processing: true,
                ajax: {
                    "url": vm.spatial_query_question_url, 
                    data: function (data) {
                      // needed because the datatables url GET length was too long - browser returned an error - jm
                      // eg. http://localhost:8000/api/spatial_query_paginated/spatial_query_question_datatable_list/?format=datatables&draw=1&length=1
                      for (var i = 10, len = data.columns.length; i < len; i++) {
                        delete data.columns[i].search;
                        delete data.columns[i].searchable;
                        delete data.columns[i].orderable;
                        delete data.columns[i].name;
                      }
                      //delete data.search.regex;
                    }
                },
                dom: 'lBfrtip',
                buttons:[
                    {
                        extend: 'excel',
                        exportOptions: {
                            columns: ':not(.noexport)',
                            orthogonal:'export'
                        }
                        /*
                        exportOptions: {
                            columns: ':visible'
                        }
                        */
                    },
                    {
                        extend: 'csv',
                        exportOptions: {
                            columns: ':not(.noexport)',
                            orthogonal:'export'
                        }
                        /*
                        exportOptions: {
                            columns: ':visible'
                        }
                        */
                    },
                ],
                columnDefs: [
                    //{ visible: false, targets: [ 3, 5, 6] } 
                    //{ visible: false, targets: [ 3, 6] } 
                    //{ orderable: false, targets: [ 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19] } 
                ],
                columns: [
                    { 
                        data: "id",
                        visible: false,
                        className: "noexport",
                        //searchable: true,
                    },
                    { 
                        data: "question",
                        width: "80%",
                        //searchable: true,
			'render': function (value) {
	  		    return helpers.dtPopover(value, 50);
			},
                        'createdCell': helpers.dtPopoverCellFn,
                        
//                        createdCell: function(td, cellData, rowData, row, col){
//                            if (vm.is_question_expired(rowData.expiry)) {
//                                vm.expired_questions.push(rowData.id) 
//                                $(td).css('color', 'blue');
//                                $(td).attr('title', 'This question has expired: ' + rowData.expiry);
//                            } else {
//                                // keep list for all non-expired questions, all layer names on the dashboard
//                                vm.current_layers.push(rowData.id) 
//                            }
//                            helpers.dtPopoverCellFn;
//                        }
                    },
                    { 
                        data: "answer_mlq",
                    },
                    { 
                        data: "layer.layer_name",
//            		  // Below Commented - caused poor performance of dashboard (disturbance/components/main/serializers.py DASMapLayerSqsSerializer)
//                        createdCell: function(td, cellData, rowData, row, col){
//                            if (!rowData.layer.available_on_sqs) {
//                                $(td).css('color', 'blue');
//                                $(td).attr('title', 'This layer is not present on SQS. First load from Geoserver');
//                            } else if (rowData.layer.available_on_sqs && !rowData.layer.active_on_sqs) {
//                                $(td).css('color', 'blue');
//                                $(td).attr('title', 'This layer is set as inactive on SQS. First set active on SQS');
//                            }
//                            helpers.dtPopoverCellFn;
//                        }

                    },
                    { 
                        data: "visible_to_proponent",
                    },
                    { 
                        data: "buffer",
                    },
                    { 
                        data: "group.name",
                    },
                    { 
                        data: "how",
                    },
                    { 
                        data: "column_name",
                    },
                    { 
                        data: "operator",
                    },
                    { 
                        data: "value",
                    },

                    { 
                        data: "layer.layer_url",
                        //data: "group.name",
                        visible: false,
                    },
                    { 
                        data: "expiry",
                        visible: false,
                    },
                    { 
                        data: "prefix_answer",
                        visible: false,
                    },
                    { 
                        data: "no_polygons_proponent",
                        visible: false,
                        className: "noexport",
                    },
                    { 
                        data: "answer",
                        visible: false,
                    },
                    { 
                        data: "prefix_info",
                        visible: false,
                    },
                    { 
                        data: "no_polygons_assessor",
                        visible: false,
                        className: "noexport",
                    },
                    { 
                        data: "assessor_info",
                        visible: false,
                    },
                    { 
                        data: "regions",
                        visible: false,
                        className: "noexport",
                    },

                    { 
                        data: "id",
                        className: "noexport",
                        width: "10%",
                        mRender:function (data,type,full) {
                            var column;
                            if (full.group.can_user_edit) {
                                column = `<a class="edit-row" data-rowid=\"__ROWID__\">Edit</a><br/>`;
                                column += `<a class="check-row" data-rowid=\"__ROWID__\" title="Check if the Question exists in Propasal Schema">Check_Question</a><br/>`;
                                column += `<a class="update-row" data-rowid=\"__ROWID__\" title="Check/Create/Update Layer exists in SQS">Check_Layer</a><br/>`;
                                column += `<a class="delete-row" data-rowid=\"__ROWID__\">Delete</a><br/>`;
                            } else {
                                column = `<a href="/" onclick="return false;" style="color: grey;" title="You are not a member of Spatial Question Group '${full.group.name}'">Edit</a><br/>`;
                                column += `<a href="/" onclick="return false;" style="color: grey;" title="You are not a member of Spatial Question Group '${full.group.name}'">Check_Question</a><br/>`;
                                column += `<a href="/" onclick="return false;" style="color: grey;" title="You are not a member of Spatial Question Group '${full.group.name}'">Check_Layer</a><br/>`;
                                column += `<a href="/" onclick="return false;" style="color: grey;" title="You are not a member of Spatial Question Group '${full.group.name}'">Delete</a><br/>`;
                            }
                            //column += `<a class="view-layer-overlay" data-rowid=\"__ROWID__\">View Overlay</a><br/>`;
                            column += `<a class="test-row" data-rowid=\"__ROWID__\">Test</a><br/>`;
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
                            vm.$refs.spatial_query_question_table.vmDataTable.search( this.value ).draw();
                        }
                    }, 0)));
                }
            },
            spatialquery: {
                id: '',
                name: '',
                question: '',
                question_id: '',
                options: null,
                headers: null,
                expanders: null,
                group: {
                    id: '',
                    name: ''
                },
                layer: {
                    id: '',
                    layer_name: ''
                },
//                masterlist_question: {
//                    question_id: '',
//                    answer_type: '',
//                    options: null
//                },
		show_add_info_section_prop: '',
		proponent_items: [
		  {
		    prefix: '',
		    answer: '',
		  },
		],
		assessor_items: [
		  {
		    prefix: '',
		    info: '',
		  },
		],
            },
            proposal: {
                lodgement_number: '',
                masterlist_question_id: '',
                group_mlqs: false,
                all_mlqs: false,
            },

            answerTypes: [],
            addedHeaders: [],
            addedHeader: {
                label: '',
                value: ''
            },
            addedExpanders: [],
            addedExpander: {
                label: '',
                value: '',
            },
            showOptions: false,
            showTables: false,
            addedOptions: [],
            addedOption: {
                id: '',
                label: '',
                value: '',
            },
            isNewEntry: false,
        }

    },
    watch:{
        filterMasterlistQuestion: function(){
            /* find question text in masterlist_questions and determine question options*/ 
            let question = this.masterlist_questions.find(o => o.question==this.filterMasterlistQuestion)
            if(question) {
                this.masterlistQuestionOptions = question.options
                this.spatialquery.question = question.question
                this.spatialquery.question_id = question.id
                this.spatialquery.answer_type = question.answer_type
            }
        },
        filterMasterlistOption: function(){
            if (this.masterlistQuestionOptions) {
                let option = this.masterlistQuestionOptions.find(o => o.label==this.filterMasterlistOption)
                //this.spatialquery.answer_mlq = this.filterMasterlistOption
                this.spatialquery.answer_mlq = option.label
                this.spatialquery.answer_mlq_id = option.value
            }
        },
        filterCddpOperator: function(){
            this.spatialquery.operator = this.filterCddpOperator
        },
    },
    computed: {
        csrf_token: function() {
            return helpers.getCookie('csrftoken')
        },
        group_mlqs: function() {
            return this.proposal.group_mlqs
        },
    },
    methods: {

        didSubmitForm(e) {
            /* https://codepen.io/sirthxalot-1471782131/pen/wvByQbz */
  	    e.preventDefault();
	    const data = new FormData(e.target);
	    console.log('Form data:', data);
        },
        is_text_widget: function () {
	    //return ['text', 'text_area', 'select', 'multi-select'].includes(this.spatialquery.answer_type)
	    return ['text', 'text_area'].includes(this.spatialquery.answer_type)
        },
//        option_disabled: function (mlq) {
//            let sq_questions_list = this.sq_questions.map((item) => item.question);
//            //return this.sq_questions.filter(x=> (!['radiobuttons', 'checkbox'].includes(x.masterlist_question.answer_type)) && x.question === question)
//	    //       && sq_questions_list.includes(question)
//            //let res = this.sq_questions.filter(x=> ['radiobuttons', 'checkbox'].includes(x.masterlist_question[0].answer_type) && x.question === question)
//            //let res = this.sq_questions.map(x=> ['radiobuttons', 'checkbox'].includes(x.masterlist_question.answer_type))
//            let res = this.sq_questions.filter(x=> (!['radiobuttons', 'checkbox'].includes(mlq.masterlist_question[0].answer_type)) && x.question == mlq.question)
//            //let res = this.sq_questions.filter(x=> x.question == mlq.question)
//            if (res.length > 0) {
//		console.log('sq_questions: ' + JSON.stringify(this.sq_questions))
//		console.log('question: ' + mlq.question)
//		console.log('res:  ' + JSON.stringify(res))
//		console.log('res2: ' + sq_questions_list.includes(mlq.question))
//		console.log('--------------------------------')
//            }
//            
//	    return sq_questions_list.includes(mlq.question) && res
//
//	    //return this.sq_questions.includes(question)
//        },
        option_disabled: function (mlq) {
	    return false;
        },
        exists_in: function (_dict, value) {
            return _dict.map(a=>a.layer_name).includes(value)
        },
        showValue: function () {
            if (this.spatialquery.operator=='GreaterThan' || this.spatialquery.operator=='LessThan' || this.spatialquery.operator=='Equals') {
                return true
            }
            return false
        },
        is_question_expired: function (expiry) {
            if (expiry) {
                let now = moment().format('YYYY-MM-DD')
                return moment(expiry).format('YYYY-MM-DD') < now;
            }
            return false;
        },
        layer_exists_in_sqs: function (layer_name) {
            return JSON.stringify(this.available_sqs_layers).indexOf('"name":"' + layer_name  + '"') > -1
        },
        layer_missing: function (layer_name) {
            return JSON.stringify(this.missing_sqs_layers).indexOf('"name":"' + layer_name  + '"') > -1
        },
//        has_missing_layers: function () {
//            this.missing_sqs_layers = [];
//            for (const layer of this.spatialquery_selects.das_map_layers) {
//                // exclude expired Spatial Question questions
//                if (!this.exists_in(this.spatialquery_selects.expired_cddp_questions, layer['layer_name'])) { 
//                    if (layer['available_in_sqs'] == false) {
//                        //msg = "Layer '" + sqs_layer.layer_name + "' does not exist in SQS. Please load layer in SQS"
//                        //console.log(msg);
//                        this.missing_sqs_layers.push({"label": "Layer '" + layer.layer_name + "' does not exist in SQS. Please load layer in SQS", "layer": layer}); 
//                    } 
//                    else if (layer['active_in_sqs'] == false) {
//                        //msg = "Layer '" + sqs_layer.layer_name + "' is set to 'inactive' in SQS. Please set layer to 'active' in SQS"
//                        //console.log(msg);
//                        this.missing_sqs_layers.push({"label": "Layer '" + layer.layer_name + "' is set to 'inactive' in SQS. Please set layer to 'active' in SQS", "layer": layer}); 
//                    }
//                }
//            }
//            //this.spatialquery_selects.expired_cddp_questions.find( t => t.layer_name === "cddp:dpaw_regions" ).expiry
//
//            if (this.missing_sqs_layers.length>0) {
//                return true;
//            } 
//            return false
//        },

        has_test_form_errors: function () {
            if (!this.proposal.lodgement_number) {
                this.missing_fields.push({'label':'Proposal lodgement number required (eg. P000123)'});
            }

            if (this.missing_fields.length>0) {
                return true;
            } 
            return false
        },
        has_no_editable_groups: function() {
            // Check if current  user is member of any groups
            var group_arr = this.spatialquery_selects.cddp_groups.map(obj => obj.can_user_edit ? obj.name : null).filter(obj => obj)
            return group_arr.length === 0;
        },
        pretty: function(value) {
            //return JSON.stringify(JSON.parse(value), null, 2);
            return JSON.stringify(JSON.parse(value), null, 2);
        },
        has_options: function(selected_id) {
            return this.selected_question(selected_id).option.length > 0;
        },
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
        setShowAdditional: function(selected_id) {
            const table = ['expander_table']
            const option = ['radiobuttons', 'checkbox', 'select', 'multi-select']
            const q_type = this.answerTypes.find( t => t.value === selected_id && (table.includes(t.value) || option.includes(t.value)))

            this.showOptions = q_type && option.includes(q_type.value) ? true : false
            this.showTables = q_type && table.includes(q_type.value) ? true : false

            if (this.showOptions && this.isNewEntry) {
                this.addedOption.id = ''
                this.addedOption.label = ''
                this.addedOption.value = ''
                let newOption = Object.assign(this.addedOption)
                this.addedOptions.push(newOption);          
            }

            if (this.showTables && this.isNewEntry) {
                let newHeader = Object.assign(this.addedHeader)
                this.addedHeaders.push(newHeader);
                let newExpander = Object.assign(this.addedExpander)
                this.addedExpanders.push(newExpander);           
            }
        },
        addOption: function() {
            this.addedOptions.push(Object.assign(this.addedOption))
        },
        addHeader: function() {
            this.addedHeaders.push(Object.assign(this.addedHeader))
        },
        addExpander: function() {
            this.addedExpanders.push(Object.assign(this.addedExpander))
        },
        close: function() {
            const self = this;

            if (!self.errors) {
                $(this.$refs.select_answer_type).val(null).trigger('change');
                $('.has-error').removeClass('has-error');
                let header_name = 'header-answer-type-0'
                $(`[name='${header_name}]`).removeClass('header-answer-type-0')
                self.addedOptions = [];
                self.addedHeaders = [];
                self.addedExpanders = [];

                self.showOptions = false;
                self.showTables = false;
                self.isModalOpen = false;
                self.showQuestionModel = false;
                self.showTestModel = false;
                self.showTestJsonResponse = false;

                self.request_time = null;
                self.num_questions = null;
                self.num_layers_utilised = null;
            }
        },

        check_layer_attrs_exist: async function(e) {
            const self = this;
            let url = '/get_sqs_attrs'
            url = helpers.add_endpoint_join(api_endpoints.spatial_query,'/'+self.spatialquery.layer.layer_name + url)

            var sqs_check_layer_response = null;
            console.log(url);
            await self.$http.get(url)
            .then((response) => {
                console.log('Response: ' + JSON.stringify(response));
                //sqs_check_layer_response = response.body;
                return response.body;
            },(error)=>{
                console.log('Error: ' + JSON.stringify(error))
                swal(
                    'Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });

        },

        saveSpatialquery: async function() {
            const self = this;
            const data = self.spatialquery;
            self.missing_fields = [];
             
            if (self.has_form_errors()) {
                self.isModalOpen = true;
                return;
            }

            if (data.id === '') {
                console.log(data);
                console.log(helpers.add_endpoint_json(api_endpoints.spatial_query,data.id));
                console.log(api_endpoints.spatial_query);
                console.log(api_endpoints.spatial_query + '.json');

                await self.$http.post(api_endpoints.spatial_query + '.json',JSON.stringify(data),{
                    emulateJSON:true
                }).then((response) => {
                    self.$refs.spatial_query_question_table.vmDataTable.ajax.reload();
                    self.close();
                }, (error) => {
                    console.log('Error: ' + JSON.stringify(error))
                    swal(
                        'Save Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });

            } else {

                if (data.operator=='IsNotNull') { data.value = '' } 

                await self.$http.post(helpers.add_endpoint_json(api_endpoints.spatial_query,data.id+'/save_spatialquery'),JSON.stringify(data),{
                        emulateJSON:true,
                }).then((response)=>{
                    self.$refs.spatial_query_question_table.vmDataTable.ajax.reload();
                    self.close();
                },(error)=>{
                    console.log('Error: ' + JSON.stringify(error))
                    swal(
                        'Save Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });

            }
            this.isNewEntry = false;
        },
        test_spatialquery: async function(e) {
            //e.preventDefault();
            const self = this;
            const data = self.proposal;
            data['csrfmiddlewaretoken'] = self.csrf_token
            data['current_ts'] = moment().format("YYYY-MM-DDTHH:mm:ss") //'2023-07-04T13:10:00'
            self.missing_fields = [];
             
            if (self.has_test_form_errors()) {
                self.isModalOpen = true;
                return;
            }

            let url = self.proposal.all_mlqs ? '/sqs_data' : '/sqs_data_single'
            const start_time = new Date()
            self.requesting = true;
            self.request_time = null;
            self.num_questions = null;
            self.num_layers_utilised = null;
            const uniq = (items) => [...new Set(items)];

            console.log(helpers.add_endpoint_json(api_endpoints.proposals,self.proposal.lodgement_number + url));
            await self.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,self.proposal.lodgement_number + url),JSON.stringify(data),{
                    emulateJSON:true,
            }).then((response)=>{
                console.log('Response: ' + JSON.stringify(response));
                if (self.is_admin) {
		    self.sqs_response = JSON.stringify(response.body, null, 4);
                } else {
                    // summary response
		    let sqs_response_basic = response.body.layer_data[0].sqs_data
		    sqs_response_basic.section = response.body.layer_data[0].name
		    sqs_response_basic.layer_name = response.body.layer_data[0].layer_name
		    sqs_response_basic.result = response.body.layer_data[0].result
                    delete sqs_response_basic.operator_response

                    if (!sqs_response_basic.answer) { delete sqs_response_basic.answer }
		    self.sqs_response = JSON.stringify(sqs_response_basic, null, 4);
                }
                self.isModalOpen = true;
                //self.close();
                self.requesting = false;
                self.num_questions = response.body['layer_data'].length;
                self.num_layers_utilised = uniq(response.body['layer_data'].map((item) => item.layer_name)).length // unique layers used
            },(error)=>{
                console.log('Error: ' + JSON.stringify(error))
                swal(
                    'Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });

            self.request_time = new Date() - start_time
            this.isNewEntry = false;
        },

        show_layer_polygon_overlay: async function(url) {
            const self = this;
            self.show_spinner = true;

            //console.log(url)
            await self.$http.get(url)
            .then((response) => {
                //swal(
                //    'Question Found in Proposal Schema!',
                //    response.body.message,
                //    'success'
                //)
                self.show_spinner = false;
            }, (error) => {
                swal(
                    'Check Question Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
                self.show_spinner = false;
            });
        },


        show_layer_attrs: function() {
            /* for given layer, show all attributes only */
            const self = this;
            let url = '/get_sqs_attrs'
            url = helpers.add_endpoint_join(api_endpoints.spatial_query,'/'+self.spatialquery.layer.layer_name + url)
            url += '?attrs_only=true'

            self.show_layer_details(url)
        },

        show_layer_attr_values: function() {
            /* for given layer attribute, show attribute values only */
            const self = this;
            let url = '/get_sqs_attrs'
            url = helpers.add_endpoint_join(api_endpoints.spatial_query,'/'+self.spatialquery.layer.layer_name + url)
            url += '?attr_name=' + self.spatialquery.column_name

            self.show_layer_details(url)
        },

        show_layer_attrs_and_values: function() {
            /* for given layer attribute, show attribute and values */
            const self = this;
            let url = '/get_sqs_attrs'
            url = helpers.add_endpoint_join(api_endpoints.spatial_query,'/'+self.spatialquery.layer.layer_name + url)

            self.show_layer_details(url)
        },

        output_vars: function() {
            /* for given layer attribute, show attribute and values */
            console.log(this.spatialquery);
        },


//        get_layer_json_url: async function() {
//            let url = '/internal/layer_json/'
//            url = helpers.add_endpoint_join(url, self.spatialquery.layer.layer_name + '/')
//        },

//        show_layer_json: async function() {
//            /* for given layer attribute, show attribute and values */
//            const self = this;
//            let url = '/internal/layer_json/'
//            url = helpers.add_endpoint_join(url, self.spatialquery.layer.layer_name + '/')
//
//            //self.show_layer_details(url)
//
//            self.requesting = true;
//            self.show_spinner = true;
//
//            console.log(url);
//            await self.$http.get(url)
//            .then((response) => {
//                console.log('Response: ' + JSON.stringify(response));
//                //self.sqs_attrs_response = JSON.stringify(response.body)
//                self.sqs_attrs_response = JSON.stringify(response.body)
//
//                self.requesting = false;
//                self.show_spinner = false;
//
//		var newWindow = window.open();
//                newWindow.document.write(self.sqs_attrs_response);
//
//                return self.sqs_attrs_response;
//            },(error)=>{
//                console.log('Error: ' + JSON.stringify(error))
//                self.requesting = false;
//                self.show_spinner = false;
//                swal(
//                    'Error',
//                    helpers.apiVueResourceError(error),
//                    'error'
//                )
//            });
//
//        },

        show_layer_details: async function(url) {
            const self = this;
            self.requesting = true;
            self.show_spinner = true;

            console.log(url);
            await self.$http.get(url)
            .then((response) => {
                console.log('Response: ' + JSON.stringify(response));
                self.sqs_attrs_response = JSON.stringify(response.body, null, 4);
                self.isModalOpen = true;
                self.showLayerAttrsModal = true;
                //self.showQuestionModal = true;
                self.showTestModal = false;

                self.requesting = false;
                self.show_spinner = false;
            },(error)=>{
                console.log('Error: ' + JSON.stringify(error))
                self.requesting = false;
                self.show_spinner = false;
                swal(
                    'Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },

        check_sqs_layer_form: async function() {
	    let self = this;
	    const data = {}
	    data['csrfmiddlewaretoken'] = self.csrf_token;
	    data['layer'] = self.spatialquery.layer;

	    swal({
		title: "Check Spatialquery Layer",
		type: "question",
		showCancelButton: true,
		confirmButtonText: 'OK',
		input: 'radio',
		inputOptions: {
		  'check_layer':  'Check Layer Exists on SQS',
		  'reload_layer': 'Create/Update Layer in SQS',
		}
	    }).then(async (result) => {
		console.log("Result: " + result);
		if (!result) {
		    swal(
			'Please select an option',
			null,
			'warning'
		    )
		    return;
		}

		if (result=='check_layer') {
		    let url = helpers.add_endpoint_json(api_endpoints.spatial_query, self.spatialquery.layer.layer_name+'/check_sqs_layer');
		    self.check_sqs_layer(url)

		}
		else if (result=='reload_layer') {
		    let url = helpers.add_endpoint_json(api_endpoints.spatial_query, self.spatialquery.layer.layer_name + '/create_or_update_sqs_layer');
		    self.create_or_update_sqs_layer(url, data)

		}
	    },(error) => {
		//
	    });                
	},


        check_sqs_layer: async function(url) {
            //await self.$http.get(helpers.add_endpoint_json(api_endpoints.spatial_query, self.spatialquery.layer.layer_name+'/check_sqs_layer'))
            const self = this;
            self.show_spinner = true;
            await self.$http.get(url)
            .then((response) => {
                //console.log(JSON.stringify(response))
                swal(
                    'Layer Exists in SQS!',
                    response.body.message,
                    'success'
                )
                self.show_spinner = false;
            }, (error) => {
                swal(
                    'Layer Check Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
                self.show_spinner = false;
            });
        },
        create_or_update_sqs_layer: async function(url, data) {
            const self = this;
            self.show_spinner = true;

            //await self.$http.post(helpers.add_endpoint_json(api_endpoints.spatial_query, self.spatialquery.layer.layer_name + '/create_or_update_sqs_layer'),JSON.stringify(data),{
            await self.$http.post(url ,JSON.stringify(data),{
                emulateJSON:true,
            }).then((response)=>{
                swal(
                    'Create/Update SQS Layer!',
                    response.body.message,
                    'success'
                )
                self.show_spinner = false;
            }, (error) => {
                swal(
                    'Create/Update Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
                self.show_spinner = false;
            });
        },

        check_cddp_question: async function(url) {
            const self = this;
            self.show_spinner = true;

            //console.log(url)
            //await self.$http.get(api_endpoints.spatial_query + '/' + spatialquery_id + '/check_cddp_question?proposal_id='+proposal_id)
            await self.$http.get(url)
            .then((response) => {
                swal(
                    'Question Found in Proposal Schema!',
                    response.body.message,
                    'success'
                )
                self.show_spinner = false;
            }, (error) => {
                swal(
                    'Check Question Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
                self.show_spinner = false;
            });
        },

        has_form_errors: function () {
            console.log
            if (!this.spatialquery.question) { this.missing_fields.push({'label':'Question field is required'}); }
            if ((!this.spatialquery.answer_mlq || this.spatialquery.answer_mlq==-1) && this.masterlistQuestionOptions) { this.missing_fields.push({'label':'Answer field is required'}); }
            if (!this.spatialquery.layer) { this.missing_fields.push({'label':'Layer Name field is required'}); }
            //if (this.spatialquery.layer_url==='') { this.missing_fields.push({'label':'Layer URL field is required'}); }
            if (!this.spatialquery.group) { this.missing_fields.push({'label':'Spatial Question Group field is required'}); }
            if (!this.spatialquery.how) { this.missing_fields.push({'label':'Intersector operator field is required'}); }
            if (!this.spatialquery.column_name) { this.missing_fields.push({'label':'Column name field is required'}); }
            if (!this.spatialquery.operator) { this.missing_fields.push({'label':'Operator field is required'}); }
            if (!this.spatialquery.buffer) { this.spatialquery.buffer=0 }

//            if (!this.spatialquery.answer && ['text', 'text_area'].includes(this.spatialquery.answer_type)) { this.missing_fields.push({'label':'Answer (Proponent Section) field is required'}); }
	    if (!this.spatialquery.proponent_items[0]['answer'] && ['text', 'text_area'].includes(this.spatialquery.answer_type)) { 
                this.missing_fields.push({'label':'Answer (Proponent Section) field is required'}); 
            }

//	    for (let i = 0; i < this.spatialquery.proponent_items.length; i++) {
//	        if (this.spatialquery.proponent_items[i])
//	    }

            //if (this.spatialquery.operator && (this.spatialquery.operator == 'Equals' || this.spatialquery.operator != 'GreaterThan' || this.spatialquery.operator != 'LessThan')) { 
            if(['Equals','GreaterThan','LessThan'].includes(this.spatialquery.operator)) {
                if (!this.spatialquery.value) { 
                    this.missing_fields.push({'label':'Value field is required (for Equals/GreaterThan/LessThan operators)'}); 
                }
            }

            if (!this.spatialquery.visible_to_proponent && !this.masterlistQuestionOptions) { this.missing_fields.push({'label':'Visible to Proponent field is required'}); }
            if (!this.spatialquery.visible_to_proponent && this.masterlistQuestionOptions) { this.spatialquery.visible_to_proponent=true; }

            if (this.missing_fields.length>0) {
                return true;
            } 
            return false
        },

        addTableEntry: async function(e) {
            await this.$http.get('/api/spatial_query_paginated/spatial_query_question_datatable_list/?format=datatables&length=all').then(res=>{
		//this.sq_questions = res.body['data'].map((item) => item.question);
		this.sq_questions = res.body['data']
            }).then((response)=>{
		this.isNewEntry = true;
		this.spatialquery.answer_type = '';
		//this.spatialquery.question = '';
		this.spatialquery.answer_mlq = null;
		this.spatialquery.answer_mlq_id = null;
		//this.spatialquery.layer_name = null;
		//this.spatialquery.layer_url = null;
		this.filterMasterlistQuestion = '';
		this.filterMasterlistOption = '';
		this.filterCddpOperator = '';
		this.spatialquery.layer = '';
		this.spatialquery.group = '';
		this.spatialquery.expiry = null;
		this.spatialquery.visible_to_proponent = null;
		this.spatialquery.buffer = 0;
		this.spatialquery.how = '';
		this.spatialquery.column_name = '';
		this.spatialquery.operator = '';
		this.spatialquery.value = '';
		this.spatialquery.prefix_answer = '';
		this.spatialquery.no_polygons_proponent = '-1';
		this.spatialquery.answer = '';
		this.spatialquery.prefix_info = '';
		this.spatialquery.no_polygons_assessor = '-1';
		this.spatialquery.assessor_info = '';
		this.spatialquery.regions = '';
		this.spatialquery.id = '';
		//this.spatialquery.proponent_items = [{'prefix': '', 'answer': ''}];
		//this.spatialquery.assessor_items = [{'prefix': '', 'info': ''}];
		this.spatialquery.show_add_info_section_prop = '';
		this.spatialquery.proponent_items = [{'': '', '': ''}];
		this.spatialquery.assessor_items = [{'': '', '': ''}];
		this.addedHeaders = [];
		this.addedExpanders = [];
     
		this.showOptions = false;
		this.proposal.lodgement_number = '';
		this.proposal.group_mlqs = false;
		this.proposal.all_mlqs = false;
		this.isModalOpen = true;
		this.showQuestionModal = true;
		this.showTestModal = false;
		this.showLayerAttrsModal = false;
		this.masterlistQuestionOptions = null;
		$(this.$refs.select_question).val(null).trigger('change');

            },err=>{
                swal(
                    'Get Application Selects Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });

            //this.has_missing_layers();
        },
        initEventListeners: function(){
            const self = this;

            self.$refs.spatial_query_question_table.vmDataTable.on('click','.edit-row', function(e) {

		self.$http.get('/api/spatial_query_paginated/spatial_query_question_datatable_list/?format=datatables&length=all').then(res=>{
		    //self.sq_questions = res.body['data'].map((item) => item.question);
		    self.sq_questions = res.body['data']
                }).then((response)=>{
		    e.preventDefault();
		    self.isNewEntry = false;
		    self.$refs.spatial_query_question_table.row_of_data = self.$refs.spatial_query_question_table.vmDataTable.row('#'+$(this).attr('data-rowid'));

		    self.spatialquery.id = self.$refs.spatial_query_question_table.row_of_data.data().id;
		    //self.filterMasterlistQuestion = self.$refs.spatial_query_question_table.row_of_data.data().filterMasterlistQuestion;
		    self.spatialquery.question = self.$refs.spatial_query_question_table.row_of_data.data().question;
		    self.spatialquery.answer_mlq = self.$refs.spatial_query_question_table.row_of_data.data().answer_mlq;
		    //self.spatialquery.layer_name = self.$refs.spatial_query_question_table.row_of_data.data().layer_name;
		    //self.spatialquery.layer_url = self.$refs.spatial_query_question_table.row_of_data.data().layer_url;
		    self.spatialquery.layer = self.$refs.spatial_query_question_table.row_of_data.data().layer;
		    self.spatialquery.group = self.$refs.spatial_query_question_table.row_of_data.data().group;
		    self.spatialquery.expiry = self.$refs.spatial_query_question_table.row_of_data.data().expiry;
		    self.spatialquery.visible_to_proponent = self.$refs.spatial_query_question_table.row_of_data.data().visible_to_proponent;
		    self.spatialquery.buffer = self.$refs.spatial_query_question_table.row_of_data.data().buffer;
		    self.spatialquery.how = self.$refs.spatial_query_question_table.row_of_data.data().how;
		    self.spatialquery.column_name = self.$refs.spatial_query_question_table.row_of_data.data().column_name;
		    self.spatialquery.operator = self.$refs.spatial_query_question_table.row_of_data.data().operator;
		    self.spatialquery.value = self.$refs.spatial_query_question_table.row_of_data.data().value;
		    self.spatialquery.regions = self.$refs.spatial_query_question_table.row_of_data.data().regions;
		    self.spatialquery.show_add_info_section_prop = self.$refs.spatial_query_question_table.row_of_data.data().show_add_info_section_prop;
		    self.spatialquery.proponent_items = self.$refs.spatial_query_question_table.row_of_data.data().proponent_items;
		    self.spatialquery.assessor_items = self.$refs.spatial_query_question_table.row_of_data.data().assessor_items;

		    self.spatialquery.prefix_answer = self.$refs.spatial_query_question_table.row_of_data.data().prefix_answer;
		    self.spatialquery.no_polygons_proponent = self.$refs.spatial_query_question_table.row_of_data.data().no_polygons_proponent;
		    self.spatialquery.answer = self.$refs.spatial_query_question_table.row_of_data.data().answer;
		    self.spatialquery.prefix_info = self.$refs.spatial_query_question_table.row_of_data.data().prefix_info;
		    self.spatialquery.no_polygons_assessor = self.$refs.spatial_query_question_table.row_of_data.data().no_polygons_assessor;
		    self.spatialquery.assessor_info = self.$refs.spatial_query_question_table.row_of_data.data().assessor_info;

		    self.filterMasterlistQuestion = self.spatialquery.question
		    self.filterMasterlistOption = self.spatialquery.answer_mlq
		    self.filterCddpOperator = self.spatialquery.operator

		    self.addedOptions = self.$refs.spatial_query_question_table.row_of_data.data().options;
		    self.addedHeaders = self.$refs.spatial_query_question_table.row_of_data.data().headers;       
		    self.addedExpanders = self.$refs.spatial_query_question_table.row_of_data.data().expanders;

		    self.isModalOpen = true;
		    self.showQuestionModal = true;
		    self.showTestModal = false;
		    self.showLayerAttrsModal = false;
		    self.showTestJsonResponse = false;
		    $(self.$refs.select_question).val(self.spatialquery.question).trigger('change');
		},err=>{
		    swal(
			'Get Application Selects Error',
			helpers.apiVueResourceError(err),
			'error'
		    )
		});

            });

            self.$refs.spatial_query_question_table.vmDataTable.on('click','.delete-row', function(e) {
                e.preventDefault();
                self.$refs.spatial_query_question_table.row_of_data = self.$refs.spatial_query_question_table.vmDataTable.row('#'+$(this).attr('data-rowid'));
                self.spatialquery.id = self.$refs.spatial_query_question_table.row_of_data.data().id;

                swal({
                    title: "Delete Spatialquery",
                    text: "Are you sure you want to delete?",
                    type: "question",
                    showCancelButton: true,
                    confirmButtonText: 'Accept'

                }).then(async (result) => {
                    if (result) {
                        await self.$http.delete(helpers.add_endpoint_json(api_endpoints.spatial_query,(self.spatialquery.id+'/delete_spatialquery')))
                        .then((response) => {
                            self.$refs.spatial_query_question_table.vmDataTable.ajax.reload();
                        }, (error) => {
                            swal(
                                'Delete Error',
                                helpers.apiVueResourceError(error),
                                'error'
                            )
                        });
                    }

                },(error) => {
                    //
                });                
            });

            self.$refs.spatial_query_question_table.vmDataTable.on('click','.test-row', function(e) {
                e.preventDefault();
                self.isNewEntry = false;
                self.proposal.group_mlqs = false;
                self.$refs.spatial_query_question_table.row_of_data = self.$refs.spatial_query_question_table.vmDataTable.row('#'+$(this).attr('data-rowid'));
                self.proposal.lodgement_number = self.$refs.spatial_query_question_table.row_of_data.data().lodgement_number;
                //self.proposal.group_mlqs = self.$refs.spatial_query_question_table.row_of_data.data().group_mlqs;
                self.proposal.all_mlqs = self.$refs.spatial_query_question_table.row_of_data.data().all_mlqs;
                self.proposal.masterlist_question_id = $(this).attr('data-rowid')
                self.isModalOpen = true;
                self.showTestModal = true;
                self.showQuestionModal = false;
                self.showLayerAttrsModal = false;
                self.showTestJsonResponse = false;
                self.sqs_response = ''
            });

            self.$refs.spatial_query_question_table.vmDataTable.on('click','.update-row', function(e) {
                e.preventDefault();
                self.$refs.spatial_query_question_table.row_of_data = self.$refs.spatial_query_question_table.vmDataTable.row('#'+$(this).attr('data-rowid'));
                self.spatialquery.id = self.$refs.spatial_query_question_table.row_of_data.data().id;
                self.spatialquery.layer = self.$refs.spatial_query_question_table.row_of_data.data().layer;

                let vm = this;
                const data = {}
                data['csrfmiddlewaretoken'] = self.csrf_token;
                data['layer'] = self.spatialquery.layer;

                swal({
                    title: "Check Spatialquery Layer",
                    //text: "Input Proposal Lodgement Number",
                    type: "question",
                    showCancelButton: true,
                    confirmButtonText: 'OK',
                    input: 'radio',
                    inputOptions: {
                      'check_layer':  'Check Layer Exists on SQS',
                      'reload_layer': 'Create/Update Layer in SQS',
                    }
                }).then(async (result) => {
                    console.log("Result: " + result);
                    if (!result) {
                        swal(
                            'Please select an option',
                            null,
                            'warning'
                        )
                        return;
                    }

                    if (result=='check_layer') {
                        let url = helpers.add_endpoint_json(api_endpoints.spatial_query, self.spatialquery.layer.layer_name+'/check_sqs_layer');
                        self.check_sqs_layer(url)

                    }
                    else if (result=='reload_layer') {
                        let url = helpers.add_endpoint_json(api_endpoints.spatial_query, self.spatialquery.layer.layer_name + '/create_or_update_sqs_layer');
                        self.create_or_update_sqs_layer(url, data)

                    }
                },(error) => {
                    //
                });                
            });

            self.$refs.spatial_query_question_table.vmDataTable.on('click','.check-row', function(e) {
                e.preventDefault();
                self.$refs.spatial_query_question_table.row_of_data = self.$refs.spatial_query_question_table.vmDataTable.row('#'+$(this).attr('data-rowid'));

                let spatialquery_id = self.$refs.spatial_query_question_table.row_of_data.data().id;

                //console.log(api_endpoints.spatial_query + '/check_sqs_layer?layer_name=' + layer_name)
                swal({
                    title: "Check Spatialquery Question",
                    text: "Input Proposal Lodgement Number",
                    type: "question",
                    showCancelButton: true,
                    confirmButtonText: 'Check',
                    input: 'text',
                    //html: '<input type="text" placeholder="Enter Proposal Lodgement Number" style="width: 65%"></input>',
                }).then(async (result) => {
                    console.log("Result: " + result);
                    if (!result) {
                        swal(
                            'Please input Proposal Lodgement Number',
                            null,
                            'warning'
                        )
                        return;
                    }

                    let proposal_id = result
                    let url = api_endpoints.spatial_query + '/' + spatialquery_id + '/check_cddp_question?proposal_id=' + proposal_id;
                    self.check_cddp_question(url);

                },(error) => {
                    //
                });                

            });

            self.$refs.spatial_query_question_table.vmDataTable.on('click','.view-layer-overlay', function(e) {
                e.preventDefault();
                self.$refs.spatial_query_question_table.row_of_data = self.$refs.spatial_query_question_table.vmDataTable.row('#'+$(this).attr('data-rowid'));

                let spatialquery_id = self.$refs.spatial_query_question_table.row_of_data.data().id;

                //console.log(api_endpoints.spatial_query + '/check_sqs_layer?layer_name=' + layer_name)
                swal({
                    title: "View Layer/Polygon Overlay",
                    text: "Input Proposal Lodgement Number",
                    type: "question",
                    showCancelButton: true,
                    confirmButtonText: 'Check',
                    input: 'text',
                    //html: '<input type="text" placeholder="Enter Proposal Lodgement Number" style="width: 65%"></input>',
                }).then(async (result) => {
                    console.log("Result: " + result);
                    if (!result) {
                        swal(
                            'Please input Proposal Lodgement Number',
                            null,
                            'warning'
                        )
                        return;
                    }

                    let proposal_id = result
                    let url = api_endpoints.spatial_query + '/' + spatialquery_id + '/view_layer_polygon_overlay?proposal_id=' + proposal_id;
                    self.show_layer_polygon_overlay(url);

                },(error) => {
                    //
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
                on("select2:selecting",function (e) {
                    let selected = $(e.currentTarget);
                }).
                on("select2:select",function (e) {
                    let selected = $(e.currentTarget);
                    self.filterMasterlistQuestion=selected.val()
                    //self.setShowOptions(selected.val())
                }).
                on("select2:unselect",function (e) {
                    let selected = $(e.currentTarget);
                    self.filterMasterlistQuestion=selected.val()
                });
        },
        initSelects: async function() {

            //console.log(helpers.add_endpoint_json(api_endpoints.spatial_query,'get_spatialquery_selects'))
            await this.$http.get(helpers.add_endpoint_json(api_endpoints.spatial_query,'get_spatialquery_selects')).then(res=>{
                    this.spatialquery_selects = res.body
                    this.masterlist_questions = this.spatialquery_selects.all_masterlist
                    this.is_admin = this.spatialquery_selects.permissions.is_admin
            },err=>{
                swal(
                    'Get Application Selects Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });

            await this.$http.get(helpers.add_endpoint_json(api_endpoints.spatial_query,'get_sqs_layers')).then(res=>{
                    this.available_sqs_layers = res.body
            },err=>{
                swal(
                    'Get Application Selects Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });

            //this.has_missing_layers();

           this.initQuestionSelector();
        },        

        fetchProfile: function(){
            let vm = this;
            Vue.http.get(api_endpoints.profile).then((response) => {
                vm.profile = response.body

            },(error) => {
                console.log(error);

            })
        },

    },
    mounted: function() {
        this.form = document.forms.spatial_query_question;
        this.fetchProfile();
        this.$nextTick(() => {
            this.initEventListeners();
            this.initSelects();
        });
    }
}
</script>

<style lang="css" scoped>
.control-label label > div {
    text-align: left;
}
.med {
    transform: scale(1.5);
}
a.disabled {
  color: grey;
  pointer-events: none;
  cursor: default;
}

br {
  content: " ";
  display: block;
  margin: 5px;
}

hr {
  border: 0;
  clear:both;
  display:block;
  width: 96%;               
  background-color:black;
  height: 1px;
}

.superscript { position: relative; top: -0.2em; font-size: 140%; }
</style>
