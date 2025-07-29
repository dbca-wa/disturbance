<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id">{{ label }}</label>

            <template v-if="help_text">
                <HelpText :help_text="help_text" />
            </template>
            <template v-if="help_text_assessor && assessorMode">
                <HelpText  :help_text="help_text_assessor" assessorMode={assessorMode} isForAssessor={true} />
            </template> 

            <template v-if="help_text_url">
                <HelpTextUrl :help_text_url="help_text_url" />
            </template>
            <template v-if="help_text_assessor_url && assessorMode">
                <HelpTextUrl  :help_text_url="help_text_assessor_url" assessorMode={assessorMode} isForAssessor={true} />
            </template> 
            <template v-if="!assessorMode">
                <RefreshSelect :parent_name="name" :parent_label="label" :assessorMode="assessorMode" :layer_data="layer_val" :proposal_id="proposal_id" :refresh_time_value="refresh_time_value" :isMultiple="isMultiple"/>
            </template>

            <template v-if="assessorMode">
                <template v-if="!showingComment">
                    <!-- <a v-if="comment_value != null && comment_value != undefined && comment_value != '' && comment_value['assessor']!=null && comment_value['assessor']!=undefined && comment_value['assessor']!= '' " href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a> -->
                    <a v-if="has_comment_value" href="" @click.prevent="toggleComment" class="noPrint"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment" class="noPrint"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>

            <LayerInfo v-show="true" :layer_value="layer_val"  :assessorMode="true"/>
     
            <template v-if="readonly">
                <select v-if="!isMultiple" disabled ref="selectB" :id="selectid" :name="name" class="form-control" :data-conditions="cons" style="width:100%">
                    <option value="">Select...</option>
                    <option v-for="op in options"  :value="op.value" :key="op.label" @change="handleChange" :selected="op.value == value">{{ op.label }}</option>
                </select>
                <select v-else disabled ref="selectB" :id="selectid" :name="name" class="form-control" multiple style="width:100%">
                    <option value="">Select...</option>
                    <option v-for="op in options"  :value="op.value" :key="op.label" :selected="multipleSelection(op.value)">{{ op.label }}</option>
                </select>
                <template v-if="isMultiple">
                    <input v-for="v in value" :key="v" input type="hidden" :name="name" :value="v" :required="isRequired"/>
                </template>
                <template v-else>
                    <input type="hidden" :name="name" :value="value" :required="isRequired"/>
                </template>
            </template>
            <template v-else>
                <select v-if="!isMultiple" ref="selectB" :id="selectid" :name="name" class="form-control" :data-conditions="cons" style="width:100%" :required="isRequired">
                    <option value="">Select...</option>
                    <option v-for="op in options"  :key="op.label" :value="op.value" @change="handleChange" :selected="op.value == value">{{ op.label }}</option>
                </select>
                <select v-else ref="selectB" :id="selectid" :name="name" class="form-control" multiple style="width:100%" :required="isRequired">
                    <option value="">Select...</option>
                    <option v-for="op in options"  :key="op.label" :value="op.value" :selected="multipleSelection(op.value)">{{ op.label }}</option>
                </select>
            </template>
        </div>
        
        <CommentBox :comment_boxes="JSON.parse(comment_boxes)" v-show="showingComment && assessorMode"/> 


    </div>
</template>

<script>
import { v4 as uuidv4 } from 'uuid';
// var select2 = require('select2');
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
// import Comment from './comment.vue'
import CommentBox from './comment_box_referral.vue'
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
import LayerInfo from './layer_info.vue'
import RefreshSelect from './refresh_select.vue'
export default {
    name:"selectComp",
    props:{
        'name':String,
        'label':String,
        'id': String,
        'isRequired': String,
        'help_text':String,
        'help_text_assessor':String,
        'help_text_url':String,
        'help_text_assessor_url':String,
        "value":[String,Array],
        //"comment_value": String,
        "comment_value": [String, Object],
        "assessor_readonly": Boolean,
        "options":Array,
        "conditions":Object,
        "handleChange":null,
        "isMultiple":{
            default:function () {
                return false;
            }
        },
        "assessorMode":{
            default:function () {
                return false;
            }
        },
        'readonly': Boolean,
        "comment_boxes":{
            default:function () {
                return "";
            }
        },
        "layer_val": {
            default:function () {
                return false;
            }
        },
        "refresh_time_value":{
            default:function () {
                return "";
            }
        },
        'proposal_id': Number,
        //"comment_boxes":[String, Array],
    },
    data:function () {
        // let vm =this;
        return{
            selected: (this.isMultiple) ? [] : "",
            selectid: "select"+uuidv4(),
            multipleSelected: [],
            showingComment: false,
           
        }
    },
    watch: {
        // Watcher needed to recreate the jquery select2 when changing proposal versions
        value: {
            immediately: true,
            handler (){
                this.init();
            },
            deep: true,
        }
    },
    computed:{
        cons:function () {
            return JSON.stringify(this.conditions);
        },
        has_comment_value:function () {
            let has_value=false;
            let boxes=JSON.parse(this.comment_boxes)
            for(var i=0; i<boxes.length; i++){
                console.log('comment box')
                console.log(boxes[i])
                if (Object.prototype.hasOwnProperty.call(boxes[i], 'value')) {
                    if(boxes[i].value!=null && boxes[i].value!=undefined && boxes[i].value!= '' ){
                        has_value=true;
                    }
                } 
            }
            return has_value;
        },
    },
    components: { HelpText, HelpTextUrl, CommentBox, LayerInfo, RefreshSelect},
    methods:{
        toggleComment(){
            this.showingComment = ! this.showingComment;
        },
       

        multipleSelection: function(val){
            if (Array.isArray(this.value)){
                if (this.value.find(v => v == val)){
                    return true;
                }
            }else{
                if (this.value == val){return true;}
            }
            return false;
        },
        init:function () {
            let vm =this;
            vm.$nextTick(function () {
                   $('#'+vm.selectid).select2({
                       "theme": "bootstrap",
                       allowClear: true,
                       placeholder:"Select..."
                   }).
                   on("select2:select",function (e) {
                       var selected = $(e.currentTarget);
                       vm.handleChange(selected[0])
                       e.preventDefault();
                        if( vm.isMultiple){
                            vm.multipleSelected = selected.val();
                        }
                   }).
                   on("select2:unselect",function (e) {
                        var selected = $(e.currentTarget);
                        vm.handleChange(selected[0])
                        e.preventDefault();
                        if( vm.isMultiple){
                            vm.multipleSelected = selected.val();
                        }
                   });
                   if (vm.value) {
                       vm.handleChange(vm.$refs.selectB);
                   }
               });
        }
    },
    mounted:function () {
        this.init();
    }
}
</script>

<style lang="css">
.select2-container {
  width: 100% !important;
}

input {
    box-shadow:none;
}
@media print { 
        .noPrint { 
        display: none;
        }
    }
</style>
