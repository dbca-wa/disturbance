<template lang="html">
    <div>
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
            <div class="container-fluid">
                <div class="row col-sm-12">

                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">Period From</label>
                        <div class="col-sm-4">
                            <div class="input-group date" ref="periodFromDatePicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" id="period_from_input_element"/>
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div></div>

                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">Period To</label>
                        <div class="col-sm-4">
                            <div class="input-group date" ref="periodToDatePicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" id="period_to_input_element"/>
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div></div>

                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">Site</label>
                        <div class="col-sm-3">
                            <!-- select class="form-control" v-model="on_site_information.apiary_site" -->
                            <select class="form-control" v-model="on_site_information.apiary_site_id">
                                <option value=""></option>
                                <!-- option v-for="site in apiary_sites_options" :value="site" :key="site.id" -->
                                <option v-for="site in apiary_sites_options" :value="site.id" :key="site.id">
                                    <span>
                                        Site: {{ site.id }}
                                    </span>
                                </option>
                            </select>
                        </div>
                    </div></div>

                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">The proposed location of the hives</label>
                        <div class="col-sm-3">
                            <textarea class="form-control" v-model="on_site_information.hives_loc"/>
                        </div>
                    </div></div>

                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">Number of hives proposed to be placed on the site</label>
                        <div class="col-sm-3">
                            <input type='number' value="0" class="form-control" v-model="on_site_information.hives_num"/>
                        </div>
                    </div></div>

                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">The names of the people who are expected to be entering the site for apiary purposes</label>
                        <div class="col-sm-3">
                            <textarea class="form-control" v-model="on_site_information.people_names"/>
                        </div>
                    </div></div>

                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">Flora targeted</label>
                        <div class="col-sm-3">
                            <textarea class="form-control" v-model="on_site_information.flora"/>
                        </div>
                    </div></div>


                    <div class="form-group"><div class="row">
                        <label class="col-sm-3">Comments</label>
                        <div class="col-sm-3">
                            <textarea class="form-control" v-model="on_site_information.comments"/>
                        </div>
                    </div></div>

                </div>
            </div>
            <div slot="footer">
                <div v-if="errorResponse" class="form-group">
                    <div class="row">
                        <div class="col-sm-12">
                            <strong>
                                <span style="white-space: pre;" v-html="errorResponse"></span>
                            </strong>
                        </div>
                    </div>
                </div>
                <button type="button" v-if="processingDetails" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Adding</button>
                <button type="button" v-else class="btn btn-default" @click="ok">Ok</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
    </div>
</template>

<script>
    import modal from '@vue-utils/bootstrap-modal.vue';
    
    export default {
        name: "OnSiteInformationAdd",
        data: function() {
            return {
                processingDetails: false,
                isModalOpen: false,
                errorResponse: '',
                apiary_sites_options: [],
            }
        },
        components: {
          modal,
        },
        props:{
            on_site_information: {
                type: Object,
            },
            approval_id: {
                type: Number,
                required: true,
                default: 0,
            },
        },
        watch:{
            isModalOpen: function() {
            }
        },
        computed: {
            modalTitle: function() {
                return 'Add on site info'
            },
        },
        mounted: function () {
            this.$nextTick(() => {
                this.addEventListeners();
            });
        },
        created: function() {
            this.loadApiarySites()
        },
        methods: {
            openMe: function () {
                this.isModalOpen = true
            },
            loadApiarySites: async function(){
                await this.$http.get('/api/approvals/' + this.approval_id + '/apiary_site/').then(
                    (accept)=>{
                        this.apiary_sites_options = accept.body
                    },
                    (reject)=>{
                    },
                )
            },
            addEventListeners: function () {
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
                        vm.on_site_information.period_from = selected_date;
                        el_to.data('DateTimePicker').minDate(selected_date);
                    } else {
                        // Date not selected
                        vm.on_site_information.period_from = selected_date;
                        el_to.data('DateTimePicker').minDate(false);
                    }
                });

                el_to.on("dp.change", function(e) {
                    let selected_date = null;
                    if (e.date){
                        selected_date = e.date.format('DD/MM/YYYY');
                        vm.on_site_information.period_to = selected_date;
                        el_fr.data('DateTimePicker').maxDate(selected_date);
                    } else {
                        vm.on_site_information.period_to = '';
                        el_fr.data('DateTimePicker').maxDate(false);
                    }
                });

                //***
                // Set dates in case they are passed from the parent component
                //***
                let searchPattern = /^[0-9]{4}/

                let period_from_passed = vm.on_site_information.period_from;
                if (period_from_passed) {
                    // If date passed
                    if (searchPattern.test(period_from_passed)) {
                        // Convert YYYY-MM-DD to DD/MM/YYYY
                        period_from_passed = moment(period_from_passed, 'YYYY-MM-DD').format('DD/MM/YYYY');
                    }
                    $('#period_from_input_element').val(period_from_passed);
                    el_to.data('DateTimePicker').minDate(period_from_passed);
                }

                let period_to_passed = vm.on_site_information.period_to;
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
            ok: async function () {
                try {
                    this.processingDetails = true;

                    // Update django database
                    const response = await this.sendData();

                    // Inform the parent component that the database has been updated
                    // so that the parent component can update a table
                    this.$emit('on_site_information_added');

                    this.close();
                } catch (err){
                    this.processError(err);
                } finally {
                    this.processingDetails = false;
                }
            },
            processError: async function(err) {
                let errorText = '';
                if (err.body.non_field_errors) {
                    // When non field errors raised
                    for (let i=0; i<err.body.non_field_errors.length; i++){
                        errorText += err.body.non_field_errors[i] + '<br />';
                    }
                } else if(Array.isArray(err.body)) {
                    // When general errors raised
                    for (let i=0; i<err.body.length; i++){
                        errorText += err.body[i] + '<br />';
                    }
                } else {
                    // When field errors raised
                    for (let field_name in err.body){
                        if (err.body.hasOwnProperty(field_name)){
                            errorText += field_name + ': ';
                            for (let j=0; j<err.body[field_name].length; j++){
                                errorText += err.body[field_name][j] + '<br />';
                            }
                        }
                    }
                }
                this.errorResponse = errorText;
            },
            cancel: async function() {
                this.isModalOpen = false;
                this.close();
            },
            close: function () {
                let vm = this;
                this.isModalOpen = false;
            },
            sendData: async function () {
                let base_url = '/api/on_site_information/'
                let payload = {}
                Object.assign(payload, this.on_site_information);

                payload.approval_id = this.approval_id

                let res = '';
                if (this.on_site_information.id){
                    // Update existing on-site-information
                    res = await Vue.http.put(base_url + this.on_site_information.id + '/', payload);
                } else {
                    // Create new on-site-information
                    res = await Vue.http.post(base_url, payload);
                }
                return res
            },
        },
    }
</script>

<style>

</style>
