<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDataStore } from '@/stores/data'
import { useAppStore } from '@/stores/app'
import type { NavKey } from '@/stores/app'
import {
  LayoutDashboard, Map, Users, Swords, Hammer, Package, Pickaxe, TrendingUp,
  Database, Languages, Moon, Sun
} from 'lucide-vue-next'

import iconUrl from '/icon.png'

const { t, locale } = useI18n()
const router = useRouter()
const route = useRoute()
const data = useDataStore()
const app = useAppStore()

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const allMenuItems = computed(() => [
  { icon: LayoutDashboard, label: t('nav.dashboard'), path: '/' as NavKey, badge: null },
  { icon: Map, label: t('nav.mapStats'), path: '/map' as NavKey, badge: null },
  { icon: Users, label: t('nav.playerStats'), path: '/players' as NavKey, badge: data.allPlayers.size > 0 ? String(data.allPlayers.size) : null },
  { icon: Swords, label: t('nav.battleStats'), path: '/battle' as NavKey, badge: null },
  { icon: Hammer, label: t('nav.craftStats'), path: '/craft' as NavKey, badge: null },
  { icon: Package, label: t('nav.itemStats'), path: '/items' as NavKey, badge: null },
  { icon: Pickaxe, label: t('nav.blockStats'), path: '/blocks' as NavKey, badge: null },
  { icon: TrendingUp, label: t('nav.activity'), path: '/activity' as NavKey, badge: null },
  { icon: Database, label: t('nav.dataManage'), path: '/data-manage' as NavKey, badge: null },
])

const menuItems = computed(() => allMenuItems.value.filter(item => app.isNavVisible(item.path)))

const currentPath = computed(() => route.path)
const isSettingsPage = computed(() => route.path === '/settings')

function navigate(path: string) {
  router.push(path)
  emit('close')
}

function toggleLocale() {
  locale.value = locale.value === 'zh-CN' ? 'en-US' : 'zh-CN'
  try {
    localStorage.setItem('locale', locale.value)
  } catch {}
}
</script>

<template>
  <div class="hidden md:flex w-56 h-full bg-white/80 dark:bg-slate-900/90 backdrop-blur-xl border-r border-brand/10 dark:border-brand/20 flex-col relative overflow-hidden sidebar-desktop">
    <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-brand/10 to-transparent dark:from-brand/5 dark:to-transparent rounded-full blur-3xl" />

    <div class="relative p-6 border-b border-brand/10 dark:border-brand/20">
      <div class="flex items-center gap-3">
        <img :src="iconUrl" alt="MineTrack" class="w-10 h-10 rounded-lg shadow-md hover:shadow-lg hover:-translate-y-1 transition-all duration-300" />
        <span class="text-lg font-semibold text-slate-800 dark:text-slate-100">MineTrack</span>
      </div>
    </div>

    <nav class="relative flex-1 p-3 space-y-1 overflow-y-auto overflow-x-hidden hide-scrollbar">
      <TransitionGroup name="nav-item">
        <button
          v-for="item in menuItems"
          :key="item.path"
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
              : 'nav-badge'"
          >
            {{ item.badge }}
          </span>

          <div
            v-if="!isSettingsPage && currentPath === item.path"
            class="nav-indicator absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-r-full"
          />
        </button>
      </TransitionGroup>
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

  <Teleport to="body">
    <Transition name="sidebar-overlay">
      <div v-if="open" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-[100] md:hidden" @click="emit('close')" />
    </Transition>

    <Transition name="sidebar-drawer">
      <div
        v-if="open"
        class="fixed inset-y-0 left-0 w-72 bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border-r border-brand/10 dark:border-brand/20 flex flex-col z-[101] md:hidden shadow-2xl"
      >
        <div class="relative p-6 border-b border-brand/10 dark:border-brand/20">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <img :src="iconUrl" alt="MineTrack" class="w-10 h-10 rounded-lg shadow-md" />
              <span class="text-lg font-semibold text-slate-800 dark:text-slate-100">MineTrack</span>
            </div>
            <button
              class="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
              @click="emit('close')"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
        </div>

        <nav class="relative flex-1 p-3 space-y-1 overflow-y-auto overflow-x-hidden hide-scrollbar">
          <button
            v-for="item in menuItems"
            :key="item.path"
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
              class="px-2 py-0.5 text-xs font-semibold rounded-full nav-badge"
            >
              {{ item.badge }}
            </span>

            <div
              v-if="!isSettingsPage && currentPath === item.path"
              class="nav-indicator absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-r-full"
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
    </Transition>
  </Teleport>
</template>

<style scoped>
.nav-indicator {
  background: linear-gradient(to bottom, var(--brand), var(--brand-light));
}

.nav-badge {
  background-color: color-mix(in srgb, var(--brand) 20%, transparent);
  color: var(--brand);
}

:global(.dark) .nav-badge {
  background-color: color-mix(in srgb, var(--brand) 30%, transparent);
  color: var(--brand-light);
}

.nav-item-enter-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.nav-item-leave-active {
  transition: all 0.12s cubic-bezier(0.4, 0, 0.2, 1);
  position: absolute;
  width: calc(100% - 1.5rem);
}
.nav-item-enter-from {
  opacity: 0;
  transform: translateX(-16px);
}
.nav-item-leave-to {
  opacity: 0;
  transform: translateX(-16px);
}
.nav-item-move {
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

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

.sidebar-overlay-enter-active {
  transition: opacity 0.3s ease;
}
.sidebar-overlay-leave-active {
  transition: opacity 0.2s ease;
}
.sidebar-overlay-enter-from,
.sidebar-overlay-leave-to {
  opacity: 0;
}

.sidebar-drawer-enter-active {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.sidebar-drawer-leave-active {
  transition: transform 0.2s cubic-bezier(0.4, 0, 1, 1);
}
.sidebar-drawer-enter-from,
.sidebar-drawer-leave-to {
  transform: translateX(-100%);
}

.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
