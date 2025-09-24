<template lang="html">
    <div id="DataTable" class="table-responsive">
        <table
            :id="id"
            :ref="id"
            class="hover table border table-striped table-bordered dt-responsive nowrap w-100"
            cellspacing="0"
            style="width: 100%"
        >
            <thead>
                <tr>
                    <th
                        v-for="(header, i) in dtHeaders"
                        :data-class="i == 0 ? 'expand' : null"
                        :key="i"
                    >
                        {{ header }}
                    </th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>
</template>
<script>
export default {
    name: 'DataTable',
    props: {
        dtHeaders: {
            type: Array,
            required: true,
        },
        dtOptions: {
            type: Object,
            required: true,
        },
        id: {
            required: true,
        },
    },
    data: function () {
        return {
            vmDataTable: null,
        };
    },
    mounted: function () {
        let vm=this;
        vm.table =$('#'+vm.id);
        //$.fn.dataTable.ext.errMode = 'throw';
        this.initEvents();
    },
    unmounted() {
        if (this.vmDataTable) {
            this.vmDataTable.destroy();
            this.vmDataTable = null;
        }
    },
    methods: {
        initEvents: function () {
            let vm = this;
            let options = vm.dtOptions; // Use the original options

            // Only override ajax for serverSide tables
            if (options.serverSide && options.ajax) {
                const originalAjax = options.ajax;
                options.ajax = function (data, callback, settings) {
                    let ajaxOptions =
                        typeof originalAjax === 'string'
                            ? { url: originalAjax, type: 'GET' }
                            : { ...originalAjax };

                    // Call the original data function to populate filters
                    if (options.data && typeof options.data === 'function') {
                        options.data.call(this, data);
                    } else if (
                        ajaxOptions.data &&
                        typeof ajaxOptions.data === 'function'
                    ) {
                        ajaxOptions.data.call(this, data);
                    }

                    $.ajax({
                        ...ajaxOptions,
                        data,
                        success: function (json) {
                            // Always wrap as DataTables expects for serverSide
                            if (Array.isArray(json)) {
                                json = {
                                    data: json,
                                    recordsTotal: json.length,
                                    recordsFiltered: json.length,
                                    draw:
                                        settings && settings.draw
                                            ? settings.draw
                                            : 0,
                                };
                            } else if (!json || typeof json !== 'object') {
                                json = {
                                    data: [],
                                    recordsTotal: 0,
                                    recordsFiltered: 0,
                                    draw:
                                        settings && settings.draw
                                            ? settings.draw
                                            : 0,
                                };
                            } else if (!('data' in json)) {
                                json.data = [];
                                json.recordsTotal = 0;
                                json.recordsFiltered = 0;
                                json.draw =
                                    settings && settings.draw
                                        ? settings.draw
                                        : 0;
                            }
                            callback(json);
                        },
                        error: function (xhr) {
                            if (xhr.status === 401 || xhr.status === 403) {
                                setTimeout(() => {
                                    window.location.href =
                                        '/login/?next=' +
                                        encodeURIComponent(
                                            window.location.pathname
                                        );
                                }, 0);
                            }
                            callback({
                                data: [],
                                recordsTotal: 0,
                                recordsFiltered: 0,
                                draw:
                                    settings && settings.draw
                                        ? settings.draw
                                        : 0,
                            });
                        },
                    });
                };
            }

            vm.vmDataTable = $(this.$refs[this.id]).DataTable(options);
            $(this.$refs[this.id]).resize(function () {
                vm.vmDataTable.draw(true);
            });
        },
    },
};
</script>

<style lang="css">
div.dt-processing div {
    display: none;
}

td > a {
    border: none;
    border-radius: 2px;
    position: relative;
    padding: 8px 10px;
    margin: 10px 1px;
    font-weight: 500;
    letter-spacing: 0;
    will-change: box-shadow, transform;
    -webkit-transition:
        -webkit-box-shadow 0.2s cubic-bezier(0.4, 0, 1, 1),
        background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1),
        color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    -o-transition:
        box-shadow 0.2s cubic-bezier(0.4, 0, 1, 1),
        background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1),
        color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    transition:
        box-shadow 0.2s cubic-bezier(0.4, 0, 1, 1),
        background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1),
        color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    outline: 0;
    cursor: pointer;
    text-decoration: none;
    background: transparent;
    color: #03a9f4;
}

td {
    word-wrap: break-word;
}

table.dataTable {
    margin-top: 8px;
    margin-bottom: 8px !important;
}

table.table-bordered.dataTable tbody th,
table.table-bordered.dataTable tbody td {
    border-bottom-width: 0;
    vertical-align: middle;
    text-align: left;
}

.schedule-button {
    width: 80px;
}

table.dataTable thead .sorting {
    background: none;
}

table.dataTable thead .sorting_desc {
    background: none;
}

table.dataTable thead .sorting_asc {
    background: none;
}

.table.rowlink td:not(.rowlink-skip),
.table .rowlink td:not(.rowlink-skip) {
    cursor: pointer;
}

table.collapsed > tbody > tr > td > span.responsiveExpander,
table.has-columns-hidden > tbody > tr > td > span.responsiveExpander {
    background: url('https://raw.githubusercontent.com/Comanche/datatables-responsive/master/files/1.10/img/plus.png')
        no-repeat 5px center;
    padding-left: 32px;
    cursor: pointer;
}

table.collapsed > tbody > tr.parent > td span.responsiveExpander,
table.has-columns-hidden > tbody > tr.detail-show > td span.responsiveExpander {
    background: url('https://raw.githubusercontent.com/Comanche/datatables-responsive/master/files/1.10/img/minus.png')
        no-repeat 5px center;
}

table.collapsed > tbody > tr > td.child,
table.has-columns-hidden > tbody > tr > td.child {
    background: #eee;
}

/* Prevent large content in child row (expander) from breaking out of parent width */
tr.child td .dtr-data {
    white-space: normal !important;
    word-break: break-word;
    overflow-wrap: break-word;
    max-width: 100%;
    display: block;
}

table.collapsed > tbody > tr > td > ul,
table.has-columns-hidden > tbody > tr > td > ul {
    list-style: none;
    margin: 0;
    padding: 0;
}

table.collapsed > tbody > tr > td > ul > li > span.dtr-title,
table.has-columns-hidden > tbody > tr > td > ul > li > span.columnTitle {
    font-weight: bold;
}

.table > tbody > tr > td,
.table > tbody > tr > th,
.table > tfoot > tr > td,
.table > tfoot > tr > th,
.table > thead > tr > td,
.table > thead > tr > th {
    vertical-align: middle;
}

div.dataTables_filter input {
    margin-left: 10px;
    display: inline-block;
}

div.dataTables_length select {
    margin-left: 10px;
    margin-right: 10px;
    display: inline-block;
}

.input-sm {
    width: auto;
}

@media screen and (max-width: 767px) {
    div.dataTables_length,
    div.dataTables_info {
        float: left;
        width: auto;
    }

    div.dataTables_filter,
    div.dataTables_paginate {
        float: right;
    }
}
</style>