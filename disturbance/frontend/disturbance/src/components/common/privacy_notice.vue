<template>
  <div v-if="apiaryTemplateGroup || dasTemplateGroup" class="privacy-notice-container">
    <div class="panel panel-info">
      <div class="panel-heading" @click="toggleCollapse" style="cursor: pointer;">
        <h4 class="panel-title">
          Personal Information Collection Notice
          <span v-if="isExpanded" class="glyphicon glyphicon-chevron-up pull-right"></span>
          <span v-else class="glyphicon glyphicon-chevron-down pull-right"></span>
        </h4>
      </div>
      <transition name="slide">
        <div v-show="isExpanded" class="panel-body">
          <!-- DAS-specific content -->
          <div v-if="dasTemplateGroup">
            <p>
              The Department of Biodiversity, Conservation and Attractions (DBCA) collects personal information, to:
            </p>
            <ul>
              <li>provide you with access to the Disturbance Approval System (DAS)</li>
              <li>assign users to the appropriate organisation</li>
              <li>enable communication regarding proposals, assessments, and approval processes</li>
            </ul>
            <p>
              We may share this information with:
            </p>
            <ul>
              <li>the relevant organisation you are seeking to be linked to, for the purpose of confirming your association</li>
              <li>the assigned DBCA assessor and approver of a proposal, to enable the proponent to be contacted and notified</li>
            </ul>
            <p>
              If you choose not to provide this information, DBCA will be unable to grant you access to DAS or link you to an organisation (including establishing a new organisation within DAS).
            </p>
            <p>
              For further details on how DBCA manage your personal information, you can read our
              <a :href="privacyPolicyUrl" target="_blank">Privacy Policy</a>.
              If you have any questions about how your personal information will be handled, or if you
              would like to access your personal information, please email DBCA at
              <a href="mailto:privacy@dbca.wa.gov.au">privacy@dbca.wa.gov.au</a>.
            </p>
          </div>

          <!-- Apiary-specific content -->
          <div v-if="apiaryTemplateGroup">
            <p>
              The Department of Biodiversity, Conservation and Attractions (DBCA) collects this personal
              information to assess, approve and grant an Apiary Authority that allows you to
              legally carry out beekeeping activities in Western Australia's national parks, conservation
              reserves and certain Crown lands for beekeeping.
            </p>
            <p>
              You are required to provide this information under the
              <em>Conservation and Land Management Act 1984</em> and
              <em>Conservation and Land Management Regulations 2002</em>.
            </p>
            <p>
              If you choose not to provide personal information, you will not be able to legally carry
              out beekeeping activities in Western Australia's national parks, conservation reserves and
              certain Crown lands for beekeeping.
            </p>
            <p>
              For further details on how DBCA manage your personal information, you can read our
              <a :href="privacyPolicyUrl" target="_blank">Privacy Policy</a>.
              If you have any questions about how your personal information will be handled, or if you
              would like to access your personal information, please email
              <a href="mailto:privacy@dbca.wa.gov.au">privacy@dbca.wa.gov.au</a>.
            </p>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PrivacyNotice',
  data() {
    return {
      isExpanded: true,
      apiaryTemplateGroup: false,
      dasTemplateGroup: false,
      privacyPolicyUrl: '#'
    }
  },
  methods: {
    toggleCollapse() {
      this.isExpanded = !this.isExpanded;
    }
  },
  mounted() {
    // Get template group from API
    this.$http.get('/template_group', {
      emulateJSON: true
    }).then(res => {
      console.log('[PrivacyNotice] Template group:', res.body.template_group, 'Route path:', this.$route.path);
      if (res.body.template_group === 'apiary') {
        this.apiaryTemplateGroup = true;
      } else if (res.body.template_group === 'das' || res.body.template_group === 'disturbance') {
        // DAS: only display on /account/ page (with or without trailing slash)
        if (this.$route.path === '/account' || this.$route.path === '/account/') {
          this.dasTemplateGroup = true;
          console.log('[PrivacyNotice] DAS template group activated for /account/');
        }
      }
    }, err => {
      console.error('Error fetching template group:', err);
    });

    // Get privacy policy URL from window.env
    if (window.env && window.env.privacy_policy_url) {
      this.privacyPolicyUrl = window.env.privacy_policy_url;
    }
  }
}
</script>

<style scoped>
.privacy-notice-container {
  margin-bottom: 20px;
}

.panel-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.slide-enter-active, .slide-leave-active {
  transition: max-height 0.3s ease, opacity 0.3s ease;
  max-height: 1000px;
  overflow: hidden;
}

.slide-enter, .slide-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
