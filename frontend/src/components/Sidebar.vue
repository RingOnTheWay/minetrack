<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDataStore } from '@/stores/data'
import { useAppStore } from '@/stores/app'
import type { NavKey } from '@/stores/app'
import {
  LayoutDashboard, Map, Users, Swords, Hammer, Package, TrendingUp,
  Database, Languages, Moon, Sun
} from 'lucide-vue-next'

import iconUrl from '/icon.png'

const { t, locale } = useI18n()
const router = useRouter()
const route = useRoute()
const data = useDataStore()
const app = useAppStore()

const allMenuItems = computed(() => [
  { icon: LayoutDashboard, label: t('nav.dashboard'), path: '/' as NavKey, badge: null },
  { icon: Map, label: t('nav.mapStats'), path: '/map' as NavKey, badge: null },
  { icon: Users, label: t('nav.playerStats'), path: '/players' as NavKey, badge: data.allPlayers.size > 0 ? String(data.allPlayers.size) : null },
  { icon: Swords, label: t('nav.battleStats'), path: '/battle' as NavKey, badge: null },
  { icon: Hammer, label: t('nav.craftStats'), path: '/craft' as NavKey, badge: null },
  { icon: Package, label: t('nav.itemStats'), path: '/items' as NavKey, badge: null },
  { icon: TrendingUp, label: t('nav.activity'), path: '/activity' as NavKey, badge: null },
  { icon: Database, label: t('nav.dataManage'), path: '/data-manage' as NavKey, badge: null },
])

const menuItems = computed(() => allMenuItems.value.filter(item => app.isNavVisible(item.path)))

const currentPath = computed(() => route.path)
const isSettingsPage = computed(() => route.path === '/settings')

function navigate(path: string) {
  router.push(path)
}

function toggleLocale() {
  locale.value = locale.value === 'zh-CN' ? 'en-US' : 'zh-CN'
  try {
    localStorage.setItem('locale', locale.value)
  } catch {}
}
</script>

<template>
  <div class="w-56 h-full bg-white/80 dark:bg-slate-900/90 backdrop-blur-xl border-r border-brand/10 dark:border-brand/20 flex flex-col relative overflow-hidden">
    <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-brand/10 to-transparent dark:from-brand/5 dark:to-transparent rounded-full blur-3xl" />

    <div class="relative p-6 border-b border-brand/10 dark:border-brand/20">
      <div class="flex items-center gap-3">
        <img :src="iconUrl" alt="MineTrack" class="w-10 h-10 rounded-lg shadow-md hover:shadow-lg hover:-translate-y-1 transition-all duration-300" />
        <span class="text-lg font-semibold text-slate-800 dark:text-slate-100">MineTrack</span>
      </div>
    </div>

    <nav class="relative flex-1 p-3 space-y-1 overflow-y-auto">
      <button
        v-for="(item, index) in menuItems"
        :key="item.path"
        v-motion-slide-left="{ delay: index * 50 }"
        class="relative w-full flex items-center justify-between px-4 py-3 rounded-lg transition-all duration-300 group"
        :class="!isSettingsPage && currentPath === item.path
          ? 'nav-item-active'
          : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100/80 dark:hover:bg-slate-800/60'"
        @click="navigate(item.path)"
      >
        <div class="relative flex items-center gap-3">
          <div
            class="nav-icon transition-colors"
            :class="!isSettingsPage && currentPath === item.path ? '' : 'text-slate-500 dark:text-slate-500'"
          >
            <component :is="item.icon" class="w-5 h-5" />
          </div>
          <span class="text-sm font-medium">{{ item.label }}</span>
        </div>

        <span
          v-if="item.badge"
          class="px-2 py-0.5 text-xs font-semibold rounded-full"
          :class="item.badge === 'New'
            ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white'
            : 'bg-brand/20 text-brand dark:bg-brand/30 dark:text-brand-light'"
        >
          {{ item.badge }}
        </span>

        <div
          v-if="!isSettingsPage && currentPath === item.path"
          class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-brand to-brand-light rounded-r-full"
        />
      </button>
    </nav>

    <div class="relative p-4 border-t border-brand/10 dark:border-brand/20">
      <div class="flex items-center gap-2">
        <button
          class="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100/80 dark:hover:bg-slate-800/60 transition-all"
          @click="toggleLocale"
        >
          <Languages class="w-4 h-4" />
          <span class="text-sm font-medium">{{ t('lang.switchTo') }}</span>
        </button>
        <button
          class="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100/80 dark:hover:bg-slate-800/60 transition-all"
          @click="app.toggleDarkMode()"
        >
          <Transition name="theme-icon" mode="out-in">
            <Moon v-if="!app.isDark" key="moon" class="w-4 h-4" />
            <Sun v-else key="sun" class="w-4 h-4" />
          </Transition>
          <span class="text-sm font-medium">{{ app.isDark ? t('theme.light') : t('theme.dark') }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.theme-icon-enter-active,
.theme-icon-leave-active {
  transition: all 0.2s ease;
}
.theme-icon-enter-from {
  opacity: 0;
  transform: rotate(-90deg) scale(0.5);
}
.theme-icon-leave-to {
  opacity: 0;
  transform: rotate(90deg) scale(0.5);
}
</style>
