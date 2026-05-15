<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAppStore, themePresets } from '@/stores/app'
import { Palette, User, Code, ExternalLink, Check, Scale, Calendar } from 'lucide-vue-next'

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
      v-motion-slide-bottom="{ delay: 100 }"
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
