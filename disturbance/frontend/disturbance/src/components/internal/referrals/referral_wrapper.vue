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
        let vm = this;
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
    beforeRouteEnter: function(to, from, next) {
          Vue.http.get(`/api/referrals/${to.params.referral_id}/referral_wrapper.json`).then(res => {
          //Vue.http.get(helpers.add_endpoint_json(api_endpoints.referrals,to.params.referral_id)).then(res => {
              next(vm => {
                  vm.referralId = res.body.id;
                //   vm.apiaryReferral = res.body.apiary_referral_exists;
              });
            },
            err => {
              console.log(err);
            });
    },

}
</script>
