<template lang="html">
    <div>
        <modal ref="contact_modal" transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" :okButtonDisabled="okButtonDisabled" large force>
            <div class="row col-sm-12">

                Enter information that will be emailed to the site licence holder. Please ensure your contact details are included if you want to be contacted by the site licence holder.
            </div>
            <div>
                <div class="form-group"><div class="row">
                    <div class="col-sm-12">
                        <textarea class="form-control" v-model="comments"/>
                    </div>
                </div></div>
            </div>
        </modal>
    </div>
</template>

<script>
    import modal from '@vue-utils/bootstrap-modal.vue';
    
    export default {
        name: "ContactLicenceHolderModal",
        data: function() {
            return {
                processingDetails: false,
                isModalOpen: false,  // This is accessed by the 'modal' component directly by this.$parent.close();
                errorResponse: '',
                apiary_site_id: null,
                comments: '',
            }
        },
        components: {
          modal,
        },
        watch:{
            okButtonDisabled: function(){
                this.$refs.contact_modal.okButtonDisabled = this.okButtonDisabled
            }
        },
        computed: {
            modalTitle: function() {
                return 'Contact Licence Holder'
            },
            okButtonDisabled: function(){
                return this.comments.length > 0 ? false : true
            }
        },
        mounted: function () {
            this.$nextTick(() => {
                this.addEventListeners();
            });
        },
        methods: {
            openMe: function () {
                this.isModalOpen = true
                this.$refs.contact_modal.okButtonDisabled = this.okButtonDisabled
            },
            addEventListeners: function () {

            },
            ok: async function () {
                // validation

                // validated.  Send data to the parent component
                this.$emit('contact_licence_holder', {'apiary_site_id': this.apiary_site_id, 'comments': this.comments})
            },
            processError: async function(err) {

            },
            cancel: async function() {
                this.close();
            },
            // This function is directly accessed by the child component 'modal' 
            close: function () {
                this.isModalOpen = false;
            },
            sendData: async function () {

            },
        },
    }
</script>

<style>
textarea {
    resize: vertical;
}
.warning {
    border: 1px solid salmon;
    box-shadow: 0 0 5px;
}
</style>
