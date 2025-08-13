<template lang="html">
    <div>
        <!-- <div>{{shapefile_json}}</div> -->
        <div class="map-wrapper row col-sm-12">
            <div :id="elem_id" class="map">
                <div class="basemap-button">
                    <img id="basemap_sat" src="../../../assets/satellite_icon.jpg" @click="setBaseLayer('sat')" />
                    <img id="basemap_osm" src="../../../assets/map_icon.png" @click="setBaseLayer('osm')" />
                </div>
                <div class="optional-layers-wrapper">
                    <div class="optional-layers-button">
                        <template v-if="mode === 'layer'">
                            <img src="../../../assets/info-bubble.svg" @click="set_mode('measure')" />
                        </template>
                        <template v-else>
                            <img src="../../../assets/ruler.svg" @click="set_mode('layer')" />
                        </template>
                    </div>
                    <!--div class="optional-layers-button" @click="set_mode(mode)">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" >
                            <path 
                                d="M18.342 0l-2.469 2.47 2.121 2.121-.707.707-2.121-2.121-1.414 1.414 1.414 1.414-.707.707-1.414-1.414-1.414 1.414 1.414 1.414-.707.707-1.414-1.414-1.414 1.414 2.121 2.122-.707.707-2.121-2.121-1.414 1.414 1.414 1.414-.708.707-1.414-1.414-1.414 1.414 1.414 1.414-.708.709-1.414-1.414-1.414 1.413 2.121 2.121-.706.706-2.122-2.121-2.438 2.439 5.656 5.657 18.344-18.343z" 
                                :fill="ruler_colour"
                            />
                        </svg>
                    </div-->
                    <div style="position:relative">                        
                        <transition>                            
                            <div v-if="optionalLayers.length" class="optional-layers-button" @mouseover="hover=true">
                                <img src="../../../assets/layers.svg" />
                            </div>
                        </transition>
                        <transition v-if="optionalLayers.length">
                            <div class="layer_options" v-show="hover" @mouseleave="hover=false" >
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
    import WMTSTilegrid from 'ol/tilegrid/WMTS';
    import Map from 'ol/Map';
    import View from 'ol/View';
    import TileLayer from 'ol/layer/Tile';
    import TileWMS from 'ol/source/TileWMS';
    import WMTS from 'ol/source/WMTS';
    import { Draw, Modify } from 'ol/interaction';
    import VectorLayer from 'ol/layer/Vector';
    import VectorSource from 'ol/source/Vector';
    import { Circle as CircleStyle, Fill, Style } from 'ol/style';
    import { FullScreen as FullScreenControl, MousePosition as MousePositionControl } from 'ol/control';
    import { LineString, Point } from 'ol/geom';
    import GeoJSON from 'ol/format/GeoJSON';
    import Overlay from 'ol/Overlay';
    import { getDisplayNameFromStatus, getDisplayNameOfCategory, getStatusForColour, getApiaryFeatureStyle } from '@/components/common/apiary/site_colours.js'
    import MeasureStyles, { formatLength } from '@/components/common/apiary/measure.js'
    import {get as getProjection} from 'ol/proj';
    import {getTopLeft, getWidth} from 'ol/extent';
    import { toRaw } from 'vue';

    export default {
        props:{
            is_external:{
                type: Boolean,
                default: false
            },
            is_internal:{
                type: Boolean,
                default: false
            },
            apiary_site_geojson_array: {
                type: Array,
                default: function(){
                    return []
                }
            },
            can_modify: {
                type: Boolean,
                default: false
            },
            display_at_time_of_submitted: {
                type: Boolean,
                default: false
            },
            shapefile_json: {
                type: Object,
                default: function(){
                    return {}
                }
            }
        },
        watch: {
            display_at_time_of_submitted: function(){

            }
        },
        data: function(){
            // let vm = this
            return{
                map: null,
                apiarySitesQuerySource: null,
                apiarySitesQueryLayer: null,
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
                style: MeasureStyles.defaultStyle,
                segmentStyle: MeasureStyles.segmentStyle,
                labelStyle: MeasureStyles.labelStyle,
                segmentStyles: null,
                shapeVectorSource: null,
                shapeVectorLayer: null,
          }      
        },
        created: function(){

        },
        mounted: function(){
            let vm = this;
            this.$nextTick(() => {
                vm.addEventListeners()
            });
            vm.initMap()
            vm.setBaseLayer('osm')
            vm.set_mode('layer')
            vm.addOptionalLayers()
            //vm.map.addLayer(vm.apiarySitesQueryLayer);
            //vm.displayAllFeatures()
        },
        components: {

        },
        computed: {
            ruler_colour: function(){
                if (this.mode === 'normal'){
                    return '#aaa';
                } else {
                    return '#53c2cf';
                }
            }
        },
        methods: {
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
            styleFunctionForMeasurement: function (feature, ){
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
                if (this.mode === 'layer'){
                    this.clearMeasurementLayer()
                    this.drawForMeasure.setActive(false)
                } else if (this.mode === 'measure') {
                    this.drawForMeasure.setActive(true)
                }
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
                        let layers = await response.json();
                        for (var i = 0; i < layers.length; i++){
                            let l = new TileWMS({
                                // url: env['kmi_server_url'] + '/geoserver/' + layers[i].layer_group_name + '/wms',
                                //url: '/kb-proxy/geoserver/' + layers[i].layer_group_name + '/wms',
                                url: layers[i].layer_group_name ? '/kb-proxy/geoserver/' + layers[i].layer_group_name + '/wms' : '/kb-proxy/geoserver/wms',
                                params: {
                                    'FORMAT': 'image/png',
                                    'VERSION': '1.1.1',
                                    tiled: true,
                                    STYLES: '',
                                    LAYERS: layers[i].layer_full_name
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
                    }
                )
            },
            setBaseLayer: function(selected_layer_name){
                console.log('in setBaseLayer')
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
            closePopup: function(){
                this.content_element.innerHTML = null
                this.overlay.setPosition(undefined)
                // this.$emit('popupClosed')
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
                            }
                        });

                // vm.tileLayerOsm = new TileLayer({
                //     title: 'OpenStreetMap',
                //     type: 'base',
                //     visible: true,
                //     source: new OSM(),
                // });

                vm.tileLayerOsmWorking= new TileLayer({
                    name: "street",
                    canDelete: "no",
                    visible: !0,
                    source: new WMTS({
                        //url: "https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts",
                        url: "/kb-proxy/geoserver/gwc/service/wmts",
                        format: "image/png",
                        layer: "kaartdijin-boodja-public:mapbox-streets-public",
                        matrixSet: matrixSet,
                        projection: 'EPSG:3857',
                        tileGrid: m
                    })

                        // url: "https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts",
                        // format: "image/png",
                        // layer: "public:mapbox-streets",
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
                    pixelRatio: 1,
                });

                if(vm.shapefile_json && Object.keys(vm.shapefile_json).length>0){
                    vm.shapeVectorSource = new VectorSource({
                        features: new GeoJSON().readFeatures(vm.shapefile_json),
                    });
                    vm.shapeVectorLayer= new VectorLayer({
                        source: vm.shapeVectorSource,
                    })
                    vm.map.addLayer(vm.shapeVectorLayer);
                    // Set zIndex to some layers to be rendered over the other layers
                    vm.shapeVectorLayer.setZIndex(10)
                    vm.displayAllFeaturesShape();
                }
                vm.apiarySitesQuerySource = new VectorSource({ });
                vm.apiarySitesQueryLayer = new VectorLayer({
                    source: vm.apiarySitesQuerySource,
                    style: function(feature){
                        let status = getStatusForColour(feature, false, vm.display_at_time_of_submitted)
                        return getApiaryFeatureStyle(status, feature.get('checked'))
                    },
                });
                vm.map.addLayer(vm.apiarySitesQueryLayer);

                // Set zIndex to some layers to be rendered over the other layers
                vm.apiarySitesQueryLayer.setZIndex(10)  

                // Full screen toggle
                vm.map.addControl(new FullScreenControl());

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

                // Add apiary_sites passed as a props
                for (let i=0; i<vm.apiary_site_geojson_array.length; i++){
                    this.addApiarySite(vm.apiary_site_geojson_array[i])
                }

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
                            if (!feature.id){
                                // When the Modify object is used for the layer, 'feature' losts some of the attributes including 'id', 'status'...
                                // Therefore try to get the correct feature by the coordinate
                                let geometry = feature.getGeometry();
                                let coord = geometry.getCoordinates();
                                feature = vm.apiarySitesQuerySource.getFeaturesAtCoordinate(coord)
                            }
                            vm.showPopup(feature[0])
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
                                        //vm.showPopupForLayersHTML(data, evt.coordinate, column_names, display_all_columns)
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
                    // let extent = vm.map.getView().calculateExtent(vm.map.getSize());
                    // let features = vm.apiarySitesQuerySource.getFeaturesInExtent(extent)
                    // vm.$emit('featuresDisplayed', features)
                });
                if (vm.can_modify){
                    let modifyTool = new Modify({
                        source: vm.apiarySitesQuerySource,
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
                                // let coords = feature.getGeometry().getCoordinates();
                                // vm.$emit('featureGeometryUpdated', {'id': id, 'coordinates': {'lng': coords[0], 'lat': coords[1]}})
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
                let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
                this.showPopup(feature)
            },
            showPopup: function(feature){
                if (feature){
                    let geometry = feature.getGeometry();
                    let coord = geometry.getCoordinates();
                    let svg_hexa = "<svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='20' width='15'>" +
                    '<g transform="translate(0, 4) scale(0.9)"><path d="M 14.3395,12.64426 7.5609998,16.557828 0.78249996,12.64426 0.7825,4.8171222 7.5609999,0.90355349 14.3395,4.8171223 Z" id="path837" style="fill:none;stroke:#ffffff;stroke-width:1.565;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" /></g></svg>'
                    //let status_str = feature.get('is_vacant') ? getDisplayNameFromStatus(feature.get('status')) + ' (vacant)' : getDisplayNameFromStatus(feature.get('status'))
                    let status_str = getDisplayNameFromStatus(getStatusForColour(feature, false, this.display_at_time_of_submitted))
                    let content = '<div style="padding: 0.25em;">' +
                    '<div style="background: darkgray; color: white; text-align: center;" class="align-middle">' + svg_hexa + ' site: ' + feature.id_ + '</div>' +
                                      '<div style="font-size: 0.8em;">' +
                                          '<div>' + status_str + '</div>' +
                                          '<div>' + getDisplayNameOfCategory(feature.get('site_category')) + '</div>' +
                                          '<div>' + feature['values_']['geometry']['flatCoordinates'] + '</div>' +
                                      '</div>' +
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
            addApiarySite: function(apiary_site_geojson) {
                
                let vm = this
                let feature = (new GeoJSON()).readFeature(apiary_site_geojson)

                feature.getGeometry().on("change", function() {
                    let feature_id = feature.getId()
                    if (vm.modifyInProgressList.indexOf(feature_id) == -1) {
                        vm.modifyInProgressList.push(feature_id);
                    }
                })

                this.apiarySitesQuerySource.addFeature(feature)
            },
            removeApiarySiteById: function(apiary_site_id){
                let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
                this.apiarySitesQuerySource.removeFeature(feature)
            },
            // zoomToApiarySiteById: function(apiary_site_id){
                // let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
                // let geometry = feature.getGeometry()
                // let coord = geometry.getCoordinates()
                // let view = this.map.getView()
                // this.map.getView().animate({zoom: 16, center: feature['values_']['geometry']['flatCoordinates']})
                // this.showPopup(feature)
            // },
            setApiarySiteSelectedStatus: function(apiary_site_id, selected) {
                let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
                let style_applied = getApiaryFeatureStyle(getStatusForColour(feature, false, this.display_at_time_of_submitted), selected)
                feature.setStyle(style_applied)
            },
            addEventListeners: function () {

            },
            displayAllFeatures: function() {
                if (this.apiarySitesQuerySource.getFeatures().length>0){
                    let view = this.map.getView()

                    let ext = this.apiarySitesQuerySource.getExtent()
                    let centre = [(ext[0] + ext[2])/2.0, (ext[1] + ext[3])/2.0]
                    //view.fit(ext)
                    let resolution = view.getResolutionForExtent(ext);
                    let z = view.getZoomForResolution(resolution) - 1
                    view.animate({zoom: z, center: centre})
                }
            },
            updateShape: function() {
                
                let vm = this
                vm.shapeVectorSource=null;
                vm.shapeVectorLayer=null;
                if(vm.shapefile_json && Object.keys(vm.shapefile_json).length>0){
                    console.log(vm.shapefile_json);
                    vm.shapeVectorSource = new VectorSource({
                        features: new GeoJSON().readFeatures(vm.shapefile_json),
                    });
                    vm.shapeVectorLayer= new VectorLayer({
                        source: vm.shapeVectorSource,
                    })
                    vm.map.addLayer(vm.shapeVectorLayer);
                    vm.displayAllFeaturesShape();
                }
            },
            addShapeToMap: function(apiary_sites_geojson){
                let features = (new GeoJSON()).readFeatures(apiary_sites_geojson)
                this.shapeVectorSource.addFeatures(features)
            },
            displayAllFeaturesShape: function() {
                if (this.shapeVectorSource.getFeatures().length>0){
                    let view = this.map.getView()

                    let ext = this.shapeVectorSource.getExtent()
                    let centre = [(ext[0] + ext[2])/2.0, (ext[1] + ext[3])/2.0]
                    //view.fit(ext)
                    let resolution = view.getResolutionForExtent(ext);
                    let z = view.getZoomForResolution(resolution) - 1
                    view.animate({zoom: z, center: centre})
                }
            },
        },
    }
</script>

<style lang="css" scoped>
    .map-wrapper {
        position: relative;
        padding: 0;
        margin: 0;
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
    .map {
        width: 100%;
        height: 500px;
    }
</style>
