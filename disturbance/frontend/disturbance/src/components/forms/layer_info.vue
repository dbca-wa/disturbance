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
            // old code for reference, but now we want to pull the layer name from the nested sqs_data.layers array
            // if(this.layer_value && Object.prototype.hasOwnProperty.call(this.layer_value, 'layer_name')) {
            //     lay_name= this.layer_value.layer_name;
            // }
            if(this.layer_value && this.layer_value.sqs_data && Array.isArray(this.layer_value.sqs_data.layers)) {
                // Step 1: look at each nested layer entry.
                // use Set() to remove the duplicate layer names in case of multiple layers with same name and different operator response.
                const layerNames = [...new Set(this.layer_value.sqs_data.layers
                    // Step 2: keep only layers that have a non-empty operator response.
                    .filter(layer => Array.isArray(layer.operator_response) ? layer.operator_response.length > 0 : layer.operator_response)
                    // Step 3: pull the layer name from layer_details when it exists for (type=radio,checkbox,select,multiselect) else pull directly layer_name when it exists for type=textarea/text. 
                    .map(layer => layer.layer_details && layer.layer_details.layer_name ? layer.layer_details.layer_name : layer.layer_name)
                    // Step 4: drop any empty values before joining.
                    .filter(layerName => layerName)
                )];

                // Step 5: show all matching names as one readable string.
                lay_name = layerNames.join(', ');
            } 
            else if(this.layer_value && Object.prototype.hasOwnProperty.call(this.layer_value, 'layer_name')) {
                // Fallback for the older flat structure.
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
