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
    if (typeof $.now !== 'function') {
      $.now = Date.now;
    }

    $(this.$refs.editor).summernote({
      height: 200,
      toolbar: [
        ['history', ['undo', 'redo']],
        ['style', ['style']],
        ['font', ['bold', 'italic', 'underline', 'strikethrough', 'clear']],
        ['fontname', ['fontname']],
        ['fontsize', ['fontsize']],
        ['color', ['color']],
        ['para', ['ul', 'ol', 'paragraph']],
        ['height', ['height']],
        ['insert', ['link', 'picture', 'table', 'hr']],
        ['view', ['fullscreen', 'codeview', 'help']]
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

<style scoped>
.summernote-wrapper :deep(.note-editor.note-frame.fullscreen) {
  background-color: #fff !important;
}

.summernote-wrapper :deep(.note-editor.note-frame.fullscreen .note-editing-area),
.summernote-wrapper :deep(.note-editor.note-frame.fullscreen .note-editable) {
  background-color: #fff !important;
}
</style>
