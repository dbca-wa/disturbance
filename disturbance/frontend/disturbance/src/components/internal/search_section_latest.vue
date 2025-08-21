<template>
<div class="container" id="internalSearch">
    

    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Search Question
                        <a :href="'#'+kBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="kBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="kBody">
                    <div class="row">
                      <div class="col-sm-12">
                          <div>
                              <label for="" class="control-label" >Proposal Type</label>
                              <div>
                                  <div class="form-group">
                                      <select class="form-control" style="width:40%" v-model="selected_proposal_type_id" @change="chainedSelectAppType(selected_proposal_type_id)">
                                          <option value="" selected disabled>Proposal Type</option>
                                          <option v-for="proposal_type in proposal_types" :value="proposal_type.value" :key="proposal_type.value">
                                                {{ proposal_type.text }}
                                          </option>
                                      </select>
                                  </div>
                                </div>
                            </div>
                            <div v-if="display_region_selectbox">
                                <label for="" class="control-label" >Region  </label>
                                <div >
                                    <div class="form-group">
                                        <select v-model="selected_region" class="form-control" style="width:40%" @change="chainedSelectDistricts(selected_region)">
                                            <!-- <option value="" selected disabled>Select region</option> -->
                                            <option value="" selected>All</option>
                                            <option v-for="region in regions" :value="region.value" :key="region.value">
                                                {{ region.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div v-if="display_region_selectbox">
                                <label for="" class="control-label">District </label>
                                <div >
                                    <div class="form-group">
                                        <select  v-model="selected_district" class="form-control" style="width:40%">
                                        <!-- <option value="" selected disabled>Select district</option> -->
                                        <option value="" selected >All</option>
                                            <option v-for="district in districts" :value="district.value" :key="district.value">
                                                {{ district.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div v-if="display_activity_matrix_selectbox">
                              <div v-if="activities.length > 0">
                                <label for="" class="control-label" >Activity Type </label>
                                <div >
                                  <div class="form-group">
                                    <select v-model="selected_activity" class="form-control" style="width:40%">
                                      <!-- <option value="" selected disabled>Select activity</option> -->
                                      <option value="" selected>All</option>
                                      <option v-for="activity in activities" :value="activity.value" :key="activity.value">
                                        {{ activity.text }}
                                      </option>
                                    </select>
                                  </div>
                                </div>
                              </div>
                            </div>

                            <div v-if="display_section_selectbox">
                              <div v-if="sections.length > 0">
                                <label for="" class="control-label" >Sections </label>
                                <div >
                                  <div class="form-group">
                                    <select v-model="selected_section" class="form-control" style="width:40%" @change="chainedSelectSections(selected_section)">
                                      <option value="" selected disabled>Select section</option>
                                      <option v-for="section in sections" :value="section.value" :key="section.value">
                                        {{ section.text }}
                                      </option>
                                    </select>
                                  </div>
                                </div>
                              </div>
                            </div>

                            <div>
                              <div v-if="questions.length > 0">
                                <label for="" class="control-label" >Questions </label>
                                <div >
                                  <div class="form-group">
                                    <select v-model="selected_question" class="form-control" style="width:40%" @change="chainedSelectOptions(selected_question)">
                                      <option value="" selected disabled>Select question</option>
                                      <option v-for="question in questions" :value="question.value" :key="question.value">
                                        {{ question.text }}
                                      </option>
                                    </select>
                                  </div>
                                </div>
                              </div>
                            </div>

                            <div v-if="selected_question">
                              <div v-if="date_type">
                                <label class="control-label"  for="Name">Answer</label>
                                <div class="form-group">
                                    <div class="input-group date" ref="question_date" style="width: 70%;">
                                        <input type="text" class="form-control" name="question_date" placeholder="DD/MM/YYYY" v-model="selected_option">
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                              </div>

                              <div v-else-if="select_type && options.length > 0">
                                <label for="" class="control-label" >Options </label>
                                <div >
                                  <div class="form-group">
                                    <select v-model="selected_option" class="form-control" style="width:40%" >
                                      <option value="" selected disabled>Select option</option>
                                      <option v-for="option in options" :value="option.value" :key="option.value">
                                        {{ option.text }}
                                      </option>
                                    </select>
                                  </div>
                                </div>
                              </div>
                              <div v-else>
                                <label class="control-label"  for="Name">Answer</label>
                                <div class="form-group">
                                    <div class="input-group" style="width: 70%;">
                                        <input type="text" class="form-control" name="question_date"  v-model="selected_option">
                                    </div>
                                </div>
                              </div>

                            </div>
                                                     
                      </div>
                                   
                    </div>

                    <div class="row">
                      <div class="col-lg-12">
                          <ul class="list-inline" style="display: inline; width: auto;">                          
                              <li class="list-inline-item" v-for="(item,i) in searchKeywords" :key="i">
                                <button @click.prevent="" class="btn btn-light" style="margin-top:5px; margin-bottom: 5px">{{item}}</button><a href="" @click.prevent="removeKeyword(i)"><span class="glyphicon glyphicon-remove "></span></a>
                              </li>
                          </ul>
                      </div>
                    </div>

                    <div class="row">
                      <div class="col-lg-12">
                        <div >
                          <button type="button" class="btn btn-primary btn-margin" @click.prevent="search()" :disabled="search_btn_disabled">
                              <i v-if="search_btn_disabled" class="fa fa-search fa-spinner fa-spin"></i>
                              <i v-else class="fa fa-search"></i>
                              Search
                          </button>
                          <button type="button" class="btn btn-primary btn-margin" @click.prevent="reset">
                              <i class="fa fa-eraser"></i>
                              Clear
                          </button>
                          <button type="button" class="btn btn-primary" @click.prevent="geoJsonButtonClicked" :disabled="get_spatialfile_btn_disabled">
                              <i v-if="get_spatialfile_btn_disabled" class="fa fa-download fa-spinner fa-spin"></i>
                              <i v-else class="fa fa-download"></i>
                              Get Spatial File
                          </button>
                        </div>
                      </div> 
                    </div>


                    <div id="loadingSpinner2" style="display: none; text-align: center; padding: 20px;">
                      <!-- You can replace this with your preferred loading spinner or element -->
                      <i class='fa fa-4x fa-spinner fa-spin'></i>
                      <p>Loading...</p>
                  </div>
                    <div class="col-lg-12">
                        <datatable ref="proposal_datatable" :id="datatable_id" :dtOptions="proposal_options"  :dtHeaders="proposal_headers"/>
                    </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { v4 as uuidv4 } from 'uuid';
import $ from 'jquery'
import datatable from '@/utils/vue/datatable.vue'
import {
  api_endpoints,
  helpers,
  constants
}
from '@/utils/hooks'
export default {
  name: 'SearchSection',
  props: {
    
  },
  data() {
    let vm = this;
    return {
      rBody: 'rBody' + uuidv4(),
      oBody: 'oBody' + uuidv4(),
      kBody: 'kBody' + uuidv4(),
      loading: [],
      searchKeywords: [],
      searchProposal: true,
      searchApproval: false,
      searchCompliance: false,
      search_btn_disabled: false,
      get_spatialfile_btn_disabled: false,
      referenceWord: '',
      keyWord: null,
      selected_organisation:'',
      organisations: null,
      results: [],
      errors: false,
      errorString: '',
      form: null,
      pBody: 'pBody' + uuidv4(),
      pBody2: 'pBody2' + uuidv4(),

      selected_application_name: '',
      selected_proposal_type_id: null,
      selected_region: '',
      selected_district: '',
      proposal_types: [],
      selected_activity: '',
      selected_section:'',
      selected_question:'',
      selected_option:'',
      regions: [],
      districts: [],
      sections:[],
      questions:[],
      options:[],
      api_options:[],
      api_questions:[],
      api_sections:[],
      api_proposal_types:[],
      activity_matrix: [],
      all_activity_matrices: [],
      activities: [],
      display_region_selectbox: true,
      display_activity_matrix_selectbox: true,
      display_section_selectbox: true,
      date_type: false,
      select_type: false,
      datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
      site_url: (api_endpoints.site_url.endsWith("/")) ? (api_endpoints.site_url): (api_endpoints.site_url + "/"),
      datatable_id: 'proposal-datatable-'+uuidv4(),
      proposal_headers:["Number","Type","Proponent","Text found","Action"],
      proposal_options:{
          language: {
              processing: constants.DATATABLE_PROCESSING_HTML,
          },
          responsive: true,
          /*ajax: {
              "url": 'api/empty_list',
              "dataSrc": ''
          },*/
          dom: 'Bfrtip',
          buttons:[
                'excel', 'csv', ],
          
          data: vm.results,
          columns: [
              {data: "number"},
              {data:"type"},
              {data: "applicant"},
              {//data: "text.value"
                data: "text",
                mRender: function (data) {
                  if(data.value){
                    return data.value;
                  }
                  else
                  {
                    return data;
                  }
                }
              },
              {
                data: "id",
                  mRender:function (data,type,full) {
                        let links = '';
                        if(full.type == 'Proposal'){
                          links +=  `<a href='/internal/proposal/${full.id}'>View</a><br/>`;
                        }
                        if(full.type == 'Compliance'){
                          links +=  `<a href='/internal/compliance/${full.id}'>View</a><br/>`;
                        }
                        if(full.type == 'Approval'){
                          links +=  `<a href='/internal/approval/${full.id}'>View</a><br/>`;
                        }
                        return links;
                  }
              }
          ],
          processing: true,
          initComplete: function() {
                    $('#loadingSpinner2').hide();
          },
      }
    }
    
  },
    watch: {
      
    },
    components: {
        datatable,
    },
    // beforeRouteEnter:function(to,from,next){
        // utils.fetchOrganisations().then((response)=>{
        //     next(vm => {
        //         vm.organisations = response;
        //     });
        // },
        // (error) =>{
        //     console.log(error);
        // });
    // },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        }
    },
    methods: {
        addListeners: function(){
            // let vm = this;
            // Initialise select2 for region
            // $(vm.$refs.searchOrg).select2({
            //     "theme": "bootstrap",
            //     allowClear: true,
            //     placeholder:"Select Organisation"
            // }).
            // on("select2:select",function (e) {
            //     var selected = $(e.currentTarget);
            //     vm.selected_organisation = selected.val();
            // }).
            // on("select2:unselect",function (e) {
            //     var selected = $(e.currentTarget);
            //     vm.selected_organisation = selected.val();
            // });
        },

        add: function() {
          let vm = this;
          if(vm.keyWord != null)
          {
            vm.searchKeywords.push(vm.keyWord);
          }
        },
        removeKeyword: function(index) {
          let vm = this;
          if(index >-1)
          {
            vm.searchKeywords.splice(index,1);
          }
        },
        reset: function() {
          let vm = this;
          if(vm.keyWord != null)
          {
            vm.searchKeywords = [];
          }
          /*vm.searchProposal = false;
          vm.searchApproval = false;
          vm.searchCompliance = false; */
          vm.keyWord = null; 
          vm.results = [];
          vm.selected_application_name='';
          vm.selected_proposal_type_id=null;
          vm.selected_region = '';
          vm.selected_district = '';
          vm.selected_activity = '';
          vm.selected_section='';
          vm.selected_question='';
          vm.selected_option='';
          vm.sections = [];
          vm.questions=[];
          vm.options=[];
          vm.date_type=false;
          vm.select_type=false;
          vm.$refs.proposal_datatable.vmDataTable.clear()
          vm.$refs.proposal_datatable.vmDataTable.draw();   
           $('#loadingSpinner2').hide();   
        },

        search: function() {
          let vm = this;
          // swal.fire(
          //         'Missing fields',
          //         'Please select all the mandatory fields',
          //         'error'
          //       );
          if(!vm.selected_proposal_type_id || !vm.selected_section || !vm.selected_question || !vm.selected_option )
          {
            //console.log('here');
            swal.fire(
                  'Missing fields',
                  'Please select all the mandatory fields',
                  'error'
                );
          }
          else
          {
            //$('#loadingSpinner2').show();
            vm.search_btn_disabled = true;
            fetch('/api/search_sections.json',{
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                proposal_type_id: vm.selected_proposal_type_id,
                region: vm.selected_region,
                district: vm.selected_district,
                activity: vm.selected_activity,
                section_label: vm.selected_section,
                question_id: vm.selected_question,
                option_label: vm.selected_option,
                is_internal: true,
              })
            }).then(async (res) => {
              if (!res.ok) {
                  const errorText = await res.text();
                  throw new Error(errorText);
              }
              vm.results = await res.json();
              vm.$refs.proposal_datatable.vmDataTable.clear()
              vm.$refs.proposal_datatable.vmDataTable.rows.add(vm.results);
              vm.$refs.proposal_datatable.vmDataTable.draw();
              //$('#loadingSpinner2').hide();
              vm.search_btn_disabled = false;
            }).catch(err => {
              console.log(err.message);
              //$('#loadingSpinner2').hide();
              vm.search_btn_disabled = false;
            });
          }

        },
   

    search_reference: function() {
          let vm = this;
          if(vm.referenceWord)
          {
            fetch('/api/search_reference.json',{
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                reference_number: vm.referenceWord,
              })
            }).then(async (res) => {
              if (!res.ok) {
                  const errorText = await res.text();
                  throw new Error(errorText);
              }
              const responseBody = await res.json();
              console.log(res)
              vm.errors = false; 
              vm.errorString = '';
              vm.$router.push({ path: '/internal/'+responseBody.type+'/'+responseBody.id });
              }).catch(error => {
              console.log(error.message);
              vm.errors = true;
              // vm.errorString = helpers.apiVueResourceError(error);
              vm.errorString = error.message;
            });
          }

        },

    searchList: function(id, search_list){
        /* Searches for dictionary in list */
        for (var i = 0; i < search_list.length; i++) {
            if (search_list[i].value == id) {
                return search_list[i];
            }
        }
        return [];
    },
      fetchRegions: function(){
        let vm = this;

        fetch(api_endpoints.regions).then(
          async (response) => {
              vm.api_regions = await response.json();
              //console.log('api_regions ' + response.body);
              for (var i = 0; i < vm.api_regions.length; i++) {
                  this.regions.push( {text: vm.api_regions[i].name, value: vm.api_regions[i].id, districts: vm.api_regions[i].districts} );
              }
          },(error) => {
            console.log(error);
          }
        )
      },
      fetchSections: function(){
        let vm = this;

        fetch(api_endpoints.proposal_type_sections).then(
          async (response) => {
            vm.api_sections = await response.json();
            //console.log('api_regions ' + response.body);
            for (var i = 0; i < vm.api_sections.length; i++) {
                this.sections.push( {text: vm.api_sections[i].section_label, value: vm.api_sections[i].section_label, questions: vm.api_sections[i].section_questions} );
            }
          },(error) => {
            console.log(error);
          }
        )
      },
      chainedSelectAppType: function(proposal_type_id){
        /* reset */
        let vm = this;
            vm.selected_region = '';
            vm.selected_district = '';
            vm.selected_activity = '';
            vm.selected_section='';
            vm.selected_question='';
            vm.selected_option='';
            vm.sections = [];
            vm.questions=[];
            vm.options=[];
            vm.date_type=false;
            vm.select_type=false;
            vm.api_sections=[];
            vm.activity_matrix=[];
            vm.selected_application_name = this.searchList(proposal_type_id, vm.proposal_types).name;
            vm.getSelectedAppActivityMatrix(vm.selected_application_name);
            vm.api_sections = this.searchList(proposal_type_id, vm.proposal_types).sections;
            if (vm.api_sections.length > 0) {
                for (var i = 0; i < vm.api_sections.length; i++) {
                        this.sections.push( {text: vm.api_sections[i].section_label, value: vm.api_sections[i].section_label, questions: vm.api_sections[i].section_questions} );

                  }
                }
      },
      chainedSelectDistricts: function(region_id){
        let vm = this;
            vm.districts = [];

            var api_districts = this.searchList(region_id, vm.regions).districts;
            if (api_districts.length > 0) {
                for (var i = 0; i < api_districts.length; i++) {
                    this.districts.push( {text: api_districts[i].name, value: api_districts[i].id} );
                }
            }
      },
      chainedSelectSections: function(section_name){
        let vm = this;
            vm.questions = [];
            vm.options=[];
            vm.date_type=false;
            vm.select_type=false;

            var api_questions = this.searchList(section_name, vm.sections).questions;
            if (api_questions.length > 0) {
                for (var i = 0; i < api_questions.length; i++) {
                    this.questions.push( {text: api_questions[i].question_name, value: api_questions[i].question_id, options: api_questions[i].question_options, answer_type: api_questions[i].answer_type  } );
                }
            }
      },
      chainedSelectOptions: function(question_id){
        let vm = this;
            vm.options = [];  
            vm.date_type=false;
            vm.select_type=false;
            var found_question=this.searchList(question_id, vm.questions)

            //var api_options = this.searchList(question_name, vm.questions).options;
            var api_options = found_question.options;
            if(found_question.answer_type=='date'){
              vm.date_type =true;
              $(vm.$refs.question_date).datetimepicker(vm.datepickerOptions);
              //vm.eventListeners()
            }
            else if (api_options&&api_options.length > 0) {
                vm.select_type=true;
                for (var i = 0; i < api_options.length; i++) {
                    this.options.push( {text: api_options[i].label, value: api_options[i].label} );
                }
            }
      },
      // chainedSelectProposalType: function(application_name){
      //   let vm = this;
      //       vm.sections = [];

      //       //var api_options = this.searchList(question_id, vm.questions).options;
      //       if (vm.api_sections.length > 0) {
      //           for (var i = 0; i < vm.api_sections.length; i++) {
      //             if(vm.api_section[i].proposal_type_name==application_name)
      //               {
      //                   this.sections.push( {text: vm.api_sections[i].section_label, value: vm.api_sections[i].section_name, questions: vm.api_sections[i].section_questions} );

      //               }
      //             }
      //           }
      // },
      fetchActivityMatrix: function(){
        let vm = this;
            vm.sub_activities1 = [];
            vm.sub_activities2 = [];
            vm.categories = [];
            vm.approval_level = '';

        fetch(api_endpoints.activity_matrix).then(
          async (response) => {
            let data = await response.json();
            this.activity_matrix = data[0].schema[0];
            this.keys_ordered = data[0].ordered;
            //console.log('this.activity_matrix ' + response.body[0].schema);

            var keys = this.keys_ordered ? Object.keys(this.activity_matrix).sort() : Object.keys(this.activity_matrix)
            for (var i = 0; i < keys.length; i++) {
                this.activities.push( {text: keys[i], value: keys[i]} );
            }
          },(error) => {
            console.log(error);
          }
        )
      },
      fetchAllActivityMatrices: function(){
        let vm = this;
        vm.sub_activities1 = [];
        vm.sub_activities2 = [];
        vm.categories = [];
        vm.approval_level = '';
        fetch(api_endpoints.activity_matrix).then(
          async (response) => {
            this.all_activity_matrices = await response.json();
            //vm.fetchRegions();
          },(error) => {
            console.log(error);
          }
        )
      },
      getSelectedAppActivityMatrix: function(selected_app){
		    let vm = this;
        vm.activities=[];
        vm.sub_activities1 = [];
        vm.sub_activities2 = [];
        vm.categories = [];
        vm.approval_level = '';
        let activity_matrix_obj = [...this.all_activity_matrices.filter(matrix => matrix.name == selected_app)]        
        this.activity_matrix = activity_matrix_obj[0].schema[0];
        this.keys_ordered = activity_matrix_obj[0].ordered;
        var keys = this.keys_ordered ? Object.keys(this.activity_matrix).sort() : Object.keys(this.activity_matrix)
        for (var i = 0; i < keys.length; i++) {
            this.activities.push( {text: keys[i], value: keys[i]} );
        }
       
      },
      chainedSelectSubActivities1: function(activity_name){
        let vm = this;
            vm.sub_activities1 = [];
            vm.sub_activities2 = [];
            vm.categories = [];
            vm.selected_sub_activity1 = '';
            vm.selected_sub_activity2 = '';
            vm.selected_category = '';
            vm.approval_level = '';

            vm.sub_activities1 = [];
            var [api_activities, res] = this.get_sub_matrix(activity_name, vm.activity_matrix)
            if (res == "null" || res == null) {
                //for (var i = 0; i < vm.activity_matrix.length; i++) {
                //    if (activity_name == vm.activity_matrix[i]['text']) {
                //        vm.activity_matrix[i]['sub_matrix']
                //    }
                //}
                vm.approval_level = api_activities;
                return;
            } else if (res == "pass") {
                var api_sub_activities = this.get_sub_matrix("pass", api_activities[0])[0];
                if ("pass" in api_sub_activities[0]) {
                    // go straight to categories widget
                    var categories = api_sub_activities[0]['pass']
                    for (var i = 0; i < categories.length; i++) {
                        this.categories.push( {text: categories[i][0], value: categories[i][0], approval: categories[i][1]} );
                    }

                } else {
                    // go to sub_activity2 widget
                    for (var j = 0; j < api_sub_activities.length; j++) {
                        var key = Object.keys(api_activities[j])[0];
                        this.sub_activities1.push( {text: key, value: key, sub_matrix: api_activities[j][key]} );
                    }
                }
            } else {
                for (var k = 0; k < api_activities.length; k++) {
                    var activity_key = Object.keys(api_activities[k])[0];
                    this.sub_activities1.push( {text: activity_key, value: activity_key, sub_matrix: api_activities[k][activity_key]} );
                }
            }
      },
      fetchProposalTypes: function(){
        let vm = this;

        fetch(api_endpoints.searchable_proposal_types).then(
          async (response) => {
            vm.api_proposal_types = await response.json();
            //console.log('api_proposal_types ' + response.body);

            for (var i = 0; i < vm.api_proposal_types.length; i++) {
                this.proposal_types.push( {
                    text: vm.api_proposal_types[i].name_with_version,
                    value: vm.api_proposal_types[i].id,
                    sections: vm.api_proposal_types[i].sections,
                    name: vm.api_proposal_types[i].name,
                    //domain_used: vm.api_proposal_types[i].domain_used,
                    //activities: (vm.api_proposal_types[i].activity_app_types.length > 0) ? vm.api_proposal_types[i].activity_app_types : [],
                    //tenures: (vm.api_proposal_types[i].tenure_app_types.length > 0) ? vm.api_proposal_types[i].tenure_app_types : [],
                } );
            }
          },(error) => {
            console.log(error);
          }
        )
      },
      eventListeners:function () {
            let vm = this;
            // Initialise Date Picker
            //console.log('here');
            $(vm.$refs.question_date).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.question_date).on('dp.change', function(e){
                if ($(vm.$refs.question_date).data('DateTimePicker').date()) {
                    vm.selected_option =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.question_date).data('date') === "") {
                    vm.selected_option = "";
                }
             });
       },
       download_content: function (content, fileName, contentType) {
                var a = document.createElement("a");
                var file = new Blob([content], { type: contentType });
                a.href = URL.createObjectURL(file);
                a.download = fileName;
                a.click();
        },
       geoJsonButtonClicked: function () {
                let vm = this
                //let proposal_lodgement_numbers=[];
                vm.get_spatialfile_btn_disabled = true;
                let proposal_lodgement_numbers=vm.$refs.proposal_datatable.vmDataTable.columns(0).data().toArray()
                if(proposal_lodgement_numbers[0].length>0){
                  fetch('/api/get_search_geojson.json',{
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                      proposal_lodgement_numbers: proposal_lodgement_numbers[0],
                    })
                  }).then(async (res) => {
                    if (!res.ok) {
                        const errorText = await res.text();
                        throw new Error(errorText);
                    }
                    const responseBody = await res.json();
                    if(responseBody && responseBody.search_geojson)
                    {
                      var geojsonContent = JSON.stringify(responseBody.search_geojson);
                      vm.download_content(geojsonContent, 'DAS_layers.geojson', 'text/plain');
                    }
                    //vm.download_content(res.body.search_geojson, 'DAS_layers.geojson', 'text/plain');
                    vm.errors = false; 
                    vm.errorString = '';
                    vm.get_spatialfile_btn_disabled = false;
                  }).catch((error) => {
                    console.log(error.message);
                    vm.errors = true;
                    // vm.errorString = helpers.apiVueResourceError(error);
                    vm.errorString = error.message;
                    vm.get_spatialfile_btn_disabled = false;
                  });
                }
                else{
                    swal.fire(
                      'Missing records',
                      'No search results to include in the Spatial file',
                      'error'
                  );
                  vm.get_spatialfile_btn_disabled = false;
                }
                
            },

    },
    mounted: function () {
        let vm = this;
        vm.fetchRegions();
        vm.fetchProposalTypes();
        // vm.fetchActivityMatrix();
        vm.fetchAllActivityMatrices();
        vm.fetchSections();
        vm.proposal_options.data = vm.results;
        vm.$refs.proposal_datatable.vmDataTable.draw();
        this.$nextTick(()=>{
            vm.eventListeners();
        });
        $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
        } );
    },
    updated: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.addListeners();
            vm.eventListeners();
        });
        
    }
}
</script>
