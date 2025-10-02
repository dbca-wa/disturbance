<template>
    <div :class="div_container ? 'container' : ''">

        <FormSection v-if="org && show_org" :formCollapse="org_collapse" label="Organisation Details" Index="org_details" subheading="View and update the organisation's details">
            <form class="form-horizontal" name="personal_form" method="post">
              <div class="form-group">
                <div class="row mb-3">
                    <label for="" class="col-sm-3 col-form-label">Name</label>
                    <div class="col-sm-6">
                        <input type="text" class="form-control" name="first_name" placeholder="" v-model="org.name">
                    </div>
                </div>
              </div>
              <div class="form-group">
                <div class="row mb-3">
                    <label for="" class="col-sm-3 col-form-label" >ABN</label>
                    <div class="col-sm-6">
                        <input type="text" disabled class="form-control" name="last_name" placeholder="" v-model="org.abn">
                    </div>
                </div>
              </div>
              <div class="form-group">
                <div class="row mb-3">
                    <label for="" class="col-sm-3 col-form-label" >Email</label>
                    <div class="col-sm-6">
                        <input type="text" class="form-control" name="email" placeholder="" v-model="org.email">
                    </div>
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
        <!-- <FormSection v-if="org && show_address" :formCollapse="address_collapse" label="Address Details" Index="add_details" subheading="View and update the organisation's address details"> -->
        <FormSection v-if="org && show_address" label="Address Details" Index="add_details" subheading="View and update the organisation's address details">
            <form class="form-horizontal" action="index.html" method="post">
              <div class="form-group">
                <div class="row mb-3">
                    <label for="" class="col-sm-3 col-form-label">Street</label>
                    <div class="col-sm-6">
                        <input type="text" class="form-control" name="street" placeholder="" v-model="org.address.line1">
                    </div>
                </div>
              </div>
              <div class="form-group">
                <div class="row mb-3">
                    <label for="" class="col-sm-3 col-form-label" >Town/Suburb</label>
                    <div class="col-sm-6">
                        <input type="text" class="form-control" name="surburb" placeholder="" v-model="org.address.locality">
                    </div>
                </div>
              </div>
              <div class="form-group">
                <div class="row mb-3">
                    <label for="" class="col-sm-3 col-form-label">State</label>
                    <div class="col-sm-3">
                        <input type="text" class="form-control" name="country" placeholder="" v-model="org.address.state">
                    </div>
                    <label for="" class="col-sm-1 col-form-label">Postcode</label>
                    <div class="col-sm-2">
                        <input type="text" class="form-control" name="postcode" placeholder="" v-model="org.address.postcode">
                    </div>
                </div>
              </div>
              <div class="form-group">
                <div class="row mb-3">
                    <label for="" class="col-sm-3 col-form-label">Country</label>
                    <div class="col-sm-4">
                        <select class="form-control" name="country" v-model="org.address.country">
                            <option v-for="c in countries" :value="c.code" :key="c.code">{{ c.name }}</option>
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

        <!-- <FormSection v-if="org && show_linked" :formCollapse="linked_collapse" label="Linked Details" Index="linked_details" subheading="Manage the user accounts linked to the organisation"> -->
        <FormSection v-if="org && show_linked" label="Linked Details" Index="linked_details" subheading="Manage the user accounts linked to the organisation">
            <div class="col-sm-12 row">
                <h6>Use the Organisation Administrator pin codes if you want the new user to be linked as organisation administrator.<br> Use the Organisation User pin codes if you want the new user to be linked as organisation user.</h6>
            </div>
            <form class="form-horizontal" action="index.html" method="post">
                <div class="row">
                <div class="col-sm-6">
                    <div class="form-group">
                        <div class="row mb-3">
                            <label for="" class="col-sm-5 col-form-label"> Organisation User Pin Code 1:</label>
                            <div class="col-sm-6">
                                <label class="col-form-label">{{org.pins.three}}</label>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="row mb-3">
                            <label for="" class="col-sm-5 col-form-label" >Organisation User Pin Code 2:</label>
                            <div class="col-sm-6">
                                <label class="col-form-label">{{org.pins.four}}</label>
                            </div>
                        </div>
                    </div>
                </div>
                 <div class="col-sm-6">
                    <div class="form-group" :disabled ='!myorgperms.is_admin'>
                        <div class="row mb-3">
                            <label for="" class="col-sm-5 col-form-label"> Organisation Administrator Pin Code 1:</label>
                            <div class="col-sm-6">
                                <label class="col-form-label">{{org.pins.one}}</label>
                            </div>
                        </div>
                    </div>
                    <div class="form-group" :disabled ='!myorgperms.is_admin'>
                        <div class="row mb-3">
                            <label for="" class="col-sm-5 col-form-label" >Organisation Administrator Pin Code 2:</label>
                            <div class="col-sm-6">
                                <label class="col-form-label">{{org.pins.two}}</label>
                            </div>
                        </div>
                    </div>
                </div>
                </div>
            </form>
            <div>
                <div class="col-sm-12 row mb-3">
                    <div class="row">
                        <div class="col-sm-12 top-buffer-s">
                            <strong>Persons linked to the organisation are controlled by the organisation. The Department cannot manage this list of people.</strong>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col-sm-12">
                    <datatable ref="contacts_datatable_user" id="organisation_contacts_datatable_ref" :dtOptions="contacts_options_ref" :dtHeaders="contacts_headers_ref" v-model="filterOrgContactStatus"/>
                </div>
            </div>
        </FormSection>

    </div>
</template>

<script>
import { v4 as uuidv4 } from 'uuid';
import { api_endpoints, helpers, constants } from '@/utils/hooks'
import datatable from '@vue-utils/datatable.vue'
import utils from '../utils'
import api from '../api'
import FormSection from "@/components/forms/section_toggle.vue"


export default {
    name: 'ManageOrganisation',
    props:{
        org_id:{
            type: Number,
            default: null
        },
        isApplication:{
            type: Boolean,
            default: false
        },
        show_org:{
            type: Boolean,
            default: true
        },
        show_address:{
            type: Boolean,
            default: true
        },
        show_linked:{
            type: Boolean,
            default: true
        },
        show_contact:{
            type: Boolean,
            default: true
        },
        org_collapse:{
            type: Boolean,
            default: false
        },
        address_collapse:{
            type: Boolean,
            default: true
        },
        linked_collapse:{
            type: Boolean,
            default: true
        },
        div_container:{
            type: Boolean,
            default: true
        },
    },
    data () {
        let vm = this;
        return {
            adBody: 'adBody'+ uuidv4(),
            pBody: 'pBody'+ uuidv4(),
            cBody: 'cBody'+ uuidv4(),
            oBody: 'oBody'+ uuidv4(),
            org: null,
            loading: [],
            countries: [],
            contact_user: {
                first_name: null,
                last_name: null,
                email: null,
                mobile_number: null,
                phone_number: null
            },
            updatingDetails: false,
            updatingAddress: false,
            updatingContact: false,
            logsTable: null,
            myorgperms: null,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            logsDtOptions:{
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                deferRender: true, 
                autowidth: true,
                order: [[2, 'desc']],
                dom:
                    "<'row'<'col-sm-5'l><'col-sm-6'f>>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                processing:true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/action_log'),
                    "dataSrc": '',
                },
                columns:[
                    {
                        data:"who",
                    },
                    {
                        data:"what",
                    },
                    {
                        data:"when",
                        mRender:function(data){
                            return moment(data).format(vm.DATE_TIME_FORMAT)
                        }
                    },
                ]
            },
            commsDtOptions:{
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                deferRender: true, 
                autowidth: true,
                order: [[0, 'desc']],
                processing:true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/comms_log'),
                    "dataSrc": '',
                },
                columns:[
                    {
                        title: 'Date',
                        data: 'created',
                        render: function (date) {
                            return moment(date).format(vm.DATE_TIME_FORMAT);
                        },
                        defaultContent: '',
                    },
                    {
                        title: 'Type',
                        data: 'type',
                        defaultContent: '',
                    },
                    {
                        title: 'Reference',
                        data: 'reference',
                        defaultContent: '',
                    },
                    {
                        title: 'To',
                        data: 'to',
                        render: vm.commaToNewline,
                        defaultContent: '',
                    },
                    {
                        title: 'CC',
                        data: 'cc',
                        render: vm.commaToNewline,
                        defaultContent: '',
                    },
                    {
                        title: 'From',
                        data: 'fromm',
                        render: vm.commaToNewline,
                        defaultContent: '',
                    },
                    {
                        title: 'Subject/Desc.',
                        data: 'subject',
                        defaultContent: '',
                    },
                    {
                        title: 'Text',
                        data: 'text',
                        'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 100,
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
                                    text: value
                                });
                            }

                            return result;
                        },
                        'createdCell': function (cell) {
                            //TODO why this is not working?
                            // the call to popover is done in the 'draw' event
                            $(cell).popover();
                        },
                        defaultContent: '',
                    },
                    {
                        title: 'Documents',
                        data: 'documents',
                        'render': function (values) {
                            var result = '';
                            _.forEach(values, function (value) {
                                // We expect an array [docName, url]
                                // if it's a string it is the url
                                var docName = '',
                                    url = '';
                                if (_.isArray(value) && value.length > 1){
                                    docName = value[0];
                                    url = value[1];
                                }
                                if (typeof s === 'string'){
                                    url = value;
                                    // display the first  chars of the filename
                                    docName = _.last(value.split('/'));
                                    docName = _.truncate(docName, {
                                        length: 18,
                                        omission: '...',
                                        separator: ' '
                                    });
                                }
                                result += '<a href="' + url + '" target="_blank"><p>' + docName+ '</p></a><br>';
                            });
                            return result;
                        },
                        defaultContent: '',
                    }
                ]
            },
            commsTable : null,





            contacts_headers:["Name","Phone","Mobile","Fax","Email","Action"],
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
                    {data:'phone_number'},
                    {data:'mobile_number'},
                    {data:'fax_number'},
                    {data:'email'},
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            if(!full.is_admin) {
                                let name = full.first_name + ' ' + full.last_name;
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
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.organisations,vm.$route.params.org_id+'/contacts_exclude'),
                    //"url": helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/contacts_exclude'),

                    "dataSrc": ''
                },
                columns: [
                    {
                        mRender:function (data,type,full) {
                            return full.first_name + " " + full.last_name;
                        },
                        defaultContent: '',
                    },
                    {data:'user_role'},
                    {data:'email'},
                    {data:'user_status'},
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            if (vm.myorgperms.is_admin){
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
             // Note: Had to add this variable, it didn't exist. It is the model of the datatable component. What is it for?
            filterOrgContactStatus: null,
        }
    },
    components: {
        datatable,
        FormSection,
    },
    computed: {
    },
    beforeRouteEnter: function(to, from, next){
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchOrganisation(to.params.org_id),
            utils.fetchOrganisationPermissions(to.params.org_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.countries = data[0];
                vm.org = data[1];
                vm.myorgperms = data[2];
                vm.org.address = vm.org.address != null ? vm.org.address : {};
                vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
               
            });
        });
    },
    beforeRouteUpdate: function(to, from, next){
        let initialisers = [
            utils.fetchOrganisation(to.params.org_id),
            utils.fetchOrganisationPermissions(to.params.org_id)
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.org = data[0];
                vm.myorgperms = data[1];
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
            fetch(helpers.add_endpoint_json(api_endpoints.organisation_contacts,_id)).then(
                async (response) => {
                    if (!response.ok) {
                        throw new Error(`Edit contact failed: ${response.status}`);
                    }
                    this.$refs.add_contact.contact = await response.json();
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
            vm.$refs.contacts_datatable_user.vmDataTable.on('click','.remove-contact',(e) => {
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
                }).then((result) => {
                    if(result.isConfirmed){
                        vm.deleteContact(id);
                    }
                },(error) => {
                    console.log(error);
                });
            });

            vm.$refs.contacts_datatable_user.vmDataTable.on('click','.edit-contact',(e) => {
                e.preventDefault();
                //var id = $(this).attr('data-id');
                //vm.editRequirement(id);
                //let id = $(this).attr('data-edit-id');
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
                    confirmButtonText: 'Accept'
                }).then((result) => {
                    if (result.isConfirmed){
                        fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/accept_user'),{
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(vm.contact_user)
                        }).then(async (response) => {
                            if (!response.ok) {
                                throw new Error(`Contact Accept failed: ${response.status}`);
                            }
                            swal.fire({
                                title: 'Contact Accept',
                                text: 'You have successfully accepted ' + name + '.',
                                icon: 'success',
                                confirmButtonText: 'Okay'
                            }).then(() => {
                                vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                            },(error) => {
                                console.log('Swal error: '+error);
                            });
                        }).catch((error) => {
                            swal.fire('Contact Accept','There was an error accepting ' + name + '.','error')
                            console.log(error?.message || JSON.stringify(error));
                        });
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
                    confirmButtonText: 'Accept'
                }).then((result) => {
                    if (result.isConfirmed){
                        fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/accept_declined_user'),{
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(vm.contact_user)
                        }).then(async (response) => {
                            if (!response.ok) {
                                throw new Error(`Contact Accept (Previously Declined) failed: ${response.status}`);
                            }
                            swal.fire({
                                title: 'Contact Accept (Previously Declined)',
                                text: 'You have successfully accepted ' + name + '.',
                                icon: 'success',
                                confirmButtonText: 'Okay'
                            }).then((result) => {
                                if(result.isConfirmed){
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }
                            },(error) => {
                                console.log(error);
                            });
                        }).catch((error) => {
                            swal.fire('Contact Accept (Previously Declined)','There was an error accepting ' + name + '.','error')
                            console.log(error?.message || JSON.stringify(error));
                        });
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
                    confirmButtonText: 'Accept'
                }).then((result) => {
                    if (result){
                        fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/decline_user'),{
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(vm.contact_user)
                        }).then(async (response) => {
                            if (!response.ok) {
                                throw new Error(`Contact Decline failed: ${response.status}`);
                            }
                            swal.fire({
                                title: 'Contact Decline',
                                text: 'You have successfully declined ' + name + '.',
                                icon: 'success',
                                confirmButtonText: 'Okay'
                            }).then((result) => {
                                if(result.isConfirmed){
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }
                            }).catch((error) => {
                                swal.fire('Contact Decline','There was an error declining ' + name + '.','error');
                                console.log(error?.message || JSON.stringify(error));
                            });
                        }, (error) => {
                            swal.fire('Contact Decline','There was an error declining ' + name + '.','error');
                            console.log(error?.message || JSON.stringify(error));
                        });
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
                    confirmButtonText: 'Accept'
                }).then((result) => {
                    if (result.isConfirmed){
                        fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/unlink_user'),{
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(vm.contact_user)
                        }).then(async (response) => {
                            if (!response.ok) {

                                // Check for specific status code
                                if (response.status === 500) {
                                    swal.fire(
                                        'Unlink',
                                        'Last Organisation Admin cannot be unlinked.',
                                        'error',
                                    );
                                } else {
                                    console.log(JSON.stringify(await response.json()));
                                }

                                throw new Error(`Unlink user failed: ${response.status}`);
                            }

                            swal.fire({
                                title: 'Unlink',
                                text: 'You have successfully unlinked ' + name + '.',
                                icon: 'success',
                                confirmButtonText: 'Okay'
                            }).then((result) => {
                                if(result.isConfirmed){
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }
                            },(error) => {
                                console.log(error);
                            });
                        }).catch((error) => {
                            console.log(error);
                        });
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
                    confirmButtonText: 'Accept'
                }).then((result) => {
                    if (result.isConfirmed) {
                        fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/make_admin_user'),{
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(vm.contact_user)
                        }).then(async (response) => {
                            if (!response.ok) {
                                throw new Error(`Organisation Admin failed: ${response.status}`);
                            }
                            swal.fire({
                                title: 'Organisation Admin',
                                text: 'You have successfully made ' + name + ' an Organisation Admin.',
                                icon: 'success',
                                confirmButtonText: 'Okay'
                            }).then((result) => {
                                if(result.isConfirmed){
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }
                            },(error) => {
                                console.log('Swal error:'+error);
                            });
                        }).catch((error) => {
                            swal.fire('Organisation Admin','There was an error making ' + name + ' an Organisation Admin.','error')
                            console.log(error?.message || JSON.stringify(error));
                        });
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
                    confirmButtonText: 'Accept'
                }).then((result) => {
                    console.log(result);
                    if (result.isConfirmed) {
                        fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/make_user'),{
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(vm.contact_user)
                        }).then(async (response) => {
                            if (!response.ok) {
                                throw new Error(`Company Admin failed: ${response.status}`);
                            }
                            swal.fire({
                                title: 'Organisation User',
                                text: 'You have successfully made ' + name + ' an Organisation User.',
                                icon: 'success',
                                confirmButtonText: 'Okay'
                            }).then((result) => {
                                if(result.isConfirmed){
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }
                            },(error) => {
                                console.log('Swal error:'+error);
                            });
                        }).catch((error) => {
                            swal.fire('Company Admin','There was an error making ' + name + ' an Organisation User.','error')
                            console.log(error?.message || JSON.stringify(error));
                        });
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
                    confirmButtonText: 'Accept'
                }).then((result) => {
                    if (result.isConfirmed) {
                        fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/suspend_user'),{
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(vm.contact_user)
                        }).then(async (response) => {
                            if (!response.ok) {
                                throw new Error(`Suspend User failed: ${response.status}`);
                            }
                            swal.fire({
                                title: 'Suspend User',
                                text: 'You have successfully suspended ' + name + ' as a User.',
                                icon: 'success',
                                confirmButtonText: 'Okay'
                            }).then((result) => {
                                if(result.isConfirmed){
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }
                            },(error) => {
                                console.log('Swal error:'+error);
                            });
                        }).catch((error) => {
                            swal.fire('Suspend User','There was an error suspending ' + name + ' as a User.','error')
                            console.log(error?.message || JSON.stringify(error));
                        });
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
                    confirmButtonText: 'Accept'
                }).then((result) => {
                    if (result.isConfirmed) {
                        fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/reinstate_user'),{
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(vm.contact_user)
                        }).then(async (response) => {
                            if (!response.ok) {
                                throw new Error(`Reinstate User failed: ${response.status}`);
                            }
                            swal.fire({
                                title: 'Reinstate User',
                                text: 'You have successfully reinstated ' + name + '.',
                                icon: 'success',
                                confirmButtonText: 'Okay'
                            }).then((result) => {
                                if(result.isConfirmed){
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }
                            },(error) => {
                                console.log('Swal error:'+error);
                            });
                        }).catch((error) => {
                            swal.fire('Reinstate User','There was an error reinstating ' + name + '.','error')
                            console.log(error?.message || JSON.stringify(error));
                        });
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
                    confirmButtonText: 'Accept'
                }).then((result) => {
                    if (result.isConfirmed) {
                        fetch(helpers.add_endpoint_json(api_endpoints.organisations,vm.org.id+'/relink_user'),{
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(vm.contact_user)
                        }).then(async (response) => {
                            if (!response.ok) {
                                throw new Error(`Relink User failed: ${response.status}`);
                            }
                            swal.fire({
                                title: 'Relink User',
                                text: 'You have successfully relinked ' + name + '.',
                                icon: 'success',
                                confirmButtonText: 'Okay'
                            }).then((result) => {
                                if(result.isConfirmed){
                                    vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                }
                            },(error) => {
                                console.log('Swal error:'+error);
                            });
                        }).catch((error) => {
                            swal.fire('Relink User','There was an error relink ' + name + '.','error')
                            console.log(error?.message || JSON.stringify(error));
                        });
                    }
                },(error) => {
                    console.log(error);
                });
            });
        },
        updateDetails: function(show_alert) {
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
                    throw new Error(`Save Organisation details failed: ${response.status}`);
                }
                vm.updatingDetails = false;
                vm.org = await response.json();
                if (vm.org.address == null){ vm.org.address = {}; }
                if (show_alert || show_alert==null) {
                    swal.fire(
                        'Saved',
                        'Organisation details have been saved',
                        'success'
                    )
                } else {
                    console.log('Org: ' + JSON.stringify(vm.org));
                }
            }, (error) => {
                console.log(error.message);
                var text= error.message;
                // var text= helpers.apiVueResourceError(error);
                if(typeof text == 'object'){
                    if (Object.prototype.hasOwnProperty.call(text, 'email')) {
                        text=text.email[0];
                    }
                }
                swal.fire(
                    'Error', 
                    'Organisation details cannot be saved because of the following error: '+text,
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
            
            fetch(helpers.add_endpoint_json(api.organisation_contacts,id),{
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(async (response) => {
                if (!response.ok) {
                    throw new Error(`Contact Deletion failed: ${response.status}`);
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
                    'Contact Deletion',
                    errorMessage,
                    'error'
                );
            })
        },
        updateContact: function(id){
            let vm = this;
            
            fetch(helpers.add_endpoint_json(api.organisation_contacts,id),{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
            }).then(async (response) => {
                if (!response.ok) {
                   throw new Error(`Contact Edit failed: ${response.status}`);
                }
                swal.fire(
                    'Update Contact', 
                    'The contact was successfully updated',
                    'success'
                )
                vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
            }).catch((error) => {
                console.log(error.message);
                var text= error.message;
                swal.fire(
                    'Contact Edit', 
                    'The contact could not be updated because of the following error : [' + text + ']',
                    'error'
                )
            });
        },

        updateAddress: function(show_alert) {
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
                    throw new Error(`Save Address Details failed: ${response.status}`);
                }
                vm.updatingAddress = false;
                vm.org = await response.json();
                if (show_alert || show_alert==null) {
                    swal.fire(
                        'Saved',
                        'Address details have been saved',
                        'success'
                    )
                } else {
                    console.log('Org: ' + JSON.stringify(vm.org));
                }
                if (vm.org.address == null){ vm.org.address = {}; }
            }).catch((error) => {
                console.log(error.message);
                vm.updatingAddress = false;
            });
        },
        unlinkUser: function(d){
            let vm = this;
            let org = vm.org;
            let org_name = org.name;
            let person = helpers.copyObject(d);
            swal.fire({
                title: "Unlink From Organisation",
                text: "Are you sure you want to unlink "+person.name+" "+person.id+" from "+org.name+" ?",
                icon: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then((result) => {
                if(result.isConfirmed){
                    fetch(helpers.add_endpoint_json(api_endpoints.organisations,org.id+'/unlink_user'),{
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ user: person.id })
                    }).then(async (response) => {
                        if (!response.ok) {
                            throw new Error(`Unlink User failed: ${response.status}`);
                        }
                        const data = await response.json();
                        vm.org = data;
                        if (vm.org.address == null){ vm.org.address = {}; }
                        swal.fire(
                            'Unlink',
                            'You have successfully unlinked '+person.name+' from '+org_name+'.',
                            'success'
                        )
                    }).catch((error) => {

                        swal.fire(
                            'Unlink',
                            'There was an error unlinking '+person.name+' from '+org_name+'. '+error?.message || JSON.stringify(error),
                            'error'
                        )
                    });
                }
            },(error) => {
                console.log(error);
            }); 
        }
    },
    mounted: function(){
        this.personal_form = document.forms.personal_form;
        let vm=this;
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchOrganisation(vm.org_id),
            utils.fetchOrganisationPermissions(vm.org_id)
        ]
        Promise.all(initialisers).then(data => {
                vm.countries = data[0];
                vm.org = data[1];
                vm.myorgperms = data[2];
                vm.org.address = vm.org.address != null ? vm.org.address : {};
                vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
            
        })
        .catch(error => {
            console.error("Error fetching organisation details:", error);
        });

    },
    updated: function(){
        // let vm = this;
        $('.panelClicker[data-toggle="collapse"]').on('click', function () {
            var chev = $(this).children()[0];
            window.setTimeout(function () {
                $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
            },100);
        }); 
        this.$nextTick(() => {
            if (this.show_linked) {
                this.eventListeners();
            }
        });
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.top-buffer-s {
    margin-top: 25px;
}
</style>
