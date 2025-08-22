<template lang="html">
        <span>
            <!--
            <template v-if="!assessorMode">
            -->
            <template v-if="layer_data && !assessorMode">
                <label  for="refresh_time_value" class="inline" > {{ refresh_time_val }}</label>
                <input type="hidden" class="form-control" :name="refresh_timestamp_name" :value="refresh_time" />
                <template v-if="!isRefreshing">
                    <a href="" @click.prevent="refresh">Refresh&nbsp;</a>
                </template>
                <template v-if="isRefreshing">
                    <i class="fa fa-spin fa-spinner">&nbsp;Refresh&nbsp;</i>
                </template>
            </template>
        </span>     
</template>
<script>
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name:"RefreshRadio",
    props:["parent_name","parent_label", "assessorMode","layer_data", "proposal_id", "refresh_time_value"],

components: {  },
data: function() {
  return{
    showingHelpText: false,
    pBody: 'pBody',
    refresh_timestamp_name : this.parent_name+'-refresh-timestamp',
    refresh_time:this.refresh_time_value,
    isRefreshing: false,
    }
  },
 computed:{
        refresh_time_val: function(){
            return this.refresh_time ? moment(this.refresh_time).format('DD/MM/YYYY') + moment(this.refresh_time).format(' h:mm:ss a') : '';
        },
 },

 methods:{
         refresh_old: async function(){
            let vm=this;
            // var ele=document.querySelectorAll('[name='+vm.parent_name+']')
            const mlq_data={label: '',
                            name: ''};
            mlq_data.label=vm.parent_label;
            mlq_data.name=vm.parent_name;
            let url = '/refresh'
            vm.isRefreshing=true;
            // var found=null;
            await this.$http.post(helpers.add_endpoint_json(api_endpoints.proposals_sqs,this.proposal_id + url),JSON.stringify(mlq_data),{
                    emulateJSON:true,
            }).then((response)=>{
                //self.isModalOpen = true;
//                var val=response.body.value;
//                //if(val){
//                    for (const el of ele){
//                      if(val){
//                        if(el.value == val){
//                            el.checked=true;
//                            found=el;                    
//                        }
//                        //if(el.labels && el.labels[0] && el.labels[0].innerText== val){
//                        //    el.checked=true;
//                        //    found=el;                    
//                        //}
//                      } else {
//			el.checked=false;
//                        found=el;                    
//                      }
//                    }
//                    if(found){
//                        var e = document.createEvent('HTMLEvents');
//                        e.initEvent('change', true, true);
//                        found.dispatchEvent(e);
//                    }
//                //}
//                vm.refresh_time= response.body.sqs_timestamp
//                vm.isRefreshing=false;
           	swal.close();
		var resp_proposal=null;
		resp_proposal=response['body']['proposal']
		vm.$emit('refreshFromResponseProposal',resp_proposal);
		//let title = response['body']['message'].includes('updated') ? "Processing refresh request (UPDATED)" : "Processing refresh request"
                let msg = '';
                if (response['body']['message'].includes('already updated')) {
                    msg = "Refresh request is already running. Cannot request another until completed.";
                } else if (response['body']['message'].includes('already queued')) {
                    msg = "Refresh request is already queued. Cannot request another until completed.";
                } else {
                    msg = "Processing refresh request";
                }
		let queue_position = response['body']['position']
		swal.fire({
		    title: 'Refresh Question',
                    html: '<p><strong>' + msg + '</strong><br>' +
			  '<span style="font-size:0.8em">You can close your browser and come back later. You will receive an email when it is complete. (' + queue_position+ ')</span>' +
			  '</p>',
		})
               
            },(error)=>{
                swal.fire(
                    'Error',
                    helpers.apiVueResourceError(error),
                    //error.body,
                    'error'
                )
                vm.isRefreshing=false;
            });
            vm.isRefreshing=false;
        },
        refresh: async function(){
            const vm = this;
            const mlq_data = {
                label: vm.parent_label,
                name: vm.parent_name
            };
            const url = '/refresh';
            vm.isRefreshing = true;
            try {
                const response = await fetch(
                    helpers.add_endpoint_json(api_endpoints.proposals_sqs, vm.proposal_id + url),
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(mlq_data)
                    }
                );
                const data = await response.json();
                swal.close();
                var resp_proposal = data['proposal'];
                vm.$emit('refreshFromResponseProposal', resp_proposal);
                
                let msg = '';
                if (data['message'].includes('already updated')) {
                    msg = "Refresh request is already running. Cannot request another until completed.";
                } else if (data['message'].includes('already queued')) {
                    msg = "Refresh request is already queued. Cannot request another until completed.";
                } else {
                    msg = "Processing refresh request";
                }
                let queue_position = data['position'];
                swal.fire({
                    title: 'Refresh Question',
                    html: '<p><strong>' + msg + '</strong><br>' +
                          '<span style="font-size:0.8em">You can close your browser and come back later. You will receive an email when it is complete. (' + queue_position + ')</span>' +
                          '</p>',
                });
            } catch (error) {
                swal.fire(
                    'Error',
                    error,
                    'error'
                );
            } finally {
                vm.isRefreshing = false;
            }
        },
   }
}
</script>

<style lang="css">
</style>


