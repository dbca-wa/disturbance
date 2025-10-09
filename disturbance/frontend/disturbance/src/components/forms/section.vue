<template lang="html">
  <div :class="['card section-wrapper', { 'expand-for-print': expandForPrint }]">
    <div class="card-header h4 fw-bold p-4">
        <div
                :id="'show_hide_switch_' + section_id"
                class="row show_hide_switch"
                aria-expanded="true"
                :aria-controls="section_id"
                @click="toggle_show_hide"
            >
            <!-- <h3 class="card-title mb-0">{{ label }}</h3>
            <a
                :href="'#' + section_id"
                class="panelClicker"
                data-bs-toggle="collapse"
                :aria-controls="section_id"
                aria-expanded="true"
            >
                <i class="bi bi-chevron-down"></i>
            </a> -->
            <div class="col-11" :style="'color:' + customColor">
                    {{ label }}
            </div>
            <div class="col-1 text-end">
                    <i
                        :id="chevron_elem_id"
                        class="bi fw-bold chevron-toggle"
                        :data-bs-target="'#' + section_id"
                    >
                    </i>
            </div>
      </div>
    </div>
    <div
      :id="section_id"
      class="collapse show card-body"
      :class="{ show: expandForPrint }"
    >
      <slot></slot>
    </div>
  </div>
</template>
<script>
import { v4 as uuid } from 'uuid';
export default {
  name: "sectionComp",
  props: ["label", "secKey" ],
  data() {
    return {
      eventInitialised: false,
      expandForPrint: true,
      chevron_elem_id: 'chevron_elem_' + uuid(),
      customColor: 'black',
    };
  },
  computed: {
    section_id() {
      return "section_" + this.secKey;
    },
  },
  methods:{
    toggle_show_hide: function () {
            // Bootstrap add a 'collapsed' class name to the element
            let elem_expanded_when_clicked = $(
                '#show_hide_switch_' + this.section_id
            ).hasClass('collapsed');
            this.elem_expanded = !elem_expanded_when_clicked;
            this.$emit('toggle-collapse');
        },
  },
  mounted() {
    if (window.matchMedia) {
      let mediaQueryList = window.matchMedia("print");
      mediaQueryList.addListener(this.handleMediaQueryChange);
      this.expandForPrint = mediaQueryList.matches;
    }
    //chevron_toggle.init();
  },
  updated() {
    this.$nextTick(() => {
      if (!this.eventInitialised) {
        document.querySelectorAll(".panelClicker[data-bs-toggle='collapse']").forEach(el => {
          el.addEventListener("click", function () {
            const icon = el.querySelector("i");
            setTimeout(() => {
              icon.classList.toggle("bi-chevron-down");
              icon.classList.toggle("bi-chevron-up");
            }, 100);
          });
        });
        this.eventInitialised = true;
      }
    });
  },
};
</script>
<style lang="css">
.card-title {
  font-weight: bold;
  font-size: 25px;
  padding: 20px;
}

.expand-for-print .card-body {
  display: block !important;
  visibility: visible !important;
  height: auto !important;
}

@media print {
  .card-body {
    display: block !important;
    visibility: visible !important;
    height: auto !important;
  }
}
.section-wrapper {
    margin-bottom: 20px;
    padding: 0;
}

.show_hide_switch {
    cursor: pointer;
}

.rotate_icon {
    transition: 0.5s;
}

.chev_rotated {
    transform: rotate(90deg);
}
</style>