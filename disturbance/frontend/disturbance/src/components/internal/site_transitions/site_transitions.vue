<template>
    <div class="container">
        <template v-if="is_local">
            site_transitions.vue
        </template>
        <FormSection :formCollapse="false" label="Site(s)" Index="site_avaiability">
        </FormSection>
    </div>
</template>

<script>
    import FormSection from "@/components/forms/section_toggle.vue"
    import {v4 as uuidv4} from 'uuid';
    import { helpers, } from "@/utils/hooks.js"

    export default {
        name: 'SiteTransitions',
        data: function(){
            return {
                component_site_selection_key: uuidv4(),
                apiary_sites: [],
                is_local: helpers.is_local(),
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
            apiarySitesUpdated: function(apiary_sites){
                console.log(apiary_sites)
            },
            loadSites: async function() {
                let vm = this

                Vue.http.get('/api/apiary_site/transitable_sites/').then(re => {
                    vm.apiary_sites = re.body.features
                    this.component_site_selection_key = uuidv4()

                    ////let temp_use = re.body.apiary_temporary_use
                    //vm.apiary_temporary_use = re.body.apiary_temporary_use
                    //if (vm.apiary_temporary_use.from_date){
                    //    console.log(vm.apiary_temporary_use.from_date);
                    //    vm.apiary_temporary_use.from_date = moment(vm.apiary_temporary_use.from_date, 'YYYY-MM-DD');
                    //    console.log(vm.apiary_temporary_use.from_date);
                    //}
                    //if (vm.apiary_temporary_use.to_date){
                    //    console.log(vm.apiary_temporary_use.to_date);
                    //    vm.apiary_temporary_use.to_date = moment(vm.apiary_temporary_use.to_date, 'YYYY-MM-DD');
                    //    console.log(vm.apiary_temporary_use.to_date);
                    //}

                    //// Update PeriodAndSites component
                    //vm.period_and_sites_key = uuidv4();
                    //// Update TemporaryOccupier component
                    //vm.temporary_occupier_key = uuidv4();
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
