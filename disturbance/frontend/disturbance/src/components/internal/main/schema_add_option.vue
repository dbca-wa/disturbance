<template lang="html">
    <div class="panel panel-primary">
        <div class="panel-heading">
            <h4 class="panel-title">Options
                <a class="panelClicker" :href="`#`+pOptionBody" data-toggle="collapse" data-parent="#userInfo" expanded="true" :aria-controls="pOptionBody">
                    <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                </a>
            </h4>
        </div>
        <div class="panel-body panel-collapse collapse" :id="``+pOptionBody">
            <div class="row">
                <div v-for="(a, aidx) in addedOptions" v-bind:key="`a_${aidx}`">

                    <div class="col-md-12">&nbsp; </div>
                    <div class="col-md-12">
                        <div class="col-md-3">
                            <label v-if="aidx===0" class="control-label pull-left" >Add Options</label>
                        </div>
                        <div class="col-md-3" v-if="canAddMore">
                            <textarea class="form-control" v-model="a.label"></textarea>
                        </div>
                        <div class="col-md-3" v-else>
                            <label>{{a.label}}</label>
                        </div>
                        <div class="col-md-6" v-if="canAddMore">
                            <a v-if="aidx!==0" class="delete-icon fa fa-trash-o" style="cursor: pointer; color:red;" title="Delete row" @click.prevent="removeOption(aidx)"></a>
                            <button v-if="aidx===0" class="btn btn-link pull-right" :name="`select_option_link_1`" @click.prevent="addOption()">[ Add Another ]</button>
                        </div>
                        <div class="col-md-6" v-else>
                            <div v-for="(c, cid) in a.conditions" v-bind:key="`condition_${cid}`" >
                                <label><input type="checkbox" :value="true" v-model="getCheckedConditions(a,c).isChecked" />&nbsp;&nbsp;{{c.label}}<input type='text' v-if="getCheckedConditions(a,c).isDisplay" class="pull-right" v-model="c.value" /></label>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { v4 as uuidv4 } from 'uuid';
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
