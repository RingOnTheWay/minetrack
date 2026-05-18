<script setup lang="ts">
import { computed, ref, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAppStore, themePresets } from '@/stores/app'
import type { NavKey } from '@/stores/app'
import { Palette, User, Code, ExternalLink, Check, Scale, Calendar, LayoutList, Lock, BarChart3, Filter, X, Plus, Shield, ShieldOff, Clock, Pickaxe } from 'lucide-vue-next'
import {
  LayoutDashboard, Map, Users, Swords, Hammer, Package, TrendingUp,
  Database,
} from 'lucide-vue-next'
import { getSettings, updateSettings, type FilterConfig } from '@/services/api'

const { t } = useI18n()
const app = useAppStore()

const buildDate = __BUILD_DATE__ as string

const amOrder = ['Rose', 'Emerald', 'Sky', 'Amber', 'Teal']
const kbOrder = ['Gold', 'Navy', 'Crimson', 'HotPink']

const colorGroups = computed(() => [
  { label: 'AM', colors: amOrder.map(name => themePresets.find(p => p.name === name)!) },
  { label: 'KB', colors: kbOrder.map(name => themePresets.find(p => p.name === name)!) },
])

function selectTheme(primary: string) {
  app.setThemeColor(primary)
}

function isActive(primary: string) {
  return app.themeColorPrimary === primary
}

const navItems = computed(() => [
  { icon: LayoutDashboard, label: t('nav.dashboard'), key: '/' as NavKey },
  { icon: Map, label: t('nav.mapStats'), key: '/map' as NavKey },
  { icon: Users, label: t('nav.playerStats'), key: '/players' as NavKey },
  { icon: Swords, label: t('nav.battleStats'), key: '/battle' as NavKey },
  { icon: Hammer, label: t('nav.craftStats'), key: '/craft' as NavKey },
  { icon: Package, label: t('nav.itemStats'), key: '/items' as NavKey },
  { icon: Pickaxe, label: t('nav.blockStats'), key: '/blocks' as NavKey },
  { icon: TrendingUp, label: t('nav.activity'), key: '/activity' as NavKey },
  { icon: Database, label: t('nav.dataManage'), key: '/data-manage' as NavKey },
])

function isNavDisabled(key: NavKey) {
  return key === '/data-manage' && app.isStatic
}

function toggleNav(key: NavKey) {
  if (isNavDisabled(key)) return
  app.toggleNavVisibility(key)
}

const filterEnabled = ref(false)
const minPlaytimeHours = ref(1)
const whitelist = ref<string[]>([])
const blacklist = ref<string[]>([])
const settingsLoading = ref(false)
const settingsSaving = ref(false)
const whitelistInput = ref('')
const blacklistInput = ref('')
const whitelistInputRef = ref<HTMLInputElement | null>(null)
const blacklistInputRef = ref<HTMLInputElement | null>(null)
const maxLegendPlayers = ref(app.maxLegendPlayers)

onMounted(async () => {
  if (app.isStatic) return
  settingsLoading.value = true
  try {
    const settings = await getSettings()
    filterEnabled.value = settings.filter_enabled === 'true'
    minPlaytimeHours.value = parseFloat(settings.min_playtime_hours) || 1
    whitelist.value = JSON.parse(settings.whitelist || '[]')
    blacklist.value = JSON.parse(settings.blacklist || '[]')
    const mlp = parseInt(settings.max_legend_players, 10)
    if (mlp > 0) {
      maxLegendPlayers.value = mlp
      app.setMaxLegendPlayers(mlp)
    }
  } catch {
  } finally {
    settingsLoading.value = false
  }
})

async function saveSettings() {
  settingsSaving.value = true
  try {
    await updateSettings({
      filter_enabled: String(filterEnabled.value),
      min_playtime_hours: String(minPlaytimeHours.value),
      whitelist: JSON.stringify(whitelist.value),
      blacklist: JSON.stringify(blacklist.value),
      max_legend_players: String(maxLegendPlayers.value),
    })
    app.setMaxLegendPlayers(maxLegendPlayers.value)
  } catch {
  } finally {
    settingsSaving.value = false
  }
}

function toggleFilterEnabled() {
  filterEnabled.value = !filterEnabled.value
  saveSettings()
}

function onMinPlaytimeChange() {
  if (minPlaytimeHours.value < 0) minPlaytimeHours.value = 0
  saveSettings()
}

function onMaxLegendPlayersChange() {
  if (maxLegendPlayers.value < 1) maxLegendPlayers.value = 1
  if (maxLegendPlayers.value > 100) maxLegendPlayers.value = 100
  saveSettings()
}

function addToWhitelist(name: string) {
  const trimmed = name.trim()
  if (!trimmed) return
  if (whitelist.value.includes(trimmed)) return
  whitelist.value.push(trimmed)
  const idx = blacklist.value.indexOf(trimmed)
  if (idx !== -1) blacklist.value.splice(idx, 1)
  whitelistInput.value = ''
  saveSettings()
}

function removeFromWhitelist(name: string) {
  const idx = whitelist.value.indexOf(name)
  if (idx !== -1) whitelist.value.splice(idx, 1)
  saveSettings()
}

function addToBlacklist(name: string) {
  const trimmed = name.trim()
  if (!trimmed) return
  if (blacklist.value.includes(trimmed)) return
  blacklist.value.push(trimmed)
  const idx = whitelist.value.indexOf(trimmed)
  if (idx !== -1) whitelist.value.splice(idx, 1)
  blacklistInput.value = ''
  saveSettings()
}

function removeFromBlacklist(name: string) {
  const idx = blacklist.value.indexOf(name)
  if (idx !== -1) blacklist.value.splice(idx, 1)
  saveSettings()
}

function onWhitelistKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    e.preventDefault()
    addToWhitelist(whitelistInput.value)
  }
}

function onBlacklistKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    e.preventDefault()
    addToBlacklist(blacklistInput.value)
  }
}
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <div
      v-motion-slide-bottom
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
            <Palette class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.themeColor') }}</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.themeColorDesc') }}</p>
          </div>
        </div>

        <div class="space-y-6">
          <div v-for="group in colorGroups" :key="group.label">
            <p class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-3">{{ group.label }}</p>
            <div class="flex flex-wrap gap-3">
              <button
                v-for="color in group.colors"
                :key="color.primary"
                class="group relative w-14 h-14 rounded-xl transition-all duration-300 hover:scale-110 hover:-translate-y-1 active:scale-95 focus:outline-none"
                :class="isActive(color.primary) ? 'ring-2 ring-offset-2 ring-brand dark:ring-offset-slate-800 shadow-lg' : 'shadow-sm hover:shadow-md'"
                :style="{ backgroundColor: color.primary }"
                @click="selectTheme(color.primary)"
              >
                <div
                  v-if="isActive(color.primary)"
                  class="absolute inset-0 flex items-center justify-center"
                >
                  <Check class="w-5 h-5 text-white drop-shadow-md" />
                </div>
                <div
                  v-else
                  class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <div class="w-3 h-3 rounded-full bg-white/60" />
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="50"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
            <LayoutList class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.navItems') }}</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.navItemsDesc') }}</p>
          </div>
        </div>

        <div class="space-y-2">
          <div
            v-for="item in navItems"
            :key="item.key"
            class="flex items-center justify-between p-3 rounded-xl transition-colors"
            :class="isNavDisabled(item.key) ? 'bg-slate-50/50 dark:bg-slate-800/30' : 'bg-slate-100/80 dark:bg-slate-700/50 hover:bg-slate-200/60 dark:hover:bg-slate-700/70'"
          >
            <div class="flex items-center gap-3">
              <div
                class="w-8 h-8 rounded-lg flex items-center justify-center"
                :class="isNavDisabled(item.key) ? 'bg-slate-200/50 dark:bg-slate-600/30' : 'bg-brand/10 dark:bg-brand/20'"
              >
                <component
                  :is="item.icon"
                  class="w-4 h-4"
                  :class="isNavDisabled(item.key) ? 'text-slate-400 dark:text-slate-500' : 'text-brand dark:text-brand-light'"
                />
              </div>
              <span
                class="text-sm font-medium"
                :class="isNavDisabled(item.key) ? 'text-slate-400 dark:text-slate-500' : 'text-slate-700 dark:text-slate-200'"
              >{{ item.label }}</span>
              <Lock
                v-if="isNavDisabled(item.key)"
                class="w-3.5 h-3.5 text-slate-400 dark:text-slate-500"
              />
            </div>

            <button
              class="relative w-10 h-6 rounded-full transition-all duration-300"
              :class="[
                isNavDisabled(item.key)
                  ? 'bg-slate-200 dark:bg-slate-600 cursor-not-allowed'
                  : app.isNavVisible(item.key)
                    ? 'bg-brand'
                    : 'bg-slate-300 dark:bg-slate-600'
              ]"
              :disabled="isNavDisabled(item.key)"
              @click="toggleNav(item.key)"
            >
              <div
                class="absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm transition-all duration-300"
                :class="app.isNavVisible(item.key) ? 'left-5' : 'left-1'"
              />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="75"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
              <BarChart3 class="w-6 h-6 text-brand dark:text-brand-light" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.chartTotal') }}</h3>
              <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.chartTotalDesc') }}</p>
            </div>
          </div>

          <button
            class="relative w-12 h-7 rounded-full transition-all duration-300"
            :class="app.showChartTotal ? 'bg-brand' : 'bg-slate-300 dark:bg-slate-600'"
            @click="app.toggleChartTotal()"
          >
            <div
              class="absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-sm transition-all duration-300"
              :class="app.showChartTotal ? 'left-5.5' : 'left-0.5'"
            />
          </button>
        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="81"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
            <Users class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.maxLegendPlayers') }}</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.maxLegendPlayersDesc') }}</p>
          </div>
          <div class="flex items-center gap-3">
            <input
              v-model.number="maxLegendPlayers"
              type="number"
              min="1"
              max="100"
              class="w-24 px-4 py-2.5 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              @change="onMaxLegendPlayersChange"
            />
            <span class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.players') }}</span>
          </div>
        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="87"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center justify-between" :class="filterEnabled ? 'mb-8' : ''">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
              <Filter class="w-6 h-6 text-brand dark:text-brand-light" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.playerFilter') }}</h3>
              <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.playerFilterDesc') }}</p>
            </div>
          </div>

          <button
            class="relative w-12 h-7 rounded-full transition-all duration-300"
            :class="filterEnabled ? 'bg-brand' : 'bg-slate-300 dark:bg-slate-600'"
            @click="toggleFilterEnabled"
          >
            <div
              class="absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-sm transition-all duration-300"
              :class="filterEnabled ? 'left-5.5' : 'left-0.5'"
            />
          </button>
        </div>

        <div v-if="filterEnabled" class="space-y-6">
          <div>
            <div class="flex items-center gap-2 mb-3">
              <Clock class="w-4 h-4 text-brand dark:text-brand-light" />
              <label class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.minPlaytime') }}</label>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mb-2">{{ t('settings.minPlaytimeDesc') }}</p>
            <div class="flex items-center gap-3">
              <input
                v-model.number="minPlaytimeHours"
                type="number"
                min="0"
                step="0.5"
                class="w-32 px-4 py-2.5 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                @change="onMinPlaytimeChange"
              />
              <span class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.hours') }}</span>
            </div>
          </div>

          <div>
            <div class="flex items-center gap-2 mb-3">
              <Shield class="w-4 h-4 text-emerald-500" />
              <label class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.whitelist') }}</label>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mb-2">{{ t('settings.whitelistDesc') }}</p>
            <div class="flex flex-wrap gap-2 mb-2 min-h-[2rem]">
              <span
                v-for="name in whitelist"
                :key="'w-'+name"
                class="inline-flex items-center gap-1 px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-medium rounded-lg border border-emerald-200 dark:border-emerald-800/50"
              >
                {{ name }}
                <button class="hover:text-emerald-900 dark:hover:text-emerald-200 transition-colors" @click="removeFromWhitelist(name)">
                  <X class="w-3 h-3" />
                </button>
              </span>
              <span v-if="whitelist.length === 0" class="text-xs text-slate-400 dark:text-slate-500 italic">{{ t('settings.emptyList') }}</span>
            </div>
            <div class="flex gap-2">
              <input
                ref="whitelistInputRef"
                v-model="whitelistInput"
                type="text"
                :placeholder="t('settings.addPlayerPlaceholder')"
                class="flex-1 px-3 py-2 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-lg text-sm dark:text-slate-200 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all"
                @keydown="onWhitelistKeydown"
              />
              <button
                class="px-3 py-2 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-100 dark:hover:bg-emerald-900/50 rounded-lg transition-all text-sm font-medium disabled:opacity-50"
                :disabled="!whitelistInput.trim()"
                @click="addToWhitelist(whitelistInput)"
              >
                <Plus class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div>
            <div class="flex items-center gap-2 mb-3">
              <ShieldOff class="w-4 h-4 text-red-500" />
              <label class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.blacklist') }}</label>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mb-2">{{ t('settings.blacklistDesc') }}</p>
            <div class="flex flex-wrap gap-2 mb-2 min-h-[2rem]">
              <span
                v-for="name in blacklist"
                :key="'b-'+name"
                class="inline-flex items-center gap-1 px-2.5 py-1 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-medium rounded-lg border border-red-200 dark:border-red-800/50"
              >
                {{ name }}
                <button class="hover:text-red-900 dark:hover:text-red-200 transition-colors" @click="removeFromBlacklist(name)">
                  <X class="w-3 h-3" />
                </button>
              </span>
              <span v-if="blacklist.length === 0" class="text-xs text-slate-400 dark:text-slate-500 italic">{{ t('settings.emptyList') }}</span>
            </div>
            <div class="flex gap-2">
              <input
                ref="blacklistInputRef"
                v-model="blacklistInput"
                type="text"
                :placeholder="t('settings.addPlayerPlaceholder')"
                class="flex-1 px-3 py-2 bg-white/80 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 rounded-lg text-sm dark:text-slate-200 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand/40 transition-all"
                @keydown="onBlacklistKeydown"
              />
              <button
                class="px-3 py-2 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/50 rounded-lg transition-all text-sm font-medium disabled:opacity-50"
                :disabled="!blacklistInput.trim()"
                @click="addToBlacklist(blacklistInput)"
              >
                <Plus class="w-4 h-4" />
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>

    <div
      v-motion-slide-bottom :delay="100"
      class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl p-8 border border-white/80 dark:border-slate-700/80 shadow-sm overflow-hidden"
    >
      <div class="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-brand/5 dark:from-brand/3 to-transparent rounded-full blur-3xl" />

      <div class="relative">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 bg-gradient-to-br from-brand/20 to-brand/10 rounded-xl flex items-center justify-center">
            <User class="w-6 h-6 text-brand dark:text-brand-light" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ t('settings.about') }}</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('settings.aboutDesc') }}</p>
          </div>
        </div>

        <div class="space-y-4">
          <div class="flex items-center gap-4 p-4 bg-slate-100/80 dark:bg-slate-700/50 rounded-xl">
            <div class="w-10 h-10 bg-gradient-to-br from-brand/30 to-brand/10 rounded-lg flex items-center justify-center shrink-0">
              <Code class="w-5 h-5 text-brand dark:text-brand-light" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.author') }}</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">RiNG</p>
            </div>
          </div>

          <div class="flex items-center gap-4 p-4 bg-slate-100/80 dark:bg-slate-700/50 rounded-xl">
            <div class="w-10 h-10 bg-gradient-to-br from-brand/30 to-brand/10 rounded-lg flex items-center justify-center shrink-0">
              <Scale class="w-5 h-5 text-brand dark:text-brand-light" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.license') }}</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">MIT</p>
            </div>
          </div>

          <div class="flex items-center gap-4 p-4 bg-slate-100/80 dark:bg-slate-700/50 rounded-xl">
            <div class="w-10 h-10 bg-gradient-to-br from-brand/30 to-brand/10 rounded-lg flex items-center justify-center shrink-0">
              <ExternalLink class="w-5 h-5 text-brand dark:text-brand-light" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.projectRepo') }}</p>
              <a
                href="https://github.com/RingOnTheWay/minetrack"
                target="_blank"
                rel="noopener noreferrer"
                class="text-sm text-brand dark:text-brand-light hover:underline"
              >GitHub</a>
            </div>
          </div>

          <div class="flex items-center gap-4 p-4 bg-slate-100/80 dark:bg-slate-700/50 rounded-xl">
            <div class="w-10 h-10 bg-gradient-to-br from-brand/30 to-brand/10 rounded-lg flex items-center justify-center shrink-0">
              <Code class="w-5 h-5 text-brand dark:text-brand-light" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.version') }}</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">v0.1.0</p>
            </div>
          </div>

          <div class="flex items-center gap-4 p-4 bg-slate-100/80 dark:bg-slate-700/50 rounded-xl">
            <div class="w-10 h-10 bg-gradient-to-br from-brand/30 to-brand/10 rounded-lg flex items-center justify-center shrink-0">
              <Calendar class="w-5 h-5 text-brand dark:text-brand-light" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ t('settings.buildDate') }}</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">{{ buildDate }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
