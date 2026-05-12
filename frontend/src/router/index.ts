import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/pages/DashboardPage.vue'),
  },
  {
    path: '/map',
    name: 'MapStats',
    component: () => import('@/pages/MapStatsPage.vue'),
  },
  {
    path: '/players',
    name: 'PlayerStats',
    component: () => import('@/pages/PlayerStatsPage.vue'),
  },
  {
    path: '/battle',
    name: 'BattleStats',
    component: () => import('@/pages/BattleStatsPage.vue'),
  },
  {
    path: '/craft',
    name: 'CraftStats',
    component: () => import('@/pages/CraftStatsPage.vue'),
  },
  {
    path: '/items',
    name: 'ItemStats',
    component: () => import('@/pages/ItemStatsPage.vue'),
  },
  {
    path: '/activity',
    name: 'Activity',
    component: () => import('@/pages/ActivityPage.vue'),
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router