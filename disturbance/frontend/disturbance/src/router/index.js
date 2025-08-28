import { createRouter, createWebHistory } from 'vue-router';
import LedgerPay from '@/components/ledgerpay.vue'
import Profile from '@/components/user/profile.vue'
import external_routes from '@/components/external/routes'
import internal_routes from '@/components/internal/routes'

const router = createRouter({
  history: createWebHistory(),
  strict: false,
  routes: [
        {
          path: '/firsttime',
          name: 'first-time',
          component: Profile
        },
        {
          path: '/account',
          name: 'account',
          component: Profile
        },
        {
          path: '/ledgerpay/:payment_item',
          name: 'ledgerpay',
          component: LedgerPay
        },
        external_routes,
        internal_routes
    ]
})

export default router;
