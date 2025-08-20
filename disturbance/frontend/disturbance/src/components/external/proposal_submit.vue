<template lang="html">
    <div class="container" >
        <div class="row">
            <div class="col-sm-12">
                <div class="row">
                    <div v-if="proposal && proposal.id" class="col-sm-offset-3 col-sm-6 borderDecoration">
                        <strong>Your proposal has been successfully submitted.</strong>
                        <br/>
                        <table>
                            <tbody>
                                <tr>
                                    <td><strong>Proposal:</strong></td>
                                    <td><strong>{{proposal.lodgement_number}}</strong></td>
                                </tr>
                                <tr>
                                    <td><strong>Date/Time:</strong></td>
                                    <td><strong> {{formatDate(proposal.lodgement_date)}}</strong></td>
                                </tr>
                            </tbody>
                        </table>
                        <router-link :to="{name:'external-proposals-dash'}" style="margin-top:15px;" class="btn btn-primary">Back to dashboard</router-link>
                    </div>
                    <div v-else class="col-sm-offset-3 col-sm-6 borderDecoration">
                        <strong>Sorry it looks like there isn't any proposal currently in your session.</strong>
                        <br /><router-link :to="{name:'external-proposals-dash'}" style="margin-top:15px;" class="btn btn-primary">Back to dashboard</router-link>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
export default {
    //props: ['proposal'],
  data: function() {
    // let vm = this;
    return {
        "proposal": {},
    }
  },
  components: {
  },
  computed: {
  },
  methods: {
    formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
        }
  },
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_proposal;
  },
  created: function () {
        if (!window.history.state.proposal) {
            this.$router.push({
                name: 'external-proposals-dash',
            });
            return;
        }
        Object.assign(
            this.proposal,
            JSON.parse(window.history.state.proposal)
        );
    },
  beforeRouteEnter: function(to, from, next) {
    next(vm => {
    })
  }
}
</script>

<style lang="css" scoped>
.borderDecoration {
    border: 1px solid;
    border-radius: 5px;
    padding: 50px;
    margin-top: 70px;
}
</style>
