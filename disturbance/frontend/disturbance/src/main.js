import './jquery-global.js';

import 'bootstrap/dist/css/bootstrap.css'; // CSS first
import 'bootstrap'; // Bootstrap JS after jQuery

import 'vite/modulepreload-polyfill';

import 'font-awesome/css/font-awesome.min.css';
import 'jquery.easing';

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import helpers from '@/utils/helpers';


import _ from 'lodash';
window._ = _;
import moment from 'moment';
// window.moment = moment;
import { extendMoment } from 'moment-range';
extendMoment(moment);
import select2 from 'select2';
import swal from 'sweetalert2';
window.swal = swal;
select2();
import jsZip from 'jszip';
window.JSZip = jsZip;

import 'bootstrap/dist/js/bootstrap.bundle.min.js';
// import 'eonasdan-bootstrap-datetimepicker'; // After Bootstrap JS
import 'datatables.net-bs5';
import 'datatables.net-buttons-bs5';
import 'datatables.net-responsive-bs5';
import 'datatables.net-buttons/js/dataTables.buttons.js';
import 'datatables.net-buttons/js/buttons.html5.js';

import 'sweetalert2/dist/sweetalert2.css';
import 'jquery-validation';
import 'select2/dist/css/select2.min.css';
import 'select2-bootstrap-theme/dist/select2-bootstrap.min.css';
import '@/../node_modules/datatables.net-bs5/css/dataTables.bootstrap5.min.css';
import '@/../node_modules/datatables.net-responsive-bs5/css/responsive.bootstrap5.min.css';
import 'summernote/dist/summernote';
import 'summernote/dist/summernote.min.css';
import 'summernote/dist/summernote-lite.min.css';
import 'summernote/dist/summernote-lite.min.js';
// import '@/../node_modules/font-awesome/css/font-awesome.min.css';


const app = createApp(App);

const originalFetch = window.fetch.bind(window);

// Do NOT make the outer wrapper async; otherwise window.fetch becomes a Promise.
window.fetch = ((orig) => {
    return async (...args) => {
        // Normalize URL (string | URL | Request)
        let url;
        if (args[0] instanceof Request) {
            url = new URL(args[0].url, window.location.origin);
        } else if (args[0] instanceof URL) {
            url = new URL(args[0].href, window.location.origin);
        } else {
            url = new URL(String(args[0]), window.location.origin);
        }
        const sameOrigin = url.origin === window.location.origin;
        const isApi = sameOrigin && url.pathname.startsWith('/api');

        // Merge headers
        let headers = new Headers();
        if (args.length > 1 && args[1]?.headers) {
            headers =
                args[1].headers instanceof Headers
                    ? new Headers(args[1].headers)
                    : new Headers(args[1].headers);
        } else if (args[0] instanceof Request && args[0].headers) {
            headers = new Headers(args[0].headers);
        }

        if (sameOrigin)
            headers.set('X-CSRFToken', helpers.getCookie('csrftoken'));
        if (
            sameOrigin &&
            args.length > 1 &&
            typeof args[1]?.body === 'string'
        ) {
            headers.set('Content-Type', 'application/json');
        }

        if (args.length > 1) {
            args[1].headers = headers;
        } else {
            args.push({ headers });
        }

        const response = await orig(...args);

        if (
            (response.status === 401 && isApi) ||
            (response.status === 403 && isApi)
        ) {
            window.location.href =
                '/login/?next=' +
                encodeURIComponent(
                    window.location.pathname +
                        window.location.search +
                        window.location.hash
                );
            return response;
        } else if (response.status === 403) {
            swal.fire({
                icon: 'error',
                title: 'Access Denied',
                text: 'You do not have permission to perform this action.',
                customClass: { confirmButton: 'btn btn-primary' },
            });
        }
        return response;
    };
})(originalFetch);

app.use(router);
router.isReady().then(() => app.mount('#app'));
