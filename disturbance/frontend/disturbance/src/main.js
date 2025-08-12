// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import { createApp } from 'vue';
// import resource from 'vue-resource'
import App from './App'
import router from './router'
import helpers from '@/utils/helpers'
import 'bootstrap'
// import api_endpoints from './api'


import $ from 'jquery';
import { extendMoment } from 'moment-range';
import jsZip from 'jszip';
window.JSZip = jsZip;
window.$ = $;

import 'datatables.net';
import 'datatables.net-bs';
import 'datatables.net-responsive-bs';
import 'datatables.net-buttons/js/dataTables.buttons.js'
import 'datatables.net-buttons/js/buttons.html5.js'

import "datatables.net-bs/css/dataTables.bootstrap.css"
import "datatables.net-responsive-bs/css/responsive.bootstrap.css"

import "sweetalert2/dist/sweetalert2.css"

import 'jquery-validation'

import 'select2';
import 'select2/dist/css/select2.min.css';
import 'select2-bootstrap-theme/dist/select2-bootstrap.min.css';



extendMoment(moment);

require( '../node_modules/bootstrap/dist/css/bootstrap.css' );
require('../node_modules/eonasdan-bootstrap-datetimepicker')
require('../node_modules/font-awesome/css/font-awesome.min.css' )
require('../node_modules/jquery.easing')


// import CKEditor from 'ckeditor4-vue';
// app.use( CKEditor );



const app = createApp(App);

const fetch = window.fetch;
window.fetch = ((originalFetch) => {
    return async (...args) => {
        // Prepare headers
        let headers;
        if (args.length > 1) {
            headers =
                args[1].headers instanceof Headers
                    ? args[1].headers
                    : new Headers(args[1].headers || {});
        } else {
            headers = new Headers();
        }

        // Add CSRF token
        headers.set('X-CSRFToken', helpers.getCookie('csrftoken'));

        // Add Content-Type for JSON requests
        if (args.length > 1 && typeof args[1].body === 'string') {
            headers.set('Content-Type', 'application/json');
        }

        // Set headers back to args
        if (args.length > 1) {
            args[1].headers = headers;
        } else {
            args.push({ headers });
        }

        // Await the response to check status
        const response = await originalFetch.apply(this, args);

        // Redirect to login if 401 or 403 from /api endpoints (assume unauthenticated)
        if (
            response.status === 401 ||
            (response.status === 403 &&
                args[0] &&
                typeof args[0] === 'string' &&
                new URL(args[0], window.location.origin).pathname.startsWith(
                    '/api'
                ))
        ) {
            window.location.href =
                '/login/?next=' + encodeURIComponent(window.location.pathname);
        } else if (response.status === 403) {
            swal.fire({
                icon: 'error',
                title: 'Access Denied',
                text: 'You do not have permission to perform this action.',
                customClass: {
                    confirmButton: 'btn btn-primary',
                },
            });
        }

        return response;
    };
})(fetch);

app.use(router);
router.isReady().then(() => app.mount('#app'));
