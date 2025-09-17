<template>
  <div class="summernote-wrapper">
    <div ref="editor"></div>
  </div>
</template>

<script>

import $ from 'jquery';
export default {
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  mounted() {
    $(this.$refs.editor).summernote({
      height: 200,
      toolbar: [
        ['style', ['bold', 'italic', 'style']],
        ['para', ['ul', 'ol']],
        ['table', ['table']],
        ['view', ['codeview']]
      ],
      callbacks: {
        onChange: (content) => {
          this.$emit('update:modelValue', content);
        }
      }
    });

    // Set initial content
    $(this.$refs.editor).summernote('code', this.modelValue);
    $(this.$refs.editor).summernote('enable');
  },
  watch: {
    modelValue(newVal) {
      const current = $(this.$refs.editor).summernote('code');
      if (newVal !== current) {
        $(this.$refs.editor).summernote('code', newVal);
      }
    }
  },
  beforeUnmount() {
    $(this.$refs.editor).summernote('destroy');
  }
};
</script>