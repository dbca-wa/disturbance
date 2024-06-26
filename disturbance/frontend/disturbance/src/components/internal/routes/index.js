import InternalDashboard from '../dashboard.vue'
import Search from '../search.vue'
import OrgAccessTable from '../organisations/dashboard.vue'
import OrgAccess from '../organisations/access.vue'
import Organisation from '../organisations/manage.vue'
//import Proposal from '../proposals/proposal.vue'
//import ProposalApiary from '../proposals/proposal_apiary.vue'
import Proposal from '../proposals/proposal_wrapper.vue';
//import Referral from '../referrals/referral.vue'
import Referral from '../referrals/referral_wrapper.vue'
import ApprovalDash from '../approvals/dashboard.vue'
import ComplianceDash from '../compliances/dashboard.vue'
import Compliance from '../compliances/access.vue'
//import Approval from '../approvals/approval.vue'
import Approval from '../approvals/approval_wrapper.vue'
import SiteTransitions from '../site_transitions/site_transitions.vue'
//import AvailableSites from '../available_sites.vue'
import AvailableSites from '@/components/common/apiary/available_sites.vue'
import Reports from '@/components/reports/reports.vue'
import SchemaManager from '../main/schema_manager.vue'

export default
{
    path: '/internal',
    component:
    {
        render(c)
        {
            return c('router-view')
        }
    },
    children: [
        {
            path: '/',
            component: InternalDashboard,
            name:"internal-dashboard",
        },
        {
            path:'reports',
            name:'reports',
            component:Reports
        },
        {
            path: 'approvals',
            component: ApprovalDash,
            name:"internal-approvals-dash"
        },
        {
            path: 'approval/:approval_id',
            component: Approval,
        },
        {
            path: 'sites',
            component: AvailableSites,
            name: 'sites',
            props: { is_internal: true }
        },
        {
            path: 'compliances',
            component: ComplianceDash,
            name:"internal-compliances-dash"
        },
        {
            path: 'compliance/:compliance_id',
            component: Compliance,

        },
        {
            path: 'search',
            component: Search,
            name:"internal-search"
        },
        {
            path: 'site_transitions',
            component: SiteTransitions,
            name:"internal-site-transitions"
        },
        {
            path: 'organisations',
            component: {
                render(c)
                {
                    return c('router-view')
                }
            },
            children: [
                {
                    path: 'access',
                    component: OrgAccessTable,
                    name:"org-access-dash"
                },
                {
                    path: 'access/:access_id',
                    component: OrgAccess,
                    name:"org-access"
                },
                {
                    path: ':org_id',
                    component: Organisation,
                    name:"internal-org-detail"
                },

            ]
        },
        {
            path: 'proposal',
            component: {
                render(c)
                {
                    return c('router-view')
                }
            },
            children: [
                {
                    path: ':proposal_id',
                    component: {
                        render(c)
                        {
                            return c('router-view')
                        }
                    },
                    children: [
                        {
                            path: '/',
                            component: Proposal,
                            name:"internal-proposal"
                        },
                        {
                            path: 'referral/:referral_id',
                            component: Referral,
                            name:"internal-referral"
                        },
                        /*
                        {
                            path: 'apiary',
                            component: ProposalApiary,
                            name:"internal-proposal-apiary"
                        },
                        */
                    ]
                },

            ]
        },
        {
            path: 'schema',
            component: SchemaManager,
            name:"schema-manager"
        },
        /*{
            path: 'proposal',
            component: Proposal,
            name:"new_proposal"
        }*/
    ]
}
