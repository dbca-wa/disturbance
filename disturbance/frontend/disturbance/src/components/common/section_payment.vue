<template lang="html">
    <div>
        <transition>
            <template v-if="alert_message">
                <div class="alert alert-warning" role="alert">
                    <i class='fa fa-times pull-right close-alert-button' @click="alert_close_clicked"></i>
                    {{ alert_message }}
                </div>
            </template>
        </transition>
        <FormSection :formCollapse="false" label="Payment" Index="payment_item">
            <div class="form-group row">
                <label class="col-sm-2">Invoice number</label>
                <div class="col-sm-3">
                    <input 
                        type="text" 
                        class="w-100 form-control" 
                        placeholder="01234567890" 
                        id="invoice_number_element" 
                        v-model="invoice_reference" 
                    />
                </div>
            </div>
            <div class="form-group row">
                <label class="col-sm-2">Invoice date</label>
                <div class="col-sm-3">
                    <div class="input-group date" ref="invoiceDatePicker">
                        <input type="text" class="form-control" placeholder="DD/MM/YYYY" id="invoice_date_element" />
                        <span class="input-group-addon">
                            <span class="glyphicon glyphicon-calendar"></span>
                        </span>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-sm-2 pull-right">
                    <input
                        :disabled="pay_button_disabled"
                        @click="pay_button_clicked"
                        type="button"
                        value="Pay"
                        class="btn btn-primary w-100"
                    />
                </div>
            </div>
        </FormSection>
    </div>
</template>

<script>
import FormSection from "@/components/forms/section_toggle.vue"
import { helpers, } from '@/utils/hooks'

export default {
    name: 'LedgerPay',
    props:{

    },
    data:function () {
        // let vm = this;
        return{
            payment_item: '',
            invoice_reference: '',
            invoice_date: '',
            alert_message: '',
        }
    },
    components: {
        FormSection
    },
    computed: {
        pay_button_disabled: function(){
            if(this.invoice_reference && this.invoice_date){
                return false
            }
            return true
        },
        csrf_token: function() {
            return helpers.getCookie('csrftoken')
        },
    },
    methods: {
        alert_close_clicked: function(){
            this.alert_message = ''
        },
        pay_button_clicked: function(){
            let vm = this
            let data = {
                'invoice_reference': vm.invoice_reference,
                'invoice_date': vm.invoice_date,
            }
            
            fetch('/validate_invoice_details/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': vm.csrf_token  // Include CSRF token in header
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(res => {
                console.log('in post');
                console.log(res);

                if (res.unpaid_invoice_exists) {
                    vm.alert_message = '';
                    helpers.mimic_redirect('/invoice_payment/' + vm.invoice_reference + '/', {
                        csrfmiddlewaretoken: vm.csrf_token
                    });
                } else {
                    console.log(res);
                    vm.alert_message = res.alert_message;
                }
            })
            .catch(err => {
                console.log(err);
            });


        },
        addEventListeners: function(){
            let vm = this;
            let el_invoice_date = $(vm.$refs.invoiceDatePicker);
            let options = {
                format: "DD/MM/YYYY",
                showClear: true ,
                useCurrent: false,
            }

            el_invoice_date.datetimepicker(options)

            el_invoice_date.on("dp.change", function(e) {
                let selected_date = null;
                if (e.date){
                    // Date selected
                    selected_date = e.date.format('DD/MM/YYYY')  // e.date is moment object
                    vm.invoice_date = selected_date;
                } else {
                    // Date not selected
                    vm.invoice_date = selected_date;
                }
            })
        }
    },
    created: function(){
        this.payment_item = this.$route.params.payment_item
    },
    mounted: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.addEventListeners();
        });
    }
}
</script>

<style>
.w-100 {
    width: 100% !important;
}
.v-enter, .v-leave-to {
    opacity: 0;
}
.v-enter-active, .v-leave-active {
    transition: 1s;
}
.close-alert-button {
    cursor: pointer;
}
</style>
