<template lang="html">
    <div class="container">
        <SectionPayment />
    </div>
</template>

<script>
import SectionPayment from '@/components/common/section_payment'

export default {
    name: 'LedgerPay',
    props:{

    },
    data:function () {
        return{
            payment_item: '',
        }
    },
    components: {
        SectionPayment
    },
    computed: {

    },
    methods: {

    },
    created: function(){
        this.payment_item = this.$route.params.payment_item
    },
    mounted: function(){

    }
}
</script>

<style>
</style>
