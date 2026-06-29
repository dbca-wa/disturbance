<template>
  <div v-if="shouldDisplay" class="privacy-notice-container">
    <div class="card">
      <div class="card-header" @click="toggleCollapse" style="cursor: pointer;">
        <h5 class="mb-0">
          Personal Information Collection Notice
          <span v-if="isExpanded" class="float-end">▲</span>
          <span v-else class="float-end">▼</span>
        </h5>
      </div>
      <transition name="slide">
        <div v-show="isExpanded" class="card-body">
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
      shouldDisplay: false,
      privacyPolicyUrl: 'https://www.dbca.wa.gov.au/media/6324/download'
    }
  },
  methods: {
    toggleCollapse() {
      this.isExpanded = !this.isExpanded;
    }
  },
  mounted() {
    console.log('PrivacyNotice: Component mounted');
    console.log('PrivacyNotice: Current route path:', this.$route.path);
    
    // Get privacy policy URL from window.env if available
    if (window.env && window.env.privacy_policy_url) {
      this.privacyPolicyUrl = window.env.privacy_policy_url;
      console.log('PrivacyNotice: Privacy policy URL from env:', this.privacyPolicyUrl);
    } else {
      console.log('PrivacyNotice: Using default privacy policy URL');
    }
    
    // Get template group from API
    fetch('/template_group', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      console.log('PrivacyNotice: API response:', data);
      console.log('PrivacyNotice: template_group:', data.template_group);
      console.log('PrivacyNotice: route path:', this.$route.path);
      
      // Only display for DAS system on /account/ page
      if (data.template_group === 'das' && this.$route.path.startsWith('/account')) {
        console.log('PrivacyNotice: Conditions met, displaying component');
        this.shouldDisplay = true;
      } else {
        console.log('PrivacyNotice: Conditions not met');
        console.log('PrivacyNotice: template_group check:', data.template_group === 'das');
        console.log('PrivacyNotice: route path check:', this.$route.path.startsWith('/account'));
      }
    })
    .catch(err => {
      console.error('PrivacyNotice: Error fetching template group:', err);
    });
  }
}
</script>

<style scoped>
.privacy-notice-container {
  margin-bottom: 20px;
}

.card-header {
  user-select: none;
  background-color: #f8f9fa;
}

.card-header h5 {
  margin: 0;
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
