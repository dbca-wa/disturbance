<template>
<div class="container" id="internalSearch">
    <div class="row">
        <div class="col-sm-12">
          <FormSection :form-collapse="false" label="Search Organisations" Index="search_organisation">
            <div class="row">
              <form name="searchOrganisationForm">
                  <div class="form-group">
                      <label class="col-form-label" for="Organisation">Search Organisation</label>
                      <div class="row">
                        <div class="col-md-8">
                          <select v-if="organisations == null" class="form-select" name="organisation">
                              <option value="">Loading...</option>
                          </select>
                          <select v-else ref="searchOrg" class="form-select" name="organisation">
                              <option value="">Select Organisation</option>
                              <option v-for="o in organisations" :value="o.id" :key="o.id">{{ o.name }}</option>
                          </select>
                        </div>
                        <div class="col-md-4">
                          <router-link v-if="selected_organisation !== ''" :to="{name:'internal-org-detail',params:{'org_id':parseInt(selected_organisation)}}" class="btn btn-primary">View Details</router-link>
                          <span v-else class="btn btn-primary disabled" style="pointer-events: none; opacity: 0.6;">View Details</span>
                        </div>
                      </div>
                  </div>
              </form>
            </div>
          </FormSection>
        </div>
    </div>

    <!--TODO There is no user details dashboard and no working search functionality below - commenting this block out until both are available -->
    <!--<div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Search User
                        <a :href="'#'+uBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="uBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="uBody">
                    <div class="row">
                        <form name="searchUserForm">
                          <div class="">
                            <div class="col-md-4">
                                <div class="form-group">
                                    <label class="control-label" for="User">Search User</label>

                                    <TextFilteredField :url="filtered_url" name="User" id="id_holder"/>
                                </div>
                            </div>
                            <div class="">
                              <div class="col-md-12 text-center">
                                <div >
                                  <input type="button" @click.prevent="viewUserDetails" class="btn btn-primary" style="margin-bottom: 5px" value="View Details"/>
                                </div>
                              </div>
                            </div>
                          </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>-->

    <div class="row">
        <div class="col-sm-12">
          <FormSection :form-collapse="false" label="Search Keywords" Index="search_keywords">
            <div class="row">
              <div class="col-lg-12">
                  <div class="form-group">
                    <label for="" class="col-form-label col-lg-12">Filter</label>
                    <div class="form-check form-check-inline col-md-3">
                        <input  class="form-check-input" ref="searchProposal" id="searchProposal" name="searchProposal" type="checkbox" v-model="searchProposal" /> 
                        <label class="form-check-label" for="searchProposal">Proposal</label>
                        
                    </div> 
                    <div class="form-check form-check-inline col-md-3">
                        <input  class="form-check-input" ref="searchApproval" id="searchApproval" name="searchApproval" type="checkbox" v-model="searchApproval" /> 
                        <label class="form-check-label" for="searchApproval">Approval</label>
                    </div> 
                    <div class="form-check form-check-inline col-md-3">
                        <input  class="form-check-input" ref="searchCompliance" id="searchCompliance" name="searchCompliance" type="checkbox" v-model="searchCompliance" /> 
                        <label class="form-check-label" for="searchCompliance">Compliance with requirements</label>
                    </div> 
                    <label for="" class="col-form-label col-lg-12">Keyword</label>                              
                    <div class="row">
                      <div class="col-md-8">
                          <input type="search"  class="form-control input-sm" name="details" placeholder="" v-model="keyWord" style="width:100%"/>
                        </div> 
                        <div class="col-md-3">
                          <input type="button" @click.prevent="add" class="btn btn-primary" value="Add"/>
                        </div>     
                      </div>                                                                          
                  </div>
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-lg-12">
                  <ul class="list-inline" style="display: inline; width: auto;">                          
                      <li class="list-inline-item" v-for="(item,i) in searchKeywords" :key="i">
                          <span class="glyphicon glyphicon-search"></span>
                          <span class="sr-only">Search Keyword</span>
                        <button @click.prevent="" class="btn btn-light" style="margin-top:5px; margin-bottom: 5px">{{item}}</button><a href="" @click.prevent="removeKeyword(i)"><span class="bi bi-x "></span></a>
                      </li>
                  </ul>
              </div>
            </div>

            <div class="row mb-2">
              <div class="col-lg-12">
                  <button  v-if="searching" type="button" class="btn btn-primary btn-margin" style="margin-bottom: 5px" value="Search" disabled>
                    Search<i class="fa fa-circle-o-notch fa-spin fa-fw"></i></button>
                  <input v-else type="button" @click.prevent="search" class="btn btn-primary btn-margin" style="margin-bottom: 5px" value="Search"/>
                  <input type="reset" @click.prevent="reset" class="btn btn-primary" style="margin-bottom: 5px" value="Clear"/>
              </div> 
            </div>
            <div id="loadingSpinner" style="display: none; text-align: center; padding: 20px;">
              <!-- You can replace this with your preferred loading spinner or element -->
              <i class='fa fa-4x fa-spinner fa-spin'></i>
              <p>Loading...</p>
            </div>
            <div class="row">
              <div class="col-lg-12">
                <datatable ref="proposal_datatable" :id="datatable_id" :dtOptions="proposal_options"  :dtHeaders="proposal_headers"/>
              </div>
            </div>
          </FormSection>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-12">
          <FormSection :form-collapse="false" label="Search Reference Number" Index="search_reference_number">
            <div class="row mb-1">
                <label for="" class="col-form-label col-lg-12">Keyword</label>   
                <div class="row">
                  <div class="col-md-8">
                      <input type="search"  class="form-control input-sm" name="referenceWord" placeholder="" v-model="referenceWord" style="width:100%"/>
                  </div>
                  <div class="col-md-3">
                    <input type="button" @click.prevent="search_reference" class="btn btn-primary" style="margin-bottom: 5px" value="Search"/>
                  </div>
                </div>
                <div>
                  <alert v-if="showError" type="danger"><strong>{{errorString}}</strong></alert>
                </div>
            </div>
          </FormSection>
        </div>
    </div>
    <div class="row">
      <div class="col-sm-12">
        <searchSection></searchSection>
      </div>
    </div>
</div>
</template>
<script>
import { v4 as uuidv4 } from 'uuid';
import FormSection from '@/components/forms/section_toggle.vue';
import alert from '@vue-utils/alert.vue'
import datatable from '@/utils/vue/datatable.vue'
import {
  api_endpoints,
  helpers,
  constants
}
from '@/utils/hooks'
import utils from './utils'
import searchSection from './search_section_latest.vue'
export default {
  name: 'ExternalDashboard',
  props: {
    
  },
  data() {
    let vm = this;
    return {
      rBody: 'rBody' + uuidv4(),
      oBody: 'oBody' + uuidv4(),
      kBody: 'kBody' + uuidv4(),
      uBody: 'uBody' + uuidv4(),
      loading: [],
      filtered_url: api_endpoints.filtered_users + '?search=',
      searchKeywords: [],
      searchProposal: true,
      searchApproval: false,
      searchCompliance: false,
      referenceWord: '',
      keyWord: null,
      selected_organisation:'',
      organisations: null,
      searching:false,
      results: [],
      errors: false,
      errorString: '',
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
          data: vm.results,
          columns: [
              {data: "number"},
              {data:"type"},
              {data: "applicant"},
              {//data: "text.value"
                data: "text",
                // mRender: function (data,type,full) {
                //   if(data.value){
                //     return data.value;
                //   }
                //   else
                //   {
                //     return data;
                //   }
                // }
                'render': function (value, type) {
                            value= value.value? value.vale : value;
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="javascript://" ' +
                                    'role="button" ' +
                                    'data-bs-toggle="popover" ' +
                                    'data-bs-trigger="hover" ' +
                                    'data-bs-placement="top"' +
                                    'data-bs-html="true" ' +
                                    'data-bs-content="<%= text %>" ' +
                                    '>More</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            //return result;
                            return type=='export' ? value : result;
                        },
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
          drawCallback: function () {
              helpers.enablePopovers();
          },
          initComplete: function() {
              $('#loadingSpinner').hide();
              helpers.enablePopovers();
          },
      }
    }
    
  },
    watch: {
      
    },
    components: {
        datatable,
        searchSection,
        alert,
        FormSection,
    },
    beforeRouteEnter:function(to,from,next){
        utils.fetchOrganisations().then((response)=>{
            next(vm => {
                vm.organisations = response;
            });
        },
        (error) =>{
            console.log(error);
        });
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        }
    },
    methods: {
        addListeners: function(){
            let vm = this;
            // Initialise select2 for region
            $(vm.$refs.searchOrg).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select Organisation"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.selected_organisation = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.selected_organisation = selected.val();
            });
        },

        viewUserDetails: function(){
          let vm=this;
          let form=document.forms.searchUserForm
          var user_selected=form.elements['User-selected']
          if(user_selected!=undefined || user_selected!=null){
            var user_id= user_selected.value;
            vm.$router.push({
              name:"internal-user-detail",
              params:{user_id:user_id}
            });
          }
          else{
            swal.fire({
                    title: 'User not selected',
                    html: 'Please select the user to view the details',
                    icon: 'error'
                }).then(() => {
                    
                });
                return;
          }
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
          vm.$refs.proposal_datatable.vmDataTable.clear()
          vm.$refs.proposal_datatable.vmDataTable.draw(); 
          $('#loadingSpinner').hide();      
        },

        search: function() {
          let vm = this;
          if(this.searchKeywords.length > 0)
          {
            vm.searching=true;
            fetch('/api/search_keywords.json',{
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                searchKeywords: vm.searchKeywords,
                searchProposal: vm.searchProposal,
                searchApproval: vm.searchApproval,
                searchCompliance: vm.searchCompliance,
                is_internal: true,
              })
            }).then(async (res) => {
              if (!res.ok) {
                  throw new Error(`HTTP error! Status: ${res.status}`);
              }
              vm.results = await res.json();
              vm.$refs.proposal_datatable.vmDataTable.clear()
              vm.$refs.proposal_datatable.vmDataTable.rows.add(vm.results);
              vm.$refs.proposal_datatable.vmDataTable.draw();
              vm.searching=false;
            }).catch(err => {
              console.log(err);
              vm.searching=false;
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
                  throw new Error(`HTTP error! Status: ${res.status}`);
              }
              const responseBody = await res.json();
              console.log(responseBody);
              vm.errors = false;
              vm.errorString = '';
              vm.$router.push({ path: '/internal/'+responseBody.type+'/'+responseBody.id });
            }).catch(error => {
              console.log(error);
              vm.errors = true;
              // vm.errorString = helpers.apiVueResourceError(error);
              vm.errorString = error;
            });
          }

        },
    },
    mounted: function () {
        let vm = this;
        vm.proposal_options.data = vm.results;
        vm.$refs.proposal_datatable.vmDataTable.draw();
        $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
        } );
        this.$nextTick(() => {
            vm.addListeners();
        });
    },
}
</script>
