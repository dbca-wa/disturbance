import { Fill, Stroke, Style, Text, RegularShape } from 'ol/style';
import { getLength } from 'ol/sphere'

let MeasureStyles = {
    'defaultStyle': new Style({
        fill: new Fill({
            color: 'rgba(255, 255, 255, 0.2)',
        }),
        stroke: new Stroke({
            //color: 'rgba(0, 0, 0, 0.5)',
            color: '#53c2cf',
            //lineDash: [10, 10],
            width: 1,
        }),
        //image: new CircleStyle({
        //    radius: 5,
        //    stroke: new Stroke({
        //        color: 'rgba(0, 0, 0, 0.7)',
        //    }),
        //    fill: new Fill({
        //        color: 'rgba(255, 255, 255, 0.2)',
        //    }),
        //}),
        image: new RegularShape({
            stroke: new Stroke({
                color: 'red',
                width: 1,
            }),
            points: 4,
            radius: 10,
            radius2: 0,
            angle: Math.PI / 4
        }),
    }),
    'segmentStyle': new Style({
        text: new Text({
            font: '12px Calibri,sans-serif',
            fill: new Fill({
                color: 'rgba(255, 255, 255, 1)',
            }),
            backgroundFill: new Fill({
                color: 'rgba(0, 0, 0, 0.4)',
            }),
            padding: [2, 2, 2, 2],
            textBaseline: 'bottom',
            offsetY: -12,
        }),
        image: new RegularShape({
            radius: 6,
            points: 3,
            angle: Math.PI,
            displacement: [0, 8],
            fill: new Fill({
                color: 'rgba(0, 0, 0, 0.4)',
            }),
        }),
    }),
    'labelStyle': new Style({
        text: new Text({
            font: '14px Calibri,sans-serif',
            fill: new Fill({
                color: 'rgba(255, 255, 255, 1)',
            }),
            backgroundFill: new Fill({
                color: 'rgba(0, 0, 0, 0.7)',
            }),
            padding: [3, 3, 3, 3],
            textBaseline: 'bottom',
            offsetY: -15,
        }),
        image: new RegularShape({
            radius: 8,
            points: 3,
            angle: Math.PI,
            displacement: [0, 10],
            fill: new Fill({
                color: 'rgba(0, 0, 0, 0.7)',
            }),
        }),
    }),
}
export function formatLength(line) {
    let cloned_line = line.clone()
    cloned_line.transform('EPSG:4326', 'EPSG:3857')
    const length = getLength(cloned_line);
    let output;
    if (length > 100) {
        output = Math.round((length / 1000) * 100) / 100 + ' km';
    } else {
        output = Math.round(length * 100) / 100 + ' m';
    }
    return output;
}

export default MeasureStyles

