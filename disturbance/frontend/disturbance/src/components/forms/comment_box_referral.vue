<template lang="html">
    <div class="col-md-12">
      <div  v-for="box in comment_boxes" :key="box.id">
        <div v-show="box.box_view" class="form-group">
            <div class="row">
              <!-- <label :id="id" class="col-md-3" for="label" >{{ box.label }}</label> -->
              <!-- <label class="col-md-3" for="label" >{{ box.label }}</label> -->
              <label :id="box.id" class="col-md-3" for="label" >{{ box.label }}</label>
              <div class="col-md-9" v-if="box.referral_box">
                  <!-- <textarea :readonly="box.readonly" :type="box.type" :class="box.box_class" :name="box.name" :value="box.value" :data-question="box.question"></textarea> -->
                       <CommentTextarea :readonly="box.readonly" :type="box.type" :box_class="box.box_class" :name="box.name" :value="box.value" :question="box.question"></CommentTextarea>
              </div>
              <div class="col-md-9" v-else>
                  <CommentTextarea :readonly="box.readonly" :type="box.type" :box_class="box.box_class" :name="box.name" :value="box.value" :question="box.question"></CommentTextarea>
              </div>
            </div>
        </div>
      </div>
    </div>
</template>

<script>
import CommentTextarea from './textarea_comment.vue'
export default {
    props:["comment_boxes"],
        components:{
          CommentTextarea
        }
}
</script>

<style lang="css">
</style>
