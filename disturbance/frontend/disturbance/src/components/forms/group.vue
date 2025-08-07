<template lang="html">
    <div class="top-buffer bottom-buffer">
        <div class="panel panel-default">
            <div class="panel-body">
                <label :id="id" class="inline">{{label}}</label>
                    <!--<i data-toggle="tooltip" v-if="help_text" data-placement="right" class="fa fa-question-circle" :title="help_text"> &nbsp; </i>-->
                <template v-if="help_text">
                    <HelpText :help_text="help_text" /> 
                </template>

                <template v-if="help_text_url">
                    <HelpTextUrl :help_text_url="help_text_url" /> 
                </template>
                <template v-if="!assessorMode && layer_val">
                    <RefreshCheckbox :parent_name="name" :parent_label="label" :assessorMode="assessorMode" :layer_data="layer_val" :proposal_id="proposal_id" :refresh_time_value="refresh_time_value"/>
                </template>
                
                <a class="collapse-link-top pull-right" @click.prevent="expand"><span class="glyphicon glyphicon-chevron-down"></span></a>
                <div class="children-anchor-point collapse in" style="padding-left: 0px"></div>
                <span :class="{'hidden':isRemovable}" v-if="isPreviewMode">
                    <a :id="'remove_'+name" >Remove {{label}}</a>
                </span>
                <a class="collapse-link-bottom pull-right"  @click.prevent="minimize"><span class="glyphicon glyphicon-chevron-up"></span></a>
                <div :class="{'row':true,'collapse':true, 'in':isExpanded}" style="margin-top:10px;" >
                    <div class="col-sm-12">
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
