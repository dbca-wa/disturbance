<template lang="html">
    <div>
        <div class="map-wrapper">
            <div class="search-box">
                <input :id="idSearchInput" class="search-input" />
            </div>
            <div :id="idMap" class="mapLeaf"></div>
            <div class="basemap-button">
                <img :id="idBasemapSat" class="basemap-button-img" :src="satelliteIcon" @click.stop="setBaseLayer('sat')" />
                <img :id="idBasemapOsm" class="basemap-button-img" :src="mapIcon" @click.stop="setBaseLayer('osm')" />
            </div>
            <div class="cursor-location">
                <div v-if="cursor_location">
                    <span>{{ cursor_location.lat.toFixed(5) }}, {{ cursor_location.lng.toFixed(5) }}</span>
                </div>
            </div>
            <div class="centre_marker" @click.stop="setMarkerCentre()">
                CenterMarker
            </div>
        </div>

        <div class="col-sm-4 form-group"><div class="row">
            <label class="col-sm-4">Latitude:</label>
            <div v-if="marker_lat">
                <input :readonly="readonly" type="number" min="-90" max="90" class="form-control" v-model.number="marker_lat" />
            </div>
        </div></div>
        <div class="col-sm-4 form-group"><div class="row">
            <label class="col-sm-4">Longitude:</label>
            <div v-if="marker_lng">
                <input :readonly="readonly" type="number" min="-180" max="180" class="form-control" v-model.number="marker_lng" />
            </div>
        </div></div>
    </div>
</template>

<script>
import Leaf from "leaflet";
import "leaflet-measure"; /* This should be imported after leaflet */
import "leaflet.locatecontrol";
import Awesomplete from "awesomplete";
import { guid } from "@/utils/helpers";
import "bootstrap/dist/css/bootstrap.css";
import "awesomplete/awesomplete.css";
import "leaflet/dist/leaflet.css";
import "leaflet-measure/dist/leaflet-measure.css";
import "leaflet.locatecontrol/dist/L.Control.Locate.min.css";
import { api_endpoints } from '@/utils/hooks'
import satelliteIcon from '@/assets/satellite_icon.jpg'
import mapIcon from '@/assets/map_icon.png'

Leaf.TileLayer.WMTS = Leaf.TileLayer.extend({
    defaultWmtsParams: {
        service: 'WMTS',
        request: 'GetTile',
        version: '1.0.0',
        layers: '',
        styles: '',
        tilematrixSet: '',
        format: 'image/jpeg'
    },

    initialize: function (url, options) { // (String, Object)
        this._url = url;
        var wmtsParams = Leaf.extend({}, this.defaultWmtsParams);
        var tileSize = options.tileSize || this.options.tileSize;
        if (options.detectRetina && Leaf.Browser.retina) {
            wmtsParams.width = wmtsParams.height = tileSize * 2;
        } else {
            wmtsParams.width = wmtsParams.height = tileSize;
        }
        for (var i in options) {
            // all keys that are not TileLayer options go to WMTS params
            if (!Object.prototype.hasOwnProperty.call(this.options, i) && i!="matrixIds") {
                wmtsParams[i] = options[i];
            }
        }
        this.wmtsParams = wmtsParams;
        this.matrixIds = options.matrixIds||this.getDefaultMatrix();
        Leaf.setOptions(this, options);
    },

    onAdd: function (map) {
        this._crs = this.options.crs || map.options.crs;
        Leaf.TileLayer.prototype.onAdd.call(this, map);
    },

    getTileUrl: function (coords) { // (Point, Number) -> String
        var tileSize = this.options.tileSize;
        var nwPoint = coords.multiplyBy(tileSize);
        nwPoint.x+=1;
        nwPoint.y-=1;
        var sePoint = nwPoint.add(new Leaf.Point(tileSize, tileSize));
        var zoom = this._tileZoom;
        var nw = this._crs.project(this._map.unproject(nwPoint, zoom));
        var se = this._crs.project(this._map.unproject(sePoint, zoom));
        var tilewidth = se.x-nw.x;
        //zoom = this._map.getZoom();
        var ident = this.matrixIds[zoom].identifier;
        var tilematrix = this.wmtsParams.tilematrixSet + ":" + ident;
        var X0 = this.matrixIds[zoom].topLeftCorner.lng;
        var Y0 = this.matrixIds[zoom].topLeftCorner.lat;
        var tilecol=Math.floor((nw.x-X0)/tilewidth);
        var tilerow=-Math.floor((nw.y-Y0)/tilewidth);
        var url = Leaf.Util.template(this._url, {s: this._getSubdomain(coords)});
        return url + Leaf.Util.getParamString(this.wmtsParams, url) + "&tilematrix=" + tilematrix + "&tilerow=" + tilerow +"&tilecol=" + tilecol;
    },

    setParams: function (params, noRedraw) {
        Leaf.extend(this.wmtsParams, params);
        if (!noRedraw) {
            this.redraw();
        }
        return this;
    },

    getDefaultMatrix : function () {
        /**
         * the matrix3857 represents the projection
         * for in the IGN WMTS for the google coordinates.
         */
        var matrixIds3857 = new Array(22);
        for (var i= 0; i<22; i++) {
            matrixIds3857[i]= {
                identifier    : "" + i,
                topLeftCorner : new Leaf.LatLng(20037508.3428,-20037508.3428)
            };
        }
        return matrixIds3857;
    }
});
Leaf.tileLayer.wmts = function (url, options) {
    return new Leaf.TileLayer.WMTS(url, options);
};

export default {
  name: "map-leaflet2",
    props: {
        marker_longitude: {
            required: false,
            default: null,
        },
        marker_latitude: {
            required: false,
            default: null,
        },
        readonly: {
            required: false,
            default: false,
        }
    },
  data: function() {
    const defaultCentre = [13775786.985667605, -2871569.067879858];

    let vm = this;
    let baseDic = {
      // shadowUrl: import("leaflet/dist/images/marker-shadow.png"),
      shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
      shadowSize: [41, 41],
      shadowAnchor: [12, 41],
      iconSize: [32, 32],
      iconAnchor: [16, 32],
      popupAnchor: [0, -20]
    };
    vm.icon_default = Leaf.icon({
      // iconUrl: require("../../assets/marker-gray-locked.svg"),
      iconUrl: new URL("../../assets/marker-gray-locked.svg", import.meta.url).href,
      ...baseDic
    });
    vm.guid = guid();

    return {
        satelliteIcon,
        mapIcon,
       // marker_lng: vm.marker_longitude,
       // marker_lat: vm.marker_latitude,
            mapboxAccessToken: null,
        marker_lng: null,
        marker_lat: null,
        defaultCenter: defaultCentre,
        projection: null,
        mainMap: null,
        popup: null,
        element: null,
        base_layer: "osm",
        awe: null,
        suggest_list: [],
        feature_marker: null,
        cursor_location: null,
        idMap: vm.guid + "mapLeaf",
        idSearchInput: vm.guid + "SearchInput",
        idBasemapSat: vm.guid + "BasemapSat",
        idBasemapOsm: vm.guid + "BasemapOsm"
    };
  },
    computed: {
     //   marker_lat: function() {
     //       return this.marker_latitude;
     //   },
     //   marker_lng: function() {
     //       return this.marker_longitude;
     //   },
    },
    watch: {
        marker_latitude: function(){
            console.log('watch lat');
            this.marker_lat = this.marker_latitude;
        },
        marker_longitude: function(){
            console.log('watch lng');
            this.marker_lng = this.marker_longitude;
        },
        marker_lat: function(){
            if (!isNaN(this.marker_lat) && !isNaN(this.marker_lng)){
                this.refreshMarkerLocation();
            }
        },
        marker_lng: function(){
            if (!isNaN(this.marker_lat) && !isNaN(this.marker_lng)){
                this.refreshMarkerLocation();
            }
        }
    },
    created: async function() {
        let temp_token = await this.retrieveMapboxAccessToken();
        this.mapboxAccessToken = temp_token.access_token;
    },
    mounted: function() {
        let vm = this;
    
        //vm.$nextTick(function() {
        vm.initMap();
        vm.setBaseLayer("osm");
        vm.initAwesomplete();
        if (vm.marker_lat && vm.marker_lng){
            /* If there is a location loaded, add a marker to the map */
            vm.addMarker([vm.marker_lat, vm.marker_lng]);
        }
        //});
    },
    methods: {
        retrieveMapboxAccessToken: async function(){
            let ret_val = await $.ajax('/api/geocoding_address_search_token');
            return ret_val;
        },
        setMarkerCentre: function() {
            let z = this.mainMap.getZoom();
            if (!isNaN(this.marker_lat) && !isNaN(this.marker_lng)){
                let latlng = [this.marker_lat, this.marker_lng]

                this.mainMap.flyTo(latlng, z, {
                    animate: true,
                    duration: 1.5
                });
            }
        },
        invalidateSize: function(){
             /*
              * Call this method when the map is shown incompletely.
              * Ref: https://gis.stackexchange.com/questions/157128/leaflet-map-isnt-loading-in-the-correct-location
              * Ref: github.com/Leaflet/Leaflet/issues/4835
              */
          let vm = this;
          setTimeout(function(){
             vm.mainMap.invalidateSize();
          }, 300);
        },
        setMarkerIcon: function() {
          let vm = this;
          if (vm.feature_marker) {
            vm.feature_marker.setIcon(vm.icon_default);
          }
        },
        addMarker(latLngArr) {
          let vm = this;
          vm.feature_marker = Leaf.marker(
            { lon: latLngArr[1], lat: latLngArr[0] },
            { icon: vm.icon_default }
          ).on("click", function() {
            // vm.feature_marker.setIcon(myIcon);
          });
          //vm.feature_marker.bindTooltip("click to lock/unlock");
          vm.feature_marker.addTo(vm.mainMap);
          vm.setMarkerIcon();
        },
        search: function(place) {
          var self = this;

          var latlng = this.mainMap.getCenter();
          $.ajax({
            url:
              api_endpoints.geocoding_address_search + 
              encodeURIComponent(place) +
              ".json?" +
              $.param({
                country: "au",
                limit: 10,
                proximity: "" + latlng.lng + "," + latlng.lat,
                        access_token: self.mapboxAccessToken,
                bbox: "112.920934,-35.191991,129.0019283,-11.9662455",
                types:
                  "region,postcode,district,place,locality,neighborhood,address,poi"
              }),
            dataType: "json",
            success: function(data) {
              self.suggest_list = []; // Clear the list first
              if (data.features && data.features.length > 0) {
                for (var i = 0; i < data.features.length; i++) {
                  self.suggest_list.push({
                    label: data.features[i].place_name,
                    value: data.features[i].place_name,
                    feature: data.features[i]
                  });
                }
              }

              self.awe.list = self.suggest_list;
              self.awe.evaluate();
            }
          });
        },
        initAwesomplete: function() {
          var self = this;
          var element_search = document.getElementById(self.idSearchInput);
          this.awe = new Awesomplete(element_search);
          $(element_search)
            .on("keyup", function(ev) {
              var keyCode = ev.keyCode || ev.which;
              if (
                (48 <= keyCode && keyCode <= 90) ||
                (96 <= keyCode && keyCode <= 105) ||
                keyCode == 8 ||
                keyCode == 46
              ) {
                self.search(ev.target.value);
                return false;
              }
            })
            .on("awesomplete-selectcomplete", function(ev) {
              ev.preventDefault();
              ev.stopPropagation();
              /* User selected one of the search results */
              for (var i = 0; i < self.suggest_list.length; i++) {
                if (self.suggest_list[i].value == ev.target.value) {
                  var latlng = {
                    lat: self.suggest_list[i].feature.geometry.coordinates[1],
                    lng: self.suggest_list[i].feature.geometry.coordinates[0]
                  };

                  self.mainMap.flyTo(latlng, 13, {
                    animate: true,
                    duration: 1.5
                  });

                    if (!self.readonly){
                      if (!self.feature_marker) {
                        self.addMarker([latlng.lat, latlng.lng]);
                      } 
                      self.marker_lat = latlng.lat;
                      self.marker_lng = latlng.lng;
                      self.refreshMarkerLocation();
                    }
                }
              }
              return false;
            });
        },
        setBaseLayer: function(selected_layer_name) {
          if (selected_layer_name == "sat") {
            this.mainMap.removeLayer(this.tileLayer);
            this.mainMap.addLayer(this.tileLayerSat);
            $("#" + this.idBasemapSat).hide();
            $("#" + this.idBasemapOsm).show();
          } else {
            this.mainMap.removeLayer(this.tileLayerSat);
            this.mainMap.addLayer(this.tileLayer);
            $("#" + this.idBasemapOsm).hide();
            $("#" + this.idBasemapSat).show();
          }
        },
        /* this function retrieve the coordinates from vuex and applys it to the marker */
        refreshMarkerLocation: function() {
            if (!isNaN(this.marker_lat) && !isNaN(this.marker_lng)){
                let latlng = [this.marker_lat, this.marker_lng];
                console.log('refreshMarkerLocation');
                console.log(latlng);

                if (!this.feature_marker) {
                    this.addMarker(latlng);
                } else {
                    this.feature_marker.setLatLng({
                        lat: this.marker_lat,
                        lng: this.marker_lng,
                    });
                }

                this.$emit('location-updated', {'lat': this.marker_lat, 'lng': this.marker_lng});
          }
        },
        initMap: function() {
            // Dependingn on when the coordinates are passed to this component,
            // this.marker_lat and this.marker_lng are not updated properly...
            // Therefore update them here to make sure
            this.marker_lat = this.marker_latitude;
            this.marker_lng = this.marker_longitude;

            if (this.marker_lat && this.marker_lng) {
                this.mainMap = Leaf.map(this.idMap).setView([this.marker_lat, this.marker_lng], 12);
            } else {
                this.mainMap = Leaf.map(this.idMap).setView([-31.9505, 115.8605], 4);
            }

          this.tileLayer = Leaf.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
              attribution:
                '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, contributiors'
            }
          );

          this.tileLayerSat = Leaf.tileLayer.wmts(
            env['kb_server_url'] +"/geoserver/gwc/service/wmts",
            {
              layer: "kaartdijin-boodja-public:mapbox-satellite-public",
              tilematrixSet: "mercator",
              format: "image/png"
            }
          );

          this.mainMap
            .on("click", this.onClick)
            .on("mousemove", this.onMouseMove)
            .on("mouseout", this.onMouseOut);
          this.setBaseLayer("osm");
          let measureControl = new Leaf.Control.Measure({
            position: "topleft",
            primaryLengthUnit: "meters",
            activeColor: "#ff7f50",
            completedColor: "#228b22"
          });
          measureControl.addTo(this.mainMap);
          Leaf.control.locate().addTo(this.mainMap);
        },
        onMouseMove: function(e) {
          let vm = this;
          vm.cursor_location = vm.mainMap.mouseEventToLatLng(e.originalEvent);
        },
        onMouseOut: function() {
          this.cursor_location = null;
        },
        onClick: function(e) {
            if (!this.readonly){
                let self = this;
                let latlng = this.mainMap.mouseEventToLatLng(e.originalEvent);
                if (!self.feature_marker) {
                    self.addMarker([latlng.lat, latlng.lng]);
                }

                /* User clicked on a map, not on any feature */
                this.marker_lat = latlng.lat;
                this.marker_lng = latlng.lng;
            }
        }
    }
};
</script>

<style scoped lang="css">
.map-wrapper {
  position: relative;
}
.mapLeaf {
  /* position: relative; */
  height: 500px;
  /* width: 800px; */
  cursor: default;
}
.search-box {
  z-index: 1000;
  position: absolute;
  top: 10px;
  left: 50px;
}
.search-input {
  z-index: 1000;
  width: 300px;
  padding: 5px;
  -moz-border-radius: 5px;
  -webkit-border-radius: 5px;
  border-radius: 5px;
}
.basemap-button {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 400;
  -moz-box-shadow: 3px 3px 3px #777;
  -webkit-box-shadow: 3px 3px 3px #777;
  box-shadow: 3px 3px 3px #777;
  -moz-filter: brightness(1);
  -webkit-filter: brightness(1);
  filter: brightness(1);
  border: 2px white solid;
}
.basemap-button:hover {
  cursor: pointer;
  -moz-filter: brightness(0.9);
  -webkit-filter: brightness(0.9);
  filter: brightness(0.9);
}
.basemap-button:active {
  top: 11px;
  right: 9px;
  -moz-box-shadow: 2px 2px 2px #555;
  -webkit-box-shadow: 2px 2px 2px #555;
  box-shadow: 2px 2px 2px #555;
  -moz-filter: brightness(0.8);
  -webkit-filter: brightness(0.8);
  filter: brightness(0.8);
}
.basemap-button:active {
  top: 11px;
  right: 9px;
  -moz-box-shadow: 2px 2px 2px #555;
  -webkit-box-shadow: 2px 2px 2px #555;
  box-shadow: 2px 2px 2px #555;
  -moz-filter: brightness(0.8);
  -webkit-filter: brightness(0.8);
  filter: brightness(0.8);
}
.location_address_field {
  resize: vertical;
}
.cursor-location {
  position: absolute;
  bottom: 0px;
  color: white;
  background-color: rgba(37, 45, 51, 0.6);
  z-index: 1050;
  font-size: 0.9em;
  padding: 5px;
}
.centre_marker {
  position: absolute;
  bottom: 30px;
  color: white;
  background-color: rgba(37, 45, 51, 0.6);
  z-index: 1050;
  font-size: 0.9em;
  padding: 5px;
  cursor: pointer;
}
</style>
