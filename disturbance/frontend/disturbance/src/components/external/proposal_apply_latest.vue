<template lang="html">
    <div class="container" >
        <div class="row">
            <div class="col-sm-12">
                <form class="form-horizontal" name="personal_form" method="post">

                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">Apply on behalf of
                                <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                                    <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                </a>
                            </h3>
                        </div>
                        <div class="panel-body collapse in" :id="pBody">

                            <div class="col-sm-12">
                                <div class="form-group" v-if="!isLoading">
                                    <template v-if="apiaryTemplateGroup && !(profile.disturbance_organisations.length)">
                                        <div class="radio">
                                            <label :title="individualHasNoLicenceTitle()">
                                              <input :disabled="individualDisableApplyRadioButton()" type="radio" name="behalf_of_individual" v-model="behalf_of" value="individual"> On behalf of yourself
                                              <span v-html="individualExistingRecordText"></span>
                                            </label>
                                        </div>
                                    </template>
                                    <div v-if="profile.disturbance_organisations.length > 0">
                                        <div v-for="org in profile.disturbance_organisations" :key="org.id" class="radio">
                                            <label :title="orgHasNoLicenceTitle(org)">
                                              <input :disabled="orgDisableApplyRadioButton(org)" type="radio" name="behalf_of_org" v-model="behalf_of"  :value="org.id"> On behalf of {{org.name}}
                                              <span v-html="org.existing_record_text.notification"></span>
                                            </label>
                                        </div>
                                        <!--
                                        <div class="radio">
                                            <label class="radio-inline">
                                              <input type="radio" name="behalf_of_org" v-model="behalf_of"  value="other" > On behalf of an organisation (as an authorised agent)
                                            </label>
                                        </div>
                                        -->
                                    </div>
                                    <div v-else-if="behalf_of !== 'individual' && dasTemplateGroup">
                                        <p style="color:red"> You cannot add a New Disturbance because you do not have an associated Organisation. First add an Organisation. </p>
                                    </div>
                                </div>
                            </div>
                            <!--
                            <div v-if="behalf_of == 'other'" class="col-sm-12">
                                <div class="row">
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label">Organisation</label>
                                        <input type="text" class="form-control" name="first_name" placeholder="" v-model="agent.organisation">
                                    </div>
                                    <div class="form-group col-sm-1"></div>
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label" >ABN / ACN</label>
                                        <input type="text" class="form-control" name="last_name" placeholder="" v-model="agent.abn">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label" >Organisation contact given name(s)</label>
                                        <input type="text" class="form-control" name="last_name" placeholder="" v-model="agent.given_names">
                                    </div>
                                    <div class="form-group col-sm-1"></div>
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label" >Orgnisation contact surname</label>
                                        <input type="text" class="form-control" name="last_name" placeholder="" v-model="agent.surname">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label" >Organisation contact email address</label>
                                        <input type="text" class="form-control" name="last_name" placeholder="" v-model="agent.email">
                                    </div>
                                </div>
                            </div>
                            -->
                        </div>
                    </div>

                    <div v-if="behalf_of != ''" class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">Apply for
                                <a :href="'#'+pBody2" data-toggle="collapse"  data-parent="#userInfo2" expanded="true" :aria-controls="pBody2">
                                    <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                </a>
                            </h3>
                        </div>
                        <div class="panel-body collapse in" :id="pBody2">
                            <div>
                                <label for="" class="control-label" >{{ objectTypeLabel }}<a v-if="dasTemplateGroup" :href="proposal_type_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a></label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select class="form-control" style="width:40%" v-model="selected_application_id" @change="chainedSelectAppType(selected_application_id)">
                                            <option value="" selected disabled>{{ objectTypeListLabel }}</option>
                                            <option v-for="application_type in applicationTypesList" :value="application_type.value" :key="application_type.value">
                                                {{ application_type.text }}
                                                {{ application_type.display_text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div v-if="display_region_selectbox">
                                <label for="" class="control-label" >Region * <a :href="region_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a> </label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select v-model="selected_region" class="form-control" style="width:40%" @change="chainedSelectDistricts(selected_region)">
											<option value="" selected disabled>Select region</option>
                                            <option v-for="region in regions" :value="region.value" :key="region.value">
                                                {{ region.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div v-if="display_region_selectbox && selected_region">
                                <label for="" class="control-label" style="font-weight: normal;">District <a :href="district_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a></label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select  v-model="selected_district" class="form-control" style="width:40%">
											<option value="" selected disabled>Select district</option>
                                            <option v-for="district in districts" :value="district.value" :key="district.value">
                                                {{ district.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div v-if="display_activity_matrix_selectbox">
								<div v-if="activities.length > 0">
									<label for="" class="control-label" >Activity Type * <a :href="activity_type_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a></label>
									<div class="col-sm-12">
										<div class="form-group">
											<select v-model="selected_activity" @change="chainedSelectSubActivities1(selected_activity)" class="form-control" style="width:40%">
												<option value="" selected disabled>Select activity</option>
												<option v-for="activity in activities" :value="activity.value" :key="activity.value">
													{{ activity.text }}
												</option>
											</select>
										</div>
									</div>
								</div>

								<div v-if="sub_activities1.length > 0">
									<label for="" class="control-label" >Sub Activity 1 * <a :href="sub_activity_1_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a></label>
									<div class="col-sm-12">
										<div class="form-group">
											<select v-model="selected_sub_activity1" @change="chainedSelectSubActivities2(selected_sub_activity1)" class="form-control" style="width:40%">
												<option value="" selected disabled>Select sub_activity 1</option>
												<option v-for="sub_activity1 in sub_activities1" :value="sub_activity1.value" :key="sub_activity1.value">
													{{ sub_activity1.text }}
												</option>
											</select>
										</div>
									</div>
								</div>

								<div v-if="sub_activities2.length > 0">
									<label for="" class="control-label" >Sub Activity 2 * <a :href="sub_activity_2_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a></label>
									<div class="col-sm-12">
										<div class="form-group">
											<select v-model="selected_sub_activity2" @change="chainedSelectCategories(selected_sub_activity2)" class="form-control" style="width:40%">
												<option value="" selected disabled>Select sub_activity 2</option>
												<option v-for="sub_activity2 in sub_activities2" :value="sub_activity2.value" :key="sub_activity2.value">
													{{ sub_activity2.text }}
												</option>
											</select>
										</div>
									</div>
								</div>

								<!-- <div v-if="categories.length > 0">
									<label for="" class="control-label" >Category * <a :href="category_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a></label>
									<div class="col-sm-12">
										<div class="form-group">
											<select v-model="selected_category" @change="get_approval_level(selected_category)" class="form-control" style="width:40%">
												<option value="" selected disabled>Select category</option>
												<option v-for="category in categories" :value="category.value" :name="category.approval">
													{{ category.text }}
												</option>
											</select>
										</div>
									</div>
								</div> -->
                            </div>
                            <!-- For Testing
                            <div v-if="approval_level">
                                <label>Approval level required: </label>  {{ approval_level }}
                            </div>
                            -->


                        </div>
                    </div>

                    <div class="col-sm-12">
                        <button v-if="!creatingProposal" :disabled="isDisabled()" @click.prevent="submit()" class="btn btn-primary pull-right">Continue</button>
                        <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Creating</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>
<script>
import { v4 as uuidv4 } from 'uuid';
import {
  api_endpoints,
}
from '@/utils/hooks'
import utils from './utils'
export default {
  data: function() {
    // let vm = this;
    return {
        "proposal": null,
        agent: {},
        behalf_of: '',
        profile: {
            disturbance_organisations: []
        },
        "loading": [],
        form: null,
        pBody: 'pBody' + uuidv4(),
        pBody2: 'pBody2' + uuidv4(),

        selected_application_id: '',
        selected_application_name: '',
        selected_region: '',
        selected_district: '',
        application_types: [],
        selected_activity: '',
        selected_sub_activity1: '',
        selected_sub_activity2: '',
        selected_category: '',
        regions: [],
        districts: [],
        activity_matrix: [],
        all_activity_matrices: [],
        activities: [],
        sub_activities1: [],
        sub_activities2: [],
        categories: [],
        approval_level: '',
        creatingProposal: false,
        display_region_selectbox: false,
        display_activity_matrix_selectbox: false,
        site_url: (api_endpoints.site_url.endsWith("/")) ? (api_endpoints.site_url): (api_endpoints.site_url + "/"),
        apiaryTemplateGroup: false,
        dasTemplateGroup: false,
        global_settings:[],
    }
  },
  components: {
  },
  computed: {
      objectTypeLabel: function() {
          let returnStr = 'Proposal Type * ';
          if (this.apiaryTemplateGroup) {
              returnStr = 'Application Type';
          }
          return returnStr;
      },
      objectTypeListLabel: function() {
          let returnStr = 'Select proposal type* ';
          if (this.apiaryTemplateGroup) {
              returnStr = 'Select application type';
          }
          return returnStr;
      },
      individualExistingRecordText: function() {
          let approvalText = '';
          if (this.profile && this.profile.existing_record_text && this.profile.current_apiary_approval===null) {
              approvalText = this.profile.existing_record_text.notification + ' (There is no current Apiary Approval)';
          }
          return approvalText;
      },
      currentApiaryApproval: function() {
          let currentApproval = null;
          if (this.behalf_of === "individual" && this.profile.current_apiary_approval) {
              currentApproval = this.profile.current_apiary_approval;
          } else if (this.behalf_of > 0 && parseInt(this.behalf_of)) {
              for (let organisation of this.profile.disturbance_organisations) {
                  if (this.behalf_of === organisation.id && organisation.current_apiary_approval) {
                      currentApproval = organisation.current_apiary_approval;
                  }
              }
          }
          return currentApproval;
      },
      currentApiaryButtonDisabled: function() {
          let currentDisabled = null;
          if (this.behalf_of === "individual" && this.profile.existing_record_text.disable_radio_button) {
              currentDisabled = this.profile.existing_record_text.disable_radio_button;
          } else if (this.behalf_of > 0 && parseInt(this.behalf_of)) {
              let org = this.profile.disturbance_organisations.find(item => item.id === this.behalf_of)
              currentDisabled = org.existing_record_text.disable_radio_button;
          }
          
          return currentDisabled;
      },

      applicationTypesList: function() {
          let returnList = [];
          for (let applicationType of this.application_types) {
              // for individual applications, only Apiary should show
              //if (this.behalf_of === 'individual') {
              if (this.apiaryTemplateGroup) {
                  if (applicationType.domain_used.toLowerCase() === "apiary") {
                      if (applicationType.text.toLowerCase() === "apiary" && !this.currentApiaryButtonDisabled){
                          applicationType.display_text = "Apiary Sites";
                          returnList.push(applicationType);
                      }
                      // add Site Transfer if selected applicant has an associated current_apiary_approval
                      if (applicationType.text.toLowerCase() === "site transfer" && this.currentApiaryApproval && !this.currentApiaryButtonDisabled){
                          applicationType.display_text = "Transfer Apiary Sites";
                          returnList.push(applicationType);
                      }
                      if (applicationType.text.toLowerCase() === "temporary use" && this.currentApiaryApproval){
                          // always allow New Temp Use Applications
                          applicationType.display_text = "Temporary Use of Apiary Sites";
                          returnList.push(applicationType);
                      }
                  }
              } else if (this.dasTemplateGroup){
                  if (applicationType.domain_used === 'das') {
                      applicationType.display_text = applicationType.text;
                      returnList.push(applicationType);
                  }
              }
          }
          return returnList;
      },
    isLoading: function() {
      return this.loading.length > 0
    },
    org: function() {
        let vm = this;
        let org_value = ''
        //if (vm.behalf_of != '' || vm.behalf_of != 'other' || vm.behalf_of != 'individual'){
        if (vm.behalf_of === '' || vm.behalf_of === 'other' || vm.behalf_of === 'individual'){
            // pass
        } else {
            org_value = vm.profile.disturbance_organisations.find(org => parseInt(org.id) === parseInt(vm.behalf_of)).name;
        }
        return org_value;
    },
    manyDistricts: function() {
      return this.districts.length > 1;
    },
    proposal_type_help_url: function() {
        //return this.site_url + "help/disturbance/user/#apply_proposal_type"
        let vm=this;
        if(vm.global_settings){
            for(var i=0; i<vm.global_settings.length; i++){
                if(vm.global_settings[i].key=='proposal_type_help_url'){
                    return vm.global_settings[i].value;
                    }
                }
            }
        return '';
    },
    region_help_url: function() {
      //return this.site_url + "help/disturbance/user/#apply_region"
      let vm=this;
        if(vm.global_settings){
            for(var i=0; i<vm.global_settings.length; i++){
                if(vm.global_settings[i].key=='region_help_url'){
                    return vm.global_settings[i].value;
                    }
                }
            }
        return '';
    },
    district_help_url: function() {
      //return this.site_url + "help/disturbance/user/#apply_district"
      let vm=this;
        if(vm.global_settings){
            for(var i=0; i<vm.global_settings.length; i++){
                if(vm.global_settings[i].key=='district_help_url'){
                    return vm.global_settings[i].value;
                    }
                }
            }
        return '';
    },
    activity_type_help_url: function() {
      //return this.site_url + "help/disturbance/user/#apply_activity_type"
      let vm=this;
        if(vm.global_settings){
            for(var i=0; i<vm.global_settings.length; i++){
                if(vm.global_settings[i].key=='activity_type_help_url'){
                    return vm.global_settings[i].value;
                    }
                }
            }
        return '';

    },
    sub_activity_1_help_url: function() {
      //return this.site_url + "help/disturbance/user/#apply_sub_activity_1"
      let vm=this;
        if(vm.global_settings){
            for(var i=0; i<vm.global_settings.length; i++){
                if(vm.global_settings[i].key=='sub_activity_1_help_url'){
                    return vm.global_settings[i].value;
                    }
                }
            }
        return '';
    },
    sub_activity_2_help_url: function() {
      //return this.site_url + "help/disturbance/user/#apply_sub_activity_2"
      let vm=this;
        if(vm.global_settings){
            for(var i=0; i<vm.global_settings.length; i++){
                if(vm.global_settings[i].key=='sub_activity_2_help_url'){
                    return vm.global_settings[i].value;
                    }
                }
            }
        return '';
    },
    category_help_url: function() {
      //return this.site_url + "help/disturbance/user/#apply_category"
      let vm=this;
        if(vm.global_settings){
            for(var i=0; i<vm.global_settings.length; i++){
                if(vm.global_settings[i].key=='category_help_url'){
                    return vm.global_settings[i].value;
                    }
                }
            }
        return '';
    }

  },
  methods: {
    submit: function() {
        let vm = this;
        let text = '';
        if (this.behalf_of === 'individual' && this.profile && this.profile.full_name) {
            text = "Are you sure you want to create " + this.alertText() + " proposal on behalf of "+ this.profile.full_name +" ?"
        } else {
            text = "Are you sure you want to create " + this.alertText() + " proposal on behalf of "+vm.org+" ?"
        }

        swal.fire({
            title: "Create " + vm.selected_application_name,
            //text: "Are you sure you want to create " + this.alertText() + " proposal on behalf of "+vm.org+" ?",
            text: text,
            icon: "question",
            showCancelButton: true,
            confirmButtonText: 'Accept'
        }).then((swalresult) => {
            if(swalresult.isConfirmed) {
                vm.createProposal();
            }
        },(error) => {
            console.log(error);
        });
    },
    individualDisableApplyRadioButton: function() {
        return this.profile.current_apiary_approval===null && this.profile.existing_record_text.disable_radio_button;
    },
    orgDisableApplyRadioButton: function(org) {
        //let org = this.profile.disturbance_organisations.find(item => item.id === _org.id)
        return org.current_apiary_approval===null && org.existing_record_text.disable_radio_button;
    },
    individualHasNoLicenceTitle: function() {
      console.log(3);
      if (this.individualDisableApplyRadioButton()) {
          //console.log(this.profile.full_name + ' has no current licence');
          return this.profile.full_name + ' has no current licence'
      }
    },
    orgHasNoLicenceTitle: function(org) {
      console.log(1);
      if (this.orgDisableApplyRadioButton(org)) {
          //console.log(this.name + ' has no current licence');
          return org.name + ' has no current licence'
      }
    },

    alertText: function() {
        let vm = this;
		if (vm.selected_application_name == 'Apiary') {
        	return "an " + vm.selected_application_name.toLowerCase();
		} else {
        	return "a " + vm.selected_application_name.toLowerCase();
		}
	},
    createProposal:function () {
        console.log('createProposal');
        let vm = this;
        vm.creatingProposal = true;
		vm.$http.post('/api/proposal.json',{
			behalf_of: vm.behalf_of,
			application: vm.selected_application_id, 
            
			region: vm.selected_region,
			district: vm.selected_district,
			//tenure: vm.selected_tenure,
			activity: vm.selected_activity,
            sub_activity1: vm.selected_sub_activity1,
            sub_activity2: vm.selected_sub_activity2,
            category: vm.selected_category,
            approval_level: vm.approval_level,
            profile: this.profile.id,
            // Site Transfer
            originating_approval_id: vm.currentApiaryApproval,
            // Temporary Use
            approval_id: vm.currentApiaryApproval,
		}).then(res => {
		    vm.proposal = res.body;
			vm.$router.push({
			    name:"draft_proposal",
				params:{proposal_id:vm.proposal.id}
			});
            vm.creatingProposal = false;
		},
		err => {
			console.log(err);
            console.log(err.bodyText);
            if (err.bodyText.includes("null_applicant_address")) {
                swal.fire({
                    title: "Cannot create application",
                    text: "Please add your address",
                    icon: "error",
                    confirmButtonText: 'Ok'
                }).then((swalresult) => {
                    if(swalresult.isConfirmed) {
                        vm.$router.push({
                            name:"account",
                        });
                    }
                });
            }
		});
    },
    isDisabled: function() {
        let vm = this;

        if (!['Apiary', 'Site Transfer', 'Temporary Use'].includes(vm.selected_application_name)) {
            // if (vm.behalf_of == '' || vm.selected_application_id == '' || vm.selected_region == '' || vm.approval_level == ''){
            //if (vm.behalf_of == '' || vm.selected_application_id == ''  || vm.approval_level == ''){
            if (vm.behalf_of == '' || vm.selected_application_id == '' || vm.selected_region == '' || vm.selected_district == '' || vm.selected_activity=='' ){
                if (vm.selected_sub_activity1==''){
                    return true;
                }
            }
            else if (vm.sub_activities1.length==0){
                // vm.selected_sub_activity1 not required
                return false;
            }
            else if ((vm.sub_activities1.length>0 && vm.selected_sub_activity1=='') || (vm.sub_activities2.length>0 && vm.selected_sub_activity2=='')){
                return true;
            }
        } else {
            if (vm.behalf_of == '' || vm.selected_application_id == ''){
                return true;
            }
        }
        return false;
    },
	fetchRegions: function(){
		let vm = this;

		fetch(api_endpoints.regions).then((response) => {
				vm.api_regions = response.body;
				//console.log('api_regions ' + response.body);

                for (var i = 0; i < vm.api_regions.length; i++) {
                    this.regions.push( {text: vm.api_regions[i].name, value: vm.api_regions[i].id, districts: vm.api_regions[i].districts} );
                }
		},(error) => {
			console.log(error);
		})
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
    fetchApplicationTypes: function(){
		let vm = this;

		fetch(api_endpoints.application_types).then((response) => {
				vm.api_app_types = response.body;
				//console.log('api_app_types ' + response.body);

                for (var i = 0; i < vm.api_app_types.length; i++) {
                    this.application_types.push( {
                        text: vm.api_app_types[i].name,
                        value: vm.api_app_types[i].id,
                        domain_used: vm.api_app_types[i].domain_used,
                        //activities: (vm.api_app_types[i].activity_app_types.length > 0) ? vm.api_app_types[i].activity_app_types : [],
                        //tenures: (vm.api_app_types[i].tenure_app_types.length > 0) ? vm.api_app_types[i].tenure_app_types : [],
                    } );
                }
		},(error) => {
			console.log(error);
		})
	},
    chainedSelectAppType: function(application_id){
        /* reset */
		let vm = this;
        vm.selected_region = '';
        vm.selected_district = '';
        vm.selected_activity = '';
        vm.display_region_selectbox = false;
        vm.display_activity_matrix_selectbox = false;
        vm.activity_matrix=[]

        vm.selected_application_name = this.searchList(application_id, vm.application_types).text
        //this.chainedSelectActivities(application_id);
        //this.chainedSelectActivities(application_id);

        if (['Apiary', 'Site Transfer', 'Temporary Use'].includes(vm.selected_application_name)) {
            vm.display_region_selectbox = false;
            vm.display_activity_matrix_selectbox = false;
        }  else {
            vm.getSelectedAppActivityMatrix(vm.selected_application_name);
            vm.display_region_selectbox = true;
            vm.display_activity_matrix_selectbox = true;
            //vm.getSelectedAppActivityMatrix(vm.selected_application_name);
        }

    },

	fetchActivityMatrix: function(){
		let vm = this;
        vm.sub_activities1 = [];
        vm.sub_activities2 = [];
        vm.categories = [];
        vm.approval_level = '';

		fetch(api_endpoints.activity_matrix).then((response) => {
				this.activity_matrix = response.body[0].schema[0];
				this.keys_ordered = response.body[0].ordered;
				//console.log('this.activity_matrix ' + response.body[0].schema);

                var keys = this.keys_ordered ? Object.keys(this.activity_matrix).sort() : Object.keys(this.activity_matrix)
                for (var i = 0; i < keys.length; i++) {
                    this.activities.push( {text: keys[i], value: keys[i]} );
                }
		},(error) => {
			console.log(error);
		})
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
    fetchAllActivityMatrices: function(){
		let vm = this;
        vm.sub_activities1 = [];
        vm.sub_activities2 = [];
        vm.categories = [];
        vm.approval_level = '';

		fetch(api_endpoints.activity_matrix).then((response) => {
				this.all_activity_matrices = response.body;
		},(error) => {
			console.log(error);
		})
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
                var act_key = Object.keys(api_activities[k])[0];
                this.sub_activities1.push( {text: act_key, value: act_key, sub_matrix: api_activities[k][act_key]} );
            }
        }
	},

    chainedSelectSubActivities2: function(activity_name){
		let vm = this;
        vm.sub_activities2 = [];
        vm.categories = [];
        vm.selected_sub_activity2 = '';
        vm.selected_category = '';
        vm.approval_level = '';

        //var api_activities = this.get_sub_matrix(activity_name, vm.sub_activities1[0]['text'])
        var [api_activities, res] = this.get_sub_matrix(activity_name, vm.sub_activities1)
        if (res == "null" || res == null) {
            vm.approval_level = api_activities;
            return;
        } else if (res == "pass") {
            for (var i = 0; i < api_activities.length; i++) {
                this.categories.push( {text: api_activities[i][0], value: api_activities[i][0], approval: api_activities[i][1]} );
            }
        } else {
            for (var m = 0; m < vm.sub_activities1.length; m++) {
                if (activity_name == vm.sub_activities1[m]['text']) {
                    var api_activities2 = vm.sub_activities1[m]['sub_matrix'];
                    for (var j = 0; j < api_activities2.length; j++) {
                        var key = Object.keys(api_activities2[j])[0];
                        this.sub_activities2.push( {text: key, value: key, sub_matrix: api_activities2[j][key]} );
                    }
                }
            }
        }
	},
    chainedSelectCategories: function(activity_name){
		let vm = this;
        vm.categories = [];
        vm.selected_category = '';
        vm.approval_level = '';

        for (var i = 0; i < vm.sub_activities2.length; i++) {
            if (activity_name == vm.sub_activities2[i]['text']) {
                var api_categories = vm.sub_activities2[i]['sub_matrix'];
                for (var j = 0; j < api_categories.length; j++) {
                    this.categories.push( {text: api_categories[j][0], value: api_categories[j][0], approval: api_categories[j][1]} );
                }
            }
        }
	},

    get_sub_matrix: function(activity_name, sub_activities){
        // this.sub_activities1[0]['text']
        if (activity_name in sub_activities) {
            if (sub_activities[activity_name].length > 0) {
                if ('pass' in sub_activities[activity_name][0]) {
                    return [sub_activities[activity_name], "pass"];

                } else if ('null' in sub_activities[activity_name][0]) {
                    var approval_level;
                    if (sub_activities[activity_name]['sub_matrix'] == null) {
                        approval_level = sub_activities[activity_name][0]['null'][0][0];
                    } else {
                        approval_level = sub_activities[activity_name]['sub_matrix'][0]['null'][0];
                    }
                    return [approval_level, "null"];
                    //return [sub_activities[activity_name], "null"];
                }
            }

            // not a sub_matrix --> this is the main activity_matrix data (as provided by the REST API)
            return [sub_activities[activity_name], true];
        }
        for (var i = 0; i < sub_activities.length; i++) {
            if (activity_name == sub_activities[i]['text']) {
                var key_sub_matrix = Object.keys(sub_activities[i]['sub_matrix'][0])[0];
                if (key_sub_matrix == "null") {
                    var sub_approval_level = sub_activities[i]['sub_matrix'][0]['null'][0];
                    return [sub_approval_level, null]
                } else if (key_sub_matrix == "pass") {
                    return [sub_activities[i]['sub_matrix'][0]['pass'], "pass"]
                } else {
                    return [sub_activities[i]['sub_matrix'][0], true];
                }
            }
        }
    },
    fetchGlobalSettings: function(){
                let vm = this;
                fetch('/api/global_settings.json').then((response) => {
                    vm.global_settings = response.body;
                    
                },(error) => {
                    console.log(error);
                } );
    },
    get_approval_level: function(category_name) {
        let vm = this;
        for (var i = 0; i < vm.categories.length; i++) {
            if (category_name == vm.categories[i]['text']) {
                vm.approval_level = vm.categories[i]['approval'];
            }
        }

    }

  },
  mounted: function() {
    let vm = this;
    vm.fetchRegions();
    vm.fetchApplicationTypes();
    //vm.fetchActivityMatrix();
    vm.fetchAllActivityMatrices();
    vm.fetchGlobalSettings();
    vm.form = document.forms.new_proposal;
  },
  beforeRouteEnter: function(to, from, next) {

    let initialisers = [
        utils.fetchProfile(),

        //utils.fetchProposal(to.params.proposal_id)
    ]
    next(vm => {
        vm.loading.push('fetching profile')
        Promise.all(initialisers).then(data => {
            vm.profile = data[0];
            //vm.proposal = data[1];
            vm.loading.splice('fetching profile', 1)
        })
    })

  },
    created: function() {
        // retrieve template group
        fetch('/template_group',{
            emulateJSON:true
            }).then(res=>{
                //this.template_group = res.body.template_group;
                if (res.body.template_group === 'apiary') {
                    this.apiaryTemplateGroup = true;
                } else {
                    this.dasTemplateGroup = true;
                }
        },err=>{
        console.log(err);
        });
    },

}
</script>

<style lang="css">
input[type=text], select{
    width:40%;
    box-sizing:border-box;

    min-height: 34px;
    padding: 0;
    height: auto;
}

.group-box {
	border-style: solid;
	border-width: thin;
	border-color: #FFFFFF;
}
.proposalWarning {
    color: red;
}
</style>
