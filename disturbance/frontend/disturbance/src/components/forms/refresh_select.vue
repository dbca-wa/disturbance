<template lang="html">
        <span>
            <template v-if="layer_data && !assessorMode">
            <!-- <template v-if="!assessorMode"> -->
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
    name:"RefreshSelect",
    props:[
        "parent_name",
        "parent_label",
        "assessorMode",
        "layer_data", 
        "proposal_id", 
        "refresh_time_value",
        "isMultiple"
        ],

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
         refreshOld: async function(){
            let vm=this;
            var ele=$('[name='+vm.parent_name+']')[0]
            //var ele=$('[name='+vm.parent_name+']')
            //add api call here to get the refresh value and refresh time stamp
            const mlq_data={label: '',
                            name: ''};
            mlq_data.label=vm.parent_label;
            mlq_data.name=vm.parent_name;
            let url = '/refresh'
            vm.isRefreshing=true;
            await this.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,this.proposal_id + url),JSON.stringify(mlq_data),{
                    emulateJSON:true,
            }).then((response)=>{
                //self.isModalOpen = true;
                console.log(response);
                var val=response.body.value;
                if(val && typeof(val)=='string')
                {
                    ele.value=val;
                }
                else if(val && typeof(val)=='object'){
                    for (const op of ele.options){
                        for (const value of val){
                            if(op.label.toLowerCase() == value){
                                // console.log('op value', op.value.toLowerCase())
                                // console.log('value', value)
                                op.selected=true;
                                //found=op;                    
                            }
                        }
                    }
                }
                if(val){
                    if(ele){
                        var e = document.createEvent('HTMLEvents');
                        e.initEvent('change', true, true);
                        ele.dispatchEvent(e);
                    }
                }
                vm.refresh_time= response.body.sqs_timestamp;
                vm.isRefreshing= false;   
            },(error)=>{
                swal.fire(
                    'Error',
                    helpers.apiVueResourceError(error),
                    //error.body,
                    'error'
                )
            });
            vm.isRefreshing= false;  
        },
        refresh: async function(){
            let vm=this;
            // var ele=$('[name='+vm.parent_name+']')[0]
            //var ele=$('[name='+vm.parent_name+']')
            //add api call here to get the refresh value and refresh time stamp
            const mlq_data={label: '',
                            name: ''};
            mlq_data.label=vm.parent_label;
            mlq_data.name=vm.parent_name;
            let url = '/refresh'
            vm.isRefreshing=true;
            await this.$http.post(helpers.add_endpoint_json(api_endpoints.proposals_sqs,this.proposal_id + url),JSON.stringify(mlq_data),{
                    emulateJSON:true,
            }).then((response)=>{
//                //self.isModalOpen = true;
//                console.log(response);
//                var val=response.body.value;
//                if(!vm.isMultiple)
//                {
//                    ele.value=val;
//                }
//                else if(vm.isMultiple){
//                    var found_options=[]
//                    for (const op of ele.options){
//                        for (const value of val){
//                            if(op.label.toLowerCase() == value){
//                                // console.log('op value', op.value.toLowerCase())
//                                // console.log('value', value)
//                                op.selected=true;
//                                found_options.push(op);                    
//                            }
//                        }
//                    }
//                    //Uncheck all the options which are not in response value
//                    for( const selected_option of ele.selectedOptions){
//                        if(!(found_options.includes(selected_option))){
//                            selected_option.selected=false;
//                        }
//                    }
//                }
//                if(ele){
//                    var e = document.createEvent('HTMLEvents');
//                    e.initEvent('change', true, true);
//                    ele.dispatchEvent(e);
//                }
//                vm.refresh_time= response.body.sqs_timestamp;
//                vm.isRefreshing= false;   

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
            });
            vm.isRefreshing= false;  
        },
   }
}
</script>

<style lang="css">
</style>


