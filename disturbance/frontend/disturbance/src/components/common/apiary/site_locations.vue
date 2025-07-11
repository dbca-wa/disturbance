<template lang="html">
    <div>
        <div class="row col-sm-12">
            Mark the location of the new proposed site either by entering the latitude and longitude or by clicking the location in the map.
        </div>

        <div class="row col-sm-12 manual_coordinate_section mt-2 mb-4">
            <label class="inline grow1">Latitude:</label>
            <input
                type="number"
                min="-36"
                max="-12"
                class="form-control grow1 ml-1"
                v-model.number="proposal.proposal_apiary.latitude"
                :readonly="readonly"
            />
            <label class="inline grow1 ml-2">Longitude:</label>
            <input
                type="number"
                min="110"
                max="129"
                class="form-control grow1 ml-1"
                v-model.number="proposal.proposal_apiary.longitude"
                :readonly="readonly"
            />
            <input
                v-if="!readonly"
                type="button"
                @click="tryCreateNewSiteFromForm"
                value="Add proposed site"
                class="btn btn-primary grow1 ml-3"
            />
        </div>

        <template v-if="display_debug_info && proposal && proposal.proposal_apiary">
            <div class="row col-sm-12 debug-info">
                <div>
                    <div><strong>New</strong></div>
                    <div>
                        <div>Previously paid sites 'South West' region: {{ num_of_sites_remain_south_west }} (${{ fee_south_west }})</div>
                        <div>Total fee: {{ total_fee_south_west }}</div>
                    </div>
                    <div>
                        <div>Previously paid sites 'Remote' region: {{ num_of_sites_remain_remote }} (${{ fee_remote }})</div>
                        <div>Total fee: {{ total_fee_remote }}</div>
                    </div>
                    <div><strong>Renewal</strong></div>
                    <div>
                        <div>Previously paid sites 'South West' region: {{ num_of_sites_remain_south_west_renewal }} (${{ fee_south_west_renewal }})</div>
                        <div>Total fee: {{ total_fee_south_west_renewal }}</div>
                    </div>
                    <div>
                        <div>Previously paid sites 'Remote' region: {{ num_of_sites_remain_remote_renewal }} (${{ fee_remote_renewal }})</div>
                        <div>Total fee: {{ total_fee_remote_renewal }}</div>
                    </div>
                </div>
            </div>
        </template>

        <div class="row col-sm-12">
            <datatable @hook:mounted="datatable_mounted" ref="site_locations_table" id="site-locations-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders" />
            <span class="view_all_button action_link" @click="displayAllFeatures">View All Proposed Sites On Map</span>
        </div>

        <div id="map-wrapper" class="row col-sm-12">
            <div id="map" class="map">
                <div :id="search_box_id" class="search-box">
                    <input :id="search_input_id" class="search-input" placeholder="longitude, latitude OR address to search"/>
                </div>
                <div id="basemap-button">
                    <img id="basemap_sat" src="../../../assets/satellite_icon.jpg" @click="setBaseLayer('sat')" />
                    <img id="basemap_osm" src="../../../assets/map_icon.png" @click="setBaseLayer('osm')" />
                </div>
                <div class="optional-layers-wrapper" @mouseleave="hover=false">
                    <div class="optional-layers-button">
                        <template v-if="mode === 'normal'">
                            <img src="../../../assets/normal.svg" @click="set_mode('layer')" />
                        </template>
                        <template v-else-if="mode === 'layer'">
                            <img src="../../../assets/info-bubble.svg" @click="set_mode('measure')" />
                        </template>
                        <template v-else>
                            <img src="../../../assets/ruler.svg" @click="set_mode('normal')" />
                        </template>
                    </div>
                    <div style="position:relative">
                        <transition v-if="optionalLayers.length">
                            <div class="optional-layers-button" @mouseover="hover=true">
                                <img src="../../../assets/layers.svg" />
                            </div>
                        </transition>
                        <transition v-if="optionalLayers.length">
                            <div div class="layer_options" v-show="hover" @mouseleave="hover=false" >
                                <div v-for="layer in optionalLayers">
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
            <div :id="popup_content_id" class="text-center"></div>
        </div>

    </div>
</template>

<script>
    import 'ol/ol.css';
    import 'ol-layerswitcher/dist/ol-layerswitcher.css'
    import Map from 'ol/Map';
    import View from 'ol/View';
    import TileLayer from 'ol/layer/Tile';
    import OSM from 'ol/source/OSM';
    import TileWMS from 'ol/source/TileWMS';
    import {Draw, Modify, Snap, Select} from 'ol/interaction';
    import {pointerMove} from 'ol/events/condition';
    import VectorLayer from 'ol/layer/Vector';
    import VectorSource from 'ol/source/Vector';
    import Cluster from 'ol/source/Cluster';
    import {Circle as CircleStyle, Fill, Stroke, Style, Icon, Text, RegularShape} from 'ol/style';
    import {FullScreen as FullScreenControl, MousePosition as MousePositionControl} from 'ol/control';
    import { Feature } from 'ol';
    import { Point, LineString } from 'ol/geom';
    import { getDistance } from 'ol/sphere';
    import { circular} from 'ol/geom/Polygon';
    import GeoJSON from 'ol/format/GeoJSON';
    import TextField from '@/components/forms/text.vue'
    import datatable from '@vue-utils/datatable.vue'
    import { v4 as uuidv4 } from 'uuid';
    import { getStatusForColour, getApiaryFeatureStyle,SiteColours, zoomToCoordinates, checkIfValidlatitudeAndlongitude } from '@/components/common/apiary/site_colours.js'
    import Overlay from 'ol/Overlay';

    import WMTS, {optionsFromCapabilities} from 'ol/source/WMTS';
    //import WMTSTileGrid from 'ol/source/WMTS';
    import WMTSTileGrid from 'ol/tilegrid/WMTS';
    import {get as getProjection} from 'ol/proj';
    import {getTopLeft, getWidth} from 'ol/extent';
    import MeasureStyles, { formatLength } from '@/components/common/apiary/measure.js'
    import { getArea, getLength } from 'ol/sphere'
    import Awesomplete from 'awesomplete'
    import { api_endpoints } from '@/utils/hooks'

    // create the WMTS tile grid in the google projection
    const projection = getProjection('EPSG:4326');
    const tileSizePixels = 1024;
    const tileSizeMtrs = getWidth(projection.getExtent()) / tileSizePixels;
    //const resolutions = [];
    //for (let i = 0; i <= 17; ++i) {
    //      resolutions[i] = tileSizeMtrs / Math.pow(2, i);
    //}
    const resolutions = [0.17578125, 0.087890625, 0.0439453125, 0.02197265625, 0.010986328125, 0.0054931640625, 0.00274658203125, 0.001373291015625, 0.0006866455078125, 0.0003433227539062, 0.0001716613769531, 858306884766e-16, 429153442383e-16, 214576721191e-16, 107288360596e-16, 53644180298e-16, 26822090149e-16, 13411045074e-16]
    //const tileGrid = new WMTSTileGrid({
    //      origin: getTopLeft(projection.getExtent()),
    //      resolutions: resolutions,
    //      matrixIds: matrixIds,
    //});

    let matrixSets = {
        'EPSG:4326': {
            '1024': {
                'name': 'gda94',
                'minLevel': 0,
                'maxLevel': 17
            }
        }
    }
    $.each(matrixSets, function (projection, innerMatrixSets) {
        $.each(innerMatrixSets, function (tileSize, matrixSet) {
            var matrixIds = new Array(matrixSet.maxLevel - matrixSet.minLevel + 1)
            for (var z = matrixSet.minLevel; z <= matrixSet.maxLevel; ++z) {
                matrixIds[z] = matrixSet.name + ':' + z
            }
            matrixSet.matrixIds = matrixIds
        })
    })
    let matrixSet = matrixSets['EPSG:4326']['1024']
    const tileGrid = new WMTSTileGrid({
        //origin: getTopLeft([-180, -90, 180, 90]),
        origin: getTopLeft(projection.getExtent()),
        resolutions: resolutions,
        matrixIds: matrixSet.matrixIds,
        tileSize: 1024,  // default: 256
    })
    // override getZForResolution on tile grid object;
    // for weird zoom levels, the default is to round up or down to the
    // nearest integer to determine which tiles to use.
    // because we want the printing rasters to contain as much detail as
    // possible, we rig it here to always round up.
    tileGrid.origGetZForResolution = tileGrid.getZForResolution
    tileGrid.getZForResolution = function (resolution, optDirection) {
        return tileGrid.origGetZForResolution(resolution*1.4, -1)
    }
    export default {
        props:{
            proposal:{
                type: Object,
                required:true
            },
            canEditActivities:{
              type: Boolean,
              default: true
            },
            is_external:{
              type: Boolean,
              default: false
            },
            is_internal:{
              type: Boolean,
              default: false
            },
            is_referral:{
              type: Boolean,
              default: false
            },
            hasReferralMode:{
                type:Boolean,
                default: false
            },
            hasAssessorMode:{
                type:Boolean,
                default: false
            },
            referral:{
                type: Object,
                required:false
            },
            proposal_parks:{
                type:Object,
                default:null
            },
        },
        data:function () {
            let vm=this;
            return{
                current_category: 'south_west',
                q: null,
                values:null,
                showingHelpText: false,
                help_text: 'My Help text ...',
                marker_lng: null,
                marker_lat: null,
                deed_poll_url: '',
                buffer_radius: 3000, // [m]
                min_num_of_sites_for_renewal: 5,
                min_num_of_sites_for_new: 5,
                style_for_vacant_selected: new Style({
                    //image: new CircleStyle({
                    image: new RegularShape({
                        //radius: existingSiteRadius,
                        points: 6,
                        radius: 6,
                        fill: new Fill({
                            color: SiteColours.vacant.fill
                        }),
                        stroke: new Stroke({
                            color: SiteColours.vacant.stroke,
                            width: 4
                        })
                    })
                }),
                style_for_new_apiary_site: new Style({
                    //image: new CircleStyle({
                    image: new RegularShape({
                        //radius: existingSiteRadius,
                        points: 6,
                        radius: 6,
                        fill: new Fill({
                            color: SiteColours.draft_external.fill
                        }),
                        stroke: new Stroke({
                            color: SiteColours.draft_external.stroke,
                            width: 2
                        })
                    })
                }),
                // Popup
                popup_id: uuidv4(),
                popup_content_id: uuidv4(),
                popup_closer_id: uuidv4(),
                content_element: null,
                overlay: null,

                // Remainders base
                num_of_sites_remain_south_west_base: 0,
                num_of_sites_remain_south_west_renewal_base: 0,
                num_of_sites_remain_remote_base: 0,
                num_of_sites_remain_remote_renewal_base: 0,

                // Sites on the map
                num_of_sites_south_west_applied_unpaid: 0,
                num_of_sites_south_west_renewal_applied_unpaid: 0,
                num_of_sites_remote_applied_unpaid: 0,
                num_of_sites_remote_renewal_applied_unpaid: 0,

                // Fee
                fee_south_west: 0,
                fee_remote: 0,
                fee_south_west_renewal: 0,
                fee_remote_renewal: 0,

                // variables for the GIS
                map: null,
                apiarySitesQuerySource: new VectorSource(),
                //apiarySitesQueryLayer: null,
                apiarySitesClusterLayer: null,
                bufferedSites: null,
                drawingLayerSource:  new VectorSource(),
                drawingLayer: null,
                drawForApiarySite: null,
                bufferLayerSource: new VectorSource(),
                bufferLayer: null,
                vacantLayerSource: new VectorSource(),
                vacantLayer: null,
                vacant_site_being_selected: null,
                swZoneSource: null,
                //

                // for timing
                proposal_vacant_draft_loaded: false,
                proposal_vacant_processed_loaded: false,
                approval_vacant_loaded: false,
                proposal_draft_loaded: false,
                proposal_processed_loaded: false,
                approval_loaded: false,
                startTime: null,
                endTime: null,

                dtHeaders: [
                    'Id',
                    'Latitude',
                    'Longitude',
                    'Category',
                    'Vacant',
                    'Action',
                ],
                dtOptions: {
                    serverSide: false,
                    searchDelay: 1000,
                    lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                    order: [
                        [0, 'desc']
                    ],
                    language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },
                    responsive: true,
                    processing: true,
                    columns: [
                        {
                            // id
                            visible: false,
                            mRender: function (data, type, full) {
                                if (full.id) {
                                    return full.id;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            // Lat
                            mRender: function (data, type, full) {
                                let coords = full.getGeometry().getCoordinates()
                                return Number.parseFloat(coords[1]).toFixed(6)
                            }
                        },
                        {
                            // Lng
                            mRender: function (data, type, full) {
                                let coords = full.getGeometry().getCoordinates()
                                return Number.parseFloat(coords[0]).toFixed(6)
                            }
                        },
                        {
                            // Category
                            mRender: function (data, type, feature) {
                                let cat = feature.get('site_category')
                                if (cat){
                                    cat = cat.replace('_', ' ')
                                    return cat.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
                                } else {
                                    return '---'
                                }
                            }
                        },
                        {
                            // Vacant
                            mRender: function (data, type, feature) {
                                let my_status = feature.get('status')
                                let is_vacant = feature.get('is_vacant')
                                if(my_status === 'vacant' || is_vacant === true){
                                    // Once saved, 'vacant' site status gets 'draft' therefore we have to check another attribute 'is_vacant', too
                                    return '<i class="fa fa-check" aria-hidden="true"></i>'
                                }
                                return ''
                            }
                        },
                        {
                            // Action
                            mRender: function (data, type, feature) {
                                let action_list = []
                                let ret_str_delete = '<span class="delete_button action_link" data-site-location-guid="' + feature.getId() + '">Delete</span>'
                                let ret_str_view = '<span class="view_on_map action_link" data-apiary-site-id="' + feature.getId() + '"/>View on map</span>';

                                let status = feature.get('status')

                                action_list.push(ret_str_view)
                                if (!vm.readonly){
                                    action_list.push(ret_str_delete)
                                }
                                return action_list.join('<br />');
                            }
                        },
                    ],
                },

                tileLayerOsm: null,
                tileLayerSat: null,
                optionalLayers: [],
                hover: false,

                // For Measurement tool
                mode: 'normal',
                drawForMeasure: null,
                style: MeasureStyles.defaultStyle,
                segmentStyle: MeasureStyles.segmentStyle,
                labelStyle: MeasureStyles.labelStyle,
                segmentStyles: null,
                measurementLayer: null,
                measuring: false,

                awe: null,
                mapboxAccessToken: null,
                search_box_id: uuidv4(),
                search_input_id: uuidv4(),
            }
        },
        components: {
            TextField,
            datatable,
        },
        computed:{
            ruler_colour: function(){
                if (this.mode === 'normal'){
                    return '#aaa';
                } else if(this.mode === 'measure') {
                    return '#53c2cf';
                } else {
                    return '#ff7f50';
                }
            },
            display_debug_info: function(){
                if (location.host === 'localhost:8071'){
                    return true
                }
                return false
            },
            is_proposal_type_new: function(){
                if (this.proposal_type_name === 'new'){
                    return true
                }
                return false
            },
            is_proposal_type_renewal: function(){
                if (this.proposal_type_name === 'renewal'){
                    return true
                }
                return false
            },
            proposal_type_name: function() {
                if (this.proposal.application_type === 'Apiary'){
                    if (this.proposal.proposal_type.toLowerCase() === 'renewal'){
                        return 'renewal'
                    } else {
                        return 'new'
                    }
                } else {
                    return '---'
                }
            },
            readonly: function() {
                let readonlyStatus = true;
                if (this.proposal.customer_status === 'Draft' && !this.is_internal) {
                    readonlyStatus = false;
                }
                return readonlyStatus;
            },

            // 1. South West
            // 1.1 New
            num_of_sites_remain_south_west: function(){
                // Number of sites paid left - number of sites to be applied
                let value = this.num_of_sites_remain_south_west_base - this.num_of_sites_south_west_applied_unpaid
                value = value >= 0 ? value : 0
                return value
            },
            num_of_sites_south_west_after_deduction: function(){
                let value = this.num_of_sites_south_west_applied_unpaid - this.num_of_sites_remain_south_west_base
                return value >= 0 ? value : 0
            },
            quotient_south_west: function(){
                return Math.floor(this.num_of_sites_south_west_after_deduction / this.min_num_of_sites_for_new)
            },
            remainder_south_west: function(){
                return this.num_of_sites_south_west_after_deduction % this.min_num_of_sites_for_new
            },
            num_of_sites_south_west_calculate: function(){
                let ret_value = this.quotient_south_west * this.min_num_of_sites_for_new
                if (this.remainder_south_west){
                    ret_value =  ret_value + this.min_num_of_sites_for_new
                }
                return ret_value
            },
            num_of_sites_south_west_to_add_as_remainder: function(){
                return this.num_of_sites_south_west_calculate - this.num_of_sites_south_west_after_deduction
            },
            total_fee_south_west: function() {
                let total_fee = this.num_of_sites_south_west_calculate * this.fee_south_west
                return total_fee
            },
            // 1.2 Renewal
            num_of_sites_remain_south_west_renewal: function(){
                // Number of sites paid left
                let value = this.num_of_sites_remain_south_west_renewal_base - this.num_of_sites_south_west_renewal_applied_unpaid
                value = value >= 0 ? value : 0
                return value
            },
            num_of_sites_south_west_renewal_after_deduction: function(){
                let value = this.num_of_sites_south_west_renewal_applied_unpaid - this.num_of_sites_remain_south_west_renewal_base
                return value >= 0 ? value : 0
            },
            quotient_south_west_renewal: function(){
                return Math.floor(this.num_of_sites_south_west_renewal_after_deduction / this.min_num_of_sites_for_renewal)
            },
            remainder_south_west_renewal: function(){
                return this.num_of_sites_south_west_renewal_after_deduction % this.min_num_of_sites_for_renewal
            },
            num_of_sites_south_west_renewal_calculate: function(){
                let ret_value = this.quotient_south_west_renewal * this.min_num_of_sites_for_renewal
                if (this.remainder_south_west_renewal){
                    ret_value =  ret_value + this.min_num_of_sites_for_renewal
                }
                return ret_value
            },
            num_of_sites_south_west_renewal_to_add_as_remainder: function(){
                return this.num_of_sites_south_west_renewal_calculate - this.num_of_sites_south_west_renewal_after_deduction
            },
            total_fee_south_west_renewal: function() {
                let total_fee = this.num_of_sites_south_west_renewal_calculate * this.fee_south_west_renewal
                return total_fee
            },

            // 2. Remote
            // 2.1 New
            num_of_sites_remain_remote: function(){
                let value = this.num_of_sites_remain_remote_base - this.num_of_sites_remote_applied_unpaid
                value = value >= 0 ? value : 0
                return value
            },
            num_of_sites_remote_after_deduction: function(){
                let value = this.num_of_sites_remote_applied_unpaid - this.num_of_sites_remain_remote_base
                return value >= 0 ? value : 0
            },
            quotient_remote: function(){
                return Math.floor(this.num_of_sites_remote_after_deduction / this.min_num_of_sites_for_new)
            },
            remainder_remote: function(){
                return this.num_of_sites_remote_after_deduction % this.min_num_of_sites_for_new
            },
            num_of_sites_remote_calculate: function(){
                let ret_value = this.quotient_remote * this.min_num_of_sites_for_new
                if (this.remainder_remote){
                    ret_value =  ret_value + this.min_num_of_sites_for_new
                }
                return ret_value
            },
            num_of_sites_remote_to_add_as_remainder: function(){
                return this.num_of_sites_remote_calculate - this.num_of_sites_remote_after_deduction
            },
            total_fee_remote: function() {
                let total_fee = this.num_of_sites_remote_calculate * this.fee_remote
                return total_fee
            },
            // 2.2 Renewal
            num_of_sites_remain_remote_renewal: function(){
                let value = this.num_of_sites_remain_remote_renewal_base - this.num_of_sites_remote_renewal_applied_unpaid
                value = value >= 0 ? value : 0
                return value
            },
            num_of_sites_remote_renewal_after_deduction: function(){
                let value = this.num_of_sites_remote_renewal_applied_unpaid - this.num_of_sites_remain_remote_renewal_base
                return value >= 0 ? value : 0
            },
            quotient_remote_renewal: function(){
                return Math.floor(this.num_of_sites_remote_renewal_after_deduction / this.min_num_of_sites_for_renewal)
            },
            remainder_remote_renewal: function(){
                return this.num_of_sites_remote_renewal_after_deduction % this.min_num_of_sites_for_renewal
            },
            num_of_sites_remote_renewal_calculate: function(){
                let ret_value = this.quotient_remote_renewal * this.min_num_of_sites_for_renewal
                if (this.remainder_remote_renewal){
                    ret_value =  ret_value + this.min_num_of_sites_for_renewal
                }
                return ret_value
            },
            num_of_sites_remote_renewal_to_add_as_remainder: function(){
                return this.num_of_sites_remote_renewal_calculate - this.num_of_sites_remote_renewal_after_deduction
            },
            total_fee_remote_renewal: function() {
                let total_fee = this.num_of_sites_remote_renewal_calculate * this.fee_remote_renewal
                return total_fee
            },

            // Total
            total_num_of_sites_on_map_unpaid: function(){
                return this.num_of_sites_south_west_applied_unpaid +
                       this.num_of_sites_south_west_renewal_applied_unpaid +
                       this.num_of_sites_remote_applied_unpaid +
                       this.num_of_sites_remote_renewal_applied_unpaid
            },
            total_num_of_sites_on_map: function(){
                let features = this.drawingLayerSource.getFeatures()
                return features.length
            }
        },
        watch:{
            fee_remote_renewal: function(){
                this.$emit('fee_remote_renewal', this.fee_remote_renewal)
            },
            fee_south_west_renewal: function(){
                this.$emit('fee_south_west_renewal', this.fee_south_west_renewal)
            },
            total_num_of_sites_on_map: function() {
                this.$emit('total_num_of_sites_on_map', this.total_num_of_sites_on_map)
            },
            total_num_of_sites_on_map_unpaid: function() {
                this.$emit('total_num_of_sites_on_map_unpaid', this.total_num_of_sites_on_map_unpaid)
            },
            num_of_sites_south_west_to_add_as_remainder: function(){
                this.$emit('num_of_sites_south_west_to_add_as_remainder', this.num_of_sites_south_west_to_add_as_remainder)
            },
            num_of_sites_remote_to_add_as_remainder: function(){
                this.$emit('num_of_sites_remote_to_add_as_remainder', this.num_of_sites_remote_to_add_as_remainder)
            },
            num_of_sites_south_west_renewal_to_add_as_remainder: function(){
                this.$emit('num_of_sites_south_west_renewal_to_add_as_remainder', this.num_of_sites_south_west_renewal_to_add_as_remainder)
            },
            num_of_sites_remote_renewal_to_add_as_remainder: function(){
                this.$emit('num_of_sites_remote_renewal_to_add_as_remainder', this.num_of_sites_remote_renewal_to_add_as_remainder)
            },
            num_of_sites_remain_south_west: function() {
                this.$emit('num_of_sites_remain_south_west', this.num_of_sites_remain_south_west)
            },
            num_of_sites_remain_remote: function() {
                this.$emit('num_of_sites_remain_remote', this.num_of_sites_remain_remote)
            },
            num_of_sites_remain_south_west_renewal: function() {
                this.$emit('num_of_sites_remain_south_west_renewal', this.num_of_sites_remain_south_west_renewal)
            },
            num_of_sites_remain_remote_renewal: function() {
                this.$emit('num_of_sites_remain_remote_renewal', this.num_of_sites_remain_remote_renewal)
            },
            total_fee_south_west: function(){
                this.$emit('total_fee_south_west', this.total_fee_south_west)
            },
            total_fee_south_west_renewal: function(){
                this.$emit('total_fee_south_west_renewal', this.total_fee_south_west_renewal)
            },
            total_fee_remote: function(){
                this.$emit('total_fee_remote', this.total_fee_remote)
            },
            total_fee_remote_renewal: function(){
                this.$emit('total_fee_remote_renewal', this.total_fee_remote_renewal)
            },
            vacant_site_being_selected: function() {
                if (this.vacant_site_being_selected){
                    this.showPopup(this.vacant_site_being_selected)
                } else {
                    this.closePopup()
                }
            }
        },
        methods:{
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
            search: function(place){
                var vm = this;

                let searching_by_latlng = checkIfValidlatitudeAndlongitude(place)

                if(!(searching_by_latlng)){
                    var latlng = vm.map.getView().getCenter();
                    $.ajax({
                        url: api_endpoints.geocoding_address_search + encodeURIComponent(place)+'.json?'+ $.param({
                            access_token: vm.mapboxAccessToken,
                            country: 'au',
                            limit: 10,
                            proximity: ''+latlng[0]+','+latlng[1],
                            bbox: '112.920934,-35.191991,129.0019283,-11.9662455',
                            types: 'region,postcode,district,place,locality,neighborhood,address,poi'
                        }),
                        dataType: 'json',
                        success: function(data, status, xhr) {
                            vm.suggest_list = [];  // Clear the list first
                            if (data.features && data.features.length > 0){
                                for (var i = 0; i < data.features.length; i++){
                                    vm.suggest_list.push({ label: data.features[i].place_name,
                                                            value: data.features[i].place_name,
                                                            feature: data.features[i]
                                                            });
                                }
                            }

                            vm.awe.list = vm.suggest_list;
                            vm.awe.evaluate();
                        }
                    });
                } else {
                    let lat = searching_by_latlng[1]
                    let lng = searching_by_latlng[4]
                    let currentZoomLevel = vm.map.getView().getZoom()
                    let targetZoomLevel = 14
                    if (targetZoomLevel < currentZoomLevel){
                        targetZoomLevel = currentZoomLevel
                    }

                    //zoomToCoordinates(vm.map, [lng, lat], targetZoomLevel)
                    zoomToCoordinates(vm.map, [lat, lng], targetZoomLevel)

                }
            },
            display_layers_option: function(mode){
                if(mode === 'layer'){
                    this.hover = true
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
            styleFunctionForMouse: function(feature){
                let vm = this
                //return this.style_for_new_apiary_site

                let styles = []

                //let geometry = feature.getGeometry()
                //vm.labelStyle.setGeometry(geometry);
                //vm.labelStyle.getText().setText('aho');
                //styles.push(vm.labelStyle);

                let myStyle = new Style({
                    image: new RegularShape({
                        fill: new Fill({
                            color: SiteColours.draft_external.fill
                        }),
                        stroke: new Stroke({
                            color: SiteColours.draft_external.stroke,
                            width: 2
                        }),
                        points: 6,
                        radius: 6,
                        //radius2: 0,
                        //angle: Math.PI / 4
                    }),
                })
                styles.push(myStyle)
                return styles
            },
            styleFunctionForNewSite: function(feature){
                console.log('in styleFunctionForNewSite')
                // This is used for the proposed apiary sites
                let vacant_selected = feature.get('vacant_selected')
                if (vacant_selected){
                    return this.style_for_vacant_selected
                } else {
                    return this.style_for_new_apiary_site
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
            styleFunctionForMeasurement: function (feature, resolution){
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
            set_mode: function(mode){
                this.mode = mode
                if (mode === 'measure'){
                    this.drawForMeasure.setActive(true)
                    this.drawForApiarySite.setActive(false)
                } else if (mode === 'layer'){
                    this.clearMeasurementLayer()
                    this.drawForMeasure.setActive(false)
                    this.drawForApiarySite.setActive(false)
                } else if (mode === 'normal') {
                    this.clearMeasurementLayer()
                    this.drawForApiarySite.setActive(true)
                    this.drawForMeasure.setActive(false)
                }
            },
            clearMeasurementLayer: function(){
                let vm = this
                let features = vm.measurementLayer.getSource().getFeatures()
                features.forEach((feature) => {
                    vm.measurementLayer.getSource().removeFeature(feature)
                })
            },
            console_layers: function(){
                let layers = this.map.getLayers()
                for (var i = 0; i < layers.array_.length; i++){
                    console.log(i + ': ' + layers.array_[i].get('title'))
                }
            },
            changeLayerVisibility: function(targetLayer){
                targetLayer.setVisible(!targetLayer.getVisible())
                let layers = this.map.getLayers()
                for (var i = 0; i < layers.array_.length; i++){
                    if (layers.array_[i].get('title') === 'Drawing Layer' || layers.array_[i].get('title') === 'Cluster Layer'){
                        try{
                            layers.array_[i].refresh()
                        } catch (err){
                            console.log('Error: ' + layers.array_[i].get('title'))
                        }
                    }
                }
            },
            addOptionalLayers: function(){
                let vm = this
                this.$http.get('/api/map_layers/').then(response => {
                    let layers = response.body
                    for (var i = 0; i < layers.length; i++){
                        let l = new TileWMS({
                            //url: 'https://kmi.dpaw.wa.gov.au/geoserver/' + layers[i].layer_group_name + '/wms',
                            url: env['kb_server_url'] + '/geoserver/' + layers[i].layer_group_name + '/wms',
                            params: {
                                'FORMAT': 'image/png',
                                'VERSION': '1.1.1',
                                tiled: true,
                                STYLES: '',
                                LAYERS: layers[i].layer_full_name,
                                //LAYERS: 'kaartdijin-boodja-public:mapbox-satellite'
                            }
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
                })
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
            datatable_mounted: function(){
                this.constructSiteLocationsTable();
            },
            load_apiary_sites_in_this_proposal: function(){
                // Load the apiary sites in this proposal on the map
                let vm = this
                for (let i=0; i<vm.proposal.proposal_apiary.apiary_sites.length; i++){
                     let apiary_site = vm.proposal.proposal_apiary.apiary_sites[i]

                    if (apiary_site.properties.status === 'vacant'){
                        // apiary_site is 'vacant' site
                        let feature = vm.apiarySitesQuerySource.getFeatureById(apiary_site.id)
                        // Set new attribute to apply a specific style for the 'vacant' selected site
                        feature.set('vacant_selected', true)

                        vm.drawingLayerSource.addFeature(feature);
                    } else {
                        let feature = (new GeoJSON).readFeature(apiary_site)
                        this.drawingLayerSource.addFeature(feature)
                        this.createBufferForSite(feature);
                    }
                }
                this.constructSiteLocationsTable();
            },
            is_feature_new_or_renewal: function(feature){
                if (feature.get('for_renewal')){
                    return 'renewal'
                } else {
                    return 'new'
                }
            },
            showPopup: function(feature){
                let geometry = feature.getGeometry();
                let coord = geometry.getCoordinates();
                let content = 'vacant'
                this.content_element.innerHTML = content;
                this.overlay.setPosition(coord);
            },
            howPopupForLayersJson: function(geojson, coord, column_names, display_all_columns, target_layer){
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
            closePopup: function(){
                this.content_element.innerHTML = null
                this.$emit('popupClosed')
                this.overlay.setPosition(undefined)
                return false
            },
            displayAllFeatures: function() {
                if (this.map){
                    if (this.drawingLayerSource.getFeatures().length>0){
                        let view = this.map.getView()

                        let ext = this.drawingLayerSource.getExtent()
                        let centre = [(ext[0] + ext[2])/2.0, (ext[1] + ext[3])/2.0]
                        let resolution = view.getResolutionForExtent(ext);
                        let z = view.getZoomForResolution(resolution) - 1
                        view.animate({zoom: z, center: centre})
                    }
                }
            },
            zoomToApiarySiteById: function(apiary_site_id){
                let feature = this.drawingLayerSource.getFeatureById(apiary_site_id)
                let geometry = feature.getGeometry()
                let coord = geometry.getCoordinates()
                let view = this.map.getView()
                this.map.getView().animate({zoom: 16, center: feature['values_']['geometry']['flatCoordinates']})
                //this.showPopup(feature)
            },
            uuidv4: function () {
                return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g,
                    function(c) {
                        return (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16);
                    }
                );
            },
            getDegrees: function(coords){
                return coords[0].toFixed(6) + ', ' + coords[1].toFixed(6);
            },
            metersToNearest: function(coords, filter) {
                // Infinity is the distance to the nearest apiary_site as default
                // Which means we it is fine to put apiary_site at the coords
                let candidates = [Number.POSITIVE_INFINITY];

                // Retrieve the nearest apiary site from the drawingLayerSource
                let nearestDrawnSite = this.drawingLayerSource.getClosestFeatureToCoordinate(coords, filter);
                if (nearestDrawnSite != null) {
                    candidates.push(getDistance(coords, nearestDrawnSite.getGeometry().getCoordinates()));
                }

                // Retrieve the nearest apiary site from the existing apiary_sites
                let nearestQuerySite = this.apiarySitesQuerySource.getClosestFeatureToCoordinate(coords, filter);
                if (nearestQuerySite != null) {
                    candidates.push(getDistance(coords, nearestQuerySite.getGeometry().getCoordinates()));
                }

                let min = candidates[0];
                for (let i = 1; i < candidates.length; i++) {
                    // Ignore NaN
                    if (!isNaN(candidates[i])){
                        min = Math.min(min, candidates[i]);
                    }
                }
                return min;
            },
            isNewPositionValid: function(coords, filter=null){
                let vm = this
                let distance = vm.metersToNearest(coords, filter);
                if (distance < vm.buffer_radius) {
                    return false
                }
                return true
            },
            zoneForCoordinates: function(coords){
                let zone = "remote";
                this.swZoneSource.getFeaturesAtCoordinate(coords).forEach(function(feat) {
                    zone = "south_west";
                });
                return zone;
            },
            createBufferForSite: function(site){
                let id = site.getId() + "_buffer";
                let coords = site.getGeometry().getCoordinates();

                // apiary from json had 2d coords packed in an inner array.
                if (coords.length == 1){
                    coords = coords[0];
                }

                let buffer = new Feature(circular(coords, this.buffer_radius, 16));
                buffer.setId(id)
                this.bufferLayerSource.addFeature(buffer);
            },
            removeBufferForSite: function(site){
                let buffer = this.bufferLayerSource.getFeatureById(site.getId() + "_buffer");
                if (buffer){
                    this.bufferLayerSource.removeFeature(buffer);
                }
            },
            existingSiteAvailableClicked: function() {
                alert("TODO: open screen 45: External - Contact Holder of Available Site in a different tab page.");
            },
            make_remainders_reactive: function(){
                let remainders = null;
                if (this.proposal.application_type === 'Apiary') {
                    remainders = this.proposal.proposal_apiary.site_remainders;
                }

                for (let i=0; i<remainders.length; i++){
                    if (remainders[i].category_name == 'South West'){
                        this.num_of_sites_remain_south_west_base = remainders[i].remainders
                        this.num_of_sites_remain_south_west_renewal_base = remainders[i].remainders_renewal
                        this.fee_south_west = remainders[i].fee
                        this.fee_south_west_renewal = remainders[i].fee_renewal
                    } else if (remainders[i].category_name == 'Remote'){
                        this.num_of_sites_remain_remote_base = remainders[i].remainders
                        this.num_of_sites_remain_remote_renewal_base = remainders[i].remainders_renewal
                        this.fee_remote = remainders[i].fee
                        this.fee_remote_renewal = remainders[i].fee_renewal
                    } else {
                        console.log('should not reach here')
                    }
                }
            },
            calculateRemainders: function(features){
                let remainders = null;
                if (this.proposal.application_type === 'Apiary') {
                    remainders = this.proposal.proposal_apiary.site_remainders;
                }
                this.num_of_sites_south_west_applied_unpaid = 0
                this.num_of_sites_remote_applied_unpaid = 0
                this.num_of_sites_south_west_renewal_applied_unpaid = 0
                this.num_of_sites_remote_renewal_applied_unpaid = 0

                for (let i=0; i<features.length; i++){
                    let new_or_renewal = this.is_feature_new_or_renewal(features[i])
                    let site_status = features[i].get('status')
                    let site_category = features[i].get('site_category')
                    let application_fee_paid = features[i].get('application_fee_paid')

                    if (application_fee_paid){
                        // For this apiary site, application fee has been already paid
                        // We should ignore this site interms of the calculation for the remainders and fees
                    } else {
                        if (site_status === 'vacant'){
                            if (site_category == 'south_west'){
                                this.num_of_sites_south_west_applied_unpaid += 1
                            } else if (site_category == 'remote'){
                                this.num_of_sites_remote_applied_unpaid += 1
                            }
                        } else {
                            if (new_or_renewal === 'renewal'){
                                if (site_category == 'south_west'){
                                    this.num_of_sites_south_west_renewal_applied_unpaid += 1
                                } else if (site_category == 'remote'){
                                    this.num_of_sites_remote_renewal_applied_unpaid += 1
                                }
                            }
                            if (new_or_renewal === 'new'){
                                if (site_category == 'south_west'){
                                    this.num_of_sites_south_west_applied_unpaid += 1
                                } else if (site_category == 'remote'){
                                    this.num_of_sites_remote_applied_unpaid += 1
                                }
                            }
                        }
                    }
                }

                let button_text = 'Pay and Submit'
                // TODO: improve this logic
                if (this.num_of_sites_remain_south_west >= 0 && this.num_of_sites_remain_remote >=0 && !this.proposal.proposal_type === 'renewal'){
                    button_text = 'Submit'
                }

                this.$emit('button_text', button_text)
            },
            constructSiteLocationsTable: function(){
                if (this.drawingLayerSource && this.$refs.site_locations_table){
                    // Clear table
                    this.$refs.site_locations_table.vmDataTable.clear().draw();

                    // Get all the features drawn
                    let features = this.drawingLayerSource.getFeatures()

                    // Insert data into the table
                    for(let i=0; i<features.length; i++){
                        this.$refs.site_locations_table.vmDataTable.row.add(features[i]).draw();
                    }

                    this.calculateRemainders(features)
                }
                // Update proposal obj, which is sent to the server when save/submit.
                //this.proposal.proposal_apiary.apiary_sites = features
                //this.updateApiarySitesData()
            },
            getFeatures: function() {
                let allFeatures = this.drawingLayerSource.getFeatures()
                return allFeatures
            },
            addEventListeners: function(){
                let vm = this

                $("#site-locations-table").on("click", ".delete_button", this.removeSiteLocation);
                $("#site-locations-table").on("click", ".view_on_map", this.zoomOnApiarySite)

                let searchLatLng = document.getElementById(this.search_input_id)
                searchLatLng.addEventListener('input', function(ev){
                    vm.search(ev.target.value);
                })
            },
            zoomOnApiarySite: function(e) {
                let apiary_site_id = e.target.getAttribute("data-apiary-site-id");
                this.zoomToApiarySiteById(apiary_site_id)
            },
            removeApiarySiteById: function(apiary_site_id){
                let myFeature = this.drawingLayerSource.getFeatureById(apiary_site_id)
                this.deleteApiarySite(myFeature)
                this.constructSiteLocationsTable()
            },
            deleteApiarySite: function(myFeature){
                let site_category = myFeature.get('site_category')
                let application_fee_paid = myFeature.get('application_fee_paid')
                let new_or_renewal = this.is_feature_new_or_renewal(myFeature)

                if (application_fee_paid){
                    // For this apiary site, application fee has been already paid
                    // We should ignore this site interms of the calculation for the remainders and fees
                } else {
                    if (new_or_renewal === 'new'){
                        if (site_category === 'south_west'){
                            this.num_of_sites_south_west_applied_unpaid -= 1
                        } else {
                            this.num_of_sites_remote_applied_unpaid -= 1
                        }
                    }
                    if (new_or_renewal === 'renewal'){
                        if (site_category === 'south_west'){
                            this.num_of_sites_south_west_renewal_applied_unpaid -= 1
                        } else {
                            this.num_of_sites_remote_renewal_applied_unpaid -= 1
                        }
                    }
                }

                let myFeatureStatus = myFeature.get('status')
                if (myFeatureStatus && myFeatureStatus != 'draft'){
                    this.drawingLayerSource.removeFeature(myFeature);
                } else {
                    // Remove buffer
                    this.removeBufferForSite(myFeature)
                    this.drawingLayerSource.removeFeature(myFeature);
                }
                // Remove vacant_selected attribute from the feature
                myFeature.unset('vacant_selected')
                //let status = this.get_status_for_colour(myFeature)
                let status = getStatusForColour(myFeature)
                let style_applied = getApiaryFeatureStyle(status)
                myFeature.setStyle(style_applied)
            },
            removeSiteLocation: function(e){
                let site_location_guid = e.target.getAttribute("data-site-location-guid");
                let myFeature = this.drawingLayerSource.getFeatureById(site_location_guid)
                this.deleteApiarySite(myFeature)

                // Remove the row from the table
                $(e.target).closest('tr').fadeOut('slow', function(){ })
            },
            initMap: async function() {
                let vm = this;

                let satelliteTileWmts = new WMTS({
                    url: env['kb_server_url'] +'/geoserver/gwc/service/wmts',
                    layer: 'kaartdijin-boodja-public:mapbox-satellite-public',
                    format: 'image/png',
                    matrixSet: 'gda94',
                    projection: 'EPSG:4326',
                    tileGrid: tileGrid,
                    style: '',
                })

                vm.tileLayerOsm = new TileLayer({
                    title: 'OpenStreetMap',
                    type: 'base',
                    visible: true,
                    source: new OSM(),
                });

                vm.tileLayerSat = new TileLayer({
                    title: 'Satellite',
                    type: 'base',
                    visible: true,
                    source: satelliteTileWmts,
                })

                vm.map = new Map({
                    layers: [
                        //vm.tileLayerOsm, 
                        //vm.tileLayerSat,
                    ],
                    target: 'map',
                    view: new View({
                        center: [115.95, -31.95],
                        zoom: 7,
                        projection: 'EPSG:4326'
                    }),
                    pixelRatio: 1,  // We need this in order to make this map work correctly with the browser and/or display scaling factor(s) other than 100%
                                    // Ref: https://github.com/openlayers/openlayers/issues/11464
                });

                let clusterSource = new Cluster({
                    distance: 50,
                    source: vm.apiarySitesQuerySource,
                })

                let styleCache = {}
                vm.apiarySitesClusterLayer = new VectorLayer({
                    title: 'Cluster Layer',
                    source: clusterSource,
                    style: function (clusteredFeature){
                        let featuresInClusteredFeature = clusteredFeature.get('features')
                        let size = featuresInClusteredFeature.length
                        let style = styleCache[size]
                        if(size == 1){
                            // When size is 1, which means the cluster feature has only one site
                            // we want to display it as dedicated style
                            let status = getStatusForColour(featuresInClusteredFeature[0])
                            return getApiaryFeatureStyle(status);
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
                                })
                            })
                            styleCache[size] = style
                        }
                        return style
                    },
                });
                //vm.map.addLayer(vm.apiarySitesClusterLayer);

                vm.bufferedSites = [];
                vm.map.on("moveend", function(attributes){
                    let zoom = vm.map.getView().getZoom();
                    if (zoom < 11) {
                        return;
                    }

                    let fresh = 0;
                    let cached = 0;

                    vm.apiarySitesQuerySource.forEachFeatureInExtent(vm.map.getView().calculateExtent(), function(feature) {
                        let id = feature.getId();
                        if (vm.bufferedSites.indexOf(id) == -1) {
                            vm.createBufferForSite(feature);
                            vm.bufferedSites.push(id);
                            fresh++;
                        }
                        else {
                            cached++;
                        }
                    });
                });
                vm.map.on('singleclick', function(evt){
                    if(vm.mode === 'layer'){
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

                                //p.then(res => res.text()).then(function(data){
                                p.then(res => res.json()).then(function(data){
                                    //vm.showPopupForLayersHTML(data, evt.coordinate, column_names, display_all_columns)
                                    vm.showPopupForLayersJson(data, evt.coordinate, column_names, display_all_columns, vm.optionalLayers[i])
                                })
                            }
                        }
                    }
                })

                // In memory vector layer for digitization
                //vm.drawingLayerSource = new VectorSource();
                vm.drawingLayerSource.on('addfeature', async function(e){
                    let coords = e.feature.getGeometry().getCoordinates()
                    let ret = await vm.$http.get('/gisdata/?layer=wa_coast_smoothed&lat=' + coords[1] + '&lng=' + coords[0])
                    if(!ret.body.hasOwnProperty('id')){
                        vm.removeBufferForSite(e.feature)
                        vm.drawingLayerSource.removeFeature(e.feature);
                    }
                    vm.constructSiteLocationsTable()
                });
                vm.drawingLayer = new VectorLayer({
                    title: 'Drawing Layer',
                    source: vm.drawingLayerSource,
                    style: vm.styleFunctionForNewSite,
                });

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

                //vm.bufferLayerSource = new VectorSource();
                vm.bufferLayer = new VectorLayer({
                    title: 'Buffer Layer',
                    source: vm.bufferLayerSource,
                    minZoom: 11,

                });

                vm.swZoneSource = new VectorSource({
                    url: "/static/disturbance/gis/sw_apiary_zone.geojson",
                    format: new GeoJSON(),
                });
                // a visible layer is required to trigger loading the data, the empty style will mean that the features are not drawn
                let swZoneLayer = new VectorLayer({
                    title: 'South West Zone Layer',
                    source: vm.swZoneSource,
                    style: new Style(),
                    visible: true,
                });

                // Add layers to the map
                vm.map.addLayer(vm.tileLayerOsm)
                vm.map.addLayer(vm.tileLayerSat)
                vm.map.addLayer(swZoneLayer)
                vm.map.addLayer(vm.apiarySitesClusterLayer)
                vm.map.addLayer(vm.bufferLayer)
                vm.map.addLayer(vm.drawingLayer)

                // Set zIndex to some layers to be rendered over the other layers
                vm.apiarySitesClusterLayer.setZIndex(10)
                vm.bufferLayer.setZIndex(20)
                vm.drawingLayer.setZIndex(30)

                // Full screen toggle
                vm.map.addControl(new FullScreenControl());

                // Show mouse coordinates
                vm.map.addControl(new MousePositionControl({
                    coordinateFormat: function(coords){
                        let message = vm.getDegrees(coords) + "\n";
                        let distance = vm.metersToNearest(coords, null);
                        if (distance < Number.POSITIVE_INFINITY) {
                            message += "<br>Nearest: "  + (distance / 1000).toFixed(2) + " km";
                        }
                        return  message;
                    },
                    target: document.getElementById('mouse-position'),
                    className: 'custom-mouse-position',
                }));

                // Draw and modify tools
                if (!vm.readonly){
                    let modifyInProgressList = [];
                    vm.drawForApiarySite = new Draw({
                        source: vm.drawingLayerSource,
                        type: "Point",
                        style: vm.styleFunctionForMouse,  // This style is for the style on the mouse
                    });
                    vm.drawForApiarySite.on("drawstart", async function(attributes){
                        if (vm.mode === 'normal'){
                            let coords = attributes.feature.getGeometry().getCoordinates()

                            if (vm.vacant_site_being_selected){
                                // Abort drawing, instead 'vacant' site is to be added
                                vm.drawForApiarySite.abortDrawing();

                                vm.vacant_site_being_selected.set('vacant_selected', true)

                                vm.drawingLayerSource.addFeature(vm.vacant_site_being_selected);
                                vm.vacant_site_being_selected.getGeometry().on("change", function() {
                                    if (modifyInProgressList.indexOf(vm.vacant_site_being_selected.getId()) == -1) {
                                        modifyInProgressList.push(vm.vacant_site_being_selected.getId());
                                    }
                                });
                            } else {
                                let coords = attributes.feature.getGeometry().getCoordinates()
                                if (!vm.isNewPositionValid(coords)) {
                                    vm.drawForApiarySite.abortDrawing();
                                }
                            }
                        } else {
                            vm.drawForApiarySite.abortDrawing();
                        }
                    });
                    vm.drawForApiarySite.on('drawend', async function(attributes){
                        if (!vm.readonly){
                            let feature = attributes.feature;
                            let draw_id = vm.uuidv4();
                            let draw_coords = feature.getGeometry().getCoordinates();

                            feature.setId(draw_id);
                            feature.set("source", "draw");
                            feature.set("stable_coords", draw_coords);
                            feature.set('site_category', vm.zoneForCoordinates(draw_coords));
                            feature.getGeometry().on("change", function() {
                                if (modifyInProgressList.indexOf(draw_id) == -1) {
                                    modifyInProgressList.push(draw_id);
                                }
                            });
                            vm.createBufferForSite(feature);
                            // Vue table is updated by the event 'addfeature' issued from the Source
                        }
                    });
                    vm.map.addInteraction(vm.drawForApiarySite);

                    let modifyTool = new Modify({
                        source: vm.drawingLayerSource,
                        condition: function(e){
                            return true
                        }
                    });
                    modifyTool.on("modifystart", function(attributes){

                    });
                    modifyTool.on("modifyend", function(attributes){
                        // this will list all features in layer, not so useful without cross referencing
                        attributes.features.forEach(async function(feature){
                            let id = feature.getId();
                            let index = modifyInProgressList.indexOf(id);
                            if (index != -1) {
                                modifyInProgressList.splice(index, 1);
                                let coords = feature.getGeometry().getCoordinates();
                                let filter = vm.excludeFeature(feature);
                                let valid = vm.isNewPositionValid(coords, filter);

                                if (!valid || feature.get('is_vacant')===true) {
                                    // rollback proposed modification
                                    let c = feature.get("stable_coords");
                                    feature.getGeometry().setCoordinates(c);
                                    // setting coords will add the id to the modification list again, we don't need that so clear it now
                                    index = modifyInProgressList.indexOf(id);
                                    modifyInProgressList.splice(index, 1);
                                }
                                else {
                                    let ret = await vm.$http.get('/gisdata/?layer=wa_coast_smoothed&lat=' + coords[1] + '&lng=' + coords[0])
                                    if(!ret.body.hasOwnProperty('id')){
                                        // rollback proposed modification
                                        let c = feature.get("stable_coords");
                                        feature.getGeometry().setCoordinates(c);
                                        // setting coords will add the id to the modification list again, we don't need that so clear it now
                                        index = modifyInProgressList.indexOf(id);
                                        modifyInProgressList.splice(index, 1);
                                    } else {
                                        // confirm proposed modification
                                        feature.set("stable_coords", coords);
                                        vm.removeBufferForSite(feature);
                                        vm.createBufferForSite(feature);
                                        feature.set('site_category', vm.zoneForCoordinates(coords));
                                        vm.constructSiteLocationsTable();
                                    }
                                }
                            }
                        });
                    });
                    vm.map.addInteraction(modifyTool);
                }
                // Measure tool
                let draw_source = new VectorSource({ wrapX: false })
                vm.drawForMeasure = new Draw({
                    source: draw_source,
                    type: 'LineString',
                    style: vm.styleFunctionForMeasurement,
                })

                // Set a custom listener to the Measure tool
                vm.drawForMeasure.set('escKey', '')
                vm.drawForMeasure.on('change:escKey', function(evt){
                    //vm.drawForMeasure.finishDrawing()
                })
                vm.drawForMeasure.on('drawstart', function(evt){
                    vm.measuring = true
                })
                vm.drawForMeasure.on('drawend', function(evt){
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

                let hoverInteraction = new Select({
                    condition: pointerMove,
                    //layers: [vm.apiarySitesQueryLayer]
                    layers:[vm.apiarySitesClusterLayer]
                });
                vm.map.addInteraction(hoverInteraction);
                hoverInteraction.on('select', function(evt){
                    if(evt.selected.length > 0 && evt.selected[0].get('features').length > 0){
                        // Mouse hover in
                        let feature_hovered = evt.selected[0].get('features')[0]

                        //let is_vacant = evt.selected[0].get('is_vacant')
                        let is_vacant = feature_hovered.get('is_vacant')
                        let making_payment = feature_hovered.get('making_payment') || false
                        let status = feature_hovered.get('status')

                        if(is_vacant && !making_payment && status != 'pending'){
                            // When mouse hover on the 'vacant' apiary site, temporarily store it
                            // so that it can be added to the new apiary site application when user clicking on it.
                            vm.vacant_site_being_selected = feature_hovered

                            // Thicken border when hover
                            let style_applied = getApiaryFeatureStyle(vm.vacant_site_being_selected.get('status'), true, 5)
                            vm.vacant_site_being_selected.setStyle(style_applied)
                        }
                        else {
                        }
                        if (vm.$route.query.debug === 'true'){
                        }
                    } else {
                        // Mouse hover out
                        if (vm.vacant_site_being_selected){
                            //let status = vm.get_status_for_colour(vm.vacant_site_being_selected)
                            let status = getStatusForColour(vm.vacant_site_being_selected)
                            let style_applied = getApiaryFeatureStyle(status, false)

                            let vacant_selected = vm.vacant_site_being_selected.get('vacant_selected')
                            if (vacant_selected){
                                style_applied = vm.style_for_vacant_selected
                            }

                            vm.vacant_site_being_selected.setStyle(style_applied)
                        }

                        // Release feature
                        vm.vacant_site_being_selected = null
                    }
                });
                vm.setBaseLayer('osm')
                vm.addOptionalLayers()

                document.addEventListener('keydown', vm.keydown, false)
            },  // End: initMap()
            keydown: function(evt){
                let vm = this

                let charCode = (evt.which) ? evt.which : evt.keyCode;
                if (charCode === 27 && vm.measuring === true){ //esc key
                    //dispatch event
                    vm.drawForMeasure.set('escKey', Math.random());
                }
            },
            //get_status_for_colour: function(feature){
            //    let status = feature.get("status");
            //    let is_vacant = feature.get('is_vacant')
            //    let making_payment = feature.get('making_payment')

            //    if (is_vacant){
            //        status = 'vacant'
            //    } else if (making_payment){
            //        status = 'making_payment'
            //    }
            //    return status
            //},
            excludeFeature: function(excludedFeature) {
                return function(f) {
                    return excludedFeature.getId() != f.getId();
                };
            },
            tryCreateNewSiteFromForm: function(){
                let lat = this.proposal.proposal_apiary.latitude
                let lon = this.proposal.proposal_apiary.longitude
                let coords = [lon, lat];
                // rough bounding box for preliminary check
                if (isNaN(lon) || lon < 112 || lon > 130 ||
                    isNaN(lat) || lat < -35 || lat > -11) {
                    return false;
                }
                if(!this.isNewPositionValid(coords))
                {
                    return false;
                }

                let feature = new Feature(new Point(coords));
                feature.setId(this.uuidv4());
                feature.set("source", "form");
                feature.set('site_category', this.zoneForCoordinates(coords));
                this.drawingLayerSource.addFeature(feature);

                this.createBufferForSite(feature);
                return true;
            },
            display_duration: function(label){
                let finishedDate = new Date()
                let delta = finishedDate - this.startTime
                console.log(label + ' ' + delta + ' [ms]')
                if (this.proposal_vacant_draft_loaded &&
                    this.proposal_vacant_processed_loaded &&
                    this.approval_vacant_loaded &&
                    this.proposal_draft_loaded &&
                    this.proposal_processed_loaded &&
                    this.approval_loaded){
                        this.endTime = new Date()
                        let timeDiff = this.endTime - this.startTime
                        let features = this.apiarySitesQuerySource.getFeatures()
                        console.log('total time: ' + timeDiff + ' [ms] (' + features.length + ' sites)')
                    }
            },
            load_existing_sites: function(){
                let vm = this
                this.$http.get('/api/apiary_site/list_existing_proposal_vacant_draft/?proposal_id=' + this.proposal.id).then(
                    res => {
                        let num_sites = 0
                        if(res.body.features){
                            vm.apiarySitesQuerySource.addFeatures((new GeoJSON()).readFeatures(res.body))
                            num_sites = res.body.features.length
                        }
                        vm.proposal_vacant_draft_loaded = true
                        vm.display_duration('proposal vacant draft (' + num_sites + ' sites)')
                    },
                    err => {}
                )
                this.$http.get('/api/apiary_site/list_existing_proposal_vacant_processed/?proposal_id=' + this.proposal.id).then(
                    res => {
                        let num_sites = 0
                        if(res.body.features){
                            vm.apiarySitesQuerySource.addFeatures((new GeoJSON()).readFeatures(res.body))
                            num_sites = res.body.features.length
                        }
                        vm.proposal_vacant_processed_loaded = true
                        vm.display_duration('proposal vacant processed (' + num_sites + ' sites)')
                    },
                    err => {}
                )
                this.$http.get('/api/apiary_site/list_existing_approval_vacant/?proposal_id=' + this.proposal.id).then(
                    res => {
                        let num_sites = 0
                        if(res.body.features){
                            vm.apiarySitesQuerySource.addFeatures((new GeoJSON()).readFeatures(res.body))
                            num_sites = res.body.features.length
                        }
                        vm.approval_vacant_loaded = true
                        vm.display_duration('approval vacant (' + num_sites + ' sites)')
                    },
                    err => {}
                )
                this.$http.get('/api/apiary_site/list_existing_proposal_draft/?proposal_id=' + this.proposal.id).then(
                    res => {
                        let num_sites = 0
                        if(res.body.features){
                            vm.apiarySitesQuerySource.addFeatures((new GeoJSON()).readFeatures(res.body))
                            num_sites = res.body.features.length
                        }
                        vm.proposal_draft_loaded = true
                        vm.display_duration('proposal draft (' + num_sites + ' sites)')
                    },
                    err => {}
                )
                this.$http.get('/api/apiary_site/list_existing_proposal_processed/?proposal_id=' + this.proposal.id).then(
                    res => {
                        let num_sites = 0
                        if(res.body.features){
                            vm.apiarySitesQuerySource.addFeatures((new GeoJSON()).readFeatures(res.body))
                            num_sites = res.body.features.length
                        }
                        vm.proposal_processed_loaded = true
                        vm.display_duration('proposal processed (' + num_sites + ' sites)')
                    },
                    err => {
                    }
                )
                this.$http.get('/api/apiary_site/list_existing_approval/?proposal_id=' + this.proposal.id).then(
                    res => {
                        let num_sites = 0
                        if(res.body.features){
                            vm.apiarySitesQuerySource.addFeatures((new GeoJSON()).readFeatures(res.body))
                            num_sites = res.body.features.length
                        }
                        vm.approval_loaded = true
                        vm.display_duration('approval (' + num_sites + ' sites)')
                    },
                    err => {}
                )
            }
        },
        created: async function() {
            this.load_apiary_sites_in_this_proposal()
            this.displayAllFeatures()
            this.startTime = new Date()
            await this.load_existing_sites()
            this.make_remainders_reactive()
            let temp_token = await this.retrieveMapboxAccessToken()
            this.mapboxAccessToken = temp_token.access_token
        },
        mounted: function() {
            let vm = this;
            this.$nextTick(() => {
                vm.initMap();
                vm.set_mode('normal')
                vm.addEventListeners();
                vm.initAwesomplete()
            });
        }
    }
</script>

<style lang="css">
    .delete_button {
        color: #337ab7 !important;
    }
    .section{
        text-transform: capitalize;
    }
    .list-group{
        margin-bottom: 0;
    }
    .fixed-top{
        position: fixed;
        top:56px;
    }
    .debug-info {
        background: #CCC;
        margin: 1em;
    }
    .debug-message {
        margin: 0 0 1em 0;
        padding: 0 0 0 1em
    }
    .debug-remainders {
        padding: 0 0 0 1em
    }
    #map-wrapper {
        position: relative;
        padding: 0;
        margin: 0;
    }
    .map {
        display: inline-block;
        width: 100%;
        height: 500px;
    }
    canvas {
        width: 100%;
    }
    #basemap-button {
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
    #basemap_sat,#basemap_osm {
    /* border-radius: 5px; */
    }
    #basemap-button:hover,.optional-layers-button:hover {
        cursor: pointer;
        -moz-filter: brightness(0.9);
        -webkit-filter: brightness(0.9);
        filter: brightness(0.9);
    }
    #basemap-button:active {
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
        padding: 4px;
        display: block;
        position: relative;
        z-index: 400;
        background: white;
        border-radius: 2px;
        border: 3px solid rgba(5, 5, 5, .1);
        cursor: pointer;
        font-size: 0;
    }
    .layer_options {
        min-width: max-content;
        position: absolute;
        top: 0;
        left: 0;
        z-index: 410;
        background: white;
        border-radius: 2px;
        cursor: auto;
        /*
        box-shadow: 3px 3px 3px #777;
        -moz-filter: brightness(1.0);
        -webkit-filter: brightness(1.0);
        */
        padding: 0.5em;
        border: 3px solid rgba(5, 5, 5, .1);
    }
    .custom-mouse-position {
        position: absolute;
        bottom: 16px;
        left: 16px;
        top: auto;
        right: auto;
        text-align: left;
        font-size: 0.8rem;
        border: 0;
        padding: 8px;
        color: white;
        background-color: rgba(37, 45, 51, 0.7);
    }
    .action_link {
        color: #347ab7;
        cursor: pointer;
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
    .manual_coordinate_section {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
    }
    .grow1 {
        flex-grow: 1;
    }
    .ml-1 {
        margin-left: 0.25em !important;
    }
    .ml-2 {
        margin-left: 0.5em !important;
    }
    .ml-3 {
        margin-left: 1em !important;
    }
    .mt-2 {
        margin-top: 0.5em !important;
    }
    .mt-3 {
        margin-top: 1em !important;
    }
    .mb-3 {
        margin-bottom: 1em !important;
    }
    .mb-4 {
        margin-bottom: 2em !important;
    }
    .v-enter-active,
    .v-leave-active {
          transition: 0.4s;
    }
    @import './map_address_search_scoped.css'
</style>

<style>
    @import './map_address_search.css'
</style>