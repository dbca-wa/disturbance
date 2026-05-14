<template lang="html">
    <div class="col-md-12">
        <div v-show="box_view" class="form-group mb-3">
            <div class="row">
                <label :id="id" class="col-md-3" for="label" >{{ label }}</label>
                <!-- <div v-if="isPrinting" class="col-md-9"><br>{{ value }}</div>
                <div v-else class="col-md-9">
                    <textarea :readonly="readonly" :type="type" class="form-control" :name="name" :value="value"></textarea>
                </div> -->
                <div class="print-text-value col-md-9 mb-3" style="display:none;"><br>{{ localValue }}</div>
                <div class="mb-3 col-md-9 form-textarea-value">
                    <textarea :readonly="readonly" :type="type" class="form-control" :name="name" :value="localValue"  @input="onInput"></textarea>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props:["box_view","type","name","value", "id", "label","readonly"],
    data(){
        //let vm = this;
        return {
            // isPrinting: false,
            localValue: this.value || '',
        }
    },
    methods: {
        onInput(event) {
            this.localValue = event.target.value;
            this.$emit('input', event.target.value);
        },
        // adjustTextareaHeight() {
        //     this.isPrinting = true;
        // },
        // revertTextareaStyleAfterPrinting() {
        //     this.isPrinting = false;
        // }
    },
    mounted() {
        // window.addEventListener('beforeprint', this.adjustTextareaHeight);
        // window.addEventListener('afterprint', this.revertTextareaStyleAfterPrinting);
    },
}
</script>

<style lang="css">
    @media print {
        .print-text-value {
            display: block !important;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .form-textarea-value {
            display: none !important;
        }
    }
</style>
