<template>
    <div class="">
        <div class="map-wrapper">
            <div v-show="!fullscreen" id="filter_search_row_wrapper">
                <div class="filter_search_wrapper" style="margin-bottom: 5px;" id="filter_search_row">
                    <div>
                        <div v-show="select2Applied">
                        <div class="row mb-1">
                                <div class="col-md-3">
                                    <div class="form-group">
                                            <div v-show="select2Applied">
                                                <label for="">Region</label>
                                                <select class="form-select" ref="filterRegion" v-model="filterProposalRegion">
                                                    <option value="All">All</option>
                                                    <option v-for="r in regions" :value="r.id" :key="r.id">{{r.search_term}}</option>
                                                </select>
                                            </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="form-group">
                                        <label for="">Activity</label>
                                        <select class="form-select" v-model="filterProposalActivity">
                                            <option value="All">All</option>
                                            <option v-for="a in activity_titles" :value="a" :key="a">{{a}}</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="form-group">
                                        <label for="">Status</label>
                                        <select class="form-select" v-model="filterProposalStatus">
                                            <option value="All">All</option>
                                            <option v-for="s in proposal_status" :value="s.value" :key="s.value">{{s.name}}</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="form-group">
                                        <label for="">Proponent</label>
                                        <select class="form-select" v-model="filterProposalApplicant">
                                            <option value="All">All</option>
                                            <option v-for="s in proposal_applicants" :value="s.id" :key="s.id">{{s.search_term}}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row mb-1">
                                <div class="col-md-3">
                                    <label for="">Lodged From</label>
                                    <div class="input-group date" ref="proposalDateFromPicker">
                                        <input type="date" class="form-control" v-model="filterProposalLodgedFrom">
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <label for="">Lodged To</label>
                                    <div class="input-group date" ref="proposalDateToPicker">
                                        <input type="date" class="form-control" v-model="filterProposalLodgedTo">
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="form-group">
                                        <label for="">Submitter</label>
                                        <select class="form-select" v-model="filterProposalSubmitter">
                                            <option value="All">All</option>
                                            <option v-for="s in proposal_submitters" :value="s.email" :key="s.email">{{s.search_term}}</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="form-group">
                                        <label for="">Proposal Type</label>
                                        <select class="form-select" v-model="filterProposalApplicationType">
                                            <option value="All">All</option>
                                            <option v-for="a in application_types" :value="a" :key="a">{{a}}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row mb-1"></div>
                            
                            <div class="row mb-1">
                                <div class="col-md-6">
                                    <!--
                                    <button type="button" class="btn btn-primary" @click="geoJsonButtonClicked"><i class="fa fa-download"></i>
                                    Get GeoJSON File</button>
                                    -->
                                    <!--
                                    <button type="button" class="btn btn-primary" @click="shapefileButtonClicked(true)"><i class="fa fa-download"></i>
                                        Get GeoJSON File</button>
                                    -->
                                    <button type="button" class="btn btn-primary btn-margin" @click="shapefileButtonClicked(false)" :disabled="download_shapefile_btn_disabled">
                                        <i v-if="download_shapefile_btn_disabled" class="fa fa-download fa-spinner fa-spin"></i>
                                        <i v-else class="fa fa-download"></i>
                                        Download Shapefile
                                    </button>
                                    <a class="btn btn-primary" href="/filelist" target="_blank">View Download Files</a>
                                </div>
                                <!-- <div class="col-md-3">
                                    <button type="button" class="btn btn-primary" id="export-png" @click="exportPNG"><i class="fa fa-download"></i>
                                        Download Image</button>
                                    <a id="image-download" download="map.png"></a>
                                </div> -->
                                
                            </div>
                            <div class="row mb-1"></div>
                        </div>
                    </div>
                </div>
            </div>
            

            <!-- <div class="d-flex justify-content-end align-items-center mb-2">
                <button type="button" class="btn btn-primary" @click="geoJsonButtonClicked"><i class="fa fa-download"></i>
                    Get GeoJSON</button>
            </div>
            <div class="d-flex justify-content-end align-items-center mb-2">
                <button type="button" class="btn btn-primary" id="export-png" @click="exportPNG"><i class="fa fa-download"></i>
                    Download PNG</button>
                <a id="image-download" download="map.png"></a>
            </div> -->
            <div :id="elem_id" class="map" style="position: relative;">
                
                <div v-show="fullscreen" id="filter_search_on_map">
                    <!-- filters on map here -->
                    <!-- end filter here -->
                </div>     
                <div v-if="loading_proposals" class="spinner_on_map">
                    <i class='fa fa-4x fa-spinner fa-spin'></i>
                </div>
                <div class="basemap-button">
                    <img id="basemap_sat" :src="satelliteIconUrl" @click="setBaseLayer('sat')" />
                    <img id="basemap_osm" :src="mapIconUrl" @click="setBaseLayer('osm')" />
                </div>
                <div class="optional-layers-wrapper">
                    <div class="optional-layers-button">
                        <template v-if="mode === 'layer'">
                            <img src="@/assets/info-bubble.svg" @click="set_mode('measure')" />
                        </template>
                        <template v-else>
                            <img src="@/assets/ruler.svg" @click="set_mode('layer')" />
                        </template>
                    </div>
                    <div style="position:relative">
                        <transition>
                            <div v-if="optionalLayers.length" class="optional-layers-button" @mouseover="hover=true">
                                <img src="@/assets/layers.svg" />
                            </div>
                        </transition>
                        <transition v-if="optionalLayers.length">
                            <div class="layer_options" v-show="hover" @mouseover="showOptions"  @mouseleave="hideOptions">
                                <div v-for="layer in optionalLayers" :key="layer.ol_uid">
                                    <input
                                        type="checkbox"
                                        :id="layer.ol_uid"
                                        :checked="layer.values_.visible"
                                        @change="changeLayerVisibility(layer)"
                                        class="layer_option"
                                    />
                                    <label :for="layer.ol_uid" class="layer_option">{{ layer.get('title') }}</label>
                                </div>
                            </div>
                        </transition>
                    </div>
                </div>
            </div>
            <!--- <div class="button_row">
                <span class="view_all_button" @click="displayAllFeatures">View All On Map</span>
            </div> -->
        </div>
        <div :id="popup_id" class="ol-popup">
            <a href="#" :id="popup_closer_id" class="ol-popup-closer">
                <svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='20' width='20' class="close-icon">
                    <g transform='scale(3)'>
                        <path d     ="M 5.2916667,2.6458333 A 2.6458333,2.6458333 0 0 1 2.6458335,5.2916667 2.6458333,2.6458333 0 0 1 0,2.6458333 2.6458333,2.6458333 0 0 1 2.6458335,0 2.6458333,2.6458333 0 0 1 5.2916667,2.6458333 Z" style="fill:#ffffff;fill-opacity:1;stroke-width:0.182031" id="path846" />
                        <path d     ="M 1.5581546,0.94474048 2.6457566,2.0324189 3.7334348,0.94474048 4.3469265,1.5581547 3.2592475,2.6458334 4.3469265,3.7334353 3.7334348,4.3469261 2.6457566,3.2593243 1.5581546,4.3469261 0.9447402,3.7334353 2.0323422,2.6458334 0.9447402,1.5581547 Z" style="fill:#f46464;fill-opacity:1;stroke:none;stroke-width:0.0512157" id="path2740-3" />
                    </g>
                </svg>
            </a>
            <div :id="popup_content_id"></div>
        </div>
    </div>
</template>

<script>
    import {v4 as uuidv4 } from 'uuid';
    import 'ol/ol.css';
    import 'ol-layerswitcher/dist/ol-layerswitcher.css'
    import Map from 'ol/Map';
    import View from 'ol/View';
    import formatWKT  from 'ol/format/WKT';
    import TileLayer from 'ol/layer/Tile';
    import TileWMS from 'ol/source/TileWMS';
    import WMTS from 'ol/source/WMTS';
    import WMTSTilegrid from 'ol/tilegrid/WMTS';
    import { Draw, Modify } from 'ol/interaction';
    import VectorLayer from 'ol/layer/Vector';
    import VectorSource from 'ol/source/Vector';
    import { Circle as CircleStyle, Fill, Stroke, Style, Text } from 'ol/style';
    import { FullScreen as FullScreenControl, MousePosition as MousePositionControl } from 'ol/control';
    import { LineString, Point } from 'ol/geom';
    import GeoJSON from 'ol/format/GeoJSON';
    import Overlay from 'ol/Overlay';
    import { zoomToCoordinates } from '@/components/common/apiary/site_colours.js'
    import MeasureStyles, { formatLength } from '@/components/common/apiary/measure.js'
    // import Datatable from '@vue-utils/datatable.vue'
    import Cluster from 'ol/source/Cluster';
    import 'select2/dist/css/select2.min.css'
    import 'select2-bootstrap-theme/dist/select2-bootstrap.min.css'
    import Awesomplete from 'awesomplete'
    import { api_endpoints, helpers } from '@/utils/hooks'
    import {getCenter} from 'ol/extent'
    import {get as getProjection} from 'ol/proj';
    import {getTopLeft, getWidth} from 'ol/extent'
    import { toRaw } from 'vue';
    // import satelliteIcon from '../../../assets/satellite_icon.jpg'
    // import mapIcon from '../../../assets/map_icon.png'

    export default {
        name: 'MapDashboard',
        data: function(){

            return {
                // AT the moment (specify the path) this works but not ideal, need to find a way to load images from assets folder
                satelliteIconUrl: '/static/disturbance_vue/src/satellite_icon.jpg',
                mapIconUrl: '/static/disturbance_vue/src/map_icon.png',
                newVectorLayer: null,
                newVectorLayerCluster: null,
                newQuerySource: null,
                debug: true,
                show_spinner: false,
                download_shapefile_btn_disabled: false,
                modalBindId: uuidv4(),
                map: null,
                proposals: null,
                filteredProposals: [],
                filterProposalRegion: 'All',
                filterProposalActivity: 'All',
                filterProposalApplicationType: 'All',
                filterProposalStatus: 'All',
                filterProposalLodgedFrom: '',
                filterProposalLodgedTo: '',
                filterProposalSubmitter: 'All',
                filterProposalApplicant: 'All',
                proposalQuerySource: null,
                proposalClusterLayer: null,
                elem_id: uuidv4(),
                popup_id: uuidv4(),
                popup_closer_id: uuidv4(),
                popup_content_id: uuidv4(),
                overlay: null,
                content_element: null,
                modifyInProgressList: [],
                tileLayerOsm: null,
                tileLayerSat: null,
                optionalLayers: [],
                hover: false,
                mode: 'normal',
                drawForMeasure: null,
                measurementLayer: null,
                style: MeasureStyles.defaultStyle,
                segmentStyle: MeasureStyles.segmentStyle,
                labelStyle: MeasureStyles.labelStyle,
                segmentStyles: null,

                
                fullscreen: false,
                

                useSelect2: true,
                select2Applied: true,
                select2Obj: null,

                
                awe: null,
                mapboxAccessToken: null,
                search_box_id: uuidv4(),
                search_input_id: uuidv4(),
                search_address_latlng_text: '',

                //filters
                activity_titles : [],
                application_types : [],
                regions: [],
                proposal_submitters: [],
                proposal_applicants: [],
                proposal_status: [],
                external_status:[
                    {value: 'draft', name: 'Draft'},
                    {value: 'with_assessor', name: 'Under Review'},
                    {value: 'approved', name: 'Approved'},
                    {value: 'declined', name: 'Declined'},
                ],
                internal_status:[
                    {value: 'draft', name: 'Draft'},
                    {value: 'with_assessor', name: 'With Assessor'},
                    {value: 'with_referral', name: 'With Referral'},
                    {value: 'with_assessor_requirements', name: 'With Assessor (Requirements)'},
                    {value: 'with_approver', name: 'With Approver'},
                    {value: 'approved', name: 'Approved'},
                    {value: 'declined', name: 'Declined'},
                    {value: 'discarded', name: 'Discarded'},
                ],
                // satelliteIcon,
                // mapIcon,
            }
        },
        components: {
        },
        props: {
            is_external:{
                type: Boolean,
                default: false
            },
            is_internal:{
                type: Boolean,
                default: false
            },
            can_modify: {
                type: Boolean,
                default: false
            },
            level:{
                type: String,
                required: true,
                validator:function(val) {
                    let options = ['internal','referral','external'];
                    return options.indexOf(val) != -1 ? true: false;
                }
            },
        },
        watch: {
             filterProposalRegion: function () {
                this.applyFiltersFrontEnd();
                this.$emit('filter-appied');
            },
            filterProposalActivity: function () {
                this.applyFiltersFrontEnd();
                //console.log('filterProposalActivity', this.filterProposalActivity)
                this.$emit('filter-appied');
            },
            filterProposalStatus: function () {
                this.applyFiltersFrontEnd();
                this.$emit('filter-appied');
            },
            filterProposalLodgedFrom: function () {
                this.applyFiltersFrontEnd();
                this.$emit('filter-appied');
            },
            filterProposalLodgedTo: function () {
                this.applyFiltersFrontEnd();
                this.$emit('filter-appied');
            },
            filterProposalSubmitter: function () {
                this.applyFiltersFrontEnd();
                this.$emit('filter-appied');
            },
            filterProposalApplicant: function () {
                this.applyFiltersFrontEnd();
                this.$emit('filter-appied');
            },
            filterProposalApplicationType: function () {
                this.applyFiltersFrontEnd();
                this.$emit('filter-appied');
            },
        },
        computed: {
            ruler_colour: function(){
                if (this.mode === 'normal'){
                    return '#aaa';
                } else {
                    return '#53c2cf';
                }
            },
            loading_proposals: function(){
                return false
            },
            csrf_token: function() { 
              return helpers.getCookie('csrftoken') 
            },

        },
        methods: {
            applyFiltersFrontEnd: function () {
                this.filteredProposals = [...this.proposals];
                if ('All' != this.filterProposalRegion) {
                    this.filteredProposals = [...this.filteredProposals.filter(proposal => proposal.region == this.filterProposalRegion)]
                }
                if ('All' != this.filterProposalActivity) {
                    this.filteredProposals = [...this.filteredProposals.filter(proposal => proposal.activity == this.filterProposalActivity)]
                }
                if ('All' != this.filterProposalStatus) {
                    if(this.is_external){
                        this.filteredProposals = [...this.filteredProposals.filter(proposal => proposal.customer_status == this.filterProposalStatus)]
                    }
                    else{
                        this.filteredProposals = [...this.filteredProposals.filter(proposal => proposal.processing_status == this.filterProposalStatus)]
                    }
                }
                if ('' != this.filterProposalLodgedFrom) {
                    this.filteredProposals = [...this.filteredProposals.filter(proposal => new Date(proposal.lodgement_date) >= new Date(this.filterProposalLodgedFrom))]
                }
                if ('' != this.filterProposalLodgedTo) {
                    this.filteredProposals = [...this.filteredProposals.filter(proposal => new Date(proposal.lodgement_date) <= new Date(this.filterProposalLodgedTo))]
                }
                if ('All' != this.filterProposalSubmitter) {
                    this.filteredProposals = [...this.filteredProposals.filter(proposal => proposal.submitter == this.filterProposalSubmitter)]
                }
                if ('All' != this.filterProposalApplicant) {
                    this.filteredProposals = [...this.filteredProposals.filter(proposal => proposal.applicant_id == this.filterProposalApplicant)]
                }
                if ('All' != this.filterProposalApplicationType) {
                    this.filteredProposals = [...this.filteredProposals.filter(proposal => proposal.application_type_name == this.filterProposalApplicationType)]
                }
                this.loadFeatures(this.filteredProposals);
            },
            retrieveMapboxAccessToken: async function(){
                let ret_val = await $.ajax('/api/geocoding_address_search_token')
                return ret_val
            },
            initAwesomplete: function(){
                var vm = this;
                var element_search = document.getElementById(vm.search_input_id);
                this.awe = new Awesomplete(element_search);
                $(element_search).on('keyup', function(ev){
                    var keyCode = ev.keyCode || ev.which;
                    if ((48 <= keyCode && keyCode <= 90)||(96 <= keyCode && keyCode <= 105)||(keyCode===8)||(keyCode===46)){
                        vm.search(ev.target.value);
                        return false;
                    }
                }).on('awesomplete-selectcomplete', function(ev){
                    ev.preventDefault();
                    ev.stopPropagation();

                    let currentZoomLevel = vm.map.getView().getZoom()
                    let targetZoomLevel = 14
                    if (targetZoomLevel < currentZoomLevel){
                        targetZoomLevel = currentZoomLevel
                    }

                    /* User selected one of the search results */
                    for (var i=0; i<vm.suggest_list.length; i++){
                        if (vm.suggest_list[i].value == ev.target.value){
                            var latlng = {lat: vm.suggest_list[i].feature.geometry.coordinates[1], lng: vm.suggest_list[i].feature.geometry.coordinates[0]};
                            zoomToCoordinates(vm.map, [latlng.lng, latlng.lat], targetZoomLevel)
                        }
                    }
                    return false;
                });
            },
            download_content: function (content, fileName, contentType) {
                var a = document.createElement("a");
                var file = new Blob([content], { type: contentType });
                a.href = URL.createObjectURL(file);
                a.download = fileName;
                a.click();
            },
            create_geoJson: function () {
                let vm = this
                // let json = new GeoJSON().writeFeatures(vm.proposalQuerySource.getFeatures(), {})
                // vm.download_content(json, 'DAS_layers.geojson', 'text/plain');
                let features = vm.proposalQuerySource.getFeatures()
                if(features.length>0){
                        features.forEach(function (f){
                            let proposal = f.getProperties().proposal;
                            if(proposal){
                                f.setProperties({
                                    org :       proposal.applicant_name ? proposal.applicant_name : '',
                                    app_no:     proposal.approval_lodgement_number ? proposal.approval_lodgement_number : '',
                                    prop_title: proposal.title ? proposal.title : '',
                                    appissdate: proposal.approval_issue_date ? proposal.approval_issue_date : '',
                                    appstadate: proposal.approval_start_date ? proposal.approval_start_date : '',
                                    appexpdate: proposal.approval_expiry_date ? proposal.approval_expiry_date : '',
                                    //proptype:   proposal.proposal_type ? proposal.proposal_type : '',
                                    proptype:   proposal.proposal_type_name ? proposal.application_type_name : '',
                                    appstatus:  proposal.approval_status ? proposal.approval_status : '',
                                    assocprop:  proposal.assocprop ? proposal.assocprop : '',
                                    propurl:    proposal.proposal_url ? proposal.proposal_url : '',
                                })
                            }
                        });
                    }
                let json = new GeoJSON().writeFeatures(features, {})
                console.log(json)
                vm.download_content(json, 'DAS_layers.geojson', 'text/plain');
                //return new GeoJSON().writeFeatures(features, {})
            },
            geoJsonButtonClicked: function () {
                let vm = this
                let json = vm.create_geoJson();
                vm.download_content(json, 'DAS_layers.geojson', 'text/plain');
            },
            shapefileButtonClicked: function (geojson) {
                let vm = this
                vm.show_spinner = true;
                vm.download_shapefile_btn_disabled = true;
                let url = '/api/proposal/create_shapefile/'

                let filter_kwargs = {}
		if (vm.filterProposalRegion != 'All')        { filter_kwargs['region_id'] = vm.filterProposalRegion; }
		if (vm.filterProposalActivity != 'All')      { filter_kwargs['activity'] = vm.filterProposalActivity; }
		if (vm.filterProposalStatus != 'All')        { filter_kwargs['processing_status'] = vm.filterProposalStatus; }
		if (vm.filterProposalApplicant != 'All')     { filter_kwargs['applicant_id'] = vm.filterProposalApplicant; }
		if (vm.filterProposalSubmitter != 'All')     { filter_kwargs['submitter__email'] = vm.filterProposalSubmitter; }
		if (vm.filterProposalApplicationType!='All') { filter_kwargs['application_type__name'] = vm.filterProposalApplicationType; }
		if (vm.filterProposalLodgedFrom)             { filter_kwargs['lodgement_date__gte'] = vm.filterProposalLodgedFrom; }
		if (vm.filterProposalLodgedTo)               { filter_kwargs['lodgement_date__lte'] = vm.filterProposalLodgedTo; }

                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        geojson: geojson,
                        filter_kwargs: filter_kwargs
                    })
                })
                .then(response => response.json())
                .then(data => {
                    swal.fire({
                        title: 'Create shapefile',
                        html: data.message + "<br> Click <a href='/filelist' target='_blank'> here </a> to view downloaded file",
                        icon: 'success'
                    });
                    vm.show_spinner = false;
                    vm.download_shapefile_btn_disabled = false;
                })
                .catch(error => {
                    swal.fire({
                        title: 'Create shapefile Error',
                        //text: helpers.apiVueResourceError(error),
                        text: error,
                        icon: 'error'
                    });
                    vm.show_spinner = false;
                    vm.download_shapefile_btn_disabled = false;
                });

            },
            exportPNG: function () {
                let vm = this;
                vm.map.once('rendercomplete', function () {
                    const mapCanvas = document.createElement('canvas');
                    const size = vm.map.getSize();
                    mapCanvas.width = size[0];
                    mapCanvas.height = size[1];
                    const mapContext = mapCanvas.getContext('2d');
                    Array.prototype.forEach.call(
                    vm.map.getViewport().querySelectorAll('.ol-layer canvas, canvas.ol-layer'),
                    function (canvas) {
                        if (canvas.width > 0) {
                        const opacity =
                            canvas.parentNode.style.opacity || canvas.style.opacity;
                        mapContext.globalAlpha = opacity === '' ? 1 : Number(opacity);
                        let matrix;
                        const transform = canvas.style.transform;
                        if (transform) {
                            // Get the transform parameters from the style's transform matrix
                            matrix = transform
                            .match(/^matrix\(([^(]*)\)$/)[1]
                            .split(',')
                            .map(Number);
                        } else {
                            matrix = [
                            parseFloat(canvas.style.width) / canvas.width,
                            0,
                            0,
                            parseFloat(canvas.style.height) / canvas.height,
                            0,
                            0,
                            ];
                        }
                        // Apply the transform to the export map context
                        CanvasRenderingContext2D.prototype.setTransform.apply(
                            mapContext,
                            matrix
                        );
                        const backgroundColor = canvas.parentNode.style.backgroundColor;
                        if (backgroundColor) {
                            mapContext.fillStyle = backgroundColor;
                            mapContext.fillRect(0, 0, canvas.width, canvas.height);
                        }
                        mapContext.drawImage(canvas, 0, 0);
                        }
                    }
                    );
                    mapContext.globalAlpha = 1;
                    mapContext.setTransform(1, 0, 0, 1, 0, 0);
                    const link = document.getElementById('image-download');
                    link.href = mapCanvas.toDataURL();
                    link.click();
                });
            vm.map.renderSync();
            },
            
            applySelect2: function(){
                let vm = this

                if (!vm.select2Applied){
                    $(vm.$refs.filterStatus).select2({
                        "theme": "bootstrap",
                        allowClear: false,
                        placeholder:"Select Status",
                        multiple:true,
                        data: vm.filter_status_options,
                        dropdownParent: $('#filters_parent'),
                    }).
                    on('select2:select', function(){
                        
                    }).
                    on('select2:unselect', function(){
                        
                    })

                    $(vm.$refs.filterAvailability).select2({
                        "theme": "bootstrap",
                        allowClear: false,
                        placeholder:"Select Availabilities",
                        multiple:true,
                        data: vm.filter_availability_options,
                        dropdownParent: $('#filters_parent'),
                    }).
                    on("select2:select",function () {
                        
                    }).
                    on("select2:unselect",function () {
                        
                    })
                    vm.select2Applied = true
                }
            },
            clearProposalsFromMap: function(){
                this.proposalQuerySource.clear()
            },
            clearAjaxObjects: function(){
            },
            addProposalsToMap: function(proposal_geojson){
                let features = (new GeoJSON()).readFeatures(proposal_geojson);
                this.proposalQuerySource.addFeatures(features);
            },
            loadFeatures: function (proposals) {
                let vm = this;
                // Remove all features from the layer
                vm.proposalQuerySource.clear();
                proposals.forEach(function (proposal) {
                    let feature = (new GeoJSON()).readFeatures(proposal.shapefile_json);
                     // let f=feature[0]
                    // f.setProperties({
                    //     proposal: proposal,
                    // })
                    if(feature.length>0){
                        feature.forEach(function (f){
                            f.setProperties({
                            proposal: proposal,
                            })
                        });
                    }
                    vm.proposalQuerySource.addFeatures(feature);
                });
            },
            addEventListeners: function () {
                let vm = this

                $("#app").on('click', 'a[data-contact-licence-holder]', this.contactLicenceHolder)

                let search_input_elem = $('#' + vm.search_input_id)
                search_input_elem.on('input', function(ev){
                    vm.search(ev.target.value);
                })
            },
            
            
            toggleStatusFilterDropdown: function(){
                $(".status_filter_dropdown").slideToggle("fast")
            },
            mouseEnter: function(e){
                let vm = this;
                if (!vm.not_close_popup_by_mouseleave){
                    let apiary_site_id = e.currentTarget.getAttribute("data-apiary-site-id");
                    if (apiary_site_id){
                        vm.showPopupById(apiary_site_id)
                    }
                }
            },
            mouseLeave: function(){
                let vm = this;
                if (!vm.not_close_popup_by_mouseleave){
                    vm.closePopup()
                }
            },
            setBaseLayer: function(selected_layer_name){
                let vm = this
                if (selected_layer_name == 'sat') {
                    vm.tileLayerOsm.setVisible(false)
                    vm.tileLayerSat.setVisible(true)
                    $('#basemap_sat').hide()
                    $('#basemap_osm').show()
                } else {
                    vm.tileLayerOsm.setVisible(true)
                    vm.tileLayerSat.setVisible(false)
                    $('#basemap_osm').hide()
                    $('#basemap_sat').show()
                }
            },
            set_mode: function(mode){
                this.mode = mode
                if (this.mode === 'layer'){
                    this.clearMeasurementLayer()
                    this.drawForMeasure.setActive(false)
                } else if (this.mode === 'measure') {
                    this.drawForMeasure.setActive(true)
                }
            },
            addJoint: function(point, styles){
                let s = new Style({
                    image: new CircleStyle({
                        radius: 2,
                        fill: new Fill({
                            color: '#3399cc'
                        }),
                    }),
                })
                s.setGeometry(point)
                styles.push(s)

                return styles
            },
            styleFunctionForMeasurement: function (feature){
                let vm = this
                let for_layer = feature.get('for_layer', false)

                const styles = []
                styles.push(vm.style)  // This style is for the feature itself
                styles.push(vm.segmentStyle)

                ///////
                // From here, adding labels and tiny circles at the end points of the linestring
                ///////
                const geometry = feature.getGeometry();
                if (geometry.getType() === 'LineString'){
                    let segment_count = 0;
                    geometry.forEachSegment(function (a, b) {
                        const segment = new LineString([a, b]);
                        const label = formatLength(segment);
                        const segmentPoint = new Point(segment.getCoordinateAt(0.5));

                        // Add a style for this segment
                        let segment_style = vm.segmentStyle.clone() // Because there could be multilpe segments, we should copy the style per segment
                        segment_style.setGeometry(segmentPoint)
                        segment_style.getText().setText(label)
                        styles.push(segment_style)

                        if (segment_count == 0){
                            // Add a tiny circle to the very first coordinate of the linestring
                            let p = new Point(a)
                            vm.addJoint(p, styles)
                        }
                        // Add tiny circles to the end of the linestring
                        let p = new Point(b)
                        vm.addJoint(p, styles)

                        segment_count++;
                    });
                }

                if (!for_layer){
                    // We don't need the last label when draw on the layer.
                    let label_on_mouse = formatLength(geometry);  // Total length of the linestring
                    let point = new Point(geometry.getLastCoordinate());
                    vm.labelStyle.setGeometry(point);
                    vm.labelStyle.getText().setText(label_on_mouse);
                    styles.push(vm.labelStyle);
                }

                return styles
            },
            clearMeasurementLayer: function(){
                let vm = this
                let features = vm.measurementLayer.getSource().getFeatures()
                features.forEach((feature) => {
                    vm.measurementLayer.getSource().removeFeature(feature)
                })
            },
            changeLayerVisibility: function(targetLayer){
                targetLayer.setVisible(!targetLayer.getVisible())
            },
            addOptionalLayers: function(){
                let vm = this
                fetch('/api/das_map_layers/').then(
                    async response => {
                        if (!response.ok) {
                            return await response.json().then(err => { throw err });
                        }
                        let layers = await response.json();
                        for (var i = 0; i < layers.length; i++ ){
                            let l = new TileWMS({
                                // url: env['kmi_server_url'] + '/geoserver/' + layers[i].layer_group_name + '/wms',
                                //url:'/kb-proxy/geoserver/' + layers[i].layer_group_name + '/wms',
                                url: layers[i].layer_group_name ? '/kb-proxy/geoserver/' + layers[i].layer_group_name + '/wms' : '/kb-proxy/geoserver/wms',
                                //url:'/kmi-proxy/geoserver/' + layers[i].layer_group_name + '/wms',
                                params: {
                                    'FORMAT': 'image/png',
                                    'VERSION': '1.1.1',
                                    tiled: true,
                                    STYLES: '',
                                    LAYERS: layers[i].layer_full_name
                                },
                                //crossOrigin: 'Anonymous',
                            });

                            let tileLayer= new TileLayer({
                                title: layers[i].display_name.trim(),
                                visible: false,
                                source: l,
                            })

                            // Set additional attributes to the layer
                            tileLayer.set('columns', layers[i].columns)
                            tileLayer.set('display_all_columns', layers[i].display_all_columns)

                            vm.optionalLayers.push(tileLayer)
                            vm.map.addLayer(tileLayer)
                        }
                    }).catch((error) => {
                        console.log(error);
                    }
                )
            },
            closePopup: function(){
                this.content_element.innerHTML = null
                this.overlay.setPosition(undefined)
                this.not_close_popup_by_mouseleave = false
                //this.$emit('popupClosed')
            },
            forceToRefreshMap: function() {
                let vm = this
                setTimeout(function(){
                    vm.map.updateSize();
                }, 50)
            },
            
            initMap: function() {
                let vm = this;
                // var ol = {'proj': proj, 'extent': Extent,}
                var projection = getProjection("EPSG:3857");
                var projectionExtent = projection.getExtent();
                var s = getWidth(projectionExtent) / 256;
                var matrixSet = "mercator";
                var resolutions = new Array(21);
                var matrixIds = new Array(21);
                
                for (var c = 0; c < 21; ++c)
                    resolutions[c] = s / Math.pow(2, c),
                    matrixIds[c] = matrixSet + ":" + c;
                
                var m = new WMTSTilegrid({
                    origin: getTopLeft(projectionExtent),
                    resolutions: resolutions,
                    matrixIds: matrixIds
                });
                
                let satelliteTileWms = new TileWMS({
                    url: env['kb_server_url'] + '/geoserver/kaartdijin-boodja-public/wms',
                    params: {
                        'FORMAT': 'image/png',
                        'VERSION': '1.1.1',
                        tiled: true,
                        STYLES: '',
                        LAYERS: 'kaartdijin-boodja-public:mapbox-satellite-public',
                    },
                });
                vm.tileLayerOsmWorking= new TileLayer({
                    name: "street",
                    canDelete: "no",
                    visible: !0,
                    source: new WMTS({
                        // url: "https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts",
                        url: "/kb-proxy/geoserver/gwc/service/wmts",
                        format: "image/png",
                        layer: "kaartdijin-boodja-public:mapbox-streets-public",
                        matrixSet: matrixSet,
                        projection: 'EPSG:3857',
                        tileGrid: m,
                        //crossOrigin: 'Anonymous'
                    })

                        // url: "https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts",
                        // format: "image/png",
                        // layer: "kaartdijin-boodja-public:mapbox-streets-public",
                        // style: 'default',
                        // projection: 'EPSG:3857',
                    })
                
                let streetsTileWMS = new TileWMS({
                url: env['kb_server_url'] + '/geoserver/kaartdijin-boodja-public/wms',
                params: {
                    FORMAT: 'image/png',
                    VERSION: '1.1.1',
                    tiled: true,
                    STYLES: '',
                    LAYERS: "kaartdijin-boodja-public:mapbox-streets-public",
                },
                });
                
                vm.tileLayerOsm= new TileLayer({
                    name: "street",
                    canDelete: "no",
                    visible: !0,
                    type: 'base',
                    source: streetsTileWMS,
                    }),

                // vm.tileLayerOsm = new TileLayer({
                //     title: 'OpenStreetMap',
                //     type: 'base',
                //     visible: true,
                //     source: new OSM(),
                // });

                vm.tileLayerSat = new TileLayer({
                    title: 'Satellite',
                    type: 'base',
                    visible: true,
                    source: satelliteTileWms,
                })

                vm.map = new Map({
                    layers: [
                        toRaw(vm.tileLayerOsm), 
                        toRaw(vm.tileLayerSat),
                    ],
                    //target: 'map',
                    target: vm.elem_id,
                    view: new View({
                        center: [115.95, -31.95],
                        zoom: 7,
                        projection: 'EPSG:4326'
                    }),
                    pixelRatio: 1,  // We need this in order to make this map work correctly with the browser and/or display scaling factor(s) other than 100%
                                    // Ref: https://github.com/openlayers/openlayers/issues/11464
                });

                vm.proposalQuerySource = new VectorSource({ });                

                let clusterSource = new Cluster({
                    distance: 50,
                    source: vm.proposalQuerySource,
                    geometryFunction: (feature) => {
                        // let resolution = this.map.getView().getResolution();
                        
                            let type = feature.getGeometry().getType();
                            if (type === 'Polygon') {
                                return feature.getGeometry().getInteriorPoint();

                            } else if (type === 'LineString') {
                                return feature.getGeometry().getCoordinateAt(0.5);

                            } else if (type === 'Point') {
                                return feature.getGeometry();
                            } else if (type === 'MultiPolygon') {
                                return new Point(getCenter(feature.getGeometry().getExtent()), 'XY');
                            }
                       
                    },
                })

                let styleCache = {}
                let sameFeature=false;
                var zoomedInStyle = new Style({
                    stroke: new Stroke({
                        color: 'orange',
                        width: 3
                    }),
                    fill: new Fill({
                        color: 'rgba(255, 165, 0, 0.1)'
                    }),
                    geometry: function(feature){
                        var originalFeature = feature.get('features');
                        return originalFeature[0].getGeometry();
                    }
                    });
                    styleCache[1]=zoomedInStyle;
                vm.proposalClusterLayer = new VectorLayer({
                    title: 'Cluster Layer',
                    source: clusterSource,
                    
                    style: function (clusteredFeature){
                        let featuresInClusteredFeature = clusteredFeature.get('features')
                        let size = featuresInClusteredFeature.length
                        let style = styleCache[size]
                        //if(size == 1 || sameFeature){
                        if(size == 1 ){
                        //if(size <= 2){
                            // When size is 1, which means the cluster feature has only one site
                            // we want to display it as dedicated style
                            // let status = getStatusForColour(featuresInClusteredFeature[0])
                            // return getApiaryFeatureStyle(status);
                            return zoomedInStyle;
                        }
                        let radius_in_pixel = 16
                        if(size < 10){
                            radius_in_pixel = 10
                        } else if (size < 100){
                            radius_in_pixel = 12
                        } else if (size < 1000){
                            radius_in_pixel = 14
                        }
                        if(!style){
                            style = new Style({
                                image: new CircleStyle({
                                    radius: radius_in_pixel,
                                    stroke: new Stroke({
                                        color: '#fff',
                                    }),
                                    fill: new Fill({
                                        color: '#3399cc'
                                    }),
                                }),
                                text: new Text({
                                    text: size.toString(),
                                    fill: new Fill({
                                        color: '#fff',
                                    })
                                }), 
                            })
                            styleCache[size] = style
                        }
                        return style
                    },
                });
                vm.map.addLayer(vm.proposalClusterLayer);
                vm.proposalClusterLayer.setZIndex(10)  

                //PA code begin
                
                vm.newVectorLayer = new VectorLayer({
                    source: vm.proposalQuerySource,
                    //name: 'layer1',
                    visible: true,
                    maxResolution: 10
                });
                
                //let styleCache = {};
                vm.newVectorLayerCluster = new VectorLayer({
                    source: new Cluster({
                        distance: 50,
                        source: vm.proposalQuerySource,
                        geometryFunction: (feature) => {
                            let resolution = this.map.getView().getResolution();
                            if (resolution < 0.05 && resolution > 0.0001){
                                let type = feature.getGeometry().getType();
                                if (type === 'Polygon') {
                                    return feature.getGeometry().getInteriorPoint();

                                } else if (type === 'LineString') {
                                    return feature.getGeometry().getCoordinateAt(0.5);

                                } else if (type === 'Point') {
                                    return feature.getGeometry();
                                } else if (type === 'MultiPolygon') {
                                    return new Point(getCenter(feature.getGeometry().getExtent()), 'XY');
                                }
                            }
                        }
                    }),
                    style: (feature) => {
                        let size = feature.get('features').length;
                        let style = styleCache[size];
                        if (!style) {
                            style = new Style({
                                image: new CircleStyle({
                                    radius: 10,
                                    stroke: new Stroke({
                                        color: '#fff',
                                    }),
                                    fill: new Fill({
                                        color: '#3399CC',
                                    }),
                                }),
                                text: new Text({
                                    text: size.toString(),
                                    fill: new Fill({
                                        color: '#fff',
                                    }),
                                })
                            });
                            styleCache[size] = style;
                        }
                        return style;
                    },
                    //name: layer['layer_id'],
                    // name: 'layer1',
                    //visible: false
                });

                //PA code end

                // Full screen toggle
                let fullScreenControl = new FullScreenControl()
                fullScreenControl.on('enterfullscreen', function(){
                    vm.fullscreen = true
                })
                fullScreenControl.on('leavefullscreen', function(){
                    vm.fullscreen = false
                })
                vm.map.addControl(fullScreenControl)

                // Measure tool
                let draw_source = new VectorSource({ wrapX: false })
                vm.drawForMeasure = new Draw({
                    source: draw_source,
                    type: 'LineString',
                    style: vm.styleFunctionForMeasurement,
                })
                // Set a custom listener to the Measure tool
                vm.drawForMeasure.set('escKey', '')
                vm.drawForMeasure.on('change:escKey', function(){
                    //vm.drawForMeasure.finishDrawing()
                })
                vm.drawForMeasure.on('drawstart', function(){
                    vm.measuring = true
                })
                vm.drawForMeasure.on('drawend', function(){
                    vm.measuring = false
                })

                // Create a layer to retain the measurement
                vm.measurementLayer = new VectorLayer({
                    title: 'Measurement Layer',
                    source: draw_source,
                    style: function(feature, resolution){
                        feature.set('for_layer', true)
                        return vm.styleFunctionForMeasurement(feature, resolution)
                    },
                });
                vm.map.addInteraction(vm.drawForMeasure)
                vm.map.addLayer(vm.measurementLayer)

                // Show mouse coordinates
                vm.map.addControl(new MousePositionControl({
                    coordinateFormat: function(coords){
                        let message = vm.getDegrees(coords) + "\n";
                        return  message;
                    },
                    target: document.getElementById('mouse-position'),
                    className: 'custom-mouse-position',
                }));

                let container = document.getElementById(vm.popup_id)
                vm.content_element = document.getElementById(vm.popup_content_id)
                let closer = document.getElementById(vm.popup_closer_id)

                vm.overlay = new Overlay({
                    element: container,
                    autoPan: false,
                    offest: [0, -10]
                })

                closer.onclick = function() {
                    vm.closePopup()
                    closer.blur()
                    return false
                }

                vm.map.addOverlay(vm.overlay)

                vm.map.on('singleclick', function(evt){
                    if (vm.mode === 'layer'){
                        let feature = vm.map.forEachFeatureAtPixel(evt.pixel, function(feature) {
                            return feature;
                            
                        });
                        if (feature){
                            let features = feature.get('features')
                            if (features.length == 1){
                                if (!feature.id){
                                    // When the Modify object is used for the layer, 'feature' losts some of the attributes including 'id', 'status'...
                                    // Therefore try to get the correct feature by the coordinate
                                    let geometry = feature.getGeometry();
                                    let coord = geometry.getCoordinates();
                                    feature = vm.proposalQuerySource.getFeaturesAtCoordinate(coord)
                                }
                                // let proposal = features[0].getProperties().proposal;
                                vm.showPopup(feature[0])
                            } else {
                                //if proposal id is different but geometry is exactly same
                                sameFeature = false;
                                for(var i=0; i<features.length; i++ ){
                                    let formatwkt = new formatWKT();
                                    let feature1 = formatwkt.writeGeometry(features[0].getGeometry());
                                    let feature2 = formatwkt.writeGeometry(features[i].getGeometry());
                                    if(feature1==feature2){
                                        sameFeature=true;
                                    }
                                    else{
                                        sameFeature=false;
                                        break;
                                    }     
                                }
                                if(sameFeature){
                                        //vm.proposalClusterLayer.setStyle(zoomedInStyle);
                                        vm.showPopupforSameFeatures(features)
                                        //vm.showPopup(features[0])
                                }
                                else{
                                    //else keep zooming in
                                    let geometry = feature.getGeometry();
                                    let coordinates = geometry.getCoordinates();
                                    let currentZoomLevel = vm.map.getView().getZoom()
                                    zoomToCoordinates(vm.map, coordinates, currentZoomLevel + 1)
                                }
                                //end
                                // //else keep zooming in
                                // let geometry = feature.getGeometry();
                                // let coordinates = geometry.getCoordinates();
                                // let currentZoomLevel = vm.map.getView().getZoom()
                                // zoomToCoordinates(vm.map, coordinates, currentZoomLevel + 1)
                            }
                        } else {
                            vm.closePopup()
                            let view = vm.map.getView()
                            let viewResolution = view.getResolution()

                            // Retrieve active layers' sources
                            for (let i=0; i < vm.optionalLayers.length; i++){
                                let visibility = vm.optionalLayers[i].getVisible()
                                if (visibility){
                                    // Retrieve column names to be displayed
                                    let column_names = vm.optionalLayers[i].get('columns')
                                    column_names = column_names.map(function(col){
                                        // Convert array of dictionaries to simple array
                                        if (vm.is_internal && col.option_for_internal){
                                            return col.name
                                        }
                                        if (vm.is_external && col.option_for_external){
                                            return col.name
                                        }
                                    })
                                    // Retrieve the value of display_all_columns boolean flag
                                    let display_all_columns = vm.optionalLayers[i].get('display_all_columns')

                                    // Retrieve the URL to query the attributes
                                    let source = vm.optionalLayers[i].getSource()
                                    let url = source.getFeatureInfoUrl(
                                        evt.coordinate, viewResolution, view.getProjection(),
                                        //{'INFO_FORMAT': 'text/html'}
                                        {'INFO_FORMAT': 'application/json'}
                                    )

                                    // Query 
                                    let p = fetch(url, {
                                        credentials: 'include'
                                    })

                                    p.then(async (res) => await res.json()).then(function(data){
                                        vm.showPopupForLayersJson(data, evt.coordinate, column_names, display_all_columns, vm.optionalLayers[i])
                                    })
                                }
                            }
                        }
                    } else if (vm.mode === 'measure'){
                        // When in measure mode, the styleFunction() is responsible for the drawing
                    }
                })
                vm.map.on('pointermove', function(e) {
                    if (e.dragging) return;
                    let pixel = vm.map.getEventPixel(e.originalEvent);
                    let hit = vm.map.hasFeatureAtPixel(pixel);
                    vm.map.getTargetElement().style.cursor = hit ? 'pointer' : '';
                });
                vm.map.on('moveend', function(){
                    let extent = vm.map.getView().calculateExtent(vm.map.getSize());
                    let features = vm.proposalQuerySource.getFeaturesInExtent(extent)
                    vm.$emit('featuresDisplayed', features)
                });
                //vm.map.on('postrender', function(){
                //   console.log('postrender')
                //});
                //vm.map.on('loadstart', function(){
                //   console.log('loadstart')
                //});
                //vm.map.on('loadend', function(){
                //   console.log('loadend')
                //});
                if (vm.can_modify){
                    let modifyTool = new Modify({
                        source: vm.proposalQuerySource,
                    });
                    modifyTool.on("modifystart", function(attributes){
                            attributes.features.forEach(function(){
                        })
                    });
                    modifyTool.on("modifyend", function(attributes){
                        attributes.features.forEach(function(feature){
                            let id = feature.getId();
                            let index = vm.modifyInProgressList.indexOf(id);
                            if (index != -1) {
                                // feature has been modified
                                vm.modifyInProgressList.splice(index, 1);
                                let coords = feature.getGeometry().getCoordinates();
                                vm.$emit('featureGeometryUpdated', {'id': id, 'coordinates': {'lng': coords[0], 'lat': coords[1]}})
                            }
                        });
                    });
                    vm.map.addInteraction(modifyTool);
                }
                document.addEventListener('keydown', vm.keydown, false)
            },
            keydown: function(evt){
                let vm = this

                let charCode = (evt.which) ? evt.which : evt.keyCode;
                if (charCode === 27 && vm.measuring === true){ //esc key
                    //dispatch event
                    this.drawForMeasure.set('escKey', Math.random());
                }
            },
            showPopupById: function(apiary_site_id){
                let feature = this.proposalQuerySource.getFeatureById(apiary_site_id)
                this.showPopup(feature)
            },
            
            showPopup: function(feature){
                let unique_id = uuidv4()
                // let proposal = feature.getProperties().proposal;
                // console.log('selected proposal', proposal);

                if (feature){
                    let geometry = feature.getGeometry();
                    let coord = geometry.getCoordinates();
                    let proposal = feature.getProperties().proposal;
                    let type = feature.getGeometry().getType();
                    if (type === 'Polygon') {
                        coord= feature.getGeometry().getInteriorPoint();
                    } else if (type === 'LineString') {
                        coord= feature.getGeometry().getCoordinateAt(0.5);
                    } else if (type === 'Point') {
                        coord= feature.getGeometry();
                    } else if (type === 'MultiPolygon') {
                        coord= new Point(getCenter(feature.getGeometry().getExtent()), 'XY');
                    }
                    coord=coord.getCoordinates();
                    let processing_status_str = proposal.processing_status_display
                    let customer_status_str = proposal.customer_status_display
                    let region_str = proposal.region_name
                    
                    //let proposal_type_str= proposal.proposal_type
                    let proposal_type_str= proposal.application_type_name
                    let lodgement_date_str= proposal.lodgement_date ? moment(proposal.lodgement_date).format('DD/MM/YYYY') : ''
                    let submitter_str=proposal.submitter_full_name
                    let applicant_name=proposal.applicant_name
                    let approval_rows=''
                    if(proposal.approval_lodgement_number){
                        approval_rows= '<tr>' +
                                  '<th scope="row">Approval</th>' +
                                  '<td>' + 
                                        '<table class="table">' +
                                        '<tbody>' +
                                        '<tr>' +
                                        '<th scope="row">Status</th>' +
                                        '<td>' + proposal.approval_status + '</td>' +
                                        '</tr>' +
                                        '<tr>' +
                                        '<th scope="row">Start Date</th>' +
                                        '<td>' + moment(proposal.approval_start_date).format('DD/MM/YYYY') + '</td>' +
                                        '</tr>' +
                                        '<tr>' +
                                        '<th scope="row">Expiry date</th>' +
                                        '<td>' + moment(proposal.approval_expiry_date).format('DD/MM/YYYY') + '</td>' +
                                        '</tr>' +
                                        '</tbody>' +
                                        '</table>'
                                  '</td>' +
                                '</tr>' 
                        
                    }
                    let a_table = ''
                    if (this.is_internal){
                        a_table = '<table class="table">' +
                              '<tbody>' +
                                '<tr>' +
                                  '<th scope="row">Proponent</th>' +
                                  '<td><span id=' + unique_id + '></span>'+ applicant_name+ '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Region</th>' +
                                  '<td>' + region_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Proposal Type</th>' +
                                  '<td>' + proposal_type_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Lodgement Date</th>' +
                                  '<td>' + lodgement_date_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Status</th>' +
                                  '<td>' + processing_status_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Submitter</th>' +
                                  '<td>' + submitter_str + '</td>' +
                                '</tr>' + 
                                approval_rows +
                              '</tbody>' +
                            '</table>'
                    } else if (this.is_external){
                        a_table = '<table class="table">' +
                              '<tbody>' +
                                '<tr>' +
                                  '<th scope="row">Proponent</th>' +
                                  '<td><span id=' + unique_id + '></span>'+ applicant_name+ '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Region</th>' +
                                  '<td>' + region_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Proposal Type</th>' +
                                  '<td>' + proposal_type_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Lodgement Date</th>' +
                                  '<td>' + lodgement_date_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Status</th>' +
                                  '<td>' + customer_status_str + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                  '<th scope="row">Submitter</th>' +
                                  '<td>' + submitter_str + '</td>' +
                                '</tr>' + 
                                approval_rows +
                              '</tbody>' +
                            '</table>'
                    }

                    let content = '<div style="padding: 0.25em;">' +
                                      '<div style="background: darkgray; color: white; text-align: center; padding: 0.5em;" class="align-middle">' + ' Proposal: ' + proposal.lodgement_number + '</div>' +
                                      a_table +
                                  '</div>'

                    this.content_element.innerHTML = content;
                    this.overlay.setPosition(coord);
                }
            },
            showPopupforSameFeatures: function(features){
                // let unique_id = uuidv4()
                // let proposal = feature.getProperties().proposal;
                // console.log('selected proposal', proposal);
                let proposal_rows='';
                for (let feature of features){
                    if (feature){
                        // let geometry = feature.getGeometry();
                        // let coord = geometry.getCoordinates();
                        let proposal = feature.getProperties().proposal;
                        // let type = feature.getGeometry().getType();
                        // if (type === 'Polygon') {
                        //     coord= feature.getGeometry().getInteriorPoint();
                        // } else if (type === 'LineString') {
                        //     coord= feature.getGeometry().getCoordinateAt(0.5);
                        // } else if (type === 'Point') {
                        //     coord= feature.getGeometry();
                        // } else if (type === 'MultiPolygon') {
                        //     coord= new Point(getCenter(feature.getGeometry().getExtent()), 'XY');
                        // }
                        // coord=coord.getCoordinates();
                        let processing_status_str = proposal.processing_status_display
                        // let customer_status_str = proposal.customer_status_display
                        let region_str = proposal.region_name
                        
                        //let proposal_type_str= proposal.proposal_type
                        let proposal_type_str= proposal.application_type_name
                        // let lodgement_date_str= proposal.lodgement_date ? moment(proposal.lodgement_date).format('DD/MM/YYYY') : ''
                        let submitter_str=proposal.submitter_full_name
                        // let applicant_name=proposal.applicant_name
                        let url = this.is_internal ? '/internal/proposal/' + proposal.id : '/external/proposal/' + proposal.id  
                        let proposal_row='<tr>' +
                                  '<td>' +proposal.lodgement_number + '</td>' +
                                //   '<td><span id=' + unique_id + '></span>'+ applicant_name+ '</td>' +
                                  '<td>' + region_str + '</td>' +
                                  '<td>' + proposal_type_str + '</td>' +
                                  '<td>' + processing_status_str + '</td>' +
                                  '<td>' + submitter_str + '</td>' +
                                  '<td>'+ '<a href="' + url + '">View</a>'
                                '</tr>'
                        proposal_rows=proposal_rows + proposal_row; 
                        
                    }
                }
                let a_table = '';
                if(features){

               
                        a_table = '<table class="table">' +
                              '<tbody>' +
                                '<tr>' +
                                  '<th scope="row">Proposal</th>' +
                                //   '<th scope="row">Applicant</th>' +
                                  '<th scope="row">Region</th>' +
                                  '<th scope="row">Proposal Type</th>' +
                                  '<th scope="row">Status</th>' +
                                  '<th scope="row">Submitter</th>' +
                                  '<th scope="row">Link</th>' +
                                '</tr>' +
                                proposal_rows+
                              '</tbody>' +
                            '</table>'
                        let geometry = features[0].getGeometry();
                        let coord = geometry.getCoordinates();
                        let type = features[0].getGeometry().getType();
                        if (type === 'Polygon') {
                            coord= features[0].getGeometry().getInteriorPoint();
                        } else if (type === 'LineString') {
                            coord= features[0].getGeometry().getCoordinateAt(0.5);
                        } else if (type === 'Point') {
                            coord= features[0].getGeometry();
                        } else if (type === 'MultiPolygon') {
                            coord= new Point(getCenter(features[0].getGeometry().getExtent()), 'XY');
                        }
                        coord=coord.getCoordinates();
                        let content = '<div style="padding: 0.25em;">' +
                                        '<div style="background: darkgray; color: white; text-align: center; padding: 0.5em;" class="align-middle">' +' Proposal: '+ '</div>' +
                                        a_table +
                                    '</div>'

                        this.content_element.innerHTML = content;
                        this.overlay.setPosition(coord);
                 }
            },
            showPopupForLayersJson: function(geojson, coord, column_names, display_all_columns, target_layer){
                let wrapper = $('<div>')  // Add wrapper element because html() used at the end exports only the contents of the jquery object
                let caption = $('<div style="text-align:center; font-weight: bold;">').text(target_layer.get('title'))
                let table = $('<table style="margin-bottom: 1em;">') //.addClass('table')
                let tbody = $('<tbody>')
                wrapper.append(caption)
                wrapper.append(table.append(tbody))

                for (let feature of geojson.features){
                    for (let key in feature.properties){
                        if (display_all_columns || column_names.includes(key)){
                            let tr = $('<tr style="border-bottom:1px solid lightgray;">')
                            let th = $('<th style="padding:0 0.5em;">').text(key)
                            let td = $('<td>').addClass('text-nowrap').text(feature.properties[key])
                            tr.append(th)
                            tr.append(td)
                            tbody.append(tr)
                        }
                    }
                    this.content_element.innerHTML += wrapper.html()  // Export contents as HTML string
                    this.overlay.setPosition(coord);
                }
            },
            showPopupForLayersHTML: function(html_str, coord, column_names, display_all_columns){
                // Generate jquery object from html_str
                let html_obj = $('<div>').html(html_str)

                // Retrieve tables as jquery object
                let tables = html_obj.find("table")

                if (!display_all_columns){
                    // Hide all columns
                    tables.find('th,td').css('display', 'none')

                    // Make a certain column visible
                    for (let i=0; i<column_names.length; i++){
                        let index = tables.find('th').filter(function(){
                            // <th> element whoose text is exactly same as column_names[i]
                            return $(this).text() === column_names[i]
                        }).css('display', '').index()

                        let idx = index + 1

                        // Display <td> in the same column
                        let td = tables.find('td:nth-child(' + idx + ')')
                        td.css('display', '')
                    }
                }

                if (tables.length){
                    this.content_element.innerHTML += html_obj.html()
                    this.overlay.setPosition(coord);
                }
            },
            getDegrees: function(coords){
                return coords[0].toFixed(6) + ', ' + coords[1].toFixed(6);
            },
            displayAllFeatures: function() {
                if (this.proposalQuerySource.getFeatures().length>0){
                    let view = this.map.getView()

                    let ext = this.proposalQuerySource.getExtent()
                    let centre = [(ext[0] + ext[2])/2.0, (ext[1] + ext[3])/2.0]
                    //view.fit(ext)
                    let resolution = view.getResolutionForExtent(ext);
                    let z = view.getZoomForResolution(resolution) - 1
                    view.animate({zoom: z, center: centre})
                }
            },
            displayAllFeaturesNew: function(querySource) {
                if (querySource.getFeatures().length>0){
                    let view = this.map.getView()

                    let ext = querySource.getExtent()
                    let centre = [(ext[0] + ext[2])/2.0, (ext[1] + ext[3])/2.0]
                    //view.fit(ext)
                    let resolution = view.getResolutionForExtent(ext);
                    let z = view.getZoomForResolution(resolution) - 1
                    view.animate({zoom: z, center: centre})
                }
            },

            contactLicenceHolder: function(e){
                //let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                // let apiary_site_id = e.target.getAttribute("data-contact-licence-holder");
                e.stopPropagation()
            },
            fetchFilterLists: function(){
                let vm = this;

                fetch(api_endpoints.filter_list_map).then(
                    async (response) => {
                        if (!response.ok) {
                            return await response.json().then(err => { throw err });
                        }
                        let filter_lists = await response.json();
                        vm.regions = filter_lists.regions;
                        vm.activity_titles = filter_lists.activities;
                        vm.application_types = filter_lists.application_types;
                        vm.proposal_submitters = filter_lists.submitters;
                        vm.proposal_applicants = filter_lists.applicants;
                        //vm.proposal_status = response.body.processing_status_choices;
                        vm.proposal_status = vm.level == 'internal' ? vm.internal_status: vm.external_status;
                    }).catch((error) => {
                        console.log(error);
                    });
                //console.log(vm.regions);
            },
            fetchProposals: async function(){
                let vm=this;
                // let _ajax_obj=null;
                var ajax_data={"proposal_status": 'All'}
                let url = api_endpoints.das_map_proposal 
                $.ajax({
                            url: url,
                            
                            //type:'GET',
                            
                            data: ajax_data,
                            dataType: 'json',
                            success: function(re){
                                vm.proposals = re;
                                vm.filteredProposals = [...vm.proposals]
                                // for (let proposal of re){
                                //     vm.addProposalsToMap(proposal.shapefile_json);

                                // }
                                vm.loadFeatures(vm.proposals);
                            },
                            error: function (jqXhr, textStatus, errorMessage) { // error callback
                                console.log(errorMessage);
                            }
                        })
            },//End fetch_ajax_data
            showOptions() {
                this.hover = true;
            },
            hideOptions() {
                this.hover = false;
            },
        },
        
        created: async function() {
            let temp_token = await this.retrieveMapboxAccessToken()
            this.mapboxAccessToken = temp_token.access_token
        },
        mounted: function() {
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners()
            });
            vm.initMap()
            vm.fetchProposals()
            vm.fetchFilterLists();
            vm.setBaseLayer('osm')
            vm.set_mode('layer')
            vm.addOptionalLayers()
            vm.displayAllFeatures()
            //vm.applySelect2()
            //vm.showHideApiarySites()
            //vm.initAwesomplete()
        },
    }
</script>

<style lang="css" scoped>
    @import '../apiary/map_address_search_scoped.css';

    .map-wrapper {
        position: relative;
        padding: 0;
        margin: 0;
    }
    #filter_search_on_map {
        position: absolute;
        top: 10px;
        left: 60px;
        z-index: 99999;
    }
    .basemap-button {
        position: absolute;
        bottom: 25px;
        right: 10px;
        z-index: 400;
        -moz-box-shadow: 3px 3px 3px #777;
        -webkit-box-shadow: 3px 3px 3px #777;
        box-shadow: 3px 3px 3px #777;
        -moz-filter: brightness(1.0);
        -webkit-filter: brightness(1.0);
        filter: brightness(1.0);
        border: 2px white solid;
    }
    .basemap-button:hover,.optional-layers-button:hover{
        cursor: pointer;
        -moz-filter: brightness(0.9);
        -webkit-filter: brightness(0.9);
        filter: brightness(0.9);
    }
    .basemap-button:active {
        bottom: 24px;
        right: 9px;
        -moz-box-shadow: 2px 2px 2px #555;
        -webkit-box-shadow: 2px 2px 2px #555;
        box-shadow: 2px 2px 2px #555;
        -moz-filter: brightness(0.8);
        -webkit-filter: brightness(0.8);
        filter: brightness(0.8);
    }
    .optional-layers-wrapper {
        position: absolute;
        top: 70px;
        left: 10px;
    }
    .optional-layers-button {
        position: relative;
        z-index: 400;
        background: white;
        border-radius: 2px;
        border: 3px solid rgba(5, 5, 5, .1);
        margin-bottom: 2px;
        cursor: pointer;
        display: block;
    }
    .layer_options {
        position: absolute;
        max-height: 400px;
        overflow-y: auto;
        top: 0;
        left: 0;
        z-index: 410;
        background: white;
        border-radius: 2px;
        cursor: auto;
        min-width: max-content;
        /*
        box-shadow: 3px 3px 3px #777;
        -moz-filter: brightness(1.0);
        -webkit-filter: brightness(1.0);
        */
        padding: 0.5em;
        border: 3px solid rgba(5, 5, 5, .1);
    }
    .ol-popup {
        position: absolute;
        min-width: 95px;
        background-color: white;
        -webkit-filter: drop-shadow(0 1px 4px rgba(0,0,0,0.2));
        filter: drop-shadow(0 1px 4px rgba(0,0,0,0.2));
        padding: 2px;
        border-radius: 4px;
        border: 1px solid #ccc;
        bottom: 12px;
        left: -50px;
    }
    .ol-popup:after, .ol-popup:before {
        top: 100%;
        border: solid transparent;
        content: " ";
        height: 0;
        width: 0;
        position: absolute;
        pointer-events: none;
    }
    .ol-popup:after {
        border-top-color: white;
        border-width: 10px;
        left: 48px;
        margin-left: -10px;
    }
    .ol-popup:before {
        border-top-color: #cccccc;
        border-width: 11px;
        left: 48px;
        margin-left: -11px;
    }
    .ol-popup-closer {
        text-decoration: none;
        position: absolute;
        top: 2px;
        right: 8px;
    }
    .ol-layer canvas {
        transform: none !important;
    }
    .close-icon:hover {
        filter: brightness(80%);
    }
    .close-icon {
        position: absolute;
        left: 1px;
        top: -11px;
        filter: drop-shadow(0 1px 4px rgba(0,0,0,0.2));
    }
    .popup-wrapper {
        padding: 0.25em;
    }
    .popup-content-header {
        background: darkgray;
        color: white;
    }
    .popup-content {
        font-size: small;
    }
    .table_caption {
        color: green;
    }
    .layer_option:hover {
        cursor: pointer;
    }
    .filter_search_wrapper {
        position: relative;
        z-index: 1100;
    }
    /*
    .table_apiary_site {
        position: relative;
        z-index: 10;
    }
    */
    .button_row {
        display: flex;
        justify-content: flex-end;
    }
    .view_all_button {
        color: #03a9f4;
        cursor: pointer;
    }
    .status_filter_dropdown_wrapper {
        position: relative;
    }
    .status_filter_dropdown_button {
        cursor: pointer;
        width: 100%;
        position: relative;
    }
    .status_filter_dropdown {
        position: absolute;
        background: white;
        display: none;
        border-radius: 2px;
        min-width: max-content;
        padding: 0.5em;
        border: 3px solid rgba(5, 5, 5, .1);
    }
    .sub_option {
        margin-left: 1em;
    }
    .dropdown_arrow::after {
        content: "";
        width: 7px;
        height: 7px;
        border: 0px;
        border-bottom: solid 2px #909090;
        border-right: solid 2px #909090;
        -ms-transform: rotate(45deg);
        -webkit-transform: rotate(45deg);
        transform: rotate(45deg);
        position: absolute;
        top: 50%;
        right: 21px;
        margin-top: -4px;
    }
    /*
    .status_filter_dropdown {
        position: absolute;
        display: none;
        background: white;
        padding: 1em;
    }
    */
    .select2-container {
        z-index: 100000;
    }
    .select2-options {
        z-index: 100000;
    }
    .dataTables_filter {
        display: none !important;
    }
    .spinner_on_map {
        position: absolute;
        top: 10%;
        left: 50%;
        z-index: 100000;
    }
    .map {
        width: 100%;
        height: 500px;
    }
</style>

<style>
    @import '../apiary/map_address_search.css'
</style>
