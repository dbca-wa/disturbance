<template lang="html">
    <div>
        <div class="form-group">
            <div class="checkbox">
                <label :id="id" style="font-weight:normal !important">
                <input :onclick="isClickable" ref="Checkbox" :name="name" type="checkbox" :class="group" data-parsley-required :data-conditions="options" @change="handleChange" :checked="isChecked" :required="isRequired"/>
                <!--{{ label }}<span v-if="assessorMode && layer_value" style="color:blue" class="tab">{{layer_name }}</span>-->
                {{ label }}<span v-if="layer_value" style="color:blue" class="tab">{{layer_name }}</span>
                </label>
                <template v-if="help_text">
                  <HelpText :help_text="help_text" />
                </template>
                <template v-if="help_text_url">
                  <HelpTextUrl :help_text_url="help_text_url" />
                </template>

            </div>
        </div>
    </div>
</template>

<script>
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
export default {
  name: "CheckboxField",
  props: ['name', 'label', 'value', 'group', 'id', 'help_text', 'help_text_url', 'conditions', "handleChange","readonly", "isRequired", "layer_value", "assessorMode"],
  components: {HelpText, HelpTextUrl},
  data: function() {
    let vm = this;
    if(vm.readonly) {
      return { isClickable: "return false;" }
    } else {
      return { isClickable: "return true;" }
    }
  },
  computed: {
    isChecked: function() {
      return (this.value == 'on');
    },
    options: function() {
      return JSON.stringify(this.conditions);
    },
    layer_name:function () {
            let lay_name='';
            // if (this.layer_value && Object.prototype.hasOwnProperty.call(this.layer_value, 'layer_name')) {
            //     lay_name= this.layer_value.layer_name;
            // }
            if(this.layer_value && this.layer_value.sqs_data && Array.isArray(this.layer_value.sqs_data.layers)) {
                // Step 1: look at each nested layer entry.
                // use Set() to remove the duplicate layer names in case of multiple layers with same name and different operator response.
                const layerNames = [...new Set(this.layer_value.sqs_data.layers
                    // Step 2: keep only layers that have a non-empty operator response.
                    .filter(layer => Array.isArray(layer.operator_response) ? layer.operator_response.length > 0 : layer.operator_response)
                    // Step 3: pull the layer name from layer_details when it exists.
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
            if (this.layer_value && Object.prototype.hasOwnProperty.call(this.layer_value, 'layer_modified_date')) {
                lay_name= lay_name + ' - ' +this.layer_value.layer_modified_date;
            }
            return lay_name;
      },
  },
  mounted:function () {
      let vm = this;
      var readonly= vm.readonly;
      readonly= (vm.$parent && vm.$parent.layer_val) ? true : vm.readonly;
      if (vm.isChecked) {
          var input = this.$refs.Checkbox;
          var e = document.createEvent('HTMLEvents');
          e.initEvent('change', true, true);

          /* replacing input.disabled with onclick because disabled checkbox does NOT get posted with form on submit */
          // if(vm.readonly) {
           if(readonly) {
              vm.isClickable = "return false;";
          } else {
              vm.isClickable = "return true;";
		  }
          input.dispatchEvent(e);
      }
      if(readonly) {
              vm.isClickable = "return false;";
          } else {
              vm.isClickable = "return true;";
		  }
  }
}
</script>

<style lang="css">
    input {
        box-shadow:none;
    }
    .tab {
      display: inline-block;
      margin-left: 4em;
      font-weight: normal !important;
    }
</style>
