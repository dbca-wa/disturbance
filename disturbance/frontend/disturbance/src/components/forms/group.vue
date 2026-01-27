<template>
    <div class="mb-3 pb-3">
        <div class="card">
            <div class="card-body">
                <label :id="id" class="form-label">{{ label }}</label>
                <template v-if="help_text">
                    <HelpText :help_text="help_text" /> 
                </template>

                <template v-if="help_text_url">
                    <HelpTextUrl :help_text_url="help_text_url" /> 
                </template>
                <template v-if="!assessorMode && layer_val">
                    <RefreshCheckbox 
                        :parent_name="name" 
                        :parent_label="label" 
                        :assessorMode="assessorMode" 
                        :layer_data="layer_val" 
                        :proposal_id="proposal_id" 
                        :refresh_time_value="refresh_time_value"
                    />
                </template>
                
                <a class="collapse-link-top float-end" @click.prevent="expand">
                    <i class="bi bi-chevron-down"></i>
                </a>
                <div class="collapse show" style="padding-left: 0px"></div>
                <span v-if="isPreviewMode && !isRemovable">
                    <a :id="'remove_'+name">Remove {{ label }}</a>
                </span>
                <a class="collapse-link-bottom float-end" @click.prevent="minimize">
                    <i class="bi bi-chevron-up"></i>
                </a>
                <div :class="{ 'row': true, 'collapse': true, 'show': isExpanded }" style="margin-top: 10px;">
                    <div class="col-12">
                        <slot></slot>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
import RefreshCheckbox from './refresh_checkbox.vue'
export default {
    name:"groupComponent",
    props:["label", "name", "id", "help_text", "help_text_url", "isRemovable","isPreviewMode", "assessorMode", "layer_val", "proposal_id", "refresh_time_value"],
    data:function () {
        return{
            isExpanded:true
        }
    },
    components: {HelpText, HelpTextUrl, RefreshCheckbox},
    methods:{
        expand:function() {
            this.isExpanded = true;
        },
        minimize:function() {
            this.isExpanded = false;
        }
    },
    mounted:function () {
        // var vm =this;
        $('[data-toggle="tooltip"]').tooltip();
    }
}
</script>

<style lang="css">
    .collapse-link-top,.collapse-link-bottom{
        cursor:pointer;
    }
</style>
