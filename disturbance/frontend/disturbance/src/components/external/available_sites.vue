<template>
    <div class="container">
    </div>
</template>

<script>
    import FormSection from "@/components/forms/section_toggle.vue"
    import uuid from 'uuid'

    export default {
        name: 'AvailableSites',
        data: function(){
            return {
                component_site_selection_key: uuid(),
                apiary_sites: [],
                modalBindId: uuid(),
            }
        },
        components: {
            FormSection,
        },
        props: {

        },
        watch: {

        },
        computed: {

        },
        methods: {
            contactLicenceHolderClicked: function(apiary_site_id){
                this.openOnSiteInformationModal(apiary_site_id)
            },
            contactLicenceHolder: function(obj){
                this.$http.post('/api/apiary_site/' + obj.apiary_site_id + '/contact_licence_holder/', obj).then(
                    res => {
                    },
                    err => {

                    }
                )
            },
            openOnSiteInformationModal: async function(apiary_site_id) {
                this.modalBindId = uuid()

                try {
                    this.$nextTick(() => {
                    });
                } catch (err) {

                }
            },
            apiarySitesUpdated: function(apiary_sites){
            },
            loadSites: async function() {
                let vm = this

                Vue.http.get('/api/apiary_site/available_sites/').then(re => {

                    vm.apiary_sites = re.body
                    this.component_site_selection_key = uuid()

                    ////let temp_use = re.body.apiary_temporary_use
                    //vm.apiary_temporary_use = re.body.apiary_temporary_use
                    //if (vm.apiary_temporary_use.from_date){
                    //    vm.apiary_temporary_use.from_date = moment(vm.apiary_temporary_use.from_date, 'YYYY-MM-DD');
                    //}
                    //if (vm.apiary_temporary_use.to_date){
                    //    vm.apiary_temporary_use.to_date = moment(vm.apiary_temporary_use.to_date, 'YYYY-MM-DD');
                    //}

                    //// Update PeriodAndSites component
                    //vm.period_and_sites_key = uuid();
                    //// Update TemporaryOccupier component
                    //vm.temporary_occupier_key = uuid();
                });
            },
        },
        created: function() {
            this.loadSites()
        },
        mounted: function() {

        },
    }
</script>

<style>

</style>
