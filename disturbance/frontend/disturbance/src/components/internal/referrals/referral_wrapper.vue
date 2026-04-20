<template>
<div class="container">
    <div v-if="referralId">
        <div v-if="apiaryReferral">
        </div>
        <div v-else>
            <Referral :referralId="referralId"/>
        </div>
    </div>

</div>
</template>
<script>

import Referral from './referral.vue';
export default {
    name: 'ReferralWrapper',
    data() {
        // let vm = this;
        return {
            referralId: null,
            apiaryReferral: false,
        }
    },
    components:{
        Referral,
    },
    watch: {},
    computed: {
    },
    methods: {
    },
    mounted: function () {
    },
    beforeRouteEnter: async function(to) {
        //   fetch(`/api/referrals/${to.params.referral_id}/referral_wrapper.json`)
        //   .then(async (res) => {
        //     if (!res.ok) { return res.json().then(err => { throw err }); }
        //     const data = await res.json();
        //   //fetch(helpers.add_endpoint_json(api_endpoints.referrals,to.params.referral_id)).then(res => {
        //       next(vm => {
        //           vm.referralId = data.id;
        //         //   vm.apiaryReferral = res.body.apiary_referral_exists;
        //       });
        //     }).catch(err => {
        //       console.log(err);
        //     });
        // return a callback from beforeRouteEnter instead of calling next(vm => ...) as it's deprecated.
        try {
            const response = await fetch(`/api/referrals/${to.params.referral_id}/referral_wrapper.json`);
            if (!response.ok) {
                return response.json().then(err => { throw err });
            }
            const data = await response.json();
            return (vm) => {
                 vm.referralId = data.id;
                //   vm.apiaryReferral = res.body.apiary_referral_exists;
            };
        } catch (err) {
            console.log(err);
        }
    },

}
</script>
