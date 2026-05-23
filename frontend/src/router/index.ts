import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAppStore } from '@/stores/app'

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
    path: '/blocks',
    name: 'BlockStats',
    component: () => import('@/pages/BlockStatsPage.vue'),
  },
  {
    path: '/activity',
    name: 'Activity',
    component: () => import('@/pages/ActivityPage.vue'),
  },
  {
    path: '/honor',
    name: 'HonorTitles',
    component: () => import('@/pages/HonorTitlesPage.vue'),
  },
  {
    path: '/data-manage',
    name: 'DataManage',
    component: () => import('@/pages/DataImportPage.vue'),
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/pages/SettingsPage.vue'),
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to) => {
  const app = useAppStore()
  if (to.path !== router.currentRoute.value.path) {
    app.setRouteLoading(true, to.path)
  }
})

router.afterEach(() => {
  const app = useAppStore()
  app.setRouteLoading(false)
})

function prefetchRoutes() {
  requestIdleCallback(() => {
    routes.forEach((route) => {
      if (typeof route.component === 'function') {
        ;(route.component as () => Promise<unknown>)().catch(() => {})
      }
    })
  })
}

export { prefetchRoutes }
export default router
