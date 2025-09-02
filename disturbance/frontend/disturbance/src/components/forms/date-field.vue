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
                <HelpTextUrl :help_text_url="help_text_assessor_url" assessorMode={assessorMode} isForAssessor={true} />
            </template> 


            <template v-if="assessorMode">
                <template v-if="!showingComment">
                   <!--  <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a> -->
                   <a v-if="has_comment_value" href="" @click.prevent="toggleComment" class="noPrint"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment" class="noPrint"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>
            <!--<LayerInfo v-show="assessorMode" :layer_value="layer_val"  :assessorMode="assessorMode"/>-->
            <LayerInfo v-show="true" :layer_value="layer_val"  :assessorMode="true"/>
            <div class='input-group date'>
                <!-- <input type="text" :readonly="readonly" :name="name" class="form-control" placeholder="DD/MM/YYYY" :value="value" :required="isRequired"/> -->
                <input type="date" :readonly="readonly" :name="name" class="form-control" placeholder="DD/MM/YYYY" :value="value" :required="isRequired"/>
                <span class="input-group-addon">
                    <span class="glyphicon glyphicon-calendar"></span>
                </span>
            </div>
        </div>
        <!-- <Comment :question="label" :readonly="assessor_readonly" :name="name+'-comment-field'" v-show="showingComment && assessorMode" :value="comment_value"/>  -->
        <CommentBox :comment_boxes="JSON.parse(comment_boxes)" v-show="showingComment && assessorMode"/> 
    </div>
</template>

<script>
// import moment from 'moment'
// import Comment from './comment.vue'
import CommentBox from './comment_box_referral.vue'
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
import LayerInfo from './layer_info.vue'
export default {
    name:"DateField",
    props: ['name', 'label', 'id', 'readonly', 'help_text', 'help_text_assessor', 'assessorMode', 'value', 'conditions', "handleChange","comment_value","assessor_readonly", "isRequired", 'help_text_url', 'help_text_assessor_url', 'comment_boxes', 'layer_val'],
    data(){
        return {
            showingComment: false
        }
    },
    components: {HelpText, HelpTextUrl, CommentBox, LayerInfo,},
    computed: {
        isChecked: function() {
        //TODO return value from database
        return false;
        },
        options: function() {
        return JSON.stringify(this.conditions);
        },
        has_comment_value:function () {
            let has_value=false;
            let boxes=JSON.parse(this.comment_boxes)
            for(var i=0; i<boxes.length; i++){
                if (Object.prototype.hasOwnProperty.call(boxes[i], 'value')) {
                    if(boxes[i].value!=null && boxes[i].value!=undefined && boxes[i].value!= '' ){
                        has_value=true;
                    }
                } 
            }
            return has_value;
        },
    },
    methods:{
        toggleComment(){
            this.showingComment = ! this.showingComment;
        }
    },
    mounted: function() {
        // $('.date').datetimepicker({
        // format: 'DD/MM/YYYY'
        // });
    }
}
</script>

<style lang="css">
    input {
        box-shadow:none;
    }
    @media print { 
            .noPrint { 
            display: none;
            }
        }
</style>
