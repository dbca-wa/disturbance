<template lang="html">
    <div>
        <div class="row col-sm-12">
            <div v-if="loading_sites" class="spinner_on_map">
                <i class='fa fa-4x fa-spinner fa-spin'></i>
            </div>
            <ComponentMap
                ref="component_map"
                :is_internal="is_internal"
                :is_external="is_external"
                :apiary_site_geojson_array="apiary_site_geojson_array"
                :key="component_map_key"
                @featuresDisplayed="updateTableByFeatures"
                :can_modify="can_modify"
                :display_at_time_of_submitted="show_col_status_when_submitted"
                @featureGeometryUpdated="featureGeometryUpdated"
                @popupClosed="popupClosed"
            />
        </div>
        <div class="row col-sm-12">
            <datatable
                ref="table_apiary_site"
                :id="table_id"
                :dtOptions="dtOptions"
                :dtHeaders="dtHeaders"
            />
            <template v-if="show_view_all_features_button">
                <div class="button_row">
                    <span class="view_all_button" @click="displayAllFeatures">View All On Map</span>
                </div>
            </template>
        </div>

    </div>
</template>

<script>
    import datatable from '@vue-utils/datatable.vue'
    import { v4 as uuidv4 } from 'uuid';
    import ComponentMap from '@/components/common/apiary/component_map.vue'
    import { getDisplayNameFromStatus, getStatusForColour, SiteColours } from '@/components/common/apiary/site_colours.js'

    export default {
        props:{
            apiary_approval_id: {
                type: Number,
                default: 0,
            },
            apiary_proposal_id: {
                type: Number,
                default: 0,
            },
            apiary_sites: {
                type: Array,
                default: function(){
                    return [];
                }
            },
            is_external:{
                type: Boolean,
                default: false,
            },
            is_internal:{
                type: Boolean,
                default: false,
            },
            table_and_map_in_a_row: {
                type: Boolean,
                default: true,
            },
            show_col_id: {
                type: Boolean,
                default: false,
            },
            show_col_checkbox: {
                type: Boolean,
                default: true,
            },
            enable_col_checkbox: {
                type: Boolean,
                default: true,
            },
            show_col_site: {
                type: Boolean,
                default: true,
            },
            show_col_site_when_submitted: {
                type: Boolean,
                default: false,
            },
            show_col_longitude: {
                type: Boolean,
                default: false,
            },
            show_col_latitude: {
                type: Boolean,
                default: false,
            },
            show_col_district: {
                type: Boolean,
                default: false,
            },
            show_col_status: {
                type: Boolean,
                default: false,
            },
            show_col_status_when_submitted: {
                type: Boolean,
                default: false,
            },
            show_col_previous_site_holder: {
                type: Boolean,
                default: false,
            },
            show_col_action: {
                type: Boolean,
                default: true,
            },
            show_col_vacant: {
                type: Boolean,
                default: false,
            },
            show_col_vacant_when_submitted: {
                type: Boolean,
                default: false,
            },
            show_col_decision:{
                type: Boolean,
                default: false,
            },
            apiary_licensed_sites: {
                type: Array,
                default: function(){
                    return [];
                }
            },
            show_col_licensed_site:{
                type: Boolean,
                default: false,
            },
            show_col_licensed_site_checkbox: {
                type: Boolean,
                default: false,
            },
            enable_col_licensed_site_checkbox: {
                type: Boolean,
                default: true,
            },

            show_view_all_features_button: {
                type: Boolean,
                default: true,
            },
            show_action_available_unavailable: {
                type: Boolean,
                default: false,
            },
            show_action_make_vacant: {
                type: Boolean,
                default: false,
            },
            show_action_contact_licence_holder: {
                type: Boolean,
                default: false,
            },
            can_modify: {
                type: Boolean,
                default: false,
            }
        },
        data: function(){
            let vm = this;
            return{
                selectAllCheckboxes: false,
                apiary_sites_local: JSON.parse(JSON.stringify(this.apiary_sites)),  // Deep copy the array
                component_map_key: '',
                table_id: uuidv4(),
                apiary_site_geojson_array: [],  // This is passed to the ComponentMap as props
                default_checkbox_checked: false,  // If checked property isn't set as a apiary_site's property, this default value is used
                popup_opened_by_link: false,
                loading_sites: false,
                dtHeaders: [
                    'Id',
                    '',
                    'Site',
                    'Site',  // coloured by the status when submitted
                    'Longitude',
                    'Latitude',
                    'District',
                    'Licensed site',
                    'Status',
                    'Status<br>(at time of submit)',
                    'Vacant<br>(current status)',  // current status of the 'is_vacant'
                    'Vacant<br>(at time of submit)',  // status of the 'is_vacant' when the application submitted
                    'Decision',
                    'Previous Site Holder<br>Applicant',
                    'Action',
                ],
                dtOptions: {
                    serverSide: false,
                    searching: false,
                    searchDelay: 1000,
                    lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                    order: [
                        [1, 'desc'], [0, 'desc'],
                    ],
                    language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },
                    responsive: true,
                    processing: true,
                    createdRow: function(row, data, index){
                        $(row).attr('data-apiary-site-id', data.id)
                    },
                    columns: [
                        {
                            // Id (database id)
                            visible: vm.show_col_id,
                            mRender: function (data, type, apiary_site) {
                                return apiary_site.id;
                            }
                        },
                        {
                            // Checkbox
                            visible: vm.show_col_checkbox,
                            className: 'dt-body-center',
                            mRender: function (data, type, apiary_site) {
                                let disabled_str = ''
                                if (!vm.enable_col_checkbox){
                                    disabled_str = ' disabled '
                                }
                                if (apiary_site.checked){
                                    return '<input type="checkbox" class="site_checkbox" data-apiary-site-id="' + apiary_site.id + '"' + disabled_str + ' checked/>'
                                } else {
                                    return '<input type="checkbox" class="site_checkbox" data-apiary-site-id="' + apiary_site.id + '"' + disabled_str + '/>'
                                }
                            }
                        },
                        {
                            // Site (current): general status. Marker
                            visible: vm.show_col_site,
                            mRender: function (data, type, apiary_site) {
                                let status_for_colour = getStatusForColour(apiary_site, false)
                                let fillColour = SiteColours[status_for_colour].fill
                                let strokeColour = SiteColours[status_for_colour].stroke
                                let sub_str = ''

                                if (status_for_colour === 'denied'){
                                    sub_str = '<svg height="20" width="20">' +
                                        '<line x1="4" y1="4" x2="16" y2="16" stroke="' + strokeColour + '" + stroke-width="2" />' +
                                        '<line x1="4" y1="16" x2="16" y2="4" stroke="' + strokeColour + '" + stroke-width="2" />' +
                                           '</svg> site: ' + apiary_site.id
                                } else {
                                    sub_str = '<svg height="20" width="20">' +
                                                '<circle cx="10" cy="10" r="6" stroke="' + strokeColour + '" stroke-width="2" fill="' + fillColour + '" />' +
                                           '</svg> site: ' + apiary_site.id
                                }
                                return '<div data-site="' + apiary_site.id + '">' + sub_str + '</div>'
                            }
                        },


                        {
                            // Site (at time of submit): pending/vacant
                            visible: vm.show_col_site_when_submitted,
                            mRender: function (data, type, apiary_site){
                                let status_when_submitted = 'pending'
                                if (apiary_site.properties.apiary_site_is_vacant_when_submitted){
                                    status_when_submitted = 'vacant'
                                }
                                let fillColour = SiteColours[status_when_submitted].fill
                                let strokeColour = SiteColours[status_when_submitted].stroke
                                let sub_str = '<svg height="20" width="20">' +
                                            '<circle cx="10" cy="10" r="6" stroke="' + strokeColour + '" stroke-width="2" fill="' + fillColour + '" />' +
                                          '</svg> site: ' + apiary_site.id
                                return '<div data-site="' + apiary_site.id + '">' + sub_str + '</div>'
                            }
                        },
                        {
                            // Longitude
                            visible: vm.show_col_longitude,
                            mRender: function (data, type, apiary_site){
                                return 'lng'
                            }
                        },
                        {
                            // Latitude
                            visible: vm.show_col_latitude,
                            mRender: function (data, type, apiary_site){
                                return 'lat'
                            }
                        },
                        {
                            // District
                            visible: vm.show_col_district,
                            mRender: function (data, type, apiary_site){
                                return 'dist'
                            }
                        },
                        {
                            // Licenced Site Checkbox - show column, default unchecked
                            visible: vm.show_col_licensed_site,
                            className: 'dt-body-center',
                            mRender: function (data, type, apiary_site) {
                                let disabled_str = ''
                                if (!vm.enable_col_licensed_site_checkbox){
                                    disabled_str = ' disabled '
                                }
                                if (apiary_site.properties.licensed_site){
                                    return '<input type="checkbox" class="licensed_site_checkbox" data-apiary-licensed-site-id="' + apiary_site.id + '"' + disabled_str + ' checked/>'
                                } else {
                                    return '<input type="checkbox" class="licensed_site_checkbox" data-apiary-licensed-site-id="' + apiary_site.id + '"' + disabled_str + '/>'
                                }
                            }
                        },


                        {
                            // Status (current): general status.  Text
                            visible: vm.show_col_status,
                            mRender: function (data, type, apiary_site){
                                let dynamic_status = getStatusForColour(apiary_site, false)
                                let display_name = getDisplayNameFromStatus(dynamic_status)
                                return display_name
                            }
                        },
                        {
                            // Status (at time of submit): pending/vacant
                            visible: vm.show_col_status_when_submitted,
                            mRender: function (data, type, apiary_site){
                                let status = 'pending'
                                let is_vacant = apiary_site.properties.apiary_site_is_vacant_when_submitted
                                if(is_vacant === true){
                                    status = 'vacant'
                                }
                                return getDisplayNameFromStatus(status)
                            }

                        },
                        {
                            // Vacant (current): yes/no
                            visible: vm.show_col_vacant,
                            mRender: function (data, type, apiary_site) {
                                let status = apiary_site.properties.status
                                let is_vacant = apiary_site.properties.is_vacant
                                if(status === 'vacant' || is_vacant === true){
                                    return '<i class="fa fa-check" aria-hidden="true"></i>'
                                }
                                return ''
                            }
                        },
                        {
                            // Vacant (at time of submit): yes/no
                            visible: vm.show_col_vacant_when_submitted,
                            mRender: function (data, type, apiary_site) {
                                let status = apiary_site.properties.status
                                let is_vacant = apiary_site.properties.apiary_site_is_vacant_when_submitted
                                if(is_vacant === true){
                                    return '<i class="fa fa-check" aria-hidden="true"></i>'
                                }
                                return ''
                            }
                        },
                        {
                            visible: vm.show_col_decision,
                            mRender: function (data, type, apiary_site) {
                                let status = apiary_site.properties.status
                                if (status == 'approved'){
                                    let myColour = SiteColours['approved'].fill
                                    return '<i class="fa fa-check" aria-hidden="true" style="color:' + myColour + ';"></i> Approved'
                                } else if (status == 'denied'){
                                    let myColour = SiteColours['denied'].stroke
                                    let sub_str =  '<i class="fa fa-times" aria-hidden="true" style="color:' + myColour + ';"></i> Denied'
                                    return sub_str
                                } else {
                                    return ''
                                }
                            }
                        },
                        {
                            // Previous Site Holder/Applicant
                            visible: vm.show_col_previous_site_holder,
                            mRender: function (data, type, apiary_site){
                                return apiary_site.properties.previous_site_holder_or_applicant
                            }
                        },
                        {
                            // Action
                            mRender: function (data, type, apiary_site) {
                                let action_list = []

                                // View on map
                                let view_on_map_html = '<a href="#' + apiary_site.id + '" data-view-on-map="' + apiary_site.id + '">View on map</a>';
                                action_list.push(view_on_map_html);

                                if (vm.show_action_available_unavailable){
                                    // Mark as Available/Unavailable
                                    let display_text = ''
                                    if (vm.is_external && ['current',].includes(apiary_site.properties.status.toLowerCase())){
                                        if (apiary_site.properties.available){
                                            display_text = 'Mark as unavailable';
                                        } else {
                                            display_text = 'Mark as available';
                                        }
                                        let ret = '<a data-toggle-availability="' + apiary_site.id + '" data-apiary-site-available="' + apiary_site.properties.available + '">' + display_text + '</a>';
                                        action_list.push(ret);
                                    //} else if (vm.is_internal && ['Current', 'current'].includes(apiary_site.status.id)){
                                    } else if (vm.is_internal && ['current',].includes(apiary_site.properties.status.toLowerCase())){
                                        if (apiary_site.properties.available){
                                            display_text = 'Available';
                                        } else {
                                            display_text = 'Unavailable';
                                        }
                                        action_list.push(display_text);
                                    }
                                }
                                if (vm.show_action_make_vacant){
                                    let display_text = 'Make Vacant'
                                    let ret = '<a data-make-vacant="' + apiary_site.id + '">' + display_text + '</a>';
                                    action_list.push(ret);
                                }
                                if (vm.show_action_contact_licence_holder){
                                    let display_text = 'Contact licence holder'
                                    let ret = '<a data-contact-licence-holder="' + apiary_site.id + '">' + display_text + '</a>';
                                    action_list.push(ret);
                                }
                                return action_list.join('<br />');
                            }
                        },
                    ],
                },
            }
        },
        created: function(){
            let vm = this;
            if (vm.apiary_proposal_id){
                vm.loading_sites = true
                let url_sites = '/api/proposal_apiary/' + vm.apiary_proposal_id + '/apiary_sites/'
                Vue.http.get(url_sites).then(
                    (res) => {
                        vm.apiary_sites = res.body
                        vm.apiary_sites_local = JSON.parse(JSON.stringify(vm.apiary_sites)),  // Deep copy the array
                        vm.constructApiarySitesTable(res.body);
                        vm.addApiarySitesToMap(res.body)
                        vm.ensureCheckedStatus();
                        vm.loading_sites = false
                    },
                    (err) => {
                        vm.loading_sites = false
                    }
                )
            } else if (vm.apiary_approval_id){
                vm.loading_sites = true
                // Retrieve apiary_sites
                let url_sites = '/api/approvals/' + vm.apiary_approval_id + '/apiary_sites/'
                Vue.http.get(url_sites).then(
                    (res) => {
                        vm.apiary_sites = res.body.features
                        vm.apiary_sites_local = JSON.parse(JSON.stringify(vm.apiary_sites)),  // Deep copy the array
                        vm.constructApiarySitesTable(res.body.features);
                        vm.addApiarySitesToMap(res.body.features)
                        vm.ensureCheckedStatus();
                        vm.loading_sites = false
                    },
                    (err) => {
                        vm.loading_sites = false
                    }
                )
            }
        },
        mounted: function(){
            let vm = this;
            vm.$nextTick(() => {
                vm.addEventListeners();
                if (!vm.apiary_approval_id && !vm.apiary_proposal_id){
                    // apiary_approval_id and apiary_proposal_id are not provided, which means apiary_sites have been already provided
                    vm.constructApiarySitesTable(vm.apiary_sites);
                    vm.addApiarySitesToMap(vm.apiary_sites)
                    vm.ensureCheckedStatus();
                }
            });
            vm.$emit('apiary_sites_updated', vm.apiary_sites_local)
        },
        components: {
            ComponentMap,
            datatable,
        },
        computed: {


        },
        methods: {
            popupClosed: function(){
                this.not_close_popup_by_mouseleave = false
            },
            featureGeometryUpdated: function(feature){
                this.$emit('featureGeometryUpdated', feature)
            },
            updateTableByFeatures: function(features) {

                // Generate a list of the feature ids displayed on the map
                let ids = $.map(features, function(feature){
                    return feature.id_
                })

                // Generate a list of apiary_sites whose ids are in the list generated above
                let apiary_sites_filtered = this.apiary_sites_local.filter(function(apiary_site){
                    return ids.includes(apiary_site.id)
                })

                // Update the table
                this.constructApiarySitesTable(apiary_sites_filtered)
            },
            ensureCheckedStatus: function() {
                if (this.apiary_sites.length > 0){
                    for(let i=0; i<this.apiary_sites.length; i++){
                        if (!this.apiary_sites[i].hasOwnProperty('checked')){
                            this.apiary_sites[i].checked = this.default_checkbox_checked
                        }
                    }
                }
            },
            forceToRefreshMap: function() {
                if (this.$refs.component_map){
                    this.$refs.component_map.forceToRefreshMap()
                }
            },
            displayAllFeatures: function(){
                if (this.$refs.component_map){
                    this.$refs.component_map.displayAllFeatures()
                }
            },
            addApiarySitesToMap: function(apiary_sites) {
                for (let i=0; i<apiary_sites.length; i++){
                    if (apiary_sites[i].hasOwnProperty('checked')){
                        //apiary_sites[i].as_geojson['properties']['checked'] = apiary_sites[i].checked
                        //apiary_sites[i].as_geojson.properties.checked = apiary_sites[i].checked
                        apiary_sites[i].properties.checked = apiary_sites[i].checked
                    }
                    //this.apiary_site_geojson_array.push(apiary_sites[i].as_geojson)
                    this.apiary_site_geojson_array.push(apiary_sites[i])
                }

                // Reload ComponentMap by assigning a new key value
                this.component_map_key = uuidv4()
            },
            constructApiarySitesTable: function(apiary_sites) {
                if (this.$refs.table_apiary_site){
                    // Clear table
                    this.$refs.table_apiary_site.vmDataTable.clear();

                    // Construct table
                    if (apiary_sites.length > 0){
                        for(let i=0; i<apiary_sites.length; i++){
                            this.addApiarySiteToTable(apiary_sites[i]);
                        }
                        if (apiary_sites.length > 1){
                            // add "select all checkbox"
                            let colOne = this.$refs.table_apiary_site.vmDataTable.column(1).header()
                            if (this.selectAllCheckboxes) {
                                $(colOne).html(
                                    `<input type="checkbox" class="select_all_checkbox" checked/>`
                                    )
                            } else {
                                $(colOne).html(
                                    `<input type="checkbox" class="select_all_checkbox"/>`
                                    )
                            }
                        }
                    }
                    this.$refs.table_apiary_site.vmDataTable.draw();
                }
            },
            addApiarySiteToTable: function(apiary_site) {
                //this.$refs.table_apiary_site.vmDataTable.row.add(apiary_site).draw();
                this.$refs.table_apiary_site.vmDataTable.row.add(apiary_site);
            },
            addEventListeners: function () {
                $("#" + this.table_id).on("click", "a[data-view-on-map]", this.zoomOnApiarySite)
                $("#" + this.table_id).on("click", "a[data-toggle-availability]", this.toggleAvailability)
                //$("#" + this.table_id).on('click', 'input[type="checkbox"]', this.checkboxClicked)
                $("#" + this.table_id).on('click', 'input[class="site_checkbox"]', this.checkboxClicked)
                $("#" + this.table_id).on('click', 'input[class="licensed_site_checkbox"]', this.checkboxLicensedSiteClicked)
                $("#" + this.table_id).on('click', 'input[class="select_all_checkbox"]', this.checkboxSelectAll)
                $("#" + this.table_id).on('click', 'a[data-make-vacant]', this.makeVacantClicked)
                $("#" + this.table_id).on('click', 'a[data-contact-licence-holder]', this.contactLicenceHolder)

                $("#" + this.table_id).on('mouseenter', "tr", this.mouseEnter)
                $("#" + this.table_id).on('mouseleave', "tr", this.mouseLeave)
            },
            updateApiarySite: function(site_updated) {
                // Update internal apiary_site data
                for (let i=0; i<this.apiary_sites.length; i++){
                    if (this.apiary_sites[i].id == site_updated.id){
                        //this.apiary_sites[i].available = site_updated.properties.available
                        this.apiary_sites[i] = site_updated
                    }
                }
            },
            removeApiarySiteById: function(site_id){
                // Remove a site for the array which the table is created based on.
                let array_index_removed = null
                for (let i=0; i<this.apiary_sites.length; i++){
                    if (this.apiary_sites[i].id == site_id){
                        array_index_removed = i
                        break
                    }
                }
                if (array_index_removed >= 0){
                    this.apiary_sites.splice(array_index_removed, 1)
                }
            },
            checkboxClicked: function(e) {
                let vm = this;
                //let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let apiary_site_id = this.getApiarySiteIdFromEvent(e)
                let checked_status = e.target.checked
                for (let i=0; i<this.apiary_sites_local.length; i++){
                    if (this.apiary_sites_local[i].id == apiary_site_id){
                        this.apiary_sites_local[i].checked = checked_status
                    }
                }
                this.$emit('apiary_sites_updated', this.apiary_sites_local)
                this.$refs.component_map.setApiarySiteSelectedStatus(apiary_site_id, checked_status)
                e.stopPropagation()
            },
            checkboxLicensedSiteClicked: function(e) {
                let vm = this;
                //let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let apiary_site_id = this.getApiaryLicensedSiteIdFromEvent(e)
                let checked_status = e.target.checked
                for (let i=0; i<this.apiary_sites_local.length; i++){
                    if (this.apiary_sites_local[i].id == apiary_site_id){
                        //this.apiary_sites_local[i].licensed_site_checked = checked_status
                        this.apiary_sites_local[i].properties.licensed_site = checked_status
                    }
                }
                this.$emit('apiary_sites_updated', this.apiary_sites_local)
                this.$refs.component_map.setApiarySiteSelectedStatus(apiary_site_id, checked_status)
                e.stopPropagation()
            },
            checkboxSelectAll: async function(e) {
                //e.preventDefault()
                this.selectAllCheckboxes = e.target.checked
                for (let i=0; i<this.apiary_sites_local.length; i++){
                    let apiarySite = Object.assign({}, this.apiary_sites_local[i])
                    apiarySite.checked = this.selectAllCheckboxes
                    Vue.set(this.apiary_sites_local, i, apiarySite)
                    this.$refs.component_map.setApiarySiteSelectedStatus(this.apiary_sites_local[i].id, this.selectAllCheckboxes)
                }
                this.$emit('apiary_sites_updated', this.apiary_sites_local)
                this.constructApiarySitesTable(this.apiary_sites_local);
                e.stopPropagation()
            },
            contactLicenceHolder: function(e){
                let vm = this;
                //let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let apiary_site_id = e.target.getAttribute("data-contact-licence-holder");

                this.$emit('contact-licence-holder-clicked', apiary_site_id)
                e.stopPropagation()
            },
            makeVacantClicked: function(e) {
                let vm = this;
                //let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                let apiary_site_id = e.target.getAttribute("data-make-vacant");
                e.stopPropagation()

                swal({
                    title: "Make Vacant",
                    text: "Are you sure you want to make this apiary site: " + apiary_site_id + " vacant?",
                    type: "question",
                    showCancelButton: true,
                    confirmButtonText: 'Yes, make vacant'
                }).then(
                    () => {
                        vm.$http.patch('/api/apiary_site/' + apiary_site_id + '/', { 'status': 'vacant' }).then(
                            async function(accept){
                                // Remove the row from the table
                                $(e.target).closest('tr').fadeOut('slow', function(){
                                    // Remove the site table which the table is based on
                                    vm.removeApiarySiteById(apiary_site_id)
                                })

                                // Remove the site from the map
                                this.$refs.component_map.removeApiarySiteById(apiary_site_id)
                                //vm.component_map_key = uuidv4()
                            },
                            reject=>{
                                swal(
                                    'Submit Error',
                                    helpers.apiVueResourceError(err),
                                    'error'
                                )
                            }
                        );
                    },
                    err => {
                    }
                );
            },
            mouseEnter: function(e){
                let vm = this;
                if (!vm.not_close_popup_by_mouseleave){
                    let apiary_site_id = e.currentTarget.getAttribute("data-apiary-site-id");
                    if (apiary_site_id){
                        vm.$refs.component_map.showPopupById(apiary_site_id)
                    }
                }
            },
            mouseLeave: function(e){
                let vm = this;
                if (!vm.not_close_popup_by_mouseleave){
                    vm.$refs.component_map.closePopup()
                }
            },
            toggleAvailability: function(e) {
                let vm = this;
                let apiary_site_id = e.target.getAttribute("data-toggle-availability");
                let current_availability = this.getApiarySiteAvailableFromEvent(e)
                let requested_availability = current_availability === 'true' ? false : true
                e.stopPropagation()

                vm.$http.patch('/api/apiary_site/' + apiary_site_id + '/', { 'available': requested_availability }).then(
                    async function(accept){
                        // Update the site in the table
                        let site_updated = accept.body
                        vm.updateApiarySite(site_updated)
                       // vm.constructApiarySitesTable();
                        vm.constructApiarySitesTable(vm.apiary_sites);
                    },
                    reject=>{
                        swal(
                            'Submit Error',
                            helpers.apiVueResourceError(err),
                            'error'
                        )
                    }
                );
            },
            zoomOnApiarySite: function(e) {
                this.not_close_popup_by_mouseleave = true

                let apiary_site_id = e.target.getAttribute("data-view-on-map");
                this.$refs.component_map.zoomToApiarySiteById(apiary_site_id)
                e.stopPropagation()
            },
            getApiarySiteIdFromEvent(e){
                let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                if (!(apiary_site_id)){
                    apiary_site_id = e.target.getElementsByTagName('span')[0].getAttribute('data-apiary-site-id')
                }
                return apiary_site_id
            },
            getApiaryLicensedSiteIdFromEvent(e){
                let apiary_site_id = e.target.getAttribute("data-apiary-licensed-site-id");
                if (!(apiary_site_id)){
                    apiary_site_id = e.target.getElementsByTagName('span')[0].getAttribute('data-apiary-licensed-site-id')
                }
                return apiary_site_id
            },
            getApiarySiteAvailableFromEvent(e){
                let apiary_site_available = e.target.getAttribute("data-apiary-site-available");

                if (!(apiary_site_available)){
                    apiary_site_available = e.target.getElementsByTagName('span')[0].getAttribute('data-apiary-site-available')
                }

                return apiary_site_available
            }
        },
    }
</script>

<style lang="css" scoped>
.component-site-selection {
    border: solid 2px #5BB;
}
.button_row {
    display: flex;
    justify-content: flex-end;
}
.view_all_button {
    color: #03a9f4;
    cursor: pointer;
}
.site_checkbox {
    text-align: center;
}
.licensed_site_checkbox {
    text-align: center;
}
.spinner_on_map {
    position: absolute;
    top: 10%;
    left: 50%;
    z-index: 100000;
}
</style>
