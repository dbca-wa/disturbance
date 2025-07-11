<template lang="html">
    <div>
        <div class="form-group"><div class="row">
            <label class="col-sm-2">Period From</label>
            <div class="col-sm-4">
                <div class="input-group date" ref="periodFromDatePicker">
                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" id="period_from_input_element" :readonly="is_readonly"/>
                    <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                    </span>
                </div>
            </div>
        </div></div>

        <div class="form-group"><div class="row">
            <label class="col-sm-2">Period To</label>
            <div class="col-sm-4">
                <div class="input-group date" ref="periodToDatePicker">
                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" id="period_to_input_element" :readonly="is_readonly"/>
                    <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                    </span>
                </div>
            </div>
        </div></div>
    </div>
</template>

<script>
    import { v4 as uuidv4 } from 'uuid';

    export default {
        name: 'SectionPeriodAndSites',
        props:{
            // If editing an existing proposal apiary temporary use, data is passed from the parent component
            from_date: {
                type: Object, // Expect moment obj
                default: null,
            },
            // If editing an existing proposal apiary temporary use, data is passed from the parent component
            to_date: {
                type: Object, // Expect moment obj
                default: null,
            },
            // array of intermediate table, TemporaryUseApiarySite
            temporary_use_apiary_sites: {
                type: Array,
                default: function(){
                    return [];
                }
            },
            // all the ProposalApiaryTemporaryUse use objects under this licence
            // to be used to calculate each apirary site availability at any moment given
            existing_temporary_uses: {
                type: Array,
                default: function(){
                    return [];
                }
            },
            is_external:{
              type: Boolean,
              default: false
            },
            is_internal:{
              type: Boolean,
              default: false
            },
            is_readonly: {
              type: Boolean,
              default: true
            },
            customer_status: {
                type: String,
                default: ''
            },
            processing_status: {
                type: String,
                default: ''
            }
        },
        data:function () {
            let vm=this;
            return{
                component_site_selection_key: '',
                period_from: '',
                period_to: '',
                //period_from_enabled: false,
                //period_to_enabled: false,
                apiary_sites: [],  // Used to construct the sites table
                                                 // Array of TemporaryUseApiarySite objects
            }
        },
        created: function() {
            // Copy the values from props (it is not allowd to change props' value)
            if (this.from_date){
                if (this.from_date instanceof moment) {
                    this.period_from = this.from_date.format('DD/MM/YYYY');
                } else {
                    // Wrong type of object, clear it
                    console.warn('The value passed to from_date is wrong type');
                    this.period_from = null;
                }
            }
            if (this.to_date){
                if (this.to_date instanceof moment) {
                    this.period_to = this.to_date.format('DD/MM/YYYY');
                } else {
                    // Wrong type of object, clear it
                    console.warn('The value passed to to_date is wrong type');
                    this.period_to = null;
                }
            }
            if (this.temporary_use_apiary_sites.length > 0){
                for (let i=0; i<this.temporary_use_apiary_sites.length; i++){
                    //let site = this.temporary_use_apiary_sites[i].apiary_site
                    let site = this.temporary_use_apiary_sites[i].apiary_site

                    // Add the status of the checkbox for this apiary site if needed
                    // otherwise the default status is unchecked
                    site.checked = this.temporary_use_apiary_sites[i].selected

                    this.apiary_sites.push(site)
                }
            }
            //this.period_from_enabled = this.from_date_enabled;
            //this.period_to_enabled = this.to_date_enabled;
            this.component_site_selection_key = uuidv4()
        },
        components: {
        },
        computed:{
            is_checkbox_enabled: function() {
                let enabled = false
                if(this.is_external){
                    if(['Draft', 'draft'].includes(this.customer_status)){
                        enabled = true
                    }
                }
                return enabled
            }
        },
        methods:{
            apiarySitesUpdated: function(apiary_sites){
                console.log(apiary_sites)
                this.$emit('apiary_sites_updated', apiary_sites)
            },
            //viewSiteOnMap: function(e){
            //    let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
            //    console.log('view site-id: ' + apiary_site_id + ' on the map');
            //},
            //siteCheckboxClicked: function(e){
            //    let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
            //    this.$emit('site_checkbox_clicked', {
            //        'apiary_site_id': apiary_site_id,
            //        'checked': e.target.checked
            //    });
            //},
            //constructApiarySitesTable: function(){
            //    // Clear table
            //    this.$refs.apiary_sites_table.vmDataTable.clear().draw();

            //    // Construct table
            //    if (this.apiary_sites.length > 0){
            //        for(let i=0; i<this.apiary_sites.length; i++){
            //            this.addApiarySiteToTable(this.apiary_sites[i]);
            //        }
            //    }
            //},
            //addApiarySiteToTable: function(temporary_use_apiary_site) {
            //    console.log('in addApiarySiteToTable');
            //    //apiary_site['_site_used'] = false  // Make the site be temporary usable
            //    //apiary_site['_from_and_to_date_set'] = false

            //    if (this.period_from && this.period_to){
            //        // Only when from and to dates are set
            //        //apiary_site['_from_and_to_date_set'] = true

            //    //    outer_loop:
            //    //    for (let i=0; i<this.existing_temporary_uses.length; i++){
            //    //        // Check the usability to each existing temporary_use object
            //    //        let temp_use = this.existing_temporary_uses[i];

            //    //        for (let j=0; j<temp_use.apiary_sites.length; j++){
            //    //            let item_in_inter_table = temp_use.apiary_sites[j];

            //    //            if (item_in_inter_table.apiary_site.id == apiary_site.id){
            //    //                // Check the availability of the site
            //    //                let used_from_date = moment(temp_use.from_date, 'YYYY-MM-DD');
            //    //                let used_to_date = moment(temp_use.to_date, 'YYYY-MM-DD');
            //    //                let period_from = moment(this.period_from, 'DD/MM/YYYY');
            //    //                let period_to = moment(this.period_to, 'DD/MM/YYYY');

            //    //                console.log('used_from_date');
            //    //                console.log(used_from_date);
            //    //                console.log('used_to_date');
            //    //                console.log(used_to_date);
            //    //                console.log('period_from');
            //    //                console.log(period_from);
            //    //                console.log('period_to');
            //    //                console.log(period_to);

            //    //                if (period_to < used_from_date || used_to_date < period_from){
            //    //                    // Site is not used.  Do nothing
            //    //                } else {
            //    //                    // This site is temporary used for the period from this.form_date to this.to_date
            //    //                    apiary_site['_site_used'] = true
            //    //                    break outer_loop;
            //    //                }
            //    //            }
            //    //        }
            //    //    }

            //    }

            //    this.$refs.apiary_sites_table.vmDataTable.row.add(temporary_use_apiary_site).draw();
            //},
            addEventListeners: function () {
            //    $("#apiary-sites-table").on("click", ".view_on_map", this.viewSiteOnMap);
            //    $("#apiary-sites-table").on("click", ".site_checkbox", this.siteCheckboxClicked);

                let vm = this;
                let el_fr = $(vm.$refs.periodFromDatePicker);
                let el_to = $(vm.$refs.periodToDatePicker);
                let options = {
                    format: "DD/MM/YYYY",
                    showClear: true ,
                    useCurrent: false,
                };

                el_fr.datetimepicker(options);
                el_to.datetimepicker(options);

                el_fr.on("dp.change", function(e) {
                    let selected_date = null;
                    if (e.date){
                        // Date selected
                        selected_date = e.date.format('DD/MM/YYYY')  // e.date is moment object
                        vm.period_from = selected_date;
                        el_to.data('DateTimePicker').minDate(selected_date);
                    } else {
                        // Date not selected
                        vm.period_from = selected_date;
                        el_to.data('DateTimePicker').minDate(false);
                    }
                    vm.$emit('from_date_changed', vm.period_from)
                    //vm.constructApiarySitesTable();
                });

                el_to.on("dp.change", function(e) {
                    let selected_date = null;
                    if (e.date){
                        selected_date = e.date.format('DD/MM/YYYY');
                        vm.period_to = selected_date;
                        el_fr.data('DateTimePicker').maxDate(selected_date);
                    } else {
                        vm.period_to = '';
                        el_fr.data('DateTimePicker').maxDate(false);
                    }
                    vm.$emit('to_date_changed', vm.period_to)
                    //vm.constructApiarySitesTable();
                });

                //***
                // Set dates in case they are passed from the parent component
                //***
                let searchPattern = /^[0-9]{4}/

                let period_from_passed = vm.period_from;
                if (period_from_passed) {
                    // If date passed
                    if (searchPattern.test(period_from_passed)) {
                        // Convert YYYY-MM-DD to DD/MM/YYYY
                        period_from_passed = moment(period_from_passed, 'YYYY-MM-DD').format('DD/MM/YYYY');
                    }
                    $('#period_from_input_element').val(period_from_passed);
                    el_to.data('DateTimePicker').minDate(period_from_passed);
                }

                let period_to_passed = vm.period_to;
                if (period_to_passed) {
                    // If date passed
                    if (searchPattern.test(period_to_passed)) {
                        // Convert YYYY-MM-DD to DD/MM/YYYY
                        period_to_passed = moment(period_to_passed, 'YYYY-MM-DD').format('DD/MM/YYYY');
                    }
                    $('#period_to_input_element').val(period_to_passed);
                    el_fr.data('DateTimePicker').maxDate(period_to_passed);
                }
            },
        },
        mounted: function() {
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners();
            });
        }
    }
</script>

<style lang="css" scoped>

</style>
