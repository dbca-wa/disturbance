<script lang="jsx">
    export default {
        props:["conditions","renderer","name","data","readonly"],
        mounted(){

        },
        render(h) {
            let vm =this;
            try {
                var conditions = vm.conditions;
                if (conditions) {
                    var values = Object.keys(conditions);
                    if (!values) {
                        return (
                            <div> no conditions </div>
                        )
                    }else{
                        return (
                            <div>
                                {values.map(val =>{
                                    {return (
                                        <div id={'cons_'+vm.name+'_'+val} class="d-none">
                                            {conditions[val].map(c=>{
                                                return vm.renderer.renderChildren(h,c,vm.data,vm.readonly)
                                            })}
                                        </div>
                                    )}
                                })}
                            </div>
                        )
                    }
                }else{
                    return ''
                }
            } catch (e) {
                console.log(e);
            }
            return ''
        }

    }
</script>
