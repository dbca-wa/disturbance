<template lang="html">
    <div class="noPrint" v-if="assessorMode && layer_value">
    <div class="row">
        <div class="col-md-12">
            <div class="form-group">
                <div class="">
 
                  <div class="row">
                      <div class="col-md-6" style="color:blue">Layer last updated: <span p style="color:blue" v-html="layer_date"></span></div>
                        <p class="col-md-6" style="color:blue" v-html="layer_name"></p>

                  </div>
                  <div v-if="new_layer_updated && new_layer_name" class="row">
                        <div class="col-md-12" style="color:red">Layer has expired.</div>
                        <div class="col-md-6" style="color:red">New layer available: <span p style="color:red" v-html="new_layer_updated"></span></div>
                        <p class="col-md-6" style="color:red" v-html="new_layer_name"></p>
                  </div>
                  

                </div>
            </div>
        </div>
    </div>
    </div>
</template>

<script>
export default {
    props:["layer_value", "assessorMode"],
    name: 'LayerInfo',
    computed:{
        
        layer_name:function () {
            let lay_name='';
            if(this.layer_value && Object.prototype.hasOwnProperty.call(this.layer_value, 'layer_name')) {
                lay_name= this.layer_value.layer_name;
            }
            return lay_name;
        },
        layer_date:function () {
            let lay_date='';
            if(this.layer_value && Object.prototype.hasOwnProperty.call(this.layer_value, 'layer_modified_date')) {
                lay_date= this.layer_value.layer_modified_date;
            }
            return lay_date;
        },
        new_layer_name:function () {
            let new_lay_name='';
            if(this.layer_value && Object.prototype.hasOwnProperty.call(this.layer_value, 'new_layer_name')){
                new_lay_name= this.layer_value.new_layer_name;
            }
            return new_lay_name;
        },
        new_layer_updated:function () {
            let new_lay_date='';
            if(this.layer_value && Object.prototype.hasOwnProperty.call(this.layer_value, 'layer_updated')){
                new_lay_date= this.layer_value.layer_updated;
            }
            return new_lay_date;
        },
    },
}

</script>

<style lang="css" scoped>
.buffer {
    margin-top: 5px;
}
@media print { 
        .noPrint { 
        display: none;
        }
    }
</style>
