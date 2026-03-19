import { createRouter, createWebHistory } from 'vue-router'
import LocalExcelDashboard from '../views/LocalExcelDashboard.vue'

import OverviewView from '../views/OverviewView.vue'
import SpatiotemporalView from '../views/SpatiotemporalView.vue'
import TypesView from '../views/TypesView.vue'
import TrendView from '../views/TrendView.vue'
import AssistantView from '../views/AssistantView.vue'
import CollaborationView from '../views/CollaborationView.vue'
import ReportView from '../views/ReportView.vue'

const routes = [
  { path: '/', component: LocalExcelDashboard },
  { path: '/local-dashboard', component: LocalExcelDashboard },
  { path: '/spatiotemporal', component: SpatiotemporalView },
  { path: '/types', component: TypesView },
  { path: '/trend', component: TrendView },
  { path: '/assistant', component: AssistantView },
  { path: '/collaboration', component: CollaborationView },
  { path: '/report', component: ReportView }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
