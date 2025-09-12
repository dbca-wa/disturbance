<template>
    <div class="container-fluid" id="internalOrgInfo">
    <div class="row">
    <div class="col-md-10 col-md-offset-1">
        <div class="row">
            <h3>{{ org.name }} - {{org.abn}}</h3>
            <div class="col-md-3">
                <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            </div>
            <div class="col-md-1">
            </div>
            <div class="col-md-8">
                <ul class="nav nav-pills mb-3" role="tablist">
                    <li class="nav-item"><a
                            id="pills-details-tab"
                            data-toggle="tab"
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
                            data-toggle="tab"
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
                                        <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Name</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="first_name" placeholder="" v-model="org.name">
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >ABN</label>
                                            <div class="col-sm-6">
                                                <input type="text" disabled class="form-control" name="last_name" placeholder="" v-model="org.abn">
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Email</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="last_name" placeholder="" v-model="org.email">
                                            </div>
                                        </div>
                                        <div class="form-group">
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
                                <FormSection :formCollapse="false" label="Address Details" Index="address_details">
                                    <form class="form-horizontal" action="index.html" method="post">
                                        <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Street</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="street" placeholder="" v-model="org.address.line1">
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                            <div class="col-sm-6">
                                                <input type="text" class="form-control" name="surburb" placeholder="" v-model="org.address.locality">
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">State</label>
                                            <div class="col-sm-2">
                                                <input type="text" class="form-control" name="country" placeholder="" v-model="org.address.state">
                                            </div>
                                            <label for="" class="col-sm-2 control-label">Postcode</label>
                                            <div class="col-sm-2">
                                                <input type="text" class="form-control" name="postcode" placeholder="" v-model="org.address.postcode">
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Country</label>
                                            <div class="col-sm-4">
                                                <select class="form-control" name="country" v-model="org.address.country">
                                                    <option v-for="c in countries" :value="c.code" :key="c.code">{{ c.name }}</option>
                                                </select>
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
                                <FormSection :formCollapse="false" label="Contact Details" Index="contact_details">
                                    <form class="form-horizontal" action="index.html" method="post">
                                        <div class="col-sm-12">
                                            <button @click.prevent="addContact()" style="margin-bottom:10px;" class="btn btn-primary pull-right">Add Contact</button>
                                        </div>
                                        <div class="col-sm-12 row top-buffer-s">
                                            <datatable ref="contacts_datatable" id="organisation_contacts_datatable" :dtOptions="contacts_options" :dtHeaders="contacts_headers"/>
                                        </div>
                                    </form>
                                </FormSection>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-12">
                                <FormSection :formCollapse="false" label="Linked Persons" Index="linked_persons" subtitle="Manage the user accounts linked to the organisation">
                                    <div class="row">
                                        <div class="col-sm-8">
                                            <div class="row">
                                                <div class="col-sm-12">
                                                    <h4>Persons linked to this organisation:</h4>
                                                </div>
                                                <div v-for="d in org.delegates" :key="d.id">
                                                    <div v-if="d.is_admin" class="col-sm-6">
                                                        <h4>{{d.name}} (Admin)</h4>
                                                    </div>
                                                    <div v-else class="col-sm-6">
                                                        <h4>{{d.name}}</h4>
                                                    </div>
                                                </div>
                                                <div class="col-sm-12 top-buffer-s">
                                                    <strong>Persons linked to the organisation are controlled by the organisation. The Department cannot manage this list of people.</strong>
                                                </div>
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
                                    </div>
                                    <form class="form-horizontal" action="index.html" method="post" v-if="org.pins">
                                         <div class="col-sm-6 row">
                                            <div class="form-group">
                                                <label for="" class="col-sm-6 control-label"> Organisation User Pin Code 1:</label>
                                                <div class="col-sm-6">
                                                    <label class="control-label">{{org.pins.three}}</label>
                                                </div>
                                            </div>
                                            <div class="form-group">
                                                <label for="" class="col-sm-6 control-label" >Organisation User Pin Code 2:</label>
                                                <div class="col-sm-6">
                                                    <label class="control-label">{{org.pins.four}}</label>
                                                </div>
                                            </div>
                                        </div>
                                         <div class="col-sm-6 row">
                                            <div class="form-group">
                                                <label for="" class="col-sm-6 control-label"> Organisation Administrator Pin Code 1:</label>
                                                <div class="col-sm-6">
                                                    <label class="control-label">{{org.pins.one}}</label>
                                                </div>
                                            </div>
                                            <div class="form-group" >
                                                <label for="" class="col-sm-6 control-label" >Organisation Administrator Pin Code 2:</label>
                                                <div class="col-sm-6">
                                                    <label class="control-label">{{org.pins.two}}</label>
                                                </div>
                                            </div>
                                        </div>
                                    </form>
                                </FormSection>
                            </div>
                        </div>
                    </div> 
                    <div :id="oTab" class="tab-pane fade" role="tabpanel" aria-labelledby="pills-other-tab">
                        <FormSection :form-collapse="false" label="Proposals" Index="proposals">
                            <ProposalDashTable ref="proposals_table" level='internal' :url='proposals_url'/>
                        </FormSection>
                        <FormSection :form-collapse="false" label="Approvals" Index="approvals">
                            <ApprovalDashTable ref="approvals_table" level='internal' :url='approvals_url'/>
                        </FormSection>
                        <FormSection :form-collapse="false" label="Compliances with requirements" Index="compliances">
                            <ComplianceDashTable ref="compliances_table" level='internal' :url='compliances_url'/>
                        </FormSection>
                    </div>
                </div>
            </div>
        </div>
        </div>
        </div>
        <AddContact ref="add_contact" :org_id="org.id" />
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
export default {
    name: 'OrganisationComponent',
    data () {
        let vm = this;
        return {
            dTab: 'dTab'+uuidv4(),
            oTab: 'oTab'+uuidv4(),
            org: {
                address: {}
            },
            loading: [],
            countries: [],
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

            proposals_url:   api_endpoints.proposals_paginated_external+'&org_id='+vm.$route.params.org_id,
            approvals_url:   api_endpoints.approvals_paginated_external+'&org_id='+vm.$route.params.org_id,
            compliances_url: api_endpoints.compliances_paginated_external+'&org_id='+vm.$route.params.org_id,

            contacts_options:{
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/contacts'),
                    "dataSrc": ''
                },
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
            }
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
    },
    computed: {
        isLoading: function () {
          return this.loading.length == 0;
        }
    },
    beforeRouteEnter: function(to, from, next){
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchOrganisation(to.params.org_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.countries = data[0];
                vm.org = data[1];
                vm.org.address = vm.org.address != null ? vm.org.address : {};
                vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
            });
        });
    },
    beforeRouteUpdate: function(to, from, next){
        let initialisers = [
            utils.fetchOrganisation(to.params.org_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.org = data[0];
                vm.org.address = vm.org.address != null ? vm.org.address : {};
                vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
            });
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
                    confirmButtonText: 'Accept'
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

            // Fix the table responsiveness when tab is shown
            $('a[href="#'+vm.oTab+'"]').on('shown.bs.tab', function () {
                vm.$refs.proposals_table.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
                vm.$refs.approvals_table.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
                vm.$refs.compliances_table.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
            });
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
                swal.fire(
                    'Saved',
                    'Organisation details have been saved',
                    'success'
                )
            }).catch((error) => {
                console.log(error);
                var text= error;
                // var text= helpers.apiVueResourceError(error);
                if(typeof text == 'object'){
                    if (Object.prototype.hasOwnProperty.call(text, 'email')) {
                        text=text.email[0];
                    }
                }
                swal.fire(
                    'Error', 
                    'Organisation details have cannot be saved because of the following error: '+text,
                    'error'
                )
                vm.updatingDetails = false;
            });
        },
        addedContact: function() {
            let vm = this;
            swal.fire(
                'Added',
                'The contact has been successfully added.',
                'success'
            )
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
                swal.fire(
                    'Contact Deleted', 
                    'The contact was successfully deleted',
                    'success'
                )
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

                swal.fire(
                    'Contact Deletion Failed',
                    errorMessage,
                    'error'
                );
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
                swal.fire(
                    'Saved',
                    'Address details have been saved',
                    'success'
                )
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
