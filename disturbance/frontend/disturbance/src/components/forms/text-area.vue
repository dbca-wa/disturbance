<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id" for="label" class="inline">{{ label }}</label>
            <template v-if="help_text">
                <HelpText :help_text="help_text" />
            </template>
            <template v-if="help_text_assessor && assessorMode">
                <HelpText :help_text="help_text_assessor" assessorMode={assessorMode} isForAssessor={true} />
            </template> 

            <template v-if="help_text_url">
                <HelpTextUrl :help_text_url="help_text_url" />
            </template>
            <template v-if="help_text_assessor_url && assessorMode">
                <HelpTextUrl :help_text_url="help_text_assessor_url" assessorMode={assessorMode} isForAssessor={true} />
            </template> 
            <template v-if="!assessorMode">
                <Refresh :parent_name="name" :parent_label="label" :assessorMode="assessorMode" :layer_data="layer_val" :proposal_id="proposal_id" :refresh_time_value="refresh_time_value"  />
            </template>

            

            <template v-if="assessorMode">
                <template v-if="!showingComment">
                    <!-- <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a> -->
                    <a v-if="has_comment_value" href="" @click.prevent="toggleComment" class="noPrint"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment" class="noPrint"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>
            <!--<LayerInfo v-show="assessorMode" :layer_value="layer_val"  :assessorMode="assessorMode"/>-->
            <LayerInfo v-show="true" :layer_value="layer_val"  :assessorMode="true"/>
            <textarea :readonly="readonly" class="form-control" rows="5" :name="name" :required="isRequired" :id="textarea_id">{{ value }} </textarea>
        </div>
        <!-- <Comment :question="label" :readonly="assessor_readonly" :name="name+'-comment-field'" v-show="showingComment && assessorMode" :value="comment_value"/>  -->
        <CommentBox :comment_boxes="JSON.parse(comment_boxes)" v-show="showingComment && assessorMode"/> 

    </div>
</template>

<script>
import Comment from './comment.vue'
import CommentBox from './comment_box_referral.vue'
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
import LayerInfo from './layer_info.vue'
import Refresh from './refresh.vue'
export default {
    name:"text-area",
    props:["name","value", "id", "isRequired", "help_text","help_text_assessor","assessorMode","label","readonly","comment_value","assessor_readonly", "help_text_url", "help_text_assessor_url","comment_boxes", "layer_val", "refresh_time_value", "proposal_id"],
    components: {Comment, HelpText, HelpTextUrl, CommentBox, LayerInfo, Refresh},
    data(){
        let vm = this;
        return {
            showingComment: false
        }
    },
    computed:{
        textarea_id:function () {
            return "textarea_"+this.id
        },
        has_comment_value:function () {
            let has_value=false;
            let boxes=JSON.parse(this.comment_boxes)
            for(var i=0; i<boxes.length; i++){
                if(boxes[i].hasOwnProperty('value')){
                    if(boxes[i].value!=null && boxes[i].value!=undefined && boxes[i].value!= '' ){
                        has_value=true;
                    }
                } 
            }
            return has_value;
        },
    },
    methods: {
        toggleComment(){
            this.showingComment = ! this.showingComment;
        },
        
        adjustTextareaHeight() {
            let textarea = document.getElementById('textarea_' + this.id);
                textarea.dataset.originalHeight = textarea.style.height;
                textarea.dataset.originalOverflow = textarea.style.overflow;
                textarea.style.height = 'auto';
                // textarea.style.height = textarea.scrollHeight + 'px';
                // textarea.style.overflow = 'hidden';
                textarea.style.overflow = 'hidden';
                textarea.style.height = (textarea.scrollHeight + 15) + 'px';                
        },
        revertTextareaStyleAfterPrinting() {
            let textarea = document.getElementById('textarea_' + this.id);
                textarea.style.height = textarea.dataset.originalHeight;
                textarea.style.overflow = textarea.dataset.originalOverflow;
        }

    },
    mounted() {
        window.addEventListener('beforeprint', this.adjustTextareaHeight);
        window.addEventListener('afterprint', this.revertTextareaStyleAfterPrinting);
    },
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
