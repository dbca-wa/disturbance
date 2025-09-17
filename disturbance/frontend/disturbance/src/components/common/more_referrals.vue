<template id="more-referrals">
    <div>
        <a v-if="!isFinalised" ref="showRef"  @click.prevent="" class="actionBtn top-buffer-s">Show Referrals</a>
    </div> 

</template>

<script>
import { v4 as uuidv4 } from 'uuid';
import {
    api_endpoints,
    helpers,
    constants,
}from '@/utils/hooks'
export default {
    name: 'MoreReferrals',
    props: {
        isFinalised: {
            type: Boolean,
            required: true
        },
        canAction: {
            type: Boolean,
            required: true
        },
        proposal: {
            type: Object,
            required: true
        },
        referral_url: {
            type: String,
            default: null
        }
    },
    data(){
        let vm = this;
        return {
            table: null,
            dateFormat: 'DD/MM/YYYY HH:mm:ss',
            datatable_url: '',
            datatable_options: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                deferRender: true, 
                autowidth: true,
                //order: [[0, 'desc']],
                processing:true,
                ajax: {
                    //"url": helpers.add_endpoint_json(api_endpoints.referrals,'datatable_list')+'?proposal='+vm.proposal.id, 
                    "url": this.referral_url,
                    "dataSrc": '',
                },
                columns:[
                    {
                        title: 'Sent On',
                        data: 'lodged_on',
                        render: function (date) {
                            return moment(date).format(vm.dateFormat);
                        },
                        defaultContent: '',
                    },
                    {
                        title: 'Referral',
                        data: 'referral',
                        render: function (data){
                            return `<span>${data.first_name} ${data.last_name}</span>`; 
                        },
                        defaultContent: '',
                    },
                    {
                        title: 'Status',
                        data: 'referral_status',
                        defaultContent: '',
                    },
                    {
                        title: 'Action',
                        data: 'id',
                        render: function (data,type,full) {
                            var result = '';
                            if (!vm.canAction){
                                return result;
                            }
                            var user = full.referral.first_name + ' ' + full.referral.last_name; 
                            if (full.referral_status == 'Awaiting'){
                                result = `<a href="" data-id="${data}" data-user="${user}" class="remindRef">Remind</a>/<a href="" data-id="${data}" data-user="${user}" class="recallRef">Recall</a>`;
                            }
                            else{
                                result = `<a href="" data-id="${data}" data-user="${user}" class="resendRef">Resend</a>`;
                            }
                            return result;
                        },
                        defaultContent: '',
                    },
                    {
                        title: 'Referral Comments',
                        data: 'referral_text',

                        'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 20,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="javascript://" ' +
                                    'role="button" ' +
                                    'data-bs-toggle="popover" ' +
                                    'data-bs-trigger="hover" ' +
                                    'data-bs-placement="top"' +
                                    'data-bs-html="true" ' +
                                    'data-bs-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            return result;
                        },
                        defaultContent: '',
                    }
                ],
                drawCallback: function () {
                    helpers.enablePopovers();
                },
                initComplete: function () {
                    helpers.enablePopovers();
                },
            },
        }
    },
    computed: {
        
    },
    methods: {
        remindReferral:function(_id,user){
            let vm = this;
            
            fetch(helpers.add_endpoint_json(api_endpoints.referrals,_id+'/remind')).then(
                async (response) => {
                    if (!response.ok) {
                        return response.json().then(err => { throw err });
                    }
                    let referrals_remind_res = await response.json();
                    vm.$emit('refreshFromResponse',referrals_remind_res);
                    vm.table.ajax.reload();
                    swal.fire({
                        title: 'Referral Reminder',
                        text: 'A reminder has been sent to '+user,
                        icon: 'success'
                    })
                }).catch(error => {
                    swal.fire({
                        title: 'Proposal Error',
                        text: error,
                        icon: 'error'
                    })
                }
            );
        },
        resendReferral:function(_id,user){
            let vm = this;
            fetch(helpers.add_endpoint_json(api_endpoints.referrals,_id+'/resend')).then(
                async (response) => {
                    if (!response.ok) {
                        return response.json().then(err => { throw err });
                    }
                    let referrals_resend_res = await response.json();
                    vm.$emit('refreshFromResponse',referrals_resend_res);
                    vm.table.ajax.reload();
                    swal.fire({
                        title: 'Referral Resent',
                        text: 'The referral has been resent to '+user,
                        icon: 'success'
                    })
                }).catch(error => {
                    swal.fire({
                        title: 'Proposal Error',
                        text: error,
                        icon: 'error'
                    })
                }
            );
        },
        recallReferral:function(_id,user){
            let vm = this;
            swal.fire({
                    title: "Loading...",
                    //text: "Loading...",
                    allowOutsideClick: false,
                    allowEscapeKey:false,
                    didOpen: () =>{
                        swal.showLoading()
                    }
            })
            fetch(helpers.add_endpoint_json(api_endpoints.referrals,_id+'/recall')).then(
                async (response) => {
                    swal.hideLoading();
                    swal.close();
                    if (!response.ok) {
                        return response.json().then(err => { throw err });
                    }
                    let ref_recall_res = await response.json()
                    vm.$emit('refreshFromResponse',ref_recall_res);
                    vm.table.ajax.reload();
                    swal.fire({
                        title: 'Referral Recall',
                        text: 'The referral has been recalled from '+user,
                        icon: 'success'
                    })
                }).catch(error => {
                    swal.fire({
                        title: 'Proposal Error',
                        text: error,
                        icon: 'error'
                    })
                }
            );
        },
        initialiseTable: function(){
            let vm = this;
            let table_id = 'more-referrals-table'+uuidv4();
            let popover_name = 'popover-'+ uuidv4();
            $(vm.$refs.showRef).popover({
                content: function() {
                    return ` 
                    <table id="${table_id}" class="hover table table-striped table-bordered dt-responsive " cellspacing="0" width="100%">
                    </table>`
                },
                template: `<div class="popover ${popover_name}" role="tooltip"><div class="arrow" style="top:110px;"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>`,
                sanitize:false,
                html: true,
                title: 'Referrals',
                container: 'body',
                placement: 'right',
                trigger: "click focus",
                //offset: '0 10',
            }).on('inserted.bs.popover', function () {
                vm.table = $('#'+table_id).DataTable(vm.datatable_options);

                // activate popover when table is drawn.
                vm.table.on('draw.dt', function () {
                    var $tablePopover = $(this).find('[data-toggle="popover"]');
                    if ($tablePopover.length > 0) {
                        $tablePopover.popover();
                        // the next line prevents from scrolling up to the top after clicking on the popover.
                        $($tablePopover).on('click', function (e) {
                            e.preventDefault();
                            return true;
                        });
                    }
                }).on('click','.resendRef',function(e){
                    e.preventDefault();
                    var _id = $(this).data('id');
                    var user = $(this).data('user');
                    vm.resendReferral(_id,user);
                }).on('click','.recallRef',function(e){
                    e.preventDefault();
                    var _id = $(this).data('id');
                    var user = $(this).data('user');
                    vm.recallReferral(_id,user);
                }).on('click','.remindRef',function(e){
                    e.preventDefault();
                    var _id = $(this).data('id');
                    var user = $(this).data('user');
                    vm.remindReferral(_id,user);
                });
            }).on('shown.bs.popover', function () {
                var el = vm.$refs.showRef;
                // var popoverheight = parseInt($('.'+popover_name).height());

                var popover_bounding_top = parseInt($('.'+popover_name)[0].getBoundingClientRect().top);
                // var popover_bounding_bottom = parseInt($('.'+popover_name)[0].getBoundingClientRect().bottom);

                var el_bounding_top = parseInt($(el)[0].getBoundingClientRect().top);
                // var el_bounding_bottom = parseInt($(el)[0].getBoundingClientRect().top);
                
                var diff = el_bounding_top - popover_bounding_top;

                // var position = parseInt($('.'+popover_name).position().top);
                // var pos2 = parseInt($(el).position().top) - 5;

                var x = diff + 5;
                $('.'+popover_name).children('.arrow').css('top', x + 'px');
            });

        },
    },
    mounted(){
        this.initialiseTable();
        
    }
}
</script>

<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
</style>
