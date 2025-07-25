<template lang="html">
    <!-- <div class="panel panel-default"> -->
    <div :class="['panel', 'panel-default', { 'expand-for-print': expandForPrint }]" >
      <div class="panel-heading">
        <h3 class="panel-title">{{label}}
            <a :href="'#'+section_id" class="panelClicker" data-toggle="collapse" expanded="true" :aria-controls="section_id">
                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
            </a>
        </h3>
      </div>
      <div class="panel-body collapse in" :id="section_id" :class="{ 'in': expandForPrint }">
    <!-- <div class="panel-body collapse" :id="section_id" > -->
          <slot></slot>
      </div>
    </div>
</template>

<script>
export default {
    name:"sectionComp",
    props:["label","secKey"],
    data:function () {
        return {
            title:"Section title",
            eventInitialised: false,
            expandForPrint: true,
        }
    },
    computed:{
        section_id:function () {
            return "section_"+this.secKey
        }
    },
    methods: {
        
    },
    mounted() {
        
        if (window.matchMedia) {
            let mediaQueryList = window.matchMedia('print');
            mediaQueryList.addListener(this.handleMediaQueryChange);
            this.expandForPrint = mediaQueryList.matches;
        }
    },
    updated:function () {
        let vm = this;
        vm.$nextTick(()=>{
            if (!vm.eventInitialised){
                $('.panelClicker[data-toggle="collapse"]').on('click',function () {

                    console.log('clicked');

                    var chev = $(this).children()[0];
                    window.setTimeout(function () {
                        $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
                    },100);
                });
                this.eventInitialised = true;
            }
        });
        
    },
}
</script>

<style lang="css">
    h3.panel-title{
        font-weight: bold;
        font-size: 25px;
        padding:20px;
    }
    .expand-for-print .panel-body {
        display: block !important;
        visibility: visible !important;
        height: auto !important;
    }

    .expand-for-print .panel-body.collapse {
        display: block !important;
    }

    .expand-for-print .panel-body.in {
        display: block !important;
    }

        /* You can adjust the styles for printing as needed */
    @media print {
    .panel-body {
        display: block !important;
        visibility: visible !important;
        height: auto !important;
    }
    }
</style>
