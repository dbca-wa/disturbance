// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import { createApp } from 'vue';
// import resource from 'vue-resource'
import App from './App'
import router from './router'
import helpers from '@/utils/helpers'
import api_endpoints from './api'


// import { extendMoment } from 'moment-range';
import jsZip from 'jszip';
window.JSZip = jsZip;

import 'datatables.net';
import 'datatables.net-bs';
import 'datatables.net-responsive-bs';
import 'datatables.net-buttons/js/dataTables.buttons.js'
import 'datatables.net-buttons/js/buttons.html5.js'

import "datatables.net-bs/css/dataTables.bootstrap.css"
import "datatables.net-responsive-bs/css/responsive.bootstrap.css"

import "sweetalert2/dist/sweetalert2.css"

// import 'jquery-validation'


// extendMoment(moment);

require( '../node_modules/bootstrap/dist/css/bootstrap.css' );
require('../node_modules/eonasdan-bootstrap-datetimepicker')
require('../node_modules/font-awesome/css/font-awesome.min.css' )
require('../node_modules/jquery.easing')

app.config.devtools = true;
app.config.productionTip = false
// app.use( resource );
app.prototype.$log = console.log

// import CKEditor from 'ckeditor4-vue';
// app.use( CKEditor );

// Add CSRF Token to every request
// Vue.http.interceptors.push( function ( request, next ) {
//   // modify headers
//   if ( request.url != api_endpoints.countries ) {
//     request.headers.set( 'X-CSRFToken', helpers.getCookie( 'csrftoken' ) );
//   }

//   // continue to next interceptor
//   next();
// } );


// /* eslint-disable no-new */
// new Vue( {
//   el: '#app',
//   router,
//   template: '<App/>',
//   components: {
//     App
//   }
// } )

// Add CSRF Token to every request
// const customHeaders = new Headers({
//     'X-CSRFToken': helpers.getCookie('csrftoken'),
// });
// const customHeadersJSON = new Headers({
//     'X-CSRFToken': helpers.getCookie('csrftoken'),
//     'Content-Type': 'application/json',
// });

const app = createApp(App);

// const fetch = window.fetch;
// window.fetch = ((originalFetch) => {
//     return (...args) => {
//         if (args.length > 1) {
//             if (typeof args[1].body === 'string') {
//                 args[1].headers = customHeadersJSON;
//             } else {
//                 args[1].headers = customHeaders;
//             }
//         }
//         const result = originalFetch.apply(this, args);
//         return result;
//     };
// })(fetch);

app.use(router);
router.isReady().then(() => app.mount('#app'));
