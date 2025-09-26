<template lang="html">
    <div>
       
        <FormSection :formCollapse="false" label="Options" Index="1">
            <div class="row mb-3">
                <div v-for="(a, aidx) in addedOptions" v-bind:key="`a_${aidx}`">
                    <div class="row">
                        <div class="col-md-3">
                            <label v-if="aidx===0" class="col-form-label float-start" >Add Options</label>
                        </div>
                        <div class="col-md-3 mb-3" v-if="canAddMore">
                            <textarea class="form-control" v-model="a.label"></textarea>
                        </div>
                        <div class="col-md-3" v-else>
                            <label>{{a.label}}</label>
                        </div>
                        <div class="col-md-6 mb-3" v-if="canAddMore">
                            <a v-if="aidx!==0" class="delete-icon fa fa-trash-o" style="cursor: pointer; color:red;" title="Delete row" @click.prevent="removeOption(aidx)"></a>
                            <button v-if="aidx===0" class="btn btn-link float-end" :name="`select_option_link_1`" @click.prevent="addOption()">[ Add Another ]</button>
                        </div>
                        <div class="col-md-6 mb-3" v-else>
                            <div v-for="(c, cid) in a.conditions" v-bind:key="`condition_${cid}`" >
                                <label>
                                    <input type="checkbox" class="form-check-input" :value="true" v-model="getCheckedConditions(a,c).isChecked" />&nbsp;&nbsp;{{c.label}}
                                    <input type='text' v-if="getCheckedConditions(a,c).isDisplay" class="pull-right" v-model="c.value" />
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </FormSection>
    </div>
</template>

<script>
import { v4 as uuidv4 } from 'uuid';
import FormSection from "@/components/forms/section_toggle.vue"
export default {
    name:"schema-add-option",
    props: {
        addedOptions: Array,
        canAddMore: Boolean,
    },
    data:function () {
        // let vm = this;
        return {
            pOptionBody: 'pOptionBody' + uuidv4(),
            addedOption: {
                id: '',
                label: '',
                value: '',
                conditions: null,
            },
            checkedConditions: [{
                id: null,
                value: null,
                addedOption: null,
                isChecked: false,
                isDisplay: false,
            }],
        };
    },
    components: {
            FormSection,
    },
    computed:{
    },
    methods: {
        addOption: function() {
            this.addedOptions.push(Object.assign({}, this.addedOption))
        },
        getCheckedConditions: function(o, c){
            let checked = this.checkedConditions.find(ch => {return ch.id===c.label && ch.value===c.value && ch.addedOption == o})
            if (checked) {

                let is_display = checked.isChecked && typeof c.value !== 'boolean' ? true : false;
                checked.isDisplay = is_display;
                if (typeof c.value === 'boolean') {
                    c.value = checked.isChecked ? true : false;
                } 

            } else {

                let is_checked = c.value ? true : false;
                let is_display = is_checked && typeof c.value !== 'boolean' ? true : false; 
                checked = {
                    id: c.label,
                    value: c.value,
                    addedOption: o,
                    isChecked: is_checked,
                    isDisplay: is_display,
                }
                this.checkedConditions.push(checked)
            }
            return checked;
        },
        removeOption: function(id=0) {
            this.addedOptions.splice(id, 1)
        },
    },
}
</script>
