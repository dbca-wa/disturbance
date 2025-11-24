<template>
    <div class="container" id="userInfo">
        <div v-if="showCompletion" class="row">
            <div class="col-sm-12">
                <div class="round-box px-3 mt-4">
                    <div class="row">
                        <div class="col-sm-12">
                            <p>
                                We have detected that this is the first time you have logged into the system.Please take a moment to provide us with your details
                                (personal details, address details, contact details, and weather you are managing approvals for an organisation).
                                Once completed, click Continue to start using the system.
                            </p>
                            <a :disabled="!completedProfile" href="/" class="btn btn-primary pull-right">Continue</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-12">
                <FormSection :form-collapse="false" label="Personal Details" Index="personal_details" subtitle="Provide your personal details">
                    <form class="form-horizontal" name="personal_form" method="post">
                        <alert v-if="showPersonalError" type="danger" style="color:red">
                            <div v-for="item in errorListPersonal" v-bind:key="item">
                                <strong>{{item}}</strong>
                            </div>
                        </alert>
                        <div class="form-group">
                            <div class="row mb-3">
                                <div class="col-sm-3"></div>
                                <div class="col-sm-6">
                                    <p>
                                        <b>To update your account name or MFA(Multi-Factor Authentication) please click <a href="/sso/setting">here:</a></b><br>
                                        Changes will not update until your next login.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div class="form-group">
                            <div class="row mb-3">
                                <label for="" class="col-sm-3 col-form-label">Given name(s)</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" id="first_name" name="Given name" v-model="profile.first_name" disabled>
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <div class="row mb-3">
                                <label for="" class="col-sm-3 control-label" >Surname</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" id="surname" name="Surname" v-model="profile.last_name" disabled>
                                </div>
                            </div>
                        </div>
                        <!--
                        <div class="form-group">
                        <div class="col-sm-12">
                            <button v-if="!updatingPersonal" class="pull-right btn btn-primary" @click.prevent="updatePersonal()">Update</button>
                            <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                        </div>
                        </div>
                        -->
                    </form>
                </FormSection>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-12">
                <FormSection :form-collapse="true" label="Address Details" Index="address_details" subtitle="Provide your address details">
                    <form class="form-horizontal" action="index.html" method="post">
                        <alert v-if="showAddressError" type="danger" style="color:red">
                            <div v-for="item in errorListAddress" v-bind:key="item">
                                <strong>{{item}}</strong>
                            </div>
                        </alert>
                          <div class="form-group">
                            <div class="row mb-3">
                                <label for="" class="col-sm-3 col-form-label">Street</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" id="line1" name="Street" placeholder="" v-model="profile.residential_address.line1">
                                </div>
                            </div>
                          </div>
                          <div class="form-group">
                            <div class="row mb-3">
                                <label for="" class="col-sm-3 col-form-label" >Town/Suburb</label>
                                <div class="col-sm-6">
                                    <input type="text" class="form-control" id="locality" name="Town/Suburb" placeholder="" v-model="profile.residential_address.locality">
                                </div>
                            </div>
                          </div>
                          <div class="form-group">
                            <div class="row mb-3">
                                <label for="" class="col-sm-3 col-form-label">State</label>
                                <div class="col-sm-3">
                                    <input type="text" class="form-control " id="state" name="State" placeholder="" v-model="profile.residential_address.state">
                                </div>
                                <label for="" class="col-sm-1 col-form-label">Postcode</label>
                                <div class="col-sm-2">
                                    <input type="text" class="form-control" id="postcode" name="Postcode" placeholder="" v-model="profile.residential_address.postcode">
                                </div>
                            </div>
                          </div>
                          <div class="form-group">
                            <div class="row mb-3">
                                <label for="" class="col-sm-3 col-form-label" >Country</label>
                                <div class="col-sm-4">
                                    <select class="form-select" id="country" name="Country" v-model="profile.residential_address.country">
                                        <option v-for="c in countries" :key="c.code" :value="c.code">{{ c.name }}</option>
                                    </select>
                                </div>
                            </div>
                          </div>
                          <div class="form-group">
                            <div class="col-sm-12">
                                <button v-if="!updatingAddress" class="pull-right btn btn-primary" @click.prevent="updateAddress()">Update</button>
                                <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                            </div>
                          </div>
                       </form>
                </FormSection> 
            </div>
        </div>
        <div class="row">
            <div class="col-sm-12">
                <FormSection :form-collapse="true" label="Contact Details" Index="contact_details" subtitle="Provide your contact details">
                    <form class="form-horizontal" action="index.html" method="post">
                        <alert v-if="showContactError" type="danger" style="color:red">
                            <div v-for="item in errorListContact" v-bind:key="item">
                                <strong>{{item}}</strong>
                            </div>
                        </alert>
                        <div class="form-group">
                            <div class="row mb-3">
                                <label for="" class="col-sm-3 col-form-label">Phone (work)</label>
                                <div v-if="profile.is_department_user" class="col-sm-6">
                                    <input :readonly="phoneNumberReadonly" type="text" class="form-control" id="phone" name="Phone" placeholder="" v-model="profile.phone_number">
                                </div>
                                <div v-else class="col-sm-6">
                                    <input type="text" class="form-control" id="phone" name="Phone" placeholder="" v-model="profile.phone_number">
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <div class="row mb-3">
                                <label for="" class="col-sm-3 col-form-label" >Mobile</label>
                                <div v-if="profile.is_department_user" class="col-sm-6">
                                    <input :readonly="mobileNumberReadonly" type="text" class="form-control" id="mobile" name="Mobile" placeholder="" v-model="profile.mobile_number">
                                </div>
                                <div v-else class="col-sm-6">
                                    <input type="text" class="form-control" id="mobile" name="Mobile" placeholder="" v-model="profile.mobile_number">
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <div class="row mb-3">
                                <label for="" class="col-sm-3 col-form-label" >Email</label>
                                <div class="col-sm-6">
                                    <input type="email" class="form-control" id="email" name="Email" placeholder="" v-model="profile.email">
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <div class="col-sm-12">
                                <button v-if="!updatingContact" class="pull-right btn btn-primary" @click.prevent="updateContact()">Update</button>
                                <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                            </div>
                        </div>
                    </form>
                </FormSection>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-12">
                <FormSection :form-collapse="true" label="Organisation" Index="organisation_details" :subtitle="organisationSectionTitleText">
                    <form class="form-horizontal" name="orgForm" method="post">
                        <div class="form-group">
                            <div class="row mb-3">
                                <label for="" class="col-sm-5 col-form-label">{{ organisationSectionDetailText }}</label>
                                <div class="col-sm-4">
                                    <label class="radio-inline">
                                        <input type="radio" class="form-check-input" name="behalf_of_org" v-model="managesOrg" value="Yes"> Yes
                                    </label>
                                    <label class="radio-inline">
                                        <input :disabled="hasOrgs" type="radio" class="form-check-input" name="behalf_of_org" v-model="managesOrg" value="No" > No
                                    </label>
                                </div>
                            </div>
                        </div>
                        <div class="form-group" v-if="managesOrg=='Yes'">
                            <div class="row mb-3">
                                <div class="col-sm-12">
                                    <button class="btn btn-primary pull-right" v-if="hasOrgs && !addingCompany" @click.prevent="addCompany()">Add Another Organisation</button>
                                </div>
                            </div>
                        </div>
                        <div v-for="org in profile.disturbance_organisations" :key="org.id">
                            <div class="form-group">
                                <div class="row mb-3">
                                    <label for="" class="col-sm-2 col-form-label" >Organisation</label>
                                    <div class="col-sm-3">
                                        <input type="text" disabled class="form-control" name="organisation" v-model="org.name" placeholder="" style="width: 100%">
                                    </div>
                                    <label for="" class="col-sm-2 col-form-label" >ABN/ACN</label>
                                    <div class="col-sm-3">
                                        <input type="text" disabled class="form-control" name="organisation" v-model="org.abn" placeholder="">
                                    </div>
                                    <a class="col-sm-2" style="cursor:pointer;text-decoration:none;" @click.prevent="unlinkUser(org)"><i class="fa fa-chain-broken fa-2x" ></i>&nbsp;Unlink</a>
                                </div>
                            </div>
                        </div>

                        <div v-for="orgReq in orgRequest_list" :key="orgReq.id">
                            <div class="form-group">
                                <div class="row mb-3">
                                    <label for="" class="col-sm-2 col-form-label" >Organisation</label>
                                    <div class="col-sm-3">
                                        <input type="text" disabled class="form-control" name="organisation" v-model="orgReq.name" placeholder="" style="width: 100%">
                                    </div>
                                    <label for="" class="col-sm-2 col-form-label" >ABN/ACN</label>
                                    <div class="col-sm-3">
                                        <input type="text" disabled class="form-control" name="organisation" v-model="orgReq.abn" placeholder="">
                                    </div>
                                    <label class="col-sm-2">&nbsp;Pending for approval</label>
                                </div>
                            </div>
                        </div>

                        <div style="margin-top:15px;" v-if="addingCompany">
                            <h3> New Organisation</h3>
                            <div class="form-group">
                                <div class="row mb-3">
                                    <label for="" class="col-sm-2 col-form-label" >Organisation</label>
                                    <div class="col-sm-6">
                                        <input type="text" class="form-control" name="organisation" v-model="newOrg.name" placeholder="">
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row mb-3">
                                    <label for="" class="col-sm-2 col-form-label" >ABN/ACN</label>
                                    <div class="col-sm-6">
                                        <input type="text" class="form-control" name="abn" v-model="newOrg.abn" placeholder="" style="width: 40%">
                                    </div>
                                    <div class="col-sm-2">
                                        <button :disabled="!isNewOrgDetails" @click.prevent="checkOrganisation()" class="btn btn-primary">Check Details</button>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group" v-if="newOrg.exists && newOrg.detailsChecked">
                                <div class="row mb-3">
                                    <label class="col-sm-12" style="text-align:left;margin-bottom:20px;">
                                        This organisation has already been  registered with the system.Please enter the two pin codes:<br/>
                                        These pin codes can be retrieved from ({{newOrg.first_five}})
                                    </label>
                                    <label for="" class="col-sm-2 col-form-label" >Pin 1</label>
                                    <div class="col-sm-2">
                                        <input type="text" class="form-control" name="abn" v-model="newOrg.pin1" placeholder="" style="width: 100%">
                                    </div>
                                    <label for="" class="col-sm-2 col-form-label" >Pin 2</label>
                                    <div class="col-sm-2">
                                        <input type="text" class="form-control" name="abn" v-model="newOrg.pin2" placeholder="" style="width: 100%">
                                    </div>
                                    <div class="col-sm-2">
                                        <button v-if="!validatingPins" @click.prevent="validatePins()" class="btn btn-primary pull-left">Validate</button>
                                        <button v-else class="btn btn-primary pull-left"><i class="fa fa-spin fa-spinner"></i>&nbsp;Validating Pins</button>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group" v-else-if="!newOrg.exists && newOrg.detailsChecked">
                                <div class="row mb-3">
                                    <label class="col-sm-12" style="text-align:left;">
                                        This organisation has not yet been registered with this system. Please upload a letter on organisation head stating that you are an employee of this organisation.<br/>
                                    </label>
                                    <div class="col-sm-12">
                                        <span class="btn btn-primary btn-file pull-left">
                                            Attach File <input type="file" ref="uploadedFile" @change="readFile()"/>
                                        </span>
                                        <span class="pull-left" style="margin-left:10px;margin-top:10px;">{{uploadedFileName}}</span>
                                    </div>
                                    <label for="" class="col-sm-10 col-form-label" style="text-align:left;">You will be notified by email once the Department has checked the organisation details.</label>
                                    <div class="col-sm-12">
                                        <button v-if="!completedProfile" disabled title="Please complete details" class="btn btn-primary pull-right">Submit</button>
                                        <button v-else-if="!registeringOrg" :disabled="!isFileUploaded" @click.prevent="orgRequest()" class="btn btn-primary pull-right">Submit</button>
                                        <button v-else disabled class="btn btn-primary pull-right"><i class="fa fa-spin fa-spinner"></i>&nbsp;Submitting</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </FormSection>
            </div>
        </div>
    </div>
</template>

<script>
import { v4 as uuidv4 } from 'uuid';
import $ from 'jquery'
import { api_endpoints, helpers } from '@/utils/hooks'
import FormSection from '@/components/forms/section_toggle.vue';
import alert from '@vue-utils/alert.vue'
export default {
    name: 'UserProfile',
    data () {
        // let vm = this;
        return {
            adBody: 'adBody'+uuidv4(),
            pBody: 'pBody'+uuidv4(),
            cBody: 'cBody'+uuidv4(),
            oBody: 'oBody'+uuidv4(),
            profile: {
                first_name: '',
                last_name: '',
                disturbance_organisations:[],
                residential_address : {}
            },
            newOrg: {
                'detailsChecked': false,
                'exists': false
            },
            countries: [],
            loading: [],
            registeringOrg: false,
            validatingPins: false,
            checkingDetails: false,
            addingCompany: false,
            managesOrg: 'No',
            uploadedFile: null,
            updatingPersonal: false,
            updatingAddress: false,
            updatingContact: false,
            orgRequest_list: [],
            missing_fields: [],
            errorListPersonal:[],
            showPersonalError: false,
            errorListAddress:[],
            showAddressError: false,
            errorListContact:[],
            showContactError: false,
            role: null,
            apiaryTemplateGroup: false,
            dasTemplateGroup: false,
            phoneNumberReadonly: false,
            mobileNumberReadonly: false,
        }
    },
    components: {
        FormSection,
        alert
    },
    watch: {
        // managesOrg: function() {
        //     if (this.managesOrg  == 'Yes' && !this.hasOrgs && this.newOrg){
        //          this.addCompany()
        //     } else if (this.managesOrg == 'No' && this.newOrg){
        //         this.resetNewOrg();
        //         this.uploadedFile = null;
        //         this.addingCompany = false;
        //     }
        // },
        managesOrg: function() {
            if (this.managesOrg == 'Yes'){
              this.newOrg.detailsChecked = false;
              this.role = 'employee'
            } else if (this.managesOrg == 'Consultant'){
              this.newOrg.detailsChecked = false;
              this.role ='consultant'
            }else{this.role = null
              this.newOrg.detailsChecked = false;
            }

            if (this.managesOrg  == 'Yes' && !this.hasOrgs && this.newOrg){
                 this.addCompany()
            } else if (this.managesOrg == 'No' && this.newOrg){
                this.resetNewOrg();
                this.uploadedFile = null;
                this.addingCompany = false;
            } else {
                this.addCompany()
                this.addingCompany=false
            }
        },
    },
    computed: {
        organisationSectionTitleText: function() {
            let titleText = 'Link to the organisations you are an employee of and for which you are managing approvals';
            if (this.apiaryTemplateGroup) {
                titleText = 'Link to the organisations you are an employee of and for which you are managing an apiary authority';
            }
            return titleText;
        },
        organisationSectionDetailText: function() {
            let detailText = 'Are you responsible for preparing proposals on behalf of an organisation?';
            if (this.apiaryTemplateGroup) {
                detailText = 'Do you manage an apiary authority on behalf of an organisation?';
            }
            return detailText;
        },
        hasOrgs: function() {
            return this.profile.disturbance_organisations && this.profile.disturbance_organisations.length > 0 ? true: false;
        },
        uploadedFileName: function() {
            return this.uploadedFile != null ? this.uploadedFile.name: '';
        },
        isFileUploaded: function() {
            return this.uploadedFile != null ? true: false;
        },
        isNewOrgDetails: function() {
            return this.newOrg && this.newOrg.name != '' && this.newOrg.abn != '' ? true: false;
        },
        showCompletion: function() {
            return this.$route.name == 'first-time'
        },
        completedProfile: function(){
            return this.profile.contact_details && this.profile.personal_details && this.profile.address_details;
        }
    },
    methods: {
        readFile: function() {
            let vm = this;
            let _file = null;
            var input = $(vm.$refs.uploadedFile)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]);
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            vm.uploadedFile = _file;
        },
        addCompany: function (){
            this.newOrg.push = {
                'name': '',
                'abn': '',
            };
            this.addingCompany=true;
        },
        resetNewOrg: function(){
            this.newOrg = {
                'detailsChecked': false,
                'exists': false
            };
        },

//        updatePersonal: function() {
//            let vm = this;
//            vm.missing_fields = [];
//            var required_fields=[];
//            vm.errorListPersonal=[];
//            required_fields = $('#first_name, #surname')
//            vm.missing_fields = [];
//            required_fields.each(function() {
//            if (this.value == '') {
//                    //var text = $('#'+id).text()
//                    //console.log(this);
//                    vm.errorListPersonal.push('Value not provided: ' + this.name)
//                    vm.missing_fields.push({id: this.id});
//                }
//            });
//
//            if (vm.missing_fields.length > 0)
//            {
//              vm.showPersonalError = true;
//              //console.log(vm.showPersonalError)
//            }
//            else
//            {
//              vm.showPersonalError = false;
//            vm.updatingPersonal = true;
//            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_personal')),JSON.stringify(vm.profile),{
//                emulateJSON:true
//            }).then((response) => {
//                //console.log(response);
//                vm.updatingPersonal = false;
//                vm.profile = response.body;
//                if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
//            }, (error) => {
//                console.log(error);
//                vm.updatingPersonal = false;
//            });
//          }
//        },

        updateContact: function() {
            let vm = this;
            vm.missing_fields = [];
            var required_fields=[];
            vm.errorListContact=[];
            required_fields = $('#email')
            vm.missing_fields = [];
            required_fields.each(function() {
            if (this.value == '') {
                    //var text = $('#'+id).text()
                    //console.log(this);
                    vm.errorListContact.push('Value not provided: ' + this.name)
                    vm.missing_fields.push({id: this.id});
                }
            });
            // if (vm.profile.mobile_number == '' || vm.profile.phone_number ==''){
            //   vm.errorListContact.push('Value not provided: mobile/ Phone number')
            //   vm.missing_fields.push({id: $('#mobile').id});
            // }
            if ((vm.profile.mobile_number == '' && vm.profile.phone_number =='')|| (vm.profile.mobile_number == null && vm.profile.phone_number ==null)){
              vm.errorListContact.push('Value not provided: mobile/ Phone number')
              vm.missing_fields.push({id: $('#mobile').id});
            }
            if (vm.missing_fields.length > 0)
            {
              vm.showContactError = true;
            }
            else{
                vm.showContactError = false;
                vm.updatingContact = true;
                fetch(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_contact')),{
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(vm.profile)
                }).then(async (response) => {
                    const res = await response.json();
                    if (!response.ok) {
                        throw new Error(`Profile Update Contact Failed: ${response.status}`);
                    }
                    console.log(res);
                    vm.updatingContact = false;
                    vm.profile = res;
                    if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                }).catch((error) => {
                    console.log(error);
                    vm.updatingContact = false;
                });
            }
        },
        updateAddress: function() {
            let vm = this;

            vm.missing_fields = [];
            var required_fields=[];
            vm.errorListAddress=[];
            required_fields = $('#postcode, #line1, #locality, #country, #state')
            vm.missing_fields = [];
            required_fields.each(function() {
            if (this.value == '') {
                    //var text = $('#'+id).text()
                    vm.errorListAddress.push('Value not provided: ' + this.name)
                    vm.missing_fields.push({id: this.id});
                }
            });

            if (vm.missing_fields.length > 0)
            {
              vm.showAddressError = true;
            }
            else{
              vm.showAddressError = false;


            vm.updatingAddress = true;
            fetch(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_address')),{
                method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(vm.profile.residential_address)
            }).then(async (response) => {
                const res = await response.json();
                if (!response.ok) {
                    throw new Error(`Profile Update Address Failed: ${response.status}`);
                }
                vm.updatingAddress = false;
                vm.profile = res;
                if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
            }).catch((error) => {
                console.log(error);
                vm.updatingAddress = false;
            });
          }
        },
        checkOrganisation: function() {
            let vm = this;
            //this.newOrg.abn = this.newOrg.abn.replace(/\s+/g,'');
            if (vm.checkOrgAlreadyLinked()) {
                swal.fire({
                    title: 'Check Organisation',
                    text: 'Organisation ABN "' + vm.newOrg.abn + '" is already linked.',
                    icon: 'success',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                    },
                })
                return;
            } else if (vm.checkOrgRequestList()) {
                swal.fire({
                    title: 'Check Organisation',
                    text: 'Organisation ABN "' + vm.newOrg.abn + '" is already registered and is Pending Approval.',
                    icon: 'success',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                    },
                })
                return;
            }


            fetch(helpers.add_endpoint_json(api_endpoints.organisations,'existance'),{
                method: 'POST',
                body: JSON.stringify(this.newOrg)
            }).then(async (response) => {
                //console.log(response);
                if (!response.ok) { return response.json().then(err => { throw err }); }
                const data = await response.json();
                this.newOrg.exists = data.exists;
                this.newOrg.detailsChecked = true;
                this.newOrg.id = data.id;
                if (data.first_five){this.newOrg.first_five = data.first_five }
            }).catch((error) => {
                console.log(error);
                swal.fire(
                    {
                        title: 'Check Organisation',
                        text: helpers.formatFetchError(error),
                        icon: 'error',
                        customClass: {
                            confirmButton: 'btn btn-primary',
                        },
                    }
                )
            });
        },

        fetchOrgRequestList: function() { //Fetch all the Organisation requests submitted by user which are pending for approval.
            let vm = this;
            fetch(helpers.add_endpoint_json(api_endpoints.organisation_requests,'get_pending_requests'))
            .then(async (response) => {
                if (!response.ok) { return response.json().then(err => { throw err }); }
                vm.orgRequest_list=await response.json();
            }).catch((error) => {
                console.log(error);
            });
        },

        checkOrgRequestList: function() { // Checks if NewOrg requested by user is already Pending Approval
            return this.orgRequest_list.map(a=>a.abn).includes(String(this.newOrg.abn));
        },

        checkOrgAlreadyLinked: function() { // Checks if NewOrg requested by user is already registered and linked 
            return this.profile.disturbance_organisations.map(a=>a.abn).includes(String(this.newOrg.abn));
        },

        validatePins: function() {
            let vm = this;
            vm.validatingPins = true;
            fetch(helpers.add_endpoint_json(api_endpoints.organisations,(vm.newOrg.id+'/validate_pins')),{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.newOrg)
            }).then(async (response) => {
                if (!response.ok) {
                    throw new Error(`Validating pins failed: ${response.status}`);
                }
                const data = await response.json();
                if (data.valid){
                    swal.fire({
                        title: 'Validate Pins',
                        text: 'The pins you entered have been validated and your request will be processed by Organisation Administrator.',
                        icon: 'success',
                        customClass: {
                            confirmButton: 'btn btn-primary',
                        },
                    })
                    vm.registeringOrg = false;
                    vm.uploadedFile = null;
                    vm.addingCompany = false;
                    vm.resetNewOrg();
                    fetch(api_endpoints.profile)
                    .then(async (response) => {
                        if (!response.ok) { return response.json().then(err => { throw err }); }
                        vm.profile = await response.json();
                        if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                        if ( vm.profile.disturbance_organisations && vm.profile.disturbance_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
                    }).catch((error) => {
                        console.log(error);
                    })
                }else {
                    swal.fire({
                        title: 'Validate Pins',
                        text: 'The pins you entered were incorrect',
                        icon: 'error',
                        customClass: {
                            confirmButton: 'btn btn-primary',
                        },
                    })
                }
                vm.validatingPins = false;
            }).catch((error) => {
                vm.validatingPins = false;
                console.log(error.message);
            });
        },
        orgRequest: function() {
            let vm = this;
            vm.registeringOrg = true;
            let data = new FormData();
            data.append('name', vm.newOrg.name);
            data.append('abn', vm.newOrg.abn);
            data.append('identification', vm.uploadedFile);
            data.append('role',vm.role);
            if (vm.newOrg.name == '' || vm.newOrg.abn == '' || vm.uploadedFile == null){
                vm.registeringOrg = false;
                swal.fire({
                    title: 'Error submitting organisation request',
                    text: 'Please enter the organisation details and attach a file before submitting your request.',
                    icon: 'error',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                    },
                })
            } else {
                fetch(api_endpoints.organisation_requests,{
                    method: 'POST',
                    body: data
                }).then(async (response) => {
                    // const res = await response.json();
                    if (!response.ok) { return response.json().then(err => { throw err }); }

                    vm.registeringOrg = false;
                    vm.uploadedFile = null;
                    vm.addingCompany = false;
                    vm.resetNewOrg();
                    swal.fire({
                        title: 'Sent',
                        html: 'Your organisation request has been successfully submitted.',
                        icon: 'success',
                        customClass: {
                            confirmButton: 'btn btn-primary',
                        },
                    }).then((swalresult) => {
                        if(swalresult.isConfirmed) {
                            window.location.reload(true);
                        }
                    });
                }).catch((error) => {
                    console.log(error);
                    vm.registeringOrg = false;
                    swal.fire({
                        title: 'Error submitting organisation request',
                        text: helpers.formatFetchError(error),
                        icon: 'error',
                        customClass: {
                            confirmButton: 'btn btn-primary',
                        },
                    });
                });
            }

        },
        orgConsultRequest: function() {
            let vm = this;
            vm.registeringOrg = true;
            let data = new FormData();
            let new_organisation = vm.newOrg;
            for (var organisation in vm.profile.disturbance_organisations) {
                if (new_organisation.abn && vm.profile.disturbance_organisations[organisation].abn == new_organisation.abn) {
                    swal.fire({
                        title: 'Checking Organisation',
                        html: 'You are already associated with this organisation.',
                        icon: 'info',
                        customClass: {
                            confirmButton: 'btn btn-primary',
                        },
                    })
                    vm.registeringOrg = false;
                    vm.uploadedFile = null;
                    vm.addingCompany = false;
                    vm.resetNewOrg();
                    return;
                }
            }
            data.append('name', vm.newOrg.name);
            data.append('abn', vm.newOrg.abn);
            data.append('identification', vm.uploadedFile);
            data.append('role',vm.role);
            if (vm.newOrg.name == '' || vm.newOrg.abn == '' || vm.uploadedFile == null){
                vm.registeringOrg = false;
                swal.fire({
                    title: 'Error submitting organisation request',
                    text: 'Please enter the organisation details and attach a file before submitting your request.',
                    icon: 'error',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                    },
                })
            } else {
                fetch(api_endpoints.organisation_requests,{
                    method: 'POST',
                    body: data
                }).then(async (response) => {
                    const res = await response.json();
                    if (!res.ok) {
                        throw new Error(`Submit Organisation request failed: ${res.status}`);
                    }
                    vm.registeringOrg = false;
                    vm.uploadedFile = null;
                    vm.addingCompany = false;
                    vm.resetNewOrg();
                    swal.fire({
                        title: 'Sent',
                        html: 'Your organisation request has been successfully submitted.',
                        icon: 'success',
                        customClass: {
                            confirmButton: 'btn btn-primary',
                        },
                    }).then((swalresult) => {
                        if(swalresult.isConfirmed) {
                            if (this.$route.name == 'account'){
                                window.location.reload(true);
                            }
                        }
                    });
                }).catch((error) => {
                    console.log(error.message);
                    vm.registeringOrg = false;
                    let error_msg = '<br/>';
                    for (var key in error.body) {
                        error_msg += key + ': ' + error.body[key] + '<br/>';
                    }
                    swal.fire({
                        title: 'Error submitting organisation request',
                        html: error_msg,
                        icon: 'error',
                        customClass: {
                            confirmButton: 'btn btn-primary',
                        },
                    });
                });
            }
        },
        toggleSection: function (e) {
            let el = e.target;
            let chev = null;
            //console.log(el);
            $(el).on('click', function () {
                chev = $(this);
                //console.log(chev);
                $(chev).toggleClass('glyphicon-chevron-down glyphicon-chevron-up');
            })
        },
        fetchCountries:function (){
            let vm =this;
            vm.loading.push('fetching countries');
            fetch(api_endpoints.countries)
            .then(async (response)=>{
                if (!response.ok) { return response.json().then(err => { throw err }); }
                vm.countries = await response.json();
                vm.loading.splice('fetching countries',1);
            }).catch((error)=>{
                console.log(error);
                vm.loading.splice('fetching countries',1);
            });
        },
        unlinkUser: function(org){
            let vm = this;
            let org_name = org.name;
            swal.fire({
                title: "Unlink From Organisation",
                text: "Are you sure you want to be unlinked from "+org.name+" ?",
                icon: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept',
                customClass: {
                    confirmButton: 'btn btn-primary',
                    cancelButton: 'btn btn-secondary',
                },
            }).then((swalresult) => {
                if(swalresult.isConfirmed) {
                    console.log(vm.profile.first_name);
                    fetch(helpers.add_endpoint_json(api_endpoints.organisations,org.id+'/unlink_user'),{
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({'user':vm.profile.id,
                        'first_name':vm.profile.first_name,'last_name':vm.profile.last_name,'email':vm.profile.email,
                        'mobile_number':vm.profile.mobile_number, 'phone_number':vm.profile.phone_number})
                    }).then(async (response) => {
                        if (!response.ok) {
                            // Check for specific status code
                                if (response.status === 500) {
                                    swal.fire({
                                        title:'Unlink',
                                        text:'Last Organisation Admin cannot be unlinked.',
                                        icon:'error',
                                        customClass: {
                                            confirmButton: 'btn btn-primary',
                                        },
                                    });
                                    return;
                                } else {
                                    console.log(JSON.stringify(await response.json()));
                                    throw new Error(`Unlink user failed: ${response.status}`);
                                }

                        }
                        fetch(api_endpoints.profile)
                        .then(async (response) => {
                            if (!response.ok) { return response.json().then(err => { throw err }); }
                            vm.profile = await response.json();
                            if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                            if ( vm.profile.disturbance_organisations && vm.profile.disturbance_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
                        }).catch((error) => {
                            console.log(error);
                        })
                        swal.fire({
                            title: 'Unlink',
                            text: 'You have been successfully unlinked from '+org_name+'.',
                            icon: 'success',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        })
                    }).catch((error) => {
                        swal.fire({
                            title: 'Unlink',
                            text: 'There was an error unlinking you from '+org_name+'. '+(error?.message || JSON.stringify(error)),
                            icon: 'error',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        })
                    });
                }
            },(error) => {
                console.log(error);
            });
        },
        fetchProfile: function(){
          let vm=this;
          fetch(api_endpoints.profile)
          .then(async (response) => {
            if (!response.ok) { return response.json().then(err => { throw err }); }
            vm.profile = await response.json();
            if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
            if ( vm.profile.disturbance_organisations && vm.profile.disturbance_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
            vm.phoneNumberReadonly = vm.profile.phone_number === '' || vm.profile.phone_number === null || vm.profile.phone_number === 0 ?  false : true;
            vm.mobileNumberReadonly = vm.profile.mobile_number === '' || vm.profile.mobile_number === null || vm.profile.mobile_number === 0 ?  false : true;
        }).catch((error) => {
            console.log(error);
        })

        },
    },
    beforeRouteEnter: function(to,from,next){
        fetch(api_endpoints.profile)
        .then(async (response) => {
            if (!response.ok) { return response.json().then(err => { throw err }); }
            const data = await response.json();
            if (data.address_details && data.personal_details && data.contact_details && to.name == 'first-time'){
                window.location.href='/';
            }
            else{
                next(vm => {
                    vm.profile = data;
                    if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
                    if ( vm.profile.disturbance_organisations && vm.profile.disturbance_organisations.length > 0 ) { vm.managesOrg = 'Yes' }
                });
            }
        }).catch((error) => {
            console.log(error);
        })
    },
    mounted: function(){
        this.fetchCountries();
        this.fetchOrgRequestList();
        this.fetchProfile(); //beforeRouteEnter doesn't work when loading this component in Application.vue so adding an extra method to get profile details.
        this.personal_form = document.forms.personal_form;
        $('.panelClicker[data-toggle="collapse"]').on('click', function () {
            var chev = $(this).children()[0];
            window.setTimeout(function () {
                $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
            },100);
        });
    },
    created: function() {
        // retrieve template group
        fetch('/template_group',{ emulateJSON:true })
        .then(async (res)=>{
            if (!res.ok) { return res.json().then(err => { throw err }); }
            //this.template_group = res.body.template_group;
            const data = await res.json();
            if (data.template_group === 'apiary') {
                this.apiaryTemplateGroup = true;
            } else {
                this.dasTemplateGroup = true;
            }
        }).catch(err=>{
            console.log(err);
        });
    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.btn-file {
    position: relative;
    overflow: hidden;
}
.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
</style>
