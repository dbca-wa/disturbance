<template lang="html">
    <div class="panel panel-default" >
      <div v-if="!hideHeader" class="panel-heading">
        <h3 class="panel-title">{{label}} <small v-if="subheading"> - {{subheading}}</small> 
            <a :href="'#'+section_id" class="panelClicker" :id="custom_id" data-toggle="collapse" expanded="true" :aria-controls="section_id">
                <span :class="panel_chevron_class"></span>
            </a>
        </h3>
      </div>
      <div :class="panel_collapse_class" :id="section_id">
          <slot></slot>
      </div>
    </div>
</template>

<script>
import {v4 as uuidv4} from 'uuid';

export default {
    name:"FormSection",
    props:{
        "label": {
            type: String,
            default: ''
        },
        "subheading":{
            type: String,
            default: ''
        },
        "Index":{
            type: String,
            default: ''
        },
        "formCollapse":{
            type: Boolean,
            default: false
        },
        "hideHeader": {
            type: Boolean,
            default: false
        },
        "treeHeight": {
            type: Boolean,
            default: false
        },
    },
    data:function () {
        return {
            title:"Section title",
            //subheading:"",
            panel_chevron_class: null,
            custom_id: uuidv4(),
        }
    },
    computed:{
        section_id: function () {
            return "section_"+this.Index
        },
        panel_collapse_class: function() {
            if (this.formCollapse) {
                this.set_panel_chevron_class();
                return "panel-body collapse";
            } else {
                if (this.treeHeight) {
                    this.set_panel_chevron_class();
                    return "panel-body collapse in flex-container";
                } else {
                    this.set_panel_chevron_class();
                    return "panel-body collapse in";
                }
            }
        },
    },
    methods:{
        set_panel_chevron_class: function() {
            return this.formCollapse ? "glyphicon glyphicon-chevron-down pull-right" : "glyphicon glyphicon-chevron-up pull-right";
        }
    },
    mounted: function() {
        $('#' + this.custom_id).on('click',function () {
            var chev = $(this).children()[0];
            window.setTimeout(function () {
                $(chev).toggleClass("glyphicon-chevron-up glyphicon-chevron-down");
            }, 100);
        });
    },
    updated:function () {
    },
}
</script>

<style lang="css">
    h3.panel-title{
        font-weight: bold;
        font-size: 25px;
        padding:20px;
    }
    .flex-container {
        display: flex;
        flex-direction: column;
        min-height: 325px;
    }
</style>
