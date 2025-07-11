<template>
    <div>

        <FormSection :formCollapse="false" label="Period and Site(s)" Index="period_and_sites">
            <template v-if="proposal && proposal.apiary_temporary_use">
                <PeriodAndSites 
                    :is_external="is_external" 
                    :is_internal="is_internal" 
                    :is_readonly="is_readonly"
                    :customer_status="proposal.customer_status"
                    :processing_status="proposal.processing_status"
                    :from_date="proposal.apiary_temporary_use.from_date"
                    :to_date="proposal.apiary_temporary_use.to_date"
                    :temporary_use_apiary_sites="proposal.apiary_temporary_use.temporary_use_apiary_sites"
                    :existing_temporary_uses="existing_temporary_uses"
                    @from_date_changed="fromDateChanged"
                    @to_date_changed="toDateChanged"
                    @apiary_sites_updated="apiarySitesUpdated"
                    :key="period_and_sites_key"
                />
            </template>
        </FormSection>

        <FormSection :formCollapse="false" label="Temporary Occupier" Index="temporary_occupier">
            <template v-if="proposal && proposal.apiary_temporary_use">
                <TemporaryOccupier 
                    :is_external="is_external"
                    :is_internal="is_internal"
                    :name="proposal.apiary_temporary_use.temporary_occupier_name"
                    :phone="proposal.apiary_temporary_use.temporary_occupier_phone"
                    :mobile="proposal.apiary_temporary_use.temporary_occupier_mobile"
                    :email="proposal.apiary_temporary_use.temporary_occupier_email"
                    :is_readonly="is_readonly"
                    @contents_changed="occupierDataChanged"
                    :key="temporary_occupier_key"
                />
            </template>
        </FormSection>

        <FormSection :formCollapse="false" label="Public Liability Insurance" Index="public_liability_insurance">
            <div class="row">
                <div class="col-sm-12">
                    <label>
                        <ol type="a" class="insurance-items">
                        <li>Attach your policy for public liability insurance that covers the areas and operations allowed under the apiary authority, and in the name of the applicant to the extent of its rights and interests, for a sum of not less than AU$10 million per event.</li>
                        <li>It is a requirement of all apiary authority holders to maintain appropriate public liability insurance.</li>
                        </ol>
                    </label>
                </div>
            </div>
            <div class="my-container input-file-wrapper">
                <div class="grow1">
                    <label>Certificate of currency</label>
                </div>
                <div class="grow2">
                    <FileField
                        ref="public_liability_insurance_documents"
                        name="public-liability-insurance-documents"
                        :isRepeatable="false"
                        :documentActionUrl="publicLiabilityInsuranceDocumentUrl"
                        :readonly="readonly"
                        :replace_button_by_text="true"
                    />
                </div>
                <div class="grow1">
                    <label>Expiry Date</label>
                </div>
                <div class="grow1">
                    <div class="input-group date" ref="expiryDatePicker">
                        <input type="text" class="form-control" placeholder="DD/MM/YYYY" id="expiry_date_input_element" :readonly="readonly"/>
                        <span class="input-group-addon">
                            <span class="glyphicon glyphicon-calendar"></span>
                        </span>
                    </div>
                </div>
            </div>
        </FormSection>


        <FormSection :formCollapse="false" label="Deed Poll" Index="deed_poll">
            <template v-if="proposal && proposal.apiary_temporary_use && documentActionUrl">
                <DeedPoll

                    :isRepeatable="false"
                    :isReadonly="is_readonly"
                    :documentActionUrl="documentActionUrl"
                />
            </template>
        </FormSection>
<!--
        <div style="margin-bottom: 50px">
            <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                <div class="navbar-inner">
                    <div class="container">
                        <p class="pull-right" style="margin-top:5px;">
                            <input type="button" @click.prevent="save_exit" class="btn btn-primary" value="Save and Exit"/>
                            <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                            <input v-if="!isSubmitting" type="button" @click.prevent="submit" class="btn btn-primary" value="Submit"/>
                            <button v-else disabled class="btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Submitting</button>
                        </p>
                    </div>
                </div>
            </div>
        </div>
-->

    </div>
</template>

<script>
    import datatable from '@vue-utils/datatable.vue'
    import { helpers, } from '@/utils/hooks'
    import FormSection from "@/components/forms/section_toggle.vue"
    import PeriodAndSites from "@/components/common/apiary/section_period_and_sites.vue"
    import TemporaryOccupier from "@/components/common/apiary/section_temporary_occupier.vue"
    import DeedPoll from "@/components/common/apiary/section_deed_poll.vue"
    import FileField from '@/components/forms/filefield_immediate.vue'

    export default {
        name: 'SectionsProposalTemporaryUse',
        props:{
            is_external: {
                type: Boolean,
                default: false,
            },
            is_internal: {
                type: Boolean,
                default: false,
            },
            proposal: {
                type: Object,
                default: null,
            }
        },
        data:function () {
            let vm=this;

            return{
                period_and_sites_key: '',
                temporary_occupier_key: '',
                pBody: 'pBody'+vm._uid,
                licence: null,
                from_date_enabled: true,
                to_date_enabled: true,
                isSubmitting: false,
                application: {},
                apiary_sites_available: [],
                existing_temporary_uses: [],
            }
        },
        components: {
            DeedPoll,
            FileField,
            FormSection,
            datatable,
            PeriodAndSites,
            TemporaryOccupier,
        },
        computed:{
            csrf_token: function() {
              return helpers.getCookie('csrftoken')
            },
            documentActionUrl: function() {
                let url = '';
                if (this.proposal && this.proposal.apiary_temporary_use) {
                    url = helpers.add_endpoint_join(
                        '/api/proposal/',
                        this.proposal.id + '/process_deed_poll_document/'
                        )
                }
                return url;
            },
            publicLiabilityInsuranceDocumentUrl: function() {
                let url = '';
                console.log('0: ' + this.proposal.apiary_temporary_use.id);
                if (this.proposal && this.proposal.apiary_temporary_use) {
                    url = helpers.add_endpoint_join(
                        '/api/proposal_apiary/',
                        this.proposal.id + '/process_public_liability_insurance_document/'
                    )
                }
                console.log('1: ' + url);
                return url;
            },
            is_readonly: function() {
                let readonlyStatus = true
                if (this.proposal && this.proposal.customer_status === 'Draft' && !this.is_internal) {
                    readonlyStatus = false
                }
                return readonlyStatus
            }
        },
        watch:{

        },
        methods:{
            occupierDataChanged: function(value){
                this.proposal.apiary_temporary_use.temporary_occupier_name = value.occupier_name
                this.proposal.apiary_temporary_use.temporary_occupier_phone = value.occupier_phone
                this.proposal.apiary_temporary_use.temporary_occupier_mobile = value.occupier_mobile
                this.proposal.apiary_temporary_use.temporary_occupier_email = value.occupier_email
            },
            fromDateChanged: function(value){
                this.proposal.apiary_temporary_use.from_date = moment(value, 'DD/MM/YYYY');
            },
            toDateChanged: function(value){
                this.proposal.apiary_temporary_use.to_date = moment(value, 'DD/MM/YYYY');
            },
            apiarySitesUpdated: function(apiary_sites){
                console.log('apiary_sites')
                console.log(apiary_sites)
                for (let i=0; i<apiary_sites.length; i++){
                    let temporary_use_apiary_site = this.proposal.apiary_temporary_use.temporary_use_apiary_sites.find(element => element.apiary_site.id == apiary_sites[i].id)
                    // Update temporary_use_apiary_site, which is sent to the backend when saving
                    temporary_use_apiary_site.apiary_site = apiary_sites[i]
                }
            },
            addEventListeners: function () {
                let vm = this;
                let el_fr = $(vm.$refs.expiryDatePicker);
                let options = {
                    format: "DD/MM/YYYY",
                    showClear: true ,
                    useCurrent: false,
                };

                el_fr.datetimepicker(options);

                el_fr.on("dp.change", function(e) {
                    if (e.date){
                        // Date selected
                        vm.expiry_date_local= e.date.format('DD/MM/YYYY')  // e.date is moment object
                    } else {
                        // Date not selected
                        vm.expiry_date_local = null;
                    }
                    vm.$emit('expiry_date_changed', vm.expiry_date_local)
                });

                //***
                // Set dates in case they are passed from the parent component
                //***
                let searchPattern = /^[0-9]{4}/

                let expiry_date_passed = vm.proposal.proposal_apiary.public_liability_insurance_expiry_date;
                console.log('passed')
                console.log(expiry_date_passed)
                if (expiry_date_passed) {
                    // If date passed
                    if (searchPattern.test(expiry_date_passed)) {
                        // Convert YYYY-MM-DD to DD/MM/YYYY
                        expiry_date_passed = moment(expiry_date_passed, 'YYYY-MM-DD').format('DD/MM/YYYY');
                    }
                    $('#expiry_date_input_element').val(expiry_date_passed);
                }
            },

        },
        created: function() {

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
    .insurance-items {
        padding-inline-start: 1em;
    }
    .my-container {
        display: flex;
        flex-direction: row;
        align-items: center;
    }
    .grow1 {
        flex-grow: 1;
    }
    .grow2 {
        flex-grow: 2;
    }
    .input-file-wrapper {
        margin: 1.5em 0 0 0;
    }
</style>
