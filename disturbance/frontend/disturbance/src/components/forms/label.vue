<template lang="html">
    <div class="form-group">
        <label :id="id" for="label" v-html="value"></label>
    </div>
</template>

<script>
export default {
    name: 'LabelComponent',
    props:["value", "id"]
}
</script>

<style lang="css">
</style>
