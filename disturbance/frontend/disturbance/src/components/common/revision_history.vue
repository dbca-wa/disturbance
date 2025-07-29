<template id="revision_history">
    <div class="row">
        <div class="panel-body panel-collapse">
            <div class="scrollable-div">
                <div style="float: left; width: 80%;">
                    <table class="table small-table">
                        <tr>
                            <th>Lodgement</th>
                            <th style="padding-left: 10px;">Date</th>
                            <th style="padding-left: 10px; text-align:center">Actions</th>
                        </tr>
                        <tr v-for="revision in this.lodgement_revisions_actions" :key="revision.id">
                            <td>{{ revision.id }}</td>
                            <td style="padding-left: 10px;">{{ formatDateNoTime(revision.date) }}</td>
                            <td style="padding-left: 10px;" v-on:click="getCompareVersions(revision['index'],revision.date)">
                                <span v-bind:id=revision.id v-html=revision.action></span>
                            </td>
                        </tr>
                    </table>
                </div>
                <div style="float: right; width: 20%;">
                    <table class="table small-table">
                        <tr>
                            <th style="visibility: hidden;">Version</th>
                        </tr>
                        <tr v-for="revision in this.lodgement_revisions_view_actions" :key="revision.id">
                            <td  style="padding-left: 15px;" v-on:click="getViewVersion(revision['index'])">
                                <span v-bind:id=revision.view_id v-html=revision.view_action></span>
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            <div v-if="compareModeActive" align="center">
                <span>&nbsp;<button class="btn btn-primary w-100" @click="getViewVersion(0)">Exit Compare Mode</button></span>
            </div>
        </div>
    </div>
</template>
<script>
import { v4 as uuidv4 } from 'uuid';
import {
    constants
}from '@/utils/hooks'
export default {
    name: 'RevisionHistorySection',
    props: {
        model_object: {
            type: Object,
            required: true
        },
        history_context: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            revisionsTable: null,
            dateFormat: 'DD/MM/YYYY HH:mm:ss',
            lodgement_revisions_actions: [],
            lodgement_revisions_view_actions: [],
            allRevisionsTableRows: '',
            popoversInitialised: false,
            versionCurrentlyShowing: 0,
            isLoadingData: false,
            compareModeActive:false,
            actionsDtOptions: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                deferRender: true, 
                autowidth: true,
                dom:
                    "<'row'<'col-sm-5'l><'col-sm-6'f>>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                processing: true,
                data: this.lodgement_revisions_actions,
                // data: this.lodgement_revisions_view_actions,
                columns: [
                    { data: 'id' },
                    { data: 'date' },
                    { data: 'action' },
                    { data: 'view_action' },
                ],
                order: []
            },
        }
    },
    components:{

    },
    watch:{

    },
    computed: {
        console: () => console,
        showLoader: function() {
            return this.isLoadingData;
        }
    },
    methods:{
        formatDateNoTime: function(data){
            return data ? moment(data).format('DD/MM/YY'): '';
        },
        getCompareVersions: async function (compare_version, lodgement_date) {
            /*  Updates the history panel to show which item is being compared against
                Then emits to the component above to process the compare.
            */

            this.compareModeActive = true;
            let clicked_version = this.lodgement_revisions_actions[compare_version]

            for (let index = 0; index < this.lodgement_revisions_actions.length; index++) {
                this.lodgement_revisions_actions[index].action = '<a style="cursor:pointer;">Compare</a>'
                clicked_version.action = '<div>Comparing</div>'        // should be non-clickable now
                this.lodgement_revisions_actions[0].action = '<div style="visibility: hidden;">&#x1f441;</div>'
                this.lodgement_revisions_view_actions[0].view_action = '<div style="">&#x1f441;</div>'
                this.lodgement_revisions_view_actions[index].view_action = '<a style="cursor:pointer;">View</a>'
            }
            
            // Process the comparison of the model versions ins the component above
            await this.$emit("compare_model_versions", {compare_version, lodgement_date})
        },
        getViewVersion: async function (version) {
            /*  Updates the history panel to show which version is being viewed
                Then emits to the component above to process the change of model object.
            */
            this.compareModeActive = false;
            let clicked_version = this.lodgement_revisions_view_actions[version]
            // Store the revision currently showing so it can be accessed from the compare method
            this.versionCurrentlyShowing = version

            // Set initial values for the View table.
            for (let index = 0; index < this.lodgement_revisions_view_actions.length; index++) {
                this.lodgement_revisions_view_actions[index].view_action = '<a style="visibility: visible; cursor:pointer;">View</a>'
                clicked_version.view_action = '<div style="">&#x1f441;</div>'
                this.lodgement_revisions_actions[0].action = '<div style="visibility: hidden;">&#x1f441;</div>'
                this.lodgement_revisions_actions[index].action = '<a style="cursor:pointer;">Compare</a>'
            }
           
            // Process the change of model version in the component above
            await this.$emit("update_model_object", version)
        },
        showRevisionHistory: function(){
            let vm = this;
            vm.$refs.revision_history.isModalOpen = true;
        },
        initialiseRevisionHistoryPopover: function(vm_uid, ref, datatable_options, actions, view_actions){
            // let vm = this;
            let actionLogId = 'actions-log-table'+vm_uid;
            let popover_name = 'popover-'+ uuidv4()+'-logs';
            $(ref).popover({
                content: function() {
                    return ` 
                    <table id="${actionLogId}" class="hover table table-striped table-bordered dt-responsive" cellspacing="0" width="100%">
                        <thead>
                            <tr>
                                <th>Lodgement</th>
                                <th>Date</th>
                                <th>Action</th>
                                <th>View</th>
                            </tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>`
                },
                html: true,
                title: 'Revision Log',
                container: 'body',
                placement: 'right',
                trigger: "click",
                template: `<div class="popover ${popover_name}" role="tooltip">
                                <div class="arrow"></div>
                                    <h3 class="popover-title"></h3>
                                        <div class="popover-content">
                                </div>
                          </div>`,
            }).on('inserted.bs.popover', function () {
                let data_for_table = []
                // Get the required combination of values from action and view action arrays.
                for (let row_count in actions) {
                    const formatted_date = moment(actions[row_count]['date']).format('DD/MM/YY HH:mm:ss');
                    data_for_table.push({"index": row_count,
                                         "id": actions[row_count]['id'],
                                         "action": actions[row_count]['action'],
                                         "view_action": view_actions[row_count]['view_action'],
                                         "date": formatted_date,
                                         })
                }
                datatable_options.data = data_for_table
                // let table = $('#'+actionLogId).DataTable(datatable_options);
                $('#'+actionLogId).DataTable(datatable_options);
            }).on('shown.bs.popover', function () {
                var el = ref;
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
        initialisePopovers: function(){ 
            if (!this.popoversInitialised){
                this.initialiseRevisionHistoryPopover(uuidv4(), 
                                                      this.$refs.showActionBtn, 
                                                      this.actionsDtOptions, 
                                                      this.lodgement_revisions_actions,
                                                      this.lodgement_revisions_view_actions);
                this.popoversInitialised = true;
            }
        },
        createLodgementRevisionTable: function() {
            /* This creates a table of versions for the current model object. Each entry has the model object ID along with the revision
                number and date of submission. An action is provided for each entry to allow comparison between versions. 
                &#x1f441; is eyeball. Viewing doesn't fit very well. */
            let index = 0
            for (let prop in this.model_object.reversion_history) {
                let action_label = '<a style="cursor:pointer;">Compare</a>'
                let view_action_label = `<a style="cursor:pointer;">View</a>`
                if (index === 0) { 
                    view_action_label = '<div style="pointer-events: none;">&#x1f441;</div>'
                    action_label = '<div style="visibility: hidden; pointer-events: none;">View</div>'
                }
                this.lodgement_revisions_actions.push({"index": index,
                                                       "id": prop,
                                                       "action": action_label,
                                                       "date": this.model_object.reversion_history[prop]["date"],
                })
                this.lodgement_revisions_view_actions.push({"index": index,
                                                            "view_id": "v_"+prop,
                                                            "view_action": view_action_label})
                                
                index += 1
            }
        },
    },
    created: function() {
        // Populate the revision table
        this.createLodgementRevisionTable()
    },
    mounted: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.initialisePopovers();
        });
        $('test-table').DataTable();
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

.scrollable-div {
    height:100px;
    white-space: nowrap;
    overflow-y: scroll;
    font-size:13px;
}

.scrollable-div::-webkit-scrollbar {
    width: 12px;
}

.scrollable-div::-webkit-scrollbar-track {
    -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.3); 
    border-radius: 10px;
}

.scrollable-div::-webkit-scrollbar-thumb {
    border-radius: 10px;
    -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.5); 
}

</style>
