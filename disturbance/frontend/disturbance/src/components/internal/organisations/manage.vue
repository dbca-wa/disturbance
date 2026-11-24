<template>
    <div class="container" id="internalOrgInfo">
    <div class="row">
        <h3>{{ org.name }} - {{org.abn}}</h3>
        <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
        </div>
        <!-- <div class="col-md-1">
        </div> -->
        <div class="col-md-9">
            <ul class="nav nav-pills" role="tablist">
                <li class="nav-item">
                    <a
                        id="pills-details-tab"
                        class="nav-link active"
                        data-bs-toggle="pill"
                        :href="'#' + dTab"
                        role="tab"
                        :aria-controls="dTab"
                        aria-selected="true"
                        >Details</a
                    >
                </li>
                <li class="nav-item">
                    <a
                        id="pills-other-tab"
                        class="nav-link"
                        data-bs-toggle="pill"
                        :href="'#' + oTab"
                        role="tab"
                        :aria-controls="oTab"
                        aria-selected="false"
                        >Other</a
                    >
                </li>
            </ul>
            <div class="tab-content">
                <div :id="dTab" class="tab-pane fade active show" role="tabpanel" aria-labelledby="pills-details-tab">
                    <div class="row">
                        <div class="col-sm-12">
                            <FormSection :formCollapse="false" label="Organisation Details" Index="organisation_details">
                                <form class="form-horizontal" name="personal_form" method="post">
                                    <div class="row mb-3">
                                        <label for="" class="col-sm-3 col-form-label">Name</label>
                                        <div class="col-sm-6">
                                            <input type="text" class="form-control" name="first_name" placeholder="" v-model="org.name">
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label for="" class="col-sm-3 col-form-label" >ABN</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="last_name" placeholder="" v-model="org.abn">
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label for="" class="col-sm-3 col-form-label" >Email</label>
                                        <div class="col-sm-6">
                                            <input type="text" class="form-control" name="last_name" placeholder="" v-model="org.email">
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-sm-12">
                                            <button v-if="!updatingDetails" class="pull-right btn btn-primary" @click.prevent="updateDetails()">Update</button>
                                            <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                        </div>
                                    </div>
                                </form>
                            </FormSection>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-sm-12">
                            <FormSection :formCollapse="true" label="Organisation Address Details" Index="address_details">
                                <form class="form-horizontal" action="index.html" method="post">
                                    <div class="row mb-3">
                                        <label for="" class="col-sm-3 col-form-label">Street</label>
                                        <div class="col-sm-6">
                                            <input type="text" class="form-control" name="street" placeholder="" v-model="org.address.line1">
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label for="" class="col-sm-3 col-form-label" >Town/Suburb</label>
                                        <div class="col-sm-6">
                                            <input type="text" class="form-control" name="surburb" placeholder="" v-model="org.address.locality">
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label for="" class="col-sm-3 col-form-label">State</label>
                                        <div class="col-sm-2">
                                            <input type="text" class="form-control" name="country" placeholder="" v-model="org.address.state">
                                        </div>
                                        <label for="" class="col-sm-2 col-form-label">Postcode</label>
                                        <div class="col-sm-2">
                                            <input type="text" class="form-control" name="postcode" placeholder="" v-model="org.address.postcode">
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label for="" class="col-sm-3 col-form-label" >Country</label>
                                        <div class="col-sm-4">
                                            <select class="form-select" name="country" v-model="org.address.country">
                                                <option v-for="c in countries" :value="c.code" :key="c.code">{{ c.name }}</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="row mb-3">
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
                            <FormSection :formCollapse="true" label="Organisation Contact Details" Index="contact_details">
                                <form class="form-horizontal" action="index.html" method="post">
                                    <div class="col-sm-12">
                                        <button @click.prevent="addContact()" style="margin-bottom:10px;" class="btn btn-primary pull-right">Add Contact</button>
                                    </div>
                                    <div class="col-sm-12 row top-buffer-s">
                                        <datatable ref="contacts_datatable" :id="datatable_id" :dtOptions="contacts_options" :dtHeaders="contacts_headers"/>
                                    </div>
                                </form>
                            </FormSection>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-sm-12">
                            <FormSection :formCollapse="true" label="Linked Persons" Index="linked_persons" subtitle="-Manage the user accounts linked to the organisation">
                                <div class="col-sm-8">
                                        <div class="col-sm-12">
                                            <h5>Persons linked to this organisation:</h5>
                                        </div>
                                        <div v-for="d in org.delegates" :key="d.id">
                                            <div v-if="d.is_admin" class="col-sm-6">
                                                <h5>{{d.name}} (Admin)</h5>
                                            </div>
                                            <div v-else class="col-sm-6">
                                                <h5>{{d.name}}</h5>
                                            </div>
                                        </div>
                                        <div>
                                            <h6>Persons linked to the organisation are controlled by the organisation. The Department cannot manage this list of people.</h6>
                                        </div>
                                </div>
                                <!-- <div class="col-sm-4" v-if="org.pins">
                                    <form class="form-horizontal" action="index.html" method="post">
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Pin 1</label>
                                        <div class="col-sm-6">
                                            <label class="control-label">{{org.pins.one}}</label>
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Pin 2</label>
                                        <div class="col-sm-6">
                                            <label class="control-label">{{org.pins.two}}</label>
                                        </div>
                                        </div>
                                    </form>
                                </div> -->
                                <form class="form-horizontal" action="index.html" method="post" v-if="org.pins">
                                    <div class="row">
                                        <div class="col-sm-6">
                                            <div class="row mb-3">
                                                <label for="" class="col-sm-6 col-form-label"> Organisation User Pin Code 1:</label>
                                                <div class="col-sm-6">
                                                    <label class="control-label">{{org.pins.three}}</label>
                                                </div>
                                            </div>
                                            <div class="row mb-3">
                                                <label for="" class="col-sm-6 col-form-label" >Organisation User Pin Code 2:</label>
                                                <div class="col-sm-6">
                                                    <label class="control-label">{{org.pins.four}}</label>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-sm-6">
                                            <div class="row mb-3">
                                                <label for="" class="col-sm-6 col-form-label"> Organisation Administrator Pin Code 1:</label>
                                                <div class="col-sm-6">
                                                    <label class="control-label">{{org.pins.one}}</label>
                                                </div>
                                            </div>
                                            <div class="row mb-3" >
                                                <label for="" class="col-sm-6 col-form-label" >Organisation Administrator Pin Code 2:</label>
                                                <div class="col-sm-6">
                                                    <label class="control-label">{{org.pins.two}}</label>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                                <div class="row mb-3">
                                    <div class="col-sm-12">
                                        <datatable ref="contacts_datatable_user" id="organisation_contacts_datatable_ref" :dtOptions="contacts_options_ref" :dtHeaders="contacts_headers_ref" v-model="filterOrgContactStatus"/>
                                    </div>
                                </div>
                            </FormSection>
                        </div>
                    </div>
                </div> 
                <div :id="oTab" class="tab-pane fade" role="tabpanel" aria-labelledby="pills-other-tab">
                    <FormSection :form-collapse="false" label="Proposals" Index="proposals">
                        <ProposalDashTable ref="proposals_table" level='internal' :url='proposals_url' :organisation_id='Number($route.params.org_id)'/>
                    </FormSection>
                    <FormSection :form-collapse="false" label="Approvals" Index="approvals">
                        <ApprovalDashTable ref="approvals_table" level='internal' :url='approvals_url' :organisation_id='Number($route.params.org_id)'/>
                    </FormSection>
                    <FormSection :form-collapse="false" label="Compliances with requirements" Index="compliances">
                        <ComplianceDashTable ref="compliances_table" level='internal' :url='compliances_url' :organisation_id='Number($route.params.org_id)'/>
                    </FormSection>
                </div>
            </div>
        </div>
    </div>
        <AddContact ref="add_contact" :org_id="org.id" />
        <AddCommLog ref="add_comm_org" :url="comms_add_url" :action="user_action" @refreshActionFromResponse="refreshActionFromResponse" id='org_comms1'/>
    </div>
</template>

<script>
import { v4 as uuidv4 } from 'uuid';
import { api_endpoints, helpers, constants } from '@/utils/hooks'
import datatable from '@vue-utils/datatable.vue'
import AddContact from '@common-utils/add_contact.vue'
import ProposalDashTable from '@common-utils/proposals_dashboard.vue'
import ApprovalDashTable from '@common-utils/approvals_dashboard.vue'
import ComplianceDashTable from '@common-utils/compliances_dashboard.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import FormSection from '@/components/forms/section_toggle.vue';
import utils from '../utils'
import AddCommLog from '@common-utils/add_comm_log_org.vue'
export default {
    name: 'OrganisationComponent',
    data () {
        let vm = this;
        return {
            dTab: 'dTab'+uuidv4(),
            oTab: 'oTab'+uuidv4(),
            datatable_id: 'organisation-contacts-datatable-'+uuidv4(),
            org: {
                address: {}
            },
            loading: [],
            countries: [],
            is_org_access_member: false,
            is_das_admin: false,
            contact_user: {
                first_name: null,
                last_name: null,
                email: null,
                mobile_number: null,
                phone_number: null
            },
            profile:{},
            user_action:'unlink',
            updatingDetails: false,
            updatingAddress: false,
            updatingContact: false,
            empty_list: '/api/empty_list',
            logsTable: null,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            activate_tables: false,
            comms_url: helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/comms_log'),
            logs_url: helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/action_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/add_comms_log'),

            contacts_headers:["Name","Phone","Mobile","Fax","Email","Action"],

            //proposals_url: helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/proposals'),
            //approvals_url: api_endpoints.approvals+'?org_id='+vm.$route.params.org_id,
            //compliances_url: api_endpoints.compliances+'?org_id='+vm.$route.params.org_id,

            proposals_url:   api_endpoints.proposals_paginated_internal+'&org_id='+vm.$route.params.org_id,
            approvals_url:   api_endpoints.approvals_paginated_internal+'&org_id='+vm.$route.params.org_id,
            compliances_url: api_endpoints.compliances_paginated_internal+'&org_id='+vm.$route.params.org_id,

            contacts_options:{
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                serverSide: true,
                dom: "<'d-flex align-items-center'<'me-auto'l>fB>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'d-flex align-items-center'<'me-auto'i>p>",
                buttons: [],
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/contacts'),
                    "dataSrc": 'data'
                },
                columnDefs: [
                                { responsivePriority: 1, targets: 0 }, // First visible column has top priority (e.g. proposal_number
                                { responsivePriority: 2, targets: 4 }, // If the actions is the last entry in columns then this will make it 2nd top priority soo as long as the screen is a decent size it will always be shown
                            ],
                columns: [
                    {
                        mRender:function (data,type,full) {
                            if(full.is_admin) {
                                return full.first_name + " " + full.last_name + " (Admin)";
                            } else {
                                return full.first_name + " " + full.last_name;
                            }
                        },
                        defaultContent: '',
                    },
                    {data:'phone_number',defaultContent: '',},
                    {data:'mobile_number',defaultContent: '',},
                    {data:'fax_number',defaultContent: '',},
                    {data:'email',defaultContent: '',},
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            let name = full.first_name + ' ' + full.last_name;
                            if(full.user_status=='ContactForm') {
                                // can delete contacts that were added via the manage.vue 'Contact Details' form
                                links +=  `<a data-email='${full.email}' data-name='${name}' data-id='${full.id}' class="remove-contact">Remove</a><br/>`;
                            }
                            links +=  `<a data-email-edit='${full.email}' data-name-edit='${name}' data-edit-id='${full.id}' class="edit-contact">Edit</a><br/>`;
                            return links;
                        },
                        defaultContent: '',
                    }
                  ],
                  processing: true
            },

            contacts_headers_ref:["Name","Role","Email","Status","Action"],
            contacts_options_ref:{
               language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                serverSide: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/contacts_exclude'),
                    //"url": helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/contacts_exclude'),

                    "dataSrc": 'data'
                },
                columnDefs: [
                                { responsivePriority: 1, targets: 0 }, // First visible column has top priority (e.g. proposal_number
                                { responsivePriority: 2, targets: 4 }, // If the actions is the last entry in columns then this will make it 2nd top priority soo as long as the screen is a decent size it will always be shown
                            ],
                columns: [
                    {
                        mRender:function (data,type,full) {
                            return full.first_name + " " + full.last_name;
                        },
                        defaultContent: '',
                    },
                    {data:'user_role', defaultContent: '',},
                    {data:'email', defaultContent: '',},
                    {data:'user_status', defaultContent: '',},
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            if (vm.is_das_admin){
                                if(full.user_status == 'Pending'){
                                    links +=  `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="accept_contact">Accept</a><br/>`;
                                    links +=  `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="decline_contact">Decline</a><br/>`;
                                } else if(full.user_status == 'Suspended'){
                                    links +=  `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="reinstate_contact">Reinstate</a><br/>`;
                                } else if(full.user_status == 'Active'){
                                    links +=  `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="unlink_contact">Unlink</a><br/>`;
                                    links +=  `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="suspend_contact">Suspend</a><br/>`;
                                    if(full.user_role == 'Organisation User'){
                                        links +=  `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="make_admin_contact">Make Organisation Admin</a><br/>`;
                                    } else {
                                        links +=  `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="make_user_contact">Make Organisation User</a><br/>`;
                                    }
                                } else if(full.user_status == 'Unlinked'){
                                    links +=  `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="relink_contact">Reinstate</a><br/>`;
                                } else if(full.user_status == 'Declined'){
                                    links +=  `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="accept_declined_contact">Accept (Previously Declined)</a><br/>`;
                                }
                            }        
                            return links;
                        },
                        defaultContent: '',
                    }
                  ],
                  processing: true,
                                  
            },
            filterOrgContactStatus: null,

        }
    },
    components: {
        datatable,
        ProposalDashTable,
        ApprovalDashTable,
        ComplianceDashTable,
        AddContact,
        CommsLogs,
        FormSection,
        AddCommLog,
    },
    computed: {
        isLoading: function () {
          return this.loading.length == 0;
        }
    },
    beforeRouteEnter: async function(to,){
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchOrganisation(to.params.org_id),
            utils.fetchProfile()
        ]
        // Promise.all(initialisers).then(data => {
        //     next(vm => {
        //         vm.countries = data[0];
        //         vm.org = data[1];
        //         vm.org.address = vm.org.address != null ? vm.org.address : {};
        //         vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
        //     });
        // });
        // return a callback from beforeRouteEnter instead of calling next(vm => ...) as it's deprecated.
        return Promise.all(initialisers).then(data => {
            return (vm) => {
                vm.countries = data[0];
                vm.org = data[1];
                vm.profile = data[2];
                vm.org.address = vm.org.address != null ? vm.org.address : {};
                vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
                vm.is_org_access_member=vm.profile.is_org_access_member;
                vm.is_das_admin=vm.profile.is_das_admin;
            };
        });
    },
    beforeRouteUpdate: async function(to){
        let initialisers = [
            utils.fetchOrganisation(to.params.org_id),
            utils.fetchProfile()
        ]
        // Promise.all(initialisers).then(data => {
        //     next(vm => {
        //         vm.org = data[0];
        //         vm.org.address = vm.org.address != null ? vm.org.address : {};
        //         vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
        //     });
        // });
        // return a callback from beforeRouteEnter instead of calling next(vm => ...) as it's deprecated.
        return Promise.all(initialisers).then(data => {
            return (vm) => {
                vm.org = data[0];
                vm.profile = data[1];
                vm.org.address = vm.org.address != null ? vm.org.address : {};
                vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
                vm.is_org_access_member=vm.profile.is_org_access_member;
                vm.is_das_admin=vm.profile.is_das_admin;
            };
        });
    },
    methods: {
        addContact: function(){
            this.$refs.add_contact.isModalOpen = true;
        },
        editContact: function(_id){
            fetch(helpers.add_endpoint_json(api_endpoints.organisation_contacts,_id))
            .then(async (response) => {
                if (!response.ok) { return response.json().then(err => { throw err }); }
                const data = await response.json();
                this.$refs.add_contact.contact = data;
                this.addContact();
            }).then(() => {
                this.$refs.contacts_datatable.vmDataTable.ajax.reload();
            }).catch((error) => {
                console.log(error);
            })
        },
        refreshDatatable: function(){
            this.$refs.contacts_datatable.vmDataTable.ajax.reload();
        },
        refreshActionFromResponse: function(action){
            let vm=this;

            if(action && this.user_action===action){
                let name = vm.contact_user?.first_name || 'the user'+ ' ' + (vm.contact_user?.last_name || '');

                if(action=='unlink'){
                    fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/unlink_user'),{
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(vm.contact_user)
                        }).then(async (response) => {
                            if (!response.ok) {
                                throw new Error(await helpers.parseApiError(response));
                            }
                            swal.fire({
                                title: 'Unlink',
                                text: 'You have successfully unlinked ' + name + '.',
                                icon: 'success',
                                confirmButtonText: 'Okay',
                                customClass: {
                                    confirmButton: 'btn btn-primary',
                                },
                            }).then((result) => {
                                if(result.isConfirmed){
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }
                            },(error) => {
                                console.log(error);
                            });
                        }).catch((error) => {
                            swal.fire({
                                title:'Organisation Unlink Error',
                                text: error.message || 'There was an error unlinking ' + name + ' from the Organisation.',
                                icon:'error',  
                                customClass: {
                                    confirmButton: 'btn btn-primary',
                                },
                            });
                            console.log(error?.message || JSON.stringify(error));
                        });
                }
                else if(action=='relink'){
                    fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/relink_user'),{
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(vm.contact_user)
                        }).then(async (response) => {
                            if (!response.ok) {
                                throw new Error(await helpers.parseApiError(response));
                            }
                            swal.fire({
                                title: 'Relink User',
                                text: 'You have successfully relinked ' + name + '.',
                                icon: 'success',
                                confirmButtonText: 'Ok',
                                customClass: {
                                    confirmButton: 'btn btn-primary',
                                },
                            }).then((result) => {
                                if(result.isConfirmed){
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }
                            },(error) => {
                                console.log('Swal error:'+error);
                            });
                        }).catch((error) => {
                            swal.fire('Relink User Error', error.message || 'There was an error relinking ' + name + '.','error',{
                                customClass: {
                                    confirmButton: 'btn btn-primary',
                                },
                            });
                            console.log(error?.message || JSON.stringify(error));
                        });
                }
                else if(action=='suspend'){
                    fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/suspend_user'),{
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(vm.contact_user)
                    }).then(async (response) => {
                        if (!response.ok) {
                            throw new Error(await helpers.parseApiError(response));
                        }
                        swal.fire({
                            title: 'Suspend User',
                            text: 'You have successfully suspended ' + name + ' as a User.',
                            icon: 'success',
                            confirmButtonText: 'Ok',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        }).then((result) => {
                            if(result.isConfirmed){
                                vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                            }
                        },(error) => {
                            console.log('Swal error:'+error);
                        });
                    }).catch((error) => {
                        swal.fire({
                            title:'Suspend User Error',
                            text: error.message || 'There was an error suspending ' + name + ' as a User.',
                            icon:'error',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        });
                        console.log(error?.message || JSON.stringify(error));
                    });
                }
                else if(action=='reinstate'){
                    fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/reinstate_user'),{
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(vm.contact_user)
                    }).then(async (response) => {
                        if (!response.ok) {
                            throw new Error(await helpers.parseApiError(response));
                        }
                        swal.fire({
                            title: 'Reinstate User',
                            text: 'You have successfully reinstated ' + name + '.',
                            icon: 'success',
                            confirmButtonText: 'Ok',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        }).then((result) => {
                            if(result.isConfirmed){
                                vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                            }
                        },(error) => {
                            console.log('Swal error:'+error);
                        });
                    }).catch((error) => {
                        swal.fire('Reinstate User Error', error.message || 'There was an error reinstating ' + name + '.','error',{
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        });
                        console.log(error?.message || JSON.stringify(error));
                    });
                }
                else if(action=='make_admin_contact'){
                    fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/make_admin_user'),{
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(vm.contact_user)
                    }).then(async (response) => {
                        if (!response.ok) {
                            throw new Error(await helpers.parseApiError(response));
                        }
                        swal.fire({
                            title: 'Organisation Admin',
                            text: 'You have successfully made ' + name + ' an Organisation Admin.',
                            icon: 'success',
                            confirmButtonText: 'Ok',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        }).then((result) => {
                            if(result.isConfirmed){
                                vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                            }
                        },(error) => {
                            console.log('Swal error:'+error);
                        });
                    }).catch((error) => {
                        swal.fire({
                            title:'Organisation Admin Error',
                            text: error.message || 'There was an error making ' + name + ' an Organisation Admin.',
                            icon:'error',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        });
                        console.log(error?.message || JSON.stringify(error));
                    });
                }
                else if(action=='make_user_contact'){
                    fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/make_user'),{
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(vm.contact_user)
                    }).then(async (response) => {
                        if (!response.ok) {
                            throw new Error(await helpers.parseApiError(response));
                        }
                        swal.fire({
                            title: 'Organisation User',
                            text: 'You have successfully made ' + name + ' an Organisation User.',
                            icon: 'success',
                            confirmButtonText: 'Ok',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        }).then((result) => {
                            if(result.isConfirmed){
                                vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                            }
                        },(error) => {
                            console.log('Swal error:'+error);
                        });
                    }).catch((error) => {
                        swal.fire({
                            title:'Company Admin',
                            text: error.message || 'There was an error making ' + name + ' an Organisation User.',
                            icon:'error',  
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        });
                        console.log(error?.message || JSON.stringify(error));
                    });
                }
                else if(action=='accept'){
                    fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/accept_user'),{
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(vm.contact_user)
                    }).then(async (response) => {
                        if (!response.ok) { return response.json().then(err => { throw err }); }
                        swal.fire({
                            title: 'Contact Accept',
                            text: 'You have successfully accepted ' + name + '.',
                            icon: 'success',
                            confirmButtonText: 'Ok',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        }).then(() => {
                            vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                        },(error) => {
                            console.log('Swal error: '+error);
                        });
                    }).catch((error) => {
                        swal.fire({
                            title:'Contact Accept Error',
                            text:helpers.formatFetchError(error),
                            icon:'error',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        });
                        console.log(error?.message || JSON.stringify(error));
                    });
                }
                else if(action=='decline'){
                    fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/decline_user'),{
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(vm.contact_user)
                    }).then(async (response) => {
                        if (!response.ok) {
                            throw new Error(await helpers.parseApiError(response));
                        }
                        swal.fire({
                            title: 'Contact Decline',
                            text: 'You have successfully declined ' + name + '.',
                            icon: 'success',
                            confirmButtonText: 'Ok',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        }).then((result) => {
                            if(result.isConfirmed){
                                vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                            }
                        }).catch((error) => {
                            swal.fire({
                                title:'Contact Decline Error',
                                text: error.message || 'There was an error declining ' + name + '.',
                                icon:'error',
                                customClass: {
                                    confirmButton: 'btn btn-primary',
                                },
                            });
                            console.log(error?.message || JSON.stringify(error));
                        });
                    }, (error) => {
                        swal.fire({
                            title:'Contact Decline Error',
                            text: error.message || 'There was an error declining ' + name + '.',
                            icon:'error',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        });
                        console.log(error?.message || JSON.stringify(error));
                    });
                }
                else if(action=='accept_declined'){
                    fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/accept_declined_user'),{
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(vm.contact_user)
                    }).then(async (response) => {
                        if (!response.ok) { return response.json().then(err => { throw err }); }
                        swal.fire({
                            title: 'Contact Accept (Previously Declined)',
                            text: 'You have successfully accepted ' + name + '.',
                            icon: 'success',
                            confirmButtonText: 'Ok',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        }).then((result) => {
                            if(result.isConfirmed){
                                vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                            }
                        },(error) => {
                            console.log(error);
                        });
                    }).catch((error) => {
                        swal.fire({
                            title:'Contact Accept (Previously Declined)',
                            // text:'There was an error accepting ' + name + '.',
                            text:helpers.formatFetchError(error),
                            icon:'error',
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        });
                        console.log(error?.message || JSON.stringify(error));
                    });
                }
            }
        },
        eventListeners: function(){
            let vm = this;
            vm.$refs.contacts_datatable.vmDataTable.on('click','.remove-contact',(e) => {
                e.preventDefault();

                let name = $(e.target).data('name');
                let email = $(e.target).data('email');
                let id = $(e.target).data('id');
                swal.fire({
                    title: "Delete Contact",
                    text: "Are you sure you want to remove "+ name + "("+ email + ") as a contact  ?",
                    icon: "error",
                    showCancelButton: true,
                    confirmButtonText: 'Accept',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                        cancelButton: 'btn btn-secondary',
                    },
                }).then((swalresult) => {
                    if(swalresult.isConfirmed){
                        vm.deleteContact(id);
                    }
                },(error) => {
                    console.log(error);
                });
            });

            vm.$refs.contacts_datatable.vmDataTable.on('click','.edit-contact',(e) => {
                e.preventDefault();
                let id = $(e.target).attr('data-edit-id');
                vm.editContact(id);
            });

            vm.$refs.contacts_datatable_user.vmDataTable.on('click','.accept_contact',(e) => {
                e.preventDefault();
                let firstname = $(e.target).data('firstname');
                let lastname = $(e.target).data('lastname');
                let name = firstname + ' ' + lastname;
                let email = $(e.target).data('email');
                // let id = $(e.target).data('id');
                let mobile = $(e.target).data('mobile');
                let phone = $(e.target).data('phone');
                vm.contact_user.first_name= firstname 
                vm.contact_user.last_name= lastname
                vm.contact_user.email= email 
                vm.contact_user.mobile_number= mobile 
                vm.contact_user.phone_number= phone 
                swal.fire({
                    title: "Contact Accept",
                    text: "Are you sure you want to accept contact request " + name + " (" + email + ")?",
                    showCancelButton: true,
                    confirmButtonText: 'Accept',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                        cancelButton: 'btn btn-secondary',
                    },
                }).then((result) => {
                    if (result.isConfirmed){
                        vm.user_action = 'accept';
                        this.addComm();
                    }
                },(error) => {
                    console.log(error);
                });
            });
            vm.$refs.contacts_datatable_user.vmDataTable.on('click','.accept_declined_contact',(e) => {
                e.preventDefault();
                let firstname = $(e.target).data('firstname');
                let lastname = $(e.target).data('lastname');
                let name = firstname + ' ' + lastname;
                let email = $(e.target).data('email');
                // let id = $(e.target).data('id');
                let mobile = $(e.target).data('mobile');
                let phone = $(e.target).data('phone');
                vm.contact_user.first_name= firstname
                vm.contact_user.last_name= lastname
                vm.contact_user.email= email
                vm.contact_user.mobile_number= mobile
                vm.contact_user.phone_number= phone
                swal.fire({
                    title: "Contact Accept (Previously Declined)",
                    text: "Are you sure you want to accept the previously declined contact request for " + name + " (" + email + ")?",
                    showCancelButton: true,
                    confirmButtonText: 'Accept',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                        cancelButton: 'btn btn-secondary',
                    },
                }).then((result) => {
                    if (result.isConfirmed){
                        vm.user_action = 'accept_declined';
                        this.addComm();
                    }
                },(error) => {
                    console.log(error);
                });
            });
            vm.$refs.contacts_datatable_user.vmDataTable.on('click','.decline_contact',(e) => {
                e.preventDefault();
                let firstname = $(e.target).data('firstname');
                let lastname = $(e.target).data('lastname');
                let name = firstname + ' ' + lastname;
                let email = $(e.target).data('email');
                // let id = $(e.target).data('id');
                let mobile = $(e.target).data('mobile');
                let phone = $(e.target).data('phone');
                vm.contact_user.first_name= firstname 
                vm.contact_user.last_name= lastname
                vm.contact_user.email= email 
                vm.contact_user.mobile_number= mobile 
                vm.contact_user.phone_number= phone 
                // console.log(vm.contact_user)
                swal.fire({
                    title: "Contact Decline",
                    text: "Are you sure you want to decline the contact request for " + name + " (" + email + ")?",
                    showCancelButton: true,
                    confirmButtonText: 'Accept',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                        cancelButton: 'btn btn-secondary',
                    },
                }).then((result) => {
                    if (result){
                        vm.user_action = 'decline';
                        this.addComm();
                    }
                },(error) => {
                    console.log(error);
                });
            });
            vm.$refs.contacts_datatable_user.vmDataTable.on('click','.unlink_contact',(e) => {
                e.preventDefault();
                let firstname = $(e.target).data('firstname');
                let lastname = $(e.target).data('lastname');
                let name = firstname + ' ' + lastname;
                let email = $(e.target).data('email');
                // let id = $(e.target).data('id');
                let mobile = $(e.target).data('mobile');
                let phone = $(e.target).data('phone');
                vm.contact_user.first_name= firstname 
                vm.contact_user.last_name= lastname
                vm.contact_user.email= email 
                vm.contact_user.mobile_number= mobile 
                vm.contact_user.phone_number= phone 
                swal.fire({
                    title: "Unlink",
                    text: "Are you sure you want to unlink " + name + " (" + email + ")?",
                    showCancelButton: true,
                    confirmButtonText: 'Accept',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                        cancelButton: 'btn btn-secondary',
                    },
                }).then((result) => {
                    if (result.isConfirmed){
                        vm.user_action = 'unlink';
                        this.addComm();
                    }
                },(error) => {
                    console.log(error);
                });
            });
            vm.$refs.contacts_datatable_user.vmDataTable.on('click','.make_admin_contact',(e) => {
                e.preventDefault();
                let firstname = $(e.target).data('firstname');
                let lastname = $(e.target).data('lastname');
                let name = firstname + ' ' + lastname;
                let email = $(e.target).data('email');
                // let id = $(e.target).data('id');
                let mobile = $(e.target).data('mobile');
                let phone = $(e.target).data('phone');
                vm.contact_user.first_name= firstname 
                vm.contact_user.last_name= lastname
                vm.contact_user.email= email 
                vm.contact_user.mobile_number= mobile 
                vm.contact_user.phone_number= phone 
                swal.fire({
                    title: "Organisation Admin",
                    text: "Are you sure you want to make " + name + " (" + email + ") an Organisation Admin?",
                    showCancelButton: true,
                    confirmButtonText: 'Accept',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                        cancelButton: 'btn btn-secondary',
                    },
                }).then((result) => {
                    if (result.isConfirmed) {
                        vm.user_action = 'make_admin_contact';
                        this.addComm();
                    }
                },(error) => {
                    console.log(error);
                });
            });
            vm.$refs.contacts_datatable_user.vmDataTable.on('click','.make_user_contact',(e) => {
                e.preventDefault();
                let firstname = $(e.target).data('firstname');
                let lastname = $(e.target).data('lastname');
                let name = firstname + ' ' + lastname;
                let email = $(e.target).data('email');
                // let id = $(e.target).data('id');
                let mobile = $(e.target).data('mobile');
                let phone = $(e.target).data('phone');
                vm.contact_user.first_name= firstname 
                vm.contact_user.last_name= lastname
                vm.contact_user.email= email 
                vm.contact_user.mobile_number= mobile 
                vm.contact_user.phone_number= phone 
                swal.fire({
                    title: "Organisation User",
                    text: "Are you sure you want to make " + name + " (" + email + ") an Organisation User?",
                    showCancelButton: true,
                    confirmButtonText: 'Accept',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                        cancelButton: 'btn btn-secondary',
                    },
                }).then((result) => {
                    console.log(result);
                    if (result.isConfirmed) {
                        vm.user_action = 'make_user_contact';
                        this.addComm();
                    }
                },(error) => {
                    console.log(error);
                });
            });
            vm.$refs.contacts_datatable_user.vmDataTable.on('click','.suspend_contact',(e) => {
                e.preventDefault();
                let firstname = $(e.target).data('firstname');
                let lastname = $(e.target).data('lastname');
                let name = firstname + ' ' + lastname;
                let email = $(e.target).data('email');
                // let id = $(e.target).data('id');
                let mobile = $(e.target).data('mobile');
                let phone = $(e.target).data('phone');
                vm.contact_user.first_name= firstname 
                vm.contact_user.last_name= lastname
                vm.contact_user.email= email 
                vm.contact_user.mobile_number= mobile 
                vm.contact_user.phone_number= phone 
                swal.fire({
                    title: "Suspend User",
                    text: "Are you sure you want to Suspend  " + name + " (" + email + ")?",
                    showCancelButton: true,
                    confirmButtonText: 'Accept',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                        cancelButton: 'btn btn-secondary',
                    },
                }).then((result) => {
                    if (result.isConfirmed) {
                        vm.user_action = 'suspend';
                        this.addComm();
                    }
                },(error) => {
                    console.log(error);
                });
            });
             vm.$refs.contacts_datatable_user.vmDataTable.on('click','.reinstate_contact',(e) => {
                e.preventDefault();
                let firstname = $(e.target).data('firstname');
                let lastname = $(e.target).data('lastname');
                let name = firstname + ' ' + lastname;
                let email = $(e.target).data('email');
                // let id = $(e.target).data('id');
                let mobile = $(e.target).data('mobile');
                let phone = $(e.target).data('phone');
                vm.contact_user.first_name= firstname 
                vm.contact_user.last_name= lastname
                vm.contact_user.email= email 
                vm.contact_user.mobile_number= mobile 
                vm.contact_user.phone_number= phone 
                swal.fire({
                    title: "Reinstate User",
                    text: "Are you sure you want to Reinstate  " + name + " (" + email + ")?",
                    showCancelButton: true,
                    confirmButtonText: 'Accept',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                        cancelButton: 'btn btn-secondary',
                    },
                }).then((result) => {
                    if (result.isConfirmed) {
                        vm.user_action = 'reinstate';
                        this.addComm();
                    }
                },(error) => {
                    console.log(error);
                });
            });
             vm.$refs.contacts_datatable_user.vmDataTable.on('click','.relink_contact',(e) => {
                e.preventDefault();
                let firstname = $(e.target).data('firstname');
                let lastname = $(e.target).data('lastname');
                let name = firstname + ' ' + lastname;
                let email = $(e.target).data('email');
                // let id = $(e.target).data('id');
                let mobile = $(e.target).data('mobile');
                let phone = $(e.target).data('phone');
                vm.contact_user.first_name= firstname
                vm.contact_user.last_name= lastname
                vm.contact_user.email= email
                vm.contact_user.mobile_number= mobile
                vm.contact_user.phone_number= phone
                swal.fire({
                    title: "Relink User",
                    text: "Are you sure you want to Relink  " + name + " (" + email + ")?",
                    showCancelButton: true,
                    confirmButtonText: 'Accept',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                        cancelButton: 'btn btn-secondary',
                    },
                }).then((result) => {
                    if (result.isConfirmed) {
                        vm.user_action = 'relink';
                        this.addComm();
                    }
                },(error) => {
                    console.log(error);
                });
            });

            // Fix the table responsiveness when tab is shown
            $('a[href="#'+vm.oTab+'"]').on('shown.bs.tab', function () {
                vm.$refs.proposals_table.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
                vm.$refs.approvals_table.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
                vm.$refs.compliances_table.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
            });
        },
        addComm(){
            this.$refs.add_comm_org.isModalOpen = true;
        },
        updateDetails: function() {
            let vm = this;
            vm.updatingDetails = true;
            fetch(helpers.add_endpoint_json(api_endpoints.organisations,(vm.org.id+'/update_details')),{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(vm.org)
            }).then(async (response) => {
                if (!response.ok) {
                    throw new Error(`Update Organisation Details Failed: ${response.status}`);
                }
                vm.updatingDetails = false;
                vm.org = await response.json();
                if (vm.org.address == null){ vm.org.address = {}; }
                swal.fire({
                    title:'Saved',
                    text:'Organisation details have been saved',
                    icon:'success',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                    },
                });
            }).catch((error) => {
                console.log(error);
                var text= error;
                // var text= helpers.apiVueResourceError(error);
                if(typeof text == 'object'){
                    if (Object.prototype.hasOwnProperty.call(text, 'email')) {
                        text=text.email[0];
                    }
                }
                swal.fire({
                    title:'Error', 
                    text:'Organisation details have cannot be saved because of the following error: '+text,
                    icon:'error',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                    },
                });
                vm.updatingDetails = false;
            });
        },
        addedContact: function() {
            let vm = this;
            swal.fire({
                title:'Added',
                text:'The contact has been successfully added.',
                icon:'success',
                customClass: {
                    confirmButton: 'btn btn-primary',
                },
            });
            vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
        },
        deleteContact: function(id){
            let vm = this;
            
            fetch(helpers.add_endpoint_json(api_endpoints.organisation_contacts,id),{
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(async (response) => {
                if (!response.ok) {
                    throw new Error(`Contact Deletetion Failed: ${response.status}`);
                }
                swal.fire({
                    title:'Contact Deleted', 
                    text:'The contact was successfully deleted',
                    icon:'success',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                    },
                });
                vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
            }).catch((error) => {
                console.log(error);
                let errorMessage = 'The contact could not be deleted because of the following error: [';

                if (error && typeof error === 'object') {
                    errorMessage += JSON.stringify(error);
                } else {
                    errorMessage += error;
                }

                errorMessage += ']';

                swal.fire({
                    title:'Contact Deletion Failed',
                    text:errorMessage,
                    icon:'error',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                    },
                });
            });


        },
        updateAddress: function() {
            let vm = this;
            vm.updatingAddress = true;
            fetch(helpers.add_endpoint_json(api_endpoints.organisations,(vm.org.id+'/update_address')),{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(vm.org.address)
            }).then(async (response) => {
                if (!response.ok) {
                    throw new Error(`Update Organisation Address Failed: ${response.status}`);
                }
                vm.updatingAddress = false;
                vm.org = await response.json();
                swal.fire({
                    title:'Saved',
                    text:'Address details have been saved',
                    icon:'success',
                    customClass: {
                        confirmButton: 'btn btn-primary',
                    },
                });
                if (vm.org.address == null){ vm.org.address = {}; }
            }).catch((error) => {
                console.log(error);
                vm.updatingAddress = false;
            });
        },
    },
    mounted: function(){
        // let vm = this;
        this.personal_form = document.forms.personal_form;
        this.eventListeners();
    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
.hidePopover {
    display: none;
}

</style>
