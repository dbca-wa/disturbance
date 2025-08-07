import {Circle as CircleStyle, Fill, Stroke, Style, Icon} from 'ol/style';

export const SiteColours = {
    'draft': {
        'fill': '#e0e0e0',
        'stroke': '#616161',
    },
    'draft_external': {
        'fill': '#ffdd44',
        'stroke': '#ffcc33',
    },
    'pending': {
        'fill': '#0070FF',
        'stroke': '#000000',
    },
    'current': {
        'fill': '#00ff00',
        'stroke': '#000000',
    },
    'approved': {
        'fill': '#0070ff',
        'stroke': '#000000',
    },
    'suspended': {
        'fill': '#ffffff',
        'stroke': '#000000',
    },
    'not_to_be_reissued': {
        'fill': '#ff0000',
        'stroke': '#000000',
    },
    'denied': {
        'fill': '#000000',
        'stroke': '#000000',
        'icon_colour': '#000000',
    },
    'vacant': {
        'fill': '#ffaa00',
        'stroke': '#000000'
    },
    'pending_vacant': {
        'fill': '#ffaa00',
        'stroke': '#0077FF'
    },
    'transferred': {
        'fill': '#888888',
        'stroke': '#000000',
    },
    'dpaw_pool_of_sites': {
        'fill': '#a900e6',
        'stroke': '#000000',
        'icon_colour': '#a900e6',
    },
    'making_payment': {
        'fill': '#40e0d0',
        'stroke': '#000000'
    },
    'discarded': {
        'fill': '#ffe0d0',
        'stroke': '#ff0000'
    },
    'default': {
        'fill': '#40e0d0',
        'stroke': '#000000'
    }
}
export default SiteColours
export let existingSiteRadius = 5
export let drawingSiteRadius = 7
export function getStatusForColour(feature_or_apiary_site, vacant_suppress_discard = true, display_at_time_of_submitted = false){
    let my_status = ''
    let is_vacant = false
    let is_vacant_when_submitted = false
    let making_payment = false

    if (Object.prototype.hasOwnProperty.call(feature_or_apiary_site, 'ol_uid')) {
        // feature_or_apiary_site is Feature object
        my_status = feature_or_apiary_site.get("status");
        is_vacant = feature_or_apiary_site.get('is_vacant')
        making_payment = feature_or_apiary_site.get('making_payment')
        is_vacant_when_submitted = feature_or_apiary_site.get('apiary_site_is_vacant_when_submitted')
    } else {
        // feature_or_apiary_site is apiary_site object
        my_status = feature_or_apiary_site.properties.status
        is_vacant = feature_or_apiary_site.properties.is_vacant
        making_payment = feature_or_apiary_site.properties.making_payment
        is_vacant_when_submitted = feature_or_apiary_site.properties.apiary_site_is_vacant_when_submitted
    }

    if (display_at_time_of_submitted){
        my_status = 'pending'
        if (is_vacant_when_submitted){
            my_status = 'vacant'
        }
    } else {
        if (making_payment){
            my_status = 'making_payment'
        } else {
            if (is_vacant){
                // Vacant
                if (my_status == 'pending'){
                    my_status = 'pending_vacant'
                } else {
                    if (!vacant_suppress_discard && my_status == 'discarded'){
                        // When the site is 'vacant' and 'discarded', status remains the 'discarded'
                    } else {
                        // Set 'vacant' to the site status
                        my_status = 'vacant'
                    }
                }
            }
        }
    }

    return my_status
}
export function getApiaryFeatureStyle(status, selected=false, stroke_width_when_selected=2){
    let additional_width = selected ? stroke_width_when_selected : 0
    switch(status){
        case 'draft':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.draft.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.draft.stroke,
                        width: 1 + additional_width
                    })
                })
            });
        case 'pending':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.pending.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.pending.stroke,
                        width: 1 + additional_width
                    })
                })
            });
        case 'current':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.current.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.current.stroke,
                        width: 1 + additional_width
                    })
                })
            });
        case 'approved':
            // Apiary site can be 'approved' status on a proposal
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.current.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.current.stroke,
                        width: 1 + additional_width
                    })
                })
            });
        case 'suspended':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.suspended.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.suspended.stroke,
                        width: 1 + additional_width
                    })
                })
            });
        case 'not_to_be_reissued':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.not_to_be_reissued.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.not_to_be_reissued.stroke,
                        width: 1 + additional_width
                    })
                })
            });
        case 'denied':
            return new Style({
                image: new Icon({
                    color: SiteColours.denied.icon_colour,
                    //src: "data/x2.png"
                    src: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwgAADsIBFShKgAAAABl0RVh0U29mdHdhcmUAcGFpbnQubmV0IDQuMC4xMzQDW3oAAACMSURBVChTlZDbDYAwDAM7AAOw/ypISEyAEMOUXHDS8viAk0xDYkPbUmv9pShgMg3lBj3NIAOrv95C1OoBngyMaoCHpN6M5wzoa31olsDN8rQAMDBtpoDazWD1I8A2FlNA3Z+pBRiYYs+7BHkRtp4PGhpAHPDtIjJwMfsvDWr1AE8G4GIO6GkGGfioWg6CRJYCwPQeRwAAAABJRU5ErkJggg=="
                })
            });
        case 'transferred':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.transferred.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.transferred.stroke,
                        width: 1 + additional_width
                    })
                })
            });
        case 'discarded':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.discarded.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.discarded.stroke,
                        width: 1 + additional_width
                    })
                })
            });
        case 'vacant':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.vacant.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.vacant.stroke,
                        width: 1 + additional_width
                    })
                })
            });
        case 'pending_vacant':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.pending_vacant.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.pending_vacant.stroke,
                        width: 1 + additional_width
                    })
                })
            });
        case 'dpaw_pool_of_sites':
            return new Style({
                image: new Icon({
                color: SiteColours.dpaw_pool_of_sites.icon_colour,
                    //src: "data/+2.png"
                    src: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAZdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuMTM0A1t6AAAAQklEQVQoU52LMQoAIBDD/P+n69KAmBvEQJaGriSToKahgpqGCmoaKqhpqKB2xie+DpOgpqGCmoYKahoqqGmocO1ZGzz92jSqmlDHAAAAAElFTkSuQmCC"
                }),
            });
        case 'making_payment':
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.making_payment.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.making_payment.stroke,
                        width: 1 + additional_width
                    })
                })
            });
        default:
            return new Style({
                image: new CircleStyle({
                    radius: existingSiteRadius,
                    fill: new Fill({
                        color: SiteColours.default.fill
                    }),
                    stroke: new Stroke({
                        color: SiteColours.default.stroke,
                        width: 2 + additional_width
                    })
                })
            });
    }
}
export function getDisplayNameOfCategory(key) {
    switch(key){
        case 'south_west':
            return 'South West'
        case 'remote':
            return 'Remote'
        default:
            return ''
    }
}
export function getDisplayNameFromStatus(status_name){
    switch(status_name){
        case 'draft':
            return 'Draft'
        case 'pending':
            return 'Pending'
        case 'approved':
            return 'Approved'
        case 'denied':
            return 'Denied'
        case 'current':
            return 'Current'
        case 'not_to_be_reissued':
            return 'Not to be re-issued'
        case 'suspended':
            return 'Suspended'
        case 'transferred':
            return 'Transferred'
        case 'vacant':
            return 'Vacant'
        case 'discarded':
            return 'Discarded'
        default:
            if (status_name.toLowerCase().includes('vacant') && status_name.toLowerCase().includes('pending')){
                //return 'Pending (vacant)'
                return 'Pending'
            }
            return status_name
    }
}
export function zoomToCoordinates(map, coordinates, zoomLevel){
    let currentZoomLevel = map.getView().getZoom()
    let targetZoomLevel = (zoomLevel) ? zoomLevel : currentZoomLevel
    map.getView().animate({
        zoom: targetZoomLevel,
        center: coordinates
    })
}
export function checkIfValidlatitudeAndlongitude(str) {
    // Regular expression to check if string is a latitude and longitude
    // const regexExp = /^((\-?|\+?)?\d+(\.\d+)?),\s*((\-?|\+?)?\d+(\.\d+)?)$/gi;
    const regexExp = /^\s*((-?|\+?)?\d+(\.\d+)?)[,,/]\s*((-?|\+?)?\d+(\.\d+)?)$/gi;

    let regResult = regexExp.exec(str)

    return regResult
}