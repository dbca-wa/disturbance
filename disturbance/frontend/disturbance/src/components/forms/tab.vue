<template lang="html">
    <div id="pill-tabs">

    <div id="tabs" class="tab-header">
        <ul class="nav nav-pills mb-3" id="tab-section" data-tabs="tabs" >
            <li class="nav-item" v-for="(tab, idx) in tabs" :key="idx" >
                <a :id=idx class="nav-link" data-toggle="pill" v-on:click="switchTab(Object.keys(tab)[0])" v-bind:class="{'nav-item active': activeTab === Object.keys(tab)[0]}">
                    <slot :name="tabHeadSlotName(Object.keys(tab)[0])">{{ Object.values(tab)[0] }}</slot>
                </a>
            </li>
        </ul>
    </div>

    <div class="tab-content"><slot :name="tabPanelSlotName"></slot></div>

    </div>
</template>
<script>
export default {
    name:"TabsComponent",
  /* Example tabs array property
     Note: Each tab requires key/value pair.
     [{"tab1": "Tab Label 1"}, {"tab2": "Tab Label 2"}]
  */
    props: {
        initialTab: String,
        tabs: Array,
    },
    data:function () {
        return {
            activeTab: this.initialTab
        };
    },
    computed:{
        tabPanelSlotName() {
            return `tab-panel-${this.activeTab}`;
        }
    },
    methods: {
        tabHeadSlotName(tabName) {
            return `tab-head-${tabName}`;
        },

        switchTab(tabName) {
            this.activeTab = tabName;
        }
    },
}
</script>
<style scoped>
#pill-tabs .nav-pills .nav-link {
  margin-right: 0.5rem;
}

#pill-tabs .nav-link.active {
  background-color: #007bff;
  color: white;
}
 .nav-item {
    cursor: pointer;
}
</style>