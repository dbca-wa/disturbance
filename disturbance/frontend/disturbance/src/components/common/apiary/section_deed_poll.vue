<template lang="html">
    <div>
        <div class="row">
            <div class="col-sm-12">
                <label>It is a requirement of all apiary authority holders to sign a deed poll to release and indemnify the State of Western Australia.</label>
                <label>Please note: electronic or digital signatures cannot be accepted where witnessing is required.</label>
                 <label>Please click <a :href="deed_poll_url" target="_blank">here</a> to download the deed poll. The deed poll must be signed in the correct section, be dated and have a witness signature when stipulated. Once signed and dated, please attach the deed poll document below.</label>
                    <FileField
                        class="input_file_wrapper"
                        ref="deed_poll_documents"
                        name="deed-poll-documents"
                        :isRepeatable="isRepeatable"
                        :documentActionUrl="documentActionUrl"
                        :readonly="isReadonly"
                        :replace_button_by_text="true"
                    />
            </div>
        </div>
    </div>
</template>

<script>
    import FileField from '@/components/forms/filefield_immediate.vue'

    export default {
        name: 'SectionDeedPoll',
        props:{
            isRepeatable: {
                type: Boolean,
                default: true,
            },
            isReadonly: {
                type: Boolean,
                default: true,
            },
            documentActionUrl: {
                type: String,
                default: '',
            }
        },
        watch: {

        },
        data: function(){
            return{
                deed_poll_url: '',
            }
        },
        created: function(){
            this.fetchDeedPollUrl()
        },
        mounted: function(){
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners();
            });
        },
        components: {
            FileField,
        },
        computed: {
        },
        methods: {
            fetchDeedPollUrl: function(){
                let vm = this;
                vm.$http.get('/api/deed_poll_url').then((response) => {
                    vm.deed_poll_url = response.body;
                },(error) => {
                    console.log(error);
                });
            },
            addEventListeners: function () {

            },
        },
    }
</script>

<style lang="css" scoped>
.input_file_wrapper {
    margin: 1.5em 0 0 0;
}
</style>
